# Sprint 22: Employee Upload Decoupling + Bulk Enroll

**Status:** CLOSED — 2026-06-08
**Arch-council:** Not required (no data contract changes — additive only)
**Stories:** EMP-BULK-1, EMP-BULK-2, EMP-BULK-3

---

## EMP-BULK-1 · Upload employees without grade or salary definition

**Priority:** P0 — upload path was broken; 180-employee imports failed with 400 errors in UAT

**As a** bureau payroll administrator,
**I want** to upload employees from an Excel file without needing salary structures or grades to be configured,
**So that** I can register employees in the system today and assign them to payroll structures separately.

### Problem Context

`handleImport` was forwarding the raw Excel grade column (`e.g. STEP_1B`) to `create_employee` as `grade_code`. The API validated this against the workspace grade table — if the grade didn't exist, the upload failed with `400 "Grade 'STEP_1B' not found"`. This caused 180 upload failures in UAT.

The root cause was coupling: upload and payroll enrollment were treated as one action. The fix requires true decoupling — grade is a payroll setup field, not an HR registration field.

### Acceptance Criteria

**Happy path — upload to workspace with no grades configured**

Given a workspace with no grade entries,
When I upload an Excel file with 180 employees (including grade values in the Grade column),
Then all 180 employees are created successfully with `grade_code: null` and `salary_definition_code: null`,
And zero 400 errors are returned.

**Grade column is ignored during upload**

Given an Excel file with `grade = "STEP_1B"`,
When the file is processed by `handleImport`,
Then `grade_code: null` is sent to the API — the raw Excel grade is never forwarded,
And the employee is created without a grade assignment.

**Backward-compatible — upload with salary def still works**

Given an employee row where the Excel grade matches an existing salary definition code,
When the upload is processed,
Then `salary_definition_code: null` is still sent — salary def assignment is deferred to the Enroll flow.

**Pre-existing smart-filter approach rejected**

The fix must NOT be "only send grade_code if it exists in the workspace." That approach still couples the upload component to workspace configuration. `grade_code: null` always, full stop.

### Out of Scope
- Storing the imported grade label as text (Sprint 23)
- Fuzzy/prefix matching for grade→salary def mapping (deferred indefinitely — wrong match in payroll is worse than no match)
- Removing the mapping resolution panel from EmployeeUpload (Sprint 23)

### Decoupling Constraints — Fields Withheld from `createEmployee` During Upload
| Field | Value sent | Reason |
|-------|-----------|--------|
| `grade_code` | `null` always | Grade is a payroll setup field — assigned via Enroll only |
| `salary_definition_code` | `null` always | Salary structure is assigned via Enroll only |
| `designation_code` | `null` if unresolved | Designation is HR data — sent only if resolved from workspace designations |

### Business Risk
- **Cost of NOT doing this:** All bulk employee imports fail. Client onboarding is blocked. UAT cannot proceed.
- **Cost of doing it wrong:** Re-uploading the same file could create duplicates or silent data corruption.
- **Who is blocked:** All new client workspaces — Sandy UAT was fully blocked.

---

## EMP-BULK-2 · Bulk enroll employees to a salary structure

**Priority:** P1 — without bulk enroll, operators must enroll 180 employees one by one

**As a** bureau payroll administrator,
**I want** to select multiple not-enrolled employees and assign them all to a salary definition in one action,
**So that** I can move employees from registered to payroll-ready without doing it individually.

### Acceptance Criteria

**Happy path — bulk enroll multiple employees**

Given a workspace with 10 not-enrolled employees and a salary definition `STEP_1`,
When I select all 10 employees and submit bulk enroll with `salary_definition_code: STEP_1`,
Then all 10 employees have `salary_definition_id` set on their open contract,
And the response returns `{enrolled: 10, skipped: 0, failed: 0}`.

**Idempotent — already-enrolled employees are skipped**

Given 5 employees already enrolled and 5 not enrolled,
When I send a bulk enroll request with all 10 IDs,
Then the response returns `{enrolled: 5, skipped: 5, failed: 0}`,
And no error is raised.

**Workspace guard fires for cross-workspace employee IDs**

Given employee IDs from workspace B sent to workspace A's bulk-enroll endpoint,
When the request is processed,
Then those IDs are returned as `failed` with reason `"not found"`,
And workspace A's data is not modified.

**Optional grade and designation**

Given a bulk-enroll request with `grade_code` and `designation_code` provided,
When the enroll is processed,
Then `grade_id` and `designation_id` are also set on each enrolled employee's contract.

**Invalid salary definition code → 400**

Given `salary_definition_code: "NONEXISTENT"`,
When the bulk-enroll is submitted,
Then a 400 is returned with a human-readable error — not an internal DB error string.

**Empty employee_ids → 422**

Given `employee_ids: []`,
When the bulk-enroll is submitted,
Then a 422 Unprocessable Entity is returned.

### API Contract
- `POST /workspaces/{workspace_id}/employees/bulk-enroll`
- Request: `{ employee_ids: string[], salary_definition_code: string, grade_code?: string, designation_code?: string }`
- Response: `{ enrolled: int, skipped: int, failed: int, details: [{employee_id, status, reason?}] }`

### Out of Scope
- Bulk unenroll
- Bulk change salary structure (separate flow)
- UUID format validation on `employee_ids` items (deferred — low severity, no SQL injection risk)

### Business Risk
- **Cost of NOT doing this:** One-by-one enrollment for 180 employees. UAT blocked on time grounds.
- **Cost of doing it wrong:** Wrong employees enrolled to wrong salary structure → incorrect payroll calculations.

---

## EMP-BULK-3 · Re-uploading the same file returns "already exists" not "failed"

**Priority:** P2 — UX friction; operators re-upload files frequently when correcting errors

**As a** bureau payroll administrator,
**I want** re-uploading a file with existing employees to show them as "already registered" (not as errors),
**So that** I can safely re-run an upload without worrying that duplicate attempts are silently causing failures.

### Acceptance Criteria

**Re-upload same employee_number → skipped (not failed)**

Given employee `EMP001` already exists in the workspace,
When I upload a file containing `EMP001` again,
Then the row result shows status `'skipped'` (blue/neutral in UI) — not `'failed'` (red),
And the response message is `"already exists"`.

**Fresh employees in the same re-upload file are still created**

Given a file with 10 employees where 8 already exist and 2 are new,
When the file is uploaded,
Then 2 are created, 8 are skipped, and 0 are failed.

### Out of Scope
- Updating existing employee data on re-upload (update is a separate Edit action)

### Business Risk
- **Cost of NOT doing this:** Operators see red "failed" rows for employees that are perfectly fine — creates false alarm, erodes trust in the UI.
