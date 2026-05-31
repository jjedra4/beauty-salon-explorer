"""Service taxonomy ORM model.

A small, normalized vocabulary of services (e.g. "hair-coloring", "manicure").
Salons relate to services many-to-many, so filtering by service type is a
simple join rather than a substring search over free text.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.salon import Salon

# Association table for the Salon <-> Service many-to-many relationship.
salon_services = Table(
    "salon_services",
    Base.metadata,
    Column("salon_id", ForeignKey("salons.id", ondelete="CASCADE"), primary_key=True),
    Column("service_id", ForeignKey("services.id", ondelete="CASCADE"), primary_key=True),
)


class Service(Base):
    """A canonical service offered by salons."""

    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Stable machine identifier, e.g. "hair-coloring".
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    # Human-readable label, e.g. "Hair coloring".
    name: Mapped[str] = mapped_column(String(128))
    # Top-level grouping (see ServiceCategory), e.g. "hair".
    category: Mapped[str] = mapped_column(String(32), index=True)

    salons: Mapped[list[Salon]] = relationship(
        secondary=salon_services,
        back_populates="services",
    )
