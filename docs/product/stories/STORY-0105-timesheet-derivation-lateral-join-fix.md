# `STORY-0105` — Fix the LATERAL join in timesheet derivation — multi-contract verification BLOCKED

**Origin code(s):** `PT-A1-24` · `EMP-B0b`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-5` — Pay Events & Inputs
**Feature:** `FEAT-13` — Timesheet capture & derivation
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `tentative`

## Actor

payroll operator

## Problem addressed

The same wrong-contract LATERAL join defect as `STORY-0104`, in the timesheet derivation path — where selecting the wrong contract changes the employee's derived payable hours.

## Delivered behaviour

The LATERAL join in timesheet derivation is corrected in the same shape as the readiness fix.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-17-employee-crud.md`, item B0b.

## Implementation evidence

Contract join in `backend/application/timesheet_derivation_service.py`.

## Test / review evidence

`docs/test-reports/2026-05-27-sprint-17-full.md` — **B0b multi-contract verification recorded as BLOCKED: the test data required to exercise a multi-contract employee through derivation did not exist.**

## Decision references

Split from `PT-A1-24` under D-023 (OQ-8) — see `STORY-0104`.

## Dependencies

`STORY-0104` — the sibling half; `STORY-0091` — the derivation path being corrected.

## Delivery sprint(s)

Sprint 17.

## Delivery history

- Sprint 17 — fix applied; verification blocked for want of multi-contract test data.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

**The fix is applied but unverified.** Confidence is `tentative` for that reason, and constructing the multi-contract test data remains outstanding. Do not cite this item as evidence that multi-contract derivation is correct.
