# Casper Prompt — Begin Stage 04: Original-Run and Retry Parity

Begin Stage 04 — Original-Run and Retry Parity.

## First: verify and normalise the handoff

1. Read:
   - `CLAUDE.md`
   - `docs/audit-program/README.md`
   - `docs/audit-program/WORKFLOW.md`
   - `docs/audit-program/audit-state.md`
   - all files in `docs/audit-program/_core/`
   - `docs/audit-program/01-system-inventory/findings.md`
   - all files in `docs/audit-program/02-execution-trace-baseline/`
   - all files in `docs/audit-program/03-configuration-integrity/`
2. Confirm from `audit-state.md` that Stage 03 is complete and Stage 04 is not started.
3. Correct any stale internal status text inside `03-configuration-integrity/findings.md` so it also says Stage 03 is complete. Do not change the substance or classification of any Stage 03 finding.
4. Confirm that:
   - `CLAUDE.md` is the governing instruction source.
   - `docs/wrapper-command/` is reference-only and non-authoritative.
   - this is a read-only audit stage against production code and shared data.

## Create Stage 04

Create:

```text
docs/audit-program/04-original-run-retry-parity/
├── CONTEXT.md
├── findings.md
└── evidence/
```

Populate `CONTEXT.md` before beginning the investigation.

Update `docs/audit-program/audit-state.md`:

- Stage 04 status: `in-progress`
- Opened date: today
- Next action: perform the Stage 04 original-run/retry parity audit

Do not alter the completed status of Stages 01–03.

## Objective

Determine whether an original payroll run and every supported retry path use equivalent inputs, configuration, snapshots, rules, calculations, totals, persistence behaviour, trace behaviour and state transitions.

The stage must distinguish:

- intentional differences
- legacy compatibility behaviour
- confirmed parity
- plausible divergence mechanisms
- reproduced divergences
- missing observability that prevents parity verification

## Primary Stage 03 input

Finding `03-002` is the highest-priority investigation:

> Retry re-resolves statutory rules and tax bands from live tables using the frozen statutory-effective date, while the original run stored the actual resolved statutory content in `rules_context_snapshot.statUTory_rule` and retry never reads it.

Stage 04 must attempt to reproduce or reject the resulting divergence through controlled non-production execution.

## Required investigation

### 1. Build a path-by-path parity map

Compare:

- original run
- per-employee retry
- partial retry, if still reachable anywhere
- full-run retry, including retired/dead paths if present
- legacy pre-snapshot runs
- legacy pre-rule-set runs
- sequential executor path
- legacy executor fallback

For each path, record:

- entry point
- allowed run status
- employee selection
- period and reference dates
- contract selection
- salary-definition selection
- component metadata source
- client override source
- payroll-rule source
- statutory-rule and tax-band source
- public-holiday source
- payroll-input source and claim semantics
- proration inputs
- rounding behaviour
- handler order
- totals construction
- trace output
- result persistence
- reconciliation effects
- run-state transitions
- failure and rollback behaviour

### 2. Reproduce the statutory-rule divergence candidate

Use controlled non-production execution only.

Design the smallest safe scenario that demonstrates whether retry can select different statutory content from the original run:

1. Create or identify a non-production payroll run whose original calculation resolves statutory rule version A.
2. Confirm the original run freezes version A and its tax bands into `rules_context_snapshot.statUTory_rule`.
3. Introduce a test statutory-rule version B whose `effective_from` makes it eligible for the same frozen `statutory_effective_date` under retry’s live query, without modifying production data.
4. Retry one affected employee.
5. Compare:
   - statutory rule ID/version
   - tax bands
   - PAYE and other statutory deductions
   - taxable income
   - net pay
   - persisted result values
   - trace or diagnostic evidence available
6. Roll back or isolate all test data according to the evidence standard.

If the environment does not permit safe controlled execution, document the exact blocker and create a deterministic test design with all required fixtures, assertions and expected outcomes. Do not falsely mark the divergence as reproduced.

### 3. Compare original-run and retry context construction

Inspect and compare all context builders and shared-context paths, including:

