"""Canonical service taxonomy.

The fixed vocabulary of salon services. Lives in ``app.core`` because it is
shared domain data: the API validates edits against it, and the data pipeline
normalizes messy source text into it. Keeping it small and closed makes both
normalization and "filter/edit by service" reliable.
"""

from typing import NamedTuple

from app.core.constants import ServiceCategory


class ServiceDef(NamedTuple):
    """A canonical service: stable slug, display name, and grouping."""

    slug: str
    name: str
    category: ServiceCategory


SERVICE_TAXONOMY: tuple[ServiceDef, ...] = (
    # Hair
    ServiceDef("womens-haircut", "Women's haircut", ServiceCategory.HAIR),
    ServiceDef("mens-haircut", "Men's haircut", ServiceCategory.HAIR),
    ServiceDef("hair-coloring", "Hair coloring", ServiceCategory.HAIR),
    ServiceDef("balayage-highlights", "Balayage & highlights", ServiceCategory.HAIR),
    ServiceDef("hair-styling", "Hair styling & blow-dry", ServiceCategory.HAIR),
    ServiceDef("hair-treatment", "Hair treatment", ServiceCategory.HAIR),
    # Barber
    ServiceDef("barber", "Barber", ServiceCategory.BARBER),
    ServiceDef("beard-trim", "Beard trim", ServiceCategory.BARBER),
    # Nails
    ServiceDef("manicure", "Manicure", ServiceCategory.NAILS),
    ServiceDef("pedicure", "Pedicure", ServiceCategory.NAILS),
    ServiceDef("gel-nails", "Gel & hybrid nails", ServiceCategory.NAILS),
    ServiceDef("nail-art", "Nail art", ServiceCategory.NAILS),
    # Brows & lashes
    ServiceDef("brow-shaping", "Brow shaping & tint", ServiceCategory.BROWS_LASHES),
    ServiceDef("lash-extensions", "Lash extensions", ServiceCategory.BROWS_LASHES),
    ServiceDef("lash-lift", "Lash lift", ServiceCategory.BROWS_LASHES),
    # Makeup
    ServiceDef("makeup", "Makeup", ServiceCategory.MAKEUP),
    # Spa / beauty
    ServiceDef("facial", "Facial treatment", ServiceCategory.SPA),
    ServiceDef("massage", "Massage", ServiceCategory.SPA),
    ServiceDef("waxing", "Waxing & depilation", ServiceCategory.SPA),
    ServiceDef("other", "Other", ServiceCategory.OTHER),
)

# Lookups derived from the taxonomy.
SERVICE_BY_SLUG: dict[str, ServiceDef] = {service.slug: service for service in SERVICE_TAXONOMY}
VALID_SERVICE_SLUGS: frozenset[str] = frozenset(SERVICE_BY_SLUG)
