# `STORY-0057` — Gate 4 bureau / workspace-setup journey, 8 pages — delivery CONTRADICTED

**Origin code(s):** `PT-UI-04`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-9` — Design System & Navigation
**Feature:** `FEAT-16` — Operator & bureau journeys
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `tentative`

## Actor

bureau setup admin

## Problem addressed

Setting up a new client workspace had no designed journey — the setup admin assembled a workspace from individually-reachable pages with no guided path.

## Delivered behaviour

Eight pages covering the bureau/workspace-setup journey. `docs/ROADMAP.md` marks the gate ✅ complete.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/ux-ui-upgrade-stories/gate-4-bureau-workspace-setup.md`; `docs/ROADMAP.md` Track UI, Gate 4.

## Implementation evidence

`frontend/src/pages/` workspace-setup journey pages.

## Test / review evidence

`docs/test-reports/2026-04-15-gate3-gate4.md`.

## Decision references

D-012 (resolving DP-06) — resolved as *investigate before trusting either source*, explicitly **not** as closed.

## Dependencies

`STORY-0045` — the design system these pages are built from.

## Delivery sprint(s)

Track UI — Gate 4 (April 2026).

## Delivery history

- Track UI Gate 4 — recorded ✅ in `docs/ROADMAP.md`.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

**An unresolved contradiction between two authoritative sources, migrated as a contradiction rather than resolved.** `docs/ROADMAP.md` marks Gate 4 ✅ complete, while its own story file `docs/stories/ux-ui-upgrade-stories/gate-4-bureau-workspace-setup.md` says "Plan approved, implementation pending". The discovery pass resolved this provisionally in favour of the roadmap because it is later-dated, and set confidence to `tentative`. This is D-012/DP-06 and remains an open follow-up owned outside this programme. **Do not cite this item as evidence that the Gate 4 journey is delivered.**
