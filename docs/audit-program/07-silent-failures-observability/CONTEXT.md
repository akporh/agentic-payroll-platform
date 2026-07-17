# Stage 07 — Silent Failures and Observability

**Status:** in-progress (see [`../audit-state.md`](../audit-state.md))

## Purpose

Identify where payroll operations can fail, diverge, degrade, or become operationally blocked without producing a clear, durable, operator-visible signal.

This stage must distinguish between:

- failures that are completely silent
- failures logged only to server logs
- failures persisted but not surfaced through the API
- failures returned by the API but not rendered in the UI
- failures visible only through indirect symptoms
- failures with incomplete or misleading error context
- failures correctly observable end to end

The goal is an evidence-backed observability map covering logs, persisted error state, audit records, events, execution traces, API responses, UI messages, and operator recovery guidance.

## Confirmed handoff state

- Stages 01–06 are complete.
- `04-001` and `05-001` are remediated and must not be reopened without regression evidence.
- `04-002` remains open: no persisted field records which statutory-rule version a specific `payroll_result` used.
- Stage 02 finding `02-002` remains open: per-employee retry creates no step-level `execution_trace` footprint.
- Stage 06 findings `06-001` and `06-004` confirm that backend `FAILED` status and `error_message` are not properly surfaced in the frontend.
- Stage 06 found `06-006` to be a missing timesheet-audit UI feature; this is a Stage 13 product gap, not the primary focus of Stage 07.
- `05-004` remains deferred to Stage 13.
- `CLAUDE.md` is authoritative; `docs/wrapper-command/` is reference-only.
- Stage 07 is read-only: no production-code, migration, frontend, test, or script changes.

## Required inputs

Read before investigation:

- `CLAUDE.md`
- `docs/audit-program/README.md`
- `docs/audit-program/WORKFLOW.md`
- `docs/audit-program/audit-state.md`
- all files under `docs/audit-program/_core/`
- Stage 01 findings, especially fallback/dead-path and diagnostic observations
- Stage 02 findings and evidence, especially `02-002` and diagnostic/export findings
- Stage 04 findings, especially `04-002`
- Stage 05 findings, especially `05-001` and the completed remediation records
- Stage 06 findings, especially `06-001`, `06-004`, and error/status propagation notes
- `docs/audit-program/remediation/04-001-05-001/summary.md`
- `docs/audit-program/remediation/04-001-05-001/verification.md`

## Objective

Build a complete observability map for the current payroll platform and determine whether a bureau operator, support engineer, auditor, or developer can answer:

1. What failed?
2. Where did it fail?
3. Which run, employee, workspace, period, input, rule, and component were affected?
4. Was any partial state persisted?
5. Can the failure be retried safely?
6. What corrective action is required?
7. Is the signal available through logs, persisted records, API, and UI?
8. Can the original calculation basis be reconstructed later?

## Required investigation

### 1. Build the failure-surface catalogue

Inventory failure points across at least:

- onboarding and workspace setup
- configuration saves and edit locks
- employee/contract creation and validation
- timesheet upload and derivation
- payroll input claiming
- payroll-run creation
- snapshot creation
- background calculation startup
- per-employee calculation
- sequential component execution
- persistence of payroll results
- run-status transitions
- retry preflight and retry execution
- reconciliation
- approval, locking, payment, and export
- audit/event writes
- diagnostic and operator routes

For each failure point record:

- trigger/precondition
- exception or return type
- catch location
- whether swallowed, transformed, re-raised, or persisted
- log level and message
- identifiers included
- persisted status/error field
- audit/event entry
- execution-trace entry
- API response
- UI rendering
- recovery guidance
- observability classification
- evidence

### 2. Revisit known observability findings

#### `04-002` — statutory identity per result

Determine the minimum reliable persisted design required to prove which statutory rule/version a specific `payroll_result` used.

Assess and compare:

- dedicated `payroll_result.statutory_rule_id` and `statutory_version`
- inclusion in `calculations_snapshot_json`
- inclusion in `component_trace_jsonb`
- inclusion in `execution_trace`
- reliance only on the run-level frozen snapshot

Do not implement the design. Produce a clear recommendation and Stage 10 handoff.

#### `02-002` — retry execution-trace gap

Trace why retry instantiates `ExecutionTracer` but produces no step rows.

Determine:

- which original-run steps are absent on retry
- whether the audit/event store compensates for any of them
- whether a failed retry can be reconstructed from current persisted data
- whether parity is required for every step or only a defined subset
- what the minimum useful retry trace should contain

This may require a human decision if the intended trace parity level is not documented.

#### `06-001` / `06-004` — backend signal not surfaced in UI

Document the complete signal path for a `FAILED` run:

```text
background failure
→ payroll_run.status/error_message
→ API response
→ frontend type
→ status badge
→ detail/action panel
→ operator recovery guidance
```

Confirm exactly where observability stops.

Do not reclassify the backend remediation as failed; treat this as a frontend observability gap.

### 3. Log-quality audit

