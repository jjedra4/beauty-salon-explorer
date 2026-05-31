"""Deduplication stage — semantic dedup via embeddings.

Overlapping searches (different districts/queries) surface the same salon under
slightly different names or formatting. We catch these by embedding
``name + address`` and clustering by cosine similarity, guarded by a string
name-similarity check so two genuinely different businesses at one address are
not merged. Each cluster collapses to a canonical record that absorbs the
others' provenance and any missing fields.

The clustering itself (:func:`cluster_indices`) is pure and unit-tested on
hand-crafted vectors; the embedding call is injected.
"""

from dataclasses import dataclass, field
from difflib import SequenceMatcher

import numpy as np

from app.ai.base import EmbeddingClient
from app.core.logging import get_logger
from pipeline.collectors.base import RawSalon

logger = get_logger(__name__)


@dataclass
class DedupCluster:
    """A canonical salon plus the source ids of records merged into it."""

    canonical: RawSalon
    merged_source_ids: list[str] = field(default_factory=list)


def _cosine_matrix(embeddings: list[list[float]]) -> np.ndarray:
    """Return the pairwise cosine-similarity matrix for row vectors."""
    arr = np.asarray(embeddings, dtype=float)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    normalized = arr / norms
    return normalized @ normalized.T


def _name_similarity(a: str, b: str) -> float:
    """Return a 0..1 string similarity between two names (case-insensitive)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def cluster_indices(
    embeddings: list[list[float]],
    names: list[str],
    *,
    similarity_threshold: float,
    name_threshold: float,
) -> list[list[int]]:
    """Group record indices into duplicate clusters via union-find.

    Two records are linked when their embeddings are at least
    ``similarity_threshold`` similar AND their names are at least
    ``name_threshold`` similar. Returns one list of indices per cluster.
    """
    n = len(embeddings)
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: int, y: int) -> None:
        parent[find(x)] = find(y)

    cosine = _cosine_matrix(embeddings)
    for i in range(n):
        for j in range(i + 1, n):
            if cosine[i, j] >= similarity_threshold and _name_similarity(
                names[i], names[j]
            ) >= name_threshold:
                union(i, j)

    clusters: dict[int, list[int]] = {}
    for i in range(n):
        clusters.setdefault(find(i), []).append(i)
    return list(clusters.values())


class Deduplicator:
    """Embedding-based salon deduplicator."""

    def __init__(
        self,
        embedder: EmbeddingClient,
        *,
        similarity_threshold: float = 0.9,
        name_threshold: float = 0.6,
    ) -> None:
        self._embedder = embedder
        self._similarity_threshold = similarity_threshold
        self._name_threshold = name_threshold

    def deduplicate(self, salons: list[RawSalon]) -> list[DedupCluster]:
        """Collapse near-duplicate salons into canonical clusters."""
        if not salons:
            return []

        texts = [f"{s.name} {s.address or ''}".strip() for s in salons]
        embeddings = self._embedder.embed(texts)
        names = [s.name for s in salons]
        groups = cluster_indices(
            embeddings,
            names,
            similarity_threshold=self._similarity_threshold,
            name_threshold=self._name_threshold,
        )

        clusters = [self._merge(salons, group) for group in groups]
        merged_away = sum(len(c.merged_source_ids) for c in clusters)
        logger.info(
            "Dedup: %d salons -> %d canonical (%d merged)",
            len(salons),
            len(clusters),
            merged_away,
        )
        return clusters

    @staticmethod
    def _merge(salons: list[RawSalon], group: list[int]) -> DedupCluster:
        """Merge a group of duplicate salons into one canonical record."""
        members = [salons[i] for i in group]
        # Canonical = most-reviewed (then highest-rated) record.
        canonical = max(members, key=lambda s: (s.review_count or 0, s.rating or 0.0))
        others = [s for s in members if s is not canonical]

        # Backfill missing optional fields from the other members.
        backfillable = ("address", "phone", "website", "latitude", "longitude", "rating")
        for other in others:
            for name in backfillable:
                if getattr(canonical, name) is None and getattr(other, name) is not None:
                    setattr(canonical, name, getattr(other, name))
            # Combine review snippets (deduplicated, order-preserving).
            canonical.reviews = list(dict.fromkeys(canonical.reviews + other.reviews))

        return DedupCluster(
            canonical=canonical,
            merged_source_ids=[s.source_id for s in others],
        )
