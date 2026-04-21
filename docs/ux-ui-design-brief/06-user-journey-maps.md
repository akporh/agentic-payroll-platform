# Artefact 6 — User Journey Maps

> Each journey is derived from the actual API endpoints and page files in the codebase.
> Where a step is implied by the data model but not yet wired to a UI screen, it is flagged.

---

## Journey 1 — Chidi (Bureau Admin): Onboard a New Client

1. Navigate to Bureau Dashboard — see all workspaces and their statuses.
2. Click "New Workspace" — enter client company name, country code (NG), base currency (NGN).
   - System creates workspace with status DRAFT.
   - Validation: country_code must have statutory rules configured (422 if not).
3. Navigate to the new workspace's onboarding flow (WorkspaceSetup screen).
4. Upload or enter: grades, designations, salary definitions, payroll rules, pay cycle.
   - Option A: Structured JSON/form entry.
   - Option B: JSON onboarding upload (`JsonOnboarding.tsx`).
5. Click "Preview" — system validates the payload and returns errors/warnings without committing.
6. Review any errors; fix and re-preview until clean.
7. Click "Commit" — system atomically inserts all records and auto-advances workspace status:
   DRAFT → STRUCTURE_DEFINED → COMPENSATION_DEFINED → RULES_DEFINED → READY.
8. Manually advance workspace to LIVE (via transition endpoint or a "Go Live" button).
9. Return to Bureau Dashboard — workspace appears as LIVE with employee count.

**Failure modes to surface:**
- Preview returns errors (missing fields, unknown codes) — must be displayed per field.
- Commit fails mid-transaction — system rolls back; user must re-commit entire payload.
- country_code has no statutory rules — hard block with admin contact prompt.

---

## Journey 2 — Ngozi (HR Admin): Update Employee Records

1. Navigate to Employees screen for the workspace.
2. View employee list (name, number, status, grade, designation, contract start).
3. Find an employee who has been promoted — click to edit contract.
4. Update grade_code and/or designation_code — system patches the active contract.
5. If multiple employees have contract date changes (e.g. year-end restructure):
   - Use bulk contract update — provide list of employee_number + contract_start + contract_end.
   - System returns count of updated and list of not_found numbers.
6. Confirm changes are reflected in the employee list.

**Failure modes to surface:**
- Grade or designation code not found in workspace — 400 error.
- Employee number not found — appears in `not_found` list (not an error, but must be visible).

---

## Journey 3 — Adaeze (Payroll Operator): Collect and Enter Variable Inputs

1. Navigate to Payroll Inputs screen for the workspace.
2. Check what unclaimed inputs already exist (from previous uploads or entries).
3. Receive input data from client HR contact (overtime hours, leave days, bonuses).
4. Option A — Individual entry: Click "Add Input", select employee, input code, quantity, and optionally a reference date if the event applies to a past period.
5. Option B — Bulk upload: Navigate to Bulk Upload screen. Prepare Excel with columns: employee_number, input_code, quantity, reference_date. Upload. System creates all valid inputs and returns error list for invalid rows.
6. Review unclaimed input list — confirm all inputs are captured.
7. Delete any erroneous inputs before the run.

