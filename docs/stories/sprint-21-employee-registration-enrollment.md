# Sprint 21: Employee Registration vs Payroll Enrollment

**Arch-council:** Approved with conditions (Senior Architect + Principal Engineer — June 2026)
**Binding decisions:** D-ENROLL-1 through D-ENROLL-5 (see plan file)

---

## EMP-REG-1 · Register an employee without a salary definition

**Priority:** P1 — blocks onboarding new clients whose salary structures are not yet finalised

**As a** bureau payroll administrator,
**I want** to upload and register employees before salary definitions are configured,
**So that** HR data entry and payroll structure setup can happen independently and in any order.

### Acceptance Criteria

**Happy path — single employee create (no salary def)**

Given a workspace with no salary definitions,
When I POST `/workspaces/{id}/employees` with `salary_definition_code` omitted,
Then a 200 is returned, the employee row is created, and the employee_contract row is created with `salary_definition_id = NULL`.

**Happy path — single employee create (with salary def, backward compatible)**

Given a workspace with salary definitions,
When I POST `/workspaces/{id}/employees` with a valid `salary_definition_code`,
Then the employee is created with `salary_definition_id` set — identical to current behaviour.

**Employee appears in "Not Enrolled" section**

Given an employee with `salary_definition_code = null`,
When the Employees page loads,
Then that employee appears in a "Not Enrolled" section above the Unmatched section, with a rose left border (`border-l-4 border-rose-400`), and a "— Not assigned —" value in the Salary Def column.

**Page-level alert**

Given at least one unenrolled employee exists,
When the Employees page loads,
Then an `AlertBanner variant="warning"` appears at the top of the page stating how many employees are not enrolled, with a scroll-to link to the Not Enrolled section.

**API error handling**

Given `salary_definition_code` is provided but does not match any workspace salary definition,
When I POST `/workspaces/{id}/employees`,
Then a 400 is returned with `"Salary definition '{code}' not found"` — same as today.

**Schema validation**

Given `salary_definition_code` is provided as an empty string,
When I POST `/workspaces/{id}/employees`,
Then it is treated as absent (no salary def lookup attempted) and the employee is created unenrolled.

### Out of Scope
- Bulk onboarding via `/onboarding/commit` — that path continues to require a salary definition for every employee (D-ENROLL-2)
- Importing unenrolled employees via the EmployeeUpload Excel component — that UI remains for enrolled employees only for now

### Business Risk
- **Not done:** New clients with large rosters cannot be partially onboarded — all salary structures must exist before any employees can be entered. This blocks go-live for clients whose HR data arrives before their salary bands are approved.
- **Done wrong (missing null guard):** `str(row[1])` in `employee_repo.py:141` without a null guard produces the string `"None"` and causes UUID cast failures in downstream callers. Fix must land before the migration is applied (AC-1).

### Open Questions
None — all decisions resolved in arch-council.

---

## EMP-REG-2 · Enroll an employee in payroll (salary mapping)

**Priority:** P1 — unenrolled employees are payroll-invisible; this is the action that makes them run-eligible

**As a** bureau payroll administrator,
**I want** to assign a salary definition to a registered employee,
**So that** they are included in the next payroll run.

### Acceptance Criteria

**Happy path — enroll via SlideOver**

