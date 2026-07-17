# Casper Prompt — Begin Stage 05: Snapshot Integrity

Begin Stage 05 — Snapshot Integrity.

## First: verify the handoff

Read:

- `CLAUDE.md`
- `docs/audit-program/README.md`
- `docs/audit-program/WORKFLOW.md`
- `docs/audit-program/audit-state.md`
- all files in `docs/audit-program/_core/`
- `docs/audit-program/03-configuration-integrity/findings.md`
- all files in `docs/audit-program/04-original-run-retry-parity/`

Confirm:

- Stage 04 is complete.
- `04-001` is a confirmed S0 release blocker.
- The decided fix direction is snapshot-first: retry must consume frozen statutory content, never silently re-resolve mutable live statutory tables.
- Stage 05 is read-only and produces findings plus a bounded remediation specification, not code changes.
- `CLAUDE.md` is the governing instruction source.
- `docs/wrapper-command/` remains reference-only and non-authoritative.

## Create Stage 05

Create:

```text
docs/audit-program/05-snapshot-integrity/
├── CONTEXT.md
├── findings.md
└── evidence/
```

Populate `CONTEXT.md` before beginning the investigation.

Update `docs/audit-program/audit-state.md`:

- mark Stage 05 `in-progress`
- set opened date to today
- set next action to execute the Stage 05 snapshot-integrity audit
- preserve the release-blocker status and remediation timing for `04-001`

## Objective

Establish whether every snapshot used by payroll execution and retry is:

- complete
- internally consistent
- immutable where required
- created at the correct lifecycle point
- consumed by the correct execution path
- versioned or identifiable enough for audit and reproduction
- safe for legacy-run handling

Stage 05 must validate and specify the canonical snapshot-first fix for `04-001`, without modifying production code.

## Required investigation

### 1. Snapshot inventory

Inventory all snapshot mechanisms and snapshot-like persisted state, including at minimum:

- `payroll_run.rules_context_snapshot`
- `payroll_run.public_holidays_snapshot`
- `component_metadata_snapshot`
- `client_component_metadata_snapshot`
- `employee_contract_snapshot`
- `payroll_result.calculations_snapshot_json`
- `payroll_result.salary_inputs_snapshot`
- `payroll_result.per_employee_context_json`
- `payroll_result.component_trace_jsonb`
- `rule_set` / `rule_set_item`
- claimed `payroll_input` rows linked to a run
- frozen period fields on `payroll_run`
- any snapshot version fields, schema markers, IDs, or migration-era compatibility checks

For each snapshot, record:

- purpose
- writer
- exact creation point
- source tables/objects
- schema and fields
- version marker
- consumer(s)
- immutability enforcement
- validation before use
- behaviour when absent or incomplete
- legacy compatibility
- whether content is actually consumed
- evidence reference

### 2. Validate the statutory snapshot for `04-001`

Inspect the exact v2 shape of:

`payroll_run.rules_context_snapshot["statutory_rule"]`

Determine whether it contains every value retry requires, including:

- statutory rule identity
- version
- country code if required
- effective date
- complete `rules_jsonb`
- complete ordered tax-band data
- all pension, PAYE, NHF, health, levy, life-insurance and other statutory values used by the executor
- any derived or normalized fields currently constructed during live retry resolution

Produce a field-by-field comparison:

```text
Original live resolution output
vs.
frozen statutory snapshot content
vs.
retry shared-context requirements
```

Classify every field as:

- present and directly usable
- present but requires deterministic normalization
- missing
- redundant
- ambiguous

Do not assume the snapshot is sufficient merely because it contains `rules_jsonb` and tax bands. Trace every downstream read.

### 3. Define the snapshot-first retry contract

Produce a bounded remediation specification for `04-001` stating:

- the exact snapshot key and schema retry must read
- the exact live queries that must no longer occur for v2 runs
- validation rules before retry begins
- hard-fail behaviour and error wording for missing, malformed or unsupported snapshot versions
- legacy-run policy
- whether any migration/backfill is safe or whether correction runs are required
- required audit/event/trace data
- required regression tests
- acceptance criteria proving original-run/retry statutory parity

The contract must explicitly prevent fallback to live statutory tables when frozen statutory content is expected but unavailable.

### 4. Legacy-run compatibility

Classify runs into at least:

- current v2 snapshot-complete runs
- snapshot-engine runs with partial or malformed statutory content
- pre-v2 rules-context snapshots
- pre-snapshot-engine runs
- runs with a frozen date but no frozen statutory object

For each class, define the safe retry behaviour:

- allow from snapshot
- reject and require correction run
- potentially backfillable only if identity can be proven without ambiguity

Do not recommend a backfill based only on re-running the current live resolution query; that would recreate the same nondeterminism as `04-001`.

### 5. Snapshot completeness and dead content

Investigate Stage 03 finding `03-003`:

- `employee_contract_snapshot.components_jsonb` is written but never read.

Determine whether it is:

- required as an audit baseline
- intended for future diffing
- inconsistent with D1 live-salary-definition semantics
- safe to remove later
- evidence that the snapshot boundary is conceptually unclear

Also identify any other snapshot fields that are:

- written but never read
- read but never validated
- duplicated without defined precedence
- missing from retry despite being available
- only partially immutable

### 6. Snapshot timing and transactional integrity

For each snapshot, determine:

- whether it is created before, during or after run creation
- whether creation is in the same transaction as the run
- what happens if snapshot creation partially fails
- whether the run can proceed with an incomplete snapshot
- whether retry validates completeness before calculation
- whether concurrent configuration edits can occur between source resolution and snapshot persistence

Identify any time-of-check/time-of-use windows.

### 7. Immutability and mutation controls

Inspect:

- database triggers
- constraints
- application guards
- update routes
- delete/reinsert retry behaviour

Determine whether each snapshot can be altered after calculation and whether immutability applies consistently across run and result snapshots.

### 8. Statutory identity observability (`04-002`)

Assess options for making statutory identity directly auditable:

- per-run immutable statutory rule ID/version
- per-result statutory rule ID/version
- inclusion in `calculations_snapshot_json`
- inclusion in `component_trace_jsonb`
- inclusion in `execution_trace`

Recommend the minimum reliable design. Keep this separate from the core `04-001` correctness fix.

### 9. Controlled verification

Use read-only code tracing and controlled non-production inspection where needed.

You may reuse the Stage 04 reproduction data and script as evidence, but do not modify production code or implement the fix.

Any controlled execution must:

- use a local/non-production database
- be self-cleaning
- record preconditions and outputs
- verify zero residue

## Required outputs

At minimum, produce:

1. Snapshot inventory and lifecycle map
2. Snapshot writer/consumer matrix
3. Snapshot schema/version register
4. Immutability and validation matrix
5. Transaction/timing integrity assessment
6. Legacy-run compatibility matrix
7. Dead, unused or ambiguous snapshot-field register
8. Field-by-field statutory snapshot sufficiency analysis
9. Canonical snapshot-first retry contract for `04-001`
10. Bounded remediation specification and acceptance criteria
11. Statutory identity observability recommendation for `04-002`
12. Findings using `_core/finding-schema.md`
13. Evidence under the Stage 05 `evidence/` folder
14. Handoff notes for Stages 07, 08, 10, 11, 12 and the immediate post-Stage-05 remediation sprint

## Finding rules

Keep separate:

- current implementation
- intended behaviour
- suspected or confirmed defect

Use one valid status per finding:

- confirmed
- plausible
- unconfirmed
- rejected
- human decision required

Do not classify a design recommendation as a confirmed defect unless evidence demonstrates the underlying failure or risk.

## Constraints

- Read-only audit stage.
- Do not modify backend code.
- Do not modify frontend code.
- Do not modify migrations.
- Do not modify scripts or tests.
- Do not implement the `04-001` fix.
- Do not start the remediation sprint.
- Do not start Stage 06.
- Do not downgrade or re-litigate the confirmed S0 status of `04-001`.
- Do not use live statutory re-resolution as a fallback recommendation.

## Completion and publication

When complete:

1. Check every Stage 05 completion criterion.
2. Leave Stage 05 `in-progress`, awaiting human review.
3. Commit and push only the Stage 05 audit documentation and evidence to `uat`.
4. Return only:

```text
Stage: 05 — Snapshot integrity
Status: in-progress, awaiting review
Primary file: docs/audit-program/05-snapshot-integrity/findings.md
Audit state: docs/audit-program/audit-state.md
Commit: <SHA>

Important decisions required:
- <decision 1>
- <decision 2>

Remediation readiness:
- 04-001 specification ready: yes/no
- Blocking gaps: <brief list or none>
```
