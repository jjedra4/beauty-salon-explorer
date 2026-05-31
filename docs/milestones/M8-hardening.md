# M8 — Hardening, docs & demo

**Status:** ⏳ Planned

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
- [ ] Fresh clone + `cp .env.example .env` + `docker compose up` → fully working
      app on seed data, no keys required.
- [ ] `make test` and `make lint` pass; CI green end-to-end.
- [ ] README answers all three required questions; architecture doc complete.

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
