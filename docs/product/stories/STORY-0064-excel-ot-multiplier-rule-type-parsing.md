# `STORY-0064` — Excel `ot_multiplier` rule-type parsing

**Origin code(s):** `PT-A1-47` · `WI-05`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-3` — Onboarding & Workspace Setup
**Feature:** `FEAT-7` — Public holiday & rate-code configuration
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

bureau setup admin

## Problem addressed

The onboarding workbook could not express an `ot_multiplier` rule type, so overtime rules could not be onboarded from file.

## Delivered behaviour

The onboarding Excel parser recognises the `ot_multiplier` rule type and constructs the corresponding payroll rule.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` WI-05.

## Implementation evidence

Onboarding Excel parsing — rule-type handling.

## Test / review evidence

`docs/test-reports/2026-05-01-sprint-10.md`

## Decision references

Rule-definition field schemas per calculation method are recorded outside this programme; `ot_multiplier` is one of the six live `calculation_method` values, and rule type is not the same thing as calculation method.

## Dependencies

`STORY-0059` — the onboarding path this enables.

## Delivery sprint(s)

Sprint 10.

## Delivery history

- Sprint 10 — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
