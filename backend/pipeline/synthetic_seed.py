"""Generate a realistic synthetic seed dataset.

The committed seed (`data/seed/salons.json`) lets the app run out-of-the-box
with no API keys. Until a real `make pipeline` run replaces it with live Google
Places data, this generator produces believable, varied Warsaw salons across
all 18 districts — enough for a rich browse/filter/detail demo. Embeddings are
left empty and generated on load when an OpenAI key is present (see
`pipeline.seed`).

Deterministic (fixed RNG seed) so the output is reproducible.

    python -m pipeline.synthetic_seed   # (re)writes data/seed/salons.json
"""

import random

from app.core.constants import WARSAW_DISTRICTS, PriceRange
from app.core.logging import configure_logging, get_logger
from pipeline.enrichment.models import EnrichedSalon
from pipeline.storage import write_enriched_salons

logger = get_logger(__name__)

# Salon "archetypes": each maps to a coherent set of taxonomy service slugs and
# a summary tone, so generated salons feel real rather than random.
_ARCHETYPES: tuple[tuple[str, list[str], str], ...] = (
    (
        "hair",
        ["womens-haircut", "mens-haircut", "hair-coloring", "balayage-highlights", "hair-styling"],
        "Popular neighbourhood hair studio. Pros: skilled colourists, great balayage, "
        "welcoming staff. Cons: books up fast on weekends.",
    ),
    (
        "barber",
        ["barber", "beard-trim", "mens-haircut"],
        "Classic barbershop vibe. Pros: precise fades, friendly conversation, walk-ins "
        "welcome. Cons: cash preferred, small waiting area.",
    ),
    (
        "nails",
        ["manicure", "pedicure", "gel-nails", "nail-art"],
        "Cosy nail bar. Pros: long-lasting hybrids, creative nail art, spotless tools. "
        "Cons: limited parking nearby.",
    ),
    (
        "beauty",
        ["facial", "waxing", "makeup", "brow-shaping"],
        "Full-service beauty salon. Pros: relaxing facials, gentle waxing, lovely makeup "
        "for events. Cons: premium pricing.",
    ),
    (
        "lashes",
        ["lash-extensions", "lash-lift", "brow-shaping"],
        "Brow & lash specialist. Pros: natural-looking extensions, careful brow shaping. "
        "Cons: appointment-only.",
    ),
    (
        "spa",
        ["massage", "facial", "hair-treatment"],
        "Calm day-spa. Pros: excellent massages, soothing atmosphere, attentive therapists. "
        "Cons: a little hard to find the entrance.",
    ),
)

_NAME_PREFIXES = ("Studio", "Salon", "Atelier", "Pracownia", "Instytut")
_NAME_THEMES = (
    "Uroda",
    "Piękno",
    "Glamour",
    "Bella",
    "Elegance",
    "Lumière",
    "Aurora",
    "Wenus",
    "Finezja",
    "Metamorfoza",
)
_OWNER_SUFFIXES = ("u Anny", "u Kasi", "u Magdy", "u Oli", "by Ewa", "by Marta", "")
_STREETS = (
    "Marszałkowska", "Puławska", "Grójecka", "Mokotowska", "Nowy Świat", "Chmielna",
    "Wilcza", "Koszykowa", "Targowa", "Świętokrzyska", "Krucza", "Belwederska",
    "Żelazna", "Wolska", "Górczewska", "Kasprzaka",
)
_PRICE_CYCLE = (PriceRange.BUDGET, PriceRange.MODERATE, PriceRange.MODERATE, PriceRange.PREMIUM)


def _district_centroid(district: str) -> tuple[float, float]:
    """Return an approximate centroid for a district (lazy import to avoid cycles)."""
    from pipeline.collectors.warsaw_districts import WARSAW_DISTRICT_CENTROIDS

    for centroid in WARSAW_DISTRICT_CENTROIDS:
        if centroid.name == district:
            return centroid.latitude, centroid.longitude
    return 52.2297, 21.0122  # Warsaw centre fallback


def generate(count: int = 60, *, rng_seed: int = 42) -> list[EnrichedSalon]:
    """Generate ``count`` deterministic, varied synthetic salons."""
    rng = random.Random(rng_seed)
    salons: list[EnrichedSalon] = []

    for i in range(count):
        archetype, services, summary = _ARCHETYPES[i % len(_ARCHETYPES)]
        district = WARSAW_DISTRICTS[i % len(WARSAW_DISTRICTS)]
        name = " ".join(
            part
            for part in (
                rng.choice(_NAME_PREFIXES),
                rng.choice(_NAME_THEMES),
                rng.choice(_OWNER_SUFFIXES),
            )
            if part
        )
        lat, lng = _district_centroid(district)
        has_site = rng.random() < 0.6
        street = rng.choice(_STREETS)
        phone = f"+48 {rng.randint(500, 899)} {rng.randint(100, 999)} {rng.randint(100, 999)}"

        salons.append(
            EnrichedSalon(
                source="synthetic",
                source_id=f"syn-{i:03d}",
                name=name,
                address=f"ul. {street} {rng.randint(1, 180)}, {district}, Warszawa",
                district=district,
                latitude=round(lat + rng.uniform(-0.01, 0.01), 6),
                longitude=round(lng + rng.uniform(-0.01, 0.01), 6),
                phone=phone,
                website=f"https://{archetype}-{i:03d}.example.pl" if has_site else None,
                price_range=_PRICE_CYCLE[i % len(_PRICE_CYCLE)].value,
                rating=round(rng.uniform(4.1, 5.0), 1),
                review_count=rng.randint(12, 820),
                raw_services_text=", ".join(services),
                review_summary=summary,
                service_slugs=services,
                embedding=None,
            )
        )

    return salons


def main() -> None:
    configure_logging()
    salons = generate()
    written = write_enriched_salons(salons)
    logger.info("Wrote %d synthetic salons to the seed dataset", written)


if __name__ == "__main__":
    main()
