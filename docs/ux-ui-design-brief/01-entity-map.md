# Artefact 1 — Entity Map

> Source: `backend/infra/db/models/`, route SQL queries, and frontend type definitions.
> Rule: Code is authoritative. Where schema and types diverge, the DB schema wins.

---

## Core Entities

### 1. Workspace
The top-level tenant boundary. Every piece of data belongs to exactly one workspace.

| Field | Type | Notes |
|---|---|---|
| workspace_id | UUID | Primary key |
| name | Text | Client company name |
| country_code | String | e.g. "NG" — drives statutory rule selection |
| base_currency | String | e.g. "NGN" |
| status | Enum | DRAFT → STRUCTURE_DEFINED → COMPENSATION_DEFINED → RULES_DEFINED → READY → LIVE |

**Relationships:** Has many Employees, PayrollRuns, SalaryDefinitions, PayrollRules, Grades, Designations, PayCycle (one active), ComponentOverrides, WorkspacePayrollConfig, RateCodes, WorkspacePublicHolidays.

---

### 2. Employee
A person employed within a workspace. Linked to salary via a contract.

| Field | Type | Notes |
|---|---|---|
| employee_id | UUID | Primary key |
| workspace_id | UUID | FK to Workspace |
| full_name | Text | Display name |
| employee_number | String | Unique identifier per workspace |
| status | Enum | ACTIVE, INACTIVE |
| personal_details_encrypted | JSONB | Sensitive biodata: TIN, RSA (pension pin), BANK, ACCOUNT_NUMBER |

**Relationships:** Has one or more EmployeeContracts (only one active at a time). Has many PayrollResults and PayrollInputs.

---

### 3. EmployeeContract
Binds an employee to a salary definition and optionally a grade and designation for a date range.

| Field | Type | Notes |
|---|---|---|
| contract_id | UUID | Primary key |
| employee_id | UUID | FK to Employee |
| salary_definition_id | UUID | FK to SalaryDefinition |
| grade_id | UUID | FK to Grade (nullable) |
| designation_id | UUID | FK to Designation (nullable) |
| start_date | Date | Contract effective from |
| end_date | Date | Nullable — open contracts have no end date |

**Relationships:** Belongs to Employee; references SalaryDefinition, Grade, Designation.

---

### 4. SalaryDefinition
A named template defining salary component amounts. Multiple employees may share one definition.

| Field | Type | Notes |
|---|---|---|
| salary_definition_id | UUID | Primary key |
| workspace_id | UUID | FK to Workspace |
| code | String | Short identifier (e.g. grade code from Excel) |
| name | Text | Human-readable label |
| components_jsonb | JSONB | `{ COMPONENT_CODE: { amount: Decimal }, ... }` |
| effective_from | Date | Nullable |
| effective_to | Date | Nullable |

**Relationships:** Used by many EmployeeContracts. Components correspond to entries in ComponentMetadata.

---

### 5. PayCycle
The pay schedule for a workspace. Only one active cycle per workspace at a time.

| Field | Type | Notes |
|---|---|---|
| pay_cycle_id | UUID | Primary key |
| workspace_id | UUID | FK to Workspace |
| frequency | String | monthly, biweekly, weekly |
| run_day | Integer | Day of month/period to run payroll |
| cutoff_day | Integer | Input cutoff day |
| payment_day | Integer | Day employees are paid |
| is_active | Boolean | At most one TRUE per workspace |
| definition_json | JSONB | Extension data |

---

### 6. PayrollRun
A single payroll execution for a workspace and period.

| Field | Type | Notes |
|---|---|---|
| payroll_run_id | UUID | Primary key |
| workspace_id | UUID | FK to Workspace |
| status | Enum | DRAFT, CALCULATING, CALCULATED, PARTIAL, APPROVED, LOCKED, PAID |
| period_start | Date | Pay period start |
| period_end | Date | Pay period end |
| pay_date | Date | Intended payment date |
| created_at | DateTime | |
| total_gross_pay | Decimal(18,2) | Sum of all employee gross pays |
| total_deduction | Decimal(18,2) | Sum of all deductions |
| total_net_pay | Decimal(18,2) | Sum of all employee net pays |
| idempotency_key | String | Optional deduplication key |
| rules_context_snapshot_jsonb | JSONB | Immutable snapshot of rules used |

