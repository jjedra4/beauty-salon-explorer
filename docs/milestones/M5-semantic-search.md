# M5 — Semantic search API

**Status:** ✅ Done

## Goal
The flagship **product-thinking** feature: natural-language salon search that
combines LLM query understanding with vector retrieval — with a graceful
keyword fallback when no AI key is configured.

## Scope / deliverables
- `GET /salons/search?q=...` in `app/api/search.py` →
  `SearchService` (`app/services/search_service.py`):
  1. **Query understanding (LLM):** extract structured filters from free text
     (district, service, price, min rating) — e.g. *"tani fryzjer na Mokotowie
     robiący balayage"* → `{district: Mokotów, services: [coloring/balayage],
     price: low}`.
  2. **Vector retrieval:** embed the query, rank salons by `pgvector` cosine
     distance, applying the extracted filters as hard constraints.
  3. **Fallback:** when `OPENAI_API_KEY` is unset, fall back to keyword /
     trigram (`ILIKE` / `pg_trgm`) search so the endpoint always works.
- Results ranked, paginated, returned as `SalonSummary` + relevance score.

## Key files
`app/api/search.py`, `app/services/search_service.py`,
`app/ai/query_parser.py`, `app/repositories/salon_repository.py` (vector +
keyword queries).

## Acceptance criteria
- [x] NL query returns relevant, ranked results — vector ranking verified
      against seeded embeddings (integration test).
- [x] Keyword fallback returns results without a key (verified live + tests);
      also falls back when the data has no embeddings yet.
- [x] LLM-extracted filters (district/service/price/rating) applied as hard
      constraints (integration test).
- [x] `/salons/search` registered before `/salons/{id}` so it isn't shadowed.

## Note
The keyword fallback (trigram on name + service text) is intentionally simple —
it exists so the keyless demo always returns something. Semantic search is the
primary path and shines on real salon names once an `OPENAI_API_KEY` is set and
embeddings are generated (via `make seed` with a key, or `make pipeline`).

## Tests
Unit: query parser (mocked LLM) → expected filter structs. Integration: vector
ranking on seeded data; fallback path with AI disabled.
