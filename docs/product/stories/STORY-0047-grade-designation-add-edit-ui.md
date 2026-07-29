# `STORY-0047` — WC-2/3/4/5: Grade/designation add + edit via UI

**Origin code(s):** `PT-A1-08` · `WC-2/3/4/5`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-3` — Onboarding & Workspace Setup
**Feature:** `FEAT-3` — Post-onboarding configuration management
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

Payroll bureau setup admin who needs to add a new grade/designation band, or correct a grade/designation description, after initial onboarding.

## Problem addressed

Grades and designations were fixed at onboarding time. Adding a new employee band, or fixing a typo in a description, had no path other than a full Excel re-upload.

## Delivered behaviour

`WorkspaceConfig.tsx` has "Add Grade" / "Add Designation" SlideOvers (code + optional description; code uppercased and enforced unique per workspace — duplicate returns a named error) and per-row Edit SlideOvers for descriptions only (the `grade_code`/`designation_code` field is shown read-only/locked — codes are immutable after creation). Backed by dedicated PATCH/POST endpoints scoped to `workspace_id`.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track J item 38 (`WC-3/WC-5`) plus the item-220/221 ROADMAP Story Index lines (`WC-2/WC-4`, `WC-3/WC-5`); full acceptance criteria in `docs/stories/track-j-workspace-config-management.md`, sections "WC-2" through "WC-5".

## Implementation evidence

- `docs/stories/track-j-workspace-config-management.md` — WC-2 through WC-5 acceptance criteria (uppercasing, uniqueness, locked-code edit form).
- `docs/ROADMAP.md` line 220/221: "Add grade / designation post-onboarding via UI ✅ (WC-2/WC-4, Track J)"; "Edit grade / designation description via UI ✅ (WC-3/WC-5, Track J)".
- Commit `db17ef9` — Track J delivery commit; not independently isolated to a WC-2/3/4/5-only diff in this pass.

## Test / review evidence

- `docs/test-reports/2026-04-21-track-j.md` — Sprint Items Verified: WC-2 PASS/PASS ("Code uppercased, appears in table. Duplicate = 500 (see bugs)"), WC-3 PASS/PASS, WC-4 PASS/PASS ("Mirrors WC-2. Duplicate = 500 (see bugs)"), WC-5 PASS/PASS. The same report's Known Pre-Existing Issues section records that a duplicate grade/designation POST returns an unhandled HTTP 500 (raw psycopg2 IntegrityError) rather than a user-friendly 422 — logged as a pre-existing gap, not a regression, and not closed within this story's scope.

## Decision references

- D-ARCH-5 (workspace isolation on all UPDATE queries) — `docs/stories/track-j-workspace-config-management.md`.
- `D-016` (`docs/programmes/product-traceability/decisions.md`) — authorises this story's migration into `docs/product/` as part of the Phase 4B confirmed-batch.

## Dependencies

None. Additive CRUD-style endpoints on `grade`/`designation`; no other story's completion is a precondition.

## Delivery sprint(s)

Track J (Gate 6 / Sprint 8 parallel track), delivered 2026-04-22 (commit `db17ef9`).

## Delivery history

- 2026-04-21/22 — Track J — Add/Edit Grade and Designation SlideOvers + endpoints delivered (commit `db17ef9`); verified PASS per `docs/test-reports/2026-04-21-track-j.md`.
- 2026-07-15 — Phase 4B confirmed-batch migration into `docs/product/` (D-016).

## Unresolved questions

The duplicate-code path returns an unhandled HTTP 500 (bubbled DB IntegrityError) rather than a 422, per the Track J test report's own "Known Pre-Existing Issues" section. This is a pre-existing defect noted at delivery time, explicitly out of this story's scope to fix, and (per this repository's API Route Rules) is the kind of raw-exception leak that should eventually be closed — it is carried forward here as a known gap, not silently fixed or hidden.
