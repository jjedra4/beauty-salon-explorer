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
