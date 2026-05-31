# M6 — Frontend: listing, filter, detail

**Status:** ⏳ Planned

## Goal
Build the core browse experience: a listing page with filters and a detail
view, consuming the REST API via a typed client.

## Scope / deliverables
- Typed API client in `frontend/lib/` generated from the backend's
  `/openapi.json` (single source of truth for types).
- **Listing page** (`app/page.tsx`): responsive salon cards (name, district,
  rating, price range, service tags), pagination, and `district` / `service`
  filter controls (populated from `/districts`, `/services`).
- **Detail view** (`app/salons/[id]/page.tsx`): full info — address, phone,
  website, services, rating + review count, the **AI review summary**, and an
  optional map from lat/lng.
- Loading / empty / error states; clean reusable components.

## Key files
`frontend/lib/api.ts` (+ generated types), `frontend/components/SalonCard.tsx`,
`FilterBar.tsx`, `SalonDetail.tsx`, `app/page.tsx`, `app/salons/[id]/page.tsx`.

## Acceptance criteria
- [ ] Listing renders seeded salons with key info; pagination works.
- [ ] Filtering by district and by service works against the API.
- [ ] Clicking a salon opens its detail view with full info + AI summary.

## Tests
Component tests (Vitest + Testing Library) for `SalonCard`, `FilterBar`, and
the detail view, with the API client mocked.

## Notes
Heed Next.js 16 conventions (see `frontend/AGENTS.md`); prefer Server
Components for data fetching, Client Components only where interactivity needs.
