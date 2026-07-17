# Stage 10 — Execution-Trace Remediation Design

**Status:** in-progress (see [`../audit-state.md`](../audit-state.md))

## Purpose

Produce an implementation-ready, read-only remediation design covering:

- minimal retry orchestration tracing
- per-result statutory identity (`04-002`)
- disabled/excluded component visibility (`08-003`)
- tenant-safe timeline access (`09-005`)
- API/UI contracts, migration sequencing, acceptance criteria, and Stage 11 scenarios

No production code, migration, test, script, or data change is permitted in this stage.

## Binding inputs and decisions

- Stages 01–09 are complete.
- `04-001` and `05-001` remain remediated and are not reopened.
- `02-002` is confirmed: retry currently writes zero `execution_trace` rows.
- `07-005` is final: retry uses a **defined minimal trace subset**, not full original-run parity and not zero trace:
  1. invocation/preflight outcome;
  2. one terminal success/failure outcome per retried employee;
  3. final run-transition outcome.
- `component_trace_jsonb` remains the detailed calculation trace.
- `04-002` requires nullable per-result `statutory_rule_id` and `statutory_version`, sourced from the exact frozen statutory context used by the calculation.
- `08-003` requires a durable distinction between excluded-by-configuration, skipped-by-eligibility, absent, executed-zero, and executed-failed.
- `09-005` requires tenant-safe trace access.
- Stage 09 decisions are binding:
  - application authentication and authorization are mandatory before live/production use;
  - network controls are defence in depth only;
  - one authenticated bureau account manages multiple client workspaces through explicit membership and RBAC;
  - minimum roles: platform administrator, bureau administrator, payroll operator, payroll approver, read-only auditor/viewer;
  - direct client users are deferred but the design must remain extensible to them.
- `03-004` remains an open product-policy question; Stage 10 is policy-neutral and designs visibility regardless of whether statutory disablement is later forbidden or controlled.
- `05-004` remains deferred to Stage 13.

## Approved Stage 10 design

The implementation design in `findings.md` is the canonical output. The following decisions are accepted for close review.

### Retry event model

Use one `invocation_id` per retry API call and persist:

- `RETRY_INVOCATION_STARTED`
- run-status and snapshot/statutory preflight checks
- `RETRY_PREFLIGHT_PASSED` or `RETRY_PREFLIGHT_FAILED`
- exactly one `RETRY_EMPLOYEE_SUCCEEDED` or `RETRY_EMPLOYEE_FAILED` row per retried employee
- totals recomputation outcome
- `RUN_STATUS_TRANSITIONED`
- `RETRY_COMPLETED` or `RETRY_FAILED`

Do not duplicate every original-run persistence step.

### Execution-trace schema

Extend `execution_trace` with queryable columns for:

- `workspace_id`
- `event_code`
- `operation_type`
- `invocation_id`
- `employee_id`
- `actor_id`
- `metadata_jsonb`
- `error_class`

Retain existing human-readable fields. Critical tenant/correlation identity must not exist only inside JSON.

Use additive, stable event codes. Existing consumers must tolerate unknown future codes.

### Error semantics

Trace-write failure must never corrupt or reverse payroll execution. It must emit structured server-side logging and a metric where supported.

No API or trace field may expose uncontrolled `str(e)`, SQL, stack traces, schema, or constraint detail.

### Per-result statutory identity

Add nullable:

- `payroll_result.statutory_rule_id UUID`
- `payroll_result.statutory_version INTEGER`

Populate both for original runs and retries from the exact frozen statutory snapshot used by calculation.

Existing rows remain NULL by default. Do not backfill from mutable live statutory tables. NULL means “not recorded/unknown”, not “no statutory deduction applied”.

Expose both additively through the existing results API and result audit detail UI.

### Excluded component visibility

Extend `component_trace_jsonb` so configured-but-disabled components receive `outcome: excluded_by_configuration`, while eligibility skips, absent components, executed-zero, and executed-failed remain distinguishable.

Add one run-level `COMPONENT_EXCLUDED_BY_CONFIGURATION` execution-trace row per distinct excluded component per run, not per employee.

### Original-run/retry relationship

Keep one unified timeline per payroll run, grouped by:

- original run
- each retry invocation

`component_trace_jsonb` remains attached to the currently persisted employee result. `execution_trace` preserves attempt history.

### Tenant-safe timeline access

Target request chain:

```text
authenticated principal
→ bureau account and role
→ workspace membership/entitlement
→ run ownership check
→ query scoped by workspace_id + run_id
```