Given an employee in the Not Enrolled section,
When I click "Enroll" and the `EnrollSlideOver` opens,
Then I see:
- Salary Definition (required, SearchableSelect populated from workspace salary defs)
- Contract Start Date (required, DateInput, defaulting to the employee's existing contract start_date)
- Grade (optional, SearchableSelect)
- Designation (optional, SearchableSelect)

When I select a valid salary definition and click "Enroll Employee",
Then:
- The employee's existing contract row is UPDATEd in place with `salary_definition_id`, `grade_id`, `designation_id` set (D-ENROLL-1: not a new contract row)
- A success toast appears: `"{Full Name} enrolled — payroll eligible"`
- The employee moves from the Not Enrolled section to the Active section on reload

**Workspace not configured (blocked state)**

Given a workspace with no salary definitions,
When the Employees page loads and unenrolled employees exist,
Then a page-level `AlertBanner variant="warning"` is shown with the text "Salary definitions must be set up before employees can be enrolled" and a link to the Configuration page.

Given the blocked state,
When I hover over the "Enroll" button on a not-enrolled row,
Then the button is `disabled` with `title="Configure salary definitions first"`.

**API — enroll endpoint**

Given an employee with an active unenrolled contract,
When I POST `/workspaces/{id}/employees/{employee_id}/enroll` with:
```json
{
  "salary_definition_code": "GL4-BASIC",
  "contract_start": "2024-01-01",
  "grade_code": "GL4",
  "designation_code": "MANAGER"
}
```
Then the active contract row is updated with the resolved `salary_definition_id`, `grade_id`, `designation_id` and a 200 is returned with the updated employee record.

**Already enrolled employee**

Given an employee with `salary_definition_id` already set,
When I POST `/workspaces/{id}/employees/{employee_id}/enroll`,
Then a 400 is returned with `"Employee is already enrolled in payroll"`.

**Invalid salary definition code**

Given `salary_definition_code` does not exist in the workspace,
When I POST `/workspaces/{id}/employees/{employee_id}/enroll`,
Then a 400 is returned with `"Salary definition '{code}' not found"`.

**No active unenrolled contract**

Given an employee with no contract or with a fully enrolled contract,
When I POST `/workspaces/{id}/employees/{employee_id}/enroll`,
Then a 404 is returned with `"No unenrolled contract found for this employee"`.

**Payroll run exclusion**

Given an unenrolled employee (salary_definition_id IS NULL) in an active workspace,
When a payroll run is initiated,
Then the unenrolled employee does not appear in the run (excluded automatically by INNER JOIN on salary_definition — no code change needed, existing behaviour).

**Downgrade safety**

Given the migration has been applied and unenrolled employees exist,
When `alembic downgrade -1` is run,
Then it fails with: `"Cannot restore NOT NULL: unenrolled employee_contract rows exist. Enroll all employees before downgrading."` — and the database is unchanged.

Given no unenrolled employees exist,
When `alembic downgrade -1` is run,
Then `salary_definition_id` reverts to `NOT NULL` successfully.

### Out of Scope
- Enrolling via bulk re-upload (future scope)
- Unenrolling an employee (removing their salary definition) — not in scope; use "Change Grade / Salary" for salary changes
- Enrolling multiple employees at once via bulk selection UI

### Business Risk
- **Not done:** Registered employees can never run in payroll — the bureau is permanently blocked from processing a client until every employee is enrolled one-by-one through the existing (inflexible) create path.
- **Done wrong (enrollment = new contract row):** Creates spurious contract history implying an employment event change that did not happen; breaks audit trail (D-ENROLL-1 binding decision: UPDATE in place).

### Open Questions
None — all resolved in arch-council.

---

## EMP-NAV-1 · Employees first in left navigation

**Priority:** P3 — usability improvement, no functional impact

**As a** bureau payroll administrator,
**I want** the Employees section to appear at the top of the workspace navigation,
**So that** the most common starting point (checking and managing people) is immediately visible without scrolling past payroll items.

### Acceptance Criteria

Given any workspace page,
When the left navigation renders,
Then the section order is:
1. People (Employees)
2. Payroll (Inputs, Runs)
3. Configuration (Configuration, Public Holidays, Rate Codes, Attendance Codes)
4. Setup Wizard

The unmatched employee count badge continues to appear on the Employees nav item.

### Out of Scope
- Renaming nav section labels
- Adding new nav items

### Business Risk
Low. Pure presentational reorder. No functional dependency.

---

## Implementation Order

| Step | Story | Backend / Frontend |
|------|-------|--------------------|
| 1 | EMP-REG-1 | Migration + `employee_repo.py` null guard (AC-1) + Optional salary_def_code |
| 2 | EMP-REG-1 | `workspace.py` create_employee update + `str(e)` fix (AC-2) |
| 3 | EMP-REG-2 | New `enroll_employee_contract` repo function |
| 4 | EMP-REG-2 | New `POST /employees/{id}/enroll` endpoint |
| 5 | EMP-REG-1 | Frontend: Not Enrolled section on Employees page |
| 6 | EMP-REG-2 | Frontend: EnrollSlideOver + enrollEmployee API call |
| 7 | EMP-NAV-1 | Navigation reorder |

Steps 1–4 are backend-only and can be verified independently via curl before frontend work begins.
