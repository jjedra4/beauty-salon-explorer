"""Schemas for natural-language search.

`SearchFilters` doubles as the LLM's structured-output target (the filters it
extracts from a query) and the internal filter object applied to the database.
"""

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.salon import SalonSummary


class SearchFilters(BaseModel):
    """Structured filters extracted from a natural-language query.

    Example: *"tani fryzjer na Mokotowie z dobrymi opiniami"* →
    ``district="Mokotów", service_slugs=["womens-haircut", ...],
    price_range="$", min_rating=4.5``.
    """

    district: str | None = None
    service_slugs: list[str] = Field(default_factory=list)
    price_range: str | None = None
    min_rating: float | None = None


class SalonSearchResult(SalonSummary):
    """A salon summary annotated with its search relevance score (0..1)."""

    score: float


class SearchResponse(BaseModel):
    """Response for ``GET /salons/search``."""

    query: str
    # Which retrieval path produced the results.
    mode: Literal["semantic", "keyword"]
    items: list[SalonSearchResult]
