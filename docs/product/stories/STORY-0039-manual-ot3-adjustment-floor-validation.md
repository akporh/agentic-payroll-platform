# `STORY-0039` — Manual OT3 hour adjustment with floor validation (PH-5)

**Origin code(s):** `PT-A4-17` · `PH-5`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-21` — Overtime, shift & public-holiday pay
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator

## Problem addressed

Derived OT3 hours sometimes need operator correction, but an unbounded adjustment allows a negative or nonsensical figure to reach payroll.

## Delivered behaviour

An operator can adjust OT3 hours manually, subject to floor validation.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Phase 1b Track C, item 20 — PH-5.

## Implementation evidence

`backend/domain/payroll/rule_evaluator.py`; run-parameter path.

## Test / review evidence

`docs/test-reports/2026-04-14-sprint-7.md`.

## Decision references

None beyond the Sprint 7 arch-council.

## Dependencies

Depends on `STORY-0038`.

## Delivery sprint(s)

Sprint 7.

## Delivery history

- Sprint 7 — delivered.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

The floor value and whether a ceiling exists are not recorded here.
