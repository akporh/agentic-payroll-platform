# `STORY-0133` — Date-aware `payroll/input-codes/by-date` endpoint (SPRINT-A-1)

**Origin code(s):** `PT-A4-28` · `SPRINT-A-1`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-22` — Rule resolution & versioning behaviour
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator

## Problem addressed

The Payroll Inputs page showed a rate that only started applying in a later period — a Dec-2025 input displaying the 2026 rate. Root cause: `list_input_codes` was flat, with no date filter at all.

## Delivered behaviour

A `POST /{workspace_id}/payroll/input-codes/by-date` endpoint resolves the rate effective as of each requested reference date, batched over multiple dates in one query. `PayrollInputs.tsx` is rewired from a flat `inputDefs` list to a date-bucketed `inputDefsByDate` map across all four consumer sites.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Sprint A — SPRINT-A-1.

## Implementation evidence

`backend/api/routes/payroll_input.py`; `backend/application/rule_set_service.py` (new shared `resolve_effective_rules()`); `frontend/src/pages/PayrollInputs.tsx`; `frontend/src/api/workspace.ts`. New test file `tests/test_payroll_input_codes_route.py`. **No migration** — query-logic only.

## Test / review evidence

`docs/test-reports/2026-07-04-sprint-a-rule-versioning-integrity.md`. The new test file exists and contains the cited test names.

## Decision references

Sprint A retro: the bug was mis-diagnosed twice before the actual defective query was found — check the literal endpoint behind a UI bug report before designing a fix around adjacent defects.

## Dependencies

None.

## Delivery sprint(s)

Sprint A, 2026-07-04.

## Delivery history

- 2026-07-04 — delivered.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

The test report was not independently re-opened during the discovery pass; confidence remains `strongly inferred`.