Inspect logging across routes, services, repositories, background tasks, retry, calculation, and reconciliation.

For each significant log statement, assess whether it includes enough context:

- workspace ID
- payroll run ID
- employee ID/number
- period
- operation/stage
- exception type and stack trace
- correlation/request ID if available
- retry attempt or transition

Identify:

- `except Exception` blocks that log too little
- `logger.error(...)` without exception stack
- `print()` statements in production paths
- duplicate or contradictory logs
- sensitive payroll or personal data written to logs
- high-value failures logged only at debug/info
- errors emitted without durable persisted state

### 4. Exception-handling audit

Search for broad catches and failure suppression, including:

- `except Exception`
- bare `except`
- `pass`
- return of empty lists/default objects after errors
- warnings treated as success
- transaction rollback followed by normal success response
- background-task exceptions that cannot reach the initiating request
- API routes converting internal failures into misleading status codes

Classify each as:

- correct containment
- visible degraded operation
- silent failure
- plausible risk
- dead/unreachable path

### 5. Persisted error-state inventory

Inventory all persisted error/status fields and related tables, including:

- `payroll_run.status`
- `payroll_run.error_message`
- `payroll_result.status`
- `payroll_result.error_message`
- `execution_trace`
- `component_trace_jsonb`
- audit log
- event store
- reconciliation status/resolution fields
- import/upload validation records
- any batch/job status tables

For each, record:

- writer
- reader
- immutability/update semantics
- API exposure
- UI exposure
- retention
- whether the field captures cause, symptom, or both

### 6. Audit/event completeness

Compare important lifecycle transitions against audit-log and event-store writes.

Verify at minimum:

- DRAFT creation
- DRAFT → CALCULATING
- DRAFT → FAILED
- CALCULATING → CALCULATED/PARTIAL
- PARTIAL → CALCULATED/PARTIAL on retry
- approval
- lock
- paid
- reconciliation transitions
- correction/resolution actions

Identify transitions that change persisted business state without an audit or event record.

### 7. Execution-trace and component-trace usefulness

Assess whether current traces allow an operator or auditor to answer:

- which component failed
- which handler/method ran
- which input values were used
- which rule/configuration identity was used
- which eligibility/proration decision was made
- where retry differed from original run
- whether a fallback executor was used

Separate:

- trace existence
- trace completeness
- trace correctness
- trace API exposure
- trace UI exposure

### 8. Error propagation to API and UI

Trace representative failures end to end, including:

- invalid configuration
- salary-definition lock conflict
- missing employee/contract
- timesheet validation failure
- payroll run `FAILED`
- partial employee failure
- retry rejected due to legacy/incomplete snapshot
- reconciliation mismatch or failed resolution
- export failure
- permission/tenant failure

Record whether the final user-facing message is:

- specific and actionable
- accurate but generic
- misleading
- absent
- available only through direct API access

### 9. Recovery and operator guidance

For every terminal or blocked condition, determine whether the system tells the operator what to do next.

Examples:

- open a correction run
- fix employee configuration and retry
- correct timesheet input and re-upload
- contact support
- create a new payroll run
- no recovery available

Identify states where the system records an error but provides no supported recovery path.

### 10. Controlled verification

Use controlled non-production execution only where static tracing is insufficient.

Candidate checks:

- force a per-employee calculation failure and inspect all resulting signals
- force a legacy-snapshot retry rejection and inspect API/UI-facing data
- inspect `FAILED` run API response and frontend handling
- compare original-run and retry trace rows
- verify audit/event records for key transitions

Any controlled test must be self-cleaning and verify zero residue.

## Required outputs

At minimum produce:

1. Failure-surface catalogue
2. Observability-layer matrix: logs → persisted state → audit/event → trace → API → UI
3. Broad-exception and swallowed-failure register
4. Log-quality and context register
5. Persisted error-state inventory
6. Lifecycle audit/event completeness matrix
7. Original-run vs retry trace comparison
8. `04-002` statutory-identity observability recommendation
9. `02-002` retry-trace parity assessment
10. API/UI error-propagation matrix
11. Recovery-guidance register
12. Positive-control register for correctly observable failures
13. Findings using `_core/finding-schema.md`
14. Evidence under `docs/audit-program/07-silent-failures-observability/evidence/`
15. Handoff notes for Stages 08, 09, 10, 11, 12, and 13

## Finding rules

Keep separate:

- current implementation
- intended behaviour
- suspected or confirmed defect

Use exactly one valid status per finding:

- confirmed
- plausible
- unconfirmed
- rejected
- human decision required

Do not call a failure silent when it is durably persisted and operator-visible. State precisely which observability layer is missing.

Do not treat every broad exception catch as a defect; verify what the catch does and whether the resulting operation remains correct and visible.

## Constraints

- Read-only audit stage.
- Do not modify frontend or backend code.
- Do not modify migrations.
- Do not modify tests or scripts.
- Do not implement trace or logging remediation.
- Do not start Stage 08.
- Do not reopen remediated `04-001` or `05-001` without regression evidence.
- Do not expand into a full security audit; send security-relevant logging/tenant findings to Stage 09.

