"""Integration tests for the salon REST API (real Postgres, seeded per test)."""

import pytest
from sqlalchemy.orm import sessionmaker

from pipeline.enrichment.models import EnrichedSalon
from pipeline.seed import load_seed

pytestmark = pytest.mark.integration


def _seed(session_factory: sessionmaker, records: list[EnrichedSalon]) -> None:
    with session_factory() as session:
        load_seed(session, records)


def _salon(source_id: str, name: str, district: str, **kwargs: object) -> EnrichedSalon:
    base: dict[str, object] = {
        "source": "synthetic",
        "source_id": source_id,
        "name": name,
        "address": f"ul. Testowa 1, {district}, Warszawa",
        "district": district,
        "service_slugs": ["hair-coloring"],
    }
    base.update(kwargs)
    return EnrichedSalon(**base)  # type: ignore[arg-type]


class TestListSalons:
    def test_lists_with_pagination_metadata(self, api_client) -> None:
        client, factory = api_client
        _seed(factory, [_salon(f"s{i}", f"Salon {i}", "Mokotów") for i in range(3)])

        body = client.get("/salons", params={"limit": 2}).json()
        assert body["total"] == 3
        assert len(body["items"]) == 2
        assert body["limit"] == 2 and body["offset"] == 0
        assert set(body["items"][0]) >= {"id", "name", "district", "rating", "price_range"}

    def test_filters_by_district(self, api_client) -> None:
        client, factory = api_client
        _seed(factory, [_salon("a", "A", "Mokotów"), _salon("b", "B", "Wola")])

        body = client.get("/salons", params={"district": "Wola"}).json()
        assert body["total"] == 1
        assert body["items"][0]["name"] == "B"

    def test_filters_by_service(self, api_client) -> None:
        client, factory = api_client
        _seed(
            factory,
            [
                _salon("a", "Color", "Wola", service_slugs=["hair-coloring"]),
                _salon("b", "Nails", "Wola", service_slugs=["manicure"]),
            ],
        )
        body = client.get("/salons", params={"service": "manicure"}).json()
        assert [s["name"] for s in body["items"]] == ["Nails"]


class TestSalonDetail:
    def test_returns_full_detail(self, api_client) -> None:
        client, factory = api_client
        _seed(factory, [_salon("a", "Studio", "Ochota", phone="+48 111", review_summary="Nice.")])

        salon_id = client.get("/salons").json()["items"][0]["id"]
        body = client.get(f"/salons/{salon_id}").json()
        assert body["name"] == "Studio"
        assert body["address"].startswith("ul. Testowa 1")
        assert body["phone"] == "+48 111"
        assert body["review_summary"] == "Nice."
        assert body["services"][0]["slug"] == "hair-coloring"

    def test_missing_salon_returns_404(self, api_client) -> None:
        client, _ = api_client
        response = client.get("/salons/999999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestUpdateSalon:
    def test_patch_persists_changes(self, api_client) -> None:
        client, factory = api_client
        _seed(factory, [_salon("a", "Old Name", "Wola")])
        salon_id = client.get("/salons").json()["items"][0]["id"]

        response = client.patch(
            f"/salons/{salon_id}",
            json={"name": "New Name", "phone": "+48 222", "service_slugs": ["manicure"]},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "New Name"

        # Re-fetch to confirm persistence.
        refetched = client.get(f"/salons/{salon_id}").json()
        assert refetched["name"] == "New Name"
        assert refetched["phone"] == "+48 222"
        assert [s["slug"] for s in refetched["services"]] == ["manicure"]

    def test_patch_unknown_district_is_400(self, api_client) -> None:
        client, factory = api_client
        _seed(factory, [_salon("a", "A", "Wola")])
        salon_id = client.get("/salons").json()["items"][0]["id"]

        response = client.patch(f"/salons/{salon_id}", json={"district": "Atlantis"})
        assert response.status_code == 400

    def test_patch_unknown_service_is_400(self, api_client) -> None:
        client, factory = api_client
        _seed(factory, [_salon("a", "A", "Wola")])
        salon_id = client.get("/salons").json()["items"][0]["id"]

        response = client.patch(f"/salons/{salon_id}", json={"service_slugs": ["bogus"]})
        assert response.status_code == 400

    def test_patch_rejects_unknown_field(self, api_client) -> None:
        client, factory = api_client
        _seed(factory, [_salon("a", "A", "Wola")])
        salon_id = client.get("/salons").json()["items"][0]["id"]

        response = client.patch(f"/salons/{salon_id}", json={"unknown": "x"})
        assert response.status_code == 422  # extra="forbid"


class TestMetaEndpoints:
    def test_districts_and_services(self, api_client) -> None:
        client, factory = api_client
        _seed(factory, [_salon("a", "A", "Wola", service_slugs=["hair-coloring", "manicure"])])

        assert client.get("/districts").json() == ["Wola"]
        services = client.get("/services").json()
        slugs = {s["slug"] for s in services}
        assert {"hair-coloring", "manicure"} <= slugs
