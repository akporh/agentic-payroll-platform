# `STORY-0007` — PAYE computed on taxable income, not gross

**Origin code(s):** `PT-A4-04`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-19` — Statutory deduction correctness
**Classification:** `compliance story`
**Status:** `delivered`
**Confidence:** `tentative`

## Actor

employee; tax authority

## Problem addressed

PAYE assessed on gross rather than taxable income over-deducts from every employee and misstates the employer's remittance.

## Delivered behaviour

PAYE is computed against `TAXABLE_INCOME`, which excludes non-taxable components and includes PAYE-only additions — the base the Act defines, not the gross figure.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Sprint 0 — Foundation, Execution (A4): “Compute PAYE on taxable income, not gross ✅”.

## Implementation evidence

`backend/domain/payroll/sequential_executor.py` — `_handle_taxable_income`.

## Test / review evidence

None dedicated at Sprint 0. The base has since been exercised repeatedly by `STORY-0078`/`0079` (Sprint 12) and `STORY-0131` (PAY-TAX-1).

## Decision references

The `TAXABLE_INCOME` contract is load-bearing for `component_class='non_taxable'` and `'paye_addition'` — see `CLAUDE.md`.

## Dependencies

None.

## Delivery sprint(s)

Sprint 0 — Foundation (pre-sprint tracking).

## Delivery history

- Sprint 0 — foundation delivery.
- Sprint 12 — base refined by the non-taxable class and PAYE-only additions path.
- 2026-06-20 — band schedule corrected to NTA 2025 (`STORY-0131`).
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

Delivered before per-sprint tracking existed. No dedicated test report covers it; confidence stays `tentative` per D-025 and must not be cited as evidence of verified behaviour without a fresh check against the engine.
