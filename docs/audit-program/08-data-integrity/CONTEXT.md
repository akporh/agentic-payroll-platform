# Stage 08 — Data Integrity

**Status:** not started (see [`../audit-state.md`](../audit-state.md))

## Purpose

Determine whether persisted payroll data remains internally consistent, complete, correctly scoped, and reproducible across onboarding, configuration, employee/employment data, payroll inputs, calculations, retries, reconciliation, approval, locking, and payment.

This stage must distinguish between:

- data that is incorrect
- data that is internally contradictory
- data that is missing but required
- data that is duplicated without a defined source of truth
- data that is stale relative to runtime behaviour
- data that is valid but operationally unreachable
- data that is intentionally denormalized with clear precedence
- historical data that cannot be reconstructed reliably

The focus is persisted business integrity, not UI design, trace design, or full security review.

## Confirmed handoff state

- Stages 01–07 are complete.
- `04-001` and `05-001` are remediated and must not be reopened without regression evidence.
- `04-004` remains unconfirmed: reconciliation refresh after retry completion was not traced in Stage 04.
- `03-004` remains open: statutory-deduction components can be disabled per workspace while D-ARCH-2 is not enforced.
- `06-002` is confirmed: `pay_cycle.definition_json` affects runtime but is unavailable for post-onboarding view or edit.
- `07-002` is confirmed: reconciliation create/resolve writes no unified `audit_log`/`event_store` entry, though reconciliation-local fields exist.
- `04-002` and the minimal retry-trace decision belong to Stage 10, not Stage 08.
- `07-001` belongs to Stages 09/13.
- `05-004` remains deferred to Stage 13.
- `CLAUDE.md` is authoritative; `docs/wrapper-command/` is reference-only.
- Stage 08 is read-only: no backend, frontend, migration, test, script, or data-remediation changes.

## Required inputs

Read before investigation:

- `CLAUDE.md`
- `docs/audit-program/README.md`
- `docs/audit-program/WORKFLOW.md`
- `docs/audit-program/audit-state.md`
- all files under `docs/audit-program/_core/`
- Stage 01 findings and data-model inventory
- Stage 02 findings and diagnostic baseline
- Stage 03 findings, especially `03-001`, `03-003`, and `03-004`
- Stage 04 findings, especially `04-004`
- Stage 05 findings and remediation records
- Stage 06 findings, especially `06-002`
- Stage 07 findings, especially `07-002`

## Objective

Establish whether the platform can guarantee that:

1. every persisted payroll value has one authoritative source or an explicit precedence rule;
2. every run references the correct workspace, period, employee, contract, configuration, inputs, rule set, and statutory context;
3. retries and reconciliation preserve consistency with the original run;
4. lifecycle transitions do not leave orphaned, contradictory, duplicate, or partially committed rows;
5. approved, locked, and paid runs are immutable in all financially relevant fields;
6. tenant-scoped records cannot be accidentally cross-linked through missing relational constraints;
7. historical payroll state can be reconstructed from persisted records without relying on mutable live configuration.

## Required investigation

### 1. Build the data-integrity invariant catalogue

Inventory the key invariants across at least:

- account/workspace ownership
- workspace lifecycle status
- pay-cycle uniqueness and period definition
- employee uniqueness and status
- employment/contract date ranges and overlap
- grade/designation/salary-definition relationships
- salary components and component metadata
- client component overrides
- rule sets and rule-set items
- statutory rules and tax bands
- payroll inputs and run claims
- payroll runs and statuses
- payroll results and retry replacement behaviour
- snapshots
- reconciliation
- approval/lock/payment records
- audit/event records

For each invariant record:

- business rule
- database constraint/trigger
- application guard
- writer(s)
- reader(s)
- known bypass paths
- current evidence
- integrity status

### 2. Reconciliation integrity and retry parity (`04-004`)

Trace reconciliation behaviour across:

- original run calculation
- creation of a reconciliation row
- transition to `MATCHED` or `MISMATCH`
- retry of failed employees
- recomputation of payroll totals
- refresh or non-refresh of `expected_total`, `actual_total`, difference, and status
- resolution of mismatches
- approval/lock/payment after reconciliation

Determine whether retry completion:

- automatically recalculates reconciliation
- leaves a stale reconciliation row
- prevents approval until refreshed
- allows approval against outdated totals
- creates duplicates
- updates resolved reconciliation incorrectly

Use controlled non-production execution if static tracing cannot prove the result.

Classify `04-004` as confirmed, rejected, plausible, or unconfirmed with evidence.

### 3. Statutory-component enforcement (`03-004` / D-ARCH-2)

