# Sprint 20: HR Readiness — Phase 3

**Delivery increment:** Contract history UI + mid-period deactivation handling + deactivation UX + external identity field  
**Depends on:** Sprint 17 (employee CRUD + append-only contract model), Sprint 18 (Phase 1 constraints), Sprint 19 (snapshot engine)  

---

## Context — What the prior sprints resolved

| Q | Question | Resolution |
|---|----------|-----------|
| Q2 | Salary definition versioning | ✅ Closed — run-time resolve; Phase 2 `salary_inputs_snapshot` covers audit |
| Q4 | Contract history audit | ✅ Closed — Sprint 17 append-only model captures history; Phase 2 per-result snapshot |
| Q5 | Period-based cohort runs | ✅ Closed — keep all-active; no subsetting needed |
| Q6 | Timesheet-first vs employee-first | ✅ Closed — employee-first; hard rejection on missing employee |
| Q1 | External HR source / identity | Deferred — external_id not needed day one (P3-3 below) |
| Q3 | Mid-period deactivation | Partial — mid-period new hires = next period only; deactivation handling = P3-2 below |

---

## Scope Boundary

**IN scope:**
- UI to view an employee's full contract history (past contracts, dates, grade changes)
- System behaviour when an employee is deactivated mid-period (inputs, results, payroll inclusion)
- `external_id` field on the employee table for future HR system integration

**OUT of scope:**
- HR system sync / API integration (no live HR system in scope for MVP)
- Bulk employee deactivation
- Retroactive contract editing
- Proration for mid-period deactivations (separate calculation story)

---

## EMP-P3-1 · Contract history UI

**Priority:** P2 — Operator productivity (data model exists from Sprint 17; UI is the remaining gap)

**As a** workspace administrator,  
**I want** to view the full contract history for any employee,  
**So that** I can see every grade and salary change with its effective dates without needing to query the database directly.

### Acceptance Criteria

**Given** an employee who has had two or more contracts (i.e. a grade/salary change was made via the "Change Grade/Salary" slide-over in Sprint 17),  
**When** I open the employee detail view,  
**Then** a "Contract History" section lists all contracts in reverse chronological order, showing:
- Salary definition name
- Start date
- End date (or "Current" if `end_date IS NULL`)
- Change reason

**Given** an employee with only one contract (never had a change),  
**When** I open their detail view,  
**Then** the history section shows one row with no end date — labelled "Current".

**Given** the contract history list,  
**When** I view it,  
**Then** it is read-only — no edit or delete actions are available on historical rows.

**Given** a contract that was closed as part of a mid-period run (end_date falls within a completed pay period),  
**When** I view the history,  
**Then** the closed contract shows the exact end_date that was set — not a derived or approximated value.

### Out of Scope
- Editing or reverting historical contracts
- Exporting contract history
- Audit log of who made the change (no `changed_by` field exists yet)

### Business Risk
- **Not done:** Administrators have no visibility into grade/salary history without DB access. Disputes about "what salary was this employee on in March?" cannot be resolved in the UI.

### Open Questions
- None. Sprint 17 append-only model provides the data. This story is UI-only.

---

## EMP-P3-2 · Mid-period employee deactivation handling

**Priority:** P1 — Data integrity (orphaned payroll inputs are a financial risk)

**As a** payroll operator,  
**I want** the system to have defined, predictable behaviour when an employee is deactivated during a pay period,  
**So that** I know whether that employee appears in the payroll run, and what happens to any payroll inputs already recorded for them.

### Acceptance Criteria

**Payroll inclusion rule**

**Given** an employee whose contract ends (end_date set) on a date within the current pay period,  
**When** a payroll run is triggered for that period,  
**Then** the employee IS included in the run — the period-overlap predicate (`start_date <= period_end AND (end_date IS NULL OR end_date >= period_start)`) includes them.

**Given** an employee whose contract ends before the pay period starts,  
**When** a payroll run is triggered,  
**Then** the employee is NOT included — contract ended before the period.

**Payroll inputs (open inputs for a deactivated employee)**

**Given** payroll inputs have been recorded for an employee and the employee is subsequently deactivated (contract end_date set within the period),  
**When** a payroll run is triggered,  
**Then** the existing inputs are processed normally — deactivation does not delete or discard inputs already recorded.

**Given** an attempt is made to add new payroll inputs for an employee whose contract has ended before the period start,  
**When** the input is submitted,  
**Then** the system rejects it with a clear error: `"Employee {number} has no active contract in this period"`.

