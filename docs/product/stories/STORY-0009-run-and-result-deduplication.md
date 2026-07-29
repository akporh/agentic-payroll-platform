# `STORY-0009` — Deduplicate runs by idempotency key and period; deduplicate per-employee results

**Origin code(s):** `PT-A5-02`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-7` — Governance & Run State Machine
**Feature:** `FEAT-29` — Run state machine & approval
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `tentative`

## Actor

payroll operator

## Problem addressed

A retried or double-submitted request could create a second run for the same period, or a second result row for the same employee within one run — either of which double-counts pay.

## Delivered behaviour

Runs are deduplicated on an idempotency key and the target period; per-employee results are deduplicated within a run.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability area A5 — Governance, Sprint 0 foundation line items.

## Implementation evidence

`backend/application/payroll_run_service.py` run creation; uniqueness constraints in `migrations/versions/`. Cited from the roadmap.

## Test / review evidence

None. No dedicated test report exists for Sprint 0.

## Decision references

None.

## Dependencies

`STORY-0008` — the state machine this dedup protects.

## Delivery sprint(s)

Sprint 0 — Foundation.

## Delivery history

- Sprint 0 — delivered as part of the foundation run lifecycle.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

Sprint 0 predates the per-sprint test-report convention, so there is no dedicated test report for this item. Its only source is `docs/ROADMAP.md`. Confidence is `tentative` for that reason and it must not be cited as evidence of verified behaviour.
