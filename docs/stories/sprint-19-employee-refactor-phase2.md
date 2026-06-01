# Sprint 19: Employee Refactor — Phase 2 (Snapshot Engine)

**Delivery increment:** Track C (snapshot tables migration) + Track D (application wiring)  
**Depends on:** Sprint 18 (Phase 1 constraints and code fixes fully applied and verified)  
**Arch-council approval:** v1–v5 (original session) + D1–D6 (second session — employee contract retry model corrected)

---

## Scope Boundary

**IN scope:**
- Three new snapshot tables: `employee_contract_snapshot`, `component_metadata_snapshot`, `client_component_metadata_snapshot`
- Retry-blocked UI state in PayrollResults (EMP-UX-3 — depends on snapshot engine being live)
- `salary_inputs_snapshot` column on `payroll_result`
- New `SnapshotService` with create and validate functions
- Original run path writes snapshot BEFORE execution begins
- Retry path reads from snapshot tables (removes all live reads for component/override/holiday data)
- Per-result audit trail via `salary_inputs_snapshot`

**OUT of scope:**
- Changing payroll calculation logic
- Snapshot UI / admin visibility of snapshot contents
- Retroactive snapshotting of historical runs (no production data exists)
- Onboarding or employee management changes (Phase 3)

---

## EMP-P2-1 · Create snapshot tables and salary audit column

**Priority:** P1 — Infrastructure prerequisite for all Phase 2 stories

**As a** payroll system architect,  
**I want** the three snapshot tables and the `salary_inputs_snapshot` column to exist in the schema,  
**So that** the application layer has a place to write and read deterministic execution context.

### Acceptance Criteria

**Given** the migration is applied (`alembic upgrade head`),  
**When** the schema is inspected,  
**Then** all three tables exist with the correct columns and constraints:
- `employee_contract_snapshot`: `UNIQUE(payroll_run_id, employee_id)`, FK to `payroll_run` and `employee`, includes `salary_definition_id UUID NOT NULL` (D1 — frozen FK used by retry to join live `salary_definition`)
- `component_metadata_snapshot`: `UNIQUE(payroll_run_id, component_code)`, FK to `payroll_run`
- `client_component_metadata_snapshot`: `UNIQUE(payroll_run_id, component_code)`, FK to `payroll_run`, includes `workspace_id`
- `payroll_result.salary_inputs_snapshot`: `JSONB NOT NULL` (no permanent server default after migration)

**Given** `alembic downgrade -1`,  
**Then**:
- `salary_inputs_snapshot` column is dropped from `payroll_result`
- All three snapshot tables are dropped in reverse FK order
- No orphaned FKs remain

**Given** the migration is run twice (idempotency check via `ADD COLUMN IF NOT EXISTS` guards),  
**Then** it completes without error the second time.

### Out of Scope
- Populating the tables (covered by EMP-P2-2 and EMP-P2-3)
- Indexes beyond the UNIQUE constraints

### Business Risk
- **Not done:** Phase 2 application code has nowhere to write — cannot proceed.
- **Done wrong:** Permanent `DEFAULT '{}'::jsonb` left on `salary_inputs_snapshot` would mask missing data silently. Must be two-step: ADD with DEFAULT, then DROP DEFAULT.

### Open Questions
- None. DDL fully specified in implementation plan (Track C — Migration C1).

---

## EMP-P2-2 · SnapshotService — create and validate

**Priority:** P1 — Core service enabling deterministic execution

**As a** payroll engineer,  
**I want** a dedicated `SnapshotService` that owns all snapshot creation and pre-flight validation,  
**So that** snapshot logic is in one place and both the original run path and the retry path enforce the same completeness gate.

### Acceptance Criteria

**`create_payroll_snapshot`**

**Given** a payroll run with N employees and M component types,  
**When** `create_payroll_snapshot(db, payroll_run_id, workspace_id, employees_data, component_metadata, client_overrides_raw)` is called,  
**Then**:
- N rows exist in `employee_contract_snapshot` for `payroll_run_id`
- M rows exist in `component_metadata_snapshot` for `payroll_run_id`
- One row per override in `client_component_metadata_snapshot` for `payroll_run_id`
- All writes use `INSERT ... ON CONFLICT DO NOTHING` (idempotent — safe to call twice)

**Given** the function is called a second time for the same `payroll_run_id`,  
**Then** it completes without error and row counts are unchanged (idempotency).

**Given** a DB error occurs while writing any of the three snapshot tables,  
**When** `create_payroll_snapshot` raises,  
**Then** no rows are committed to any snapshot table — all three INSERT batches share one `db.commit()` and a failure in any batch aborts the whole write (D3 atomicity).

