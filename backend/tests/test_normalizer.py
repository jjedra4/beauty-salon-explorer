"""Unit tests for the normalization stage."""

from pipeline.collectors.base import RawSalon
from pipeline.enrichment.normalizer import (
    SalonNormalizer,
    normalize_price_range,
    resolve_district,
)
from tests.fakes import FakeLLM


def _raw(**kwargs: object) -> RawSalon:
    base: dict[str, object] = {"source": "test", "source_id": "x", "name": "Salon"}
    base.update(kwargs)
    return RawSalon(**base)  # type: ignore[arg-type]


class TestResolveDistrict:
    def test_prefers_district_found_in_address(self) -> None:
        raw = _raw(address="ul. Puławska 1, Mokotów, Warszawa", district_hint="Ursynów")
        assert resolve_district(raw) == "Mokotów"

    def test_falls_back_to_hint_when_address_uninformative(self) -> None:
        raw = _raw(address="ul. Testowa 1, Warszawa", district_hint="Wola")
        assert resolve_district(raw) == "Wola"

    def test_defaults_to_centre_when_unknown(self) -> None:
        raw = _raw(address="somewhere", district_hint=None)
        assert resolve_district(raw) == "Śródmieście"


class TestNormalizePriceRange:
    def test_maps_known_levels(self) -> None:
        assert normalize_price_range("PRICE_LEVEL_INEXPENSIVE") == "$"
        assert normalize_price_range("PRICE_LEVEL_MODERATE") == "$$"
        assert normalize_price_range("PRICE_LEVEL_VERY_EXPENSIVE") == "$$$"

    def test_unknown_or_missing_is_none(self) -> None:
        assert normalize_price_range(None) is None
        assert normalize_price_range("PRICE_LEVEL_UNSPECIFIED") is None


class TestServiceClassification:
    def test_filters_invalid_slugs_and_dedupes(self) -> None:
        llm = FakeLLM(service_slugs=["hair-coloring", "not-a-real-slug", "hair-coloring"])
        result = SalonNormalizer(llm).normalize(_raw(raw_services_text="koloryzacja"))
        assert result.service_slugs == ["hair-coloring"]

    def test_defaults_to_other_when_nothing_valid(self) -> None:
        llm = FakeLLM(service_slugs=["nonsense"])
        result = SalonNormalizer(llm).normalize(_raw())
        assert result.service_slugs == ["other"]

    def test_strips_other_when_a_specific_slug_is_present(self) -> None:
        llm = FakeLLM(service_slugs=["manicure", "other"])
        result = SalonNormalizer(llm).normalize(_raw())
        assert result.service_slugs == ["manicure"]


class TestTypeFloor:
    def test_primary_category_floor_is_always_present(self) -> None:
        # The model returns nothing, but a barber_shop must still offer 'barber'.
        llm = FakeLLM(parse_fields={"service_slugs": [], "price_tier": "unknown"})
        result = SalonNormalizer(llm).normalize(_raw(primary_type="barber_shop"))
        assert "barber" in result.service_slugs

    def test_floor_merges_with_model_services_without_duplicates(self) -> None:
        llm = FakeLLM(
            parse_fields={"service_slugs": ["barber", "beard-trim"], "price_tier": "unknown"}
        )
        result = SalonNormalizer(llm).normalize(_raw(types=["barber_shop"]))
        assert result.service_slugs == ["barber", "beard-trim"]


class TestPriceInference:
    def test_uses_review_derived_tier_when_google_price_absent(self) -> None:
        llm = FakeLLM(parse_fields={"service_slugs": ["manicure"], "price_tier": "budget"})
        result = SalonNormalizer(llm).normalize(_raw(types=["nail_salon"]))
        assert result.price_range == "$"

    def test_prefers_google_price_level_over_review_tier(self) -> None:
        llm = FakeLLM(parse_fields={"service_slugs": ["manicure"], "price_tier": "budget"})
        result = SalonNormalizer(llm).normalize(_raw(price_level="PRICE_LEVEL_EXPENSIVE"))
        assert result.price_range == "$$$"

    def test_unknown_tier_yields_no_price(self) -> None:
        llm = FakeLLM(parse_fields={"service_slugs": ["manicure"], "price_tier": "unknown"})
        result = SalonNormalizer(llm).normalize(_raw())
        assert result.price_range is None