- `backend/api/routes/payroll.py`
- `backend/application/payroll_retry_service.py`
- `backend/application/snapshot_service.py`
- `backend/domain/payroll/executor.py`
- `backend/domain/payroll/sequential_executor.py`
- `backend/domain/payroll/batch_processor.py`
- `backend/domain/payroll/run_executor.py`
- rule, salary, result-building and persistence services used by either path

Identify duplicated context-building logic and verify whether both copies remain semantically equivalent.

### 4. Verify snapshot parity

For every snapshotted domain, determine whether retry reads:

- the frozen content
- a frozen identifier joined to immutable content
- a frozen date used to re-query mutable live content
- live content with no snapshot boundary

At minimum cover:

- component metadata
- client component overrides
- employee contract
- salary definition/components
- payroll rules/rule sets
- statutory rules/tax bands
- public holidays
- payroll inputs
- period context

### 5. Verify calculation parity

Compare original and retry behaviour for:

- component eligibility
- component ordering
- proration
- taxable/non-taxable classification
- gross pay
- employee and employer deductions
- PAYE annualisation/cumulative logic
- NHF/pension/health/levy/life-insurance rules
- arrears
- overtime and attendance-derived inputs
- rounding
- total earnings
- total deductions
- net pay

Use existing tests where reliable, but verify that they exercise the current production paths identified in Stages 01–02.

### 6. Verify persistence and state parity

Compare:

- result insert/update semantics
- unique-key behaviour
- old-result replacement or retention
- snapshot persistence
- `component_trace_jsonb`
- `execution_trace`
- reconciliation refresh/update
- failure rollback
- run status transitions
- retry status transitions

Carry forward Stage 02 finding `02-002`: per-employee retry currently writes no step-level `execution_trace` rows. Determine whether this prevents parity verification and whether any other trace or persisted result can prove equivalent execution.

### 7. Classify every difference

Each difference must be classified as one of:

- confirmed parity
- intentional divergence
- legacy compatibility divergence
- plausible defect
- reproduced defect
- unverifiable due to missing observability
- human decision required

Do not treat different code structure alone as a defect.

## Required outputs

At minimum produce:

1. Original-run/retry execution comparison matrix
2. Context-construction comparison
3. Snapshot-source comparison
4. Rule-resolution comparison
5. Calculation and rounding comparison
6. Persistence and state-transition comparison
7. Trace-footprint comparison
8. Legacy-run compatibility assessment
9. Controlled statutory-divergence test evidence, or a precise blocked-test design
10. Confirmed parity register
11. Divergence register
12. Findings using `_core/finding-schema.md`
13. Evidence under `04-original-run-retry-parity/evidence/`
14. Handoff notes for Stages 05, 07, 08, 10, 11 and 13

## Finding rules

Keep separate:

- current implementation
- intended behaviour
- suspected or confirmed defect

Use only these status values:

- confirmed
- plausible
- unconfirmed
- rejected
- human decision required

For `03-002`:

- upgrade to `confirmed` only if an actual original-run/retry divergence is reproduced with compliant evidence
- keep as `plausible` if only the mechanism remains proven
- mark `rejected` only if controlled evidence demonstrates the live re-resolution cannot change the selected statutory content or result under valid system constraints

## Constraints

- Do not modify production application code.
- Do not modify frontend code.
- Do not modify migrations.
- Do not repair retry behaviour.
- Do not change shared production data.
- Controlled test fixtures may be created only in an isolated non-production environment and must be documented.
- Do not start Stage 05 or later.
- Do not rely on stale diagnostic scripts identified in Stage 02 without independently validating them.
- Do not infer parity from matching function names or similar code.
- Record unresolved product or architecture decisions in `_core/human-decisions.md`.

## Completion and GitHub reporting

When the investigation is complete:

1. Check every Stage 04 completion criterion.
2. Leave Stage 04 `in-progress` pending human review.
3. Commit and push the audit documentation and evidence to `uat`.
4. Do not include unrelated working-tree changes in the commit.
5. Return only:

```text
Stage: 04 — Original-run and retry parity
Status: in-progress, awaiting review
Primary file: docs/audit-program/04-original-run-retry-parity/findings.md
Audit state: docs/audit-program/audit-state.md
Commit: <SHA>

Important decisions required:
- <decision 1>
- <decision 2>
```

Do not paste the full findings into chat; GitHub is the source of truth.
