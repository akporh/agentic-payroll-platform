# Stage 08 — Data Integrity

**Status:** in-progress (see [`../audit-state.md`](../audit-state.md))

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
- `04-004` entered this stage unconfirmed and is resolved by the findings as rejected.
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

Trace reconciliation behaviour across original calculation, retry, approval, locking, reconciliation creation/resolution, and payment. Determine whether retry can coexist with an existing reconciliation row or create stale reconciliation totals.

### 3. Statutory-component enforcement (`03-004` / D-ARCH-2)

Inspect whether required statutory deductions can be disabled or bypassed through metadata, overrides, salary composition, handler registration, rule eligibility, APIs, UI, or direct persisted state. Determine whether omission is recorded anywhere.

### 4. `pay_cycle.definition_json` integrity (`06-002`)

Determine whether persisted values are present, schema-consistent, aligned with dedicated pay-cycle columns, deterministically consumed, and free from stale or contradictory states.

### 5. Employee and employment temporal integrity

Verify employee-number uniqueness/nullability, overlapping and open-ended contracts, contract selection precedence, employment status alignment, and joiner/leaver date use.

### 6. Referential and tenant consistency

Inspect foreign keys and joins for schema-permitted cross-workspace combinations. Keep exploitation analysis for Stage 09.

### 7. Payroll-input integrity

Verify uniqueness, claiming, retry reuse, invalid-value guards, duplicate uploads, batch transaction behaviour, and orphaned claims after failed runs.

### 8. Payroll-result integrity

Inspect result uniqueness, retry replacement, arithmetic, precision, run-total derivation, failed-result values, stale aggregates, and immutability.

### 9. Run lifecycle and partial-commit integrity

Map transaction boundaries across snapshots, status transitions, results, totals, inputs, audit/events, retry, reconciliation, approval, lock, and payment.

### 10. Immutability after approval, lock, and payment

Verify protections for run totals/periods, result fields, inputs, reconciliation, snapshots, and lifecycle metadata. Keep broad snapshot-trigger harmonisation (`05-004`) deferred unless an active mutation path is found.

### 11. Duplicate source-of-truth and precedence audit

Classify duplicated representations as intentional/enforced, intentional/unenforced, stale-risk, dead storage, or ambiguous.

### 12. Historical reproducibility

Determine whether past runs can be reconstructed using persisted state only, and list any remaining mutable live dependencies.

### 13. Controlled verification

Use self-cleaning local/non-production checks only where static analysis is insufficient. Verify zero residue.

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

When the investigation is complete, create `findings.md` and evidence, update audit state to `in-progress`, and leave the stage awaiting review.

---

## Close-review instruction

Use this section after the initial Stage 08 findings have been committed and presented for human review.

### Review conclusion

No new human decision is required to close Stage 08.

Accept the following conclusions:

- `04-004` is **rejected**. Retry is only available for `PARTIAL` runs; reconciliation is only available for `LOCKED` runs reached through `CALCULATED → APPROVED → LOCKED`. The two operations cannot overlap for the same run, so retry cannot leave an existing reconciliation stale.
- `08-001` is confirmed S2: `employee.employee_number` remains nullable because migration `c9d0e1f2a3b4` swallows any `SET NOT NULL` failure with `EXCEPTION WHEN others THEN NULL`. The local development rows demonstrate the schema-permitted state, not production prevalence.
- `08-002` is confirmed S2: `payroll_run` totals and period fields lack DB-level immutability until `PAID`; no active application mutation path was found for `APPROVED` or `LOCKED`, so this is a defence-in-depth gap.
- `08-003` is confirmed S2: disabled statutory components are removed before execution with no class-aware guard and no trace/audit signal that a mandatory component was omitted. The underlying policy question from `03-004` remains open; do not resolve it in Stage 08.
- No financial miscalculation, stale aggregate, reconciliation corruption, contract-overlap gap, or new historical-reproducibility defect was found.

### Review requirements

Before closing Stage 08, verify that:

1. the `04-004` rejection cites the complete lifecycle chain and all redundant guards;
2. `08-001` clearly distinguishes a confirmed schema defect from local-development prevalence;
3. `08-002` does not claim an active exploit or application mutation path that was not found;
4. `08-003` distinguishes correct mechanical engine behaviour from the missing compliance/observability guard;
5. the positive controls remain recorded: contract overlap, active-contract uniqueness, result uniqueness/immutability, reconciliation checks, and payroll-input constraints;
6. `03-004` remains an open human decision for later policy/backlog resolution;
7. `04-001` and `05-001` remain remediated and are not reopened;
8. all completion criteria are satisfied and each finding uses one valid status.

### Close the stage

Update:

- `docs/audit-program/08-data-integrity/findings.md`
  - change Stage 08 status to `complete`
  - preserve `04-004` as `rejected`
  - add a final review/closure summary
- `docs/audit-program/audit-state.md`
  - mark Stage 08 `complete`
  - set the closed date to today
  - set next action to open Stage 09 — Security and tenant isolation
  - leave Stage 09 not started
  - mark `04-004` closed/rejected with no remediation required
  - carry `08-001` and `08-002` to Stages 11/13
  - carry `08-003` to Stages 09/10/13 and preserve the open `03-004` policy decision
  - carry `07-002` to Stage 13 as an audit-consistency issue; do not reinterpret it as reconciliation data corruption
  - preserve `04-002` and the minimal retry-trace design for Stage 10
  - preserve `05-004` for Stage 13
  - preserve all prior completed stages and remediation records

### Constraints during close review

- Do not modify backend/frontend code, migrations, tests, scripts, or data.
- Do not implement the `employee_number` correction migration.
- Do not add immutability triggers.
- Do not enforce or remove statutory-component disablement.
- Do not begin Stage 09.
- Do not create a separate close-review prompt file; this `CONTEXT.md` is the executable instruction.

### Publish

Commit and push the Stage 08 closure documentation to `uat`.

Return only:

```text
Stage: 08 — Data integrity
Status: complete
Primary file: docs/audit-program/08-data-integrity/findings.md
Audit state: docs/audit-program/audit-state.md
Commit: <SHA>

Result:
- 04-004 rejected: retry and reconciliation cannot overlap by lifecycle construction.
- Confirmed gaps: 08-001 nullable employee_number; 08-002 payroll_run immutability window; 08-003 statutory-component omission without guard/trace.
- Financial/data corruption found: none.

Next stage:
09 — Security and tenant isolation
```
