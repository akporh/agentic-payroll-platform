# `STORY-0035` — Workspace-configurable public-holiday engine (PH-1 – PH-11)

**Origin code(s):** `PT-A1-01` · `PH-1`…`PH-11`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-3` — Onboarding & Workspace Setup
**Feature:** `FEAT-7` — Public holiday & rate-code configuration
**Classification:** `platform capability`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator; bureau setup admin

## Problem addressed

Public holidays were not modelled at all. Overtime and holiday pay could not be calculated correctly around national or workspace-specific holidays, and there was no way to represent how a workspace treats a holiday that falls on a weekend.

## Delivered behaviour

`NationalPublicHoliday` and `WorkspacePublicHoliday` tables; a source-tagged immutable snapshot taken at run approval; weekend-PH classification configuration; `WorkspacePayrollConfig` carrying `ph_mode` and the D3/D4 flags, versioned by `effective_from`; a PH pre-flight check; and PH count-mismatch warnings surfaced in the execution trace.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Phase 1b Tracks B/C/D (PH-1, PH-2, PH-2b, PH-6, PH-9, PH-10, PH-11); design in `docs/stories/phase1-sprint7-public-holiday.md` and `docs/stories/phase1-sprint7-public-holiday-ui.md`; arch-council decisions in `docs/stories/arch-council-sprint7-decisions.md`.

## Implementation evidence

PH handlers under `backend/domain/payroll/`; migrations creating `NationalPublicHoliday`, `WorkspacePublicHoliday` and `WorkspacePayrollConfig`.

## Test / review evidence

`docs/test-reports/2026-04-14-sprint-7.md`, `docs/test-reports/2026-04-21-sprint-7-wc12-wc13.md`.

## Decision references

Arch-council, Sprint 7: pensionability lives in `component_metadata`, not in the rate-code registry — see `STORY-0036`.

## Dependencies

`STORY-0036` — the rate-code registry the PH/OT multipliers resolve against.

## Delivery sprint(s)

Sprint 7 (Tracks B/C/D).

## Delivery history

- Sprint 7 — delivered; PH-7's `is_pensionable` flag on `PH_OT` explicitly deferred (see `STORY-0036`).
- Sprint 10 — `PH_ADDITIVE` removed from the UI with a backend fallback (`STORY-0061`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

Migration-file existence for the PH tables was cited from the roadmap rather than re-read during discovery; that spot-check is what stands between this item and `confirmed`.
