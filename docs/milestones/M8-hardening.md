# M8 — Hardening, docs & demo

**Status:** ✅ Done

## Goal
Turn a working app into a polished, reviewable deliverable: tests green,
coverage gated, docs complete, demo ready.

## Scope / deliverables
- **Tests & coverage:** fill gaps; enforce a coverage threshold in CI for the
  backend; ensure frontend + e2e run in CI.
- **CI finalize:** build + (optionally) push images; cache deps; compose smoke
  test that hits `/health`.
- **README:** complete the three required sections — how to run, technical
  solution & tools, and *what I'd improve with more time*.
- **`docs/architecture.md`:** finalize diagrams, the data-model section, ADR
  notes, and the **"scale to all of Poland"** narrative.
- **Demo:** screenshots / short GIF in the README; verify a clean clone →
  `docker compose up` → working app on seed data.

## Acceptance criteria
- [x] Fresh `docker compose up` (clean volume) → entrypoint migrates + seeds 60
      salons; `/health` ok, `/salons` total 60, frontend 200. No keys, no steps.
- [x] `make test` and `make lint` pass; backend 88% coverage (gate 80%).
- [x] README answers all three required questions; architecture doc complete
      (data model, ADR notes, scale-to-Poland); demo screenshots captured.

## Notes on what shipped
- Tests use a dedicated `salon_test` database (auto-created), so they never
  touch the app's data.
- Backend Docker image runs `entrypoint.sh`: migrate → seed (idempotent) → API.
- CI: backend (lint/type/test + 80% gate on a pgvector service), frontend
  (lint/vitest/build), and a Playwright e2e job.
- Demo screenshots in `docs/screenshots/` (captured via Playwright).

## Discussion readiness (maps to SumUp's questions)
- **Why this source?** → Google Places (New): official, richest fields,
  reproducible (ADR note).
- **Messy/missing data?** → the M3 AI pipeline: LLM normalization + embedding
  dedup + nullable handling + fallbacks.
- **Scale to all of Poland?** → Strategy-pattern collectors per region, batched
  ingestion, pgvector + pagination, caching.

## Deferred (out of MVP scope)
Conversational agent, auth/users, booking, real-time map clustering,
multi-source dedup beyond Google Places — listed in the README.
