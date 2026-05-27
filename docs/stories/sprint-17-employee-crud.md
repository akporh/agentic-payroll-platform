# Sprint 17: Employee CRUD + Onboarding Decoupling (Track B)

**Arch-council status:** APPROVED WITH CONDITIONS (2026-05-27) — all 6 blocking issues resolved  
**Must ship with:** sprint-17-employee-ux.md  
**Depends on:** Nothing — no prior sprint dependency

---

## Scope Boundary

**IN scope:**
- B0a: Fix LATERAL join in `payroll_readiness_service.py` (BLK-3)
- B0b: Fix LATERAL join in `timesheet_derivation_service.py` (BLK-4)
- B1: New employee CRUD API (6 endpoints) + `employee_repo` — with run-lock and backdating guard
- B2: Replace inline employee SQL in `onboarding.py:451–598` with repo calls (BLK-5)
- B3: Enhance existing `Employees.tsx` — split edit actions, add ChangeContractSlideOver
- B4: Index-only migration on `employee_contract` (BLK-6 — end_date already exists)

**OUT of scope:**
- `payroll.py` temporal JOIN — already live (BLK-6), no change needed
- `emit_employees_sql()` preview emitter — untouched (preview-only path)
- Contract history UI (Sprint 20)
- Deactivation UI (Sprint 20)
- External ID field (Sprint 20)

---

## EMP-B0a · Fix readiness service — LATERAL join for multi-contract employees

**Priority:** P0 — Must land before any multi-contract employee can exist

**As a** payroll operator,  
**I want** the payroll readiness check to correctly evaluate employees who have a terminated contract and a future-dated new contract,  
**So that** I am not blocked from running payroll by a false "missing salary definition" warning.

### Context

`payroll_readiness_service.py:131–157` currently uses:
```sql
LEFT JOIN employee_contract ec ON ec.employee_id = e.employee_id
  AND (ec.end_date IS NULL OR ec.end_date >= CURRENT_DATE)
```
When Sprint 17 introduces multi-contract employees, an employee with an ended contract and a future-dated new contract returns **zero** rows from this JOIN — causing a false-positive readiness block.

### Acceptance Criteria

**Given** an employee whose old contract ended yesterday and whose new contract starts next month,  
**When** the readiness check runs,  
**Then** the employee is evaluated against their most recent contract (the future one) — no false-positive block is raised.

**Given** an employee with only one active contract,  
**When** the readiness check runs,  
**Then** behaviour is unchanged from today.

**After the fix**, the JOIN uses the LATERAL pattern from `workspace.py:208–215`:
```sql
LEFT JOIN LATERAL (
  SELECT ec2.*
  FROM employee_contract ec2
  WHERE ec2.employee_id = e.employee_id
  ORDER BY COALESCE(ec2.end_date, '9999-12-31') DESC, ec2.start_date DESC NULLS LAST
  LIMIT 1
) ec ON true
```

### Out of Scope
- Changing what the readiness check validates — same checks, correct contract

### Business Risk
- **Not fixed:** First grade change creates a second contract row. Readiness check immediately blocks every affected employee as "missing salary definition". Payroll cannot run until manually investigated.

### Open Questions
- None.

---

## EMP-B0b · Fix timesheet derivation — LATERAL join for multi-contract employees

**Priority:** P0 — Must land before any multi-contract employee can exist

**As a** payroll operator,  
**I want** timesheet uploads to derive attendance data against the correct contract for each employee,  
**So that** an employee with a contract history is not silently mapped to the wrong contract during derivation.

### Context

`timesheet_derivation_service.py:85–96` (`_get_employee_map`) uses:
```sql
LEFT JOIN employee_contract ec ON ...
  AND (ec.end_date IS NULL OR ec.end_date >= CURRENT_DATE)
```
With no `ORDER BY` and no `LIMIT`. Multi-contract employees produce duplicate rows. The dict comprehension at line 99 (keyed on `employee_number`) silently overwrites — which contract survives depends on query order, which is undefined.

### Acceptance Criteria

**Given** an employee with two contract rows (one ended, one current),  
**When** a timesheet is uploaded,  
**Then** derivation uses the current (most recent) contract — not the ended one, not a random one.

**Given** an employee with one contract row,  
**When** a timesheet is uploaded,  
**Then** behaviour is unchanged.

**After the fix**, `_get_employee_map` uses the same LATERAL pattern:
```sql
LEFT JOIN LATERAL (
  SELECT ec2.*
  FROM employee_contract ec2
  WHERE ec2.employee_id = e.employee_id
  ORDER BY COALESCE(ec2.end_date, '9999-12-31') DESC, ec2.start_date DESC NULLS LAST
  LIMIT 1
) ec ON true
```

### Out of Scope
- Changing timesheet derivation logic — same output shape, correct input contract

### Business Risk
- **Not fixed:** An employee's timesheet is derived against their old (lower) salary. Attendance-based proration uses wrong base rate. Silent financial error — no warning, no failure.

