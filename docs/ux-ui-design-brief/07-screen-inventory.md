# Artefact 7 — Screen Inventory

> Source: `frontend/src/pages/` (13 pages found), route structures, and journey maps.
> Each screen entry includes: purpose, triggering action, primary data shown, primary action available.
> Grouped by primary actor. A screen may serve multiple actors.

---

## Bureau-Level Screens

### S1 — Bureau Dashboard
**File:** `BureauDashboard.tsx`
**Actor:** Bureau Administrator
**Purpose:** At-a-glance overview of all client workspaces, their status, and any outstanding actions.
**Triggering action:** User logs in or navigates to the root of the bureau portal.
**Primary data shown:** List of workspaces with name, country_code, status (LIVE/DRAFT/etc.), active_employee_count. Likely: runs pending, reconciliation mismatches outstanding.
**Primary action:** Navigate into a workspace; create a new workspace.

**States:**
- Empty state: No workspaces yet — prompt to create first workspace.
- Normal: List of workspaces, sortable/filterable.
- Alert state: Workspaces with MISMATCH reconciliations or PARTIAL runs highlighted.

---

### S2 — Create Workspace
**File:** Not a dedicated page — likely a modal or form on the Bureau Dashboard.
**Actor:** Bureau Administrator
**Purpose:** Create a new client workspace.
**Triggering action:** Click "New Workspace" on Bureau Dashboard.
**Primary data shown:** Form fields.
**Primary action:** Submit (name, country_code, base_currency).

**States:**
- Form idle
- Error: country_code has no statutory rules (422) — must show actionable message.

---

## Workspace Setup & Onboarding Screens

### S3 — Workspace Setup (Onboarding Stepper)
**File:** `WorkspaceSetup.tsx`
**Actor:** Bureau Administrator, HR Admin
**Purpose:** Multi-step wizard to onboard a new client workspace — grades, designations, salary definitions, payroll rules, pay cycle.
**Triggering action:** Navigating to a workspace in DRAFT or incomplete setup state.
**Primary data shown:** Per-step form with validation preview and commit controls.
**Primary action:** Preview (dry-run validation), then Commit (atomic write).

**States:**
- Step 1: Structure (grades, designations, pay cycle)
- Step 2: Compensation (salary definitions)
- Step 3: Rules (payroll rules, component overrides)
- Preview state: Shows errors and warnings from dry-run validation
- Committed state: Auto-advance workspace status, show success and next steps

---

### S4 — JSON Onboarding
**File:** `JsonOnboarding.tsx`
**Actor:** Bureau Administrator (technical)
**Purpose:** Alternative onboarding path — paste or upload raw JSON payload for atomic processing.
**Triggering action:** Navigating to this screen explicitly (likely a power-user entry point).
**Primary data shown:** JSON editor, response (errors, warnings, preview SQL).
**Primary action:** Preview, then Commit.

**States:**
- Editor idle
- Preview result (errors, warnings)
- Committed

---

### S5 — Workspace Configuration
**File:** `WorkspaceConfig.tsx`
**Actor:** Bureau Administrator, Payroll Operator
**Purpose:** Read-only and edit view of workspace structural configuration: grades, designations, salary definitions, payroll rules, component overrides.
**Triggering action:** Navigate to "Config" tab within a workspace.
**Primary data shown:** Full config snapshot (W13 endpoint response): workspace details, pay cycle, grades, designations, salary definitions, rules, component overrides.
**Primary action:** Edit component overrides (toggle is_active, set proration strategy).

**States:**
- Loaded (data from GET /{workspace_id}/config)
- Editing an override
- Save confirmation

---

## Employee Management Screens

### S6 — Employee List
**File:** `Employees.tsx`
**Actor:** HR Admin, Payroll Operator
**Purpose:** View and manage all employees in a workspace.
**Triggering action:** Navigate to "Employees" for a workspace.
**Primary data shown:** Table: full_name, employee_number, status (ACTIVE/INACTIVE), designation, grade, contract_start.
**Primary action:** Edit an employee's grade or designation (single); bulk-update contract dates.

**States:**
- Normal: paginated/searchable list
- Empty: no employees — prompt to complete onboarding
- Editing single employee contract
- Bulk update mode (upload list of employee_number + dates)

---

## Payroll Input Screens

