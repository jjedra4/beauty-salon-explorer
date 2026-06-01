# 💇 Warsaw Beauty Salon Explorer

A full-stack application that collects hair & beauty salons across Warsaw,
serves them through a REST API, and presents them in a web UI where you can
**browse, filter, search in natural language, and edit** salon details.

Built for the **SumUp Warsaw Accelerator 2026** home task. AI is applied where
the task's hard problems actually live — **data quality** (LLM normalization +
embedding-based deduplication) and **discovery** (natural-language semantic
search + review summaries) — rather than bolted on.

| AI concierge (home) | Search results | Detail + AI summary |
| --- | --- | --- |
| ![Hero](docs/screenshots/hero.png) | ![Search](docs/screenshots/search.png) | ![Detail](docs/screenshots/detail.png) |

---

## Quick start

The app ships with a committed, AI-ready **seed dataset**, so it runs
end-to-end with **no API keys** — one command, and the database is migrated and
seeded automatically.

```bash
cp .env.example .env        # defaults work out of the box
docker compose up --build   # or: make up
```

| Service        | URL                            |
| -------------- | ------------------------------ |
| Frontend       | http://localhost:3000          |
| API (Swagger)  | http://localhost:8000/docs     |
| Health check   | http://localhost:8000/health   |

That's it — open http://localhost:3000. The home page is an **AI concierge**:
describe what you want in plain language and it routes you to ranked results.

## The UI

A search-first, editorial dark theme ("Warsaw After-Hours" — Fraunces /
Hanken Grotesk / Space Mono, a single neon accent, CSS-only motion):

- **`/` — Discover:** an oversized concierge prompt bar with example queries that
  type themselves out; submitting routes to the results page.
- **`/search` — Results:** large result tiles (rank, rating, services, and a
  relevance meter for semantic results) plus a badge showing which retrieval
  path ran (AI **Semantic** vs. **Keyword** fallback).
- **`/browse` — Directory:** the full catalogue with district/service filters
  and pagination.
- **`/salons/[id]` — Detail:** contact info, services, a map link, and the
  **AI-generated review summary**; edit any field inline (persists via the API).

## The AI approach (the differentiator)

AI is placed on the task's two hard problems, which map onto SumUp's grading
criteria:

1. **Data quality → an AI ingestion pipeline** (`backend/pipeline/`):
   - **LLM normalization**: messy, multilingual service text → a fixed,
     canonical taxonomy (the genuinely hard NLP task). District and price are
     resolved deterministically — AI is used only where it adds value.
   - **Embedding-based deduplication**: salons surfaced by overlapping searches
     are clustered by cosine similarity (guarded by name similarity) and merged
     into canonical records.
   - **Review summarization**: reviews → a short pros/cons + vibe blurb.
2. **Discovery → semantic search** (`backend/app/services/search_service.py`):
   the LLM extracts structured filters from the query, the query is embedded,
   and salons are ranked by `pgvector` cosine distance with the filters applied
   as hard constraints. Falls back to trigram keyword search with no key.

This spans classical ML (embeddings, similarity, vector retrieval) + applied
LLM (structured extraction, query understanding, summarization).

## Tech stack

| Layer     | Choice                                                                 |
| --------- | ---------------------------------------------------------------------- |
| Backend   | Python · FastAPI · SQLAlchemy 2 · Alembic                              |
| Database  | PostgreSQL + `pgvector` (relational data + vector search in one)       |
| AI        | OpenAI — `text-embedding-3-small` (search/dedup) + GPT (extraction)    |
| Frontend  | Next.js 16 (App Router) · TypeScript · Tailwind CSS · SWR             |
| Data      | Google Places API (New)                                                |
| Tooling   | Docker Compose · uv · ruff · mypy · pytest · ESLint · Vitest · Playwright |

## Enabling real data & live AI

The committed seed is realistic **synthetic** data so the app runs offline.
To use real salons and live semantic search, add keys to `.env`:

```bash
OPENAI_API_KEY=...          # enables LLM enrichment + semantic search
GOOGLE_MAPS_API_KEY=...        # enables live collection from Google Places
```