### Open Questions
- None.

---

## EMP-B1 · Employee CRUD backend

**Priority:** P1 — Enables all employee management and decoupling

**As a** workspace administrator,  
**I want** API endpoints to create, view, update, and manage contracts for individual employees,  
**So that** every employee change can be made without a bulk Excel upload.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/{wid}/employees` | List all employees with current contract |
| `POST` | `/{wid}/employees` | Create employee + initial contract in one transaction |
| `GET` | `/{wid}/employees/{eid}` | Single employee with full contract history |
| `PATCH` | `/{wid}/employees/{eid}` | Update employee fields (full_name, status, personal_details) |
| `POST` | `/{wid}/employees/{eid}/contracts` | Add new contract (closes current, opens new) |
| `PATCH` | `/{wid}/employee-contracts/{cid}` | Update contract (end_date, change_reason only) |

### Acceptance Criteria

**Create employee**

**Given** a valid payload with `employee_number`, `full_name`, `salary_definition_id`, `contract_start`,  
**When** `POST /{wid}/employees` is called,  
**Then** one `employee` row and one `employee_contract` row are created in the same transaction.

**Given** `employee_number` is missing from the payload,  
**Then** HTTP 422 is returned — no record created.

**Given** `salary_definition_id` belongs to a different workspace,  
**Then** HTTP 400: *"Salary definition not found in this workspace."*

**Given** `salary_definition.effective_from > contract_start` (NULL-safe: skip check if `effective_from` is NULL),  
**Then** HTTP 400: *"Salary definition not effective on contract start date."*

**Note:** The existing `POST /{wid}/employees` in `workspace.py:284` currently lacks this `effective_from` check. Apply the same NULL-safe validation there as part of this story.

**Add contract (append-only)**

**Given** `POST /{wid}/employees/{eid}/contracts` with `salary_definition_id`, `start_date`, `change_reason`,  
**When** called,  
**Then**:
- Current active contract `end_date` is set to `new_start_date - 1 day` (binding — not `new_start_date`)
- New contract row is created with `start_date = new_start_date`
- Both updates are in a single transaction

**D-ARCH-1 run-lock (BLK-2)**

**Given** a SUBMITTED or APPROVED run exists for the workspace,  
**When** `POST /{eid}/contracts` is called,  
**Then** HTTP 409 is returned: *"A payroll run is in progress. Contract changes are locked until the run is complete."*  
No contract rows are touched.

**Backdating guard**

**Given** `new_start_date <= current_contract.start_date`,  
**When** `POST /{eid}/contracts` is called,  
**Then** HTTP 422: *"New contract start date must be after the current contract start date."*

**Given** the employee has no active contract (already terminated),  
**When** `POST /{eid}/contracts` is called,  
**Then** HTTP 400: *"Employee has no active contract to close."*

**PATCH contract — restricted fields**

**Given** a payload attempting to change `salary_definition_id` via `PATCH /{wid}/employee-contracts/{cid}`,  
**Then** HTTP 422 — only `end_date` and `change_reason` are patchable.

**Workspace scoping**

All queries filter by `workspace_id` on the `employee` table. `employee_contract` is scoped through the employee FK.

### Out of Scope
- Bulk contract operations
- Hard-delete endpoints

### Business Risk
- **Not done:** Bulk upload remains the only change path. Every salary review, new joiner, or leaver requires a full Excel re-upload.
- **Run-lock missing:** Without BLK-2 guard, a grade change mid-run reads a new `salary_definition` against an already-started run — silent financial corruption.
- **Backdating missing:** A backdated start_date breaks the subquery sort in `workspace.py:482`, producing an unpredictable wrong-contract edit.

### Open Questions
- None.

---

## EMP-B2 · Unify employee creation in onboarding commit path

**Priority:** P1 — Architecture correctness (closes dual-path employee creation)

**As a** system architect,  
**I want** the onboarding commit path to create employees via `employee_repo` rather than inline SQL,  
**So that** all employee creation goes through one code path regardless of how it was triggered.

### Context (BLK-5 correction)

`emit_employees_sql()` in `backend/domain/onboarding/sql_emitter.py` generates **SQL text strings for the `/preview` endpoint display only** — it does not execute at commit time. Do not change it.

The actual commit path is **inline `db.execute()` calls at `onboarding.py:451–598`** — these are the blocks to replace.

### Acceptance Criteria

**Given** a valid onboarding payload with employee rows,  
**When** `POST /onboarding/commit` is called,  
**Then** each employee is created via `employee_repo.insert_employee()` + `employee_repo.insert_employee_contract()`, not inline SQL.

**Given** the commit is called with one invalid employee (missing `employee_number`),  
**When** processed,  
**Then** the entire transaction rolls back — no partial state. HTTP 422 returned.

**Given** the commit is called with an employee whose `employee_number` already exists in the workspace,  
**When** processed,  
**Then** HTTP 409 with a clear message — not a raw DB constraint error.

**Given** the `/preview` endpoint is called,  
**Then** `emit_employees_sql()` still runs unchanged — preview output is unaffected.

**Given** the workspace setup data (grades, designations, salary definitions, payroll rules),  
**Then** these are still handled by their existing onboarding paths — only the employee INSERT blocks change.

**After the change**, the inline `db.execute()` blocks at `onboarding.py:451–598` that INSERT into `employee` and `employee_contract` are replaced with repo calls. The blocks are not present in the function in any form.

### Out of Scope
- Changing the onboarding payload format
- Changing the onboarding validation layer

### Business Risk
- **Not done:** Two independent code paths create employees. A future constraint change (e.g. Sprint 18 `employee_number NOT NULL`) applied to the repo is silently bypassed by the onboarding SQL path — different data quality per creation route.

### Open Questions
- None.

---

## EMP-B3 · Employee management UI — enhance existing Employees.tsx

**Priority:** P1 — Operator self-service for employee lifecycle

**As a** workspace administrator,  
**I want** to add, edit, and change the grade/salary of individual employees from the UI,  
**So that** I am not dependent on the bulk onboarding upload for routine employee changes.

### Context

`frontend/src/pages/Employees.tsx` already exists with `AddEmployeeSlideOver` and `EditSlideOver`. This story enhances it — it does not create from scratch. The existing `EditSlideOver` conflates grade, designation, and contract end date in one form. After Sprint 17, grade changes are contract changes (append-only). The slide-over must be split.

### Acceptance Criteria

**Add Employee (existing, verify unchanged)**

**Given** the operator clicks "Add Employee",  
**When** the SlideOver opens,  
**Then** `employee_number`, `full_name`, `salary_definition_id`, `contract_start` are present and required.  
**And** on save, the employee appears in the active section.

**Edit Details (refined scope)**

**Given** the operator clicks "Edit" on a row,  
**When** the SlideOver opens,  
**Then** it contains only: `full_name`, `status` (ACTIVE/INACTIVE).  
**And** it does NOT contain grade, designation, or contract end date.  
**And** it saves via `PATCH /{wid}/employees/{eid}` — no contract row is touched.

**Change Grade / Salary (new)**

**Given** the operator clicks "Change Grade / Salary" on a row,  
**When** the `ChangeContractSlideOver` opens,  
**Then** it contains: new `salary_definition_id` (dropdown), `start_date` (required), `change_reason` (required).  
**And** an info note reads: *"This will close the current contract and open a new one from the selected date."*  
**And** on save: old contract `end_date` = `start_date - 1 day`; new contract created.

**Given** the workspace has an active run (SUBMITTED or APPROVED),  
**When** the operator attempts to save a contract change,  
**Then** the SlideOver shows an error: *"A payroll run is in progress. Contract changes are locked."*  
**And** no change is saved.

**View Contracts (placeholder)**

**Given** the table actions column,  
**When** rendered,  
**Then** a "View Contracts" action is present on every active row.  
In Sprint 17 it opens a read-only panel listing: current contract salary definition, start date, status (Current).  
Full contract history (multiple rows) is Sprint 20.

**API client — `frontend/src/api/employees.ts`**

New file with: `listEmployees`, `createEmployee`, `updateEmployee`, `addContract`.

### Out of Scope
- Deactivation UI (Sprint 20 EMP-P3-2 / EMP-UX-2)
- Contract history showing multiple past rows (Sprint 20 EMP-P3-1)
- Bulk employee operations

### Business Risk
- **Not done:** Salary reviews require re-uploading a full Excel. No operator self-service for routine changes.

### Open Questions
- None.

---

## EMP-B4 · Migration — employee_contract temporal index

**Priority:** P2 — Performance (correctness unaffected; needed before contract history grows)

**As a** system engineer,  
**I want** an index on `employee_contract(employee_id, start_date)`,  
**So that** the LATERAL joins introduced in B0a and B0b perform efficiently as contract history accumulates.

### Context (BLK-6 correction)

`end_date` already exists on `employee_contract` from migration `7685c65f5d2`. Do NOT add it again. This migration is **index-only**.

### Acceptance Criteria

**Given** the migration is applied,  
**When** the schema is inspected,  
**Then** index `idx_employee_contract_employee_date` exists on `(employee_id, start_date)`.

**Given** the migration runs on a DB where the index already exists,  
**Then** `CREATE INDEX IF NOT EXISTS` completes without error.

**Given** `alembic downgrade -1`,  
**Then** `DROP INDEX IF EXISTS idx_employee_contract_employee_date` runs cleanly. No column is dropped.

The migration description must state: *"end_date pre-exists from migration 7685c65f5d2; this migration adds a performance index on (employee_id, start_date) to support LATERAL temporal JOIN queries introduced in Sprint 17."*

### Out of Scope
- Composite index including `end_date`
- Any column additions

### Business Risk
- Low immediate risk — no production data. Matters when contract history reaches hundreds of rows.

### Open Questions
- None.
