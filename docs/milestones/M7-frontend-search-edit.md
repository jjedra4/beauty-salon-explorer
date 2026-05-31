# M7 — Frontend: NL search & edit

**Status:** ⏳ Planned

## Goal
Complete the product loop: a prominent natural-language search bar and inline
editing of salon details — then prove the whole flow with an end-to-end test.

## Scope / deliverables
- **NL search bar** (front and centre on the listing page) wired to
  `GET /salons/search`, with a sensible placeholder example and results state.
- **Edit mode** on the detail view: a form to modify fields, submitting via
  `PATCH /salons/{id}`, with optimistic update or refetch + success/error
  feedback and validation mirroring the API.
- One Playwright **e2e** test: list → search → open detail → edit → persisted.

## Key files
`frontend/components/SearchBar.tsx`, `EditSalonForm.tsx`,
`app/salons/[id]/edit` interaction, `frontend/e2e/salon-flow.spec.ts`,
Playwright config.

## Acceptance criteria
- [ ] Typing a natural-language query returns ranked results in the UI.
- [ ] Editing a salon saves and the change is visible after reload.
- [ ] Playwright e2e passes locally and in CI.

## Tests
Component tests for `SearchBar` and `EditSalonForm`; one Playwright e2e for the
full journey.
