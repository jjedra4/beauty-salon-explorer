"""Domain constants shared across the API, the data pipeline, and search.

Keeping these in one place means the salon model, the LLM normalizer, and the
search filters all agree on the same canonical districts, price bands, and
embedding dimension.
"""

from enum import StrEnum

# Dimension of OpenAI `text-embedding-3-small` vectors.
EMBEDDING_DIM = 1536

# The 18 official districts (dzielnice) of Warsaw. The normalizer maps every
# salon to exactly one of these; the API exposes them as filter options.
WARSAW_DISTRICTS: tuple[str, ...] = (
    "Bemowo",
    "Białołęka",
    "Bielany",
    "Mokotów",
    "Ochota",
    "Praga-Południe",
    "Praga-Północ",
    "Rembertów",
    "Śródmieście",
    "Targówek",
    "Ursus",
    "Ursynów",
    "Wawer",
    "Wesoła",
    "Wilanów",
    "Włochy",
    "Wola",
    "Żoliborz",
)


class PriceRange(StrEnum):
    """Coarse price band for a salon, normalized from source signals."""

    BUDGET = "$"
    MODERATE = "$$"
    PREMIUM = "$$$"


class ServiceCategory(StrEnum):
    """Top-level grouping for the normalized service taxonomy."""

    HAIR = "hair"
    NAILS = "nails"
    BARBER = "barber"
    BROWS_LASHES = "brows_lashes"
    SPA = "spa"
    MAKEUP = "makeup"
    OTHER = "other"