**`validate_snapshot_complete`**

**Given** a `payroll_run_id` with zero rows in `employee_contract_snapshot` OR `component_metadata_snapshot` OR `public_holidays_snapshot IS NULL`,  
**When** `validate_snapshot_complete(db, payroll_run_id)` is called,  
**Then** a `ValueError` is raised: `"Run {id} predates snapshot engine — open a correction run"`.

**Given** a `payroll_run_id` with fully populated snapshot tables,  
**When** `validate_snapshot_complete` is called,  
**Then** it returns without raising.

### Out of Scope
- Snapshot deletion or expiry
- Snapshot schema versioning

### Business Risk
- **Not done:** No completeness gate — retry can proceed on a run with partial or missing snapshot data, producing silently wrong results.
- **Done wrong:** Non-idempotent inserts would fail if called twice (e.g. after a transient error retry) — `ON CONFLICT DO NOTHING` is mandatory.

### Open Questions
- None.

---

## EMP-P2-3 · Original run writes snapshot before execution

**Priority:** P1 — Core execution principle enforcement

**As a** payroll operator,  
**I want** the system to snapshot all execution inputs before any calculation begins,  
**So that** if a run fails mid-execution, the snapshot still exists and the run can be retried deterministically.

### Acceptance Criteria

**Given** a payroll run is triggered via the API,  
**When** the run executes,  
**Then** the following sequence is enforced:
1. Live data is queried from DB (employee contracts, component metadata, overrides, public holidays)
2. `create_payroll_snapshot(...)` is called and committed to DB
3. `payroll_run.public_holidays_snapshot` is written and committed
4. Only then does `execute_and_persist()` begin

**Given** `create_payroll_snapshot` raises an exception (e.g. DB error),  
**When** the run is triggered,  
**Then** execution does NOT proceed — a 500 error is returned and no payroll results are written.

**Given** a run completes successfully,  
**When** `SELECT COUNT(*) FROM employee_contract_snapshot WHERE payroll_run_id = '{id}'` is queried,  
**Then** the count equals the number of employees included in the run.

**Given** a run completes successfully,  
**When** `SELECT COUNT(*) FROM component_metadata_snapshot WHERE payroll_run_id = '{id}'` is queried,  
**Then** the count equals the number of distinct component codes loaded for the run.

**Given** a run completes successfully and salary component amounts are edited in-place on the same `salary_definition` record,  
**When** a PER_EMPLOYEE retry is triggered,  
**Then** the retry picks up the corrected amounts — because retry joins `salary_definition` live using the `salary_definition_id` frozen in `employee_contract_snapshot` (D1). The retry result differs from the original by the correction amount; this divergence is intentional and detectable via `salary_inputs_snapshot` comparison.

**Given** a run completes successfully and `employee_contract.salary_definition_id` is changed to point to a different salary definition,  
**When** a PER_EMPLOYEE retry is triggered,  
**Then** the retry still uses the original `salary_definition_id` from the snapshot — the new FK is ignored. Correcting which salary definition an employee is on requires a correction run, not a retry.

### Out of Scope
- Changing what live data is queried (same queries as before, just snapshotted now)
- Snapshot UI visibility

### Business Risk
- **Snapshot written after execution (prior plan bug — now corrected):** A failed run leaves no snapshot, retry is blocked permanently. Operators must open a new correction run — losing context of what failed.
- **Done wrong:** If snapshot commit and execution share a single DB transaction, a rollback on failure would also undo the snapshot — defeating the purpose. Snapshot commit must be separate and prior.

### Open Questions
- None.

---

## EMP-P2-4 · Per-result salary audit trail

**Priority:** P2 — Audit and compliance traceability

**As a** payroll auditor,  
**I want** each individual payroll result row to record the salary inputs used in its calculation,  
**So that** I can reproduce the exact gross and net pay for any employee without needing to know the historical state of `salary_definition` at run time.

### Acceptance Criteria

**Given** a payroll run completes,  
**When** a `payroll_result` row is inspected,  
**Then** `salary_inputs_snapshot` is a non-empty JSONB object containing the derived salary components used for that employee (e.g. `{"BASIC": "150000.00", "HOUSING": "60000.00", ...}`).

**Given** a salary_definition is edited after a run,  
**When** the original `payroll_result` row is queried,  
**Then** `salary_inputs_snapshot` still reflects the values at the time of the original run — unchanged by the edit.

**Given** a PER_EMPLOYEE retry completes with no salary corrections made,  
**When** the new `payroll_result` row is inspected,  
**Then** `salary_inputs_snapshot` matches the original result row — the same amounts were used.

