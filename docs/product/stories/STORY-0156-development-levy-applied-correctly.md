# `STORY-0156` — Development Levy applied correctly — dual cadence triggers (DEV-LEVY-1)

**Origin code(s):** `DEV-LEVY-1`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-19` — Statutory deduction correctness
**Classification:** `compliance story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

employee; statutory body

## Problem addressed

The January 2026 reconciliation against Sandy's legacy system (run `e3bd910a`) showed **every one of 184 employees short a ₦100 Development Levy deduction**. The `development_levy_flat` handler existed at priority 430 but never fired — and would have computed ₦0 even if it had.

## Delivered behaviour

The levy is evaluated every run against **two independent triggers, OR'd together, never exclusive branches**: (a) the run period contains January, (b) it is the employee's first paid month. A December-start hire is charged in December via (b) and again the following January via (a) — one charge per calendar year, not a double-charge. The amount resolves from a statutory default (₦100) plus an optional per-workspace override under the key `annual_amount` (renamed from `monthly_amount`); an override may be explicitly `0`, which is distinct from no override present.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/sprints/dev-levy-rule-pct/CONTEXT.md` — Story 1, DEV-LEVY-1 (P1, statutory compliance). Root cause in `plan.md` §Context.

## Implementation evidence

`backend/domain/payroll/sequential_executor.py` (post-audit fix applied and re-verified); migrations A and B, dev DB at `75c53c1c6a5b`.

## Test / review evidence

`docs/test-reports/2026-07-16-dev-levy-rule-pct.md` — 327 passed / 1 intentional skip / 0 failed; 8 LIVE API checks; verdict **PASS**. `docs/audit/2026-07-16-dev-levy-rule-pct-audit-review.md` — a CRITICAL finding was raised, fixed, and re-verified **before** the test pass began.

## Decision references

`docs/sprints/dev-levy-rule-pct/decisions.md` DEC-01–DEC-09: DEC-04 (dual OR'd triggers, explicitly not a double-charge), DEC-08 (`annual_amount` key rename), DEC-09 (explicit zero override distinct from absent).

## Dependencies

None.

## Delivery sprint(s)

ICM sprint `dev-levy-rule-pct`, closed 2026-07-16.

## Delivery history

- 2026-07-16 — delivered; CRITICAL audit finding fixed and re-verified pre-test; test report PASS.
- 2026-07-28 — captured into `docs/product/` under D-026 (the discovery inventory has a 2026-07-15 horizon; this closed one day later).
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

None.
