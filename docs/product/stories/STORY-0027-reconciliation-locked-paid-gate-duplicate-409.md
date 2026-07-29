# `STORY-0027` — Reconciliation gated to LOCKED/PAID runs; duplicate returns 409 not 500

**Origin code(s):** `PT-A6-02` · `P0-4` · `P0-5`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-8` — Disbursement & Exports
**Feature:** `FEAT-32` — Payroll reconciliation
**Classification:** `compliance story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator

## Problem addressed

Reconciling a run that had not yet been locked compares against figures that can still change; and a duplicate reconciliation attempt surfaced as an unhandled server error rather than a meaningful conflict.

## Delivered behaviour

Reconciliation is permitted only against a run in `LOCKED` or `PAID` state, and a duplicate reconciliation returns HTTP 409 rather than 500.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability area A6, items P0-4 and P0-5.

## Implementation evidence

`backend/infra/repositories/reconciliation_repo.py`; reconciliation route guards.

## Test / review evidence

None dedicated — Sprints 1–6 predate the per-sprint test-report convention.

## Decision references

None.

## Dependencies

`STORY-0010` — the reconciliation surface this gates.

## Delivery sprint(s)

Sprints 1–6 (Core MVP).

## Delivery history

- Sprints 1–6 — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report exists for this period. A workspace-scoping gap in the reconciliation repository was noted in later analysis and is tracked outside this record.
