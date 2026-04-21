# Artefact 3 — Business Rules Register

> Source: `backend/domain/payroll/`, `backend/api/routes/payroll.py`, `backend/infra/db/models/`.
> Each rule notes whether the UI needs to surface it to the user.

---

## Payroll Calculation Rules

### BR-1 — PAYE: Cumulative Annual Method
**What:** Personal income tax is computed on an annualised basis using progressive tax bands. The engine annualises the employee's income, calculates the annual tax, then de-annualises it to the period.

**Statutory basis:** Nigerian PITA. Bands are stored in `tax_band` table, linked to the active `statutory_rule`.

**UI surface needed:** None during normal flow. On the results screen, the component trace will show the PAYE amount. If tax bands are missing the run will fail with a 500 error — the UI should surface this clearly.

---

### BR-2 — Pension: 8% Employee / 10% Employer
**What:** Pension employee contribution = 8% of pensionable earnings (typically basic). Employer contribution = 10%. Rates are stored in `statutory_rule.rules_jsonb.pension` and must be present — the system raises a hard 500 if missing.

**UI surface needed:** If the run fails with "Statutory rule is missing pension rates" the UI must show a user-facing error rather than a raw 500.

---

### BR-3 — NHF: 2.5% of Basic Salary
**What:** National Housing Fund contribution. Rate stored as `statutory_rule.rules_jsonb.nhf.employee_rate` (default 0.025). Field key is `employee_rate`.

**UI surface needed:** None — system handles automatically.

---

### BR-4 — Health Insurance: Fixed Monthly Amount
**What:** A flat monthly employee deduction stored in `statutory_rule.rules_jsonb.health_insurance.employee_amount`. Can be overridden at workspace level via `client_component_metadata`. Field key is `employee_amount`.

**UI surface needed:** The workspace config screen needs to allow operators to override this amount per workspace.

---

### BR-5 — Development Levy: Fixed Annual Amount
**What:** A flat annual levy stored in `statutory_rule.rules_jsonb.development_levy.amount`. Can be overridden at workspace level. Field key is `amount`.

**UI surface needed:** Same as BR-4.

---

### BR-6 — Proration on Mid-Period Hire / Termination
**What:** If an employee's contract starts or ends within a pay period, their salary components are prorated by the number of working days they were active within the period.

**Proration strategies:** `FULL_MONTH` (no proration) or `WORKING_DAYS` (prorate). Set per component via `client_component_metadata.overrides_json.calculations_behaviour.proration_strategy`.

**UI surface needed:** Component overrides screen should show proration strategy per component.

---

### BR-7 — Public Holiday Pay
**What:** Employees who work on a public holiday receive an additional payment calculated using the configured `ph_rate_code` multiplier from `rate_code_registry`.

**Modes:**
- `AUTOMATIC` — engine detects PH dates from the calendar and applies automatically.
- `FILE_BASED` — PH events must be submitted as explicit payroll inputs.

**Conflict rules (configured per workspace):**
- Saturday PH: `PH_TAKES_PRECEDENCE` or `DAY_OF_WEEK_TAKES_PRECEDENCE`
- Sunday PH: same options
- Leave overlap (D3): `LEAVE_ABSORBS_PH` or `PH_ADDITIVE`
- Absence on PH (D4): `ABSENT_IS_DEDUCTIBLE` or `PH_EXCUSES_ABSENCE`

**UI surface needed:** Workspace payroll config screen must expose all four conflict rules as explicit choices with descriptions. An incorrect mode selection will produce wrong pay silently.

---

### BR-8 — Cross-Period Input Rate Resolution
**What:** A payroll input can carry a `reference_date` pointing to a previous period. When present, the engine resolves the rule set that was effective on that historical date to calculate the correct rate — not the current period's rate.

**UI surface needed:** The input creation form should make `reference_date` optional but label it clearly as "applies to period (if different from current)". The results trace will show `resolution_source` indicating which rule set was used.

---

### BR-9 — Payroll Readiness Check
**What:** Before a run executes, the system validates that the workspace is fully configured. Failure returns HTTP 422 with a structured list of errors. Known checks: workspace must have structure, compensation, and rules defined.

**UI surface needed:** The "Run Payroll" screen must display these errors clearly with actionable guidance (e.g. "Salary definitions are missing — go to Workspace Setup").

---

