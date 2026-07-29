# `STORY-0040` — PH count-mismatch warnings and AUTOMATIC-mode pre-flight check (PH-10 / PH-11)

**Origin code(s):** `PT-A4-18` · `PH-10` · `PH-11`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-21` — Overtime, shift & public-holiday pay
**Classification:** `operational story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator

## Problem addressed

In AUTOMATIC public-holiday mode, a mismatch between expected and configured holidays silently produces wrong pay. The operator needed to be told before approving, not after.

## Delivered behaviour

A pre-flight check runs for AUTOMATIC-mode runs; PH count-mismatch and duplicate warnings are surfaced in the execution trace.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Phase 1b Track D — PH-10, PH-11.

## Implementation evidence

`backend/domain/payroll/` PH pre-flight path; warnings written to the execution trace.

## Test / review evidence

`docs/test-reports/2026-04-14-sprint-7.md`.

## Decision references

None beyond the Sprint 7 arch-council.

## Dependencies

Depends on `STORY-0037`.

## Delivery sprint(s)

Sprint 7.

## Delivery history

- Sprint 7 — delivered as part of Track D.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

Whether the pre-flight check blocks the run or only warns is not established by this record.
