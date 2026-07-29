# `STORY-0034` — Track A mandatory defect fixes (FIX-1 – FIX-5)

**Origin code(s):** `PT-A4-14` · `FIX-1`–`FIX-5`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-24` — Engine defect remediation
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

employee; payroll operator

## Problem addressed

Five defects had to land before any PH/OT work, because the PH/OT path would amplify each: dead cross-period prefetch code, an NHF key mismatch in the retry service, a health/dev-levy extraction-key error, `tax_bands` held as float, a `rent_relief` rate seeded as the literal string “TBD”, and a `_resolve_inputs` type mismatch reading a dict while receiving a list.

## Delivered behaviour

All five fixed: an isinstance guard for list inputs in cross-period prefetch (FIX-1); NHF key aligned to `employee_rate` in the retry service and `simulate_payroll` (FIX-2); health/dev-levy extraction key corrected in route and retry service (FIX-3); `tax_bands` converted float→`Decimal` at extraction (FIX-4); `rent_relief` “TBD” seed corrected; `_resolve_inputs` type mismatch resolved.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Phase 1b Track A — mandatory defect fixes, pre-approved with no arch-council gate.

## Implementation evidence

`backend/domain/payroll/`, `backend/application/payroll_retry_service.py`, `backend/api/routes/payroll.py`, DB seed for `rent_relief`.

## Test / review evidence

`docs/test-reports/2026-04-14-sprint-7.md`.

## Decision references

Sprint 7 arch-council recorded FIX-1–FIX-5 as mandatory prerequisites for Track C.

## Dependencies

Blocks `STORY-0037`, `STORY-0038` — Track A had to land before any PH/OT feature.

## Delivery sprint(s)

Sprint 7 (Track A).

## Delivery history

- Sprint 7 — all five delivered ahead of Track C.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

Recorded as a single item because ROADMAP groups them as one Track A block. FIX-2 and FIX-3 are the same key-mismatch defect class as `STORY-0023` (SR9), recurring in a different code path.
