"""Pydantic schemas for the health endpoint."""

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response body for ``GET /health``."""

    status: Literal["ok", "degraded"]
    database: bool
    ai_enabled: bool
