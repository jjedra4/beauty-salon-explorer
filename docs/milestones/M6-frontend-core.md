# M6 — Frontend: listing, filter, detail

**Status:** ✅ Done

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
- [x] Listing renders seeded salons with key info; pagination works
      (URL-driven, SWR; `next build` + lint clean; serves 200).
- [x] Filtering by district and by service works against the API.
- [x] Detail view shows full info + AI summary + maps link (route serves 200).
- [~] Browser data-rendering is verified end-to-end by the M7 Playwright e2e.

## Notes on what shipped
- Client-side fetching with **SWR** (Docker-safe: the browser always calls
  `NEXT_PUBLIC_API_BASE_URL`, avoiding SSR-in-container dual-URL issues).
- Filter + pagination state lives in the URL (shareable, back-button works);
  the `SalonBrowser` reads `useSearchParams` inside a `<Suspense>` boundary.
- Typed client (`lib/api.ts` + `lib/types.ts`) mirrors the OpenAPI schema.
- The NL search bar is added in M7 (the browser already has the seam for it).

## Tests
Component tests (Vitest + Testing Library) for `SalonCard`, `FilterBar`, and
the detail view, with the API client mocked.

## Notes
Heed Next.js 16 conventions (see `frontend/AGENTS.md`); prefer Server
Components for data fetching, Client Components only where interactivity needs.
