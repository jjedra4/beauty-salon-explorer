"""Salon ORM model — the central entity of the application.

A salon carries provenance (which source it came from), the required fields
(name/address/district), optional contact and quality signals, and the
AI-generated artifacts: a review summary and a `pgvector` embedding used for
semantic search.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    DateTime,
    Float,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import EMBEDDING_DIM
from app.core.database import Base
from app.models.service import salon_services

if TYPE_CHECKING:
    from app.models.service import Service


class Salon(Base):
    """A hair/beauty salon and everything we know about it."""

    __tablename__ = "salons"
    # A salon is uniquely identified by (source, source_id); dedup across
    # sources happens in the pipeline before load, so rows here are canonical.
    __table_args__ = (UniqueConstraint("source", "source_id", name="uq_salon_source"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    # --- Provenance ---
    source: Mapped[str] = mapped_column(String(32), index=True)
    source_id: Mapped[str] = mapped_column(String(128))

    # --- Required fields ---
    name: Mapped[str] = mapped_column(String(255), index=True)
    address: Mapped[str] = mapped_column(String(512))
    district: Mapped[str] = mapped_column(String(64), index=True)

    # --- Location (nice-to-have) ---
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    # --- Contact (nice-to-have) ---
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    website: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # --- Quality / pricing signals (nice-to-have) ---
    price_range: Mapped[str | None] = mapped_column(String(8), nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    review_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # --- AI-enriched fields ---
    # Original, un-normalized service text kept for transparency/debugging.
    raw_services_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    # LLM-generated pros/cons + "vibe" summary of reviews.
    review_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Embedding of the salon's searchable text, for vector similarity search.
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)

    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    services: Mapped[list[Service]] = relationship(
        secondary=salon_services,
        back_populates="salons",
        lazy="selectin",
    )
