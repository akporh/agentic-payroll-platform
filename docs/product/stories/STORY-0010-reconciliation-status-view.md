# `STORY-0010` — Reconciliation status view

**Origin code(s):** `PT-A6-01`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-8` — Disbursement & Exports
**Feature:** `FEAT-32` — Payroll reconciliation
**Classification:** `operational story`
**Status:** `delivered`
**Confidence:** `tentative`

## Actor

payroll operator

## Problem addressed

After a run was paid there was no view showing whether what actually left the bank matched what the platform expected.

## Delivered behaviour

A reconciliation view showing per-run reconciliation status — the first version of the surface later gated, corrected and extended by `STORY-0027` and `STORY-0028`.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability area A6 — Disbursement, Sprint 0 foundation line items.

## Implementation evidence

`backend/infra/repositories/reconciliation_repo.py`; reconciliation routes. Cited from the roadmap.

## Test / review evidence

None. No dedicated test report exists for Sprint 0.

## Decision references

None.

## Dependencies

None.

## Delivery sprint(s)

Sprint 0 — Foundation.

## Delivery history

- Sprint 0 — delivered as the first reconciliation surface.
- Sprints 1–6 — gated to LOCKED/PAID and duplicate-handled (`STORY-0027`); MISMATCH correction added (`STORY-0028`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

Sprint 0 predates the per-sprint test-report convention, so there is no dedicated test report for this item. Its only source is `docs/ROADMAP.md`. Confidence is `tentative` for that reason and it must not be cited as evidence of verified behaviour.
