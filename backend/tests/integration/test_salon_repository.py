"""Integration tests for the persistence layer.

These exercise the real SQLAlchemy models and repositories against a live
Postgres (with pgvector), verifying CRUD, filtering, pagination, and the
service taxonomy relationship.
"""

import pytest
from sqlalchemy.orm import Session

from app.models.salon import Salon
from app.repositories.salon_repository import SalonRepository
from app.repositories.service_repository import ServiceRepository

pytestmark = pytest.mark.integration


def _make_salon(source_id: str, name: str, district: str, **kwargs: object) -> Salon:
    """Build a Salon with sensible required-field defaults for tests."""
    return Salon(
        source="test",
        source_id=source_id,
        name=name,
        address=kwargs.get("address", "Test 1"),
        district=district,
        rating=kwargs.get("rating"),
        price_range=kwargs.get("price_range"),
    )


class TestSalonRepository:
    def test_add_and_get(self, db_session: Session) -> None:
        repo = SalonRepository(db_session)
        salon = repo.add(_make_salon("g1", "Studio Alpha", "Mokotów"))

        fetched = repo.get(salon.id)
        assert fetched is not None
        assert fetched.name == "Studio Alpha"
        assert fetched.district == "Mokotów"

    def test_get_missing_returns_none(self, db_session: Session) -> None:
        assert SalonRepository(db_session).get(999_999) is None

    def test_get_by_source(self, db_session: Session) -> None:
        repo = SalonRepository(db_session)
        repo.add(_make_salon("place-123", "Studio Beta", "Wola"))

        assert repo.get_by_source("test", "place-123") is not None
        assert repo.get_by_source("test", "nope") is None

    def test_list_filters_by_district_and_paginates(self, db_session: Session) -> None:
        repo = SalonRepository(db_session)
        for i in range(3):
            repo.add(_make_salon(f"m{i}", f"Mokotow Salon {i}", "Mokotów"))
        repo.add(_make_salon("w0", "Wola Salon", "Wola"))

        items, total = repo.list_salons(district="Mokotów", limit=2, offset=0)
        assert total == 3
        assert len(items) == 2
        assert all(s.district == "Mokotów" for s in items)

        page2, _ = repo.list_salons(district="Mokotów", limit=2, offset=2)
        assert len(page2) == 1

    def test_list_filters_by_service(self, db_session: Session) -> None:
        salon_repo = SalonRepository(db_session)
        service_repo = ServiceRepository(db_session)
        coloring = service_repo.get_or_create("hair-coloring", "Hair coloring", "hair")

        with_service = salon_repo.add(_make_salon("s1", "Color Studio", "Ochota"))
        with_service.services = [coloring]
        salon_repo.add(_make_salon("s2", "Plain Cuts", "Ochota"))
        db_session.flush()

        items, total = salon_repo.list_salons(service_slug="hair-coloring")
        assert total == 1
        assert items[0].name == "Color Studio"

    def test_apply_update_scalars_and_services(self, db_session: Session) -> None:
        salon_repo = SalonRepository(db_session)
        service_repo = ServiceRepository(db_session)
        manicure = service_repo.get_or_create("manicure", "Manicure", "nails")
        salon = salon_repo.add(_make_salon("u1", "Old Name", "Bielany"))

        salon_repo.apply_update(
            salon,
            values={"name": "New Name", "phone": "+48 111 222 333"},
            services=[manicure],
        )

        refreshed = salon_repo.get(salon.id)
        assert refreshed is not None
        assert refreshed.name == "New Name"
        assert refreshed.phone == "+48 111 222 333"
        assert [s.slug for s in refreshed.services] == ["manicure"]

    def test_list_districts_distinct_sorted(self, db_session: Session) -> None:
        repo = SalonRepository(db_session)
        repo.add(_make_salon("d1", "A", "Wola"))
        repo.add(_make_salon("d2", "B", "Mokotów"))
        repo.add(_make_salon("d3", "C", "Wola"))

        assert repo.list_districts() == ["Mokotów", "Wola"]


class TestServiceRepository:
    def test_get_or_create_is_idempotent(self, db_session: Session) -> None:
        repo = ServiceRepository(db_session)
        first = repo.get_or_create("barber", "Barber", "barber")
        second = repo.get_or_create("barber", "Barber", "barber")
        assert first.id == second.id

    def test_get_by_slugs(self, db_session: Session) -> None:
        repo = ServiceRepository(db_session)
        repo.get_or_create("manicure", "Manicure", "nails")
        repo.get_or_create("pedicure", "Pedicure", "nails")

        found = repo.get_by_slugs(["manicure", "pedicure", "missing"])
        assert {s.slug for s in found} == {"manicure", "pedicure"}
        assert repo.get_by_slugs([]) == []

    def test_list_all_ordered(self, db_session: Session) -> None:
        repo = ServiceRepository(db_session)
        repo.get_or_create("manicure", "Manicure", "nails")
        repo.get_or_create("haircut", "Haircut", "hair")
        services = repo.list_all()
        # Ordered by (category, name): hair before nails.
        categories = [s.category for s in services]
        assert categories == sorted(categories)
