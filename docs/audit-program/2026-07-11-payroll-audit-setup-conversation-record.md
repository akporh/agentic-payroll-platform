# Payroll Audit Setup — Conversation Record

**Date:** 11 July 2026  
**Repository:** `akporh/agentic-payroll-platform`  
**Purpose:** Preserve the reasoning, decisions, prompts, and progress from the conversation used to design and establish the payroll audit programme.

> **Continuity note:** This file records the conversation and decisions that led to the audit setup. It is not an authoritative audit-state file. If this record becomes stale, the current contents of `docs/audit-program/audit-state.md`, the relevant stage `CONTEXT.md`, findings, evidence, and human-decision records take precedence.

---

## 1. Why the audit was needed

The original concern was not limited to obvious bugs. The larger risk was that the payroll platform could appear to work while different parts of the system were using inconsistent versions of the same configuration or business rule.

Examples already observed included:

- snapshot behaviour existing in the main payroll engine but not in retry
- onboarding writing configuration into JSON while the UI updated a separate database column
- the engine reading a different representation from the one being edited
- settings captured during onboarding but never used later
- UI controls that were not wired through to backend behaviour
- backend capabilities that existed but were not exposed in the UI
- duplicate configuration locations with unclear precedence
- silent failures, fallbacks, or defaults producing plausible but incorrect payroll results
- execution traces and step-through scripts that had drifted from the current implementation

The central problem was therefore defined as:

> There was no verified, end-to-end trace proving that each payroll configuration had one authoritative source, was persisted correctly, was consumed consistently across original and retry execution, was represented accurately in the UI, and produced reproducible, observable results.

---

## 2. Desired outcome

The audit should produce an evidence-backed assurance backlog rather than a speculative code review.

Expected outputs include:

- a configuration catalogue
- a source-of-truth map
- an execution-path map
- a snapshot integrity map
- a UI/API/backend wiring map
- an execution-trace baseline
- a diagnostic-script inventory
- silent-failure findings
- data-integrity findings
- security and tenant-isolation findings
- scenario-test gaps
- simplification opportunities
- a prioritised remediation backlog

Every finding should clearly separate:

- current implementation
- intended behaviour
- suspected or confirmed defect

Every confirmed finding should be supported by one or more of:

- code references
- test results
- database evidence
- controlled non-production execution

---

## 3. Role of the stronger model

The working strategy was to use a stronger coding model for the high-judgement investigation and backlog design, then use cheaper models later for bounded remediation tasks.

The stronger model should act as:

- principal auditor
- systems investigator
- evidence gatherer
- backlog designer

It should not act as an unquestioned autonomous fixer.

The audit should separate:

1. exploration
2. evidence collection
3. interpretation
4. human decisions
5. remediation planning
6. implementation
7. independent verification

---

## 4. Execution trace and diagnostic scripts

The system already had execution tracing and step-through or simulation scripts, but they were no longer aligned with the current payroll platform.

This was agreed to be part of the same audit programme, but as its own workstream.

The trace and scripts are both:

- an audit subject, because they may be stale or misleading
- an audit enabler, because reliable traces make configuration, snapshot, and retry inconsistencies easier to prove

The key design principle agreed was:

> Step-through scripts must not become a second implementation of payroll logic.

The target relationship should be:

```text
Shared production calculation and context services
        ↓
Original run
Retry
Preview
Step-through
Trace presentation
```

Execution traces should be emitted by the real calculation path rather than reconstructed independently by scripts.

---

## 5. ICM-style audit structure

The audit was organised using an ICM-style staged workspace.

The working principles were:

- filesystem as workflow
- one folder per stage
- explicit stage contracts
- evidence and findings stored with each stage
- a central audit-state file
- human review gates between stages
- one governing instruction source
- no hidden assumptions carried across sessions

### Responsibility split

Casper should help with:

- inspecting the repository
- identifying current architecture and execution paths
- creating audit folders and templates
- populating repository maps
- adding code references
- gathering evidence
- maintaining audit state

Casper should not independently decide:

- intended payroll behaviour
- authoritative configuration sources
- business severity without context
- architecture decisions requiring human approval
- whether suspected issues are acceptable
- production-code remediation during the audit

---

## 6. Repository orientation

Casper performed a read-only repository orientation and identified the main areas of the codebase.

Relevant locations included:

- payroll engine under `backend/domain/payroll/`
- retry under `backend/application/payroll_retry_service.py`
- snapshots under `backend/application/snapshot_service.py` and domain snapshot logic
- execution tracing under:
  - `backend/application/execution_tracer.py`
  - `backend/application/trace_decorators.py`
  - `backend/infra/repositories/execution_trace_repo.py`
- diagnostic tooling split across:
  - `scripts/`
  - `backend/scripts/`
- onboarding under backend routes/services and frontend setup pages
- workspace configuration UI under frontend pages
- migrations under `migrations/versions/`
- root test suite under `tests/`
- UAT scenario harness under `uat/`

The selected audit workspace location was:

```text
docs/audit-program/
```

---

## 7. Approved audit scaffold

The approved minimal scaffold was:

```text
docs/audit-program/
├── README.md
├── WORKFLOW.md
├── audit-state.md
├── _core/
│   ├── evidence-standard.md
│   ├── finding-schema.md
│   ├── severity-model.md
│   └── human-decisions.md
└── 01-system-inventory/
    ├── CONTEXT.md
    ├── findings.md
    └── evidence/
```

Important decisions:

- `CLAUDE.md` remains the sole governing repository instruction source.
- No additional root `AGENTS.md` was added.
- The entire audit programme is read-only.
- Even the future execution-trace remediation stage produces recommendations rather than code changes.
- Production remediation begins only after Stage 13 produces an approved backlog.
- Historical documentation is reference-only until reverified against current code.

Severity model:

- S0 — Critical
- S1 — High
- S2 — Medium
- S3 — Low

---

## 8. Planned audit stages

1. System inventory
2. Execution trace and diagnostic-script baseline
3. Configuration integrity
4. Original-run and retry parity
5. Snapshot integrity
6. UI/API/backend wiring
7. Silent failures and observability
8. Data integrity
9. Security and tenant isolation
10. Execution-trace remediation design
11. Scenario testing
12. Code simplification
13. Consolidated backlog

All audit stages are read-only.

---

## 9. Stage 01 — System Inventory

Stage 01 was opened, executed, reviewed, and closed.

### Outputs produced

- verified repository map
- current execution-path map
- configuration entry-point inventory
- persistence and repository-layer map
- test and diagnostic-tool inventory
- document-authority inventory
- 13 findings
- supporting evidence files

### Confirmed findings

Eight S3 findings were confirmed.

Plausible findings included:

- duplicate ORM repository directory
- empty `component_metadata` potentially triggering the legacy executor fallback
- unclear authority of `docs/wrapper-command/`

### Open human decisions

1. Is silent fallback to the legacy executor when `component_metadata` is empty intended?
2. Is the second repository directory intentional or architectural debt?
3. What is the authority status of `docs/wrapper-command/`?

### Stage 01 status

- Status: complete
- Opened: 11 July 2026
- Closed: 11 July 2026

---

## 10. Documentation-authority decision

The following decision was made:

> `docs/wrapper-command/` is reference-only and non-authoritative pending future verification.

Additional rule:

> `CLAUDE.md` remains the sole governing instruction source for the audit programme.

The wrapper-command documents were not archived or deleted.

---

## 11. Stage 02 — Execution Trace and Diagnostic-Script Baseline

Stage 02 was identified as the next stage.

### Objective

Establish the current, evidence-backed baseline for:

- production execution flow
- trace creation and persistence
- `component_trace_jsonb`
- execution-trace repository behaviour
- original-run tracing
- retry tracing
- diagnostic scripts
- step-through scripts
- script drift
- script safety as audit instrumentation

### Required investigation

- trace production execution from payroll-run orchestration through handlers and persistence
- inspect tracer creation, enrichment, persistence, and exposure
- inspect both script locations
- identify scripts that:
  - call production services
  - reimplement payroll logic
  - depend on stale schemas
  - use sequential execution
  - fall through to legacy execution
  - write data
  - are read-only
  - are duplicates or obsolete