### BR-10 — Period Uniqueness
**What:** Only one run is allowed per workspace per `(period_start, period_end)` pair. A duplicate attempt returns HTTP 409.

**UI surface needed:** The run list should show any existing run for the same period. The "Run Payroll" form should warn if a run already exists for the selected period.

---

### BR-11 — Input Quantity Non-Negativity
**What:** `payroll_input.quantity` must be >= 0. Negative quantities are rejected at the API layer (422).

**UI surface needed:** Input form must validate quantity >= 0 client-side.

---

### BR-12 — Reconciliation: LOCKED Status Required
**What:** A reconciliation can only be submitted when the run is in LOCKED status. Attempting on any other status returns 400.

**UI surface needed:** The reconciliation submit button must be disabled unless the run is LOCKED. Show current run status prominently on the reconciliation screen.

---

### BR-13 — Reconciliation: One Per Run
**What:** Only one reconciliation record is allowed per run. A second attempt returns 409.

**UI surface needed:** Once a reconciliation exists, the submit form should be replaced by the reconciliation result view. Do not show a submit form if status is MATCHED, MISMATCH, or RESOLVED.

---

### BR-14 — Reconciliation Resolution: Notes and Resolved-By Required
**What:** Resolving a MISMATCH requires both `notes` (explanation) and `resolved_by` (operator identity). Either missing → 400.

**UI surface needed:** Both fields must be required in the resolution form with clear labels.

---

### BR-15 — APPROVED Run Immutability (Partial)
**What:** Once APPROVED, a run cannot be retried or recalculated. The only valid next step is LOCK.

**UI surface needed:** On an APPROVED run, disable the "Retry" button and do not show "Run Again" options. Show only "Lock Run".

---

### BR-16 — PAID Run Full Immutability
**What:** Once PAID, a DB trigger prevents all updates to both the run and all its results. This is irreversible.

**UI surface needed:** Show a clear warning before the "Mark as Paid" action. Treat PAID state as a terminal read-only view throughout the UI.

---

### BR-17 — Exports: LOCKED or PAID Only
**What:** CSV exports (bank upload, PAYE, pension) can only be downloaded when the run is LOCKED or PAID.

**UI surface needed:** Export buttons must be hidden or disabled for runs not in LOCKED or PAID status. Show the status requirement to the user.

---

### BR-18 — Rate Code: Platform Seeds Cannot Be Deleted
**What:** Rate codes with `workspace_id IS NULL` are platform seeds. Attempting to delete them returns 403.

**UI surface needed:** Platform seed rate codes should be visually distinguished (e.g. read-only badge) and their delete controls hidden or disabled.

---

### BR-19 — National Public Holidays Cannot Be Deleted via Workspace API
**What:** The workspace public holiday delete endpoint returns 404 if the `holiday_id` is not found in the workspace table — national holidays only exist in the national table and are not deletable.

**UI surface needed:** National holidays should be displayed as read-only. Only workspace-specific holidays should show a delete control.

---

### BR-20 — Workspace Status Gate on Running Payroll
**What:** The frontend disables the "New Run" action unless workspace status is LIVE (observed in `PayrollRuns.tsx`).

**UI surface needed:** Show workspace status prominently. Block the run action if not LIVE. Link to workspace setup if setup is incomplete.

---

### BR-21 — Idempotency: Same Key = Same Run
**What:** If `Idempotency-Key` header is provided and a run already exists for that key and workspace, the server returns the original `payroll_run_id` without re-running. Response includes `"idempotent": true`.

**UI surface needed:** Not directly user-facing; relevant to any retry/refresh logic in the frontend to avoid double submissions.

---

### BR-22 — Annualisation Factor by Period Type
**What:** The system uses different annualisation factors to compute annual income equivalents:
- MONTHLY: factor = 12
- FORTNIGHTLY: factor = 26
- CUSTOM: factor = 365 / calendar_days

**UI surface needed:** When the user selects CUSTOM period type, the "Working Days" field becomes required. The UI must show this requirement clearly.

---

### BR-23 — Statutory Rule Temporal Selection
**What:** The engine selects the statutory rule whose `effective_from` is on or before `period_end`. If multiple rules qualify, the most recently effective one wins. If no rule qualifies, the run fails (400).

**UI surface needed:** Not directly user-facing, but the configuration screen should show the effective date of the current statutory rule so operators can see which version is active.
