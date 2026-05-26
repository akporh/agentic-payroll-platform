# Employee Page Enhancements — Retrospective Stories

Delivered: 2026-05-26
Implemented in: `frontend/src/pages/Employees.tsx`, `backend/api/routes/workspace.py`, `frontend/src/api/workspace.ts`

---

## Story EMP-01 — Show Contract Start and End Dates in Employee List

**As a** payroll bureau operator,
**I want to** see each employee's contract start and end date directly in the employee list,
**So that** I can identify upcoming contract terminations and audit contract coverage without opening individual records.

### Acceptance Criteria

- **Given** the employee list is loaded, **when** I view any section (Active, Unmatched, Ended), **then** both a Start Date and End Date column are visible on every row
- **Given** an employee has no end date, **when** I view their row, **then** End Date shows "—" (not blank, not null, not an error)
- **Given** an active employee has a future end date set, **when** I view their row, **then** the end date is shown in amber to signal a scheduled termination
- **Given** an employee is in the Contract Ended section, **when** I view their row, **then** the end date is shown in standard grey (it is historical, not a warning)

### Out of Scope
- Sorting or filtering by date in this story
- Date-range alerts or expiry notifications

### Business Risk
- **Cost of NOT doing**: Operators cannot see upcoming terminations at a glance — they either miss them or have to open every record. In a 177-person payroll, this is a real audit gap.
- **Cost of doing it wrong**: If is_ended logic is wrong, active employees appear in the Ended section — they are excluded from the next payroll run silently.

### Priority: P2 — Operator productivity / audit visibility

---

## Story EMP-02 — Add a Single Employee

**As a** payroll bureau operator,
**I want to** add a new employee directly from the Employees page,
**So that** I can onboard a single joiner without triggering the full workspace onboarding wizard.

### Acceptance Criteria

- **Given** I am on the Employees page, **when** I click "Add Employee", **then** a SlideOver opens with fields for: first name, last name, employee number, salary definition, grade, designation, contract start, contract end, TIN, RSA, bank, account number
- **Given** I submit the form with all required fields (name, employee number, salary definition), **when** the save succeeds, **then** the new employee appears in the Active or Unmatched section immediately (list reloads) and a success toast confirms the name
- **Given** I submit an employee number that already exists in this workspace, **when** the API responds, **then** I see a specific error: *"Employee number 'X' already exists in this workspace"* — not a generic failure
- **Given** I enter an invalid salary definition code, **when** the API responds, **then** I see a specific error naming the code that was not found
- **Given** I enter a contract_end earlier than contract_start, **when** the API responds, **then** I see a validation error before the record is created
- **Given** I leave contract start blank, **when** the record is created, **then** contract start defaults to today
- **Given** I close the SlideOver without saving, **when** I reopen it, **then** all fields are empty (no stale state)

### Out of Scope
- Editing existing employee core identity fields (name, employee number) — separate story
- Bulk creation via this form
- Validation of TIN/RSA format (free text for now)

### Business Risk
- **Cost of NOT doing**: Every new joiner requires re-running the onboarding wizard — disproportionate effort for a single hire mid-period.
- **Cost of doing it wrong**: If the employee is created without a contract record, they will be invisible to the payroll engine — they appear in the list but produce no results and no error.

### Priority: P2 — Operator productivity

### Open Questions (future sprints)
- Should adding an employee with a past contract_start trigger a backdated payroll input prompt?
- Should the system warn if the salary definition selected has no components configured?

---

## Story EMP-03 — Bulk Upload Employees via Excel

**As a** payroll bureau operator,
**I want to** upload a spreadsheet of new employees in one action,
**So that** I can onboard a cohort of joiners quickly without entering each one individually.

### Acceptance Criteria

- **Given** I am on the Employees page, **when** I click "Upload from Excel", **then** a SlideOver opens with the existing Excel upload and mapping interface
- **Given** I upload a valid `.xlsx` or `.csv` file with the required columns, **when** parsing completes, **then** I see a preview of loaded employees and any unresolved salary definition or designation mappings that need attention before import
- **Given** all employees are mapped (no unresolved rows), **when** I click "Import N Employees", **then** the system creates each employee sequentially and shows a results summary on completion
- **Given** import completes with some successes and some failures, **when** I view the results, **then** I see a table listing each failed employee by name and employee number with a specific reason per row — not a single aggregate error
- **Given** import completes with at least one success, **when** I view the results, **then** the employee list reloads in the background
- **Given** some employees in the file are unresolved (mapping_unresolved or designation_unresolved = true), **when** I attempt to import, **then** only resolved rows are imported; unresolved rows are excluded from the batch
- **Given** I close the SlideOver after a successful import, **when** I reopen it, **then** the file and results are cleared

### Out of Scope
- Editing existing employees via upload (additive only)
- Updating employee numbers via upload
- Partial retry of failed rows without re-uploading the file

### Business Risk
- **Cost of NOT doing**: Period-end batch onboarding (e.g. 50 new hires) requires 50 individual form submissions — a full working day of data entry.
- **Cost of doing it wrong**: Silent partial import with no per-row feedback causes the operator to believe all employees are loaded when they are not — missing employees produce no payroll output and no error.

### Priority: P2 — Operator productivity (high leverage: saves hours per cohort)

### Open Questions
- Should failed import rows be downloadable as a corrected template for re-upload?
- Is there a maximum row count that should be enforced (e.g. 500 rows) to prevent timeouts on large batches?

---

## Story EMP-04 — Edit an Employee's Contract End Date

**As a** payroll bureau operator,
**I want to** set or update a contract end date on an existing employee from the Employees page,
**So that** I can schedule a termination or correct a wrongly set end date without going through onboarding.

### Acceptance Criteria

- **Given** I click Edit on any employee (active or ended), **when** the SlideOver opens, **then** it shows a Contract End Date field pre-populated with the current end date (or blank if open-ended)
- **Given** I enter a valid date and save, **when** the save succeeds, **then** the employee list refreshes and the End Date column shows the new value
- **Given** I clear the end date field and save, **when** the save succeeds, **then** the employee's contract_end is set to NULL — they become open-ended again and, if previously in the Ended section, move to Active on next reload
- **Given** I save without changing the end date field, **when** other fields (grade, designation) are also changed, **then** all changes save correctly — the end date is not reset by the operation
- **Given** I save grade/designation only (the existing Edit flow, no set_contract_end in payload), **when** the PATCH is submitted, **then** the contract end date is not touched
- **Given** I enter an invalid date format, **when** the API responds, **then** a specific error message is shown naming the invalid value

### Out of Scope
- Editing contract start date (affects payroll history — separate story)
- Soft-deleting or deactivating employees
- Setting end date in bulk

### Business Risk
- **Cost of NOT doing**: Operators must manually run SQL or re-trigger onboarding to correct a termination date — a compliance risk if a terminated employee is inadvertently included in a payroll run.
- **Cost of doing it wrong**: If clearing the end date silently fails, an operator believes the employee is reinstated when they are not — excluded from the next run with no visible reason.

### Priority: P1 — Termination accuracy is a compliance obligation; including a terminated employee in payroll is a payroll error.

---

## Summary

| Story | Priority | Risk if wrong |
|---|---|---|
| EMP-01 Show dates in list | P2 | Audit gap — terminations missed |
| EMP-02 Add single employee | P2 | Employee invisible to payroll engine |
| EMP-03 Bulk Excel upload | P2 | Silent partial import, missed employees |
| EMP-04 Edit end date | P1 | Terminated employee included in payroll run |
