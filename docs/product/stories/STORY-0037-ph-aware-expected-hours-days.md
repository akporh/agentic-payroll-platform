# `STORY-0037` — PH-aware `expected_hours` and `expected_days` in execution context (PH-2 / PH-9)

**Origin code(s):** `PT-A4-15` · `PH-2` · `PH-9`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-21` — Overtime, shift & public-holiday pay
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator

## Problem addressed

Expected hours and days were computed without regard to public holidays, so every downstream rate derived from them was wrong in any period containing a holiday.

## Delivered behaviour

`expected_hours` is computed from PH-adjusted working days; `expected_days` is computed separately and PH-aware, and is snapshotted into the run trace header alongside `ph_dates_used`.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Phase 1b Track C, items 13–14 — PH-2, PH-9.

## Implementation evidence

`backend/domain/payroll/period_context.py`; trace-header snapshot fields.

## Test / review evidence

`docs/test-reports/2026-04-14-sprint-7.md`; `docs/test-reports/2026-04-21-sprint-7-wc12-wc13.md`.

## Decision references

Sprint 7 arch-council decisions (`docs/stories/arch-council-sprint7-decisions.md`).

## Dependencies

None.

## Delivery sprint(s)

Sprint 7.

## Delivery history

- Sprint 7 — delivered as part of Track C.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

Cited in ROADMAP and covered by the Sprint 7 test reports; the underlying migrations were not independently re-read in the discovery pass.
