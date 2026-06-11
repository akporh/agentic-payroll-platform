🏛 ARCH COUNCIL SUBMISSION v3 (FINAL RESOLUTION PACK)

This version converts your document into:

A decision-required system spec, not just an architecture proposal

1. 📌 UPDATED EXECUTIVE TRUTH
Replace prior claim:

“We are building a deterministic snapshot payroll engine”

With:

“We are transitioning from a live-evaluation payroll system to a fully snapshot-driven deterministic engine through controlled elimination of live dependencies.”

2. 🧭 FINAL TARGET ARCHITECTURE (CORRECTED)
2.1 Execution Reality Model
                ┌──────────────────────┐
                │ Employee Registry    │
                └─────────┬────────────┘
                          │
                          ▼
         ┌─────────────────────────────────┐
         │ Employment Configuration Layer │
         │ (Mutable, NOT authoritative)   │
         └─────────┬──────────────────────┘
                   │
                   ▼
     ┌────────────────────────────────────────┐
     │ SNAPSHOT COMPLETENESS CHECK (NEW GATE) │
     └─────────┬──────────────────────────────┘
               │
     ┌─────────▼──────────────────────────────┐
     │ SNAPSHOT STATE (TARGET TRUTH)           │
     │ - contracts                           │
     │ - components                          │
     │ - client overrides                   │
     │ - statutory rules                    │
     │ - tax bands                         │
     └─────────┬────────────────────────────┘
               │
               ▼
     ┌──────────────────────────────────────┐
     │ DETERMINISTIC EXECUTION ENGINE       │
     └──────────────────────────────────────┘
3. 🔥 CRITICAL ARCHITECTURAL ADDITION (NEW)
🚨 SNAPSHOT COMPLETENESS GATE

Before ANY payroll run executes:

assert no_live_reads_in_execution_path == true
assert all_snapshot_tables_exist == true
assert all_component_sources_snapshotized == true

👉 This is missing today — and is the core blocker identified by both reviewers

4. 🧾 SNAPSHOT SCOPE (FINAL DEFINITION)
MUST BE SNAPSHOTTED (NO EXCEPTIONS)
Employment
employee_contract_snapshot
Components
component_metadata_snapshot
client_component_metadata_snapshot
Rules
rules_context_snapshot (already done)
⚠️ NEW ADDITION (CRITICAL)
statutory rules
tax bands
public holiday calendar

👉 These were missed in v2 — this is the key correction

❗ IMPORTANT CONSEQUENCE

Without statutory snapshots, your system is STILL non-deterministic even if everything else is fixed.

5. 🔁 RETRY MODEL (FINAL RESOLUTION)
Split retry into 2 formally defined systems
A. FULL_RUN (DEPRECATED MODE)
Decision required:

👉 RECOMMENDED: HARD DISABLE

Because:

deletes SUCCESS rows
uses live reads
violates snapshot model
causes silent financial restatement risk
B. PER_EMPLOYEE RETRY (CORRECT MODEL)

Allowed:

live salary correction
BUT MUST STILL:
use contract snapshot
use component snapshot
use statutory snapshot
use period_start/period_end

👉 Key correction:

“fix flow” ≠ “live recomputation”

6. 📅 TIME MODEL (FINAL FIX)
Replace ALL occurrences of:
CURRENT_DATE ❌
With:
payroll_run.period_start
payroll_run.period_end
Applies to:
original run
retry
filtering
contract inclusion
7. 🧩 CONTRACT OVERLAP RESOLUTION (NEW REQUIRED DECISION)
Problem:

Multiple contracts can satisfy:

contract.start_date <= period_end
AND contract.end_date overlaps
Council must choose ONE:
Option A — Most recent contract wins
simple
deterministic
Option B — explicit primary contract flag
HR-controlled
more correct long-term
Option C — strict DB constraint (no overlap allowed)
safest
most rigid

👉 This is REQUIRED before Phase 2

8. 🔒 FULL_RUN FINAL POSITION
Recommendation:

❌ REMOVE FULL_RUN ENTIRELY from system design

OR

🔒 convert to snapshot replay ONLY mode

Because current behavior:

is destructive
is non-deterministic
cannot be reconciled with audit requirements
9. ⚠️ UPDATED RISK REGISTER (DELTA ONLY)
🔴 NEW CRITICAL RISKS
ID	Risk	Severity
N1	Statutory rules not snapshotted	CRITICAL
N2	FULL_RUN deletes SUCCESS rows	CRITICAL
N3	CURRENT_DATE used in all run paths	CRITICAL
N4	Retry system mixes live + snapshot data	CRITICAL
🟠 UPDATED HIGH RISKS
ID	Risk	Severity
H1	Contract overlap undefined resolution	HIGH
H2	Missing snapshot completeness gate	HIGH
H3	No unified execution contract enforcement	HIGH
10. 🧠 FINAL OPEN DECISIONS (BLOCKING)

Council MUST decide:

D1 — Statutory Data Model
snapshot or live?

👉 Recommendation: SNAPSHOT

D2 — FULL_RUN
delete entirely OR snapshot-only OR guarded?

👉 Recommendation: REMOVE

D3 — Contract overlap rule
win condition definition required
D4 — Retry philosophy
correction system vs recomputation system

👉 Recommendation:

Retry = correction flow ONLY (never recomputation)

D5 — Snapshot completeness ownership
which service builds snapshot layer?
11. 🧪 FINAL GO / NO-GO GATE
🚫 NO-GO IF ANY OF:
any live reads remain in execution path
statutory rules not snapshotted
FULL_RUN remains destructive
CURRENT_DATE still used
contract overlap unresolved
✅ GO ONLY WHEN:
snapshot completeness gate exists
ALL calculation inputs are snapshot-driven
retry is deterministic
time model unified
contract rules defined
🏁 FINAL COUNCIL VERDICT (UPDATED)
Phase 1:

✔ APPROVED

Phase 2:

❌ BLOCKED UNTIL:

statutory snapshot scope added
FULL_RUN resolved
time model unified
overlap rules defined
snapshot completeness gate implemented