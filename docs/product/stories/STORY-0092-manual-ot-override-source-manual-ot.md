# `STORY-0092` — Manual overtime override, recorded with `source=MANUAL_OT`

**Origin code(s):** `PT-A3-09` · `TM-4`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-5` — Pay Events & Inputs
**Feature:** `FEAT-13` — Timesheet capture & derivation
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

payroll operator

## Problem addressed

Derived overtime is sometimes wrong for reasons the timesheet cannot express — an authorised exception, a correction agreed with the client. Without an override the operator's only recourse was to edit the source file and re-upload, destroying the original.

## Delivered behaviour

An operator may override derived overtime for an employee; the overridden value is stored with `source=MANUAL_OT` so the trace distinguishes a derived figure from a human one.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-16-timesheet-layer.md`, TM-4.

## Implementation evidence

Manual OT override path in `backend/application/timesheet_derivation_service.py`; override UI in the timesheet page.

## Test / review evidence

`docs/test-reports/2026-05-13-sprint-16.md`

## Decision references

None.

## Dependencies

`STORY-0091` — the derived value being overridden.

## Delivery sprint(s)

Sprint 15 (design) / Sprint 16 (delivery).

## Delivery history

- Sprint 16 — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
