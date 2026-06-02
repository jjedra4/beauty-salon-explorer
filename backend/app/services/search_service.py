"""Natural-language search business logic.

Two retrieval paths:

* **Semantic** (when an OpenAI key is configured): the LLM extracts structured
  filters from the query, the query is embedded, and salons are ranked by
  vector cosine distance with the filters applied as hard constraints.
* **Keyword** (fallback): trigram/substring matching, so search always returns
  something even with no API key or no embeddings in the data.

The clients are injected, so the service is fully testable; ``from_settings``
wires the real OpenAI-backed clients for production use.
"""

import math
from dataclasses import dataclass
from typing import Literal

from sqlalchemy.orm import Session

from app.ai import get_embedding_client, get_llm_client
from app.ai.base import EmbeddingClient, LLMClient
from app.ai.query_parser import QueryParser
from app.core.logging import get_logger
from app.models.salon import Salon
from app.repositories.salon_repository import SalonRepository
from app.schemas.search import SearchFilters

logger = get_logger(__name__)

# Blended relevance weights (sum to 1). Vector similarity leads; a salon's
# review-weighted quality and how well it matches the extracted filters refine
# the order without ever excluding a candidate.
_W_SIMILARITY = 0.62
_W_QUALITY = 0.20
_W_FILTERS = 0.18
# Rating assumed for unrated salons (slightly below the ~4.6 city average).
_DEFAULT_RATING = 3.6
# Review count at which we fully trust a rating (log10(1000) = 3).
_CONFIDENCE_SATURATION = 3.0


@dataclass
class SearchOutcome:
    """Result of a search: the ranked salons and which path produced them."""

    mode: Literal["semantic", "keyword"]
    results: list[tuple[Salon, float]]


class SearchService:
    """Runs natural-language search, preferring semantic, falling back to keyword."""

    def __init__(
        self,
        db: Session,
        *,
        llm: LLMClient | None = None,
        embedder: EmbeddingClient | None = None,
    ) -> None:
        self._repo = SalonRepository(db)
        self._llm = llm
        self._embedder = embedder

    @classmethod
    def from_settings(cls, db: Session) -> "SearchService":
        """Build a service wired to the configured OpenAI clients (if any)."""
        return cls(db, llm=get_llm_client(), embedder=get_embedding_client())

    def search(self, query: str, limit: int = 20) -> SearchOutcome:
        """Search for salons matching a natural-language ``query``."""
        query = query.strip()
        if not query:
            return SearchOutcome(mode="keyword", results=[])

        if self._llm is not None and self._embedder is not None:
            outcome = self._semantic_search(query, limit)
            if outcome.results:
                return outcome
            # No embeddings in the data (or no matches) — fall through.

        results = self._repo.keyword_search(query, SearchFilters(), limit)
        return SearchOutcome(mode="keyword", results=results)

    def _semantic_search(self, query: str, limit: int) -> SearchOutcome:
        """Run LLM filter extraction + vector retrieval + blended re-ranking."""
        assert self._llm is not None and self._embedder is not None
        filters = QueryParser(self._llm).parse(query)
        vector = self._embedder.embed([query])[0]
        # Pull a generous candidate pool, then re-rank — so soft signals reorder
        # results instead of filtering them away.
        pool = self._repo.vector_candidates(
            vector, district=filters.district, pool_size=max(limit * 4, 60)
        )
        ranked = self._rank(pool, filters)[:limit]
        logger.info("Semantic search '%s' -> %d results", query, len(ranked))
        return SearchOutcome(mode="semantic", results=ranked)

    def _rank(
        self, pool: list[tuple[Salon, float]], filters: SearchFilters
    ) -> list[tuple[Salon, float]]:
        """Re-rank a candidate pool by a blended 0..1 relevance score."""
        scored = [(salon, self._score(salon, distance, filters)) for salon, distance in pool]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored

    def _score(self, salon: Salon, distance: float, filters: SearchFilters) -> float:
        """Blend vector similarity, review-weighted quality, and filter match."""
        similarity = max(0.0, 1.0 - distance)
        rating = salon.rating if salon.rating is not None else _DEFAULT_RATING
        confidence = min(1.0, math.log10((salon.review_count or 0) + 1) / _CONFIDENCE_SATURATION)
        # A high rating counts more when many reviews back it up.
        quality = (rating / 5.0) * (0.5 + 0.5 * confidence)
        return (
            _W_SIMILARITY * similarity
            + _W_QUALITY * quality
            + _W_FILTERS * self._filter_match(salon, filters)
        )

    @staticmethod
    def _filter_match(salon: Salon, filters: SearchFilters) -> float:
        """Fraction of the extracted soft filters this salon satisfies (0..1).

        Returns a neutral 0.5 when the query carried no soft filters, so the
        term neither helps nor hurts.
        """
        signals: list[float] = []
        if filters.service_slugs:
            wanted = set(filters.service_slugs)
            offered = {service.slug for service in salon.services}
            signals.append(1.0 if wanted & offered else 0.0)
        if filters.price_range:
            signals.append(1.0 if salon.price_range == filters.price_range else 0.0)
        if filters.min_rating is not None:
            signals.append(1.0 if (salon.rating or 0.0) >= filters.min_rating else 0.0)
        return sum(signals) / len(signals) if signals else 0.5
