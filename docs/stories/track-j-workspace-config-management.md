# Track J — Post-Onboarding Workspace Configuration Management

**Phase 2 — Track J**
**Sprint:** Gate 6 / Sprint 8 parallel track
**Arch-council:** Reviewed April 2026 — 8 binding decisions (D-ARCH-1 through D-ARCH-8)

## Story Index

| Story | Summary | Priority | Effort |
|-------|---------|----------|--------|
| WC-1 | Edit pay cycle settings | P2 | S |
| WC-2 | Add a grade | P2 | S |
| WC-3 | Edit grade description | P3 | S |
| WC-4 | Add a designation | P2 | S |
| WC-5 | Edit designation description | P3 | S |
| WC-6 | Add a new salary definition with components | P1 | M |
| WC-7 | Edit salary definition components | P1 | M |
| WC-8 | Toggle payroll rule active/inactive | P2 | S |
| WC-9 | Add a new payroll rule | P2 | M |
| WC-10 | Edit/toggle statutory component override | P1 | S |
| WC-11 | Add component override for unconfigured platform component | P2 | S |

---

## WC-1 — Edit Pay Cycle Settings

**As a** payroll operator,
**I want to** update pay cycle settings (run day, cutoff day, payment day, frequency) after onboarding,
**So that** I can correct scheduling configuration without re-uploading the full Excel file.

**Rationale:** Pay cycle fields are set once during onboarding and currently immutable via UI. Operators discover errors (wrong cutoff day, incorrect payment date) only when running payroll. The fix today is a full Excel re-upload.

**Acceptance Criteria:**

- Given a workspace with an active pay cycle, when the operator opens the Edit Pay Cycle SlideOver, all current values are pre-filled
- When the operator submits valid values, the active `pay_cycle` row is updated and the card reflects the new values on reload
- `run_day`, `cutoff_day`, `payment_day` must be integers 1–31; frequency must be one of: monthly / bi-weekly / weekly. Invalid values show field-level errors; form does not submit
- **Edge case — in-progress run guard (D-ARCH-1 lock window):** If any run for this workspace is in status `SUBMITTED | PROCESSING | CALCULATED | PARTIAL | APPROVED`, the PATCH returns 409 and the SlideOver shows: "Pay cycle cannot be changed while a payroll run is in progress or pending approval."
- **Edge case — frequency change mid-year (D-ARCH-6):** If the operator attempts to change `frequency` AND any PAID run exists for this workspace in the current calendar year, the PATCH returns 409: "Pay cycle frequency cannot be changed mid-year. A PAID run for this period exists."
- **Informational note (D-ARCH-7):** `run_day`, `cutoff_day`, `payment_day` are not read by the payroll execution engine. A note inside the SlideOver reads: "Run day, cutoff day, and payment day are stored for reference only and are not currently used in payroll calculations."
- Guard enforced at the repository layer, not the route layer

**Out of scope:** Creating a second pay cycle; retroactive correction of past runs.

---

## WC-2 — Add a Grade

**As a** payroll operator,
**I want to** add a new grade after onboarding,
**So that** I can accommodate new employee bands without re-uploading the full config.

**Acceptance Criteria:**

- "Add Grade" button in Grades card header opens a SlideOver with `grade_code` (required) and `description` (optional)
- Grade code is uppercased on save; must be unique per workspace — duplicate returns: "Grade code [X] already exists."
- On success, the new grade appears in the table immediately
- **Edge case:** Empty grade code shows: "Grade code is required." Form does not submit

**Out of scope:** Deleting grades; renaming grade codes (codes are immutable after creation).

---

## WC-3 — Edit a Grade Description

**As a** payroll operator,
**I want to** correct a grade's description,
**So that** grades are accurately labelled without regenerating the entire config.

**Acceptance Criteria:**

- Each grade row has an Edit icon button (pencil, 44×44px touch target)
- SlideOver shows `grade_code` read-only (grey background input + lock icon) and `description` editable
- On save, the description updates in the table
- Empty description is allowed (displays "—")
- **Edge case:** Code field is visually locked — operator cannot tab into it or modify it

---

## WC-4 — Add a Designation

**As a** payroll operator,
**I want to** add a new designation after onboarding,
**So that** I can introduce new job titles without re-uploading the full config.

Acceptance criteria mirror WC-2 for designations (`designation_code` + `description`).

