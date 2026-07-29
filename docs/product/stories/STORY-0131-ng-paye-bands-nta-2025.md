# `STORY-0131` — NG PAYE thresholds and rates corrected to the NTA 2025 schedule

**Origin code(s):** `PAY-TAX-1`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-19` — Statutory deduction correctness
**Classification:** `compliance story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

employee; tax authority

## Problem addressed

The seeded PAYE band schedule did not match the Nigeria Tax Act 2025. Every employee's PAYE was computed against superseded thresholds — a statutory-compliance defect affecting the whole population.

## Delivered behaviour

Migration `de1f2a3b4c5d` updates the NG PAYE thresholds and rates to the NTA 2025 schedule, with test coverage added.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Sprint PAY-TAX-1 — “Correct statutory PAYE bands to match the Nigeria Tax Act 2025 schedule.”

## Implementation evidence

`migrations/versions/de1f2a3b4c5d_fix_ng_paye_bands_nta_2025.py`; `tests/test_paye.py`.

## Test / review evidence

`docs/test-reports/2026-06-20-sprint-pay-tax-1.md`.

## Decision references

Retro lesson recorded: a statutory seed migration must be verified against the **named Act**, not against a prior seed.

## Dependencies

None.

## Delivery sprint(s)

Sprint PAY-TAX-1, 2026-06-20.

## Delivery history

- 2026-06-20 — delivered; bands corrected to NTA 2025.
- 2026-07-28 — captured into `docs/product/` under D-024 (absent from the discovery inventory).
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

None.
