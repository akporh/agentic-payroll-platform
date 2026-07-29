# `STORY-0095` — Per-employee `expected_hours` derived from `shift_type` (C1 live-bug fix)

**Origin code(s):** `PT-A3-12` · `C1`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-5` — Pay Events & Inputs
**Feature:** `FEAT-13` — Timesheet capture & derivation
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

payroll operator; employee

## Problem addressed

Expected hours were being applied uniformly when they are in fact a property of the employee's shift pattern. A shift worker and a day worker with identical attendance were being assessed against the same expectation, producing wrong overtime for one of them.

## Delivered behaviour

`expected_hours` is resolved per employee from their `shift_type` rather than from a single workspace-level value.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-16-timesheet-layer.md`, C1 — a live bug found during the Sprint 16 client validation.

## Implementation evidence

Per-employee expected-hours resolution in `backend/application/timesheet_derivation_service.py`.

## Test / review evidence

`docs/test-reports/2026-05-13-sprint-16.md`

## Decision references

Sprint 15 retro lesson recorded outside this programme: a per-employee context value must not be computed as a scalar shared across the run — this bug is the instance that produced the lesson.

## Dependencies

`STORY-0071` — the `shift_type` field on the employee record.

## Delivery sprint(s)

Sprint 16.

## Delivery history

- Sprint 16 — found live during client validation and fixed within the sprint.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
