# `STORY-0107` — Mid-period hire warning in `AddEmployeeSlideOver`

**Origin code(s):** `PT-A1-26` · `EMP-UX-3`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-4` — Employee Lifecycle Management
**Feature:** `FEAT-11` — Employee page UX
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator

## Problem addressed

Registering an employee with a start date inside the current period has a pay consequence — proration — that the operator was given no signal about at the moment of entry.

## Delivered behaviour

A warning shown in the add-employee slide-over when the contract start date falls inside the current pay period.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-17-employee-ux.md`, item EMP-UX-3.

## Implementation evidence

`frontend/src/` `AddEmployeeSlideOver` date validation and warning.

## Test / review evidence

`docs/test-reports/2026-05-27-sprint-17-full.md`

## Decision references

None.

## Dependencies

`STORY-0005` and `STORY-0086` — the proration behaviour the warning is about.

## Delivery sprint(s)

Sprint 17.

## Delivery history

- Sprint 17 — delivered.
- Sprint 25 — contract start/end date fields reworked in the same slide-over (`STORY-0117`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
