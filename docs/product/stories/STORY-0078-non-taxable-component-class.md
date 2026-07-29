# `STORY-0078` — Non-taxable component class, excluded from GROSS_PAY and TAXABLE_INCOME (M1)

**Origin code(s):** `PT-A4-21` · `NEW-GAP14` · `M1`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-19` — Statutory deduction correctness
**Classification:** `compliance story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

employee; tax authority

## Problem addressed

Components that are legally non-taxable had no way to be represented: any component included in earnings also entered the PAYE base, so a non-taxable allowance was taxed.

## Delivered behaviour

`component_class='non_taxable'` is excluded from `GROSS_PAY` and `gross_components_jsonb`, and from `TAXABLE_INCOME`, while still included in `NET_PAY`. The `gross_components_jsonb` exclusion is deliberate and is the correct legal treatment.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track M, M1 — NEW-GAP14. Arch-council joint review with M2 before any code.

## Implementation evidence

`backend/domain/payroll/sequential_executor.py` — `_handle_sum_earnings` exclusion; migrations applied.

## Test / review evidence

`docs/test-reports/2026-05-03-sprint-12-m1-m2.md`.

## Decision references

Sprint 12 M1+M2 arch-council binding decisions. Invariants recorded in `CLAUDE.md`: a `non_taxable` component must **not** have `is_pensionable=True`, and cannot be injected via payroll rules — no `NON_TAXABLE` rule type exists.

## Dependencies

None.

## Delivery sprint(s)

Sprint 12.

## Delivery history

- Sprint 12 — delivered; arch-council reviewed; migrations applied.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

None.
