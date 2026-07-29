# `STORY-0094` — Timesheet audit trail — derivation summary, policy snapshot, per-day grid

**Origin code(s):** `PT-A3-11` · `TM-6`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-5` — Pay Events & Inputs
**Feature:** `FEAT-13` — Timesheet capture & derivation
**Classification:** `operational story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

auditor; payroll operator

## Problem addressed

A derived overtime figure that cannot be explained back to the days and policy that produced it is not defensible — and the policy in force can change before anyone asks.

## Delivered behaviour

Each timesheet carries a derivation summary, a snapshot of the attendance policy applied, and a per-day grid showing how each day was classified and counted.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-16-timesheet-layer.md`, TM-6.

## Implementation evidence

Derivation summary and policy snapshot persistence in `backend/application/timesheet_derivation_service.py`; per-day grid view in the timesheet page.

## Test / review evidence

`docs/test-reports/2026-05-13-sprint-16.md`

## Decision references

Same principle as the run-level snapshot discipline: what a calculation was performed against is stored, not re-derived from live configuration.

## Dependencies

`STORY-0091` — the derivation being explained.

## Delivery sprint(s)

Sprint 15 (design) / Sprint 16 (delivery).

## Delivery history

- Sprint 16 — delivered.
- Sprint 16 — `timesheet_source` added to the run trace header so the payroll side records which timesheet fed it (`STORY-0097`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
