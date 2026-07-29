# `STORY-0104` — Fix the LATERAL join in the readiness service for multi-contract employees

**Origin code(s):** `PT-A1-24` · `EMP-B0a`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-4` — Employee Lifecycle Management
**Feature:** `FEAT-8` — Enrollment & payroll readiness
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

payroll operator

## Problem addressed

The readiness query's LATERAL join picked the wrong contract row for an employee holding more than one, so payroll readiness was assessed against a contract that was not the live one.

## Delivered behaviour

The LATERAL join is corrected to select the applicable contract, so readiness reflects the employee's live contract.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-17-employee-crud.md`, item B0a.

## Implementation evidence

Readiness query in the employee readiness service.

## Test / review evidence

`docs/test-reports/2026-05-27-sprint-17-full.md` — B0a verified.

## Decision references

`STORY-0104` was split from `PT-A1-24` under D-023 (OQ-8) because the original item carried mixed confidence across its two halves. The split is vindicated by the halves belonging to different features — this one to enrollment and readiness, its sibling to timesheet derivation.

## Dependencies

`STORY-0105` — the sibling half of the same original item.

## Delivery sprint(s)

Sprint 17.

## Delivery history

- Sprint 17 — delivered and verified.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None for this half. Its sibling `STORY-0105` remains unverified.
