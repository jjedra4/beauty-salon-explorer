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
        self._client = client or OpenAI(api_key=api_key)
        self._chat_model = chat_model
        self._embedding_model = embedding_model

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts in a single request."""
        if not texts:
            return []
        response = self._client.embeddings.create(model=self._embedding_model, input=texts)
        return [item.embedding for item in response.data]

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
