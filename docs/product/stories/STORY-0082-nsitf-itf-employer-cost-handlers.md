# `STORY-0082` — NSITF / ITF employer-cost handlers, threshold-gated (M5)

**Origin code(s):** `PT-A4-25` · `NEW-GAP7` · `M5`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-19` — Statutory deduction correctness
**Classification:** `compliance story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

employer; statutory bodies

## Problem addressed

NSITF and ITF are employer costs, not employee deductions. Without a distinct class they would either be missing entirely or wrongly reduce net pay.

## Delivered behaviour

Both compute 1% × (BASIC + HOUSING + TRANSPORT) with `component_class='employer_cost'` and no employee net-pay deduction. ITF is gated on a threshold: ≥5 employees **and** ≥₦50M annual payroll.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track M, M5 — NEW-GAP7.

## Implementation evidence

`backend/domain/payroll/rule_evaluator.py` — employer-cost handlers with the ITF threshold gate.

## Test / review evidence

No dedicated Sprint 13 report; ROADMAP marks ✅.

## Decision references

Track M arch-council joint review.

## Dependencies

None.

## Delivery sprint(s)

Sprint 13.

## Delivery history

- Sprint 13 — delivered with the ITF threshold gate.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

The ITF threshold is evaluated per run; whether the ≥₦50M annual-payroll test uses actual annualised payroll or a projection is not established by this record.
