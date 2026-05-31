"""Unit tests for the summarizer and search-text embedder helpers."""

from pipeline.enrichment.embedder import build_search_text
from pipeline.enrichment.summarizer import ReviewSummarizer
from tests.fakes import FakeLLM


class TestReviewSummarizer:
    def test_returns_none_without_reviews(self) -> None:
        assert ReviewSummarizer(FakeLLM()).summarize("Salon", []) is None

    def test_summarizes_when_reviews_present(self) -> None:
        summarizer = ReviewSummarizer(FakeLLM(summary="Great vibe. Pros: x. Cons: y."))
        result = summarizer.summarize("Salon", ["good", "fast"])
        assert result == "Great vibe. Pros: x. Cons: y."

    def test_blank_summary_becomes_none(self) -> None:
        assert ReviewSummarizer(FakeLLM(summary="   ")).summarize("Salon", ["good"]) is None


class TestBuildSearchText:
    def test_composes_known_parts(self) -> None:
        text = build_search_text(
            "Studio Hair", "Mokotów", ["hair-coloring", "balayage-highlights"], "Cosy place."
        )
        assert "Studio Hair" in text
        assert "District: Mokotów" in text
        assert "Hair coloring" in text
        assert "Balayage & highlights" in text
        assert "Cosy place." in text

    def test_skips_empty_sections(self) -> None:
        text = build_search_text("Bare Salon", "Wola", [], None)
        assert text == "Bare Salon. District: Wola"

    def test_ignores_unknown_slugs(self) -> None:
        text = build_search_text("X", "Wola", ["bogus"], None)
        assert "Services" not in text
