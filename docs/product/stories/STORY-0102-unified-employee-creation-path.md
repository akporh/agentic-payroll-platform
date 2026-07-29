# `STORY-0102` — Unified employee creation path via `employee_repo` (B2, Sprint 17)

**Origin code(s):** `PT-A1-22` · `EMP-B2`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-4` — Employee Lifecycle Management
**Feature:** `FEAT-4` — Employee records & CRUD
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

Not directly user-facing — this is an internal consistency fix ensuring the onboarding wizard and the standalone employee-creation API create employee records through the same code path.

## Problem addressed

`onboarding.py` (lines 451–598 per the story file) had inline raw SQL for employee creation, duplicating logic that now also lived in the new `employee_repo` (`STORY-0101` (was `PT-A1-21`)). Two independent code paths creating the same kind of row is a maintenance and correctness risk — a fix or validation rule added to one path silently would not apply to the other.

## Delivered behaviour

`onboarding.py`'s inline employee-creation SQL (lines 451–598) is replaced with calls into the same `employee_repo` used by the standalone employee CRUD API (`STORY-0101` (was `PT-A1-21`)). There is now exactly one code path that creates an `employee` row, regardless of whether it originates from the onboarding wizard or the Employees-page "Add Employee" flow.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track O era, item B2 in `docs/stories/sprint-17-employee-crud.md` ("B2: Replace inline employee SQL in `onboarding.py:451–598` with repo calls (BLK-5)").

## Implementation evidence

- `docs/stories/sprint-17-employee-crud.md` — B2 scope statement, referencing the specific pre-refactor line range in `onboarding.py`.
- Commit `0ed5bfb` (2026-05-27) — same commit as `STORY-0101` (was `PT-A1-21`); B1 and B2 were delivered together in Sprint 17 Track B.

## Test / review evidence

- `docs/test-reports/2026-05-27-sprint-17-full.md` — Check breakdown table: "B2 | — | 3 PASS | — | —" (3 static/compilation checks). The report's overall verdict for the full Sprint 17 batch (which B2 is part of) is PASS: 266 unit/integration tests passed, 0 failed.

## Decision references

- BLK-5 (blocking issue resolved as part of Sprint 17's "APPROVED WITH CONDITIONS" arch-council gate — `docs/stories/sprint-17-employee-crud.md`).
- `D-016` (`docs/programmes/product-traceability/decisions.md`) — authorises this story's migration into `docs/product/` as part of the Phase 4B confirmed-batch.

## Dependencies

Depends on `STORY-0101` (was `PT-A1-21`) (`employee_repo` must exist before `onboarding.py` can be refactored to call it) — both delivered in the same commit.

## Delivery sprint(s)

Sprint 17 (Track B), delivered 2026-05-27 (commit `0ed5bfb`).

## Delivery history

- 2026-05-27 — Sprint 17 — `onboarding.py` inline employee-creation SQL replaced with `employee_repo` calls (commit `0ed5bfb`); 3/3 static checks PASS per `docs/test-reports/2026-05-27-sprint-17-full.md`.
- 2026-07-15 — Phase 4B confirmed-batch migration into `docs/product/` (D-016).

## Unresolved questions

None.
