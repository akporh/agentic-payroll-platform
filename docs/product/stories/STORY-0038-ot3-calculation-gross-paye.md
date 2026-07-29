# `STORY-0038` — OT3 at 3.25× flowing into GROSS_PAY and the PAYE base (PH-3 / PH-4)

**Origin code(s):** `PT-A4-16` · `PH-3` · `PH-4`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-21` — Overtime, shift & public-holiday pay
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `tentative`

## Actor

employee; payroll operator

## Problem addressed

Overtime worked on a public holiday attracts a 3.25× multiplier, and that pay is taxable — it must reach both gross and the PAYE base.

## Delivered behaviour

An `ot_multiplier` handler computes OT3 at 3.25× `basic_hourly` for PH hours worked, reading hours from inputs; the result flows into `GROSS_PAY` and the PAYE base.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Phase 1b Track C, items 18–19 — PH-3, PH-4.

## Implementation evidence

`backend/domain/payroll/rule_evaluator.py` — `ot_multiplier` handler. `classify_day` is defined.

## Test / review evidence

`docs/test-reports/2026-04-14-sprint-7.md`.

## Decision references

Sprint 7 arch-council: Model A for PH-8 — extend `apply_payroll_rules` signature rather than thread state.

## Dependencies

Depends on `STORY-0037` (PH-aware expected hours).

## Delivery sprint(s)

Sprint 7.

## Delivery history

- Sprint 7 — delivered as part of Track C.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

**Status ambiguity, deliberately not resolved.** ROADMAP marks PH-3 ✅ but its own notes column records that `classify_day` “has no call site yet (dead code)”. A function that exists but is never called is a materially different delivery state from “done”. Confidence stays `tentative`; this must be resolved by inspection before the item is cited as complete. Carried from the discovery document's §14 risk list.
