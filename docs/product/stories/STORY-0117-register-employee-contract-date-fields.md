# `STORY-0117` — Register employee — contract start/end date fields in `AddEmployeeSlideOver`

**Origin code(s):** `EMP-TABLE-3`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-4` — Employee Lifecycle Management
**Feature:** `FEAT-4` — Employee records & CRUD
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

payroll operator; HR admin

## Problem addressed

Contract dates could not be entered when registering an employee, so every new record needed a second edit before it was usable for payroll.

## Delivered behaviour

Contract start and end date fields in the add-employee slide-over.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-25d-register-employee-contract-dates.md`.

## Implementation evidence

`frontend/src/` `AddEmployeeSlideOver` fields; `createEmployee` payload.

## Test / review evidence

None dedicated — see `STORY-0113`.

## Decision references

Consistent with the Upload/Enroll separation (`STORY-0109`): contract dates are HR data and belong on the upload/register path, not the enroll path.

## Dependencies

`STORY-0107` — the mid-period hire warning driven by the start date entered here.

## Delivery sprint(s)

Sprint 25 (2026-06-10).

## Delivery history

- Sprint 25 — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report for Sprint 25.
