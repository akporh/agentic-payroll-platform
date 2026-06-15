# Fix Sprint — Workspace Activation: Complete Surface Coverage

**Date:** 2026-06-13  
**Sprint goal:** Ensure an operator with a READY workspace can activate it from any natural landing point — never stranded, never sent to the wrong place.

---

## Background

The workspace lifecycle has six states: `DRAFT → STRUCTURE_DEFINED → COMPENSATION_DEFINED → RULES_DEFINED → READY → LIVE`. The `READY → LIVE` transition (activation) is required before any payroll run can be created. The API endpoint already existed (`POST /{workspace_id}/transition?target_state=LIVE`). The gap was purely UI coverage.

Before this sprint, the only activation path was buried in Step 4 of the `WorkspaceSetup.tsx` wizard — a path that required the operator to have navigated through all wizard steps in a single session. Three natural landing points had no activation CTA:

| Landing point | Status before fix | Why operators land here |
|---|---|---|
| `WorkspaceConfig` page | No activation CTA — READY badge with no action | Direct link, sidebar nav, post-config review |
| `PayrollRuns` page | "Continue Setup →" sent to wizard regardless of status | First place an operator goes to run payroll |
| `WorkspaceSetup` (ExistingConfigView) | Read-only config dump with no activation CTA | Navigated from "Continue Setup →" on PayrollRuns when READY |

All three gaps were fixed in this sprint. No backend changes were required.

---

## UX Strategy

**Target user:** Payroll bureau operator who has completed workspace configuration (status = READY). They are goal-blocked — they want to run payroll but the system is either silent about what to do next, or actively misleading them (sending them to a setup wizard when setup is done).

**Core insight:** READY and incomplete-setup are fundamentally different states. One means "you have more work to do." The other means "you have one button to press." Treating them identically — same copy, same destination — is the root cause of all three gaps.

**Key decisions:**

| Decision | Choice | Reason |
|---|---|---|
| PayrollRuns — READY banner variant | `success` (not `info`) | Setup is complete — that's positive. `info` implies something still wrong. |
| PayrollRuns — READY action | Inline ConfirmDialog, no navigation | Operator is already where they want to end up. Sending them elsewhere to press a button and come back is unnecessary friction. |
| WorkspaceSetup ExistingConfigView — banner position | Top of content, before all config sections | Impossible to miss. Cannot be in ContentHeader — ExistingConfigView is a sub-component with limited header control. |
| Confirmation copy | "Configuration can still be edited at any time." | The primary operator anxiety is "will this lock my config?" — address it directly. |
| ConfirmDialog styling | Default (not destructive/red) | Activation is not destructive. Nothing is deleted. No data is irreversible. |
| Post-activation — page behaviour | Optimistic local state update; no reload | Keeps the operator on the page they were on. No jarring navigation. |

---

## Story 1 — WS-ACTIVATE-1: Activate from WorkspaceConfig page

**Priority:** P1 · Operator Experience

```
As Sandy (payroll operator),
When my workspace status is READY and I am on the Configuration page,
I want a clear action to activate the workspace,
So that I can go live without returning to the setup wizard.
```

### What changed

**`frontend/src/pages/WorkspaceConfig.tsx`**

| Area | Change |
|---|---|
| State | Added `activateConfirmOpen`, `activating`, `activateSuccess`, `activateError` |
| Handler | `handleActivateConfirm()` — calls `workspaceApi.transition(workspaceId, 'LIVE')`, updates local `config.workspace.status` optimistically, sets success/error state |
| `ContentHeader` action | When `status === 'READY'`: renders primary "Activate Workspace →" alongside secondary "Re-upload Config". When status is anything else: primary button absent. |
| `ConfirmDialog` | Confirms intent before API call. |
| Banners | Success + error `AlertBanner` (dismissible) below `ContentHeader`, above load-error banner. |

### Acceptance Criteria

- [ ] Config page loads with `status = READY`: primary "Activate Workspace →" button visible in header
- [ ] Config page loads with `status = LIVE` or any pre-READY status: no activate button shown
- [ ] Clicking "Activate Workspace →": ConfirmDialog opens
- [ ] ConfirmDialog cancel: dialog closes, status unchanged, CTA still present
- [ ] ConfirmDialog confirm: API fires, button enters loading/disabled state
- [ ] On success: dialog closes, status badge → LIVE, CTA disappears, success AlertBanner shown
- [ ] On error: dialog closes, error AlertBanner shown, CTA still present (user can retry)

---

## Story 2 — WS-ACTIVATE-2: Correct PayrollRuns page for READY workspaces

**Priority:** P1 · Operator Experience

```
As Sandy (payroll operator),
When I navigate to the Payroll Runs page and my workspace is READY,
I want to see that setup is complete and be able to activate directly,
Instead of being sent to the setup wizard where nothing works.
```

### What changed

**`frontend/src/pages/PayrollRuns.tsx`**

| Area | Before | After |
|---|---|---|
| Status tracking | `isLive` bool only | `workspaceStatus` string + `isReady` derived bool |
| AlertBanner (READY) | `info` — "Complete the setup wizard to activate" + "Continue Setup →" navigates away | `success` — "Setup complete. Activate it to start running payroll." + "Activate Workspace →" (inline ConfirmDialog) |
| AlertBanner (pre-READY) | Same `info` banner | Unchanged — "Continue Setup →" still navigates to /setup |
| EmptyState (READY) | "Complete setup to unlock payroll runs" + "Continue Setup" | "Ready to activate" + "Activate Workspace →" (inline ConfirmDialog) |
| EmptyState (pre-READY) | Same as above | "Complete setup…" + "Continue Setup →" (unchanged) |
| Activation | Not possible | Inline ConfirmDialog + `workspaceApi.transition()` |
| Post-activation | N/A | `isLive` → true, `workspaceStatus` → 'LIVE', banners clear, "New Run" button enables |

