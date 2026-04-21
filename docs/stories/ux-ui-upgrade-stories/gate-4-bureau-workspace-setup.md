# Gate 4 — Bureau & Workspace Setup Journey
## UX/UI Upgrade Stories

**Status:** 🔜 Plan approved (April 2026) — implementation pending  
**Skills active:** `/ui-designer`, `/ux-designer`, `/pm`  
**Personas:**
- Sandy — bureau operator, sets up and manages client workspaces
- Adaeze — payroll operator, uses workspace hub + employees pages

**Design decisions honoured:** DD-1, DD-3, DD-4, DD-5, DD-12, DD-14, DD-15, DD-17

**Binding architecture decisions:**
- `JsonOnboarding` page deleted; "New Client" is a SlideOver on Bureau Dashboard
- WorkspaceDashboard StateFlow: bespoke horizontal pipeline (re-skinned with tokens), NOT OnboardingStepper
- Transition buttons: human-readable action labels, not technical state names
- WorkspaceSetup: UI shell migration only — wizard logic + child components untouched
- Component overrides: StatusBadge ("Active"/"Inactive"), NOT Toggle

---

## G4-UI-1 — Bureau Dashboard

**Priority:** P2 — Operator productivity

> As **Sandy (bureau operator)**,  
> I want to see all managed client workspaces at a glance with their onboarding status,  
> So that I can immediately identify which clients need setup attention and which are live.

### Acceptance Criteria

- Given I land on `/`: ContentHeader title="Bureau Dashboard", subtitle showing count ("X workspaces"), primary "+ New Client" Btn
- Given workspaces exist: table sorted LIVE first, then by setup progress descending; columns = Name (truncated at 40 chars, `title` attribute for full name), Country, Status (StatusBadge — DD-12), Active Employees, Action
  - LIVE rows: "Open →" ghost Btn
  - Non-LIVE rows: "Continue Setup →" secondary Btn
- Given I type in the search field (above table): table filters by workspace name client-side (case-insensitive)
- Given no workspaces exist: EmptyState headline="No client workspaces yet" body="Create your first workspace to start onboarding a client." action="+ New Client" (DD-5)
- Given loading: 5 SkeletonRows
- Given load fails: AlertBanner variant="error"
- Given I click "+ New Client": SlideOver opens (not a page navigation)

**New Client SlideOver** (replaces `JsonOnboarding` page):
- TextInput label="Workspace Name" required
- SearchableSelect label="Country" options=[NG, GH, KE, ZA, UG], default=NG
- TextInput label="Currency" value=auto-derived from country, disabled (read-only)
- On submit: `workspaceApi.create()` → navigate to `/workspaces/:id/setup` → close SlideOver
- On failure: AlertBanner inside SlideOver (page does not close)

### Out of Scope
- Deleting a workspace
- Workspace-level metrics beyond active employee count

### Open Questions — Resolved
- **"New Client" routing:** SlideOver on Bureau Dashboard (not standalone page). `/onboarding` route removed entirely.

---

## G4-UI-2 — Workspace Dashboard

**Priority:** P2 — Operator productivity

> As **Sandy or Adaeze**,  
> I want a single hub page for a workspace that shows its onboarding status, lifecycle state, and quick navigation,  
> So that I can understand the workspace health and get to any area in one click.

### Acceptance Criteria

- Given I open a workspace: ContentHeader title=**workspace name** (NOT UUID — name fetched via `workspaceApi.list()` filtered by workspaceId), subtitle=StatusBadge
- **Bespoke StateFlow pipeline** (horizontal flex, re-skinned with design tokens):
  - Done steps: `bg-green-100 text-green-800`
  - Current step: `bg-brand text-white`
  - Pending steps: `bg-gray-100 text-gray-400`
  - Arrows: `text-gray-300`
- ProgressBar showing `status.progress_percent` below pipeline
- **Transition buttons** use human-readable labels (NOT technical state names):
  ```
  STRUCTURE_DEFINED    → "Confirm structure is set up →"
  COMPENSATION_DEFINED → "Confirm compensation is set up →"
  RULES_DEFINED        → "Confirm payroll rules are set up →"
  READY                → "Mark workspace as ready →"
  LIVE                 → "Activate workspace →"
  ```
- For non-LIVE: "Continue Setup" is the primary Btn (visually elevated, not an equal tile)
- For LIVE: AlertBanner variant="success" "Workspace is LIVE. Payroll runs are enabled."
- Given transition succeeds: toast success + reload status
- Given transition fails: AlertBanner variant="error" inline below buttons
- Quick Actions: 2-col Card grid (each tile = Card with label, description, Btn); "Run Payroll" tile disabled + `title` tooltip when not LIVE
- Loading: SkeletonCard ×2

### Out of Scope
- Editing workspace name or country inline
- Deleting a workspace

### Open Questions — Resolved
- **StateFlow vs OnboardingStepper:** Bespoke horizontal pipeline kept. Stepper is for wizard nav; this is a lifecycle state display — different semantic need.
- **Transition labels:** Human-readable actions confirmed by user.

