# `PT-A1-18` — WorkspaceConfig.tsx full interactive overhaul (Gate 6)

**Outcome:** `OUT-3` (see `../OUTCOMES.md`)
**Capability:** `CAP-3` (see `../CAPABILITIES.md`)
**Feature:** `FEAT-3` (see `../FEATURES.md`)
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

Payroll operator / bureau setup admin managing a workspace's configuration after onboarding.

## Problem addressed

Before Track J, `WorkspaceConfig.tsx` was a read-only display of onboarding-time configuration — any correction required a full Excel re-upload. There was no single screen where an operator could review and interactively manage pay cycle, grades, designations, salary definitions, payroll rules, and statutory component overrides.

## Delivered behaviour

`WorkspaceConfig.tsx` is the single interactive screen for post-onboarding configuration management, assembling every WC-1→WC-11 SlideOver into one page: Edit Pay Cycle, Add/Edit Grade, Add/Edit Designation, Add/Edit Salary Definition, Toggle (now Withdraw) Payroll Rule, Add Payroll Rule, Edit/Add Component Override, plus Add Rate Code. `docs/ROADMAP.md`'s own Gate 6 completion note lists the SlideOvers it considers delivered: "AddGrade, EditGrade, AddDesignation, EditDesignation, EditSalaryDef, EditPayrollRule, EditPayrollConfig, AddRateCode" (this list does not separately name "AddSalaryDef" — see `PT-A1-09`'s Unresolved questions for the discrepancy that surfaced during this migration pass).

## Source reference

`docs/ROADMAP.md` Track J item 43 ("Frontend: WorkspaceConfig.tsx full interactive overhaul (Gate 6) | Onboarding (A1+A2) | WC-1→WC-11 | See Gate 6 in UI track") and the Track UI table, Gate 6 row: "Post-Onboarding Config Management — WorkspaceConfig.tsx interactive overhaul (WC-1→WC-11, Track J) | ✅ | Completed (all SlideOvers: AddGrade, EditGrade, AddDesignation, EditDesignation, EditSalaryDef, EditPayrollRule, EditPayrollConfig, AddRateCode)".

## Implementation evidence

- `frontend/src/pages/WorkspaceConfig.tsx` — confirmed by direct inspection during this migration pass to contain `AddSalaryDefSlideOver` (line 1629) and the state/handlers for all of the WC-* SlideOvers referenced by `PT-A1-07` through `PT-A1-11`.
- Commit `db17ef9` (2026-04-22) — the single Track J delivery commit covering this whole page overhaul; not decomposed into a per-SlideOver diff in this pass.

## Test / review evidence

- `docs/test-reports/2026-04-21-track-j.md` — this is the umbrella test report for the whole page: 18 API verifications across WC-1 through WC-11, overall verdict "PASS with 2 known gaps" (the duplicate-code 500 and the not-yet-implemented WC-6 add flow, both documented in this batch's other story records). TypeScript compile check ("`npx tsc --noEmit` — no errors") recorded in the same report's Environment section.

## Decision references

- All 8 Track J arch-council decisions (D-ARCH-1 through D-ARCH-8, `docs/stories/track-j-workspace-config-management.md`) apply to this page as their combined delivery surface.
- `D-016` (`docs/programmes/product-traceability/decisions.md`) — authorises this story's migration into `docs/product/` as part of the Phase 4B confirmed-batch.

## Dependencies

Composed of `PT-A1-07`, `PT-A1-08`, `PT-A1-09`, `PT-A1-10`, `PT-A1-11` (the individual WC-* stories) and depends on `PT-A1-15` (the blocking migration) and `PT-A1-17` (the extended `/configuration` GET this page reads from). This is a rollup/assembly story, not an independent feature.

## Delivery sprint(s)

Track J (Gate 6 / Sprint 8 parallel track), delivered 2026-04-22 (commit `db17ef9`).

## Delivery history

- 2026-04-21/22 — Track J / Gate 6 — full interactive overhaul of `WorkspaceConfig.tsx` delivered (commit `db17ef9`); overall verdict PASS with 2 known gaps per `docs/test-reports/2026-04-21-track-j.md`.
- 2026-07-05 — Payroll Rule toggle superseded by one-way Withdraw action on this same page (commit `0a2702d`) — see `PT-A1-10` for detail.
- 2026-07-15 — Phase 4B confirmed-batch migration into `docs/product/` (D-016).

## Unresolved questions

This story is a rollup of the individual WC-* stories in this batch; see each individual story's own Unresolved questions (notably `PT-A1-09`'s flagged WC-6 evidence gap) rather than duplicating them here.
