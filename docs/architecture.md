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

_Defined in M1._ The core entity is `Salon` (with provenance, location,
contact, normalized services, an AI review summary, and a `pgvector` embedding)
related many-to-many to a normalized `Service` taxonomy.

## Key decisions

_Captured inline as ADR-style notes as milestones land._

- **Data source — Google Places API (New):** official and licensed, with the
  richest field coverage (ratings, reviews, phone, website, geo) and a
  reproducible query model. (M2)
- **Postgres + pgvector:** keeps relational data and vector search in one
  engine — simpler ops and a realistic path to scale. (M1/M5)

## Scaling to all of Poland

_Expanded in M8._ The collector Strategy pattern lets us add a collector per
region/city and fan out ingestion; pgvector + pagination keep reads bounded;
enrichment is batched and cacheable to control LLM cost.
