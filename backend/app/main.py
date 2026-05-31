"""FastAPI application factory and entrypoint.

Run locally with::

    uvicorn app.main:app --reload

The OpenAPI/Swagger UI is served at ``/docs`` and the schema at
``/openapi.json`` — the latter is consumed by the frontend to generate a
typed API client.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    """Build and configure the FastAPI application.

    Using an explicit factory (rather than a module-level app built inline)
    keeps construction testable and side-effect-free until called.
    """
    configure_logging()

    app = FastAPI(
        title="Warsaw Beauty Salon Explorer API",
        description=(
            "REST API for browsing, searching, and editing Warsaw beauty "
            "salons, backed by an AI-enriched dataset."
        ),
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)
    register_exception_handlers(app)
    return app


app = create_app()
