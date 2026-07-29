# `STORY-0018` — Run payroll with period_type, working_days_override and retry_strategy in the UI (P1-7)

**Origin code(s):** `PT-A4-05` · `P1-7`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-18` — Core calculation & component execution
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator

## Problem addressed

Run parameters existed in the API but could not be set from the UI, so an operator could not choose a period type or override working days without a raw API call.

## Delivered behaviour

The run-payroll UI exposes `period_type`, `working_days_override` and `retry_strategy` as operator-settable parameters.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Phase 1 — Sprints 1–6, Execution (A4): “Run payroll with period_type, working_days_override, retry_strategy in UI ✅ (P1-7)”.

## Implementation evidence

`backend/api/routes/payroll.py`; `frontend/src/pages/PayrollRuns.tsx`. Cited in ROADMAP; not independently re-verified in the discovery pass.

## Test / review evidence

No dedicated report for Sprints 1–6.

## Decision references

`retry_strategy` is per-run on `payroll_run`, never on Workspace — a standing architectural constraint.

## Dependencies

None.

## Delivery sprint(s)

Sprints 1–6 (Core MVP).

## Delivery history

- Sprints 1–6 — delivered as P1-7.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

`retry_strategy` was later restricted: `PER_EMPLOYEE` only, with `FULL_RUN` disabled by migration (`CLAUDE.md` data-contract table). The UI's current option set should be re-checked against that allowlist.
