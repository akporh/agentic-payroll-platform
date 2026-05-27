# Sprint: Employee Refactor — Phase 1 (Payroll Integrity Hardening)

**Delivery increment:** Track A (code fixes) + Track B (schema constraints)  
**Depends on:** commit 010f51f (FULL_RUN disabled, CURRENT_DATE fixed — already applied)  
**Blocks:** Phase 2 (snapshot engine cannot be safely wired until Phase 1 constraints are live)

---

## Scope Boundary

**IN scope:**
- Fix total_tax misassignment in retry path
- Remove dead FULL_RUN code and enum value
- Remove statutory live-read fallback
- Add NULL period-date guard
- Harden onboarding loader against missing employee_number
- Enforce no-overlap contract constraint at DB level
- Enforce employee_number NOT NULL + unique index
- Add public_holidays_snapshot column on payroll_run

**OUT of scope:**
- Snapshot tables (Phase 2)
- Retry-reads-from-snapshot wiring (Phase 2)
- Onboarding UI changes
- Any new employee management endpoints

---

## EMP-P1-1 · Fix PAYE total_tax in retry

**Priority:** P1 — Financial compliance obligation

**As a** payroll compliance officer,  
**I want** the `total_tax` field on a payroll run to reflect PAYE withholding only,  
**So that** statutory reporting (PAYE remittance, tax filings) is based on correct figures and not inflated by non-tax deductions.

### Acceptance Criteria

**Given** a completed payroll run where employees have both PAYE and non-PAYE deductions (e.g. Pension, NHF),  
**When** a PER_EMPLOYEE retry is triggered and completes successfully,  
**Then**:
- `payroll_run.total_tax` equals the sum of `deductions_jsonb->>'PAYE'` across all result rows
- `payroll_run.total_deduction` equals the sum of ALL deductions (PAYE + Pension + NHF + etc.)
- `total_tax` ≤ `total_deduction` always
- `total_tax` matches the value produced by the original run (which was already correct)

**Given** an employee with zero PAYE (below tax threshold),  
**When** retry runs,  
**Then** `total_tax` contribution for that employee is 0 (not null, not error).

**Given** the retry service code,  
**When** inspected,  
**Then** `total_tax` and `total_deduction` are bound to distinct query columns (no shared binding).

### Out of Scope
- Changing how PAYE is calculated (calculation logic unchanged)
- Fixing total_tax in the original run path (already correct)

### Business Risk
- **Not fixed:** Statutory PAYE remittance figures from retry runs are overstated — includes pension, NHF, levy. Could trigger regulatory audit.
- **Done wrong:** Under-reported PAYE (opposite direction) — equally a compliance failure.

### Open Questions
- None. 'PAYE' is the confirmed canonical key in `deductions_jsonb`.

---

## EMP-P1-2 · Remove FULL_RUN retry — dead code and enum

**Priority:** P1 — Financial data integrity

**As a** payroll system operator,  
**I want** FULL_RUN retry mode to be completely removed from the codebase and database,  
**So that** it is impossible to accidentally trigger a mode that deletes SUCCESS payroll rows and re-runs against live salary data.

### Acceptance Criteria