**Failure modes to surface:**
- Invalid input_code (not in workspace's active rules) — 422.
- Negative quantity — 422.
- Unknown employee_number — error in bulk upload response.
- reference_date not parseable — 422.

---

## Journey 4 — Adaeze (Payroll Operator): Run and Review Payroll

1. Navigate to Payroll Runs screen.
2. Verify workspace status is LIVE — if not, "New Run" is disabled.
3. Click "New Run" — navigate to Run Payroll screen.
4. Select or confirm: period_start, period_end, period_type (MONTHLY/FORTNIGHTLY/CUSTOM).
   - If CUSTOM: enter working_days (required).
5. Submit the run.
   - System executes asynchronously (or synchronously — not clear from code).
   - Run status begins as CALCULATING.
6. Return to Payroll Runs list — see new run with status.
7. If status is PARTIAL: some employees failed. Navigate to results.
8. On Payroll Results screen, find employees with FAILED status.
9. Investigate failure: check component trace for error details.
10. Fix the underlying data (e.g. missing input, bad salary definition).
11. Click "Retry" on the run — system reprocesses only FAILED employees.
12. Repeat until no FAILED employees remain — run transitions to CALCULATED.
13. Review totals and per-employee results for sense-check.
14. Hand off to Emeka for approval.

**Failure modes to surface:**
- 400: No active employees, missing statutory rule, workspace not found.
- 409: Run already exists for this period — show existing run, do not create duplicate.
- 422: Payroll readiness check failed — show structured error list with links to fix each issue.
- PARTIAL result: clearly indicate how many employees failed and list them.

---

## Journey 5 — Emeka (Finance Authoriser): Approve and Lock a Run

1. Receive notification from Adaeze that a run is in CALCULATED status.
2. Navigate to Payroll Runs screen — find the run in CALCULATED state.
3. Open the run — review totals (gross, deductions, net), employee count.
4. Navigate to Payroll Results — spot-check individual employees if needed.
5. Check audit log — confirm who ran the payroll and when.
6. Click "Approve" — run moves to APPROVED.
   - Audit log records: action=APPROVE, performed_by=Emeka's identity.
7. Notify the bank team to initiate payment.
8. Receive bank confirmation of payment value.
9. Click "Lock Run" — run moves to LOCKED.
   - Export buttons become available.
10. Download bank upload CSV — send to bank for reconciliation file match.
11. Navigate to Reconciliation screen for the run.
12. Enter actual_payment total from bank confirmation.
13. System compares against expected (total_net_pay):
    - MATCHED: reconciliation complete.
    - MISMATCH: proceed to resolution.
14. If MISMATCH: investigate discrepancy. Enter resolution notes and resolved_by name. Submit.
    - Run reconciliation status → RESOLVED.
15. Click "Mark as Paid" — run moves to PAID (terminal, irreversible).
    - Confirm dialog must warn about irreversibility.

**Failure modes to surface:**
- Approve attempt on non-CALCULATED run — 400.
- Lock attempt on non-APPROVED run — 400.
- Reconciliation submitted on non-LOCKED run — 400.
- Duplicate reconciliation submission — 409.
- Resolution attempt on non-MISMATCH record — 400.

---

## Journey 6 — Tunde (Compliance Officer): Download Statutory Reports

1. Navigate to Payroll Runs screen after payroll is LOCKED or PAID.
2. Find the relevant run by period.
3. Click "Download PAYE Remittance" — CSV downloads immediately.
4. Click "Download Pension Contributions" — CSV downloads immediately.
5. Upload files to relevant regulatory portals (external to this system).

**Failure modes to surface:**
- Run not yet LOCKED — exports disabled with status reason shown.
- Employees with FAILED results — excluded from CSVs silently (UI should note this).

---

## Journey 7 — Chidi (Bureau Admin): Monitor and Triage Across Workspaces

1. Open Bureau Dashboard — see all workspaces with key metrics.
2. Identify any workspaces with: runs stuck in CALCULATING, MISMATCH reconciliations, incomplete onboarding.
3. Drill into a specific workspace.
4. Check run timeline (execution trace) for any run that appears stuck.
5. Check legacy executor stats (ops endpoint) to see if any runs are falling back to the deprecated path.
6. Take corrective action or escalate.

**Note:** The Bureau Dashboard page exists (`BureauDashboard.tsx`) but the exact metrics it surfaces are not determinable from the current page file without reading its full content.

---

## Journey 8 — Chidi (Bureau Admin): Configure Public Holidays for a Workspace

1. Navigate to Public Holidays screen for a workspace.
2. See combined list: national (read-only, Tier-1) and workspace-specific (editable, Tier-2).
3. Filter by year if needed.
4. Add a workspace-specific holiday: enter date and name.
5. Delete a workspace-specific holiday if incorrectly entered.
6. Configure payroll config (navigate to workspace payroll config):
   - Set PH mode (AUTOMATIC or FILE_BASED).
   - Set ph_rate_code (which rate code to use for PH pay calculation).
   - Set conflict resolution rules for Saturday PH, Sunday PH, leave overlap, absence.
7. Add or review rate codes if a new multiplier is needed for PH pay.