- compare original-run, retry, and diagnostic-script traces
- determine whether `component_trace_jsonb` and the execution-trace repository are one trace system or separate mechanisms
- determine which scripts can be retained, repaired, replaced, or retired

### Stage 02 constraints

- read-only
- no production-code changes
- no script repairs yet
- no assumptions based only on names or comments
- confirmation through code tracing, tests, or controlled non-production execution
- unresolved decisions recorded in `_core/human-decisions.md`

---

## 12. Approved Stage 02 kickoff prompt

```text
Begin Stage 02 — Execution Trace and Diagnostic-Script Baseline.

Before starting:

1. Read:
   - docs/audit-program/README.md
   - docs/audit-program/WORKFLOW.md
   - docs/audit-program/audit-state.md
   - all files in docs/audit-program/_core/
   - docs/audit-program/01-system-inventory/findings.md
   - the Stage 01 evidence relevant to executor paths, scripts and document authority
2. Confirm the human decision that:
   - CLAUDE.md is the sole governing instruction source for this audit
   - docs/wrapper-command/ is reference-only and non-authoritative pending future verification
3. Create:
   - docs/audit-program/02-execution-trace-baseline/CONTEXT.md
   - docs/audit-program/02-execution-trace-baseline/findings.md
   - docs/audit-program/02-execution-trace-baseline/evidence/
4. Populate CONTEXT.md before performing the stage.
5. Update audit-state.md to mark Stage 02 in-progress with today's opened date.

Objective:

Establish the current, evidence-backed baseline for execution tracing,
component-level trace persistence, step-through and simulation scripts,
original-run tracing, retry tracing, and diagnostic-script drift.

Required investigation:

- Trace the production execution path from payroll-run orchestration through
  employee execution, sequential execution, handlers, result building and persistence.
- Identify where execution traces are created, enriched, persisted and exposed.
- Inspect:
  - backend/application/execution_tracer.py
  - backend/application/trace_decorators.py
  - backend/infra/repositories/execution_trace_repo.py
  - all production callers of the tracer
- Inventory and inspect:
  - scripts/
  - backend/scripts/
- Identify which scripts:
  - invoke production services directly
  - reimplement calculation logic
  - depend on stale schemas, models, fields or execution assumptions
  - use the sequential executor
  - can fall through to the legacy executor path
  - persist data
  - are read-only
  - appear unused or duplicated
- Determine whether component_trace_jsonb and the execution-trace repository
  represent one trace system or separate trace mechanisms.
- Compare trace behaviour across:
  - original payroll execution
  - full retry
  - partial retry
  - per-employee retry
  - diagnostic or step-through scripts
- Determine whether current scripts can safely be used as audit instrumentation.

Required outputs:

- current production execution-flow map
- execution-trace lifecycle map
- trace schema/field inventory
- diagnostic-script catalogue
- script-to-production-service dependency map
- original-run/retry/script trace comparison
- list of stale, duplicated or unsafe scripts
- retain/repair/replace/retire assessment
- findings using the shared schema
- evidence stored in the Stage 02 evidence folder

Constraints:

- read-only audit stage
- no application, script, test, migration, or existing documentation changes
  outside docs/audit-program/
- do not repair scripts yet
- do not infer correctness from names or comments
- verify through code tracing, tests, or controlled non-production execution
- keep implementation, intended behaviour, and suspected defect separate
- record unresolved decisions in _core/human-decisions.md

When complete:

- check every Stage 02 completion criterion
- do not mark the stage complete without explicit approval
- report outputs, findings, script disposition, human decisions,
  completion status, and git status
- do not commit or push
```

---

## 13. Current position at the end of this conversation

The audit programme has been established.

- Stage 01 is complete.
- The `docs/wrapper-command/` authority question has been resolved for audit purposes.
- Stage 02 is the next planned stage.
- No production code should be changed as part of Stage 02.

The next operational action is:

> Open and execute Stage 02 — Execution Trace and Diagnostic-Script Baseline.
