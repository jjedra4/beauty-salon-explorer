# M4 — Backend REST API

**Status:** ✅ Done

## Goal
Expose the enriched data through a clean, documented REST API satisfying the
task's list / detail / modify requirements.

## Scope / deliverables
Endpoints (all under OpenAPI at `/docs`):
- `GET /salons` — list summaries (name, district, rating, price_range) with
  **pagination** + `district` / `service` filters.
- `GET /salons/{id}` — full details.
- `PATCH /salons/{id}` — partial update, persisted.
- `GET /districts`, `GET /services` — populate filter controls.
- `GET /health` — (from M0).

Layering: routers (`app/api/salons.py`) → `SalonService`
(`app/services/`) → `SalonRepository`. Centralized error handling
(404 / 422), structured logging, consistent error envelope.

## Key files
`app/api/salons.py`, `app/api/meta.py`, `app/services/salon_service.py`,
`app/schemas/salon.py` (extended), `app/core/errors.py`.

## Acceptance criteria
- [x] All endpoints work against the seeded DB and appear in Swagger
      (verified live: `/salons`, `/salons/{id}`, `/districts`, `/services`).
- [x] List endpoint paginates and filters correctly (district + service).
- [x] `PATCH` persists and round-trips; unknown field → 422; unknown
      district/service → 400; missing salon → 404.

## Tests
Integration tests per endpoint (seeded test DB): pagination, each filter,
update happy/error paths, OpenAPI schema presence.
