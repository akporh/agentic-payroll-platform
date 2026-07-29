# `STORY-0096` — Timesheet completeness gate before `link_inputs_to_run`

**Origin code(s):** `PT-A3-13` · `C2`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-5` — Pay Events & Inputs
**Feature:** `FEAT-13` — Timesheet capture & derivation
**Classification:** `compliance story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

payroll operator

## Problem addressed

Running payroll against a partially-uploaded timesheet silently underpays every employee whose attendance had not yet been loaded — and the run looks successful.

## Delivered behaviour

A completeness gate checked before inputs are linked to a run, refusing to proceed when the workspace is in timesheet mode and the period's timesheet is incomplete.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-16-timesheet-layer.md`, C2.

## Implementation evidence

Completeness check ahead of `link_inputs_to_run` in the run start path.

## Test / review evidence

`docs/test-reports/2026-05-13-sprint-16.md`

## Decision references

None.

## Dependencies

`STORY-0093` — the timesheet-to-input conversion this gates; `STORY-0088` — the workspace timesheet-mode configuration.

## Delivery sprint(s)

Sprint 16.

## Delivery history

- Sprint 16 — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
