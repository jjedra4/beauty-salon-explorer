"""Integration tests for semantic + keyword search (real Postgres + pgvector)."""

import pytest

from app.core.constants import EMBEDDING_DIM
from app.services.search_service import SearchService
from pipeline.enrichment.models import EnrichedSalon
from pipeline.seed import load_seed
from tests.fakes import ConstantEmbedder, FakeLLM

pytestmark = pytest.mark.integration


def _onehot(index: int) -> list[float]:
    vector = [0.0] * EMBEDDING_DIM
    vector[index] = 1.0
    return vector


def _salon(source_id: str, name: str, *, district: str = "Wola", **kwargs: object) -> EnrichedSalon:
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


class TestSemanticSearch:
    def test_ranks_by_vector_distance(self, api_client) -> None:
        _client, factory = api_client
        with factory() as session:
            load_seed(
                session,
                [
                    _salon("a", "Alpha", embedding=_onehot(0)),
                    _salon("b", "Beta", embedding=_onehot(1)),
                    _salon("c", "Gamma", embedding=_onehot(2)),
                ],
            )

        # Query embedding equals Beta's vector -> Beta ranks first.
        with factory() as session:
            service = SearchService(
                session,
                llm=FakeLLM(parse_fields={"service_slugs": []}),
                embedder=ConstantEmbedder(_onehot(1)),
            )
            outcome = service.search("anything")

        assert outcome.mode == "semantic"
        assert outcome.results[0][0].name == "Beta"

    def test_applies_extracted_filters(self, api_client) -> None:
        _client, factory = api_client
        with factory() as session:
            load_seed(
                session,
                [
                    _salon("a", "Mokotow Salon", district="Mokotów", embedding=_onehot(0)),
                    _salon("b", "Wola Salon", district="Wola", embedding=_onehot(0)),
                ],
            )

        # LLM extracts a district filter -> only Mokotów returned.
        with factory() as session:
            service = SearchService(
                session,
                llm=FakeLLM(parse_fields={"district": "Mokotów", "service_slugs": []}),
                embedder=ConstantEmbedder(_onehot(0)),
            )
            outcome = service.search("salon w Mokotowie")

        assert [s.name for s, _ in outcome.results] == ["Mokotow Salon"]


class TestKeywordFallback:
    def test_keyword_search_without_ai(self, api_client) -> None:
        _client, factory = api_client
        with factory() as session:
            load_seed(session, [_salon("a", "Barber Bros"), _salon("b", "Nail Palace")])

        with factory() as session:
            outcome = SearchService(session).search("Barber")  # no llm/embedder

        assert outcome.mode == "keyword"
        assert any(s.name == "Barber Bros" for s, _ in outcome.results)

    def test_falls_back_when_no_embeddings_present(self, api_client) -> None:
        _client, factory = api_client
        with factory() as session:
            # Salons without embeddings -> semantic finds nothing -> keyword.
            load_seed(session, [_salon("a", "Barber Bros", embedding=None)])

        with factory() as session:
            service = SearchService(
                session,
                llm=FakeLLM(parse_fields={"service_slugs": []}),
                embedder=ConstantEmbedder(_onehot(0)),
            )
            outcome = service.search("Barber")

        assert outcome.mode == "keyword"


class TestSearchEndpoint:
    def test_endpoint_keyword_mode(self, api_client, monkeypatch) -> None:
        client, factory = api_client
        # Force the keyword path regardless of any ambient OPENAI_API_KEY.
        monkeypatch.setattr("app.services.search_service.get_llm_client", lambda: None)
        monkeypatch.setattr("app.services.search_service.get_embedding_client", lambda: None)
        with factory() as session:
            load_seed(session, [_salon("a", "Barber Bros")])

        body = client.get("/salons/search", params={"q": "Barber"}).json()
        assert body["mode"] == "keyword"
        assert body["query"] == "Barber"
        assert body["items"][0]["name"] == "Barber Bros"
        assert 0.0 <= body["items"][0]["score"] <= 1.0

    def test_search_route_not_shadowed_by_detail(self, api_client, monkeypatch) -> None:
        client, _factory = api_client
        monkeypatch.setattr("app.services.search_service.get_llm_client", lambda: None)
        monkeypatch.setattr("app.services.search_service.get_embedding_client", lambda: None)
        # "/salons/search" must hit search (200), not "/salons/{id}" (422/404).
        response = client.get("/salons/search", params={"q": "x"})
        assert response.status_code == 200
