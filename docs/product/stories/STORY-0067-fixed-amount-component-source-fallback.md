# `STORY-0067` — `fixed_amount` handler `component_source` fallback fix (WI-04a)

**Origin code(s):** `PT-A4-13` · `WI-04a` · `K3`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-24` — Engine defect remediation
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

employee; auditor

## Problem addressed

Salary-referenced rules using the `fixed_amount` handler resolved to ₦0 because the component source was not resolved on the fallback path.

## Delivered behaviour

`component_source` is set in the `fixed_amount` handler (`rule_evaluator.py:316`), fixing the ₦0 result for salary-referenced rules.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track K, K3 — WI-04 Sub-A.

## Implementation evidence

`backend/domain/payroll/rule_evaluator.py:316` (line reference as recorded at the time).

## Test / review evidence

`docs/audit/2026-05-01-sprint-10-audit-review.md`; `docs/test-reports/2026-05-01-sprint-10.md`.

## Decision references

This fix **opened** audit observation AUD-1/Q1 — the trace did not name the derivation source on the fallback path — later closed by `STORY-0145`.

## Dependencies

None.

## Delivery sprint(s)

Sprint 10 (CB-7).

## Delivery history

- Sprint 10 — delivered; opened AUD-1/Q1.
- 2026-07-12 — AUD-1/Q1 closed by `STORY-0145` (`component_source` added to the trace entry).
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

None.