### S7 — Payroll Inputs (Variable Event Inbox)
**File:** `PayrollInputs.tsx`
**Actor:** Payroll Operator
**Purpose:** View and manage unclaimed variable payroll inputs (overtime, leave, etc.) for the workspace.
**Triggering action:** Navigate to "Inputs" for a workspace.
**Primary data shown:** Table of unclaimed inputs: employee_number, employee_name, input_code, input_category, quantity, reference_date, source, created_at.
**Primary action:** Add a new input; delete an incorrect input.

**States:**
- Loaded: List of unclaimed inputs
- Empty: No unclaimed inputs yet
- Add input form (inline or modal): employee picker, input_code dropdown (from I1 endpoint), quantity, reference_date
- Error state: invalid code or employee (422 response)

---

### S8 — Bulk Input Upload
**File:** `PayrollInputsBulkUpload.tsx`
**Actor:** Payroll Operator
**Purpose:** Upload an Excel/CSV file to create many payroll inputs at once.
**Triggering action:** Click "Bulk Upload" from the Payroll Inputs screen.
**Primary data shown:** File drop zone; after upload: success count, error list.
**Primary action:** Upload file; review errors; retry failed rows.

**Expected file format:** employee_number, input_code, quantity, reference_date (columns)

**States:**
- Idle: Drop zone
- Processing: Upload in progress
- Result: success count + error rows listed with reason

---

## Payroll Run Screens

### S9 — Payroll Runs List
**File:** `PayrollRuns.tsx`
**Actor:** Payroll Operator, Finance Authoriser
**Purpose:** View all payroll runs for a workspace with their lifecycle status.
**Triggering action:** Navigate to "Payroll Runs" for a workspace.
**Primary data shown:** Table: period (start–end), status badge, pay_date, total_net_pay, created_at.
**Primary action:** Navigate to a run; create a new run (disabled if workspace not LIVE).

**States:**
- List loaded
- Empty: No runs yet — show workspace status and prompt if not LIVE
- Run status badges: DRAFT, CALCULATING, CALCULATED, PARTIAL, APPROVED, LOCKED, PAID
- Alert: Runs in PARTIAL or long-running CALCULATING state highlighted

---

### S10 — Run Payroll (New Run Form)
**File:** `RunPayroll.tsx`
**Actor:** Payroll Operator
**Purpose:** Configure and trigger a new payroll run.
**Triggering action:** Click "New Run" from the Payroll Runs list.
**Primary data shown:** Form: period_start (date picker), period_end (date picker), period_type (MONTHLY/FORTNIGHTLY/CUSTOM), working_days (conditional on CUSTOM), run_type (REGULAR/ADJUSTMENT), rule_set_id (optional).
**Primary action:** Submit run.

**States:**
- Form idle
- Working days field: hidden unless period_type = CUSTOM
- Submitting: loading state
- Error: payroll readiness failures (422) — display structured error list with links
- Duplicate period warning (409)
- Success: redirect to run detail or runs list

---

### S11 — Payroll Results
**File:** `PayrollResults.tsx`
**Actor:** Payroll Operator, Finance Authoriser, Compliance Officer
**Purpose:** View per-employee computation results for a specific run, run totals, and component traces.
**Triggering action:** Navigate to a run and click "View Results".
**Primary data shown:** 
- Run summary: period, status, total gross, total deductions, total net, employee count.
- Results table: employee_name, employee_number, gross_pay, total_deductions, net_pay, status (SUCCESS/FAILED).
- Expandable per-employee component trace: rule, method, status, amount, note, warning.
- Run control actions based on current status.
**Primary action:** 
- If CALCULATED: Approve run (→ APPROVED).
- If APPROVED: Lock run (→ LOCKED).
- If LOCKED: Mark as Paid (→ PAID); download exports.
- If PARTIAL: Retry failed employees.

**States:**
- DRAFT / CALCULATING: show loading/pending state
- PARTIAL: highlight FAILED rows, show Retry button, show failure summary
- CALCULATED: show Approve button
- APPROVED: show Lock button, disable Retry
- LOCKED: show exports, show Mark as Paid, show reconciliation link
- PAID: read-only, show exports, show reconciliation
- Empty: No results yet

**Export buttons (visible only on LOCKED or PAID):**
- Download Bank Upload CSV
- Download PAYE Remittance CSV
- Download Pension Contributions CSV