**Constraints:** `(workspace_id, period_start, period_end)` is unique — no duplicate periods. `(workspace_id, idempotency_key)` is unique.

**Relationships:** Has many PayrollResults (one per employee). Has at most one PayrollReconciliation.

---

### 7. PayrollResult
The computed payroll output for one employee within one run.

| Field | Type | Notes |
|---|---|---|
| payroll_result_id | UUID | Primary key |
| payroll_run_id | UUID | FK to PayrollRun |
| employee_id | UUID | FK to Employee |
| status | Enum | SUCCESS, FAILED, PARTIAL |
| net_pay | Decimal(18,2) | Null if FAILED |
| gross_components_jsonb | JSONB | Per-earning-component amounts |
| deductions_jsonb | JSONB | Per-deduction-component amounts |
| component_trace_jsonb | JSONB | Step-by-step execution trace |

**Immutability:** A DB trigger prevents any updates once the parent run reaches PAID status.

---

### 8. PayrollReconciliation
The record of actual vs expected payment for a completed run.

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| payroll_run_id | UUID | FK to PayrollRun (unique — one per run) |
| expected_total | Decimal(18,2) | Copied from payroll_run.total_net_pay |
| actual_total | Decimal(18,2) | Supplied by operator after disbursement |
| status | Enum | MATCHED, MISMATCH, PENDING (legacy), RESOLVED |
| reconciled_at | DateTime | When MATCHED or MISMATCH was created |
| notes | Text | Operator explanation (required when resolving) |
| resolved_by | String | Identity of resolver (required when resolving) |
| resolved_at | DateTime | When resolution was recorded |

---

### 9. PayrollInput
A variable event (overtime, leave, etc.) entered for an employee before a run.

| Field | Type | Notes |
|---|---|---|
| payroll_input_id | UUID | Primary key |
| workspace_id | UUID | FK to Workspace |
| payroll_run_id | UUID | FK to PayrollRun (null until claimed by a run) |
| employee_id | UUID | FK to Employee |
| input_code | String | Valid code from active payroll rules |
| input_category | Enum | EARNING, DEDUCTION, INFORMATION |
| quantity | Decimal(12,2) | Optional; must be >= 0 |
| reference_date | Date | For cross-period inputs; normalised to 1st of month |
| source | String | "MANUAL" or upload source |
| input_json | JSONB | Extension data |

**State:** "Unclaimed" = payroll_run_id is null. "Claimed" = linked to a run after run execution.

---

### 10. StatutoryRule
The Nigerian tax and statutory deduction parameters for a country at a point in time.

| Field | Type | Notes |
|---|---|---|
| statutory_rule_id | UUID | Primary key |
| country_code | String | e.g. "NG" |
| version | Integer | Increments on update |
| effective_from | Date | Temporal selection key |
| rules_jsonb | JSONB | Contains: pension (employee_rate, employer_rate), nhf (employee_rate), health_insurance (employee_amount), development_levy (amount), life_insurance (employer_rate), reliefs (rent_relief) |
| tax_method | String | "CUMULATIVE" (PAYE method) |

**Unique constraint:** `(country_code, effective_from)` — no two rules for the same country and date.

**Relationships:** Has many TaxBands.

---

### 11. TaxBand
One bracket in the progressive PAYE tax schedule for a given statutory rule.

| Field | Type | Notes |
|---|---|---|
| statutory_rule_id | UUID | FK to StatutoryRule |
| lower_limit | Decimal(18,2) | Band start (NGN) |
| upper_limit | Decimal(18,2) | Band end (NGN); null = top band |
| rate | Decimal(8,6) | Rate as fraction (e.g. 0.05 = 5%) |

---

### 12. ComponentMetadata
Platform-level definition of every payroll component (earnings, deductions, employer costs).

| Field | Type | Notes |
|---|---|---|
| component_metadata_id | UUID | Primary key |
| component_code | String | e.g. "BASIC", "PAYE", "PENSION_EMPLOYEE" |
| country_code | String | Scoped to country |
| component_class | Enum | earning, statutory_deduction, employer_cost |
| calculation_method | String | Algorithm identifier |
| execution_priority | Integer | Processing order |
| is_active | Boolean | |
| metadata_json | JSONB | Detailed metadata including proration_strategy |
| effective_from | Date | |

