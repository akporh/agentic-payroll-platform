# Sprint 23: Employee Upload — Full Decoupling

**Status:** IN PROGRESS — 2026-06-09
**Arch-council:** Approved — binding decisions D-ARCH-1 through D-ARCH-6
**Stories:** EMP-REG-3, EMP-REG-4, EMP-REG-5

---

## Background

Sprint 22 fixed the hard failure (grade_code null always). But the upload flow is still coupled:
- `EmployeeUpload` still loads salary definitions from the workspace
- It still auto-matches grades to salary defs and shows a "Resolve Salary Mappings" panel
- Designation resolution runs inline during upload
- The operator sees amber warnings unless all mappings are resolved — implying workspace config must be done before upload

This sprint removes all of that. Upload = register employees as HR records. Enroll = assign salary structure. These are two separate, independent actions.

**Enrolled definition (unchanged — D-ARCH-2):** `salary_definition_id IS NOT NULL`. Not changing this sprint.

---

## EMP-REG-3 · Upload stores imported labels; creates not-enrolled employees only

**Priority:** P1 — upload flow still feels broken; operators are confused by the coupled UX

**As a** bureau payroll administrator,
**I want** to upload an employee file and have all employees registered immediately regardless of workspace configuration,
**So that** I can register employees today without waiting for payroll structures to be set up, and without seeing resolution warnings.

### Problem Context

Even after Sprint 22, the EmployeeUpload component:
1. Requires salary definitions to be loaded before it renders
2. Auto-matches the Excel grade column to salary definition codes (using a mapping panel)
3. Shows amber "unresolved" warnings for employees whose grade didn't match any salary def
4. Resolves designations inline and blocks import if any designation is "unresolved"

The admin cannot import employees without engaging with the mapping panel — even though the actual API call no longer needs a salary def or grade. The UI is the remaining source of coupling.

### Acceptance Criteria

**Upload works with no workspace config at all**

Given a workspace with zero salary definitions, zero grades, zero designations,
When I upload an Excel file with 50 employees,
Then all 50 employees are created with `salary_definition_id = null`, `grade_id = null`, `designation_id = null`,
And zero errors are returned.
And the import button reads "Register N employees" (not "Import").

**Imported grade and designation labels are stored**

Given an Excel file with `grade = "STEP_1B"` and `designation = "Manager"`,
When the employee is created,
Then `employee_contract.imported_grade_label = "STEP_1B"` and `imported_designation_label = "Manager"` are persisted,
And these values are returned in the `GET /employees` response.

**No mapping panel shown**

Given any workspace state (configured or not),
When I open the Upload SlideOver and load a file,
Then no "Resolve Salary Mappings" panel appears,
And no "Resolve Designations" panel appears,
And no amber warning states appear.

**Upload payload — explicit field constraint (decoupling invariant)**

The upload API call (`createEmployee`) must always send:
| Field | Value | Reason |
|-------|-------|--------|
| `salary_definition_code` | `null` | Payroll setup — Enroll flow only |
| `grade_code` | `null` | Payroll setup — Enroll flow only |
| `designation_code` | `null` | Payroll setup — Enroll flow only |
| `imported_grade_label` | raw Excel value or null | Preserved for reference during enroll |
| `imported_designation_label` | raw Excel value or null | Preserved for reference during enroll |

**Results display has three outcomes only**

Given an upload of 10 employees where 7 are new and 3 already exist,
When the import completes,
Then the results show: 7 green "Registered", 3 blue "Already exists", 0 red.
And there is no "not enrolled" amber category.

**All four `employee_contract` INSERT sites updated (D-ARCH-5)**

Given any code path that creates an `employee_contract` row:
- `workspace.py` `create_employee` inline INSERT
- `employee_repo.py` `insert_employee_contract` function
- `load_employee_contracts.py` script
- Test fixtures
All must include `imported_grade_label` and `imported_designation_label` columns (passing `None` where no label data exists).

### Out of Scope
- Storing any other Excel columns not already captured
- Validating imported labels against workspace config (they are free text — stored as-is)
- Changing the `is_enrolled` definition (D-ARCH-2 — do not touch this sprint)
- Designation validation or resolution in the upload flow

### Business Risk
- **Cost of NOT doing this:** Upload UX is still confusing. Operators must engage with a mapping panel that serves no function post-Sprint 22. Trust in the platform erodes.
- **Cost of doing it wrong:** If `salary_definition_code` is accidentally sent non-null, employees are enrolled during upload — breaking the enrollment model entirely.

---