**Given** the retry service,  
**When** `_retry_full_run` is called (shouldn't be possible after this story),  
**Then** a `ValueError` is raised immediately with message containing "FULL_RUN retry is disabled".

**Given** the `payroll_run` table,  
**When** a row with `retry_strategy = 'FULL_RUN'` is inserted,  
**Then** the DB CHECK constraint rejects it with a constraint violation.

**Given** the codebase,  
**When** `_retry_full_run` is inspected after this change,  
**Then** the function body contains only the `raise ValueError` gate and its docstring — all SQL and logic is deleted.

**Given** the migration applied to a clean DB,  
**When** `alembic downgrade -1` is run,  
**Then** the constraint reverts to allow both `'FULL_RUN'` and `'PER_EMPLOYEE'` without data loss.

### Out of Scope
- Changing PER_EMPLOYEE retry behaviour
- Exposing retry strategy selection in the UI

### Business Risk
- **Not done:** A developer or operator could theoretically trigger FULL_RUN, which deletes SUCCESS rows — financial restatement without an audit trail.
- **Done wrong:** Accidental deletion of existing `PER_EMPLOYEE` constraint if migration is malformed.

### Open Questions
- None.

---

## EMP-P1-3 · Remove statutory live-read fallback + add period-date guard

**Priority:** P1 — Determinism / audit obligation

**As a** payroll auditor,  
**I want** retry runs to always resolve statutory rules using the date stored on the original run,  
**So that** a retry never silently applies a different tax band version than the original calculation.

**As a** payroll system operator,  
**I want** retry to fail fast with a clear error if the run has no period dates,  
**So that** corrupt or incomplete run records never silently produce wrong results.

### Acceptance Criteria

**Given** a payroll run with `statutory_effective_date` populated,  
**When** PER_EMPLOYEE retry is triggered,  
**Then** statutory rules are resolved using that exact date — the same rules applied in the original run.

**Given** a payroll run where `statutory_effective_date IS NULL` (legacy or corrupt run),  
**When** retry is triggered,  
**Then** retry fails immediately with error: `"Run {id} predates snapshot engine — open a correction run"`.  
**And** no calculation proceeds.

**Given** a payroll run where `period_start IS NULL OR period_end IS NULL`,  
**When** retry is triggered,  
**Then** retry fails immediately with error: `"Run {id} has no period dates — cannot retry"`.  
**And** no calculation proceeds.

**Given** the codebase after this change,  
**When** `_build_shared_context` is inspected,  
**Then** there is no `else` branch falling back to `ORDER BY version DESC` — the temporal query is the only statutory resolution path.

### Out of Scope
- Backfilling `statutory_effective_date` on legacy runs (no production data exists)
- Changing the statutory rule structure

### Business Risk
- **Not done:** A statutory rule update (e.g. new PAYE bands mid-year) silently changes the outcome of a retry on a run from before the update — undetectable financial restatement.

### Open Questions
- None.

---

## EMP-P1-4 · Harden onboarding loader — require employee_number

**Priority:** P1 — Data integrity (prerequisite for B3)

**As a** workspace administrator,  
**I want** the onboarding loader to reject any employee record missing an `employee_number`,  
**So that** no employee is inserted with a fallback "UNKNOWN" value that would silently violate the unique constraint once it is enforced.

### Acceptance Criteria

**Given** an onboarding payload where one employee has no `employee_number` field,  
**When** the payload is processed by the loader,  
**Then** a `ValueError` is raised identifying the employee by index — no DB INSERT is attempted.

**Given** an onboarding payload where all employees have valid, distinct `employee_number` values,  
**When** the payload is processed,  
**Then** all employees are inserted successfully (behaviour unchanged).

**Given** the codebase after this change,  
**When** `loader.py` line ~76 is inspected,  
**Then** there is no `"UNKNOWN"` default — the field is required or an exception is raised.

### Out of Scope
- Changing the validation layer (`onboarding_validation.py`) — it already rejects missing numbers
- Adding employee_number auto-generation

### Business Risk
- **Not done:** After B3 enforces NOT NULL + UNIQUE, the first duplicate "UNKNOWN" employee hits the DB constraint and the transaction rolls back — harder to debug than an explicit error.

### Open Questions
- None.

---

## EMP-P1-5 · Enforce no-overlap contracts at DB level

**Priority:** P1 — Payroll correctness (arch-council D3, Option C)

**As a** payroll operator,  
**I want** the system to prevent two overlapping contracts for the same employee from existing simultaneously,  
**So that** payroll always resolves to exactly one contract for any pay period without ambiguity.

### Acceptance Criteria

**Given** an employee with an active contract (no end_date),  
**When** an attempt is made to insert a second contract for the same employee with any start_date,  
**Then** the DB rejects it with a constraint violation (`excl_employee_contract_no_overlap`).

**Given** an employee with a contract ending 2026-03-31,  
**When** a new contract starting 2026-04-01 is inserted,  
**Then** the insert succeeds (adjacent, non-overlapping).

**Given** an employee with a contract covering 2026-01-01 to 2026-06-30,  
**When** a contract starting 2026-03-01 is inserted,  
**Then** the insert is rejected (overlap detected).

**Given** the migration applied,  
**When** `alembic downgrade -1` is run,  
**Then** the exclusion constraint is dropped and adjacent/overlapping inserts are both permitted again.

**Given** the `btree_gist` extension,  
**When** the migration runs,  
**Then** `CREATE EXTENSION IF NOT EXISTS btree_gist` executes without error (extension confirmed available in target environment).

### Out of Scope
- Retroactive cleanup of any existing overlapping contracts (no production data exists)
- UI validation for contract dates (separate concern)

### Business Risk
- **Not done:** Payroll silently picks one of two valid contracts — which one depends on query ordering, making output non-deterministic and unauditable.
- **Done wrong:** Half-open interval (`[)`) vs closed interval (`[]`) must use `COALESCE(end_date, 'infinity'::date)` — a closed interval with NULL end_date throws at apply time.

### Open Questions
- None. btree_gist availability confirmed by Michael in prior session.

---

## EMP-P1-6 · Enforce employee_number NOT NULL + unique index

**Priority:** P1 — Identity stability (arch-council R5)

**As a** payroll operator,  
**I want** every employee to have a mandatory, unique employee number within their workspace,  
**So that** payroll outputs, payslips, and exports reliably reference a single, stable human-readable identity.

### Acceptance Criteria

**Given** the `employee` table after migration,  
**When** an INSERT is attempted with `employee_number = NULL`,  
**Then** the DB rejects it with a NOT NULL violation.

**Given** two employees in the same workspace,  
**When** an INSERT is attempted with the same `employee_number` as an existing row,  
**Then** the DB rejects it with a unique constraint violation (`ux_employee_number`).

**Given** two employees in different workspaces,  
**When** they share the same `employee_number`,  
**Then** both inserts succeed (workspace-scoped uniqueness only).

**Given** the old partial index `uq_employee_number_per_workspace`,  
**When** this migration runs,  
**Then** that index is dropped before the new `ux_employee_number` index is created (no duplicate indexes).

**Given** `alembic downgrade -1`,  
**Then** `ux_employee_number` is dropped, `employee_number` becomes nullable again, and `uq_employee_number_per_workspace` is restored.

### Out of Scope
- Backfilling employee_number values (no production data exists)
- Exposing employee_number as editable in the UI (separate story)

### Business Risk
- **Not done:** NULL employee_number allows duplicate or unidentifiable employees. Multiple NULLs bypass the UNIQUE constraint (SQL NULL ≠ NULL). Payroll inputs linked by employee_number silently fail to resolve.

### Open Questions
- None.

---

## EMP-P1-7 · Snapshot public holiday calendar at run creation

**Priority:** P1 — Determinism (v5 execution spec gap)

**As a** payroll operator,  
**I want** the public holiday calendar used during a payroll run to be recorded on the run record,  
**So that** a retry always uses the same holiday set as the original run, even if the calendar is later amended.

### Acceptance Criteria

**Given** a payroll run is created for a period containing bank holidays,  
**When** the run is executed,  
**Then** `payroll_run.public_holidays_snapshot` is populated with the sorted list of holiday dates for that period before any calculation begins.

**Given** a public holiday is added to the workspace calendar after a run completes,  
**When** a PER_EMPLOYEE retry is triggered on the original run,  
**Then** the retry uses the snapshot dates (not the updated calendar) — the new holiday is not applied.

**Given** a payroll run where `public_holidays_snapshot IS NULL` (pre-engine run),  
**When** retry is triggered,  
**Then** retry fails immediately with: `"Run {id} has no public holiday snapshot — open a correction run"`.

**Given** the migration,  
**When** `alembic downgrade -1` runs,  
**Then** the `public_holidays_snapshot` column is dropped cleanly.

### Out of Scope
- Changing how public holidays affect proration or attendance calculations (logic unchanged)
- UI display of the snapshotted holidays

### Business Risk
- **Not done:** A calendar correction (e.g. government declares an ad-hoc holiday after payroll is run) changes the retry output vs the original — silent financial discrepancy in a closed period.

### Open Questions
- None.