---

## G4-UI-3 — Workspace Setup Wizard

**Priority:** P1 — Compliance (onboarding is a hard requirement before payroll)

> As **Sandy (bureau operator)**,  
> I want a guided multi-step wizard to configure a new client workspace — pay structure, compensation, rules, employees — without needing to write JSON manually,  
> So that I can onboard a new client accurately in under 30 minutes.

### Acceptance Criteria

**UI Shell Replacements (logic unchanged):**
- `PageHeader` → `ContentHeader` (title="Workspace Setup", back link to workspace dashboard)
- `AlertBox` → `AlertBanner` (all variants)
- Legacy `Btn` → design system `Btn`
- Legacy `Card` → design system `Card`

**OnboardingStepper** (added above step content):
```
Steps: Structure & Pay | Components | Employees | Activate
```
- Current step highlighted; completed steps shown as ✓
- For non-DRAFT workspace (re-run wizard): stepper reflects completed steps as ✓, starts at first incomplete step

**Step behaviour:**
- File upload steps use `FileDropZone` — only if child components don't own the file input (child components `WorkspaceExcelUpload` + `EmployeeUpload` are NOT modified)
- On validate/preview/commit errors: `AlertBanner` with specific message (not just "failed")
- On partial commit failure: show per-entity success/fail counts; offer "Resume from employees" recovery path
- LocalStorage draft: graceful degradation if unavailable (no error thrown, wizard still works without draft persistence)
- On commit success: toast + redirect to Workspace Dashboard

**CRITICAL — DO NOT CHANGE:**
- All wizard state variables and `useEffect` hooks
- `buildConfigTemplate`, `employeesToCommitShape`, `extractConfigSalaryDefs`, `buildFinalPayload`
- `saveDraft`, `loadDraft`, `clearDraft`
- `WorkspaceExcelUpload` component (untouched)
- `EmployeeUpload` component (untouched)
- `DetailsModal` component

### Out of Scope
- Editing individual employees within the wizard
- Importing from external HR systems
- Changing any business logic

---

## G4-UI-4 — Employees List

**Priority:** P2 — Operator productivity

> As **Adaeze**,  
> I want to see all employees with their grade/designation assignments, and fix any that are missing them,  
> So that every employee is correctly classified before I run payroll.

### Acceptance Criteria

- ContentHeader title="Employees" subtitle="`${employees.length} employee${s}`" (or "Loading…")
- Given `unmatched.length > 0`: AlertBanner variant="warning" title="`${unmatched.length} employees need grade and designation assignment`" — description includes scroll-to anchor link "View employees needing assignment →" pointing to `#unmatched-section`
- Unmatched rows: `border-l-4 border-amber-400 bg-amber-50` (DD-15: not colour alone — border provides second visual signal)
- Given I click "Edit" Btn on a row: SlideOver opens (DD-3 — NOT inline row editing) with SearchableSelect for Grade + SearchableSelect for Designation, pre-populated with current values
- SlideOver footer: Cancel (secondary) + Save (primary, loading={saving})
- On save success: SlideOver closes, row refreshes, `toast.show('success', 'Employee updated')`
- On save failure: AlertBanner inside SlideOver (panel stays open)
- All employees use design system StatusBadge for ACTIVE/INACTIVE (DD-12)
- Loading: 5 SkeletonRows
- Given no employees: EmptyState headline="No employees found" body="Employees are added during workspace setup." action="Go to Setup →" (DD-5)

### Out of Scope
- Adding employees outside setup wizard
- Deactivating employees from this page
- Pagination (scrollable container with max-height for matched section)

---

## G4-UI-5 — New Client (JsonOnboarding → DELETED)

**Status:** Page deleted. Route `/onboarding` removed from router.

Functionality absorbed into the "New Client" SlideOver on Bureau Dashboard (G4-UI-1).

---

## G4-UI-6 — Workspace Configuration View

**Priority:** P2 — Operator productivity

> As **Sandy or Adaeze**,  
> I want to view the full configuration of a workspace — pay cycle, grades, designations, salary definitions, payroll rules, component overrides — in a structured read-only view, and re-upload config when needed,  
> So that I can audit the setup and update it when client requirements change.

### Acceptance Criteria

- ContentHeader title="Configuration" subtitle=`config.workspace.name`; action=secondary Btn "Update Config ↑" → opens SlideOver
- Loading: SkeletonCard ×4
- Error: AlertBanner variant="error"

**Configuration Sections (each a Card):**
1. Workspace — 4-col grid: Name, Country, Currency, Status (StatusBadge)
2. Pay Cycle — 4-col grid: Frequency, Run Day, Cutoff Day, Payment Day; or muted "No pay cycle defined."
3. Grades — table (Code, Description); or muted "No grades defined."
4. Designations — table (Code, Description); or muted "No designations defined."
5. Salary Definitions — per-definition expandable section (DD-17: grid-template-rows); header = name + code badge + chevron; expanded = component table (Component, Amount)
6. Payroll Rules — table (Name, Type, Method); or muted "No rules defined."
7. Component Overrides — list rows: component name + **StatusBadge "Active"/"Inactive"** (NOT Toggle — false affordance avoided)

