# `STORY-0022` — Execution trace / timeline view (P1-6)

**Origin code(s):** `PT-A4-09` · `P1-6`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-25` — Execution observability
**Classification:** `operational story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator; auditor

## Problem addressed

Without a view of what the engine did during a run, a wrong figure could only be investigated by re-deriving it by hand.

## Delivered behaviour

An execution trace and timeline view exposes the run's component-by-component execution.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Phase 1 — Sprints 1–6, Execution (A4): “View execution trace / timeline ✅ (P1-6)”.

## Implementation evidence

`backend/api/routes/payroll.py` (`get_run_timeline`); frontend trace view.

## Test / review evidence

No dedicated report for Sprints 1–6.

## Decision references

None recorded at the time.

## Dependencies

None.

## Delivery sprint(s)

Sprints 1–6 (Core MVP).

## Delivery history

- Sprints 1–6 — delivered as P1-6.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

The architecture-review programme's finding F-07-01 records `get_run_timeline` as one of five routes with decorative rather than enforced workspace scoping. That is a security finding against this story's route, not yet remediated.
