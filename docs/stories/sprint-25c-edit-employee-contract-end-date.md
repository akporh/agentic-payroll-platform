# Story: Edit Employee — Contract End Date Field
**Written in retrospective — 2026-06-09**
**Sprint 25c — implemented same session, no sprint planning precursor**

---

## Story — Operator can set a contract end date from the Edit Employee SlideOver

**As a** payroll bureau operator,
**I want** to be able to set or update a contract end date directly from the Edit Employee
SlideOver,
**So that** I can record when an employee's contract ends without needing a dedicated
employee staging UI that doesn't yet exist.

### Acceptance Criteria

**Happy path — enrolled employee:**
- **Given** an employee is enrolled (has a contract assigned), **when** I open Edit Employee,
  **then** I see a "Contract End Date" date input pre-populated with the existing end date
  (or blank if open-ended).
- **Given** I set or change the end date and click Save, **then** the contract is updated
  via `PATCH /workspaces/{id}/employee-contracts/{contract_id}` and a success toast is shown.
- **Given** I leave the end date unchanged, **then** no contract patch request is made.

**Unenrolled employee — field disabled:**
- **Given** an employee has no contract assigned (not yet enrolled), **when** I open Edit
  Employee, **then** the Contract End Date field is disabled with the hint
  "No contract assigned — enroll this employee first".

**Invariant — inclusive last paid day:**
- The hint text reads "Inclusive last paid day. Leave unchanged to keep the current date."
  — reinforcing the domain rule that `end_date` is the last day payroll runs for this
  employee, not the final physical working day.

### Out of Scope
- Setting or editing contract start date from the Edit form (start date is immutable
  post-enrollment; editable only at registration time)
- Clearing an existing end date back to NULL (not supported by `update_employee_contract`
  which skips None values — deferred)

### Implementation Summary

**Root cause for disabled field on enrolled employee:** `workspace.py::list_employees` uses
its own inline SQL query (separate from `employee_repo.py::get_employees_with_contracts`)
that never projected `ec.contract_id`. The frontend always received `undefined` for
`contract_id`, so the field was always disabled.

**Fix — backend:** `backend/api/routes/workspace.py` `list_employees` inline SQL — added
`ec.contract_id` to the SELECT clause and `"contract_id": str(row[15]) if row[15] else None`
to the response dict (row index 15, after `imported_designation_label`).

**Fix — frontend:**
- `frontend/src/types/payroll.ts` — added `contract_id?: string` to `Employee` interface.
- `frontend/src/api/employees.ts` — added `patchContract(workspaceId, contractId, payload)`
  method calling `PATCH /{workspaceId}/employee-contracts/{contractId}`.
- `frontend/src/pages/Employees.tsx` `EditSlideOver` — added `contractEnd` state,
  pre-populated from `employee.contract_end`; on save, calls `patchContract` only when the
  value differs from the original and `contract_id` is present.

### Business Risk / Impact
- **Cost of not doing:** No UI path to record a termination date short of going to the
  Contracts sub-page (4 clicks away). Operators were leaving `end_date` blank, causing
  terminated employees to remain eligible for payroll runs.
- **Cost of doing it wrong:** Incorrect end date could prorate pay incorrectly for the
  final period. Risk is operator-visible — they set the date explicitly.

### Priority
**P1** — operator cannot correctly model employee terminations without this field.
