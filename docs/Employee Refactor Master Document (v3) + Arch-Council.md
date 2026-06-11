📄 V4 DELTA DOCUMENT — Payroll Architecture
Purpose

This document captures all changes from v3 → v4 required to:

Resolve council-blocking decisions
Address Principal Engineer challenges
Make Phase 2 approvable and implementable
✅ 1. Immediate Code Fixes (APPLIED — commit 010f51f, branch uat, 2026-05-27)

1.1 FULL_RUN Crash (P0) — FIXED
def _retry_full_run(...):
    # FULL_RUN is disabled pending snapshot engine implementation (arch-council v3).
    # It deletes SUCCESS rows unconditionally and reads live salary/component data,
    # both of which violate the determinism contract. Use PER_EMPLOYEE retry instead.
    raise ValueError("FULL_RUN retry is disabled. Use PER_EMPLOYEE retry or open a new correction run.")
Prevents NameError (tracer out of scope)
Aligns with planned removal of FULL_RUN
_build_shared_context return dict now includes period_start and period_end

1.2 CURRENT_DATE Removal (All 4 Sites Fixed) — FIXED

Affected locations (all replaced):

payroll.py:131 → employee contract inclusion filter
payroll.py:199 → union member eligibility filter
payroll_retry_service.py:516 → FULL_RUN employee load (now dead code behind raise)
payroll_retry_service.py:841 → PER_EMPLOYEE per-employee contract load

Correct predicate (implemented at all four sites):

ec.start_date <= :period_end_date
AND (ec.end_date IS NULL OR ec.end_date >= :period_start_date)

period_end_date / period_start_date sourced from:
  payroll.py       → _period_end_date / _period_start_date (extracted local vars)
  retry service    → shared_ctx["period_end"] / shared_ctx["period_start"]

Important distinction:

payroll.py:131 → affects employee inclusion (mid-period hires/terminations)
payroll.py:199 → affects is_union_member eligibility (separate downstream effect on percentage_of_sum)
🧱 2. D3 — Contract Overlap (DECISION MADE)
Decision

✅ Option C — Enforce no overlapping contracts at DB level

Implementation
Constraint
ALTER TABLE employee_contract
ADD CONSTRAINT no_overlapping_contracts
EXCLUDE USING gist (
  employee_id WITH =,
  daterange(start_date, end_date, '[]') WITH &&
);
Rationale
Eliminates ambiguity in payroll computation
Prevents silent data corruption
Removes need for runtime resolution logic
Impact
Requires one-time data cleanup migration
Guarantees correctness going forward
🧠 3. D5 — Snapshot Ownership (DECISION MADE)
Decision

✅ Dedicated SnapshotService owns all snapshot creation

Responsibilities
Capture all input data at payroll run creation
Persist snapshot tables
Provide snapshot reads for execution & retry
Alternatives Considered
Route handler → rejected (too thin, orchestration leak)
payroll_run_service → rejected (bloats domain service)
Outcome
Clear ownership boundary
Deterministic execution inputs
Reusable across retries, audits, replays
📊 4. Section 5B — Audit Model (CORRECTED)
v3 Issue
Assumed calculations_snapshot_json contained salary inputs
In reality stores only:
{ "gross": ..., "paye": ..., "net": ... }
v4 Solution
New Column
ALTER TABLE payroll_result
ADD COLUMN salary_inputs_snapshot JSONB NOT NULL;
Captured Data (at original run time)
components_jsonb (earnings + deductions)
base salary
overrides
proration inputs
any runtime adjustments
Execution Rule
PER_EMPLOYEE retry uses snapshot inputs only
No live salary reads allowed
Outcome
Full auditability
Deterministic retry behavior
Compliance-safe payroll traceability
📅 5. CURRENT_DATE Fix (SPECIFICATION TIGHTENED)

v4 explicitly defines required predicate:

start_date <= :period_end
AND (end_date IS NULL OR end_date >= :period_start)
Clarification
NOT equivalent to >= period_end
NOT equivalent to >= period_start
Risk Prevented
Excluding mid-period terminated employees
Incorrect union eligibility resolution
🔁 6. FULL_RUN Removal (MIGRATION DEFINED)
Migration Plan
-- Step 1: Normalize existing rows
UPDATE payroll_run
SET retry_strategy = 'PER_EMPLOYEE'
WHERE retry_strategy = 'FULL_RUN';

-- Step 2: Drop constraint
ALTER TABLE payroll_run
DROP CONSTRAINT ck_payroll_run_retry_strategy;

-- Step 3: Recreate constraint
ALTER TABLE payroll_run
ADD CONSTRAINT ck_payroll_run_retry_strategy
CHECK (retry_strategy = 'PER_EMPLOYEE');
Outcome
No orphaned enum values
Aligns DB constraint with application logic
🆔 7. R5 — employee_number Constraint (RESOLVED)
Problem
UNIQUE index allows multiple NULLs
Creates false sense of identity enforcement
v4 Fix
Step 1 — Backfill

Populate employee_number for all NULL rows

Step 2 — Enforce NOT NULL
ALTER TABLE employee
ALTER COLUMN employee_number SET NOT NULL;
Step 3 — Retain uniqueness
CREATE UNIQUE INDEX ux_employee_number
ON employee(workspace_id, employee_number);
Outcome
True identity stability
Eliminates duplicate NULL loophole
⚖️ 8. Statutory Fallback (DECISION MADE)
Decision

✅ Backfill statutory_effective_date for all legacy runs

Change
Remove fallback:
ORDER BY version DESC
Outcome
Fully deterministic statutory resolution
No live dependency during retry
Aligns with architecture principle
🧾 9. Additional Risk Register Entries (NEW)
9.1 total_tax Misassignment (HIGH)
Issue
total_tax = total_deduction
total_deduction includes non-tax items
total_tax expected to be PAYE only
Risk
Incorrect statutory reporting
Compliance failure downstream
9.2 Legacy Statutory Drift (RESOLVED)
Previously: live fallback risk
Now: eliminated via backfill
9.3 Audit Gap (RESOLVED)
Previously: no salary input trace
Now: salary_inputs_snapshot ensures traceability
🧱 10. Snapshot Tables (NOW IMPLEMENTABLE)

v3 referenced but did not define these.

v4 requires:

Models
Migrations
SnapshotService integration
Gate Condition (Now Real)

Execution requires:

All required snapshot rows exist for payroll_run_id

(Not pseudocode — enforced via SnapshotService pre-flight check)

🚦 11. Approval Status (Updated)
Area	Status
Phase 1	✅ Approved
Phase 2	✅ Now unblocked (pending council approval of v4)
🎯 12. Summary of What Changed from v3
✅ All blocking decisions resolved (D3, D5, statutory fallback)
✅ Audit model corrected (new snapshot column)
✅ CURRENT_DATE fix fully specified
✅ FULL_RUN removal fully defined
✅ employee_number constraint fixed
✅ Snapshot system now implementable (not aspirational)
✅ Risk register expanded with real defects
✅ Final Position

v4 converts the architecture from conceptually correct (v3)
to fully specified, enforceable, and implementable

There are now:

No unresolved design decisions
No undefined data contracts
No hidden live dependencies