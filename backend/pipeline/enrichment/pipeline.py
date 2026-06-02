"""Enrichment orchestration.

Ties the stages together in order: **dedup → normalize → summarize → embed**.
Dedup runs first so the (more expensive) LLM normalization and summarization
only process canonical records, not duplicates. All AI access is via injected
clients, so the whole flow is testable with in-memory fakes.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed

from app.ai.base import EmbeddingClient, LLMClient
from app.core.logging import get_logger
from pipeline.collectors.base import RawSalon
from pipeline.enrichment.deduplicator import DedupCluster, Deduplicator
from pipeline.enrichment.embedder import SalonEmbedder, build_search_text
from pipeline.enrichment.models import EnrichedSalon
from pipeline.enrichment.normalizer import SalonNormalizer
from pipeline.enrichment.summarizer import ReviewSummarizer

logger = get_logger(__name__)

# Per-salon LLM calls are I/O-bound, so a modest thread pool turns a multi-hour
# sequential run into minutes. Kept low enough to stay near the model's
# per-minute token limit; the client's retry/backoff absorbs the rest.
_DEFAULT_WORKERS = 6


def _enrich_cluster(
    cluster: DedupCluster, normalizer: SalonNormalizer, summarizer: ReviewSummarizer
) -> EnrichedSalon:
    """Normalize + summarize one canonical salon. Failures degrade, never abort."""
    raw = cluster.canonical
    normalized = normalizer.normalize(raw)
    try:
        summary = summarizer.summarize(raw.name, raw.reviews)
    except Exception:  # noqa: BLE001 - one bad summary shouldn't kill the run
        logger.exception("Summarization failed for %s; leaving summary empty", raw.name)
        summary = None
    return EnrichedSalon(
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


def enrich_salons(
    raw_salons: list[RawSalon],
    *,
    llm: LLMClient,
    embedder: EmbeddingClient,
    similarity_threshold: float = 0.9,
    max_workers: int = _DEFAULT_WORKERS,
) -> list[EnrichedSalon]:
    """Run the full enrichment pipeline over raw salons.

    Args:
        raw_salons: Records as collected from a source.
        llm: Client for normalization (service classification) + summarization.
        embedder: Client for dedup embeddings + search embeddings.
        similarity_threshold: Cosine threshold for treating salons as duplicates.
        max_workers: Concurrency for the per-salon LLM calls.

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

    # Normalize + summarize concurrently, preserving cluster order in the output.
    enriched: list[EnrichedSalon | None] = [None] * len(clusters)
    with ThreadPoolExecutor(max_workers=min(max_workers, len(clusters))) as pool:
        futures = {
            pool.submit(_enrich_cluster, cluster, normalizer, summarizer): index
            for index, cluster in enumerate(clusters)
        }
        for done, future in enumerate(as_completed(futures), start=1):
            enriched[futures[future]] = future.result()
            if done % 200 == 0 or done == len(clusters):
                logger.info("Enriched %d/%d salons", done, len(clusters))
    salons = [salon for salon in enriched if salon is not None]

    # Batch-embed the search text for all canonical salons at once.
    search_texts = [
        build_search_text(s.name, s.district, s.service_slugs, s.review_summary) for s in salons
    ]
    vectors = SalonEmbedder(embedder).embed_texts(search_texts)
    for salon, vector in zip(salons, vectors, strict=True):
        salon.embedding = vector

    logger.info("Enriched %d canonical salons", len(salons))
    return salons
