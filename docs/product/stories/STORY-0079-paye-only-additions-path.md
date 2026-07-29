# `STORY-0079` — PAYE-only additions path via `input_category` (M2)

**Origin code(s):** `PT-A4-22` · `NEW-GAP15` · `M2`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-19` — Statutory deduction correctness
**Classification:** `compliance story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

employee; tax authority

## Problem addressed

Some amounts are taxable but are not paid to the employee and must not inflate gross or net. There was no path for a value to enter the PAYE base alone.

## Delivered behaviour

`payroll_input.input_category` accepts `PAYE_ONLY`; such rows aggregate into `TAXABLE_INCOME` only — never `GROSS_PAY` or `NET_PAY`. Handled at priority 95 via `component_class='paye_addition'`, read only by `_handle_taxable_income`.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track M, M2 — NEW-GAP15.

## Implementation evidence

`backend/domain/payroll/sequential_executor.py` — `_handle_taxable_income`; `input_category VARCHAR(20)` migration.

## Test / review evidence

`docs/test-reports/2026-05-03-sprint-12-m1-m2.md`.

## Decision references

Sprint 12 M1+M2 arch-council. `CLAUDE.md` records the invariants: allowed `input_category` values are uppercase (`EARNING`, `DEDUCTION`, `STANDARD`, `PAYE_ONLY`), and `PAYE_ONLY` must use the standard `link_inputs_to_run` claiming path so a retry reproduces the same `TAXABLE_INCOME`.

## Dependencies

Depends on `STORY-0007` (the `TAXABLE_INCOME` base must exist).

## Delivery sprint(s)

Sprint 12.

## Delivery history

- Sprint 12 — delivered; arch-council reviewed; migrations applied.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

None.
