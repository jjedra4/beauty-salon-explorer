"""Collector abstractions (Strategy pattern).

A :class:`SalonCollector` knows how to pull raw salon records from one data
source. New sources (Booksy, OSM, other cities) are added by implementing this
interface — the rest of the pipeline is source-agnostic, which is what makes
scaling to all of Poland a matter of adding collectors rather than rewriting.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from datetime import UTC, datetime

from pydantic import BaseModel, Field


class RawSalon(BaseModel):
    """A salon record exactly as collected from a source, before enrichment.

    Fields mirror what sources actually provide (e.g. Google's enum price level
    and raw place ``types``); normalization into the canonical domain happens
    later in the AI enrichment stage (M3).
    """

    source: str
    source_id: str
    name: str
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    phone: str | None = None
    website: str | None = None
    rating: float | None = None
    review_count: int | None = None
    # Source-specific price signal (e.g. Google "PRICE_LEVEL_MODERATE").
    price_level: str | None = None
    # Source category labels (e.g. Google place ``types``).
    types: list[str] = Field(default_factory=list)
    # Free-text review snippets, used later for AI summarization.
    reviews: list[str] = Field(default_factory=list)
    # Any free text describing services (editorial summary, joined types, ...).
    raw_services_text: str | None = None
    # Which district's query surfaced this place — a hint for normalization.
    district_hint: str | None = None
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SalonCollector(ABC):
    """Strategy interface for a salon data source."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Stable identifier for this source (stored as ``RawSalon.source``)."""

    @abstractmethod
    def collect(self) -> Iterator[RawSalon]:
        """Yield raw salon records from the source.

        Implementations are responsible for paging through the source and for
        within-run deduplication by ``source_id``.
        """
