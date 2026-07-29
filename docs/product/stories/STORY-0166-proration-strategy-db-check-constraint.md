# `STORY-0166` — S6 — `proration_strategy` DB CHECK constraint

**Origin code(s):** `S6` · `SEC-S5`
**Outcome:** `OUT-2` — Sustainable delivery process
**Capability:** `CAP-2` — Security & Compliance Hardening
**Feature:** `FEAT-34` — Input validation & enum guards
**Classification:** `technical enabler`
**Status:** `backlog`
**Confidence:** `requires human classification`

## Actor

engineer

## Problem addressed

`proration_strategy` accepts an arbitrary string. An invalid value is stored silently and the engine falls back with no error, so a typo produces a wrong proration basis rather than a failure. An API-level guard was added; the database itself is still unguarded, so any writer that bypasses the route can still store nonsense.

## Delivered behaviour

**Not delivered.** Recorded here because the item was open in `docs/ROADMAP.md` and carried no `STORY-<nnnn>`.

## Acceptance criteria

**This item is not delivered.** It is recorded so that an allocated identifier exists and its absence from the delivered set is explicit rather than silent. If it is ever scheduled, criteria are written in the sprint that takes it.

## Source reference

`docs/ROADMAP.md` Track S security register, S6 — ⬜ "DB constraint pending" (API guard shipped ✅).

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

- Sprint 14 — raised as S6 from security report SEC-S5. API guard added; DB CHECK constraint still missing.
- 2026-07-29 — allocated and recorded by the `roadmap-split` sprint (`STORY-0160`).

## Unresolved questions

Not delivered. Note this is a **partial** item — the roadmap marks it ⬜ but its API half shipped. The residual is the DB constraint alone, and a migration adding it must pre-check for existing invalid rows before applying, per the standing migration rule.