---

### S12 — Reconciliation
**File:** `Reconciliation.tsx`
**Actor:** Finance Authoriser
**Purpose:** Submit the actual payment total after bank disbursement; view and resolve mismatches.
**Triggering action:** Navigate to "Reconciliation" from a LOCKED or PAID run.
**Primary data shown:** 
- Expected total (from engine's total_net_pay)
- Reconciliation status (MATCHED / MISMATCH / RESOLVED / not yet submitted)
- If MISMATCH: actual_payment, variance (actual − expected), notes, resolved_by
**Primary action:**
- If no reconciliation exists (and run is LOCKED): submit form with actual_payment.
- If MISMATCH: resolution form with notes + resolved_by fields.
- If MATCHED or RESOLVED: read-only view.

**States:**
- No reconciliation yet (run is LOCKED): show submission form
- MATCHED: show green confirmation with amounts
- MISMATCH: show red warning with variance, show resolution form
- RESOLVED: show read-only resolution details (who resolved, when, notes)
- Run not LOCKED: show disabled state with explanation

---

## Configuration Screens

### S13 — Public Holidays Calendar
**File:** `PublicHolidays.tsx`
**Actor:** Bureau Administrator, Payroll Operator
**Purpose:** View and manage the two-tier public holiday calendar for a workspace.
**Triggering action:** Navigate to "Public Holidays" settings.
**Primary data shown:** 
- Combined list of national (read-only) and workspace-specific holidays.
- Year filter.
- Tier indicator (NATIONAL vs WORKSPACE).
**Primary action:**
- Add workspace-specific holiday (date + name).
- Delete workspace-specific holiday.
- National holidays: read-only (no delete).

**States:**
- Loaded by year
- Empty year: no holidays in selected year
- Add form (inline): date picker, name
- National holiday: no delete control shown

---

### S14 — Workspace Payroll Config
**Not a dedicated page in current codebase** — likely within WorkspaceConfig.tsx or WorkspaceSetup.tsx.
**Actor:** Bureau Administrator, Payroll Operator
**Purpose:** Configure public holiday behaviour and attendance rules for a workspace.
**Primary data shown:** ph_mode, ph_rate_code, saturday_ph_rule, sunday_ph_rule, d3_leave_overlap_rule, d4_absence_rule.
**Primary action:** Save config (PUT endpoint with effective_from date).

**States:**
- Loaded (defaults if no config exists)
- Editing
- Saved

---

### S15 — Rate Code Registry
**Not a dedicated page in current codebase** — likely within WorkspaceConfig.tsx.
**Actor:** Bureau Administrator
**Purpose:** View and manage rate codes (multipliers for public holiday pay).
**Primary data shown:** Table: code, multiplier, unit, base, description, scope (PLATFORM vs WORKSPACE).
**Primary action:**
- Add new workspace rate code.
- Delete workspace rate code (platform codes: no delete control).

**States:**
- Loaded
- Add form
- Platform codes: visually marked as read-only
- Conflict: duplicate code (409)

---

## Operational / Internal Screens

### S16 — Run Timeline (Execution Trace)
**Not a dedicated page** — accessible from the run detail or results page.
**Actor:** Bureau Administrator (debugging), Payroll Operator
**Purpose:** View the step-by-step execution trace for a payroll run.
**Triggering action:** Click "View Timeline" from a run detail.
**Primary data shown:** Ordered list of trace steps from the `execution_trace` table.
**Primary action:** None — read-only diagnostic view.

---

### S17 — Run Audit Log
**Not a dedicated page** — accessible from the run detail.
**Actor:** Finance Authoriser, Bureau Administrator
**Purpose:** View the immutable audit trail of all state transitions for a run.
**Triggering action:** Click "View Audit Log" from a run detail.
**Primary data shown:** Ordered list: action, old_value, new_value, performed_by, performed_at.
**Primary action:** None — read-only.

---

### S18 — Workspace Dashboard
**File:** `WorkspaceDashboard.tsx`
**Actor:** Payroll Operator, Bureau Administrator
**Purpose:** Per-workspace summary landing page.
**Triggering action:** Navigate into a workspace from the Bureau Dashboard.
**Primary data shown:** Workspace status, active employee count, recent runs, outstanding actions.
**Primary action:** Navigate to runs, employees, inputs, config.
