"""Normalization stage — the heart of the data-quality story.

Turns messy, multilingual source fields into the canonical domain:

* **District** and **price range** are resolved deterministically (cheap,
  reliable signals — address text and Google's price enum).
* **Services** are classified by the LLM, which is where the genuine NLP value
  is: mapping free-text like *"koloryzacja, baleyage, strzyżenie"* onto the
  fixed taxonomy. The model's output is always validated against known slugs.
"""

from pydantic import BaseModel

from app.ai.base import LLMClient
from app.core.constants import WARSAW_DISTRICTS, PriceRange
from app.core.logging import get_logger
from app.core.taxonomy import SERVICE_TAXONOMY, VALID_SERVICE_SLUGS
from pipeline.collectors.base import RawSalon

logger = get_logger(__name__)

_DEFAULT_DISTRICT = "Śródmieście"

# Google Places (New) price level enum -> canonical price band.
_PRICE_LEVEL_MAP: dict[str, PriceRange] = {
    "PRICE_LEVEL_INEXPENSIVE": PriceRange.BUDGET,
    "PRICE_LEVEL_MODERATE": PriceRange.MODERATE,
    "PRICE_LEVEL_EXPENSIVE": PriceRange.PREMIUM,
    "PRICE_LEVEL_VERY_EXPENSIVE": PriceRange.PREMIUM,
}

_SERVICE_SYSTEM_PROMPT = (
    "You classify Polish/English beauty-salon descriptions into a fixed service "
    "taxonomy. Return only slugs from the provided list that the salon clearly "
    "offers. Do not invent slugs. If nothing matches, return ['other']."
)


class NormalizedFields(BaseModel):
    """The normalized subset of a salon's fields."""

    district: str
    price_range: str | None
    service_slugs: list[str]


class _ServiceClassification(BaseModel):
    """Structured LLM output: chosen service slugs (validated downstream)."""

    service_slugs: list[str]


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


class SalonNormalizer:
    """Normalizes raw salons; uses an LLM only for service classification."""

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def normalize(self, raw: RawSalon) -> NormalizedFields:
        """Return normalized district, price band, and service slugs."""
        return NormalizedFields(
            district=resolve_district(raw),
            price_range=normalize_price_range(raw.price_level),
            service_slugs=self._classify_services(raw),
        )

    def _classify_services(self, raw: RawSalon) -> list[str]:
        """Classify a salon's services into canonical slugs via the LLM."""
        description = " | ".join(
            part for part in [raw.name, raw.raw_services_text, " ".join(raw.types)] if part
        )
        allowed = ", ".join(f"{s.slug} ({s.name})" for s in SERVICE_TAXONOMY)
        result = self._llm.parse(
            system=_SERVICE_SYSTEM_PROMPT,
            user=f"Allowed slugs: {allowed}\n\nSalon: {description}",
            schema=_ServiceClassification,
        )
        # Validate against the taxonomy; drop anything hallucinated.
        valid = [slug for slug in result.service_slugs if slug in VALID_SERVICE_SLUGS]
        deduped = list(dict.fromkeys(valid))  # preserve order, remove repeats
        return deduped or ["other"]