---

### 13. ClientComponentMetadata (Component Override)
Workspace-level overrides on top of platform component definitions.

| Field | Type | Notes |
|---|---|---|
| client_component_metadata_id | UUID | Primary key |
| workspace_id | UUID | FK to Workspace |
| component_code | String | References ComponentMetadata.component_code |
| overrides_json | JSONB | `{ is_active, monthly_amount, employee_monthly_amount, calculations_behaviour: { proration_strategy } }` |

**Unique constraint:** `(workspace_id, component_code)`.

---

### 14. PayrollRule (Legacy)
Workspace-specific earning/deduction rules (being superseded by RuleSet).

| Field | Type | Notes |
|---|---|---|
| rule_id | UUID | Primary key |
| workspace_id | UUID | FK to Workspace |
| rule_name | String | |
| rule_type | Enum | EARNING, DEDUCTION, INFORMATION |
| rule_definition_json | JSONB | Calculation definition |
| is_active | Boolean | |

---

### 15. RuleSet / RuleSetItem
Versioned, immutable snapshots of workspace rules published at a point in time.

| RuleSet Field | Notes |
|---|---|
| rule_set_id | UUID PK |
| workspace_id | FK |
| effective_from | Date — temporal selection key |
| created_at | DateTime |
| created_by | UUID |

| RuleSetItem Field | Notes |
|---|---|
| rule_set_id | Part of composite PK |
| rule_name | Part of composite PK |
| rule_definition_json | JSONB — immutable copy |
| rule_type | EARNING, DEDUCTION, INFORMATION |

**Unique constraint on RuleSet:** `(workspace_id, effective_from)`.

---

### 16. WorkspacePayrollConfig
Time-versioned public holiday and attendance behaviour settings for a workspace.

| Field | Type | Notes |
|---|---|---|
| config_id | UUID | Primary key |
| workspace_id | UUID | FK to Workspace |
| effective_from | Date | Temporal selection key |
| ph_mode | Enum | AUTOMATIC, FILE_BASED |
| ph_rate_code | String | e.g. "OT005" — rate code for public holiday pay |
| saturday_ph_rule | Enum | PH_TAKES_PRECEDENCE, DAY_OF_WEEK_TAKES_PRECEDENCE |
| sunday_ph_rule | Enum | PH_TAKES_PRECEDENCE, DAY_OF_WEEK_TAKES_PRECEDENCE |
| d3_leave_overlap_rule | Enum | LEAVE_ABSORBS_PH, PH_ADDITIVE |
| d4_absence_rule | Enum | ABSENT_IS_DEDUCTIBLE, PH_EXCUSES_ABSENCE |

---

### 17. RateCodeRegistry
Defines multiplier codes used for public holiday pay calculation.

| Field | Type | Notes |
|---|---|---|
| rate_code_id | UUID | Primary key |
| workspace_id | UUID | Null for platform seeds |
| code | String | e.g. "OT005" |
| multiplier | Decimal(8,4) | e.g. 1.5 = 150% of base |
| unit | String | hour, day |
| base | String | basic_hourly, basic_daily |
| description | String | |
| is_active | Boolean | |

---

### 18. NationalPublicHoliday / WorkspacePublicHoliday
Two-tier public holiday calendar: national (platform-managed) and workspace-specific.

| Field | Notes |
|---|---|
| holiday_id | UUID PK |
| country_code / workspace_id | Scope |
| holiday_date | Date |
| name | String |

---

### 19. Grade / Designation
Simple lookup codes used to categorise employees within a workspace.

| Field | Notes |
|---|---|
| grade_id / designation_id | UUID PK |
| workspace_id | FK |
| grade_code / designation_code | Unique per workspace |
| description | Optional label |

---

### 20. AuditLog
Immutable record of all state-transition actions.

| Field | Notes |
|---|---|
| entity_type | e.g. "payroll_run" |
| entity_id | UUID of affected entity |
| action | e.g. "APPROVE", "LOCK", "PAY" |
| old_value_jsonb | State before |
| new_value_jsonb | State after |
| performed_by | Identity string |
| performed_at | DateTime |
| workspace_id | Scoping |
