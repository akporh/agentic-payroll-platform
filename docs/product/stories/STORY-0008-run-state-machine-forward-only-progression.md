# `STORY-0008` — Run state-machine enforcement — DB trigger plus Python, forward-only progression from DRAFT

**Origin code(s):** `PT-A5-01`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-7` — Governance & Run State Machine
**Feature:** `FEAT-29` — Run state machine & approval
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `tentative`

## Actor

payroll operator; auditor

## Problem addressed

Without an enforced lifecycle a run could move backwards or skip states — an approved run could be returned to draft and silently recalculated, destroying the guarantee that an approved figure is the figure that was paid.

## Delivered behaviour

A payroll run starts at `DRAFT` and progresses forward only. Enforcement is doubled: a database trigger and a Python-level guard, so the invariant survives a caller that bypasses the service layer.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability area A5 — Governance, Sprint 0 foundation line items.

## Implementation evidence

Run state-transition trigger in `migrations/versions/`; `backend/application/payroll_run_service.py` transition guards. Cited from the roadmap.

## Test / review evidence

None. No dedicated test report exists for Sprint 0.

## Decision references

Related standing invariant recorded in `CLAUDE.md`: `payroll_run.status = 'APPROVED'` is immutable — no employee results may be modified.

## Dependencies

None.

## Delivery sprint(s)

Sprint 0 — Foundation.

## Delivery history

- Sprint 0 — delivered as part of the foundation run lifecycle.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

Sprint 0 predates the per-sprint test-report convention, so there is no dedicated test report for this item. Its only source is `docs/ROADMAP.md`. Confidence is `tentative` for that reason and it must not be cited as evidence of verified behaviour.
