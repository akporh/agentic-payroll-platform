# `STORY-0090` — Timesheet upload — parsing, employee matching, code validation, PH header check

**Origin code(s):** `PT-A3-07` · `TM-2`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-5` — Pay Events & Inputs
**Feature:** `FEAT-13` — Timesheet capture & derivation
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

payroll operator

## Problem addressed

Attendance data arrived as client spreadsheets and had to be transcribed into payroll inputs by hand — the largest single source of manual effort and error in the monthly cycle.

## Delivered behaviour

Timesheet upload that parses the client's file, matches rows to employees, validates the attendance codes used against the workspace's configured codes, and checks the public-holiday header against the workspace's PH configuration.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-16-timesheet-layer.md`, TM-2.

## Implementation evidence

`backend/application/timesheet_derivation_service.py` and the timesheet upload route; timesheet parsing under `backend/application/`.

## Test / review evidence

`docs/test-reports/2026-05-13-sprint-16.md` — 22/22 code-level checks PASS.

## Decision references

Sprint 16 open-question resolutions recorded outside this programme: `employee_number` is the matching identifier; a NULL `shift_type` is a hard reject; attendance codes are workspace-only.

## Dependencies

`STORY-0088` — the workspace timesheet configuration; `STORY-0089` — the attendance codes validated against.

## Delivery sprint(s)

Sprint 15 (design) / Sprint 16 (delivery).

## Delivery history

- Sprint 15 — designed.
- Sprint 16 — delivered.
- 2026-07-13 — a 10 MB server-side size guard added to this endpoint (`STORY-0146`).
- Sprint 24 — re-upload over an APPROVED timesheet blocked (`STORY-0111`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
