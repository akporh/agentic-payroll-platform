# `STORY-0006` — Freeze period context at run start; Decimal precision on monetary values

**Origin code(s):** `PT-A4-03`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-18` — Core calculation & component execution
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `tentative`

## Actor

payroll operator; auditor

## Problem addressed

If period context were re-read during execution, two employees in the same run could be calculated against different inputs. Separately, float arithmetic on money produces rounding errors that compound across components.

## Delivered behaviour

Period context is frozen at run start and reused for every employee in the run. All monetary values use `Decimal`, never float — a standing rule in `CLAUDE.md`.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Sprint 0 — Foundation, Execution (A4): “Freeze period context at run start ✅”, “Decimal precision on all monetary values ✅”.

## Implementation evidence

`backend/domain/payroll/period_context.py`; `Decimal` usage is enforced throughout `backend/domain/payroll/`.

## Test / review evidence

Not dedicated to this item, but `docs/test-reports/2026-07-11-test-harness-baseline.md` and the financial-engine suite exercise Decimal-exactness across all six calculation methods.

## Decision references

`CLAUDE.md` standing rule: “Decimal for all monetary values — never float”.

## Dependencies

None.

## Delivery sprint(s)

Sprint 0 — Foundation (pre-sprint tracking).

## Delivery history

- Sprint 0 — foundation delivery; no dated record.
- 2026-07-16 — a float→Decimal defect of the same class (`tax_bands`) was fixed separately under `STORY-0034` FIX-4, showing the rule needed enforcing after Sprint 0.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

Delivered before per-sprint tracking existed. No dedicated test report covers it; confidence stays `tentative` per D-025 and must not be cited as evidence of verified behaviour without a fresh check against the engine.
