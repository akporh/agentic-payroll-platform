# `STORY-0066` — GAP-5: PAYE CUSTOM annualization corrected to ×12

**Origin code(s):** `PT-A4-12` · `GAP-5` · `K2`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-24` — Engine defect remediation
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

employee; tax authority

## Problem addressed

PAYE annualization for the CUSTOM period type used the wrong multiplier, so the annual figure the cumulative method depends on was wrong — and with it every month's PAYE.

## Delivered behaviour

Annualization is ×12 (`period_context.py:211–216`).

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track K, K2 — GAP-5-FIX.

## Implementation evidence

`backend/domain/payroll/period_context.py:211–216` (line reference as recorded at the time).

## Test / review evidence

`docs/audit/2026-05-01-sprint-10-audit-review.md` — audit-reviewed; `docs/test-reports/2026-05-01-sprint-10.md`.

## Decision references

Pre-approved Track K defect fix; no arch-council gate.

## Dependencies

None.

## Delivery sprint(s)

Sprint 10 (CB-2).

## Delivery history

- Sprint 10 — delivered and audit-reviewed.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

None.
