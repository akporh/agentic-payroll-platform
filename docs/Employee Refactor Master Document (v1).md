🧭  Refactor Master Document (v1)
1. 🎯 North Star Architecture
Goal

Transform the payroll system from a live-state, tightly coupled model into a:

deterministic, snapshot-based payroll execution engine with separated identity, employment, and calculation layers

Core Layers
🧾 1. Employee Registry (Identity Layer)

Purpose: Who exists in the system

employee
employee_id
workspace_id
employee_number (unique)
full_name
status (ACTIVE / INACTIVE)
external_hr_id (future)

📌 Rules:

Must NOT contain payroll logic
Must NOT be used directly in payroll calculations
🧩 2. Employment Layer (Business Configuration)

Purpose: How an employee is paid

employee_contract
salary_definition
grade
designation

📌 Rules:

Can change over time
Represents CURRENT intended state
Must NEVER be used directly in payroll execution
🔒 3. Payroll Snapshot Layer (Execution Boundary)

Purpose: Freeze truth at payroll run time

employee_contract_snapshot (NEW)
rules_context_snapshot (existing)

📌 Rules:

Created at payroll run start
Immutable
ONLY source used by payroll engine
⚙️ 4. Payroll Execution Layer

Purpose: Compute payroll deterministically

payroll_run_service
payroll_result
timesheet aggregation

📌 Rules:

Reads ONLY snapshot + period inputs
MUST NOT read live tables
2. 🚫 Forbidden Coupling Rules (CRITICAL)

Casper must enforce:

❌ Payroll Engine MUST NOT:
read employee_contract directly
read salary_definition directly
read grade directly
depend on live employee state
❌ Onboarding MUST NOT:
create employees (post-migration)
trigger payroll execution logic
❌ Employee Registry MUST NOT:
contain payroll rules or calculations
3. 🧾 Current System Reality (Baseline Audit)
Existing coupling issues:
Payroll reads live employee_contract → ❌ unsafe
Salary/grade changes affect historical recalculation → ❌ non-deterministic
onboarding creates employee + contract in one transaction → ❌ tight coupling
no snapshot of employment state → ❌ no execution boundary
employee_number not unique → ❌ identity instability
4. 🧠 Target State Summary

Payroll becomes a pure function:

payroll_result = f(snapshot, timesheet_input, payroll_input, rules_snapshot)

NOT:

payroll_result = f(live_database_state)
5. 🧭 System Workflow (Target Architecture)
Step 1 — Workspace Creation
create workspace
configure payroll rules shell
Step 2 — Employee Registry Population

Methods:

bulk upload (Excel/API)
manual entry (admin UI)

Creates:

employee only
Step 3 — Employment Assignment (Onboarding Layer)

Attach:

employee_contract
salary_definition
grade
shift_type
Step 4 — Payroll Run Trigger

At start of run:

Snapshot creation:
employee_contract_snapshot
rules_context_snapshot
Step 5 — Payroll Execution

Uses ONLY:

snapshot tables
timesheet_entry
payroll_input
6. 📦 Data Ownership Rules
Layer	Owns	Mutable	Used in Payroll
Employee Registry	Identity	Yes	No
Employment Layer	Pay configuration	Yes	No
Snapshot Layer	Frozen execution state	No	Yes
Payroll Engine	Computation	N/A	Yes
7. 📅 Handling Real-World Payroll Events
🆕 Mid-period hire
employee added anytime
included in snapshot if active during period
🚪 Mid-period termination
employee remains in registry
contract end_date determines inclusion
💰 Mid-period salary change
Phase 1 approach:
snapshot captures current active contract
no historical splitting
Future Phase 3:
contract versioning + split-period payroll
8. 🔧 Refactor Phases
🟢 Phase 1 — Identity Stabilisation (LOW RISK)
Goals:
decouple employee identity from onboarding
stabilise references
Changes:
add UNIQUE(workspace_id, employee_number)
implement employee upsert
add bulk upload API
optionally add external_hr_id
Risk: LOW
Impact: NO payroll logic change
🟡 Phase 2 — Snapshot Engine (CRITICAL)
Goals:
introduce payroll execution boundary
remove live-table dependency
Changes:
create employee_contract_snapshot table
modify payroll_run_service:
snapshot all employees at run start
update payroll_result linkage
Risk: HIGH (core system change)
Requires:
full regression testing
🟠 Phase 3 — Onboarding Decoupling
Goals:
remove employee creation from onboarding
Changes:
onboarding only manages contracts
enforce employee existence beforehand
🔵 Phase 4 — HR Integration Readiness
Optional:
external_hr_id sync
employee sync API
contract versioning
soft delete model
9. 🧪 Casper Validation & Safety Gates

Before any change, Casper MUST:

Check:
 Does payroll read any live tables?
 Does snapshot fully represent execution state?
 Can payroll be replayed identically?
 Are employee identifiers stable?
 Are any hidden joins introduced?
After any change, Casper MUST:
validate deterministic payroll output
verify no new live dependencies
ensure backward compatibility for active runs
10. 🧠 Casper Critic Mode (MANDATORY BEHAVIOUR)

Casper is not just an implementer.

It must:

Always:
flag architectural risks
propose simpler alternatives
challenge unnecessary complexity
detect hidden coupling
warn about financial correctness risks
Casper is explicitly authorised to say:

“This design is unsafe / incomplete / over-engineered”

even if implementation instructions say otherwise.

11. 🧯 Rollback Strategy

Each phase must support:

database migration rollback scripts
feature flag toggles for snapshot engine
dual-run comparison mode (optional Phase 2 safety mode)
12. 📌 Key Principle (must not be violated)

Payroll correctness > system simplicity > feature completeness