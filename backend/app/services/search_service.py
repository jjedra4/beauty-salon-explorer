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
        """Run LLM filter extraction + vector ranking."""
        assert self._llm is not None and self._embedder is not None
        filters = QueryParser(self._llm).parse(query)
        vector = self._embedder.embed([query])[0]
        results = self._repo.vector_search(vector, filters, limit)
        logger.info("Semantic search '%s' -> %d results", query, len(results))
        return SearchOutcome(mode="semantic", results=results)
