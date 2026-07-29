# `STORY-0029` — Component-level calculation trace in the UI; rule trace with resolution source and warnings

**Origin code(s):** `PT-A7-01` · `P2-4` · `P2-7`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-1` — Correctness, Audit & Snapshot
**Feature:** `FEAT-1` — Payroll calculation trace auditability
**Classification:** `operational story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

auditor; payroll operator

## Problem addressed

A net pay figure could be read but not explained — there was no way to see which components produced it, or which rule version each value was resolved from.

## Delivered behaviour

A per-component calculation trace surfaced in the UI, with the rule trace carrying `resolution_source` and any warning raised during resolution.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability areas A7–A10, items P2-4 and P2-7.

## Implementation evidence

`backend/domain/payroll/sequential_executor.py` trace emission; run trace view in `frontend/src/pages/`.

## Test / review evidence

None dedicated — Sprints 1–6 predate the per-sprint test-report convention.

## Decision references

None.

## Dependencies

`STORY-0031` — the persisted `component_trace_jsonb` this view reads.

## Delivery sprint(s)

Sprints 1–6 (Core MVP).

## Delivery history

- Sprints 1–6 — delivered.
- Sprint 10 → 2026-07-12 — `component_source` gap on the `fixed_amount` fallback path found and closed (`STORY-0145`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report exists for this period. A related structural gap recorded outside this programme is that `_rule_trace` returned by `apply_payroll_rules` was discarded in the legacy executor, leaving rule evaluation outcomes unverifiable from the database on that path.
