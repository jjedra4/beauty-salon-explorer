"""Application configuration.

All runtime configuration is centralised here and loaded from environment
variables (or a local `.env` file) via pydantic-settings. Importing the
module-level :data:`settings` singleton gives every other module a single,
validated source of truth — nothing else should read ``os.environ`` directly.
"""

from functools import lru_cache

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings.

    Values are read from the process environment first, falling back to a
    `.env` file at the repository root. Unknown variables are ignored so the
    same `.env` can be shared with the frontend and docker-compose.
    """

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Database ---
    postgres_user: str = "salon"
    postgres_password: str = "salon"
    postgres_db: str = "salon"
    postgres_host: str = "db"
    postgres_port: int = 5432

    # --- Backend behaviour ---
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"

    # --- AI providers (optional; app degrades gracefully without them) ---
    openai_api_key: str | None = Field(default=None)
    openai_chat_model: str = "gpt-5.4-nano"
    openai_embedding_model: str = "text-embedding-3-small"
    google_maps_api_key: str | None = Field(default=None)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        """SQLAlchemy connection URL for the configured Postgres instance."""
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origin_list(self) -> list[str]:
        """CORS origins parsed from the comma-separated env value."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def ai_enabled(self) -> bool:
        """Whether live AI calls are possible (an OpenAI key is configured)."""
        return bool(self.openai_api_key)


@lru_cache
def get_settings() -> Settings:
    """Return the cached settings singleton.

    Wrapped in :func:`lru_cache` so the environment is parsed once per process
    and so tests can override it via dependency injection.
    """
    return Settings()


settings = get_settings()
