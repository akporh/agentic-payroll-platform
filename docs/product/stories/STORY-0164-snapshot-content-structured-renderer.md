# `STORY-0164` — Expose snapshot content with a structured UI renderer

**Origin code(s):** —
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-1` — Correctness, Audit & Snapshot
**Feature:** `FEAT-26` — Period & rule snapshot integrity
**Classification:** `user-facing story`
**Status:** `backlog`
**Confidence:** `requires human classification`

## Actor

auditor

## Problem addressed

The frozen period/rule snapshot is persisted and is what makes a run independently verifiable, but there is no way to read it other than querying the database directly. The audit trail exists and is effectively inaccessible to the people it was built for.

## Delivered behaviour

**Not delivered.** Recorded here because the item was open in `docs/ROADMAP.md` and carried no `STORY-<nnnn>`.

## Acceptance criteria

**This item is not delivered.** It is recorded so that an allocated identifier exists and its absence from the delivered set is explicit rather than silent. If it is ever scheduled, criteria are written in the sprint that takes it.

## Source reference

`docs/ROADMAP.md` Phase 1b — Correctness & Audit (A10), ⬜ open.

## Implementation evidence

None — not implemented.

## Test / review evidence

None — not implemented.

## Decision references

Allocated by the `roadmap-split` sprint under `STORY-0160` (`docs/sprints/roadmap-split/CONTEXT.md`), which closed the forward-coverage gap: `ID-ALLOCATION.md` claims that an item absent from it is an item no known evidence records, and that property held for delivered work but not for open work — only 6 of 20 open roadmap items carried an identifier. Classified `backlog` following the D-011 precedent.

## Dependencies

`STORY-0165` — replay consumes the same snapshot this renders.

## Delivery sprint(s)

Not scheduled.

## Delivery history

- Phase 1b — raised alongside snapshot replay. Still open.
- 2026-07-29 — allocated and recorded by the `roadmap-split` sprint (`STORY-0160`).

## Unresolved questions

Not delivered.
