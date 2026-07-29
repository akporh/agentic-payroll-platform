# `STORY-0101` — Employee CRUD API + D-ARCH-1 run-lock/backdating guard (B1, Sprint 17)

**Origin code(s):** `PT-A1-21` · `EMP-B1`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-4` — Employee Lifecycle Management
**Feature:** `FEAT-4` — Employee records & CRUD
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

Payroll operator managing an employee's HR record and contract history — name/status edits, and new contracts (grade/salary changes) over the employee's lifecycle.

## Problem addressed

There was no dedicated employee CRUD API with proper safeguards: editing an employee, or issuing a new contract, needed to be blocked while a payroll run was in-flight (to avoid corrupting an in-progress calculation) and needed to reject a new contract that would backdate before an existing one's coverage.

## Delivered behaviour

Six new employee-lifecycle endpoints (`GET /{wid}/employees/{eid}`, `PATCH /{wid}/employees/{eid}`, `POST /{wid}/employees/{eid}/contracts`, plus supporting reads) backed by a new `employee_repo`. `PATCH` validates `status` against an allowlist (422 with a specific message for invalid values). `POST .../contracts` enforces a backdating guard (422 if the new contract's `start_date` is not after the existing coverage) and, on success, closes the prior contract's `end_date` to the day before the new contract's `start_date` (append-only contract history). A D-ARCH-1 run-lock guard blocks contract changes with HTTP 409 while any run for the workspace is in-flight (`SUBMITTED | PROCESSING | CALCULATED | PARTIAL | APPROVED`).

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track O era, item B1 in `docs/stories/sprint-17-employee-crud.md` ("B1: New employee CRUD API (6 endpoints) + `employee_repo` — with run-lock and backdating guard"); arch-council status "APPROVED WITH CONDITIONS (2026-05-27) — all 6 blocking issues resolved."

## Implementation evidence

- `docs/stories/sprint-17-employee-crud.md` — full B1 scope and acceptance criteria; "Depends on: Nothing — no prior sprint dependency."
- Commit `0ed5bfb` ("feat: Sprint 17 — employee lifecycle refactor + UX corrections", 2026-05-27).

## Test / review evidence

- `docs/test-reports/2026-05-27-sprint-17-full.md` — B1 section: 13 live API checks executed against a running backend (workspace `fe0db67a`, employee `0d88966c`), all PASS, including: `GET .../{eid}` happy path (200), wrong-workspace 404, `PATCH` name update + restore, `PATCH` invalid status 422, `POST .../contracts` backdating-guard 422, invalid-salary-def 422, happy-path 201 creating a new contract, and confirmation that the old contract's `end_date` was set to `new_start − 1 day`. The D-ARCH-1 guard is specifically noted: "Tested against workspace `6b70612c` (has CALCULATED runs). `POST /employees/{eid}/contracts` returned HTTP 409... PASS." Overall report summary: 266 unit/integration tests passed, 1 skipped, 0 failed; 14/14 live API checks PASS; 13/13 static checks PASS.

## Decision references

- Arch-council: "APPROVED WITH CONDITIONS (2026-05-27) — all 6 blocking issues resolved" (`docs/stories/sprint-17-employee-crud.md`).
- D-ARCH-1 (run-lock guard, extended here from its original Track J salary-definition-edit scope to employee-contract changes).
- `D-016` (`docs/programmes/product-traceability/decisions.md`) — authorises this story's migration into `docs/product/` as part of the Phase 4B confirmed-batch.

## Dependencies

None upstream (the story file itself states "Depends on: Nothing"). It is a documented precondition for `STORY-0102` (was `PT-A1-22`) (unified creation path reusing this same `employee_repo`) and `STORY-0106` (was `PT-A1-25`) (the split Edit/Change-Grade UI that calls these endpoints).

## Delivery sprint(s)

Sprint 17 (Track B), delivered 2026-05-27 (commit `0ed5bfb`).

## Delivery history

- 2026-05-27 — Sprint 17 — employee CRUD API (6 endpoints) + `employee_repo` + D-ARCH-1 run-lock/backdating guard delivered (commit `0ed5bfb`); 14/14 live API checks PASS, 266/267 test suite PASS per `docs/test-reports/2026-05-27-sprint-17-full.md`.
- 2026-07-15 — Phase 4B confirmed-batch migration into `docs/product/` (D-016).

## Unresolved questions

None. (Two related Sprint 17 items — B3 browser SlideOver UAT and B0b multi-contract timesheet-derivation verification — were recorded as **BLOCKED**, not fully live-verified, in the same test report; neither is this story's own scope, and both are correctly excluded from this batch per the discovery document's own confidence downgrade for `STORY-0103` — not yet migrated, see `../ID-ALLOCATION.md` (was `PT-A1-23`)/`STORY-0104/0105` — not yet migrated, see `../ID-ALLOCATION.md` (was `PT-A1-24`).)
