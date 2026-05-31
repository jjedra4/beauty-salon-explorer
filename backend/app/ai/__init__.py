"""AI provider factory.

Single place to obtain configured AI clients. Returns ``None`` when no API key
is set, so callers (search, pipeline) can degrade gracefully instead of
crashing — the app is designed to run keyless on seed data.
"""

from app.ai.base import EmbeddingClient, LLMClient
from app.ai.openai_client import OpenAIClient
from app.core.config import settings


def get_openai_client() -> OpenAIClient | None:
    """Return a configured OpenAI client, or ``None`` if no key is set."""
    if not settings.openai_api_key:
        return None
    return OpenAIClient(
        settings.openai_api_key,
        chat_model=settings.openai_chat_model,
        embedding_model=settings.openai_embedding_model,
    )


def get_llm_client() -> LLMClient | None:
    """Return an LLM client if AI is configured, else ``None``."""
    return get_openai_client()


def get_embedding_client() -> EmbeddingClient | None:
    """Return an embedding client if AI is configured, else ``None``."""
    return get_openai_client()


__all__ = [
    "EmbeddingClient",
    "LLMClient",
    "OpenAIClient",
    "get_embedding_client",
    "get_llm_client",
    "get_openai_client",
]
