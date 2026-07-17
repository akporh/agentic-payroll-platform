# `PT-A1-39` — Workspace activation CTA reachable from 3 landing points

**Outcome:** `OUT-3` (see `../OUTCOMES.md`)
**Capability:** `CAP-3` (see `../CAPABILITIES.md`)
**Feature:** `FEAT-4` (see `../FEATURES.md`)
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

Payroll bureau operator whose workspace has reached `READY` status and now needs to transition it to `LIVE` before any payroll run can be created.

## Problem addressed

The `READY → LIVE` activation endpoint already existed (`POST /{workspace_id}/transition?target_state=LIVE`), but the only UI path to it was buried in Step 4 of the `WorkspaceSetup.tsx` onboarding wizard — reachable only if the operator had navigated the full wizard in one session. Three other natural landing points (the `WorkspaceConfig` page, the `PayrollRuns` page, and `WorkspaceSetup`'s read-only `ExistingConfigView` for a workspace visited outside the wizard) had no activation path at all; `PayrollRuns` actively misdirected READY workspaces back to the wizard with a "Continue Setup →" button that led nowhere useful.

## Delivered behaviour

All three gaps are closed, with no backend changes required (the transition endpoint already existed): `WorkspaceConfig.tsx` gains a primary "Activate Workspace →" button in its header when `status === 'READY'`, behind a `ConfirmDialog`; `PayrollRuns.tsx`'s READY-state banner changes from an `info` "Complete the setup wizard" (with a dead-end "Continue Setup →" link) to a `success` "Setup complete" banner with an inline "Activate Workspace →" action (no navigation away from the page); `WorkspaceSetup.tsx`'s `ExistingConfigView` gains a `success` AlertBanner at the top of the page for READY workspaces with the same inline activation flow. All three use an identical pattern: button → `ConfirmDialog` → `workspaceApi.transition(workspaceId, 'LIVE')` → optimistic local status update + success/error `AlertBanner`.

## Source reference

`docs/stories/fix-workspace-activation-cta.md` — full background, the three-landing-point gap table, UX strategy rationale, and per-story acceptance criteria (WS-ACTIVATE-1/2/3).

## Implementation evidence

- `docs/stories/fix-workspace-activation-cta.md`, "Files Changed" table: `frontend/src/pages/WorkspaceConfig.tsx` (WS-ACTIVATE-1), `frontend/src/pages/PayrollRuns.tsx` (WS-ACTIVATE-2), `frontend/src/pages/WorkspaceSetup.tsx` (WS-ACTIVATE-3). Explicitly states "No backend changes. No migration. No new dependencies."
- `"Activate Workspace"` string confirmed present in `frontend/src/pages/WorkspaceConfig.tsx` by `git log -S`, isolating commit `98f2100`.
- Commit `98f2100` (2026-06-15) — same bundled commit as `PT-A1-38`; this fix and the EMP-REG-5 fix shipped together with Sprint 27/28.

## Test / review evidence

- The story file provides itemised acceptance criteria per surface (WS-ACTIVATE-1/2/3), each as a checklist (`- [ ]`), not marked as executed/checked in the file itself. No separately named test report was found verifying these specific acceptance criteria as executed and passed; the fix is bundled into the same commit as the Sprint 27/28 work (`docs/test-reports/2026-06-15-sprint-27-28.md`), but this pass did not find that report calling out the workspace-activation-CTA fix by name.

## Decision references

- None recorded beyond routine execution — the story file frames this purely as UI-coverage completion of an already-existing, already-approved backend transition endpoint.
- `D-016` (`docs/programmes/product-traceability/decisions.md`) — authorises this story's migration into `docs/product/` as part of the Phase 4B confirmed-batch.

## Dependencies

None. Purely additive UI coverage of an existing endpoint; no migration, no other story's completion is a precondition.

## Delivery sprint(s)

Fix sprint, 2026-06-13 (per the story file's own date header), landed in commit `98f2100` (dated 2026-06-15 — see Unresolved questions for this date discrepancy).

## Delivery history

- 2026-06-13/15 — fix sprint — activation CTA added to `WorkspaceConfig`, `PayrollRuns`, and `WorkspaceSetup`'s `ExistingConfigView` (commit `98f2100`); story file states all three landing points now have a working activation path.
- 2026-07-15 — Phase 4B confirmed-batch migration into `docs/product/` (D-016).

## Unresolved questions

The story file's own header date is "2026-06-13," but the commit found in this pass (`98f2100`) is dated 2026-06-15 — a two-day gap not explained by any evidence found in this pass (possibly the story was drafted before the commit landed, or the commit bundles several days' work; not resolved here). No dedicated test report was found confirming the itemised acceptance criteria (which remain unchecked `- [ ]` checkboxes in the source story file) as executed and passed — this is carried forward honestly rather than treated as verified.
