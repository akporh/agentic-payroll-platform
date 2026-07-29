# `STORY-0175` — Automated payroll scheduling (pay cycle scheduler)

**Origin code(s):** —
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-7` — Governance & Run State Machine
**Feature:** `FEAT-29` — Run state machine & approval
**Classification:** `user-facing story`
**Status:** `backlog`
**Confidence:** `requires human classification`

## Actor

payroll administrator

## Problem addressed

`pay_cycle.definition_json` is stored but unused in execution scheduling — the roadmap flags this as a ⚠️ partial as far back as Sprint 0. A pay cycle can be defined and then does nothing; every run is still started by hand.

## Delivered behaviour

**Not delivered.** Recorded here because the item was open in `docs/ROADMAP.md` and carried no `STORY-<nnnn>`.

## Acceptance criteria

**This item is not delivered.** It is recorded so that an allocated identifier exists and its absence from the delivered set is explicit rather than silent. If it is ever scheduled, criteria are written in the sprint that takes it.

## Source reference

`docs/ROADMAP.md` Phase 3 — Platform Scale (future list), "automated payroll scheduling (pay cycle scheduler)"; the underlying gap is recorded at Sprint 0 A1 as "define pay cycle ⚠️ — `definition_json` stored but unused in execution scheduling".

## Implementation evidence

None — not implemented.

## Test / review evidence

None — not implemented.

## Decision references

Allocated by the `roadmap-split` sprint under `STORY-0160` (`docs/sprints/roadmap-split/CONTEXT.md`), which closed the forward-coverage gap: `ID-ALLOCATION.md` claims that an item absent from it is an item no known evidence records, and that property held for delivered work but not for open work — only 6 of 20 open roadmap items carried an identifier. Classified `backlog` following the D-011 precedent.

## Dependencies

None.

## Delivery sprint(s)

Not scheduled.

## Delivery history

- Sprint 0 — the gap recorded as an A1 partial (⚠️). Never closed.
- Phase 3 — the fix recorded in the future list, roughly two years of roadmap apart from the gap it closes.
- 2026-07-29 — allocated and recorded by the `roadmap-split` sprint (`STORY-0160`).

## Unresolved questions

Deferred to Phase 3. Worth noting the shape of this one: the **gap** is recorded at the top of the roadmap and the **fix** at the bottom, under different organising principles and with no link between them. It is a clean illustration of why the roadmap's dual role was worth retiring.
