# Artefact 2 — API Surface Document

> Source: `backend/api/routes/` — every route file read in full.
> All endpoints are prefixed by the FastAPI router mount (no global prefix observed in code).

---

## Workspace Management (`workspace.py`)

| # | Method | Path | Purpose | Key Inputs | Key Outputs |
|---|---|---|---|---|---|
| W1 | POST | `/workspace` | Create a new client workspace | name, country_code, base_currency | workspace_id, status="DRAFT" |
| W2 | GET | `/workspaces` | List all workspaces with employee counts | — | List: workspace_id, name, country_code, status, active_employee_count |
| W3 | GET | `/workspace/info` | Quick summary for header/nav (returns first workspace found) | — | workspace_id, workspace_name, active_employee_count |
| W4 | POST | `/{workspace_id}/transition` | Manually advance workspace status state machine | target_state | result object |
| W5 | GET | `/{workspace_id}/onboarding-status` | Check which onboarding stages are complete | — | Per-stage completeness flags |
| W6 | GET | `/{workspace_id}/employees` | List all employees with active contract details | — | List: employee_id, full_name, employee_number, status, designation, grade, contract_start |
| W7 | PATCH | `/{workspace_id}/employees/contracts` | Bulk-update contract start/end dates by employee_number | List of {employee_number, contract_start, contract_end?} | updated count, not_found list |
| W8 | PATCH | `/{workspace_id}/employees/{employee_id}/contract` | Update a single employee's grade or designation | grade_code, designation_code | status, employee_id |
| W9 | GET | `/{workspace_id}/salary-definitions` | List salary definitions (for UI dropdowns) | — | List: salary_definition_id, code, name |
| W10 | POST | `/{workspace_id}/salary-definitions` | Create a minimal salary definition by code | code, name | salary_definition_id, code, name |
| W11 | GET | `/{workspace_id}/designations` | List designation codes | — | List: designation_id, code |
| W12 | POST | `/{workspace_id}/pay-cycle` | Create pay cycle for workspace | frequency, run_day, cutoff_day, payment_day | Created cycle |
| W13 | GET | `/{workspace_id}/config` | Get full workspace configuration snapshot | — | workspace, pay_cycle, grades, designations, salary_definitions, payroll_rules, component_overrides |
| W14 | PATCH | `/{workspace_id}/component-overrides/{component_code}` | Enable/disable or configure a payroll component | is_active, overrides_json, proration_strategy | status, component_code |
| W15 | GET | `/workspaces/{workspace_id}/payroll-config` | Get public holiday and attendance config (returns defaults if none set) | — | WorkspacePayrollConfig object |
| W16 | PUT | `/workspaces/{workspace_id}/payroll-config` | Create or update versioned payroll config | effective_from, ph_mode, ph_rate_code, saturday_ph_rule, sunday_ph_rule, d3_leave_overlap_rule, d4_absence_rule | Updated config |
| W17 | GET | `/workspaces/{workspace_id}/rate-codes` | List rate codes (platform seeds + workspace-specific, workspace shadows platform for same code) | — | List of rate codes with multiplier, unit, base |
| W18 | POST | `/workspaces/{workspace_id}/rate-codes` | Create workspace-specific rate code | code, multiplier, unit, base, description | Created rate code |
| W19 | DELETE | `/workspaces/{workspace_id}/rate-codes/{code}` | Deactivate workspace rate code (403 if platform seed) | — | status, code |
| W20 | GET | `/workspaces/{workspace_id}/public-holidays` | List public holidays (national + workspace-specific) | year (optional query param) | List with tier indicator |
| W21 | POST | `/workspaces/{workspace_id}/public-holidays` | Add workspace-specific holiday | date (YYYY-MM-DD), name | Created holiday |
| W22 | DELETE | `/workspaces/{workspace_id}/public-holidays/{holiday_id}` | Remove workspace-specific holiday (404 if national) | — | status, holiday_id |

---

## Onboarding (`onboarding.py`, `onboarding_validation.py`)

| # | Method | Path | Purpose | Key Inputs | Key Outputs |
|---|---|---|---|---|---|
| O1 | POST | `/onboarding/upload` | Full upload: validate, generate SQL, optionally execute | workspace_id, employees[], salary_definitions[], payroll_rules[], grades[], designations[] | status, message, review, sql |
| O2 | POST | `/onboarding/preview` | Dry-run: validate and generate SQL without executing | Same as O1 | status, errors[], warnings[], preview: { employees_sql, salary_definitions_sql, payroll_rules_sql } |
| O3 | POST | `/onboarding/commit` | Execute a previously previewed onboarding payload | Same as O1 | status, message, warnings[] |
| O4 | POST | `/onboarding/validate` | Structural validation only (no business logic, fast) | workspace payload | status ("valid"/"invalid"), errors[], warnings[] |

---

## Payroll Inputs (`payroll_input.py`)

