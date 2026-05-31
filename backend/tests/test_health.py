"""Tests for the health endpoint.

These are pure unit tests: no database is required. When Postgres is
unreachable the endpoint must still respond 200 and report ``degraded`` so
orchestrators get a structured signal instead of a crash.
"""

from fastapi.testclient import TestClient


def test_health_returns_200_and_expected_shape(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"status", "database", "ai_enabled"}
    assert body["status"] in {"ok", "degraded"}
    assert isinstance(body["database"], bool)
    assert isinstance(body["ai_enabled"], bool)


def test_health_degrades_without_database(client: TestClient) -> None:
    # No Postgres is running in the unit-test environment, so readiness must
    # report the database as unavailable rather than raising.
    body = client.get("/health").json()
    assert body["database"] is False
    assert body["status"] == "degraded"
