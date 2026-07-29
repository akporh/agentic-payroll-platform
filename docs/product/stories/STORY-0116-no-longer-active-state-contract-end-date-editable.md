# `STORY-0116` — "No longer active" state surfaced; contract end date editable

**Origin code(s):** `EMP-TABLE-2`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-4` — Employee Lifecycle Management
**Feature:** `FEAT-11` — Employee page UX
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

payroll operator; HR admin

## Problem addressed

An employee whose contract had ended looked the same as an active one in the list, and the end date could not be corrected once entered — so a leaver recorded with the wrong last paid day stayed wrong.

## Delivered behaviour

A "no longer active" state is surfaced in the table, and the contract end date is editable.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-25b-no-longer-active-ux.md`, `docs/stories/sprint-25c-edit-employee-contract-end-date.md`.

## Implementation evidence

`frontend/src/pages/Employees.tsx` state display; edit-employee slide-over end-date field.

## Test / review evidence

None dedicated — see `STORY-0113`.

## Decision references

`CLAUDE.md` records the binding semantics of the field being made editable: `employee_contract.end_date` is the **inclusive last paid day**, never the last physical day worked. Garden leave, notice buyout and suspension-before-exit are not modelled.

## Dependencies

`STORY-0115` — the same table rework; `STORY-0120` — the edit-employee surface.

## Delivery sprint(s)

Sprint 25 (2026-06-10).

## Delivery history

- Sprint 25 — delivered across two story files (25b, 25c).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report for Sprint 25. The absence of a `termination_reason` field is a known deferral recorded in `CLAUDE.md`, not addressed here.
