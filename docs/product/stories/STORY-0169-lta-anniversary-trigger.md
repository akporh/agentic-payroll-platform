# `STORY-0169` — O5 / NEW-GAP11 — LTA anniversary trigger

**Origin code(s):** `O5` · `NEW-GAP11`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-19` — Statutory deduction correctness
**Classification:** `user-facing story`
**Status:** `backlog`
**Confidence:** `requires human classification`

## Actor

payroll administrator

## Problem addressed

Leave travel allowance is due on an employee's engagement anniversary and must be entered by hand every period. Nothing detects that an employee's `date_engaged` anniversary falls inside the current pay period, so the entitlement is missed unless someone remembers.

## Delivered behaviour

**Not delivered.** Recorded here because the item was open in `docs/ROADMAP.md` and carried no `STORY-<nnnn>`.

## Acceptance criteria

**This item is not delivered.** It is recorded so that an allocated identifier exists and its absence from the delivered set is explicit rather than silent. If it is ever scheduled, criteria are written in the sprint that takes it.

## Source reference

`docs/ROADMAP.md` Track O, O5 — ⬜ open, "deferred to Sprint 12 (D10); blocked on M2".

## Implementation evidence

None — not implemented.

## Test / review evidence

None — not implemented.

## Decision references

Allocated by the `roadmap-split` sprint under `STORY-0160` (`docs/sprints/roadmap-split/CONTEXT.md`), which closed the forward-coverage gap: `ID-ALLOCATION.md` claims that an item absent from it is an item no known evidence records, and that property held for delivered work but not for open work — only 6 of 20 open roadmap items carried an identifier. Classified `backlog` following the D-011 precedent.

## Dependencies

`STORY-0079` — M2, the PAYE-only additions path. **Delivered**, so this item's stated blocker is cleared.

## Delivery sprint(s)

Not scheduled.

## Delivery history

- Track O — raised as NEW-GAP11, deferred to Sprint 12 under D10, blocked on M2.
- Sprint 12 — M2 (`STORY-0079`) delivered the PAYE-only additions path. The blocker is gone; the item was never picked back up.
- 2026-07-29 — allocated and recorded by the `roadmap-split` sprint (`STORY-0160`).

## Unresolved questions

Its stated blocker no longer exists — M2 shipped. The deferral reason recorded in the roadmap is stale, which is exactly the kind of fact the roadmap's dual role made hard to notice. Whether it is now scheduled is a prioritisation decision, not a dependency one.
