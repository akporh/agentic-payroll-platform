# `STORY-0098` — Gate 5 — Navigation modernisation and the Rate Codes page

**Origin code(s):** `PT-UI-05` · `UI-NAV-1` · `UI-NAV-2` · `UI-NAV-3`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-9` — Design System & Navigation
**Feature:** `FEAT-17` — Navigation & information architecture
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

payroll operator; bureau setup admin

## Problem addressed

Navigation had accreted as pages were added, so related functions sat far apart and some delivered capability — the rate-code registry among it — had no page at all.

## Delivered behaviour

A modernised navigation structure plus a Rate Codes page surfacing the registry delivered in Sprint 7.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track UI, Gate 5 (UI-NAV-1/2/3).

## Implementation evidence

`frontend/src/` navigation structure; Rate Codes page.

## Test / review evidence

`docs/test-reports/2026-05-13-sprint-16.md`

## Decision references

Navigation and information-architecture decisions are recorded in `docs/design/ui-decisions.md`.

## Dependencies

`STORY-0036` — the rate-code registry the new page surfaces.

## Delivery sprint(s)

Track UI — Gate 5 (Sprint 16 period).

## Delivery history

- Track UI Gate 5 — delivered.
- 2026-05-26 — nav reorder plus the employee-mismatch badge (`STORY-0100`).
- Sprint 25 — sidebar badge behaviour corrected (`STORY-0113`, `STORY-0114`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

A UI gap audit conducted later found delivered capability still unreachable from navigation; that audit is owned outside this record.
