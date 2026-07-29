# `STORY-0174` — P4-6 — multi-tenant bureau scaling

**Origin code(s):** `P4-6`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-3` — Onboarding & Workspace Setup
**Feature:** `FEAT-6` — Client onboarding & workspace creation
**Classification:** `technical enabler`
**Status:** `backlog`
**Confidence:** `requires human classification`

## Actor

bureau operator

## Problem addressed

The platform serves a small number of workspaces created by hand. Operating as a bureau across many client workspaces has not been designed for — provisioning, isolation at scale, and per-tenant configuration are all manual.

## Delivered behaviour

**Not delivered.** Recorded here because the item was open in `docs/ROADMAP.md` and carried no `STORY-<nnnn>`.

## Acceptance criteria

**This item is not delivered.** It is recorded so that an allocated identifier exists and its absence from the delivered set is explicit rather than silent. If it is ever scheduled, criteria are written in the sprint that takes it.

## Source reference

`docs/ROADMAP.md` Phase 3 — Platform Scale (future list), `P4-6`.

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

- Phase 3 — recorded in the future list. Never scheduled.
- 2026-07-29 — allocated and recorded by the `roadmap-split` sprint (`STORY-0160`).

## Unresolved questions

Deferred to Phase 3. This is a heading rather than a scoped item — it would need decomposition before it could be scheduled, and would touch workspace scoping, which is a mandatory query-level invariant across the whole platform.
