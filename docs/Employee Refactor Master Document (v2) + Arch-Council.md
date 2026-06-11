🏛 ARCH COUNCIL SUBMISSION PACK (v1)
Employee Refactor — Payroll Deterministic Execution System
1. 📌 EXECUTIVE SUMMARY
Proposal

We propose a controlled refactor of the payroll system into a:

fully deterministic, snapshot-driven payroll execution engine

This removes all reliance on live database state during payroll execution and introduces strict separation between:

Identity (Employee Registry)
Employment Configuration (Contracts, Salary, Grade)
Execution Context (Snapshots)
Payroll Calculation Engine (Deterministic runtime)
Core Outcome

After implementation:

✔ Payroll runs become fully replayable
✔ No live-data drift in recalculation or retry
✔ HR integration becomes safe and non-breaking
✔ Audit compliance is structurally guaranteed
✔ Payroll becomes a deterministic financial system

2. 🧭 TARGET ARCHITECTURE
2.1 High-Level System Flow
                ┌──────────────────────┐
                │  Employee Registry   │
                │  (Identity Layer)    │
                └─────────┬────────────┘
                          │
                          ▼
            ┌────────────────────────────┐
            │ Employment Configuration   │
            │ (Contracts, Grade, Salary)│
            └─────────┬──────────────────┘
                      │
                      ▼
        ┌────────────────────────────────────┐
        │ Payroll Snapshot Engine (NEW CORE) │
        │ - contract_snapshot               │
        │ - component_snapshot              │
        │ - rules_snapshot                 │
        └─────────┬────────────────────────┘
                  │
                  ▼
     ┌──────────────────────────────────────┐
     │ Payroll Execution Engine (Deterministic) │
     │ sequential_executor / run_executor       │
     └─────────┬──────────────────────────────┘
               │
               ▼
        ┌───────────────┐
        │ Payroll Result │
        └───────────────┘
2.2 Data Dependency Model
CURRENT (PROBLEMATIC)
----------------------
Payroll → live employee_contract
Payroll → live salary_definition
Payroll → live component_metadata
Payroll → live client overrides


TARGET (CORRECT)
----------------------
Payroll → snapshot tables ONLY
3. 🧱 SYSTEM LAYERS (FORMAL SPEC)
3.1 Employee Registry (Identity Layer)
employee
employee_number (UNIQUE, NOT NULL)
workspace_id
status
Purpose:

Identity only. No payroll logic.

3.2 Employment Layer
employee_contract
salary_definition
grade
designation
Purpose:

Mutable configuration layer (NOT execution source).

3.3 Snapshot Layer (NEW CRITICAL LAYER)
employee_contract_snapshot
component_metadata_snapshot
client_component_metadata_snapshot
rules_context_snapshot (existing)
Purpose:

Freeze execution context at runtime.

3.4 Execution Layer
sequential_executor
run_executor
payroll_result
Purpose:

Deterministic computation engine.

4. 🔁 EXECUTION MODEL
Payroll Function Definition
payroll_result = f(snapshot_state, period_inputs, rules_snapshot)

NOT:

payroll_result = f(live_database_state)
5. 📅 EMPLOYMENT TIMING RULE
Inclusion Rule (Canonical)
contract.start_date <= period_end
AND
(contract.end_date IS NULL OR contract.end_date >= period_start)
Decision:
employee.status is NOT used for payroll inclusion
6. 🔒 RETRY SEMANTICS
6.1 Retry Model

Retry is a re-execution of snapshot, NOT recomputation

6.2 Allowed
snapshot reuse only
deterministic recomputation
6.3 Forbidden
any live DB reads
any recalculation from updated salary/grade/components
6.4 FULL_RUN Rule

FULL_RUN must:

be blocked if SUCCESS rows exist OR
behave strictly as snapshot replay
6.5 Correction Model

Any correction requires a new payroll_run_id

No historical mutation allowed.

7. 🧾 SNAPSHOT SPECIFICATION
7.1 Snapshot Trigger

At:

payroll_run START

7.2 Snapshot Tables
Employment Snapshot
employee_contract_snapshot
includes:
contract state
salary_definition reference
grade
union status
validity dates
version hash (recommended)
Component Snapshot (NEW CRITICAL GAP FIX)
component_metadata_snapshot
client_component_metadata_snapshot

Includes:

calculation method
execution priority
overrides
effective configuration at runtime
Rules Snapshot (existing)
rules_context_snapshot (immutable)
8. ⚠️ RISK REGISTER
8.1 CRITICAL RISKS
ID	Risk	Impact	Mitigation
R1	FULL_RUN recomputes SUCCESS rows using live logic	Financial inconsistency, audit failure	Block FULL_RUN or enforce snapshot-only execution
R2	Missing snapshot of component_metadata	Non-deterministic payroll output	Expand snapshot scope before Phase 2
R3	Missing snapshot of client overrides	Silent payroll variation between runs	Include workspace-level snapshot
R4	Retry system re-reads live salary data	Determinism violation	Rewrite retry to snapshot-only execution
8.2 HIGH RISKS
ID	Risk	Impact	Mitigation
R5	employee_number NULL allowed in DB	Duplicate employees, duplicate payslips	Add NOT NULL + backfill migration
R6	Missing effective_from/to filters in retry	Salary drift in retry runs	Align retry query with main run filters
R7	Missing POST /employees API	Blocks Phase 3 decoupling	Scope new employee service
8.3 MEDIUM RISKS
ID	Risk	Impact	Mitigation
R8	Status used instead of contract dates	Incorrect inclusion/exclusion	Enforce contract-based logic only
R9	Snapshot schema incomplete	Re-introduces live joins	Require Arch Council approval before migration
9. 🧠 OPEN ARCHITECTURAL DECISIONS

Council must approve:

D1 — Retry Semantics
Option A (recommended): snapshot-only retry
Option B: hybrid retry (NOT recommended)
D2 — Mid-period hire rule
contract-based inclusion (recommended)
or status-based (rejected)
D3 — Snapshot model
one row per employee per run (recommended)
OR version-split model (not needed yet)
D4 — FULL_RUN behavior
strict snapshot replay (recommended)
OR disable until Phase 2 complete
10. 🧪 VALIDATION CRITERIA (GO/NO-GO)
GO Criteria for Phase 2

✔ Snapshot scope includes ALL calculation-critical tables
✔ Retry is snapshot-only
✔ FULL_RUN behavior defined and safe
✔ employee_number migration safe (backfill included)
✔ No live reads in execution path

NO-GO Conditions

❌ Any live DB reads in payroll execution
❌ Incomplete snapshot schema
❌ Undefined retry semantics
❌ Missing mitigation for FULL_RUN risk

11. 🎨 UI/UX VALIDATION ROLE (NON-BLOCKING)
Purpose:

Ensure workflows are understandable to humans

Responsibilities:
validate admin journeys
identify missing workflow steps
validate terminology consistency
Constraint:

No UI design until Phase 2 completion

12. 🧭 ARCHITECTURAL PRINCIPLES
Payroll correctness > system simplicity > feature completeness
Snapshot defines truth, not database state
Retry is execution, not recomputation
Contracts define employment, not employee status
All financial outputs must be deterministic
13. 📌 FINAL RECOMMENDATION
APPROVAL STATUS REQUESTED

Approve Phase 1 + Phase 2 with mandatory risk mitigations applied.