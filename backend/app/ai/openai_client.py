"""OpenAI implementation of the AI provider interfaces.

Wraps the OpenAI SDK behind :class:`~app.ai.base.LLMClient` and
:class:`~app.ai.base.EmbeddingClient`. Structured completions use OpenAI's
native structured-output parsing so the model returns a validated Pydantic
object rather than free-form JSON we have to parse defensively.
"""

from openai import OpenAI

from app.ai.base import SchemaT
from app.core.logging import get_logger

logger = get_logger(__name__)

# OpenAI's embeddings endpoint accepts at most 2048 inputs per request; stay
# comfortably under that (also keeps each request well within token limits).
_EMBED_BATCH_SIZE = 1000


class OpenAIClient:
    """Adapter over the OpenAI SDK for chat + embeddings."""

    def __init__(
        self,
        api_key: str,
        *,
        chat_model: str,
        embedding_model: str,
        client: OpenAI | None = None,
    ) -> None:
        # Bulk enrichment can saturate the per-minute token limit; let the SDK
        # ride out 429s with its exponential backoff (it honours Retry-After)
        # instead of surfacing the error to the pipeline.
        self._client = client or OpenAI(api_key=api_key, max_retries=8)
        self._chat_model = chat_model
        self._embedding_model = embedding_model

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed texts, chunking into requests within the API's batch limit."""
        vectors: list[list[float]] = []
        for start in range(0, len(texts), _EMBED_BATCH_SIZE):
            batch = texts[start : start + _EMBED_BATCH_SIZE]
            response = self._client.embeddings.create(model=self._embedding_model, input=batch)
            vectors.extend(item.embedding for item in response.data)
        return vectors

    def parse(self, *, system: str, user: str, schema: type[SchemaT]) -> SchemaT:
        """Return a structured completion validated against ``schema``."""
        completion = self._client.beta.chat.completions.parse(
            model=self._chat_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format=schema,
        )
        parsed = completion.choices[0].message.parsed
        if parsed is None:
            raise ValueError("OpenAI returned no parsed structured output")
        return parsed

    def complete(self, *, system: str, user: str) -> str:
        """Return a free-text completion."""
        completion = self._client.chat.completions.create(
            model=self._chat_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return completion.choices[0].message.content or ""
