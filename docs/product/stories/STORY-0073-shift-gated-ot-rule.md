# `STORY-0073` — Shift-gated OT rule; `shift_type` threaded per employee (WI-04b)

**Origin code(s):** `PT-A4-19` · `WI-04b`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-21` — Overtime, shift & public-holiday pay
**Classification:** `compliance story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

employee; payroll operator

## Problem addressed

A `basic_daily` OT rule applied to non-shift employees would pay overtime to staff not entitled to it. `shift_type` was not available per employee at the point the rule was evaluated.

## Delivered behaviour

`shift_type` is threaded through to per-employee rule evaluation; the `basic_daily` OT rule returns ₦0 for non-shift employees rather than computing a rate they are not eligible for.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track O / Sprint 11 — WI-04b.

## Implementation evidence

`backend/domain/payroll/rule_evaluator.py`; `shift_type` on `employee`, added by `STORY-0071`.

## Test / review evidence

`docs/audit/2026-05-02-sprint-11-audit-review.md` — audit-reviewed; `docs/test-reports/2026-05-02-sprint-11.md`.

## Decision references

None beyond routine execution.

## Dependencies

Depends on `STORY-0071` (`shift_type` must exist on the employee record).

## Delivery sprint(s)

Sprint 11.

## Delivery history

- Sprint 11 — delivered and audit-reviewed.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

None.
