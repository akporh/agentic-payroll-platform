# Stage 10 — Execution-Trace Remediation Design

**Status:** not started (see [`../audit-state.md`](../audit-state.md))

## Purpose

Produce an implementation-ready design for the platform’s execution-trace and per-result auditability gaps without changing production code.

This stage converts prior findings and human decisions into a bounded remediation specification covering:

- retry orchestration tracing
- per-result statutory identity
- omitted/disabled component visibility
- trace-route tenant isolation and authorization
- API and UI consumption requirements
- schema, repository, service, and migration impacts
- acceptance criteria and regression scenarios

This is a design stage only. It must not implement the remediation.

## Confirmed handoff state

- Stages 01–09 are complete.
- `04-001` and `05-001` are remediated and must not be reopened without regression evidence.
- `02-002` is confirmed: per-employee retry currently creates zero `execution_trace` rows.
- The `07-005` human decision is final: retry uses a **defined minimal trace subset**, not full original-run parity and not zero trace.
- Minimum retry trace:
  1. invocation/preflight outcome;
  2. one success/failure outcome per retried employee;
  3. final run-transition outcome.
- `component_trace_jsonb` remains the detailed calculation trace.
- `04-002` remains confirmed: no dedicated persisted fields identify which statutory rule/version a specific `payroll_result` used.
- Approved recommendation from Stages 05/07: add nullable `payroll_result.statutory_rule_id` and `payroll_result.statutory_version`, populated from the exact frozen statutory context used by original calculation and retry.
- `08-003` is confirmed: disabled statutory components are filtered before execution and leave no persisted trace that they were omitted.
- `09-005` is confirmed S1: the timeline route accepts `workspace_id` in the path but does not pass it into the service layer, so tenant ownership is not enforced.
- Stage 09 decisions are binding:
  - application authentication and authorization are mandatory before live/production-data use;
  - network controls are defence in depth only;
  - tenancy model is one authenticated bureau account managing multiple client workspaces through explicit membership and RBAC;
  - minimum roles: platform administrator, bureau administrator, payroll operator, payroll approver, read-only auditor/viewer;
  - direct client users are deferred, but the design must remain extensible to them.
- `03-004` remains an open product-policy question: whether statutory components may ever be disabled. Stage 10 must design traceability for omission regardless of the eventual policy decision.
- `05-004` remains deferred to Stage 13.
- `CLAUDE.md` is authoritative; `docs/wrapper-command/` is reference-only.
- Stage 10 is read-only: no code, migration, test, script, or data changes.

## Required inputs

Read before designing:

- `CLAUDE.md`
- `docs/audit-program/README.md`
- `docs/audit-program/WORKFLOW.md`
- `docs/audit-program/audit-state.md`
- all files under `docs/audit-program/_core/`
- Stage 02 findings/evidence, especially `02-002`, `02-004`, and trace baseline
- Stage 04 findings/evidence, especially `04-002`
- Stage 05 findings, especially statutory identity and snapshot sufficiency analysis
- Stage 07 findings, especially `07-005`
- Stage 08 findings, especially `08-003`
- Stage 09 findings, especially `09-005` and the authentication/RBAC decisions
- completed remediation records for `04-001 + 05-001`

## Objective

Define one coherent trace and auditability design that allows an authorized operator or auditor to answer:

1. Was this an original run or a retry?
2. Did retry preflight start, pass, or fail?
3. Which employees were selected for retry?
4. Which employees succeeded or failed?
5. What final run transition occurred?
6. Which statutory rule ID and version produced each result?
7. Which components ran, were skipped by eligibility, or were excluded by configuration?
8. Which workspace owns the run and trace?
9. Which authenticated user is authorized to view the trace?
10. Can the design support future direct-client users without weakening bureau-level isolation?

## Required design work

### 1. Current-state trace architecture

Document the existing trace stack:

