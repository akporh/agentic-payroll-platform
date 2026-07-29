# `STORY-0137` — Stale copy and banner cleanup on the Payroll Rules tab

**Origin code(s):** `PT-UI-07` · `B-UI-4` · `B-UI-5`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-9` — Design System & Navigation
**Feature:** `FEAT-17` — Navigation & information architecture
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

bureau setup admin

## Problem addressed

Copy and banners written for the pre-versioning behaviour survived the versioning change, telling the operator things about rules that were no longer true.

## Delivered behaviour

Stale copy and banners on the Payroll Rules tab are corrected to describe versioned behaviour.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Sprint B-UI (B-UI-4/5).

## Implementation evidence

`frontend/src/` payroll rules tab copy and banners.

## Test / review evidence

None dedicated — the roadmap records B-UI-4/5 as ✅ complete.

## Decision references

The rule-versioning sprint's retro recorded the general lesson this item is the instance of: removing or changing a feature requires a copy audit, because prose describing the old behaviour does not fail loudly.

## Dependencies

`STORY-0136` — delivered as the same clean-up pass.

## Delivery sprint(s)

Sprint B-UI.

## Delivery history

- Sprint B-UI — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report for Sprint B-UI.
