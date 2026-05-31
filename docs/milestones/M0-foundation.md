# M0 — Foundation & scaffolding

**Status:** ✅ Done

## Goal
Stand up the monorepo skeleton so every later milestone has a working,
one-command-runnable home: database, backend, frontend, tooling, and CI.

## Scope / deliverables
- Monorepo layout: `backend/`, `frontend/`, `docs/`, `.github/`.
- `docker-compose.yml` running **Postgres + pgvector**, the **FastAPI**
  backend, and the **Next.js** frontend.
- Backend skeleton: settings (`app/core/config.py`), logging, DB session,
  `GET /health`, FastAPI app factory, Dockerfile.
- Frontend skeleton: Next.js + TypeScript + Tailwind, branded landing page,
  standalone-output Dockerfile.
- DX: `Makefile`, `.env.example`, `.gitignore`, `.dockerignore`s.
- CI skeleton (`.github/workflows/ci.yml`): backend lint/type/test, frontend
  lint/build, docker build.
- Docs: `README.md`, `docs/architecture.md`, this milestone roadmap.

## Key files
- `docker-compose.yml`, `Makefile`, `.env.example`
- `backend/pyproject.toml`, `backend/app/main.py`, `backend/app/core/*`,
  `backend/app/api/health.py`
- `frontend/next.config.ts`, `frontend/app/page.tsx`, `frontend/Dockerfile`

## Acceptance criteria
- [x] `docker compose up --build` starts all three services.
- [x] `GET http://localhost:8000/health` → `200` `{status:"ok",database:true,...}`.
- [x] `http://localhost:3000` loads the branded landing page.
- [x] `make test` passes (backend health tests); `ruff`, `mypy`, `eslint`,
      `next build` all clean.

## Notes
- The app runs with **no API keys**; AI is reported as disabled via
  `health.ai_enabled` until a key is configured.
- Next.js scaffolded at **v16** (App Router, Tailwind v4). Its `AGENTS.md`
  flags breaking changes vs. older versions — consult bundled docs when
  building UI in M6/M7.
