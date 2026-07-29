# `STORY-0042` — Snapshot `expected_days`, `ph_dates_used` and `ph_source` in the run trace header

**Origin code(s):** `PT-A7-09` · `PH-9`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-1` — Correctness, Audit & Snapshot
**Feature:** `FEAT-1` — Payroll calculation trace auditability
**Classification:** `operational story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

auditor

## Problem addressed

Public-holiday-aware calculations depend on which holiday dates were in force and where they came from. Without recording that in the trace, a past run's PH arithmetic could not be reproduced once the holiday configuration changed.

## Delivered behaviour

The run trace header carries `expected_days`, the `ph_dates_used` list, and `ph_source` identifying whether the dates came from the national or workspace table.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability areas A7–A10, item PH-9.

## Implementation evidence

`_period_context` trace-header construction in the run start path.

## Test / review evidence

`docs/test-reports/2026-04-14-sprint-7.md`, `docs/test-reports/2026-04-21-sprint-7-wc12-wc13.md`.

## Decision references

None.

## Dependencies

`STORY-0035` — the PH engine whose inputs this snapshots; `STORY-0037` — the PH-aware expected-hours/days computation.

## Delivery sprint(s)

Sprint 7.

## Delivery history

- Sprint 7 — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test line item isolates this field set; it is covered inside the Sprint 7 PH test scope.