| # | Method | Path | Purpose | Key Inputs | Key Outputs |
|---|---|---|---|---|---|
| I1 | GET | `/{workspace_id}/payroll/input-codes` | List valid input codes (derived from active rules) | — | List: code, category, rule_name, calculation_method |
| I2 | GET | `/{workspace_id}/payroll/inputs` | List all unclaimed inputs for workspace | — | List of PayrollInput objects |
| I3 | POST | `/{workspace_id}/payroll/inputs` | Create a single payroll input | employee_id, input_code, quantity?, reference_date? | Created input |
| I4 | POST | `/{workspace_id}/payroll/inputs/bulk` | Bulk-create inputs from Excel-like array | List of input objects | count created, errors[] |
| I5 | DELETE | `/{workspace_id}/payroll/inputs/{input_id}` | Delete an unclaimed input | — | status |

---

## Payroll Runs (`payroll.py`)

| # | Method | Path | Purpose | Key Inputs | Key Outputs |
|---|---|---|---|---|---|
| P1 | POST | `/payroll/run` | Execute a payroll run (also workspace-scoped as `/{workspace_id}/payroll/run`) | workspace_id, period_start?, period_end?, period_type?, working_days?, run_type?, rule_set_id?, retry_strategy?; header: Idempotency-Key | payroll_run_id, summary totals |
| P2 | GET | `/{workspace_id}/payroll/runs` | List all runs for workspace | — | List of run summaries |
| P3 | GET | `/{workspace_id}/payroll/runs/{run_id}` | Get a single run's details | — | Full PayrollRun object |
| P4 | GET | `/{workspace_id}/payroll/runs/{run_id}/results` | Get per-employee results for a run | — | results[], totals{gross, deductions, net, employee_count} |
| P5 | POST | `/payroll/run/{run_id}/approve` | CALCULATED → APPROVED | header: X-Performed-By | run_id, run_status |
| P6 | POST | `/payroll/run/{run_id}/lock` | APPROVED → LOCKED | header: X-Performed-By | run_id, run_status |
| P7 | POST | `/payroll/run/{run_id}/pay` | LOCKED → PAID | body: {actor_id?} | run_id, run_status |
| P8 | POST | `/payroll/run/{run_id}/retry` | Retry FAILED employees in a PARTIAL run | header: X-Performed-By | retried count, success count, still_failed count |
| P9 | GET | `/{workspace_id}/payroll/runs/{run_id}/reconciliation` | Get reconciliation record for a run | — | ReconciliationRecord |
| P10 | POST | `/{workspace_id}/payroll/runs/{run_id}/reconciliation` | Submit actual payment total (creates MATCHED or MISMATCH) | actual_payment | ReconciliationRecord |
| P11 | PATCH | `/{workspace_id}/payroll/runs/{run_id}/reconciliation` | Resolve a MISMATCH (MISMATCH → RESOLVED) | notes, resolved_by | ReconciliationRecord |
| P12 | GET | `/{workspace_id}/payroll/runs/{run_id}/timeline` | Get execution trace steps in order | — | List of trace steps |
| P13 | GET | `/{workspace_id}/payroll/runs/{run_id}/audit` | Get audit log entries for a run | — | List: entity_type, action, old_value, new_value, performed_by, performed_at |
| P14 | GET | `/{workspace_id}/payroll/runs/{run_id}/exports/bank-upload` | Download bank upload CSV (LOCKED or PAID only) | — | CSV: employee_number, employee_name, bank_name, account_number, net_pay |
| P15 | GET | `/{workspace_id}/payroll/runs/{run_id}/exports/paye` | Download PAYE remittance CSV (LOCKED or PAID only) | — | CSV: employee_number, employee_name, tin, gross_pay, paye_withheld, period |
| P16 | GET | `/{workspace_id}/payroll/runs/{run_id}/exports/pension` | Download pension contribution CSV (LOCKED or PAID only) | — | CSV: employee_number, employee_name, rsa_pin, basic_pay, pension_base, employee_contribution, employer_contribution, period |
| P17 | GET | `/{workspace_id}/payroll/ops/legacy-executor-stats` | Monitoring — legacy executor usage stats | — | total_runs, runs_with_legacy, pct_affected, by_run |

---

## Admin / HTML Templates (`admin.py`)

| # | Method | Path | Purpose |
|---|---|---|---|
| A1 | GET | `/admin` | Serve admin dashboard HTML template |
| A2 | GET | `/admin/onboarding` | Serve onboarding HTML template |
| A3 | GET | `/admin/payroll` | Serve payroll HTML template |

---

## Health (`health.py`)

| # | Method | Path | Purpose |
|---|---|---|---|
| H1 | GET | `/health` | Liveness check — returns {"status": "ok"} |

---

## Key Error Codes the UI Must Handle

| HTTP Code | When |
|---|---|
| 400 | Missing required fields, invalid business state (e.g. wrong run status for action) |
| 403 | Attempt to delete a platform-seeded rate code |
| 404 | Workspace, run, employee, or reconciliation not found |
| 409 | Duplicate run for same period, duplicate reconciliation, rate code code collision |
| 422 | Validation failure — payroll readiness not met; returns structured error list |
| 500 | Statutory rule misconfigured (missing pension rates in rules_jsonb) |
