# `STORY-0091` — Timesheet derivation — the three-step cap formula

**Origin code(s):** `PT-A3-08` · `TM-3`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-5` — Pay Events & Inputs
**Feature:** `FEAT-13` — Timesheet capture & derivation
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

payroll operator; employee

## Problem addressed

Raw attendance hours are not payable hours. Turning one into the other requires applying the workspace's expected hours, its overtime thresholds and its caps — arithmetic that was being done by hand on a spreadsheet.

## Delivered behaviour

A derivation pipeline that converts parsed attendance into payable quantities via a three-step cap formula, producing the payroll inputs a run then claims.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-16-timesheet-layer.md`, TM-3.

## Implementation evidence

`backend/application/timesheet_derivation_service.py` — the derivation pipeline.

## Test / review evidence

`docs/test-reports/2026-05-13-sprint-16.md` — and explicitly client-validated: a three-employee Client B validation had gross figures verified to match the client's own spreadsheet exactly.

## Decision references

Sprint 15 retro lesson recorded outside this programme: a derivation formula must ship with a worked example, because a formula stated in prose is not independently checkable.

## Dependencies

`STORY-0090` — the parsed timesheet this derives from; `STORY-0095` — per-employee `expected_hours` from `shift_type`.

## Delivery sprint(s)

Sprint 15 (design) / Sprint 16 (delivery).

## Delivery history

- Sprint 15 — designed, including the cap formula.
- Sprint 16 — delivered and validated against the client's own figures.
- Sprint 17 — a LATERAL join defect in this service found; multi-contract verification left BLOCKED (`STORY-0105`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None for the single-contract case. The multi-contract case is `STORY-0105` and is **not** verified.
