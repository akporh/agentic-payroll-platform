# `STORY-0093` — Timesheet-to-pay-instruction flow — atomic approval and readiness gate

**Origin code(s):** `PT-A3-10` · `TM-5`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-5` — Pay Events & Inputs
**Feature:** `FEAT-13` — Timesheet capture & derivation
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

payroll operator

## Problem addressed

An approved timesheet has to become payroll inputs. Doing that non-atomically risks a half-converted timesheet — some employees' hours turned into inputs and others not — which is worse than not converting at all.

## Delivered behaviour

Timesheet approval converts the derived quantities into payroll inputs atomically, behind a readiness gate that refuses to convert an incomplete timesheet.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-16-timesheet-layer.md`, TM-5.

## Implementation evidence

Approval and conversion path in `backend/application/timesheet_derivation_service.py`.

## Test / review evidence

`docs/test-reports/2026-05-13-sprint-16.md`

## Decision references

None.

## Dependencies

`STORY-0091` — the derivation whose output is converted; `STORY-0096` — the completeness gate on the run side.

## Delivery sprint(s)

Sprint 15 (design) / Sprint 16 (delivery).

## Delivery history

- Sprint 16 — delivered.
- Sprint 24 — re-upload after approval blocked, closing the evidence-destruction path (`STORY-0111`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

Actor identity is **not** captured on these transitions — an approved timesheet does not record who approved it. That gap is `STORY-0153`, still open and deferred to the future authentication work.