- `ExecutionTracer`
- `execution_trace` schema/table
- trace repository and write semantics
- original-run `.step(...)` call sites
- retry service tracer instantiation and zero-write gap
- `component_trace_jsonb`
- `payroll_result.error_message`
- audit log/event store
- timeline API route/service/repository
- frontend timeline and component-trace views

Clearly separate:

- orchestration trace
- calculation/component trace
- lifecycle audit/event history
- per-result identity fields

### 2. Retry trace event model

Specify the minimal retry event set required by the final human decision.

At minimum define events for:

#### Retry invocation/preflight

- retry invocation started
- run eligibility/status check
- snapshot completeness validation
- statutory snapshot validation
- requested/retried employee count
- preflight passed or failed

#### Per-employee outcome

- employee selected
- employee retry started, if necessary
- employee retry succeeded
- employee retry failed
- result replacement outcome

#### Final run outcome

- result totals recomputed
- final status transition (`PARTIAL → CALCULATED` or `PARTIAL → PARTIAL`)
- retry invocation completed or failed

Avoid reproducing every original-run persistence sub-step unless it adds distinct audit value.

### 3. Trace schema and field contract

Assess whether the current `execution_trace` schema can support the design without migration.

Specify required fields, including where already present:

- trace ID
- workspace ID
- payroll run ID
- employee ID where applicable
- operation type: original run vs retry
- retry invocation/correlation ID
- step/event code
- status/outcome
- timestamp and duration
- message
- structured metadata JSON
- error class/code
- safe error message
- actor/user ID where available after authentication work

Determine whether new columns are required or whether structured metadata is sufficient.

Prefer queryable columns for high-value identifiers used for tenant scoping, filtering, and correlation. Avoid hiding all important identity in JSON.

### 4. Stable event taxonomy

Define stable machine-readable event codes and human-readable labels.

The design should include a proposed taxonomy such as:

- `RUN_CALCULATION_STARTED`
- `RUN_CALCULATION_COMPLETED`
- `RETRY_STARTED`
- `RETRY_PREFLIGHT_PASSED`
- `RETRY_PREFLIGHT_FAILED`
- `RETRY_EMPLOYEE_SUCCEEDED`
- `RETRY_EMPLOYEE_FAILED`
- `RETRY_COMPLETED`
- `RUN_STATUS_TRANSITIONED`
- `COMPONENT_EXCLUDED_BY_CONFIGURATION`

Do not rely only on free-text messages for semantics.

Specify versioning/extension rules so future events can be added without breaking existing consumers.

### 5. Retry correlation and idempotency

Design how multiple retry attempts on the same run are distinguished.

Specify:

- retry invocation/correlation ID generation
- whether each API retry request gets one invocation ID
- how per-employee rows link to it
- how duplicate client requests are detected or represented
- whether failed preflight attempts are persisted
- whether repeated retries remain append-only
- ordering guarantees

### 6. Error and failure semantics

Define which failures must generate durable trace rows:

- invalid run status
- incomplete snapshot
- invalid statutory snapshot
- employee no longer retryable
- result replacement failure
- result persistence failure
- total recomputation failure
- final transition failure

Specify what happens if trace persistence itself fails.

Preserve the existing principle that trace failure must not corrupt payroll calculation, but design a compensating observability signal such as structured server logging/metrics for trace-write failures.

Do not return raw `str(e)` details to clients.

### 7. Per-result statutory identity (`04-002`)

Produce the implementation design for:

- `payroll_result.statutory_rule_id UUID NULL`
- `payroll_result.statutory_version INTEGER NULL`

Specify:

- migration and backfill policy
- original-run insert call sites
- retry insert call sites
- source of values: exact frozen `rules_context_snapshot["statutory_rule"]` used by the calculation
- null semantics for legacy results and non-statutory jurisdictions/configurations
- API exposure
- UI/audit display
- indexing requirements
- validation and consistency checks against the run snapshot
- immutability requirements

Legacy rows must not be backfilled from mutable current statutory tables. Define them as unknown/unavailable unless frozen historical evidence proves identity.

### 8. Disabled/excluded component visibility (`08-003`)

Design how a run records components excluded before execution.

