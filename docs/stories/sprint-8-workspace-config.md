# Sprint 8 — WorkspaceConfig Completion

**Sprint goal:** Surface post-onboarding config management in WorkspaceConfig — structured tabs, salary definition creation, OT & holidays surface, and fix the payroll rule edit data-loss bug.

**Arch-council:** Not required. All data contract decisions were ratified in Track J (D-ARCH-1–8). No new migrations, status fields, or cross-service boundaries in this sprint.

---

## Story Index

| Story | Summary | Priority | Effort |
|-------|---------|----------|--------|
| S8-1 | WorkspaceConfig tab restructure | P2 | S |
| S8-2 | Add a new salary definition (WC-6 frontend) | P1 | M |
| S8-3 | Backend guard: POST /salary-definition mandatory components | P1 | S |
| S8-4 | Fix EditPayrollRuleSlideOver: silent data loss on OT and daily rate rules | P0 | S |
| S8-5 | OT & Holidays tab: PH config + Rate Code Registry | P2 | M |
| S8-6 | API client: getPayrollConfig, updatePayrollConfig, createRateCode, deleteRateCode | P2 | XS |
| S8-7 | UI consistency sweep: WorkspaceConfig typography and layout | P3 | XS |

---

## S8-1 — WorkspaceConfig Tab Restructure

**As a** payroll operator,
**I want to** navigate workspace configuration through clearly separated tabs,
**So that** I can find salary, rules, holidays, and deduction settings without scrolling through a single long page.

**Acceptance Criteria:**

