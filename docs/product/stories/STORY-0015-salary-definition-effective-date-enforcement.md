# `STORY-0015` — Salary definition effective-date enforcement at run time

**Origin code(s):** `PT-A1-12` · `P3-5`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-3` — Onboarding & Workspace Setup
**Feature:** `FEAT-3` — Post-onboarding configuration management
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator; auditor

## Problem addressed

A salary definition edited after a period had been worked would otherwise apply retroactively to that period, changing history.

## Delivered behaviour

The engine resolves a salary definition by its effective date against the run's period rather than taking the latest row unconditionally.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability area A1, item P3-5.

## Implementation evidence

`salary_definition` effective-date resolution in the run start path.

## Test / review evidence

None dedicated — Sprints 1–6 predate the per-sprint test-report convention.

## Decision references

Related: `salary_definition.components_jsonb` is read live at run start, which is why Track J's D-ARCH-1 edit-lock was required before any post-onboarding PATCH was allowed.

## Dependencies

None.

## Delivery sprint(s)

Sprints 1–6 (Core MVP).

## Delivery history

- Sprints 1–6 — delivered.
- Track J — edit path added behind the D-ARCH-1 run-lock (`STORY-0048`, `STORY-0101`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report exists for this period.