Distinguish:

- excluded because disabled by workspace/client override
- skipped because eligibility condition evaluated false
- absent because component is not part of the applicable configuration
- executed and returned zero
- executed and failed

Assess whether exclusion should be represented in:

- `component_trace_jsonb`
- `execution_trace`
- a run-level configuration snapshot/header
- a dedicated excluded-components field/table

Recommend the smallest design that creates an unambiguous, durable record without duplicating all component metadata.

The design must work whether Stage 13 ultimately forbids statutory disablement or permits it under controlled policy.

### 9. Original-run and retry trace relationship

Define the expected relationship between:

- original-run `execution_trace`
- retry `execution_trace`
- original result `component_trace_jsonb`
- retried result `component_trace_jsonb`
- audit log/event store

Specify what an operator should see as one timeline versus separate attempts.

Determine whether retry rows should appear in the existing timeline endpoint by default and how they should be grouped.

### 10. Tenant isolation and authorization (`09-005`)

Design the secure timeline/trace access contract.

At minimum:

- authenticated user required
- bureau account membership verified
- workspace membership/entitlement verified
- run ownership verified against path workspace
- service method accepts workspace/account authorization context
- repository query scopes by both run ID and workspace ID
- direct child IDs never bypass parent ownership checks
- read-only auditor/viewer may view traces
- payroll operator and approver may view traces
- platform administrator access is explicit and auditable
- future direct-client users can only view their permitted workspace

The trace route must not trust `workspace_id` merely because it appears in the path.

Specify expected responses:

- unauthenticated: `401`
- authenticated but unauthorized: `403` or a deliberately chosen non-disclosing `404`
- resource absent within authorized scope: `404`

Record the chosen resource-concealment policy if one is needed.

### 11. API contract design

Specify request/response contracts for:

- timeline retrieval
- filtering by attempt/invocation, employee, event code, status, and time
- pagination and deterministic ordering
- retry invocation summary
- per-result statutory identity
- excluded component display

Define backward compatibility for existing frontend consumers.

No raw exception or internal stack/schema information may be returned.

### 12. UI/operator experience design

Define the minimum UI changes required later, without implementing them:

- timeline grouping by original run and retry invocation
- preflight failure display
- per-employee retry outcomes
- final retry transition summary
- statutory rule ID/version display in result audit detail
- excluded/disabled component indicators
- role-based trace visibility
- clear empty states for legacy runs with unavailable trace/identity

Do not turn Stage 10 into a general UI redesign.

### 13. Audit/event boundary

Define which information belongs in:

- `execution_trace`
- `component_trace_jsonb`
- `audit_log`
- `event_store`
- `payroll_result` identity fields

Avoid duplicate writes with unclear ownership.

Recommended boundary to assess:

- execution trace: orchestration and attempt outcomes
- component trace: calculation decisions and component values
- audit log: human/business lifecycle actions and before/after state
- event store: domain events/integration history
- result columns: durable queryable calculation identity

### 14. Migration and rollout design

Produce a migration/rollout sequence covering:

- schema additions if required
- compatibility with legacy runs/results
- application writes before reads, where relevant
- dual-read/dual-write requirements, if any
- API versioning or additive response changes
- frontend deployment order
- authentication/RBAC dependency from Stage 09
- rollback strategy
- data-retention considerations

Stage 10 must explicitly state that trace-route remediation cannot be considered production-safe until Stage 09’s authentication, membership, RBAC, and ownership controls exist.

### 15. Acceptance criteria

Define testable acceptance criteria for the future implementation.

At minimum:

- retry invocation writes a correlated preflight event
- failed preflight is durably visible
- each retried employee has one terminal success/failure outcome event
- final run transition is recorded
- component trace remains detailed and correct
- result rows record statutory rule ID/version from the frozen snapshot
- legacy results do not fabricate statutory identity from live data
- disabled/excluded components are distinguishable from zero-result or eligibility-skip components
- timeline query cannot return another workspace’s rows
- unauthorized users cannot access timeline data
- timeline output is ordered, paginated, and stable
- trace-write failure does not corrupt payroll calculation
- API errors are sanitized

