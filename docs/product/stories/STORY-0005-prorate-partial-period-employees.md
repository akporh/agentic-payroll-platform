# `STORY-0005` — Prorate pay for partial-period employees

**Origin code(s):** `PT-A4-02`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-20` — Proration & period handling
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `tentative`

## Actor

employee; payroll operator

## Problem addressed

An employee hired or terminated mid-period must be paid for the portion worked, not a full month.

## Delivered behaviour

Pay is prorated for employees active for part of the period only.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Sprint 0 — Foundation, Execution (A4): “Prorate pay for partial-period employees ✅”.

## Implementation evidence

`backend/domain/payroll/` proration path; superseded in behaviour by `STORY-0086`.

## Test / review evidence

None dedicated at Sprint 0.

## Decision references

None beyond routine execution.

## Dependencies

None.

## Delivery sprint(s)

Sprint 0 — Foundation (pre-sprint tracking).

## Delivery history

- Sprint 0 — initial proration.
- Sprint 14 — substantially reworked by `STORY-0086`: strategy-aware, per-component, and re-ordered relative to `apply_payroll_rules`.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

Delivered before per-sprint tracking existed. No dedicated test report covers it; confidence stays `tentative` per D-025 and must not be cited as evidence of verified behaviour without a fresh check against the engine. Its behaviour is largely superseded by `STORY-0086`; treat that story as the current description of proration.
