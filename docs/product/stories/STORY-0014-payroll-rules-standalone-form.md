# `STORY-0014` — Payroll rules entered as a standalone form, not raw JSON

**Origin code(s):** `PT-A1-06` · `P3-1`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-3` — Onboarding & Workspace Setup
**Feature:** `FEAT-3` — Post-onboarding configuration management
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

bureau setup admin

## Problem addressed

Payroll rules had to be entered as raw JSON, which is unusable by a bureau operator and makes a malformed rule an easy and silent mistake.

## Delivered behaviour

A structured form for creating and editing a payroll rule, with the fields appropriate to the rule's calculation method rather than a free-text JSON blob.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability area A1, item P3-1.

## Implementation evidence

`frontend/src/pages/` payroll rules form; `payroll_rule.rule_definition_json`.

## Test / review evidence

None dedicated — Sprints 1–6 predate the per-sprint test-report convention.

## Decision references

None.

## Dependencies

None.

## Delivery sprint(s)

Sprints 1–6 (Core MVP).

## Delivery history

- Sprints 1–6 — delivered.
- Track J — active/inactive control added (`STORY-0049`).
- Sprint RULE-VER-1 — superseded by effective-dated versioning (`STORY-0132`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report exists for this period. The form's field set is method-dependent; a later finding recorded outside this programme is that `calculation_method` must be treated as read-only on edit because the live method set is wider than the rule-type options the form offers.
