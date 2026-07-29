# `STORY-0153` — AUD-16-1 / Q7 — `approved_by` actor identity on timesheet transitions

**Origin code(s):** `PT-Q-07` · `AUD-16-1` · `Q7`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-7` — Governance & Run State Machine
**Feature:** `FEAT-30` — Audit trail & actor attribution
**Classification:** `compliance story`
**Status:** `backlog`
**Confidence:** `requires human classification`

## Actor

auditor

## Problem addressed

Timesheet approval records that a transition happened but not who performed it, so the approval chain on derived pay quantities has no attributable actor.

## Delivered behaviour

**Not delivered.** Explicitly deferred to the future Track P authentication work, since attributing an action requires an authenticated identity to attribute it to.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

**This item is not delivered.** It is recorded under D-011 so that an allocated identifier exists and its absence from the delivered set is explicit rather than silent. If it is ever scheduled, criteria are written in the sprint that takes it.

## Source reference

`docs/ROADMAP.md` Track Q register, AUD-16-1 / Q7 — ⬜ open, deferred to Track P.

## Implementation evidence

None — not implemented.

## Test / review evidence

None — not implemented.

## Decision references

Classified `backlog` under D-011. The dependency on authentication is the stated reason for deferral, not a scheduling preference.

## Dependencies

Track P (authentication) — not yet built. Related: `STORY-0041`, where the same actor-attribution gap exists on the run governance routes with only the backend half delivered.

## Delivery sprint(s)

Not scheduled — deferred to Track P.

## Delivery history

- Sprint 16 — raised as audit observation AUD-16-1. Still open.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

**Not delivered.** Together with `STORY-0041` this is the platform's standing actor-attribution gap: governance and approval actions are recorded without a verified actor.
