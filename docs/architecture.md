# Architecture

> Living document. Sections are expanded as the corresponding milestones land.

## Overview

The system has three cooperating parts, plus an offline data pipeline:

```
                ┌─────────────────────────────────────────────────────┐
                │                   Offline (run once)                 │
   Google       │   pipeline/                                          │
   Places API ──┼──▶ collect ─▶ normalize ─▶ dedup ─▶ summarize ─▶     │
   (New)        │              (LLM)      (embeddings) (LLM)           │
                │                                       └─▶ embed ─▶ load │
                └───────────────────────────────────────────┬──────────┘
                                                             ▼
   Browser ──▶ Next.js frontend ──HTTP──▶ FastAPI backend ──▶ Postgres
   (Tailwind UI)                          (REST + OpenAPI)   (+ pgvector)
```

- **Pipeline** (`backend/pipeline/`) — collects raw salon data, then uses AI to
  clean it (normalize services into a taxonomy, infer districts/price bands),
  deduplicate near-identical listings via embeddings, summarize reviews, and
  generate search embeddings. Output is loaded into Postgres and exported as a
  committed seed so the app runs without re-collection.
- **Backend** (`backend/app/`) — a FastAPI REST API over the salon data, with
  auto-generated OpenAPI/Swagger. Layered: API → services → repositories → ORM.
- **Frontend** (`frontend/`) — a Next.js app for browsing, filtering,
  natural-language search, and editing salons.

## Layering & design patterns

| Concern              | Where                     | Pattern                          |
| -------------------- | ------------------------- | -------------------------------- |
| HTTP routing         | `app/api/`                | Thin controllers                 |
| Business logic       | `app/services/`           | Service layer                    |
| Data access          | `app/repositories/`       | Repository pattern               |
| Persistence model    | `app/models/`             | SQLAlchemy ORM                   |
| Transport contracts  | `app/schemas/`            | DTO (Pydantic), separate from ORM|
| Wiring               | `app/core/`, FastAPI `Depends` | Dependency injection        |
| Data sources         | `pipeline/collectors/`    | Strategy (pluggable collectors)  |
| AI providers         | `app/ai/`                 | Provider abstraction / adapter   |
| Ingestion            | `pipeline/`               | Pipeline / staged transforms     |

## Configuration

All configuration is centralised in `app/core/config.py` (pydantic-settings),
sourced from environment variables / `.env`. No module reads `os.environ`
directly. The app is designed to **degrade gracefully**: with no `OPENAI_API_KEY`
it still serves the seed data and falls back to keyword search.

## Data model

```
┌────────────────────────────┐         ┌──────────────────┐
│ salons                      │         │ services         │
│  id (PK)                    │  M : N  │  id (PK)         │
│  source, source_id (uniq)   │◀───────▶│  slug (uniq)     │
│  name, address, district    │ salon_  │  name            │
│  latitude, longitude        │ services│  category        │
│  phone, website             │         └──────────────────┘
│  price_range, rating, …     │
│  raw_services_text          │   raw, un-normalized text (transparency)
│  review_summary             │   LLM-generated
│  embedding  vector(1536)    │   pgvector — semantic search
│  created_at, updated_at     │
└────────────────────────────┘
```

- `Salon` carries **provenance** (`source` + `source_id`, unique together) so
  records are traceable and dedup is auditable.
- **Required** fields (name/address/district) are non-null; nice-to-haves
  (phone/website/price/rating) are nullable and handled gracefully everywhere.
- `embedding` is a `pgvector` column with an **HNSW** cosine index; `name` has a
  **pg_trgm** GIN index for the keyword fallback.
- Services are a **closed, normalized taxonomy** (`app/core/taxonomy.py`) joined
  many-to-many, so "filter/edit by service" is a clean join, not text matching.

## Key decisions (ADR-style notes)

- **Data source — Google Places API (New):** official and licensed, with the
  richest field coverage (ratings, reviews, phone, website, geo) and a
  reproducible query model (district grid × query terms). Alternatives: OSM
  (free but sparse), Booksy (most relevant but no public API / ToS concerns).
- **Postgres + pgvector:** relational data and vector search in one engine —
  simpler ops than a separate vector DB and a realistic path to scale.
- **AI only where it adds value:** district and price are resolved
  deterministically (reliable signals); the LLM is reserved for the genuinely
  hard task (service classification) and summarization. Every AI feature has a
  non-AI fallback, so the app runs with no keys.
- **Dedup before enrich:** deduplication runs first so the costlier LLM steps
  only process canonical records.
- **Committed synthetic seed + auto-seed on startup:** guarantees a working,
  keyless demo from a single `docker compose up`.

## Scaling to all of Poland

- **More sources/regions = more collectors**, not rewrites — the
  `SalonCollector` Strategy interface isolates source specifics; a city is just
  a different set of district centroids / query terms.
- **Batched, cacheable enrichment**: the pipeline is offline and idempotent;
  LLM/embedding calls can be cached and batched to bound cost and time.
- **Bounded reads**: `pgvector` (ANN index) + pagination keep list/search fast
  as the dataset grows; the same schema and API serve any city unchanged.
- **Operational path**: queue-based ingestion per region, scheduled refreshes,
  and provenance-based incremental updates (re-enrich only changed records).