**Re-upload SlideOver:**
- FileDropZone accept=".xlsx"
- On success: close SlideOver + reload config + `toast.show('success', 'Configuration updated')`
- On failure: AlertBanner inside SlideOver

### Out of Scope
- Editing individual config values in-place
- Interactive component override toggles

---

## G4-UI-7 — Public Holidays

**Priority:** P2 — Operator productivity

> As **Sandy**,  
> I want to view and manage the public holiday calendar for a workspace by year,  
> So that the payroll engine has accurate PH data when calculating OT and working-day adjustments.

### Acceptance Criteria

- ContentHeader title="Public Holidays" subtitle="Workspace holiday calendar"; action=primary "+ Add Holiday" Btn
- **Year navigator** (above table): IconBtn `<` (44×44px min — DD-14) + year text + IconBtn `>`; defaults to current year
- Loading: 5 SkeletonRows
- Given no holidays for selected year: EmptyState headline=`"No holidays for ${year}"` body="Add workspace-specific holidays or check the national calendar has been seeded." action="Add Holiday" (DD-5)
- Table: Date (formatted `dd MMM yyyy`), Name, Source badge (NATIONAL: `bg-blue-100 text-blue-800`; WORKSPACE: `bg-gray-100 text-gray-600`), Action column
  - **NATIONAL rows: no delete button** (source-conditional — system-managed)
  - WORKSPACE rows: IconBtn trash (hover red) → opens ConfirmDialog

**Add Holiday SlideOver:**
- DateInput label="Date" required
- **Client-side duplicate check:** if `holidays.some(h => h.date === addDate)` → InlineError "A holiday on this date already exists."
- TextInput label="Name" required
- Footer: Cancel + "Add Holiday" (primary, loading={addSaving})
- On success: close SlideOver + refresh + `toast.show('success', 'Holiday added')`
- On failure: AlertBanner inside SlideOver

**Delete ConfirmDialog (DD-4):**
- title=`Delete "${holiday.name}"?`
- description="This will remove the holiday from payroll calculations. National holidays cannot be deleted here."
- confirmLabel="Delete Holiday" destructive={true}

### Out of Scope
- Bulk importing national holidays (backend seed operation)
- Editing an existing holiday (delete and re-add)

---

## Design Decisions Verified — Gate 4

| DD | Honoured where |
|----|----------------|
| DD-3 | Employees: Edit→SlideOver; WorkspaceConfig: re-upload→SlideOver; PublicHolidays: add→SlideOver |
| DD-4 | PublicHolidays: delete→ConfirmDialog with destructive btn |
| DD-5 | BureauDashboard, WorkspaceDashboard, Employees, PublicHolidays — all EmptyState with CTA |
| DD-12 | StatusBadge everywhere; Component Overrides StatusBadge not Toggle |
| DD-14 | All spacing on 8pt grid; IconBtn year nav ≥44×44px touch targets |
| DD-15 | Unmatched employee rows: border-l-4 border-amber-400 (not colour alone) |
| DD-17 | WorkspaceConfig salary definitions use grid-template-rows expand |

---

## UX Review Findings Applied

| Finding | Story | Resolution |
|---------|-------|------------|
| UUID shown as WorkspaceDashboard title | G4-UI-2 | workspace name via `workspaceApi.list()` |
| Transition labels are technical state names | G4-UI-2 | TRANSITION_LABELS map to human actions |
| "New Client" route orphaned as standalone page | G4-UI-1 | SlideOver on Bureau Dashboard |
| Toggle as read-only override indicator | G4-UI-6 | StatusBadge replaces Toggle |
| Re-upload buried at bottom of long config page | G4-UI-6 | Moved to ContentHeader action SlideOver |
| Inline row editing in dense table | G4-UI-4 | SlideOver with SearchableSelect (DD-3) |
| NATIONAL holidays deletable | G4-UI-7 | Source-conditional delete column render |
| Duplicate holiday date not validated client-side | G4-UI-7 | InlineError before submit |
| Bureau Dashboard no search filter | G4-UI-1 | TextInput filter above table |
| Non-LIVE workspace "Run Payroll" equal weight tile | G4-UI-2 | Disabled tile with tooltip |

## UI Review Findings Applied

| Finding | Story | Resolution |
|---------|-------|------------|
| StateFlow ad-hoc classes | G4-UI-2 | Re-skinned with design system tokens |
| Action column width shift | G4-UI-1 | Fixed `w-36` on action column |
| Stepper position | G4-UI-3 | Full-width above step content Card |
| Year nav touch targets | G4-UI-7 | IconBtn (min 44×44px) |