**State/behaviour split by status:**

```
getOnboardingStatus() returns status string
  ├─ 'LIVE'          → normal run experience, no banners
  ├─ 'READY'         → success banner + "Activate Workspace →" (inline)
  │                     EmptyState: "Ready to activate" + same CTA
  └─ anything else   → info banner + "Continue Setup →" (navigate to wizard)
                        EmptyState: "Complete setup…" + same CTA
```

### Acceptance Criteria

- [ ] PayrollRuns loads with `status = READY`: success AlertBanner "Setup complete" visible with "Activate Workspace →" button
- [ ] PayrollRuns loads with `status = LIVE`: no banner; "New Run" button enabled
- [ ] PayrollRuns loads with status < READY: info AlertBanner "Complete workspace setup" with "Continue Setup →"
- [ ] Empty table + READY status: EmptyState shows "Ready to activate" with "Activate Workspace →"
- [ ] Empty table + pre-READY status: EmptyState shows "Complete setup…" with "Continue Setup →"
- [ ] "Activate Workspace →" (banner or empty state): opens ConfirmDialog inline — no navigation
- [ ] Activation success: banner clears, status updates to LIVE, "New Run" button becomes enabled
- [ ] Activation error: error AlertBanner shown (dismissible), success banner restored, user can retry

---

## Story 3 — WS-ACTIVATE-3: Activation CTA in WorkspaceSetup ExistingConfigView

**Priority:** P1 · Operator Experience

```
As Sandy (payroll operator),
When I land on the workspace setup page and my workspace is READY,
I want to see a clear activation prompt at the top of the page,
So that I can activate without having to navigate elsewhere.
```

### What changed

**`frontend/src/pages/WorkspaceSetup.tsx` — `ExistingConfigView` component only**

`ExistingConfigView` is the component rendered for any non-DRAFT workspace that visits the setup page. Before this fix it showed a static blue "read-only" notice with no path forward for READY workspaces.

| Area | Before | After |
|---|---|---|
| Top notice (READY) | Static blue "This workspace is READY. Configuration is read-only." | `success` AlertBanner — "Setup complete — one step left. Activate this workspace to enable payroll runs." + "Activate Workspace →" CTA |
| Top notice (READY, post-activation) | N/A | `success` AlertBanner — "Workspace is now live." (dismissible) |
| Top notice (LIVE / other) | Same blue notice | Static blue notice preserved (correct for non-READY non-DRAFT states) |
| Activation | Not possible | Local `handleActivate()` → `workspaceApi.transition()` + `activateSuccess` flag |
| ConfirmDialog | Absent | Added — same spec as WS-ACTIVATE-1 and WS-ACTIVATE-2 |
| Error handling | N/A | `activateError` AlertBanner (dismissible) |

**State management note:** `ExistingConfigView` receives `workspace` as a prop and cannot mutate it. Post-activation state is tracked via local `activateSuccess` bool — the banner switches from "activate" CTA to "now live" message, and the READY-gated CTA disappears. The workspace prop status remains `READY` in memory but the UI correctly reflects the live state.

### Acceptance Criteria

- [ ] Setup page visited with `status = READY`: green AlertBanner "Setup complete — one step left" shown at top, before all config sections
- [ ] Setup page visited with `status = LIVE` or other: blue read-only notice shown (unchanged)
- [ ] "Activate Workspace →" button in banner: opens ConfirmDialog
- [ ] Activation success: CTA banner replaced by "Workspace is now live." success banner (dismissible)
- [ ] Activation error: error AlertBanner shown (dismissible), READY banner and CTA restored
- [ ] Config sections below the banner remain fully visible and scrollable after activation

---

## Architecture Notes

### Consistent activation pattern (all three surfaces)

All three activation points use identical flow and components:

```
"Activate Workspace →" button
  └─ ConfirmDialog
       title: "Activate workspace?"
       body: "Once active, this workspace is eligible to run payroll.
              Configuration can still be edited at any time."
       confirmLabel: "Activate →"
       loading: <activating state>
       ├─ Cancel → dialog closes, no change
       └─ Confirm → workspaceApi.transition(workspaceId, 'LIVE')
                      ├─ Success → optimistic local update + success AlertBanner
                      └─ Error   → extractError(e) → error AlertBanner (dismissible)
```

### `extractError` helper

`WorkspaceConfig.tsx` already had `extractError`. It was added fresh to both `PayrollRuns.tsx` and `WorkspaceSetup.tsx` as module-level functions (identical implementation). Not extracted to a shared utility — three usages across three files does not justify the indirection.

### Status tracking in PayrollRuns

`getOnboardingStatus()` was already called; only `isLive` (bool) was derived from it. Now `workspaceStatus` (string) is also stored. `isReady` is a derived const (`workspaceStatus === 'READY'`). No additional API call was introduced.

---

## Files Changed

| File | Stories |
|---|---|
| `frontend/src/pages/WorkspaceConfig.tsx` | WS-ACTIVATE-1 |
| `frontend/src/pages/PayrollRuns.tsx` | WS-ACTIVATE-2 |
| `frontend/src/pages/WorkspaceSetup.tsx` | WS-ACTIVATE-3 |

No backend changes. No migration. No new dependencies.
