# Story: Register Employee — Contract Start and End Date Fields
**Written in retrospective — 2026-06-09**
**Sprint 25d — implemented same session, no sprint planning precursor**

---

## Story — Operator captures contract dates when registering a new employee

**As a** payroll bureau operator,
**I want** to enter a contract start date (and optionally an end date) when registering
a new employee,
**So that** the employee's contract reflects their actual hire date rather than the
day the record was entered into the system.

### Acceptance Criteria

**Happy path — start date provided:**
- **Given** I open the Register Employee SlideOver, **then** I see a "Contract" section
  with a "Start Date" (required) and "End Date" (optional) date input.
- **Given** I complete all required fields including Start Date and click Register,
  **then** the employee and contract are created with `start_date` set to the entered value.
- **Given** I leave End Date blank and click Register, **then** the contract is
  created open-ended (`end_date = NULL`).
- **Given** I provide both dates, **then** both are persisted on the contract.

**Validation:**
- **Given** I click Register without entering a Start Date, **then** a validation error
  fires: "First name, last name, employee number, and contract start date are required."
  — the form does not submit.

**Batch entry flow:**
- After a successful registration, the form resets (including the date fields) and stays
  open so the operator can immediately register the next employee.

**Invariant — start date ≠ registration date:**
- The contract start date is always the value the operator enters — the backend default of
  `CURRENT_DATE` (used when `contract_start` is null) is never invoked from this form.

### Out of Scope
- Pre-populating dates from a previously uploaded spreadsheet (bulk upload already handles
  this separately via `handleImport`)
- Editing contract start date post-registration (start date is treated as immutable after
  the contract is created)

### Implementation Summary

**Root cause:** The Register Employee form previously sent `contract_start: null`,
causing the backend `POST /employees` route to default `start_date = CURRENT_DATE`.
All manually registered employees silently got today as their contract start date,
regardless of their actual hire date.

The contract dates were originally present in the form but were removed when the
enrollment fields (salary def, grade, designation) were stripped — the dates were
incorrectly classified as enrollment data. They are HR data and belong on the
registration form.

**Fix:** `frontend/src/pages/Employees.tsx` `AddEmployeeSlideOver`:
- Added `contractStart` (string) and `contractEnd` (string) state.
- Added a "Contract" section between Identity and Payroll Details with two `DateInput`
  components: Start Date (required) and End Date (optional, hint: "Leave blank if
  open-ended").
- `reset()` clears both date fields on each successful registration.
- Validation requires `contractStart` before submission.
- API call passes `contract_start: contractStart` and `contract_end: contractEnd || null`.

No backend changes. No migration required.

### Business Risk / Impact
- **Cost of not doing:** Every manually registered employee has `start_date = today`,
  breaking proration for any employee whose contract started in a prior period — a
  silent data error with financial consequences in the first payroll run that includes them.
- **Cost of doing it wrong:** Operator enters wrong date → incorrect proration for that
  employee's first period. Visible in payroll results; correctable via Edit Employee
  (contract end date) or direct DB update. Not a systemic risk.

### Priority
**P1** — financial correctness. Incorrect start date directly affects proration.
