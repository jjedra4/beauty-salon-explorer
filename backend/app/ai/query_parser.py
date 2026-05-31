"""LLM query understanding for semantic search.

Turns a free-text query into structured :class:`SearchFilters`. The model's
output is always re-validated against the domain (known districts, taxonomy
slugs, price bands, rating range) so a hallucinated value becomes a dropped
filter rather than a broken query.
"""

from app.ai.base import LLMClient
from app.core.constants import WARSAW_DISTRICTS, PriceRange
from app.core.taxonomy import SERVICE_TAXONOMY, VALID_SERVICE_SLUGS
from app.schemas.search import SearchFilters

_VALID_PRICE_RANGES = {band.value for band in PriceRange}

_SYSTEM_PROMPT = (
    "You extract structured search filters from a user's query for a Warsaw "
    "beauty-salon directory. Queries may be in Polish or English. Only set a "
    "field when the query clearly implies it; otherwise leave it null/empty. "
    "Map service mentions to the provided slugs. Interpret 'cheap/tani' as '$', "
    "'premium/drogi' as '$$$'. Interpret 'good/great reviews' as min_rating 4.5."
)


class QueryParser:
    """Extracts and validates structured filters from a search query."""

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def parse(self, query: str) -> SearchFilters:
        """Return validated filters extracted from ``query``."""
        allowed = ", ".join(f"{s.slug} ({s.name})" for s in SERVICE_TAXONOMY)
        raw = self._llm.parse(
            system=_SYSTEM_PROMPT,
            user=f"Allowed service slugs: {allowed}\n\nDistricts: {', '.join(WARSAW_DISTRICTS)}\n\n"
            f"Query: {query}",
            schema=SearchFilters,
        )
        return self._sanitize(raw)

    @staticmethod
    def _sanitize(filters: SearchFilters) -> SearchFilters:
        """Drop any values that fall outside the known domain."""
        district = filters.district if filters.district in WARSAW_DISTRICTS else None
        slugs = [slug for slug in filters.service_slugs if slug in VALID_SERVICE_SLUGS]
        price = filters.price_range if filters.price_range in _VALID_PRICE_RANGES else None
        rating = filters.min_rating
        if rating is not None:
            rating = max(0.0, min(5.0, rating))
        return SearchFilters(
            district=district,
            service_slugs=list(dict.fromkeys(slugs)),
            price_range=price,
            min_rating=rating,
        )
