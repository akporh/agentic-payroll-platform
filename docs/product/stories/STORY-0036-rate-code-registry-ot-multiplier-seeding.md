# `STORY-0036` — Rate-code registry and OT multiplier seeding (PH-7)

**Origin code(s):** `PT-A1-02` · `PH-7`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-3` — Onboarding & Workspace Setup
**Feature:** `FEAT-7` — Public holiday & rate-code configuration
**Classification:** `platform capability`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

bureau setup admin

## Problem addressed

Overtime and shift-allowance multipliers had no canonical registry — rates were duplicated inline in rule definitions with no single source of truth and no agreed home for pensionability semantics.

## Delivered behaviour

A `rate_code_registry` table with the platform OT codes (OT001–OT007) seeded, plus a read endpoint and UI view. The registry deliberately carries **no** `is_pensionable` column: by arch-council decision pensionability lives in `component_metadata` instead.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` PH-7, with the arch-council decision recorded inline ("pension via component_metadata not registry"); `docs/stories/arch-council-sprint7-decisions.md`.

## Implementation evidence

`rate_code_registry` table and seed migration; rate-code read route; Rate Codes UI page (delivered under Gate 5 — `STORY-0098`).

## Test / review evidence

`docs/test-reports/2026-04-14-sprint-7.md`

## Decision references

Arch-council, Sprint 7 — pensionability is a component-metadata concern, not a rate-registry concern.

## Dependencies

None.

## Delivery sprint(s)

Sprint 7.

## Delivery history

- Sprint 7 — delivered, with one sub-item deferred: the `component_metadata` row for `PH_OT` was seeded but its `is_pensionable=true` flag was intentionally held until the `PH_OT` handler could ship atomically.
- Sprint 10 — `ot_code` → `rate_code` normalisation (`STORY-0063`) and Excel rule-type parsing (`STORY-0064`) built on this registry.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

**The `PH_OT` `is_pensionable` deferral (ROADMAP OQ1) has never been found resolved in any later sprint.** Recorded as D-010/DP-04 and carried as an open follow-up owned outside this programme. Registry constraints discovered later and recorded outside this record: `unit` must be singular (`hour`/`day`), `base` must be `basic_hourly`/`basic_daily`, and `description` is NOT NULL.
