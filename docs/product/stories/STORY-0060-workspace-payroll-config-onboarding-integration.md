# `STORY-0060` — `WorkspacePayrollConfig` onboarding integration — optional 7th Excel sheet

**Origin code(s):** `PT-A1-43` · `WI-06` · `H2`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-3` — Onboarding & Workspace Setup
**Feature:** `FEAT-6` — Client onboarding & workspace creation
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

bureau setup admin

## Problem addressed

`WorkspacePayrollConfig` — the PH mode and related payroll behaviour flags — could not be set during onboarding, so every new workspace needed a manual configuration step after its file was loaded.

## Delivered behaviour

An optional seventh sheet in the onboarding workbook carries the workspace payroll configuration, which is created as part of onboarding when present and defaulted when absent.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` WI-06 / H2.

## Implementation evidence

Onboarding ingestion — seventh-sheet parsing and `workspace_payroll_config` creation.

## Test / review evidence

`docs/test-reports/2026-05-01-sprint-10.md`

## Decision references

None.

## Dependencies

`STORY-0035` — the PH engine whose configuration this carries.

## Delivery sprint(s)

Sprint 10.

## Delivery history

- Sprint 10 — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
