# `STORY-0059` — `ot_multiplier` rules onboarded via Excel/JSON

**Origin code(s):** `PT-A1-13` · `PH-8` · `WI-05`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-3` — Onboarding & Workspace Setup
**Feature:** `FEAT-7` — Public holiday & rate-code configuration
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

bureau setup admin

## Problem addressed

Overtime multiplier rules had to be created by hand after onboarding, so a client workspace was never fully set up by its onboarding file alone.

## Delivered behaviour

`ot_multiplier` payroll rules can be supplied through the onboarding Excel/JSON path and are created as part of workspace setup.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` PH-8 / WI-05; `docs/stories/client-b-sprint-10-engine-ot-foundations.md`.

## Implementation evidence

Onboarding ingestion path — rule creation from the Excel/JSON payload.

## Test / review evidence

`docs/test-reports/2026-05-01-sprint-10.md`

## Decision references

None.

## Dependencies

`STORY-0036` — the rate-code registry the multipliers reference; `STORY-0064` — the Excel rule-type parsing this depends on.

## Delivery sprint(s)

Sprint 7 (design) / Sprint 10 (delivery).

## Delivery history

- Sprint 7 — specified as PH-8.
- Sprint 10 — delivered with the Excel parsing work (`STORY-0064`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
