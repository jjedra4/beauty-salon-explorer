"""AI provider interfaces.

The application depends on these small Protocols, not on the OpenAI SDK
directly. That keeps the provider swappable (a different LLM/embedding backend
is a new implementation, not a rewrite) and makes the pipeline trivially
testable with in-memory fakes.
"""

from typing import Protocol, TypeVar

from pydantic import BaseModel

SchemaT = TypeVar("SchemaT", bound=BaseModel)


class EmbeddingClient(Protocol):
    """Produces dense vector embeddings for text."""

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one embedding vector per input text, in order."""
        ...


class LLMClient(Protocol):
    """A chat LLM supporting free-text and structured (typed) completions."""

    def parse(self, *, system: str, user: str, schema: type[SchemaT]) -> SchemaT:
        """Return a structured completion validated against ``schema``."""
        ...

    def complete(self, *, system: str, user: str) -> str:
        """Return a free-text completion."""
        ...
