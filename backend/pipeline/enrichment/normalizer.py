"""Normalization stage — the heart of the data-quality story.

Turns messy, multilingual source fields into the canonical domain:

* **District** is resolved deterministically from the address text (a cheap,
  reliable signal).
* **Services and price tier** are extracted by a single LLM call over the
  salon's name, Google categories, and — crucially — its **customer reviews**.
  Reviews are the richest signal: they name concrete services ("koloryzacja",
  "trwała", "fade") and price cues ("400 zł", "przystępne ceny") that the coarse
  Google ``types`` and (usually empty) ``editorialSummary`` never capture.

The model's service output is validated against the closed taxonomy, deduped,
and unioned with a deterministic floor for the salon's primary category so the
obvious core service is never missed. Price falls back from any Google price
level to the review-derived tier. ``other`` is only kept when nothing else fits.
"""

from pydantic import BaseModel

from app.ai.base import LLMClient
from app.core.constants import WARSAW_DISTRICTS, PriceRange
from app.core.logging import get_logger
from app.core.taxonomy import SERVICE_TAXONOMY, VALID_SERVICE_SLUGS
from pipeline.collectors.base import RawSalon

logger = get_logger(__name__)

_DEFAULT_DISTRICT = "Śródmieście"
_MAX_REVIEWS = 6
_REVIEW_CHARS = 2400

# Google Places (New) price level enum -> canonical price band.
_PRICE_LEVEL_MAP: dict[str, PriceRange] = {
    "PRICE_LEVEL_INEXPENSIVE": PriceRange.BUDGET,
    "PRICE_LEVEL_MODERATE": PriceRange.MODERATE,
    "PRICE_LEVEL_EXPENSIVE": PriceRange.PREMIUM,
    "PRICE_LEVEL_VERY_EXPENSIVE": PriceRange.PREMIUM,
}

# Review-derived price tier (LLM) -> canonical price band. "unknown" -> None.
_PRICE_TIER_MAP: dict[str, PriceRange] = {
    "budget": PriceRange.BUDGET,
    "moderate": PriceRange.MODERATE,
    "premium": PriceRange.PREMIUM,
}

# Deterministic floor: a salon's primary Google category implies a core service
# that should always be present, even when reviews are sparse. Kept conservative
# (only unambiguous categories) so it never injects a wrong service.
_TYPE_FLOOR: dict[str, list[str]] = {
    "barber_shop": ["barber"],
    "hair_salon": ["womens-haircut"],
    "nail_salon": ["manicure"],
    "spa": ["massage"],
    "massage_spa": ["massage"],
    "skin_care_clinic": ["facial"],
}

_ENRICHMENT_SYSTEM_PROMPT = (
    "You are a data analyst for a Warsaw beauty-salon directory. From the salon's "
    "name, Google categories and CUSTOMER REVIEWS, output the services it actually "
    "offers (taxonomy slugs) and a price tier.\n"
    "SERVICES — include a slug only with clear evidence: a review mentioning it, or "
    "a Google category that directly implies it (hair_salon->haircuts, nail_salon->"
    "manicure, barber_shop->barber, spa/massage->massage). Map Polish terms: "
    "koloryzacja->hair-coloring; baleyage/sombre/refleksy/pasemka->balayage-highlights; "
    "strzyżenie damskie->womens-haircut; strzyżenie męskie/fryzjer męski/fade->"
    "mens-haircut; broda/zarost->beard-trim; trwała/modelowanie/prostowanie/upięcie->"
    "hair-styling; keratyna/botoks/regeneracja/nawilżanie włosów->hair-treatment; "
    "hybryda/żel/paznokcie->gel-nails; manicure->manicure; pedicure->pedicure; "
    "zdobienia->nail-art; rzęsy/przedłużanie rzęs->lash-extensions; lifting/laminacja "
    "rzęs->lash-lift; brwi/henna brwi/regulacja brwi->brow-shaping; makijaż->makeup; "
    "masaż->massage; oczyszczanie/zabieg na twarz/peeling/mezoterapia->facial; "
    "depilacja/woskowanie/wosk->waxing. Do NOT assume a full menu from one mention "
    "(a barber doing fades is NOT a colorist; a nail salon is NOT a hairdresser). "
    "Prefer specific slugs; use 'other' ONLY when nothing fits, never alongside "
    "specific slugs.\n"
    "PRICE TIER from review language ONLY: 'budget' (tanio/niedrogo/przystępne ceny "
    "or low prices), 'premium' (drogo/wygórowane/ekskluzywny or high prices), "
    "'moderate' (explicit reasonable/fair/mid or mixed price mentions), 'unknown' "
    "(no price or value language — do NOT guess from quality or ambience)."
)


