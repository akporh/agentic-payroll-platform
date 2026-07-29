# `STORY-0024` — Approve / Lock / Mark-paid actions in the UI

**Origin code(s):** `PT-A5-03` · `P0-1`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-7` — Governance & Run State Machine
**Feature:** `FEAT-29` — Run state machine & approval
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator

## Problem addressed

The run lifecycle existed in the backend but had no operator surface — a run could not be advanced through approval without calling the API directly.

## Delivered behaviour

Approve, Lock and Mark-paid actions available from the run view, driving the state machine that `STORY-0008` enforces.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability area A5, item P0-1.

## Implementation evidence

`frontend/src/pages/` run detail actions; approve/lock/mark-paid routes in `backend/api/routes/payroll.py`.

## Test / review evidence

None dedicated — Sprints 1–6 predate the per-sprint test-report convention.

## Decision references

None.

## Dependencies

`STORY-0008` — the state machine these actions drive.

## Delivery sprint(s)

Sprints 1–6 (Core MVP).

## Delivery history

- Sprints 1–6 — delivered.
- Sprint 7 — `X-Performed-By` actor attribution added on these routes, backend-only (`STORY-0041`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report exists for this period.