The route/service/repository must all carry `workspace_id`; child filters never bypass the parent ownership check.

Use:

- `401` for no valid identity
- non-disclosing `404` for absent or unauthorized run/workspace combinations

Read-only auditor/viewer, payroll operator, and payroll approver may view authorized traces. Platform-administrator access must be explicit and audited.

This route is not production-secure until Stage 09 authentication, membership, RBAC, and ownership controls exist.

### API/UI design

Keep the existing timeline route and add optional filters for invocation, operation type, employee, event code, status, time range, cursor, and limit.

Use deterministic ordering `(created_at, id)`.

Add a derived retry-invocation summary endpoint over the same trace source of truth.

UI requirements are limited to grouping attempts, showing preflight failures, per-employee outcomes, final transition summaries, statutory identity, excluded-component states, and explicit legacy empty states.

### Migration and rollout

Use additive schema changes and safe backfills only:

1. add nullable trace columns;
2. backfill `workspace_id` from `payroll_run` and validate before applying NOT NULL;
3. backfill legacy `event_code` from known step mappings with `UNKNOWN_LEGACY_STEP` fallback;
4. add nullable statutory identity columns with no automatic legacy backfill;
5. deploy writes before dependent UI reads;
6. keep API changes additive;
7. deploy trace authorization only after Stage 09 authentication/RBAC foundations exist.

## Required future acceptance criteria

The future implementation must verify at minimum:

- correlated retry preflight events
- durable failed-preflight evidence with zero employee mutation
- one terminal outcome per retried employee
- final run-transition trace
- unchanged correct component tracing
- statutory identity parity between run snapshot and every new result
- no fabricated legacy identity
- excluded components distinguishable from skipped/zero/failed
- cross-workspace timeline requests denied after authentication work
- stable attempt grouping and ordering
- trace-write failure containment
- no raw exception/internal detail in API responses

## Stage 11 handoff

Stage 11 should use the 12 scenarios specified in `findings.md`, including successful/mixed retry, failed preflight, repeated attempts, grouping, statutory identity parity, excluded-component visibility, tenant denial, authorized auditor access, and trace-write failure containment.

---

## Close-review instruction

No new human decision is required to close Stage 10.

### Review requirements

Before closing, verify that:

1. the design implements the binding minimal retry-trace decision without expanding to full parity;
2. `execution_trace` gains queryable tenant, correlation, operation, event, employee, and actor fields;
3. per-result statutory identity is sourced only from the frozen calculation context;
4. existing result rows are not backfilled from mutable live tables;
5. excluded components are durably distinguishable from skipped, absent, zero, and failed components;
6. the timeline design closes `09-005` only when Stage 09 authentication/membership/RBAC dependencies are present;
7. authorization uses non-disclosing `404` for unauthorized resource combinations;
8. error semantics prohibit uncontrolled `str(e)` disclosure;
9. migration, rollback, API compatibility, UI requirements, acceptance criteria, and Stage 11 scenarios are implementation-ready;
10. Stage 10 remains design-only and no production files were changed.

### Close the stage

Update:

- `docs/audit-program/10-execution-trace-remediation-design/findings.md`
  - change status to `complete`
  - add a final review/closure summary
  - preserve the proposed design as the approved implementation specification
- `docs/audit-program/audit-state.md`
  - mark Stage 10 `complete`
  - set the closed date to today
  - set next action to open Stage 11 — Scenario testing
  - leave Stage 11 not started
  - carry the approved trace package (`02-002`/`07-005`, `04-002`, `08-003`, `09-005`) to Stage 13 for sequencing and implementation
  - carry the 12 regression scenarios to Stage 11
  - preserve the Stage 09 S0 authentication/RBAC dependency and all prior findings/remediation state

### Constraints during close review

- Do not modify backend/frontend code, migrations, tests, scripts, or data.
- Do not implement the trace design.
- Do not begin Stage 11.
- Do not create a separate close-review prompt file; this `CONTEXT.md` is the executable instruction.

### Publish

Commit and push the Stage 10 closure documentation to `uat`.

Return only:

```text
Stage: 10 — Execution-trace remediation design
Status: complete
Primary file: docs/audit-program/10-execution-trace-remediation-design/findings.md
Audit state: docs/audit-program/audit-state.md
Commit: <SHA>

Result:
- Minimal retry trace design approved.
- Per-result statutory identity design approved.
- Excluded-component visibility design approved.
- Tenant-safe timeline design approved, dependent on Stage 09 authentication/RBAC remediation.

Next stage:
11 — Scenario testing
```