## Completion criteria

Stage 07 is ready for human review only when:

- all required failure surfaces are covered or explicitly marked not investigated
- every confirmed silent failure identifies the exact missing observability layers
- `04-002` has a bounded observability recommendation
- `02-002` has an evidence-backed parity assessment and any required human decision
- `FAILED` run propagation is mapped end to end
- audit/event coverage is assessed across the required transitions
- representative recovery guidance is documented
- all findings use a valid status and evidence reference
- handoffs exist for Stages 08–13 as applicable

## Publication

When the investigation is complete:

1. Create `findings.md` and the `evidence/` directory under this stage.
2. Update `docs/audit-program/audit-state.md`:
   - mark Stage 07 `in-progress`
   - set opened date to today
   - set next action to human review of Stage 07
   - preserve all completed stages and remediation records
3. Leave Stage 07 `in-progress, awaiting review`; do not self-close.
4. Commit and push only Stage 07 audit documentation/evidence and the audit-state update to `uat`.
5. Return only:

```text
Stage: 07 — Silent failures and observability
Status: in-progress, awaiting review
Primary file: docs/audit-program/07-silent-failures-observability/findings.md
Audit state: docs/audit-program/audit-state.md
Commit: <SHA>

Important decisions required:
- <decision or none>

Headline observability gaps:
- Completely silent: <count>
- Logs only: <count>
- Persisted/API but not UI: <count>
- Trace/audit gaps: <count>
```

---

## Close-review instruction

Use this section after the initial Stage 07 findings have been committed and presented for human review.

### Human decision: retry execution-trace parity

Resolve `07-005` and the inherited `02-002` decision as follows:

- Retry should produce a **defined minimal execution trace**, not full step-by-step parity with the original run and not zero trace.
- The minimum required retry trace is:
  1. one persisted row per retry invocation recording start and preflight outcome, including whether snapshot/statutory validation passed or failed;
  2. one persisted row per retried employee recording success or failure and the employee identifier;
  3. one final persisted row recording the resulting run transition (`PARTIAL → CALCULATED` or `PARTIAL → PARTIAL`).
- `component_trace_jsonb` remains the authoritative fine-grained calculation trace; `execution_trace` should cover orchestration, preflight, and outcome.
- Full duplication of all original-run persistence and batching steps is unnecessary unless Stage 10 identifies a concrete audit requirement.

Rationale: this provides enough durable evidence to reconstruct whether retry started, passed preflight, which employees were processed, and how the run ended, without duplicating every original-run orchestration step already represented elsewhere.

### Review requirements

Before closing Stage 07, verify that:

1. `07-001` is supported by the 21-site evidence and remains S1.
2. `07-002` accurately distinguishes missing unified audit/event entries from the reconciliation row's own local `notes`/`resolved_by` history.
3. `07-003` accurately identifies the outer background-task catch as logs-only with no persisted status, audit/event, API, or UI signal.
4. `07-004` remains an S3 cleanup finding.
5. `07-005` is updated from `human decision required` to `confirmed`, recording the minimal-trace decision above.
6. The `04-002` recommendation remains unchanged: add per-result `statutory_rule_id` and `statutory_version` as the primary auditable identity.
7. `04-001` and `05-001` remain remediated and are not reopened.
8. Every completion criterion above is satisfied and every finding uses one valid status.

### Close the stage

Update:

- `docs/audit-program/07-silent-failures-observability/findings.md`
  - change Stage 07 status to `complete`
  - update `07-005` to `confirmed`
  - record the defined minimal retry-trace decision
  - add the final decision and handoff summary
- `docs/audit-program/_core/human-decisions.md`
  - mark the retry trace-parity question resolved with the decision above
- `docs/audit-program/audit-state.md`
  - mark Stage 07 `complete`
  - set the closed date to today
  - set next action to open Stage 08 — Data integrity
  - leave Stage 08 not started
  - carry `07-001` to Stages 09/13
  - carry `07-002` to Stages 08/13
  - carry `07-003` to Stages 11/13
  - carry `07-004` to Stage 12
  - carry `04-002`, `02-002`, and the resolved minimal-trace specification to Stage 10
  - preserve `05-004` for Stage 13 and the completed status of prior stages/remediation

### Constraints during close review

- Do not modify frontend or backend code.
- Do not implement tracing, logging, reconciliation audit, or error-handling changes.
- Do not begin Stage 08.
- Do not create a separate close-review prompt file; this `CONTEXT.md` is the executable instruction.

### Publish

Commit and push the Stage 07 closure documentation to `uat`.

Return only:

```text
Stage: 07 — Silent failures and observability
Status: complete
Primary file: docs/audit-program/07-silent-failures-observability/findings.md
Audit state: docs/audit-program/audit-state.md
Commit: <SHA>

Decision:
- Retry execution_trace uses a defined minimal subset: invocation/preflight, per-employee outcome, and final run transition. component_trace_jsonb remains the detailed calculation trace.

Next stage:
08 — Data integrity
```
