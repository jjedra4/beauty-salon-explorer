"""In-memory fake AI clients for tests.

These implement the :mod:`app.ai.base` protocols so the enrichment pipeline can
be exercised deterministically and offline, with no OpenAI calls.
"""

from collections.abc import Callable

from app.ai.base import SchemaT


class FakeEmbedder:
    """Deterministic embedder producing one-hot vectors per distinct key.

    Texts mapping to the same ``key`` get identical vectors (cosine 1.0); texts
    with different keys get orthogonal vectors (cosine 0.0). This gives tests
    precise control over which records are treated as duplicates.
    """

    def __init__(self, dim: int = 16, key: Callable[[str], str] | None = None) -> None:
        self._dim = dim
        self._key = key or (lambda text: text)
        self._keys: dict[str, int] = {}

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(text) for text in texts]

    def _vector(self, text: str) -> list[float]:
        bucket = self._keys.setdefault(self._key(text), len(self._keys))
        vector = [0.0] * self._dim
        vector[bucket % self._dim] = 1.0
        return vector


class FakeLLM:
    """A fake LLM returning canned structured + text completions.

    ``parse`` builds the requested schema from ``parse_fields``, keeping only
    keys the schema actually declares — so the same fake serves both the
    service-classification and the search-filter schemas.
    """

    def __init__(
        self,
        *,
        service_slugs: list[str] | None = None,
        parse_fields: dict[str, object] | None = None,
        summary: str = "Lovely salon. Pros: friendly. Cons: busy.",
    ) -> None:
        if parse_fields is not None:
            self._parse_fields = parse_fields
        else:
            slugs = service_slugs if service_slugs is not None else ["womens-haircut"]
            self._parse_fields = {"service_slugs": slugs}
        self._summary = summary

    def parse(self, *, system: str, user: str, schema: type[SchemaT]) -> SchemaT:
        fields = schema.model_fields
        data = {key: value for key, value in self._parse_fields.items() if key in fields}
        return schema(**data)

    def complete(self, *, system: str, user: str) -> str:
        return self._summary


class ConstantEmbedder:
    """An embedder that returns the same fixed vector for any input."""

    def __init__(self, vector: list[float]) -> None:
        self._vector = vector

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [list(self._vector) for _ in texts]
