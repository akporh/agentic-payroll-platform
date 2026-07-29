# `STORY-0115` — Employees table UX — start/end dates visible, column alignment, inactive styling

**Origin code(s):** `EMP-TABLE-1`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-4` — Employee Lifecycle Management
**Feature:** `FEAT-11` — Employee page UX
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

payroll operator

## Problem addressed

The employees table did not show contract dates, so the operator could not tell from the list who was newly hired or about to leave; column alignment and the styling of inactive employees made the table harder to scan than it needed to be.

## Delivered behaviour

Contract start and end dates are shown in the table, columns are aligned consistently, and inactive employees are styled distinctly.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-25a-employees-table-ux-fixes.md`.

## Implementation evidence

`frontend/src/pages/Employees.tsx` table columns and row styling.

## Test / review evidence

None dedicated — see `STORY-0113`.

## Decision references

Captured under D-024.

## Dependencies

`STORY-0099` — the earlier employee-page enhancements this extends.

## Delivery sprint(s)

Sprint 25 (2026-06-10).

## Delivery history

- Sprint 25 — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report for Sprint 25.
