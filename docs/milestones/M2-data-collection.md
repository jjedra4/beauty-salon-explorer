# M2 — Data collection

**Status:** ✅ Done

## Goal
Collect 100+ raw Warsaw salon records from Google Places (New), behind a
pluggable collector interface, with provenance preserved.

## Scope / deliverables
- `SalonCollector` Strategy interface (`pipeline/collectors/base.py`) and
  `GooglePlacesCollector` implementation.
- Warsaw coverage strategy: iterate the 18 dzielnice (district centroids) ×
  query terms (`fryzjer`, `salon kosmetyczny`, `barber`, `beauty salon`),
  paginate, then fetch Place Details with field masks.
- Raw records persisted as JSON under `backend/data/raw/` with `source` +
  `source_id` + fetched-at timestamp.
- Resilient HTTP: retries/backoff (`tenacity`), rate-limit handling, field
  masks to control cost.

## Key files
`pipeline/collectors/base.py`, `pipeline/collectors/google_places.py`,
`pipeline/collectors/warsaw_districts.py` (centroids), `pipeline/config.py`.

## Acceptance criteria
- [x] Runs without a key in tests (HTTP mocked with recorded fixtures).
- [x] Raw JSON stored with provenance (`pipeline/storage.py`).
- [~] Collector returns ≥100 de-duplicated-by-`source_id` raw salons given a
      key — mechanism (18 districts × 6 queries × paging, deduped) tested with
      fixtures; the live run is the user's `make pipeline` with a Google key.

## Tests
Unit tests with mocked Google Places responses (fixtures): parsing, pagination,
field mapping, retry on transient errors. No network in CI.

## Notes
Why Google Places (New): official/licensed, richest fields, reproducible query
model. Documented as an ADR note in `docs/architecture.md`.
