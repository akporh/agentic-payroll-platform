# `STORY-0168` — N2 / WI-03 — `ot_multiplier` rate-base reconstruction (residual)

**Origin code(s):** `N2` · `WI-03`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-20` — Proration & period handling
**Classification:** `technical enabler`
**Status:** `backlog`
**Confidence:** `requires human classification`

## Actor

engineer

## Problem addressed

`ot_multiplier` computes against the prorated salary rather than the full BASIC, so a mid-period hire's overtime is calculated on the wrong rate base. The parallel `daily_rate_deduction` defect was resolved in Sprint 14 by moving hire proration after `apply_payroll_rules`; the `ot_multiplier` half was never separately confirmed as resolved by that ordering change.

## Delivered behaviour

**Not delivered.** Recorded here because the item was open in `docs/ROADMAP.md` and carried no `STORY-<nnnn>`.

## Acceptance criteria

**This item is not delivered.** It is recorded so that an allocated identifier exists and its absence from the delivered set is explicit rather than silent. If it is ever scheduled, criteria are written in the sprint that takes it.

## Source reference

`docs/ROADMAP.md` Track N, N2 — 🔜 marked **PARTIALLY ADDRESSED**.

## Implementation evidence

None — not implemented.

## Test / review evidence

None — not implemented.

## Decision references

Allocated by the `roadmap-split` sprint under `STORY-0160` (`docs/sprints/roadmap-split/CONTEXT.md`), which closed the forward-coverage gap: `ID-ALLOCATION.md` claims that an item absent from it is an item no known evidence records, and that property held for delivered work but not for open work — only 6 of 20 open roadmap items carried an identifier. Classified `backlog` following the D-011 precedent.

## Dependencies

`STORY-0086` — the Sprint 14 proration ordering fix that resolved this item's sibling defect.

## Delivery sprint(s)

Not scheduled.

## Delivery history

- Track N — raised as WI-03 covering both `ot_multiplier` and `daily_rate_deduction`.
- Sprint 14 — the ordering fix landed and resolved the `daily_rate_deduction` rate-base issue. The roadmap records the `ot_multiplier` half as "separate story if still needed" — never confirmed either way.
- 2026-07-29 — allocated and recorded by the `roadmap-split` sprint (`STORY-0160`).

## Unresolved questions

**Whether any work remains at all.** The roadmap's own note is conditional ("if still needed"). The first task is to verify against the current engine whether the Sprint 14 ordering change already fixed this; it may be closeable without code. Carried as open because nothing on record confirms it was checked.