- Four tabs render below the Workspace Info and Pay Cycle cards: **Workforce**, **Payroll Rules**, **OT & Holidays**, **Deductions**
- `workforce` is the default active tab on page load
- Tab content is lazy-rendered (only the active tab's sections mount)
- The rule-change `AlertBanner` (if visible) renders **above** the tab bar, not inside any tab
- Workspace Info card and Pay Cycle card remain always-visible above the tab bar on all tabs
- Switching tabs does not trigger any API calls or lose unsaved SlideOver state
- No other layout, card, or data changes in this story — purely structural

| Tab key | Sections |
|---|---|
| `workforce` (default) | Grades + Designations + Salary Definitions |
| `rules` | Payroll Rules |
| `ot-holidays` | OT & Holiday Behaviour + Rate Code Registry |
| `deductions` | Component Overrides |

**Out of scope:** Tab persistence across page navigations. Any new sections or data not already present in the current WorkspaceConfig.

**Priority:** P2

---

## S8-2 — Add a New Salary Definition (WC-6, implementation sprint)

**As a** payroll operator,
**I want to** create a new salary definition with earning components from within WorkspaceConfig,
**So that** I can support new salary bands introduced mid-year without re-uploading the full Excel file.

*(Full story in Track J WC-6. Sprint 8 acceptance criteria cover the implementation requirements.)*

**Acceptance Criteria:**

- "Add Salary Definition" button appears in the Salary Definitions section header within the Workforce tab
- Button opens `AddSalaryDefSlideOver` with: `name` (required), `code` (required, `.toUpperCase()` on change, `font-mono`), and a component table pre-populated with BASIC / HOUSING / TRANSPORT as mandatory rows with editable amounts
- Operator can add additional component rows (component code + amount); duplicate code within the same definition shows a field-level error: "Component code [X] is already in this definition."
- BASIC, HOUSING, TRANSPORT rows: remove icon hidden entirely (not disabled)
- Amounts must be positive numbers (> 0); zero or negative shows: "Amount must be greater than zero."
- No info AlertBanner at the top of the SlideOver — this is a new record, not a live-run risk
- On save, POST to `/{wid}/salary-definition` via `workspaceApi.createSalaryDefinition`; on success, SlideOver closes and `loadConfig()` refreshes the list
- Duplicate definition code returns server 422, shown as AlertBanner (error): "Salary definition code [X] already exists."
- Missing mandatory component returns server 422: "Required components missing: [BASIC/HOUSING/TRANSPORT]."

**Out of scope:** Editing existing salary definitions (WC-7, future sprint). Assigning employees to the new definition.

**Priority:** P1 — operators are blocked from adding new salary bands without Excel re-upload.

---

## S8-3 — Backend Guard: POST /salary-definition Mandatory Components

**As a** system,
**I want to** reject any request to create a salary definition missing BASIC, HOUSING, or TRANSPORT components or with invalid amounts,
**So that** no salary definition enters the database in an invalid state.

**Acceptance Criteria:**

- `POST /{wid}/salary-definition` validates that `components_jsonb` contains keys `BASIC`, `HOUSING`, and `TRANSPORT`
- Missing any of the three → 422: `{"detail": "Required components missing: [sorted list]."}`
- Any component amount ≤ 0 → 422: `{"detail": "Amount for '[CODE]' must be greater than zero."}`
- Any unparseable amount → 422: `{"detail": "Invalid amount for '[CODE]'."}`
- Validation logic mirrors `patch_salary_definition` (workspace.py lines 1060–1079)
- Workspace scoping enforced: definition created with `workspace_id = wid`; cross-workspace creation returns 404

**Out of scope:** Validating component codes against a platform-level component registry (future story).

**Priority:** P1 — pairs with S8-2; data integrity guard.

---

## S8-4 — Fix EditPayrollRuleSlideOver: Silent Data Loss on OT and Daily Rate Rules

**As a** payroll operator,
**I want to** edit an overtime multiplier or daily rate deduction rule and have all fields pre-filled and saved correctly,
**So that** I don't silently lose `rate_code`, `multiplier`, `absent_days_input_code`, or `working_days_in_month` values when I submit the form.

**Rationale:** `ot_multiplier` and `daily_rate_deduction` rules map to `'UNIT_RATE'` in `METHOD_TO_RULE_TYPE`, but `RuleFields` for `UNIT_RATE` only renders `input_field` / `rate` / `unit`. Custom keys are loaded into `fieldValues` but never shown — and are silently dropped by `buildDefinition()` on save.

**Acceptance Criteria:**

- For a rule with `calculation_method = 'ot_multiplier'`: the SlideOver pre-fills `rate_code` and `multiplier` fields; submitting the form includes both in the payload
- For a rule with `calculation_method = 'daily_rate_deduction'`: the SlideOver pre-fills `absent_days_input_code` and `working_days_in_month`; submitting the form includes both in the payload
- `calculation_method` is read-only in the edit form — it cannot be changed after rule creation
- Saving an `ot_multiplier` rule with empty `rate_code` shows: "Rate code is required."
- Saving a `daily_rate_deduction` rule with empty `absent_days_input_code` shows: "Absent days input code is required."
- Regression: existing `unit_multiplier` and `fixed_amount` rule edits continue to work correctly
- Save and re-open any affected rule → values persist (no silent drop)

**Out of scope:** Changing `calculation_method` on an existing rule. Validating `rate_code` values against the rate code registry.

**Priority:** P0 — silent data corruption on every save of affected rule types.

---

## S8-5 — OT & Holidays Tab: PH Config and Rate Code Registry

**As a** payroll operator,
**I want to** view and manage public holiday settings and rate codes from within WorkspaceConfig,
**So that** all post-onboarding configuration is accessible from one place without navigating to a separate page.

**Acceptance Criteria:**

**OT & Holiday Behaviour card:**
- Displays `ph_mode` (as StatusBadge), `saturday_ph_rule`, `sunday_ph_rule`, `d3_leave_overlap_rule`, and `d4_absence_rule`
- "Edit" button opens `EditPayrollConfigSlideOver` with 5 SelectField fields; pre-fills all current values
- A hint below `ph_mode` in the SlideOver reads: "Automatic mode calculates PH OT from the calendar. Manual requires hours as inputs."
- On save, card refreshes with updated values
- If no config exists: "No payroll behaviour configured. Defaults apply."

**Rate Code Registry card:**
- Two sub-sections: **PLATFORM CODES** (read-only) and **YOUR CODES** (workspace-managed)
- Platform rows: muted text (`text-gray-400`), lock icon (14px), no hover state, no delete button
- Workspace rows: editable, delete `✕` button (matches salary def remove button pattern)
- "Add Rate Code" button appears in the **YOUR CODES** group header (not the main section header)
- Clicking "Add Rate Code" opens `AddRateCodeSlideOver` with 5 fields: `code` (required, uppercase, font-mono), `multiplier` (min 0.01), `unit` (select: hours/days), `base` (select: basic_hourly/basic_daily/basic_monthly), `description` (optional)
- On success, the new code appears in the workspace section without a full page reload
- Empty workspace codes section shows: "No custom rate codes. Platform codes apply." with an "Add Rate Code" CTA
- The standalone `RateCodes.tsx` page at `/workspaces/:id/rate-codes` is **not removed** — this surface is additive

**Out of scope:** Editing platform rate codes. Bulk import of rate codes. Moving employees between rate codes.

**Priority:** P2 — data already exists server-side; operators currently must navigate to a separate URL.

---

## S8-6 — API Client: Payroll Config and Rate Code Methods

**As a** frontend engineer,
**I want** `workspace.ts` to expose `getPayrollConfig`, `updatePayrollConfig`, and (if missing) `createRateCode` / `deleteRateCode` functions,
**So that** the OT & Holidays tab can fetch and update PH configuration and rate codes without duplicating fetch logic.

**Acceptance Criteria:**

- `getPayrollConfig(workspaceId)` → `GET /workspaces/{wid}/payroll-config`
- `updatePayrollConfig(workspaceId, payload)` → `PUT /workspaces/{wid}/payroll-config` (PUT, not PATCH)
- `createRateCode(workspaceId, payload)` and `deleteRateCode(workspaceId, code)` confirmed present; added if missing
- URL prefix matches backend convention: `/workspaces/{wid}/` (not `/{wid}/`)
- All methods use the existing HTTP wrapper in `workspace.ts`; no new client introduced

**Out of scope:** Error retry logic. Optimistic update patterns.

**Priority:** P2 — technical enabler for S8-5.

---

## S8-7 — UI Consistency Sweep: WorkspaceConfig Typography and Layout

**As a** payroll operator,
**I want** WorkspaceConfig to use consistent text sizing and button alignment throughout,
**So that** the page feels polished and doesn't have legacy styling inconsistencies.

**Acceptance Criteria:**

- All `text-[11px]` instances replaced with `text-xs`
- Grade and designation code cells: `text-xs font-mono text-gray-700`
- `RowEditBtn` padding: `p-1.5` (was `p-2.5`) — aligns with sm button height in table rows
- Activate/Deactivate buttons: `min-w-[90px]` — no layout shift on label change
- Status column: `w-28`
- All table `<tr>` rows: standardised `py-2` padding
- Rate code multiplier column: `tabular-nums`
- No functional changes — visual alignment only

**Out of scope:** Redesigning any card layout. Changing component types or interaction patterns.

**Priority:** P3 — polish pass.
