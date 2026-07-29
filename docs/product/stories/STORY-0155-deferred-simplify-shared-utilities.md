# `STORY-0155` — Two deferred `/simplify` items — shared date utilities, shared rule loader

**Origin code(s):** `PT-X-04`
**Outcome:** `OUT-2` — Sustainable delivery process
**Capability:** `CAP-10` — Delivery Infrastructure
**Feature:** `FEAT-39` — Code simplification & technical debt
**Classification:** `discovery or architecture item`
**Status:** `backlog`
**Confidence:** `requires human classification`

## Actor

engineer

## Problem addressed

A `/simplify` pass identified two duplications worth consolidating: date handling repeated across modules, and more than one implementation of loading the latest rule set.

## Delivered behaviour

**Not delivered.** Both were explicitly deferred at the time they were surfaced.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

**This item is not delivered.** It is recorded under D-011 so that an allocated identifier exists and its absence from the delivered set is explicit rather than silent. If it is ever scheduled, criteria are written in the sprint that takes it.

## Source reference

`docs/ROADMAP.md` — two `/simplify` items surfaced in the Sprint 32/33 period and deferred.

## Implementation evidence

None — not implemented.

## Test / review evidence

None — not implemented.

## Decision references

Classified `backlog` under D-011.

## Dependencies

The shared rule-loader item overlaps `STORY-0135`, where the legacy current-period rule loader was date-capped — consolidation would have to preserve that fix.

## Delivery sprint(s)

Not scheduled.

## Delivery history

- Sprint 32/33 — surfaced in a `/simplify` pass and deferred.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

**Not delivered.** Recorded so a known technical-debt item is visible in the hierarchy rather than living only in a retro.
