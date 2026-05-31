# M1 — Domain model & persistence

**Status:** ✅ Done

## Goal
Model the domain and make it persistable: ORM entities, migrations (incl. the
`pgvector` extension), a repository layer, and Pydantic DTOs.

## Scope / deliverables
- SQLAlchemy models in `app/models/`:
  - `Salon` — `id`, `source` + `source_id` (provenance), `name`, `address`,
    `district`, `lat`/`lng`, `phone?`, `website?`, `price_range?`, `rating?`,
    `review_count?`, `raw_services_text`, `review_summary?`, `embedding`
    (`Vector`), `created_at`, `updated_at`, dedup fields.
  - `Service` — normalized taxonomy; many-to-many `Salon ↔ Service`.
- Alembic configured; initial migration creates tables + `CREATE EXTENSION
  vector` + an ivfflat/hnsw index on `embedding`.
- Repository layer (`app/repositories/`) — `SalonRepository` with typed CRUD +
  list/filter; isolates SQLAlchemy from services.
- Pydantic schemas (`app/schemas/`) — `SalonSummary`, `SalonDetail`,
  `SalonUpdate`, `ServiceRead`.

## Key files
`app/models/salon.py`, `app/models/service.py`, `app/repositories/salon_repository.py`,
`app/schemas/salon.py`, `alembic/`, `alembic.ini`.

## Acceptance criteria
- [x] `make migrate` applies cleanly against the compose Postgres.
- [x] Repository CRUD + filter covered by tests (integration, real Postgres).
- [x] `pgvector` column + index created by the migration.

## Tests
Integration tests for `SalonRepository` (create/get/list/filter/update) against
a Postgres test database; schema (de)serialization unit tests.
