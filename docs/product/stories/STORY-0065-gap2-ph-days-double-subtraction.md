# `STORY-0065` — GAP-2: remove double-subtraction of PH days in AUTOMATIC mode

**Origin code(s):** `PT-A4-11` · `GAP-2` · `K1`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-24` — Engine defect remediation
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

employee

## Problem addressed

In AUTOMATIC public-holiday mode, public-holiday days were subtracted twice from working days — understating expected days and so overstating every daily-rate-derived figure.

## Delivered behaviour

The double subtraction is removed (`payroll.py:505`).

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track K, K1 — GAP-2-FIX, identified in the Client B gap audit 2026-04-30.

## Implementation evidence

`backend/api/routes/payroll.py:505` (line reference as recorded at the time).

## Test / review evidence

`docs/audit/2026-05-01-sprint-10-audit-review.md` — **0 findings on this exact change**; `docs/test-reports/2026-05-01-sprint-10.md`.

## Decision references

Track K items are pre-approved defect fixes with no migration or data-contract change, so no arch-council gate.

## Dependencies

None.

## Delivery sprint(s)

Sprint 10 (CB-1).

## Delivery history

- Sprint 10 — delivered and audit-reviewed with zero findings.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

None.