### 16. Regression scenario design

Define scenarios for Stage 11, including:

- successful retry with one employee
- retry with multiple employees, mixed success/failure
- preflight failure due to legacy/incomplete snapshot
- statutory snapshot validation failure
- repeated retry attempts on the same run
- original-run vs retry timeline grouping
- statutory identity parity between original and retry results
- disabled statutory component recorded as excluded
- cross-workspace timeline request denied
- read-only auditor allowed to view authorized trace
- unauthorized direct-client user denied
- trace-write failure containment

## Required outputs

At minimum produce:

1. Current-state trace architecture map
2. Retry event model
3. Execution-trace schema assessment
4. Stable event taxonomy
5. Retry correlation/idempotency design
6. Error/failure trace semantics
7. `04-002` per-result statutory-identity design
8. `08-003` excluded-component visibility design
9. Original-run/retry relationship design
10. `09-005` secure timeline access design
11. API contract specification
12. Minimal UI/operator requirements
13. Audit/event ownership boundary
14. Migration and rollout sequence
15. Acceptance criteria
16. Stage 11 regression scenario specification
17. Risks, trade-offs, and alternatives considered
18. Findings/design decisions using the audit programme’s schemas
19. Evidence under `docs/audit-program/10-execution-trace-remediation-design/evidence/`
20. Handoff notes for Stages 11, 12, and 13

## Finding and design rules

Keep separate:

- current implementation
- approved decisions
- proposed design
- alternatives rejected
- unresolved human decisions

Use one valid finding status where findings are recorded:

- confirmed
- plausible
- unconfirmed
- rejected
- human decision required

Do not redesign the entire observability architecture when a smaller additive change satisfies the approved requirements.

Do not store critical tenant or result identity only inside unindexed free-form JSON.

Do not fabricate historical statutory identity for legacy results.

Do not treat network controls as authorization.

## Constraints

- Findings and design only.
- No backend or frontend code changes.
- No migrations created or edited.
- No tests or scripts changed.
- No data modification.
- Do not start Stage 11.
- Do not reopen `04-001` or `05-001` without regression evidence.
- Do not resolve `03-004`’s product-policy decision; design omission traceability for either outcome.
- Do not design trace access without application authentication, membership, RBAC, and ownership checks.

## Completion criteria

Stage 10 is ready for human review only when:

- the approved minimal retry-trace decision is fully specified
- the existing trace schema is assessed and any additions are justified
- retry event codes, correlation, ordering, and failure semantics are defined
- `04-002` has an implementation-ready per-result identity design
- `08-003` has a durable excluded-component visibility design
- `09-005` has an end-to-end tenant-safe route/service/repository design
- authentication/RBAC dependencies are explicit
- API/UI impacts and migration order are defined
- acceptance criteria are testable
- Stage 11 regression scenarios are specified
- trade-offs and rejected alternatives are documented
- any genuinely unresolved decision is clearly isolated

## Publication

When the design is complete:

1. Create `findings.md` and supporting design/evidence files under this stage.
2. Update `docs/audit-program/audit-state.md`:
   - mark Stage 10 `in-progress`
   - set opened date to today
   - set next action to human review of Stage 10
   - preserve all completed stages, decisions, and remediation records
3. Leave Stage 10 `in-progress, awaiting review`; do not self-close.
4. Commit and push only Stage 10 documentation/evidence and the audit-state update to `uat`.
5. Return only:

```text
Stage: 10 — Execution-trace remediation design
Status: in-progress, awaiting review
Primary file: docs/audit-program/10-execution-trace-remediation-design/findings.md
Audit state: docs/audit-program/audit-state.md
Commit: <SHA>

Important decisions required:
- <decision or none>

Design summary:
- Retry trace model: <summary>
- Per-result statutory identity: <summary>
- Excluded-component visibility: <summary>
- Tenant-safe timeline access: <summary>
```