---

## WC-5 — Edit a Designation Description

Mirrors WC-3 for designations.

---

## WC-6 — Add a New Salary Definition

**As a** payroll operator,
**I want to** create a new salary definition with earning components,
**So that** I can support a new salary band introduced after initial onboarding.

**Rationale:** New employee grades or salary bands are added mid-year routinely. Current path requires full Excel re-upload.

**Acceptance Criteria:**

- "Add Salary Definition" button opens a SlideOver with: `name` (required), `code` (required, unique per workspace), and a component table with BASIC / HOUSING / TRANSPORT pre-populated as mandatory rows with editable amounts
- Operator can add additional component rows (code + amount)
- Codes uppercased; amounts must be positive numbers (> 0)
- Duplicate definition code returns: "Salary definition code [X] already exists."
- BASIC, HOUSING, TRANSPORT rows: remove button hidden (not disabled) — their absence is clearer than a greyed state
- On save, the new definition appears in the Salary Definitions card as an expandable row
- **Edge case:** Attempting to save without all three mandatory components → 422: "BASIC, HOUSING, and TRANSPORT components are required."
- **Edge case:** Amount of zero or negative → field-level error: "Amount must be greater than zero."
- **Edge case (D-ARCH-5):** All DB writes scoped with `workspace_id`

**Out of scope:** Assigning employees to the new definition (done via Employees page).

---

## WC-7 — Edit a Salary Definition (Components)

**As a** payroll operator,
**I want to** change component amounts, add new earning components, or remove optional ones from an existing salary definition,
**So that** I can apply approved salary changes without generating a new Excel file.

**Rationale:** Salary reviews are routine. The execution engine reads `components_jsonb` live at run start — it is NOT snapshotted. Edits are safe only when no run is in-flight (D-ARCH-1). FULL_RUN retry deletes ALL results (including previously successful employees) and recalculates from live data — the same lock prevents corruption here too.

**Acceptance Criteria:**

- Each salary definition row has an "Edit" button inside the expandable row header
- SlideOver opens with an editable component table (code + amount per row)
- BASIC, HOUSING, TRANSPORT rows: remove button hidden; they cannot be removed
- Operator can add new component rows (code + amount); duplicate code within this definition returns a field-level error
- All amounts must be positive numbers
- An `AlertBanner` (info) at the top of the SlideOver: "Changes apply from the next payroll run only. They do not affect runs already in progress or results already calculated."
- **Edge case — edit-lock (D-ARCH-1):** If any run for this workspace is in status `SUBMITTED | PROCESSING | CALCULATED | PARTIAL | APPROVED` AND an employee on that run has an active contract pointing to this salary definition → PATCH returns 409. SlideOver shows: "This salary definition cannot be edited while a payroll run is in progress or pending approval."
- **Edge case — FULL_RUN retry safety:** CALCULATED and PARTIAL statuses are included in the lock window, covering full-run retries which recalculate every employee from live salary data
- **Edge case — workspace isolation (D-ARCH-5):** UPDATE includes `AND workspace_id = :wid`; cross-workspace attempts return 404
- **Edge case:** Saving without BASIC/HOUSING/TRANSPORT → 422; zero/negative amount → 422 with field name

---

## WC-8 — Toggle a Payroll Rule Active / Inactive

**As a** payroll operator,
**I want to** deactivate a payroll rule without deleting it,
**So that** I can suspend a bonus or allowance rule and re-enable it later without losing its configuration.

**Rationale:** Rule toggles operate on the source `payroll_rule` table. In-progress runs read from the `rule_set_item` snapshot — they are NOT affected. Future runs pick up the change only after the rule set is re-published. The `is_active` column shown in WorkspaceConfig reflects the **current management state** (live table). Historical "state at run time" is in `rule_set_item` snapshots, visible in the Run Trace — not here.

**Acceptance Criteria:**

- Each payroll rule row shows an `is_active` StatusBadge (ACTIVE / INACTIVE) and a Deactivate / Activate button
- Clicking shows a confirmation dialog: "Deactivating [Rule Name] will exclude it from future payroll runs after the rule set is re-published. This does not affect any run currently in progress. Continue?"
- On confirm, status badge updates optimistically; reverts with an error banner if the API call fails
- A dismissible `AlertBanner` (info) appears on the main config page after any toggle: "Rule changes take effect only after the rule set is re-published from Workspace Setup → Rules."
- **Edge case — historical rule display:** The `is_active` column header carries a tooltip (ℹ️): "Current activation state. Historical state per run is visible in the Run Trace."
- The rule is NOT deleted; it can be re-activated at any time

