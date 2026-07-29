# `STORY-0099` — Employee page enhancements: contract dates in list, colour-coded warnings (EMP-01+)

**Origin code(s):** `PT-A1-28` · `EMP-01+`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-4` — Employee Lifecycle Management
**Feature:** `FEAT-11` — Employee page UX
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

Payroll bureau operator reviewing the employee list to spot upcoming contract terminations and audit contract coverage.

## Problem addressed

The employee list showed no contract start/end dates — an operator managing a 177-person payroll had to open every individual record to see whether a contract was ending soon, making upcoming terminations easy to miss.

## Delivered behaviour

Both a Start Date and End Date column are visible on every employee-list row across all sections (Active, Unmatched, Ended). An employee with no end date shows "—" (not blank). An active employee with a future end date shows that date in amber (a scheduled-termination signal); an employee already in the Contract Ended section shows its end date in standard grey (historical, not a warning).

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/employee-page-enhancements.md`, "Story EMP-01 — Show Contract Start and End Dates in Employee List" (this is the first of a set of retrospectively-written stories in that file — EMP-01 is the one this discovery-document item names specifically; EMP-02 "Add a Single Employee" and further stories in the same file are separate items not claimed by this story record).

## Implementation evidence

- `docs/stories/employee-page-enhancements.md` — full EMP-01 acceptance criteria (colour rules, "—" placeholder, section-scoped colour logic).
- `frontend/src/pages/Employees.tsx`, `backend/api/routes/workspace.py`, `frontend/src/api/workspace.ts` — named as the implementation files in the story file's header ("Implemented in:").
- Commit `8a9d548` ("feat: employee page enhancements + nav UX improvements", 2026-05-26) — isolated via `git log --all --oneline --grep`.

## Test / review evidence

- No dedicated test report was found for this item in `docs/test-reports/` — the story file itself is dated "Delivered: 2026-05-26" and is documented retrospectively (i.e. written after the fact, in the same style as the other retrospective story files in `docs/stories/`), rather than through a pre-sprint story + dedicated test-report pair. This matches the discovery document's own note that this item's evidence is "`docs/stories/employee-page-enhancements.md` + files changed cited," not a test report.

## Decision references

- None recorded beyond routine execution.
- `D-016` (`docs/programmes/product-traceability/decisions.md`) — authorises this story's migration into `docs/product/` as part of the Phase 4B confirmed-batch.

## Dependencies

None. Additive display columns on the existing employee list; no other story's completion is a precondition.

## Delivery sprint(s)

Retrospective delivery increment, 2026-05-26 (commit `8a9d548`).

## Delivery history

- 2026-05-26 — retrospective delivery increment — contract start/end date columns + colour-coded warning logic added to the employee list (commit `8a9d548`); documented after the fact in `docs/stories/employee-page-enhancements.md`, no dedicated test report found.
- 2026-07-15 — Phase 4B confirmed-batch migration into `docs/product/` (D-016).

## Unresolved questions

This item's test/review evidence is a retrospective story file describing what was built, not a dedicated pre/post-delivery test report with pass/fail checks — weaker verification than the sprint-tracked items in this same batch (e.g. Track J, Sprint 11, Sprint 17), though the code paths named are genuine and match the current codebase's file structure. This is noted rather than silently treated as equivalent to a full test-report-backed item.
