"""Search-embedding stage.

Builds a compact, information-dense text representation of each salon (name,
district, services, review summary) and embeds it. These vectors back the
semantic search in M5. The text-building is deterministic and unit-tested; the
embedding call is delegated to the injected client.
"""

from app.ai.base import EmbeddingClient
from app.core.taxonomy import SERVICE_BY_SLUG


def build_search_text(
    name: str,
    district: str,
    service_slugs: list[str],
    review_summary: str | None,
) -> str:
    """Compose the text that represents a salon for semantic search."""
    service_names = [SERVICE_BY_SLUG[s].name for s in service_slugs if s in SERVICE_BY_SLUG]
    parts = [
        name,
        f"District: {district}",
        f"Services: {', '.join(service_names)}" if service_names else "",
        review_summary or "",
    ]
    return ". ".join(part for part in parts if part)


class SalonEmbedder:
    """Generates search embeddings for salons in batches."""

    def __init__(self, embedder: EmbeddingClient) -> None:
        self._embedder = embedder

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of pre-built search texts."""
        return self._embedder.embed(texts)