---

## WC-9 — Add a New Payroll Rule

**As a** payroll operator,
**I want to** define a new payroll rule (bonus, allowance, deduction) post-onboarding,
**So that** I can introduce new pay components without touching the Excel template.

**Acceptance Criteria:**

- "Add Rule" button opens a SlideOver with: `rule_name` (required), `rule_type` (select: Unit × Rate / Fixed Amount / Daily Rate Deduction), and type-driven definition fields
- Rule name must be unique per workspace — duplicate returns: "A rule named [X] already exists for this workspace."
- On save, the rule appears in Payroll Rules table as ACTIVE
- Dismissible banner shown after save: "After adding a rule, re-publish the rule set from Workspace Setup → Rules for it to take effect on the next payroll run."

---

## WC-10 — Edit / Toggle a Statutory Component Override

**As a** payroll operator,
**I want to** adjust a statutory component's proration strategy or active state for this workspace,
**So that** I can customise how deductions are calculated without touching platform-level settings.

**Rationale:** Disabling a statutory component (PAYE, Pension, NHF) is a compliance-sensitive action. The guard is enforced server-side (D-ARCH-2) — a frontend warning is a secondary signal only.

**Acceptance Criteria:**

- Each component override row has an Edit icon button
- SlideOver shows: component name (read-only), `is_active` toggle Btn, `proration_strategy` select (Full Month / Working Days / Calendar Days / Fixed 30)
- When operator sets `is_active` to disabled: inline `AlertBanner` (warning) in the SlideOver: "Disabling this component means it will not be calculated for any employee in the next payroll run."
- **Edge case — statutory hard reject (D-ARCH-2):** If `component_metadata.component_class = 'statutory_deduction'` for this workspace's country AND `is_active = false` → server returns 422: "[COMPONENT] cannot be disabled. It is a statutory obligation under Nigerian law." Error shown in AlertBanner (error) at the top of the SlideOver.
- **Edge case — country validation (D-ARCH-8):** component_code must exist in `component_metadata WHERE country_code = workspace.country_code`; invalid codes return 422

---

## WC-11 — Add a Component Override for an Unconfigured Platform Component

**As a** payroll operator,
**I want to** create a workspace override for a platform component not yet configured,
**So that** I can customise proration for components added or enabled after initial onboarding.

**Acceptance Criteria:**

- "Add Override" button opens a SlideOver with a dropdown listing platform components NOT yet overridden (sourced from `GET /{wid}/platform-components` minus existing overrides)
- Operator selects component, sets `is_active` and `proration_strategy`
- Statutory guard (D-ARCH-2) applies: selecting `is_active = false` for a statutory_deduction component → server returns 422, shown in SlideOver
- If all platform components already have overrides → button disabled, tooltip: "All available components are already configured."
- **Edge case (D-ARCH-8):** Dropdown only shows components valid for this workspace's country

---

## Arch-Council Decisions Reference

| Decision | Summary |
|----------|---------|
| D-ARCH-1 | Salary def edit-lock: block edits when any run in SUBMITTED→APPROVED references an employee on that def. Guard in repository layer. |
| D-ARCH-2 | Statutory suppression: server-side 422 hard reject for `is_active=false` on `component_class='statutory_deduction'`. No acknowledgment flag. |
| D-ARCH-3 | Audit minimum: `updated_at = NOW()` on every mutated row + operator user ID logged from `X-Performed-By` header. |
| D-ARCH-4 | Migration first (BLOCKER): `client_component_metadata` needs `is_active` + `proration_strategy` columns. |
| D-ARCH-5 | Workspace isolation: all UPDATE queries include `AND workspace_id = :wid`. |
| D-ARCH-6 | Frequency change guard: block if any PAID run exists in the current calendar year. |
| D-ARCH-7 | `run_day`/`cutoff_day`/`payment_day` are informational only — not read by execution engine. Noted in UI and API response. |
| D-ARCH-8 | Component code country validation: verify `component_code` exists in `component_metadata WHERE country_code = workspace.country_code`. |
