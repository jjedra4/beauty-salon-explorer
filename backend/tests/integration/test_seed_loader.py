"""Integration tests for the seed loader (real Postgres)."""

import pytest
from sqlalchemy.orm import Session

from app.repositories.salon_repository import SalonRepository
from pipeline.enrichment.models import EnrichedSalon
from pipeline.seed import load_seed
from tests.fakes import FakeEmbedder

pytestmark = pytest.mark.integration


def _enriched(source_id: str, name: str, **kwargs: object) -> EnrichedSalon:
    base: dict[str, object] = {
        "source": "synthetic",
        "source_id": source_id,
        "name": name,
        "address": "ul. Testowa 1, Mokotów, Warszawa",
        "district": "Mokotów",
        "service_slugs": ["hair-coloring", "womens-haircut"],
    }
    base.update(kwargs)
    return EnrichedSalon(**base)  # type: ignore[arg-type]


def test_load_seed_persists_salons_and_services(db_session: Session) -> None:
    records = [_enriched("s1", "Studio Alpha"), _enriched("s2", "Studio Beta")]

    loaded = load_seed(db_session, records)
    assert loaded == 2

    repo = SalonRepository(db_session)
    salon = repo.get_by_source("synthetic", "s1")
    assert salon is not None
    assert salon.name == "Studio Alpha"
    assert {s.slug for s in salon.services} == {"hair-coloring", "womens-haircut"}


def test_load_seed_is_idempotent_and_updates(db_session: Session) -> None:
    load_seed(db_session, [_enriched("s1", "Original Name")])
    load_seed(db_session, [_enriched("s1", "Updated Name")])

    repo = SalonRepository(db_session)
    _, total = repo.list_salons(district="Mokotów")
    assert total == 1  # upserted, not duplicated
    assert repo.get_by_source("synthetic", "s1").name == "Updated Name"  # type: ignore[union-attr]


def test_load_seed_generates_embeddings_when_embedder_present(db_session: Session) -> None:
    record = _enriched("s1", "Studio Alpha", embedding=None)
    load_seed(db_session, [record], FakeEmbedder(dim=1536))

    salon = SalonRepository(db_session).get_by_source("synthetic", "s1")
    assert salon is not None
    assert salon.embedding is not None
    assert len(salon.embedding) == 1536
