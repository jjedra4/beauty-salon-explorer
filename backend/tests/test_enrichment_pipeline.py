"""Unit test for the full enrichment orchestration (with fake AI clients)."""

from pipeline.collectors.base import RawSalon
from pipeline.enrichment.pipeline import enrich_salons
from tests.fakes import FakeEmbedder, FakeLLM


def _raw(source_id: str, name: str, **kwargs: object) -> RawSalon:
    return RawSalon(source="google_places", source_id=source_id, name=name, **kwargs)  # type: ignore[arg-type]


def test_enrich_dedupes_normalizes_summarizes_and_embeds() -> None:
    llm = FakeLLM(service_slugs=["hair-coloring"], summary="Great. Pros: a. Cons: b.")
    embedder = FakeEmbedder(key=lambda text: "".join(c for c in text.lower() if c.isalnum()))

    raw = [
        _raw("a", "Studio Hair", address="ul. Testowa 1, Mokotów, Warszawa",
             review_count=10, reviews=["ok"], price_level="PRICE_LEVEL_MODERATE"),
        _raw("b", "Studio Hair", address="ul. Testowa 1, Mokotów, Warszawa",
             review_count=200, reviews=["love it"], price_level="PRICE_LEVEL_MODERATE"),
        _raw("c", "Barber Bros", address="ul. Wolska 5, Wola, Warszawa", review_count=50),
    ]

    enriched = enrich_salons(raw, llm=llm, embedder=embedder)

    # a + b deduped into one canonical record -> 2 salons total.
    assert len(enriched) == 2

    studio = next(s for s in enriched if s.name == "Studio Hair")
    assert studio.source_id == "b"  # most reviewed
    assert studio.merged_source_ids == ["a"]
    assert studio.district == "Mokotów"
    assert studio.price_range == "$$"
    assert studio.service_slugs == ["hair-coloring"]
    assert studio.review_summary == "Great. Pros: a. Cons: b."
    assert studio.embedding is not None and len(studio.embedding) == 16


def test_enrich_empty_returns_empty() -> None:
    assert enrich_salons([], llm=FakeLLM(), embedder=FakeEmbedder()) == []
