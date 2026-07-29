# `STORY-0163` — Statutory rule management UI for bureau operators

**Origin code(s):** `P3-2`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-7` — Governance & Run State Machine
**Feature:** `FEAT-31` — Statutory & payroll rule versioning
**Classification:** `user-facing story`
**Status:** `backlog`
**Confidence:** `requires human classification`

## Actor

bureau operator

## Problem addressed

Statutory rates (PAYE bands, NHF, pension) can only be changed by a seed migration written by an engineer. A bureau operator cannot respond to a statutory change without a code deployment.

## Delivered behaviour

**Not delivered.** Recorded here because the item was open in `docs/ROADMAP.md` and carried no `STORY-<nnnn>`.

## Acceptance criteria

**This item is not delivered.** It is recorded so that an allocated identifier exists and its absence from the delivered set is explicit rather than silent. If it is ever scheduled, criteria are written in the sprint that takes it.

## Source reference

`docs/ROADMAP.md` Phase 1b Onboarding (⬜, `P3-2`) and the Phase 3 future list.

## Implementation evidence

None — not implemented.

## Test / review evidence

None — not implemented.

## Decision references

Allocated by the `roadmap-split` sprint under `STORY-0160` (`docs/sprints/roadmap-split/CONTEXT.md`), which closed the forward-coverage gap: `ID-ALLOCATION.md` claims that an item absent from it is an item no known evidence records, and that property held for delivered work but not for open work — only 6 of 20 open roadmap items carried an identifier. Classified `backlog` following the D-011 precedent.

## Dependencies

`STORY-0162` — the read view should land first; editing a surface nobody can inspect is the riskier order.

## Delivery sprint(s)

Not scheduled.

## Delivery history

- Phase 1b — raised as `P3-2`. Still open.
- Phase 3 — restated in the future list as "statutory rule management for bureau operators". Same item.
- 2026-07-29 — allocated and recorded by the `roadmap-split` sprint (`STORY-0160`).

## Unresolved questions

This writes to a financially critical table under a `(country_code, effective_from)` UNIQUE constraint and would need `/arch-council` before any implementation. Sprint PAY-TAX-1's lesson also applies: a statutory rate change must be verifiable against the named Act, which an operator-facing form does not by itself guarantee.
