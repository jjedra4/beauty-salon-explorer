# 💇 Warsaw Beauty Salon Explorer

A full-stack application that collects hair & beauty salons across Warsaw,
serves them through a REST API, and presents them in a web UI where you can
**browse, search (in natural language), and edit** salon details.

Built for the **SumUp Warsaw Accelerator 2026** home task. AI is applied where
the task's hard problems actually live — **data quality** (LLM normalization +
embedding-based deduplication) and **discovery** (natural-language semantic
search) — rather than bolted on.

> **Status:** under active construction, milestone by milestone. See
> [`docs/milestones/`](docs/milestones/) for the roadmap and
> [`docs/architecture.md`](docs/architecture.md) for the design.

---

## Quick start

The app ships with a committed, AI-enriched **seed dataset**, so it runs
end-to-end with **no API keys**.

```bash
cp .env.example .env       # defaults work out of the box
docker compose up --build  # or: make up
```

Then open:

| Service        | URL                            |
| -------------- | ------------------------------ |
| Frontend       | http://localhost:3000          |
| API (Swagger)  | http://localhost:8000/docs     |
| Health check   | http://localhost:8000/health   |

Add an `OPENAI_API_KEY` to `.env` to enable **live** natural-language semantic
search; without it, search degrades gracefully to keyword matching.

## Tech stack

| Layer     | Choice                                                                 |
| --------- | ---------------------------------------------------------------------- |
| Backend   | Python · FastAPI · SQLAlchemy · Alembic                                |
| Database  | PostgreSQL + `pgvector` (relational data + vector search in one)       |
| AI        | OpenAI — `text-embedding-3-small` (search/dedup) + GPT (extraction)    |
| Frontend  | Next.js (App Router) · TypeScript · Tailwind CSS                       |
| Data      | Google Places API (New)                                                |
| Tooling   | Docker Compose · uv · ruff · mypy · pytest · ESLint                    |

## Development

```bash
make help          # list all tasks
make test          # backend + frontend test suites
make lint          # ruff + mypy + eslint
make backend-dev   # uvicorn with autoreload (needs local Postgres)
make frontend-dev  # next dev server
```

## Documentation

- [`docs/architecture.md`](docs/architecture.md) — system design, data model,
  key decisions, and how this scales to all of Poland.
- [`docs/milestones/`](docs/milestones/) — the milestone-by-milestone build log.

## What I'd improve with more time

_Filled in at M8 — see the milestone roadmap for the deferred scope (e.g.
conversational agent, multi-source dedup, auth, map clustering)._
