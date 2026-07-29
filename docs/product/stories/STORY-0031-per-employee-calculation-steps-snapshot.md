# `STORY-0031` — Per-employee calculation-steps snapshot — `component_trace_jsonb`

**Origin code(s):** `PT-A7-03` · `P2-4`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-1` — Correctness, Audit & Snapshot
**Feature:** `FEAT-1` — Payroll calculation trace auditability
**Classification:** `platform capability`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

auditor

## Problem addressed

Without a persisted per-employee record of how each component was calculated, verifying a historical payslip required re-running the engine against live configuration — which by then may have changed.

## Delivered behaviour

Each employee's calculation steps are persisted as `component_trace_jsonb` on the result row, so a stored figure is independently verifiable from stored data.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability areas A7–A10, item P2-4.

## Implementation evidence

`backend/domain/payroll/sequential_executor.py` — the production executor path that produces `component_trace_jsonb`.

## Test / review evidence

None dedicated — Sprints 1–6 predate the per-sprint test-report convention.

## Decision references

Recorded as a standing data-contract invariant in `CLAUDE.md`: `payroll_result.status = 'SUCCESS'` means `net_pay` and `component_trace_jsonb` are populated.

## Dependencies

None.

## Delivery sprint(s)

Sprints 1–6 (Core MVP).

## Delivery history

- Sprints 1–6 — delivered on the sequential executor path.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report exists for this period. The legacy executor fallback does **not** produce `component_trace_jsonb` — see `STORY-0032`, which added the deprecation signalling for exactly that reason.
