"""Top-level API router.

Aggregates every feature router into a single object that ``main.py`` mounts.
New endpoint modules are wired into the application by registering them here,
keeping :mod:`app.main` stable as the API grows.
"""

from fastapi import APIRouter

from app.api import health, meta, salons, search

api_router = APIRouter()
api_router.include_router(health.router)
# Search is registered before the salons router so `/salons/search` resolves
# before the `/salons/{salon_id}` path parameter.
api_router.include_router(search.router)
api_router.include_router(salons.router)
api_router.include_router(meta.router)
