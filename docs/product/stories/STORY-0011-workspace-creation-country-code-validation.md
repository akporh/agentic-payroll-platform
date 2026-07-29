# `STORY-0011` — Workspace creation with country-code statutory-rule validation

**Origin code(s):** `PT-A1-03` · `P3-7`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-3` — Onboarding & Workspace Setup
**Feature:** `FEAT-6` — Client onboarding & workspace creation
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

bureau setup admin

## Problem addressed

A workspace could be created for a country with no statutory rule set loaded, producing a workspace that looked valid but could never run payroll correctly.

## Delivered behaviour

Workspace creation validates the supplied country code against the statutory rules the platform actually holds, and rejects a workspace it cannot compute statutory deductions for.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability area A1, item P3-7.

## Implementation evidence

`backend/api/routes/` workspace creation route; `statutory_rule` lookup by `country_code`.

## Test / review evidence

None dedicated — Sprints 1–6 predate the per-sprint test-report convention.

## Decision references

None.

## Dependencies

`STORY-0026` — the `statutory_rule` uniqueness constraint this validation reads against.

## Delivery sprint(s)

Sprints 1–6 (Core MVP).

## Delivery history

- Sprints 1–6 — delivered as part of core MVP workspace setup.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report exists for this period; confidence is `strongly inferred` from the roadmap's ✅ plus the surrounding delivered surface.
