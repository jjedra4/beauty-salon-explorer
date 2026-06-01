"""Unit tests for the OpenAI client adapter (no real API calls).

A stub stands in for the OpenAI SDK so we can verify request batching — OpenAI
rejects embedding requests with more than 2048 inputs, so `embed` must chunk.
"""

from dataclasses import dataclass

from app.ai.openai_client import OpenAIClient


@dataclass
class _Embedding:
    embedding: list[float]


class _EmbeddingsResource:
    def __init__(self, recorded_batch_sizes: list[int]) -> None:
        self._recorded = recorded_batch_sizes

    def create(self, *, model: str, input: list[str]):  # noqa: A002 - matches SDK kwarg
        self._recorded.append(len(input))
        return type("Response", (), {"data": [_Embedding([0.0]) for _ in input]})()


class _StubOpenAI:
    """Minimal stand-in exposing only `.embeddings.create`."""

    def __init__(self) -> None:
        self.batch_sizes: list[int] = []
        self.embeddings = _EmbeddingsResource(self.batch_sizes)


def _client(stub: _StubOpenAI) -> OpenAIClient:
    return OpenAIClient("key", chat_model="chat", embedding_model="embed", client=stub)  # type: ignore[arg-type]


def test_embed_empty_makes_no_request() -> None:
    stub = _StubOpenAI()
    assert _client(stub).embed([]) == []
    assert stub.batch_sizes == []


def test_embed_chunks_inputs_within_the_api_limit() -> None:
    stub = _StubOpenAI()
    vectors = _client(stub).embed([f"text-{i}" for i in range(2075)])

    assert len(vectors) == 2075
    # 2075 inputs -> batches of at most 1000: 1000 + 1000 + 75.
    assert stub.batch_sizes == [1000, 1000, 75]
    assert all(size <= 2048 for size in stub.batch_sizes)