class NormalizedFields(BaseModel):
    """The normalized subset of a salon's fields."""

    district: str
    price_range: str | None
    service_slugs: list[str]


class _SalonEnrichment(BaseModel):
    """Structured LLM output: services + a coarse price tier (validated downstream)."""

    service_slugs: list[str]
    # budget | moderate | premium | unknown. Defaulted so partial fakes/old
    # outputs stay valid; the real model always sets it.
    price_tier: str = "unknown"


def resolve_district(raw: RawSalon) -> str:
    """Resolve a salon to one of Warsaw's 18 districts.

    Prefers the authoritative address text; falls back to the district whose
    query surfaced the place; finally defaults to the city centre.
    """
    if raw.address:
        address_lower = raw.address.lower()
        for district in WARSAW_DISTRICTS:
            if district.lower() in address_lower:
                return district
    if raw.district_hint is not None and raw.district_hint in WARSAW_DISTRICTS:
        return raw.district_hint
    return _DEFAULT_DISTRICT


def normalize_price_range(price_level: str | None) -> str | None:
    """Map a Google price-level enum to a canonical price band, or ``None``."""
    if not price_level:
        return None
    band = _PRICE_LEVEL_MAP.get(price_level)
    return band.value if band else None


def _type_floor(raw: RawSalon) -> list[str]:
    """Core service(s) implied by the salon's primary Google category."""
    primary = raw.primary_type or (raw.types[0] if raw.types else None)
    return _TYPE_FLOOR.get(primary or "", [])


class SalonNormalizer:
    """Normalizes raw salons; uses one LLM call for services + price tier."""

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def normalize(self, raw: RawSalon) -> NormalizedFields:
        """Return normalized district, price band, and service slugs."""
        enrichment = self._enrich(raw)
        # Trust Google's own price level when present (rare for salons); otherwise
        # use the review-derived tier.
        price_range = normalize_price_range(raw.price_level)
        if price_range is None:
            tier = _PRICE_TIER_MAP.get(enrichment.price_tier.strip().lower())
            price_range = tier.value if tier else None
        return NormalizedFields(
            district=resolve_district(raw),
            price_range=price_range,
            service_slugs=self._resolve_services(raw, enrichment.service_slugs),
        )

    def _enrich(self, raw: RawSalon) -> _SalonEnrichment:
        """Single structured LLM call extracting services + price tier from reviews."""
        allowed = ", ".join(f"{s.slug} ({s.name})" for s in SERVICE_TAXONOMY)
        reviews = "\n".join(f"- {r}" for r in raw.reviews[:_MAX_REVIEWS])[:_REVIEW_CHARS]
        user = (
            f"Taxonomy slugs: {allowed}\n\n"
            f"Name: {raw.name}\n"
            f"Google categories: {', '.join(raw.types) or 'n/a'}\n"
            f"Primary category: {raw.primary_type_display or 'n/a'}\n"
            f"Reviews:\n{reviews or '(none)'}"
        )
        try:
            return self._llm.parse(
                system=_ENRICHMENT_SYSTEM_PROMPT, user=user, schema=_SalonEnrichment
            )
        except Exception:  # noqa: BLE001 - never let one salon abort the pipeline
            logger.exception("Enrichment failed for %s; using type floor only", raw.name)
            return _SalonEnrichment(service_slugs=[], price_tier="unknown")

    def _resolve_services(self, raw: RawSalon, llm_slugs: list[str]) -> list[str]:
        """Validate, union with the type floor, dedupe, and clean up the slug list."""
        valid = [slug for slug in llm_slugs if slug in VALID_SERVICE_SLUGS]
        merged = list(dict.fromkeys([*_type_floor(raw), *valid]))  # floor first, ordered
        specific = [slug for slug in merged if slug != "other"]
        return specific or ["other"]
