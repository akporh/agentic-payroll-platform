# `STORY-0165` — Replay a run using its frozen snapshot

**Origin code(s):** `P4-2`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-1` — Correctness, Audit & Snapshot
**Feature:** `FEAT-26` — Period & rule snapshot integrity
**Classification:** `operational story`
**Status:** `backlog`
**Confidence:** `requires human classification`

## Actor

auditor

## Problem addressed

A completed run cannot be re-executed against the exact context it was originally calculated with. Reproducing a historical result depends on the current state of the rules rather than the frozen snapshot, so a disputed payslip cannot be independently re-derived.

## Delivered behaviour

**Not delivered.** Recorded here because the item was open in `docs/ROADMAP.md` and carried no `STORY-<nnnn>`.

## Acceptance criteria

**This item is not delivered.** It is recorded so that an allocated identifier exists and its absence from the delivered set is explicit rather than silent. If it is ever scheduled, criteria are written in the sprint that takes it.

## Source reference

`docs/ROADMAP.md` Phase 1b — Correctness & Audit (A10), ⬜ open, annotated "may move to Phase 3"; also listed in the Phase 3 future list as "snapshot replay endpoint (`P4-2`)".

## Implementation evidence

None — not implemented.

## Test / review evidence

None — not implemented.

## Decision references

Allocated by the `roadmap-split` sprint under `STORY-0160` (`docs/sprints/roadmap-split/CONTEXT.md`), which closed the forward-coverage gap: `ID-ALLOCATION.md` claims that an item absent from it is an item no known evidence records, and that property held for delivered work but not for open work — only 6 of 20 open roadmap items carried an identifier. Classified `backlog` following the D-011 precedent.

## Dependencies

`STORY-0164` — shares the snapshot-reading surface.

## Delivery sprint(s)

Not scheduled.

## Delivery history

- Phase 1b — raised as `P4-2`, flagged as possibly belonging to Phase 3.
- Phase 3 — also listed in the future list. One item, recorded twice; the roadmap never resolved which phase owns it.
- 2026-07-29 — allocated and recorded by the `roadmap-split` sprint (`STORY-0160`).

## Unresolved questions

Which phase owns it. The roadmap records the ambiguity ("may move to Phase 3") and never settles it — carried forward unresolved rather than decided here, since this sprint moves items and does not judge them.