## EMP-REG-4 · Employee list shows imported grade/designation as reference columns

**Priority:** P2 — without this, the operator has no visibility of imported labels when deciding how to enroll

**As a** bureau payroll administrator,
**I want** to see the imported grade and designation labels in the Not Enrolled employee table,
**So that** I know what salary structure each employee should be assigned to when I enroll them.

### Acceptance Criteria

**Not Enrolled table shows imported labels**

Given a not-enrolled employee with `imported_grade_label = "STEP_1B"`,
When the Not Enrolled section is displayed,
Then the Grade column shows `"STEP_1B"` with a subtle `(imported)` badge,
And the Designation column shows the `imported_designation_label` the same way.

**Enrolled employees show resolved code (not imported label)**

Given an enrolled employee with `grade_code = "STEP_1"`,
When the employee row is displayed,
Then the Grade column shows `"STEP_1"` (the resolved code) without any badge.

**No imported label → dash**

Given a not-enrolled employee with `imported_grade_label = null`,
When the row is displayed,
Then the Grade column shows "—".

**Imported label is read-only display only**

The `(imported)` badge is informational — it is not a link, not editable, and not actionable from the table row. Action is taken via the Enroll button or the auto-suggest banner.

### Out of Scope
- Separate "Imported Grade" and "Grade" columns (one column that degrades gracefully is cleaner)
- Editing the imported label
- Filtering or sorting by imported label

---

## EMP-REG-5 · Auto-suggest enrollment by grade group

**Priority:** P2 — significantly reduces the manual effort of enrolling 180 employees after upload

**As a** bureau payroll administrator,
**I want** the system to group my not-enrolled employees by their imported grade label and suggest matching salary structures,
**So that** I can enroll an entire grade group in one click instead of selecting employees one by one.

### Acceptance Criteria

**Banner appears when grade matches exist**

Given 86 not-enrolled employees with `imported_grade_label = "STEP_1"`,
And a salary definition with `code = "STEP_1"` exists in the workspace,
When the Not Enrolled section loads,
Then a suggestion banner appears above the table: `"STEP_1 — 86 employees → STEP_1 [Enroll]"`.

**Banner row with no match shows "Select" instead of "Enroll"**

Given 12 not-enrolled employees with `imported_grade_label = "STEP_1B"`,
And no salary definition with `code = "STEP_1B"` exists,
Then the banner row shows: `"STEP_1B — 12 employees → no match [Select]"`.

**Case-insensitive matching (D-ARCH-6)**

Given `imported_grade_label = "step_1"` and salary def code `"STEP_1"`,
Then the match is found (UPPER() normalisation on both sides).

**"Enroll" button pre-fills BulkEnrollSlideOver**

Given I click "Enroll" on the `STEP_1` banner row,
Then BulkEnrollSlideOver opens with:
- The 86 STEP_1 employees pre-selected
- `salary_definition_code` pre-filled with `"STEP_1"`

**"Select" button opens BulkEnrollSlideOver without pre-fill**

Given I click "Select" on the `STEP_1B` banner row (no match),
Then BulkEnrollSlideOver opens with the 12 STEP_1B employees pre-selected,
And `salary_definition_code` is empty (operator must choose).

**Banner is hidden when all not-enrolled employees have no imported label**

Given all not-enrolled employees have `imported_grade_label = null`,
Then no banner is shown.

**Banner is hidden when there are no not-enrolled employees**

Given all employees are enrolled,
Then no banner is shown.

### Matching Logic

```
suggestedGroups = notEnrolledEmployees
  .filter(e => e.imported_grade_label)
  .groupBy(e => e.imported_grade_label.toUpperCase())
  .map(group => ({
    label: group.key,
    count: group.employees.length,
    employeeIds: group.employees.map(e => e.employee_id),
    matchedSalaryDef: salaryDefinitions.find(
      sd => sd.code.toUpperCase() === group.key
    ) || null
  }))
  .sortBy(g => -g.count)   // largest group first
```

### Out of Scope
- Fuzzy/prefix matching (STEP_1B → STEP_1) — deferred. Wrong match in payroll is worse than no match.
- Auto-enrolling without user confirmation
- Suggesting grade or designation assignments

### Business Risk
- **Cost of NOT doing this:** Operator must manually select and enroll every grade group. For 180 employees across 5 grade groups, this is 5 separate BulkEnroll operations — all manual.
- **Cost of doing it wrong:** Banner suggests wrong salary def → operator clicks Enroll → all employees in that group get wrong structure → payroll calculations are wrong.
