"""Unit tests for LLM query understanding (filter extraction + sanitization)."""

from app.ai.query_parser import QueryParser
from tests.fakes import FakeLLM


def test_extracts_valid_filters() -> None:
    llm = FakeLLM(
        parse_fields={
            "district": "Mokotów",
            "service_slugs": ["hair-coloring", "balayage-highlights"],
            "price_range": "$",
            "min_rating": 4.5,
        }
    )
    filters = QueryParser(llm).parse("tani fryzjer na Mokotowie robiący balayage")

    assert filters.district == "Mokotów"
    assert filters.service_slugs == ["hair-coloring", "balayage-highlights"]
    assert filters.price_range == "$"
    assert filters.min_rating == 4.5


def test_sanitizes_invalid_values() -> None:
    llm = FakeLLM(
        parse_fields={
            "district": "Atlantis",          # not a Warsaw district -> dropped
            "service_slugs": ["bogus", "manicure", "manicure"],  # filtered + deduped
            "price_range": "£££",            # invalid band -> dropped
            "min_rating": 9.0,               # out of range -> clamped to 5.0
        }
    )
    filters = QueryParser(llm).parse("anything")

    assert filters.district is None
    assert filters.service_slugs == ["manicure"]
    assert filters.price_range is None
    assert filters.min_rating == 5.0
