"""Enrichment orchestration.

Ties the stages together in order: **dedup → normalize → summarize → embed**.
Dedup runs first so the (more expensive) LLM normalization and summarization
only process canonical records, not duplicates. All AI access is via injected
clients, so the whole flow is testable with in-memory fakes.
"""

from app.ai.base import EmbeddingClient, LLMClient
from app.core.logging import get_logger
from pipeline.collectors.base import RawSalon
from pipeline.enrichment.deduplicator import Deduplicator
from pipeline.enrichment.embedder import SalonEmbedder, build_search_text
from pipeline.enrichment.models import EnrichedSalon
from pipeline.enrichment.normalizer import SalonNormalizer
from pipeline.enrichment.summarizer import ReviewSummarizer

logger = get_logger(__name__)


def enrich_salons(
    raw_salons: list[RawSalon],
    *,
    llm: LLMClient,
    embedder: EmbeddingClient,
    similarity_threshold: float = 0.9,
) -> list[EnrichedSalon]:
    """Run the full enrichment pipeline over raw salons.

    Args:
        raw_salons: Records as collected from a source.
        llm: Client for normalization (service classification) + summarization.
        embedder: Client for dedup embeddings + search embeddings.
        similarity_threshold: Cosine threshold for treating salons as duplicates.

    Returns:
        Canonical, enriched salons with services, summaries, and embeddings.
    """
    if not raw_salons:
        return []

    clusters = Deduplicator(embedder, similarity_threshold=similarity_threshold).deduplicate(
        raw_salons
    )
    normalizer = SalonNormalizer(llm)
    summarizer = ReviewSummarizer(llm)

    enriched: list[EnrichedSalon] = []
    for cluster in clusters:
        raw = cluster.canonical
        normalized = normalizer.normalize(raw)
        summary = summarizer.summarize(raw.name, raw.reviews)
        enriched.append(
            EnrichedSalon(
                source=raw.source,
                source_id=raw.source_id,
                name=raw.name,
                address=raw.address or "",
                district=normalized.district,
                latitude=raw.latitude,
                longitude=raw.longitude,
                phone=raw.phone,
                website=raw.website,
                price_range=normalized.price_range,
                rating=raw.rating,
                review_count=raw.review_count,
                raw_services_text=raw.raw_services_text,
                review_summary=summary,
                service_slugs=normalized.service_slugs,
                merged_source_ids=cluster.merged_source_ids,
            )
        )

    # Batch-embed the search text for all canonical salons at once.
    search_texts = [
        build_search_text(e.name, e.district, e.service_slugs, e.review_summary) for e in enriched
    ]
    vectors = SalonEmbedder(embedder).embed_texts(search_texts)
    for salon, vector in zip(enriched, vectors, strict=True):
        salon.embedding = vector

    logger.info("Enriched %d canonical salons", len(enriched))
    return enriched