Inspect whether required statutory deductions can be disabled or bypassed through:

- `component_metadata.is_active`
- `client_component_metadata.is_active`
- component overrides
- salary-definition composition
- handler registration
- rule-set eligibility
- onboarding/configuration APIs
- direct database state

Determine:

- which components are legally/architecturally mandatory
- whether the engine skips disabled statutory components
- whether any current workspace has them disabled
- whether configuration save routes reject this
- whether the UI prevents it
- whether a run records that a statutory component was omitted

Do not make a legal-compliance conclusion beyond documented product rules; record compliance-policy questions for Stage 13 where required.

### 4. `pay_cycle.definition_json` integrity (`06-002`)

Determine whether existing persisted `definition_json` values are:

- present where expected
- schema-consistent
- aligned with `frequency`, `run_day`, `cutoff_day`, and `payment_day`
- consumed deterministically by the payroll engine
- duplicated by dedicated columns with a defined precedence rule
- stale or contradictory in any observed workspace

Assess whether the inability to view/edit this field creates an actual integrity risk or only a configurability gap.

If using local/non-production data, summarize counts and anomalies without treating test data as production evidence.

### 5. Employee and employment temporal integrity

Revisit known contract risks and verify current implementation for:

- unique employee number per workspace
- nullable employee numbers
- employee status vs active contract state
- overlapping employment contracts
- open-ended contracts
- start/end date validation
- multiple contracts effective in one pay period
- contract selection precedence
- terminated employees included/excluded correctly
- joiner/leaver proration source dates

Determine whether database constraints, application validation, and payroll selection logic agree.

### 6. Referential and tenant consistency

Inspect foreign keys and query joins for records that carry both a direct workspace ID and a linked parent that also implies workspace ownership.

Examples:

- employee ↔ workspace
- employee_contract ↔ employee/salary_definition/grade/designation
- payroll_run ↔ workspace/pay_cycle/rule_set
- payroll_result ↔ payroll_run/employee
- payroll_input ↔ workspace/employee/payroll_run
- reconciliation ↔ payroll_run/workspace
- snapshot tables ↔ payroll_run/employee

Identify whether the schema permits cross-workspace combinations even when API queries usually prevent them.

This is relational data integrity; security exploitation analysis belongs to Stage 09.

### 7. Payroll-input integrity

Verify:

- uniqueness/idempotency of imported inputs
- claimed/unclaimed transitions
- whether an input can be linked to multiple runs
- whether retry reuses the same claimed inputs
- negative/invalid value guards
- arrears/reference-period semantics
- employee existence validation
- duplicate upload handling
- transaction behaviour if only part of a batch fails
- orphaned claims after failed/aborted runs

Pay special attention to the new `FAILED` run path and whether snapshot failure or outer background failure can leave inputs claimed or partially persisted.

### 8. Payroll-result integrity

Inspect:

- uniqueness of `(payroll_run_id, employee_id)`
- retry DELETE+INSERT behaviour
- status/result consistency
- financial totals vs snapshot JSON
- Decimal precision and rounding persistence
- `gross_pay`, deductions, tax, and `net_pay` arithmetic invariants
- failed-result rows containing partial financial values
- run totals matching sum of successful employee results
- stale aggregates after retry
- result immutability after approval/lock/payment

Use targeted SQL or controlled test scenarios where useful.

### 9. Run lifecycle and partial-commit integrity

For each major transition, determine whether all related writes are atomic:

- run creation and initial snapshots
- DRAFT → CALCULATING
- employee result persistence
- run total/status update
- audit/event writes
- input claiming
- retry result replacement
- reconciliation update
- approval
- locking
- payment

Identify transactions that can leave:

- status advanced without results
- results written without totals
- inputs claimed without results
- audit/event missing while state changed
- reconciliation stale while run changed
- partial success hidden as complete

### 10. Immutability after approval, lock, and payment

Verify database and application protections for:

- payroll_run totals and period fields
- payroll_result financial fields and snapshots
- payroll inputs linked to the run
- reconciliation rows
- snapshot tables
- approval/lock/payment metadata

Determine whether any route, repository method, or direct SQL path can mutate financially relevant data after the lifecycle should make it immutable.

Carry broad snapshot-trigger harmonisation (`05-004`) to Stage 13 unless this stage finds an active mutation path.

### 11. Duplicate source-of-truth and precedence audit

Search for fields represented in multiple places, including:

- `proration_strategy` column vs override JSON
- `is_active` column vs override JSON
- pay-cycle dedicated columns vs `definition_json`
- salary-definition live content vs snapshot content
- run-level totals vs sum of result rows
- statutory identity in run snapshot vs missing per-result identity
- reconciliation totals vs payroll-run/result totals

For each duplication, classify:

- intentional with enforced precedence
- intentional but unenforced
- stale-risk
- dead storage
- ambiguous source of truth

### 12. Historical reproducibility

Determine whether an auditor can reconstruct a past run using persisted data only.

Assess availability and sufficiency of:

- frozen period
- employee/contract snapshot
- salary input snapshot
- component metadata snapshots
- client override snapshots
- rule-set snapshot
- statutory snapshot
- public holiday snapshot
- payroll inputs
- calculation/component trace
- result totals
- reconciliation history

List any mutable live dependency still required to explain a historical run.

### 13. Controlled verification

Use local/non-production data only where static analysis is insufficient.

Candidate scenarios:

- retry a `PARTIAL` run with an existing reconciliation and compare before/after reconciliation values
- attempt to disable a statutory component and trace calculation outcome
- create overlapping contracts and observe validation/selection
- force failure after input claiming and inspect residue
- compare run totals to employee-result sums
- test mutation attempts after `APPROVED`, `LOCKED`, or `PAID`

Every controlled test must:

- be self-cleaning
- record preconditions and outputs
- verify zero residue
- avoid production/shared data

## Required outputs

At minimum produce:

1. Data-integrity invariant catalogue
2. Constraint/guard coverage matrix
3. Reconciliation lifecycle and retry-parity assessment
4. `04-004` final classification
5. Statutory-component enforcement assessment for `03-004`
6. `pay_cycle.definition_json` consistency assessment
7. Employee/contract temporal-integrity matrix
8. Referential and cross-workspace consistency register
9. Payroll-input lifecycle matrix
10. Payroll-result arithmetic and uniqueness assessment
11. Transaction/partial-commit matrix
12. Approval/lock/payment immutability matrix
13. Duplicate-source-of-truth and precedence register
14. Historical-reproducibility assessment
15. Positive-control register for correctly enforced invariants
16. Findings using `_core/finding-schema.md`
17. Evidence under `docs/audit-program/08-data-integrity/evidence/`
18. Handoff notes for Stages 09, 10, 11, 12, and 13

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

Do not classify the absence of a UI editor as a data-integrity defect unless persisted values are shown to be wrong, contradictory, or uncorrectable in a way that affects runtime correctness.

Do not classify denormalization as a defect when precedence is explicit, consistently enforced, and tested.

Do not treat local development-data anomalies as production facts. Use them as evidence of schema-permitted states or test coverage gaps only.

## Constraints

- Read-only audit stage.
- Do not modify backend or frontend code.
- Do not modify migrations.
- Do not modify tests or scripts.
- Do not repair data.
- Do not start Stage 09.
- Do not reopen remediated `04-001` or `05-001` without regression evidence.
- Do not expand into full security analysis; record tenant-integrity handoffs for Stage 09.
- Do not implement broad immutability remediation (`05-004`).

## Completion criteria

Stage 08 is ready for human review only when:

- all required invariant domains are covered or explicitly marked not investigated
- `04-004` is evidence-backed and classified
- `03-004` has an evidence-backed enforcement assessment
- reconciliation integrity across retry is resolved
- input/result/run transaction boundaries are mapped
- employee/contract temporal integrity is assessed
- duplicate sources of truth have explicit classifications
- post-approval/lock/payment mutation protections are assessed
- historical reproducibility is assessed from persisted data only
- every finding uses a valid status and evidence reference
- handoffs exist for Stages 09–13 as applicable

## Publication

When the investigation is complete:

1. Create `findings.md` and the `evidence/` directory under this stage.
2. Update `docs/audit-program/audit-state.md`:
   - mark Stage 08 `in-progress`
   - set opened date to today
   - set next action to human review of Stage 08
   - preserve all completed stages and remediation records
3. Leave Stage 08 `in-progress, awaiting review`; do not self-close.
4. Commit and push only Stage 08 audit documentation/evidence and the audit-state update to `uat`.
5. Return only:

```text
Stage: 08 — Data integrity
Status: in-progress, awaiting review
Primary file: docs/audit-program/08-data-integrity/findings.md
Audit state: docs/audit-program/audit-state.md
Commit: <SHA>

Important decisions required:
- <decision or none>

Headline integrity gaps:
- Confirmed financial/data-integrity defects: <count>
- Reconciliation gaps: <count>
- Temporal/referential gaps: <count>
- Historical-reproducibility gaps: <count>
```
