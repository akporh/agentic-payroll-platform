# `STORY-0075` — `shift_type` and `salary_basis` added to `_period_context` trace header

**Origin code(s):** `PT-A7-05` · `AUD-4` · `Q4`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-1` — Correctness, Audit & Snapshot
**Feature:** `FEAT-1` — Payroll calculation trace auditability
**Classification:** `operational story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

auditor

## Problem addressed

Shift-gated overtime makes an employee's `shift_type` and `salary_basis` determinants of their pay, but neither was recorded in the trace — so a shift-gated result could not be explained from stored data.

## Delivered behaviour

`shift_type` and `salary_basis` are carried in the per-employee `_period_context` trace header.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track Q register, AUD-4 / Q4 — raised and resolved in the same sprint.

## Implementation evidence

`_period_context` construction in the run start path; per-employee context assembly.

## Test / review evidence

`docs/audit/2026-05-02-sprint-11-audit-review.md`, `docs/test-reports/2026-05-02-sprint-11.md`.

## Decision references

None.

## Dependencies

`STORY-0073` — the shift-gated OT rule that makes these fields determinative.

## Delivery sprint(s)

Sprint 11.

## Delivery history

- Sprint 11 — raised as audit finding AUD-4 and fixed within the same sprint.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None. `PT-Q-04` is the Track Q register's duplicate code for this same item, and resolves to `STORY-0075`.
