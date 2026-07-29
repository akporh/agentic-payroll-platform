# `STORY-0121` — Status toggle ACTIVE ↔ INACTIVE with a payroll-exclusion warning

**Origin code(s):** `PT-A1-34` · `EMP-STATUS-1`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-4` — Employee Lifecycle Management
**Feature:** `FEAT-9` — Employee status & lifecycle actions
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator; HR admin

## Problem addressed

Employee status could not be changed from the UI, and the payroll consequence of doing so — the engine excludes non-ACTIVE employees from runs — was not communicated anywhere.

## Delivered behaviour

An ACTIVE ↔ INACTIVE toggle with a warning stating that an INACTIVE employee will not appear in the next payroll run.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-26-employee-registration-status-management.md`, item EMP-STATUS-1.

## Implementation evidence

`frontend/src/pages/Employees.tsx` status action; employee status update route.

## Test / review evidence

`docs/test-reports/2026-06-11-sprint-26.md`

## Decision references

`CLAUDE.md` records the binding interpretation: an INACTIVE employee with a live contract is a **valid HR state** (suspension, maternity leave). Payroll ineligibility is a consequence of that status, not a data error, and no hard PATCH guard may be added to reject it — the UI warns instead. That warning is this story.

## Dependencies

`STORY-0123` — the row-level actions this sits among.

## Delivery sprint(s)

Sprint 26 (2026-06-11).

## Delivery history

- Sprint 26 — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
