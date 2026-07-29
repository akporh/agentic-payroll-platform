# `STORY-0162` — View applicable statutory rules — read endpoint + UI

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

An operator cannot see which statutory rule version a workspace will actually be calculated against. The rules are resolved correctly by the engine but are not surfaced anywhere, so the operator must trust the outcome rather than inspect the inputs.

## Delivered behaviour

**Not delivered.** Recorded here because the item was open in `docs/ROADMAP.md` and carried no `STORY-<nnnn>`.

## Acceptance criteria

**This item is not delivered.** It is recorded so that an allocated identifier exists and its absence from the delivered set is explicit rather than silent. If it is ever scheduled, criteria are written in the sprint that takes it.

## Source reference

`docs/ROADMAP.md` Sprint 0 A1 (⬜) and Phase 1b Onboarding (⬜, `P3-2`) — the same item recorded in two places under one code.

## Implementation evidence

None — not implemented.

## Test / review evidence

None — not implemented.

## Decision references

Allocated by the `roadmap-split` sprint under `STORY-0160` (`docs/sprints/roadmap-split/CONTEXT.md`), which closed the forward-coverage gap: `ID-ALLOCATION.md` claims that an item absent from it is an item no known evidence records, and that property held for delivered work but not for open work — only 6 of 20 open roadmap items carried an identifier. Classified `backlog` following the D-011 precedent.

## Dependencies

`STORY-0163` — the write side of the same surface. This is the read half and can ship alone.

## Delivery sprint(s)

Not scheduled.

## Delivery history

- Sprint 0 — raised as an A1 workspace-setup gap. Still open.
- Phase 1b — restated as `P3-2` with an explicit read endpoint + UI scope. Still open.
- 2026-07-29 — allocated and recorded by the `roadmap-split` sprint (`STORY-0160`).

## Unresolved questions

Whether the read view shows only the *effective* rule for a given date or the full version history. The Sprint A lesson applies directly: `is_active` alone never identifies the applicable row — any such view must resolve date-driven (`effective_from <= date`, ordered `effective_from DESC`) or it will display the same wrong answer that Sprint A fixed twice.