```bash
make pipeline   # collect from Google Places + AI-enrich -> writes the seed
make seed       # load the seed into the DB (generates embeddings if a key is set)
```

With only an `OPENAI_API_KEY`, `make seed` generates embeddings for the existing
seed, so **semantic search works on the demo data without a Google key**.

## API overview

Full interactive docs at `/docs`. Key endpoints:

| Method & path            | Description                                            |
| ------------------------ | ------------------------------------------------------ |
| `GET /salons`            | List (name, district, rating, price) + filters + pages |
| `GET /salons/{id}`       | Full salon details                                     |
| `PATCH /salons/{id}`     | Update a salon (validated, persisted)                  |
| `GET /salons/search?q=`  | Natural-language semantic search (keyword fallback)    |
| `GET /districts`         | Districts present in the data (for filters)            |
| `GET /services`          | Service taxonomy (for filters / editing)               |

## Development

```bash
make help          # list all tasks
make test          # backend (pytest) + frontend (vitest)
make lint          # ruff + mypy + eslint
make e2e           # Playwright end-to-end (needs the stack up)
make backend-dev   # uvicorn with autoreload
make frontend-dev  # next dev server
```

- **Backend tests** run against a dedicated `salon_test` database (created
  automatically) and never touch the app's data. OpenAI is faked in tests.
- **88%** backend line coverage; CI gates at 80%.
- **Tests**: 58 backend (unit + integration on real Postgres/pgvector),
  8 frontend component tests, 3 Playwright e2e specs.

## Project structure

```
backend/
  app/            FastAPI app — api/ services/ repositories/ models/ schemas/ ai/ core/
  pipeline/       ETL — collectors/ (Google Places) + enrichment/ (normalize, dedup, summarize, embed)
  alembic/        migrations          tests/  unit + integration
frontend/
  app/            App Router pages    components/  UI    lib/  typed API client
  __tests__/      component tests     e2e/  Playwright
docs/             architecture.md + milestones/ (M0–M8 build log) + screenshots/
```

## Technical solution & frameworks

- **Layered backend** (API → service → repository → ORM) with Pydantic DTOs
  distinct from SQLAlchemy models, and FastAPI dependency injection.
- **Strategy pattern** for data sources (`SalonCollector` → `GooglePlacesCollector`)
  and a provider abstraction for AI clients — both swappable, which is also how
  the project scales to new sources/regions.
- **Pipeline** as discrete, individually-tested stages (dedup → normalize →
  summarize → embed → load), with all AI access injected so it runs with
  in-memory fakes in tests.
- **Graceful degradation**: every AI feature has a non-AI fallback, so the app
  is fully functional with no API keys.
- One-command Docker run that migrates + seeds on startup; OpenAPI-typed API.

See [`docs/architecture.md`](docs/architecture.md) for diagrams, the data model,
and decision notes.

## Data quality & scaling to all of Poland

- **Messy / missing data** is handled by the enrichment pipeline: LLM
  normalization into a closed taxonomy (validated against known slugs),
  deterministic district/price resolution, embedding dedup with a name
  guardrail, nullable optional fields, and field back-filling when merging.
- **Scaling to Poland**: the collector Strategy pattern means new
  regions/sources are new collectors, not rewrites; ingestion is batched and
  the enriched output is cacheable; `pgvector` + pagination keep reads bounded;
  the same schema and API serve any city.

## What I'd improve with more time

- A conversational, tool-using salon-finder **agent** on top of the search API.
- **Multi-source** collection (e.g. Booksy + OSM) to exercise cross-source dedup
  on real overlapping records.
- LLM-response **caching** and batch embedding to cut pipeline cost/time.
- Hybrid search (blend vector + keyword scores) and a smarter keyword fallback.
- A map view with clustering; user accounts & auth; richer review handling.
- Generate the frontend's API types directly from the live OpenAPI schema in CI.

---

Built milestone by milestone — see [`docs/milestones/`](docs/milestones/) for the
full build log (M0–M8).
