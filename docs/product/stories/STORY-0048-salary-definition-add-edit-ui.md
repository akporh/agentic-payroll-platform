# `STORY-0048` — WC-6/7: Salary definition add + edit via UI

**Origin code(s):** `PT-A1-09` · `WC-6/7`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-3` — Onboarding & Workspace Setup
**Feature:** `FEAT-3` — Post-onboarding configuration management
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

Payroll operator who needs to introduce a new salary band, or adjust an existing salary definition's components (e.g. after an approved salary review), after initial onboarding.

## Problem addressed

New employee grades/salary bands and routine salary reviews are common mid-year events. Before this story, the only path to add or change a salary definition's components was a full Excel re-upload of the workspace configuration.

## Delivered behaviour

`WorkspaceConfig.tsx` has an "Add Salary Definition" SlideOver (`name` + unique `code` + a component table with BASIC/HOUSING/TRANSPORT mandatory rows, plus optional additional rows; amounts must be positive; save is rejected with a 422 if the three mandatory components are missing) and an "Edit" action per salary-definition row that opens a component-table editor (same mandatory-component rules, plus an in-SlideOver `AlertBanner` warning that changes only apply to future runs). The edit path is protected by the D-ARCH-1 edit-lock: PATCH is rejected with 409 if any run for the workspace is in `SUBMITTED | PROCESSING | CALCULATED | PARTIAL | APPROVED` status and an employee on that run has a contract pointing at this salary definition. Both add and edit are scoped by `workspace_id` (D-ARCH-5).

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track J item 39 (`WC-7`, ref D-ARCH-1/D-ARCH-5); full acceptance criteria in `docs/stories/track-j-workspace-config-management.md`, sections "WC-6 — Add a New Salary Definition" and "WC-7 — Edit a Salary Definition (Components)".

## Implementation evidence

- `backend/api/routes/workspace.py:939` — `create_salary_definition_endpoint` (`POST /{workspace_id}/salary-definition`), and `backend/api/routes/workspace.py:1507` — `patch_salary_definition` (`PATCH /{workspace_id}/salary-definition/{salary_definition_id}`), both confirmed present in the current codebase by direct inspection during this migration pass.
- `frontend/src/pages/WorkspaceConfig.tsx:1629` — `AddSalaryDefSlideOver` component, confirmed present by direct inspection during this migration pass.
- Commit `db17ef9` (2026-04-22) — `git log -S "AddSalaryDefSlideOver"` and `git log -S "create_salary_definition_endpoint"` both isolate this single commit as the one that introduced the add-flow frontend component and backend endpoint respectively.

## Test / review evidence

- `docs/test-reports/2026-04-21-track-j.md` — WC-7 (edit) verified **PASS**/PASS: "D-ARCH-1 409 guard ✓, mandatory lock ✓, list format accepted ✓". **WC-6 (add) is recorded in the same report as a GAP**: "Add SlideOver not implemented; only Edit. See deferred" — the report's own Deferred section states: "WC-6 Add Salary Definition SlideOver | Not implemented in this sprint. Salary defs can still be added via Excel upload... Tracked as a future story."
- The `db17ef9` commit that added `AddSalaryDefSlideOver` and the `POST /salary-definition` endpoint is dated 2026-04-22, one day after the 2026-04-21 Track J test report — consistent with the add-flow landing just after that report was written, not before it.
- No later dedicated test report re-verifying the WC-6 add flow specifically was found in this pass. `docs/ROADMAP.md`'s Gate 6 completion note (line 494) lists the SlideOvers it considers delivered ("AddGrade, EditGrade, AddDesignation, EditDesignation, EditSalaryDef, EditPayrollRule, EditPayrollConfig, AddRateCode") and does **not** name an "AddSalaryDef" SlideOver in that list, even though the code demonstrably exists today.

## Decision references

- D-ARCH-1, D-ARCH-5 (`docs/stories/track-j-workspace-config-management.md`).
- `D-016` (`docs/programmes/product-traceability/decisions.md`) — authorises this story's migration into `docs/product/` as part of the Phase 4B confirmed-batch.

## Dependencies

None. Additive endpoint + SlideOver; no other story's completion is a precondition.

## Delivery sprint(s)

Track J (Gate 6 / Sprint 8 parallel track). WC-7 (edit) verified 2026-04-21; WC-6 (add) code landed 2026-04-22 (commit `db17ef9`), after the dated test report.

## Delivery history

- 2026-04-21 — Track J — WC-7 (edit salary definition) delivered and verified PASS per `docs/test-reports/2026-04-21-track-j.md`; WC-6 (add) recorded as not-yet-implemented in the same report.
- 2026-04-22 — Track J — WC-6 (add salary definition) SlideOver + `POST /{wid}/salary-definition` endpoint landed (commit `db17ef9`), the day after the WC-7 test report.
- 2026-07-15 — Phase 4B confirmed-batch migration into `docs/product/` (D-016).

## Unresolved questions

**Flagged for reviewer attention:** the discovery document classifies this whole item (WC-6+WC-7) as `confirmed`, but the primary dated test-report evidence (`docs/test-reports/2026-04-21-track-j.md`) explicitly records WC-6 (the add flow) as a **GAP, not implemented** at that date — the opposite of confirmed delivery. Direct inspection in this migration pass found the add-flow code (frontend `AddSalaryDefSlideOver` and backend `POST /salary-definition`) genuinely present today, landed the day after that test report per `git log`. So the feature is real and in the codebase, but there is no dedicated test report verifying the add flow specifically (only the edit flow, WC-7, was ever test-reported as PASS) and the ROADMAP's own Gate 6 completion note omits "AddSalaryDef" from its list of completed SlideOvers. This item is migrated as `confirmed` on the strength of the direct code inspection performed in this pass, but the test/review evidence for the add half specifically is thinner than the discovery document's blanket `confirmed` label implies — a future pass should either locate a WC-6-specific verification record or commission one.