**Given** a PER_EMPLOYEE retry completes after an operator deliberately corrected salary amounts in-place on `salary_definition`,  
**When** the new `payroll_result` row is inspected,  
**Then** `salary_inputs_snapshot` reflects the corrected amounts — not the original. The divergence between the original and retry result rows is visible and expected (D4).

**Given** a result row is inserted without a `salary_inputs_snapshot` value,  
**Then** the DB rejects it with a NOT NULL violation (no silent omission).

### Out of Scope
- Displaying `salary_inputs_snapshot` in the UI (future)
- Comparing original vs retry snapshots in the UI (future)

### Business Risk
- **Not done:** No per-result audit trace. Cannot answer "what salary did this employee have when this result was calculated?" without reconstructing historical DB state — practically impossible after data changes.

### Open Questions
- None.

---

## EMP-P2-5 · Retry reads from snapshots — no live data

**Priority:** P1 — Determinism contract enforcement

**As a** payroll operator,  
**I want** PER_EMPLOYEE retry to read component configuration, client overrides, public holidays, and employee contract structure exclusively from the snapshot tables,  
**So that** a retry after any data change produces identical output to the original run for unchanged employees, and any intentional corrections are picked up only through controlled channels.

### Acceptance Criteria

**`validate_snapshot_complete` gate**

**Given** retry is triggered for a run with no snapshot rows,  
**Then** retry fails immediately with: `"Run {id} predates snapshot engine — open a correction run"`. No calculation proceeds.

**Component metadata — snapshot reads**

**Given** a component's `execution_priority` is changed in `component_metadata` after a run,  
**When** PER_EMPLOYEE retry is triggered on that run,  
**Then** the retry uses the priority from `component_metadata_snapshot` (not the updated live value) — output is unchanged.

**Client overrides — snapshot reads**

**Given** a workspace override (e.g. Housing Allowance percentage) is changed in `client_component_metadata` after a run,  
**When** PER_EMPLOYEE retry is triggered,  
**Then** the retry uses the override from `client_component_metadata_snapshot` — the updated override does NOT affect the retry output.

**Workspace scoping**

**Given** two workspaces with runs in the same period,  
**When** retry is triggered for workspace A,  
**Then** `client_component_metadata_snapshot` rows from workspace B are never loaded — `workspace_id` scoping enforced at query level.

**Public holidays — snapshot reads**

**Given** a public holiday is added to the calendar after a run,  
**When** PER_EMPLOYEE retry is triggered,  
**Then** the retry uses the `public_holidays_snapshot` from the original run — the new holiday does not affect the retry output.

**Employee contract structural fields — snapshot reads (D1)**

**Given** an employee's `shift_type` is changed on their live contract after a run,  
**When** PER_EMPLOYEE retry is triggered,  
**Then** the retry uses the `shift_type` frozen in `employee_contract_snapshot` — the updated value is NOT picked up. OT eligibility gates behave identically to the original run.

**Given** an employee's contract `end_date` is backdated after a run (to fall before the pay period),  
**When** PER_EMPLOYEE retry is triggered,  
**Then** the retry still includes the employee — scope is determined by snapshot existence, not by re-evaluating live contract dates against the period.

**Given** an employee's `grade_id` is changed after a run,  
**When** PER_EMPLOYEE retry is triggered,  
**Then** the retry uses the `grade_id` and `grade_jsonb` frozen in `employee_contract_snapshot` — percentage-based salary derivation is unchanged.

**Salary amounts — live read via frozen FK (D1)**

**Given** salary component amounts are edited in-place on `salary_definition` after a run (same record, same `salary_definition_id`),  
**When** PER_EMPLOYEE retry is triggered,  
**Then** the retry picks up the corrected amounts — retry joins `salary_definition` live using the `salary_definition_id` frozen in the snapshot. The corrected result differs from the original; this divergence is intentional.

**Given** `employee_contract.salary_definition_id` is changed to point to a different salary definition after a run,  
**When** PER_EMPLOYEE retry is triggered,  
**Then** the retry uses the original `salary_definition_id` from the snapshot — the new FK is ignored. This correction requires a correction run, not a retry.

**Employee set frozen (D2)**

**Given** an employee was included in the original run (snapshot row exists),  
**When** PER_EMPLOYEE retry is triggered,  
**Then** that employee is always in scope for retry — regardless of any live contract changes made after the run.

**Given** an employee was NOT included in the original run (no snapshot row),  
**When** PER_EMPLOYEE retry is triggered,  
**Then** the employee cannot be added to the retry — requires a correction run.

