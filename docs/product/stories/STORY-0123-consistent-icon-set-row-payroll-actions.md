# `STORY-0123` — Consistent icon set; payroll actions surfaced from the employee row

**Origin code(s):** `PT-A1-36` · `EMP-ICONS-1` · `EMP-PAYROLL-ACTIONS-1`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-4` — Employee Lifecycle Management
**Feature:** `FEAT-9` — Employee status & lifecycle actions
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator

## Problem addressed

Row actions used inconsistent icons and buried the payroll-relevant ones, so the operator had to open a record to perform an action that could have been offered in the list.

## Delivered behaviour

A consistent icon set across employee row actions, with the payroll actions surfaced directly from the row.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-26-employee-registration-status-management.md`, items EMP-ICONS-1 and EMP-PAYROLL-ACTIONS-1.

## Implementation evidence

`frontend/src/pages/Employees.tsx` row action set and icons.

## Test / review evidence

`docs/test-reports/2026-06-11-sprint-26.md`

## Decision references

Design-system icon conventions are recorded in `docs/design/ui-decisions.md`.

## Dependencies

`STORY-0103` — the split-action rework these actions sit within.

## Delivery sprint(s)

Sprint 26 (2026-06-11).

## Delivery history

- Sprint 26 — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
