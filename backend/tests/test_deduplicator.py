"""Unit tests for the deduplication stage."""

from pipeline.collectors.base import RawSalon
from pipeline.enrichment.deduplicator import Deduplicator, cluster_indices
from tests.fakes import FakeEmbedder


def _raw(source_id: str, name: str, **kwargs: object) -> RawSalon:
    return RawSalon(source="test", source_id=source_id, name=name, **kwargs)  # type: ignore[arg-type]


class TestClusterIndices:
    def test_groups_similar_vectors_with_similar_names(self) -> None:
        # 0 and 1 are identical vectors + similar names -> one cluster; 2 apart.
        embeddings = [[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]]
        names = ["Studio Hair", "Studio Hairs", "Nails World"]
        clusters = cluster_indices(
            embeddings, names, similarity_threshold=0.9, name_threshold=0.6
        )
        grouped = sorted(sorted(c) for c in clusters)
        assert grouped == [[0, 1], [2]]

    def test_name_guardrail_prevents_merge(self) -> None:
        # Identical vectors but very different names -> not merged.
        embeddings = [[1.0, 0.0], [1.0, 0.0]]
        names = ["Barber Joe", "Lashes by Zoe"]
        clusters = cluster_indices(
            embeddings, names, similarity_threshold=0.9, name_threshold=0.7
        )
        assert sorted(sorted(c) for c in clusters) == [[0], [1]]


class TestDeduplicator:
    def test_merges_duplicates_and_picks_canonical(self) -> None:
        # Two near-identical salons (same key) + one distinct.
        embedder = FakeEmbedder(key=lambda text: "".join(c for c in text.lower() if c.isalnum()))
        salons = [
            _raw("a", "Studio Hair", address="ul. Testowa 1", review_count=10, phone=None),
            _raw("b", "Studio Hair", address="ul. Testowa 1", review_count=200,
                 website="https://x.pl", reviews=["nice"]),
            _raw("c", "Nails World", address="ul. Inna 5", review_count=5),
        ]
        clusters = Deduplicator(embedder, similarity_threshold=0.9).deduplicate(salons)

        assert len(clusters) == 2
        merged = next(c for c in clusters if c.merged_source_ids)
        # Canonical is the most-reviewed of the duplicate pair (b).
        assert merged.canonical.source_id == "b"
        assert merged.merged_source_ids == ["a"]

    def test_backfills_missing_fields_from_duplicates(self) -> None:
        embedder = FakeEmbedder(key=lambda text: "dup")  # everything collides
        salons = [
            _raw("a", "Studio Hair", address="ul. Testowa 1", review_count=300, website=None),
            _raw("b", "Studio Hair", address="ul. Testowa 1", review_count=5,
                 website="https://x.pl", reviews=["great"]),
        ]
        clusters = Deduplicator(embedder).deduplicate(salons)
        assert len(clusters) == 1
        canonical = clusters[0].canonical
        assert canonical.source_id == "a"  # most reviewed
        assert canonical.website == "https://x.pl"  # backfilled from b
        assert canonical.reviews == ["great"]

    def test_empty_input(self) -> None:
        assert Deduplicator(FakeEmbedder()).deduplicate([]) == []