**Status field rule**

**Given** an employee's `status` field is set to `INACTIVE`,  
**When** a payroll run is triggered,  
**Then** `status` is NOT used for payroll inclusion or exclusion — only contract dates determine inclusion (confirmed arch principle: contracts define employment, not employee status).

**Operator warning — unprocessed inputs for excluded employees**

**Given** one or more employees are excluded from a payroll run (contract ended before period start) AND those employees have recorded payroll inputs for the period (e.g. bonus, overtime, deduction),  
**When** the payroll run is initiated,  
**Then** the API response includes a warning listing the affected employee numbers: e.g. `"The following employees are excluded from this run but have unprocessed inputs: EMP-001, EMP-007"`.  
**And** the run still proceeds — this is a warning, not a blocker.  
**And** the inputs are NOT silently discarded — they remain in `payroll_input` for the operator to action.

**Why this matters:** An unprocessed bonus means an employee was underpaid; an unprocessed recovery deduction means the company failed to reclaim money owed. Both are financial errors that must be visible before the run is finalised.

### Out of Scope
- Automatic proration for partial periods (separate calculation sprint)
- Bulk deactivation workflows
- Automatic deactivation from HR feed

### Business Risk
- **Not done:** An employee deactivated mid-period could either be silently excluded (underpayment, legal risk) or silently included (overpayment). Both are financial and compliance failures.
- **Done wrong:** Using `status = INACTIVE` as the exclusion mechanism is architecturally incorrect — confirmed in arch-council decisions. Contract dates are the only authoritative source.

**Results screen — final period indicator**

**Given** a payroll run includes an employee whose contract `end_date` falls within the current period (i.e. this is their last payslip),  
**When** the operator views the run results,  
**Then** that employee's result row is marked "Final period" (or equivalent label) with their contract end date visible.  
**And** this indicator is present both in the on-screen results table and in any exported payslip or results file for that run.

**Operator warning — unprocessed inputs at point of deactivation**

**Given** an operator sets a contract `end_date` for an employee (deactivating them),  
**AND** that employee has recorded payroll inputs for a period that starts after their contract end date,  
**When** the deactivation is saved,  
**Then** the API response includes a warning: `"Employee {number} has {n} unprocessed input(s) in period(s) after their contract end date. Review before confirming deactivation."`.  
**And** the deactivation still saves — this is a warning, not a blocker.

### Open Questions
- None. OQ-1 resolved: show "Final period" on results screen. OQ-2 resolved: warn operator at point of deactivation and at run time.

---

## EMP-P3-3 · External identity field (`external_id`)

**Priority:** P3 — Future HR integration enabler (not blocking MVP)

**As a** workspace administrator integrating with an external HR system,  
**I want** each employee record to carry an optional `external_id` field,  
**So that** payroll records can be matched to the HR system's employee reference without relying on `employee_number` (which may be redefined per bureau).

### Acceptance Criteria

**Given** the migration is applied,  
**When** the `employee` table is inspected,  
**Then** an `external_id VARCHAR NULL` column exists, with `UNIQUE(workspace_id, external_id) WHERE external_id IS NOT NULL`.

**Given** two employees in the same workspace,  
**When** they are given the same `external_id`,  
**Then** the DB rejects the second with a unique constraint violation.

**Given** two employees in different workspaces with the same `external_id`,  
**When** both are inserted,  
**Then** both succeed — uniqueness is workspace-scoped.

**Given** an employee is created without an `external_id`,  
**Then** the field is NULL — not required, not defaulted.

**Given** the POST /employees and PATCH /employees/{eid} endpoints,  
**When** a payload includes `external_id`,  
**Then** the value is stored. When the payload omits it, the existing value is unchanged (PATCH semantics).

**Given** `alembic downgrade -1`,  
**Then** the column and partial unique index are dropped cleanly.

### Out of Scope
- Syncing employees from an HR system (no live integration in this story)
- Exposing `external_id` as a search/lookup field in the UI (future)
- Making `external_id` mandatory

### Business Risk
- **Not done now:** No immediate risk. MVP does not require HR system integration. This is an enabler for when it becomes needed.
- **Done wrong:** If the unique constraint is non-partial (not `WHERE external_id IS NOT NULL`), multiple employees without an `external_id` would violate the constraint — NULL must be allowed freely.

### Open Questions
- **OQ-1:** Is `external_id` needed before any HR integration is contracted? If not, defer past Sprint 20.
