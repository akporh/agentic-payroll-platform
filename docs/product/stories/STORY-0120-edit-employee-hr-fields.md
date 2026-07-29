# `STORY-0120` — Edit employee — name, number, TIN, RSA, bank

**Origin code(s):** `PT-A1-33` · `EMP-EDIT-1`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-4` — Employee Lifecycle Management
**Feature:** `FEAT-4` — Employee records & CRUD
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator; HR admin

## Problem addressed

HR corrections — a misspelt name, a corrected TIN or RSA PIN, a changed bank account — had no editing surface, so a wrong record stayed wrong.

## Delivered behaviour

An edit form covering the HR fields: name, employee number, TIN, RSA PIN and bank details. Grade and salary changes are deliberately **not** on this form — they are a separate action (`STORY-0106`).

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-26-employee-registration-status-management.md`, item EMP-EDIT-1.

## Implementation evidence

`frontend/src/` edit-employee slide-over; employee update route.

## Test / review evidence

`docs/test-reports/2026-06-11-sprint-26.md`

## Decision references

Sprint 25's retro recorded that removing a field from a form must be checked against the backend's defaults, and that cross-field form consistency needs an explicit audit — both lessons arose on this surface.

## Dependencies

`STORY-0101` — the employee CRUD API and its D-ARCH-1 run-lock.

## Delivery sprint(s)

Sprint 26 (2026-06-11).

## Delivery history

- Sprint 26 — delivered.
- Sprint 25 — contract end date made editable here (`STORY-0116`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
