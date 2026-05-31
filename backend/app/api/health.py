"""Health / readiness endpoint.

Exposes ``GET /health`` for container orchestration and uptime checks. The
endpoint reports liveness unconditionally and database readiness on a
best-effort basis so a failing DB surfaces as ``degraded`` rather than a hard
crash.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.schemas.health import HealthResponse

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)) -> HealthResponse:
    """Return service liveness, database readiness, and AI availability."""
    try:
        db.execute(text("SELECT 1"))
        database_ok = True
    except Exception:  # noqa: BLE001 - readiness check must never raise
        database_ok = False

    return HealthResponse(
        status="ok" if database_ok else "degraded",
        database=database_ok,
        ai_enabled=settings.ai_enabled,
    )
