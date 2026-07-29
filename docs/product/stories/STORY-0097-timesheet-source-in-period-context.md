# `STORY-0097` — `timesheet_source` added to the `_period_context` trace header

**Origin code(s):** `PT-A7-06` · `AUD-16-3` · `Q5`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-1` — Correctness, Audit & Snapshot
**Feature:** `FEAT-1` — Payroll calculation trace auditability
**Classification:** `operational story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

auditor

## Problem addressed

Once quantities could originate either from manual input or from timesheet derivation, a stored result gave no way to tell which — so a figure could not be traced back to the process that produced it.

## Delivered behaviour

`timesheet_source` is carried in the `_period_context` trace header, recording the provenance of the period's quantities.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track Q register, AUD-16-3 / Q5.

## Implementation evidence

`_period_context` construction in the run start path.

## Test / review evidence

`docs/test-reports/2026-05-13-sprint-16.md`

## Decision references

None.

## Dependencies

`STORY-0093` — the timesheet-to-input conversion whose provenance this records.

## Delivery sprint(s)

Sprint 16.

## Delivery history

- Sprint 16 — raised as audit finding AUD-16-3 and fixed within the same sprint.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None. `PT-Q-05` is the Track Q register's duplicate code for this same item, and resolves to `STORY-0097`.
