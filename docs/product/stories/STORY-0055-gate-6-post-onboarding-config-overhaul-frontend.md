# `STORY-0055` — Gate 6 — Post-onboarding configuration management overhaul (frontend)

**Origin code(s):** `PT-UI-06`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-9` — Design System & Navigation
**Feature:** `FEAT-16` — Operator & bureau journeys
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

bureau setup admin

## Problem addressed

Once onboarding was complete, a workspace's configuration was effectively frozen from the operator's point of view — every correction required an engineer.

## Delivered behaviour

The frontend half of Track J: a fully interactive workspace-configuration surface covering grades, designations, salary definitions, payroll rules, statutory overrides and pay cycles. Gate 6 and Track J close together — this record is the design-system/journey view of the same delivery whose backend stories are `STORY-0046`–`STORY-0054`.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/track-j-workspace-config-management.md`; `docs/ROADMAP.md` Track UI, Gate 6.

## Implementation evidence

`frontend/src/pages/WorkspaceConfig.tsx` and its slide-overs — see `STORY-0054` for the page-level record.

## Test / review evidence

`docs/test-reports/2026-04-21-track-j.md`.

## Decision references

Track J arch-council decisions D-ARCH-1 – D-ARCH-8 govern this surface; D-ARCH-2 (statutory hard reject) is visible in it as `STORY-0052`.

## Dependencies

`STORY-0054` — the same delivery recorded as the WorkspaceConfig page overhaul; `STORY-0046`–`STORY-0053` — the endpoints it drives.

## Delivery sprint(s)

Track J / Gate 6 (2026-04-21).

## Delivery history

- Track J / Gate 6 — delivered; UI gate and backend track closed together.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

This item and `STORY-0054` describe the same delivery from the Track UI and capability-area A1 viewpoints respectively. They are kept as two records because the discovery inventory carried both codes and the two registers are independently navigable; the overlap is stated here rather than resolved by deleting one.