**Hard-fail on missing snapshot row (D6)**

**Given** retry is processing a failed employee and no `employee_contract_snapshot` row exists for that employee on that run,  
**When** the retry service looks up the snapshot,  
**Then** it raises immediately with a data integrity error — it does NOT silently skip the employee. This is not a "no active contract" case; it is a snapshot integrity failure.

**Live reads eliminated**

**Given** the retry service code after this change,  
**When** `_build_shared_context` and the per-employee retry loop are inspected,  
**Then** there are no live queries against:
- `component_metadata`
- `client_component_metadata`
- `national_public_holiday` or `workspace_public_holiday`
- `employee_contract` (structural reads — scope, shift_type, grade)

**Then** the only live read in the per-employee loop is a join to `salary_definition` via the `salary_definition_id` frozen in `employee_contract_snapshot`.

**Given** `alembic downgrade` reverts Phase 2 migrations,  
**Then** retry reverts to prior behaviour (this is inherently unsafe — downgrade is only for dev/rollback, not production use).

### Out of Scope
- Snapshotting statutory rules (already handled by `rules_context_snapshot` on `payroll_run`)
- Snapshotting `salary_definition` amounts at run time for audit purposes (covered by `salary_inputs_snapshot` on `payroll_result` in EMP-P2-4)
- Retroactive re-snapshotting of historical runs
- Any UI surface for snapshot inspection (future sprint)

### Business Risk
- **Not done:** A component config or override change between original run and retry silently produces different output — undetectable financial discrepancy. Two runs of the same payroll period produce different totals with no audit trail.
- **Not done (employee contract):** An operator can backdate a contract `end_date` between run and retry, silently removing an employee from payroll for the period. Or change `shift_type`, silently altering OT eligibility. Neither change leaves any trace in the retry audit log under the prior (live-read) behaviour.
- **Done wrong — workspace scoping missing:** Cross-workspace override leakage via `client_component_metadata_snapshot` — a critical financial data isolation failure.
- **Done wrong — D6 missing (silent skip):** If a missing snapshot row is silently skipped, a failed employee is never retried and the run is left in PARTIAL with no error surfaced. The operator has no visibility into why the employee was dropped.

### Open Questions
- None. All decisions resolved in second arch-council session (D1–D6).

---

## EMP-UX-3 · Retry-blocked state in PayrollResults

**Priority:** P1 — Operator experience (without this, a blocked retry surfaces as an opaque error toast)

**As a** payroll operator,  
**I want** a clear, actionable message when a retry cannot proceed because the run predates the snapshot engine,  
**So that** I understand what happened and know the correct next step (open a correction run) rather than retrying repeatedly.

### Context

After Sprint 19, `payrollApi.retryRun(runId)` returns an error containing `"predates snapshot engine"` for any run created before the snapshot engine was deployed. The current UI routes all retry errors to a generic `actionError` `AlertBanner` (`PayrollResults.tsx:771`). This is insufficient — the operator needs to distinguish a retryable transient failure from a permanently blocked run.

### Acceptance Criteria

**Blocked retry — modal**

**Given** the operator clicks "Retry",  
**When** the API returns an error whose message contains `"predates snapshot engine"`,  
**Then** a modal appears (not a toast, not an inline banner) with:
- Title: *"Cannot retry this run"*
- Body: *"This run was created before the snapshot engine was enabled. Retrying would read live data and may produce different results to the original. To correct this period, open a new payroll run."*
- Two buttons: **Close** (secondary) and **New Run →** (primary)

**Given** the operator clicks "New Run →",  
**Then** they navigate to `/workspaces/{id}/payroll/new`.

**Given** the operator clicks "Close" or the ✕,  
**Then** the modal closes and the run is unchanged.

**Pre-emptive button disable**

**Given** the run detail response has `statutory_effective_date` null or absent,  
**When** the results page loads,  
**Then** the Retry button is disabled with tooltip: *"This run cannot be retried — open a correction run instead."*  
No API call needed — the block is detectable from existing run metadata on mount.

**Generic retry failure (unchanged)**

**Given** any other API error (network, server fault),  
**Then** the existing `actionError` `AlertBanner` behaviour is unchanged — no modal.

### Implementation note
Disable check on mount from run metadata avoids a wasted API round-trip. Modal is a fallback for edge cases where `statutory_effective_date` is present but the snapshot rows are missing.

### Out of Scope
- Automated correction run creation
- Backend changes — frontend only

### Business Risk
- **Not done:** Operator hits a cryptic error, retries multiple times, raises a support ticket. A modal with a single CTA ("New Run →") resolves without support intervention.

### Open Questions
- None.
