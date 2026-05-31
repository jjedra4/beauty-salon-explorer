# M3 — AI enrichment pipeline

**Status:** ✅ Done

## Goal
Turn messy raw records into a clean, deduplicated, enriched dataset — the
project's core **data-quality** story — and export it as a committed seed.

## Scope / deliverables
Staged transforms in `pipeline/enrichment/`, orchestrated by
`pipeline/run_pipeline.py`:
1. **Normalize (LLM structured output)** — map free-text/`types` → canonical
   `Service` taxonomy; normalize to one of Warsaw's 18 dzielnice; derive price
   band. Uses OpenAI structured outputs (JSON schema) for reliability.
2. **Deduplicate (embeddings)** — embed `name + address`, cosine-similarity
   cluster near-duplicates, fuzzy name/address guardrail, choose canonical +
   merge fields.
3. **Summarize reviews (LLM)** — pros/cons + one-line "vibe" per salon.
4. **Embed for search** — `name + district + services + summary` →
   `text-embedding-3-small` → `pgvector`.
5. **Load** — upsert into Postgres; export enriched seed to
   `backend/data/seed/salons.json` (committed) + a `pipeline/seed.py` loader.

## Key files
`pipeline/enrichment/normalizer.py`, `deduplicator.py`, `summarizer.py`,
`embedder.py`, `pipeline/run_pipeline.py`, `pipeline/seed.py`,
`app/ai/` (OpenAI client wrappers + provider abstraction).

## Acceptance criteria
- [x] Pipeline produces a clean, deduped, enriched dataset from raw input
      (`enrich_salons`, verified end-to-end with fake AI clients).
- [x] Enriched seed committed (`data/seed/salons.json`, 60 salons / 18
      districts); `make seed` loads it into a fresh DB (verified: 60 salons,
      19 services, 220 links).
- [x] Dedup + normalization logic unit-tested with mocked LLM + fixtures.

## Notes on what shipped
- Order is **dedup → normalize → summarize → embed** (dedup first so the LLM
  only processes canonical records — a cost optimization over the planned order).
- District + price are resolved deterministically; the LLM is used for the
  genuinely hard task (service classification), with output validated against
  the taxonomy.
- The committed seed is **synthetic** (`pipeline/synthetic_seed.py`,
  deterministic) so the app runs keyless; embeddings are `null` and generated
  on load when an OpenAI key is present. `make pipeline` replaces it with real
  Google Places data.

## Tests
Unit tests: dedup clustering on crafted near-duplicate fixtures; normalizer
output validation (mocked LLM); seed loader idempotency.

## Notes
Reproducibility: pipeline needs OpenAI + Google keys, but the committed seed
lets the app run fully offline. LLM responses cached to limit cost.
