# `STORY-0152` — AUD-3 / Q3 — `Decimal(str(...))` conversion in the simulate script

**Origin code(s):** `PT-Q-03` · `AUD-3` · `Q3`
**Outcome:** `OUT-2` — Sustainable delivery process
**Capability:** `CAP-10` — Delivery Infrastructure
**Feature:** `FEAT-39` — Code simplification & technical debt
**Classification:** `technical enabler`
**Status:** `backlog`
**Confidence:** `requires human classification`

## Actor

engineer

## Problem addressed

The simulation script converts values in a way that can introduce float imprecision, so a simulated figure may not exactly match what the engine would produce.

## Delivered behaviour

**Not delivered.** The roadmap still shows AUD-3 / Q3 open.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

**This item is not delivered.** It is recorded under D-011 so that an allocated identifier exists and its absence from the delivered set is explicit rather than silent. If it is ever scheduled, criteria are written in the sprint that takes it.

## Source reference

`docs/ROADMAP.md` Track Q register, AUD-3 / Q3 — 🔜 open.

## Implementation evidence

None — not implemented.

## Test / review evidence

None — not implemented.

## Decision references

Classified `backlog` under D-011.

## Dependencies

None.

## Delivery sprint(s)

Not scheduled.

## Delivery history

- Sprint 10 — raised as audit observation AUD-3. Still open.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

**Not delivered.** A related, separately-recorded limitation is that the simulation scripts have no proration step at all, so mid-period hire scenarios cannot be reproduced or validated through them.
