# `STORY-0080` — Check-off dues handler — `percentage_of_sum` (M3)

**Origin code(s):** `PT-A4-23` · `NEW-GAP6` · `M3`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-19` — Statutory deduction correctness
**Classification:** `compliance story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

employee; union

## Problem addressed

Union check-off dues had no handler; the deduction could not be expressed as a percentage of a component subset.

## Delivered behaviour

A `percentage_of_sum` handler computes 2% × (BASIC + HOUSING + TRANSPORT) with `component_class='statutory_deduction'`, gated on an `is_union_member` eligibility rule, at priority 450.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track M, M3 — NEW-GAP6.

## Implementation evidence

`backend/domain/payroll/rule_evaluator.py` — `percentage_of_sum` method; seeded `component_metadata` row.

## Test / review evidence

`docs/test-reports/2026-05-03-sprint-12-m1-m2.md` scope note; Sprint 13 covered in ROADMAP.

## Decision references

Sprint 13 M3 arch-council D1–D6, including the priority-chain placement `CHECK_OFF_DUES=450`.

## Dependencies

None.

## Delivery sprint(s)

Sprint 13.

## Delivery history

- Sprint 13 — delivered.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

Sprint 13 has no dedicated test report of its own; verification is referenced through the Sprint 12 report's scope note and the ROADMAP entry.
