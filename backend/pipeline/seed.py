"""Load the committed enriched seed dataset into the database.

Run via ``python -m pipeline.seed`` (or ``make seed``). Idempotent: salons are
upserted by their ``(source, source_id)`` key, so re-running updates in place.

If the seed records have no embeddings (the committed seed ships without them)
and an OpenAI key is configured, embeddings are generated on load — that is how
semantic search can be enabled on the demo data with only an OpenAI key, no
Google key or re-collection required.
"""

from sqlalchemy.orm import Session

from app.ai import get_embedding_client
from app.ai.base import EmbeddingClient
from app.core.database import SessionLocal
from app.core.logging import configure_logging, get_logger
from app.core.taxonomy import SERVICE_BY_SLUG, SERVICE_TAXONOMY
from app.models.salon import Salon
from app.models.service import Service
from app.repositories.salon_repository import SalonRepository
from app.repositories.service_repository import ServiceRepository
from pipeline.enrichment.embedder import build_search_text
from pipeline.enrichment.models import EnrichedSalon
from pipeline.storage import read_enriched_salons

logger = get_logger(__name__)

# Salon fields copied verbatim from an EnrichedSalon record on upsert.
_COPIED_FIELDS = (
    "name",
    "address",
    "district",
    "latitude",
    "longitude",
    "phone",
    "website",
    "price_range",
    "rating",
    "review_count",
    "raw_services_text",
    "review_summary",
)


def _generate_missing_embeddings(
    records: list[EnrichedSalon], embedder: EmbeddingClient
) -> None:
    """Populate embeddings in place for records that lack them."""
    missing = [r for r in records if r.embedding is None]
    if not missing:
        return
    texts = [
        build_search_text(r.name, r.district, r.service_slugs, r.review_summary) for r in missing
    ]
    for record, vector in zip(missing, embedder.embed(texts), strict=True):
        record.embedding = vector
    logger.info("Generated embeddings for %d seed salons", len(missing))


def load_seed(
    session: Session,
    records: list[EnrichedSalon],
    embedder: EmbeddingClient | None = None,
) -> int:
    """Upsert enriched salons (and their services) into the database.

    Returns the number of salons loaded.
    """
    if embedder is not None:
        _generate_missing_embeddings(records, embedder)

    service_repo = ServiceRepository(session)
    salon_repo = SalonRepository(session)

    # Materialize the full taxonomy up front so every valid service is
    # available for filtering and editing, not just those a seeded salon uses.
    for definition in SERVICE_TAXONOMY:
        service_repo.get_or_create(definition.slug, definition.name, definition.category.value)

    for record in records:
        services = _resolve_services(service_repo, record.service_slugs)
        salon = salon_repo.get_by_source(record.source, record.source_id)
        if salon is None:
            salon = Salon(source=record.source, source_id=record.source_id)
            session.add(salon)
        for field in _COPIED_FIELDS:
            setattr(salon, field, getattr(record, field))
        if record.embedding is not None:
            salon.embedding = record.embedding
        salon.services = services

    session.commit()
    logger.info("Seeded %d salons", len(records))
    return len(records)


def _resolve_services(service_repo: ServiceRepository, slugs: list[str]) -> list[Service]:
    """Materialize taxonomy services for the given slugs (creating as needed)."""
    services: list[Service] = []
    for slug in slugs:
        definition = SERVICE_BY_SLUG.get(slug)
        if definition is None:
            continue
        services.append(
            service_repo.get_or_create(definition.slug, definition.name, definition.category.value)
        )
    return services


def main() -> None:
    """CLI entrypoint: read the seed file and load it into the database."""
    configure_logging()
    records = read_enriched_salons()
    with SessionLocal() as session:
        load_seed(session, records, get_embedding_client())


if __name__ == "__main__":
    main()
