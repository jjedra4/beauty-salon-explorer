"""Pydantic schemas (DTOs) for salons.

These define the API's transport contracts and are deliberately separate from
the SQLAlchemy ORM models: the list view is a lean summary, the detail view is
rich, and updates are partial. Keeping them apart avoids leaking persistence
concerns (embeddings, provenance) into the public API.
"""

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.service import ServiceRead


class SalonSummary(BaseModel):
    """Lightweight salon representation for list/search results."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    district: str
    rating: float | None = None
    review_count: int | None = None
    price_range: str | None = None
    services: list[ServiceRead] = Field(default_factory=list)


class SalonDetail(SalonSummary):
    """Full salon details for the detail view."""

    address: str
    latitude: float | None = None
    longitude: float | None = None
    phone: str | None = None
    website: str | None = None
    review_summary: str | None = None


class SalonUpdate(BaseModel):
    """Partial update payload for ``PATCH /salons/{id}``.

    Every field is optional; only provided fields are applied. ``service_slugs``
    replaces the salon's services when present.
    """

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=255)
    address: str | None = Field(default=None, min_length=1, max_length=512)
    district: str | None = Field(default=None, max_length=64)
    phone: str | None = Field(default=None, max_length=64)
    website: str | None = Field(default=None, max_length=512)
    price_range: str | None = Field(default=None, max_length=8)
    rating: float | None = Field(default=None, ge=0, le=5)
    review_count: int | None = Field(default=None, ge=0)
    review_summary: str | None = None
    service_slugs: list[str] | None = None


class PaginatedSalons(BaseModel):
    """A page of salon summaries plus pagination metadata."""

    items: list[SalonSummary]
    total: int
    limit: int
    offset: int
