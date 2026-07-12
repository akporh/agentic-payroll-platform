# Stage 11 — Scenario Testing

**Status:** not started (see [`../audit-state.md`](../audit-state.md))

## Purpose

Validate the platform’s critical payroll guarantees through controlled, evidence-backed scenarios rather than relying only on static code inspection.

This stage must:

- execute the highest-value scenarios that are supported by the current implementation;
- re-run the regression scenarios for the completed `04-001`/`05-001` remediation;
- test known integrity, failure, lifecycle, retry, and tenant-scoping hypotheses where safe;
- distinguish current executable tests from future acceptance scenarios that depend on unimplemented Stage 09/10 remediation;
- identify missing automated coverage and convert it into implementation-ready Stage 13 backlog inputs.

This is an audit/testing stage, not a remediation stage. Do not alter production behaviour to make a scenario pass.

## Confirmed handoff state

- Stages 01–10 are complete.
- `04-001` and `05-001` are remediated and their focused regression suite previously passed.
- Stage 10’s trace-remediation design is approved but **not implemented**. Its 12 regression scenarios are specifications for the future implementation; execute only those portions supported by current code and classify the remainder as blocked-by-unimplemented-design rather than failed current behaviour.
- Stage 09 found S0 production blockers: no authentication, membership, or RBAC exists. Cross-workspace authorization scenarios can prove current exposure, but secure post-auth outcomes cannot be executed until the security remediation exists.
- `07-003` is confirmed: unexpected outer background-task failures can remain log-only.
- `08-001` is confirmed: `employee.employee_number` remains nullable due to a silently failed migration guard.
- `08-002` is confirmed: `payroll_run` totals/period fields lack DB-level immutability until `PAID`.
- `08-003` is confirmed: disabled statutory components are omitted without a guard or trace signal.
- `09-008` is confirmed: CSV exports lack formula-injection sanitization.
- `04-004` is rejected and requires no further testing unless contradictory evidence appears.
- `CLAUDE.md` is authoritative; `docs/wrapper-command/` is reference-only.

## Required inputs

Read before execution:

- `CLAUDE.md`
- `docs/audit-program/README.md`
- `docs/audit-program/WORKFLOW.md`
- `docs/audit-program/audit-state.md`
- all files under `docs/audit-program/_core/`
- Stage 02 findings and existing diagnostic scripts
- Stage 04 findings and controlled statutory-divergence reproduction
- Stage 05 findings and remediation records
- `docs/audit-program/remediation/04-001-05-001/summary.md`
- `docs/audit-program/remediation/04-001-05-001/verification.md`
- Stage 06–09 findings for UI, observability, integrity, and security scenarios
- Stage 10 findings, especially §§15–16 acceptance criteria and regression scenarios
- existing tests under `tests/`
- existing scripts under `scripts/` and prior stage evidence directories

## Testing principles

1. Use only local, disposable, non-production data.
2. Prefer existing test fixtures and transaction rollback.
3. Every database scenario must document preconditions, inserted/modified rows, cleanup method, and zero-residue verification.
4. Do not weaken guards or modify production code to create testability.
5. Do not treat an unimplemented design requirement as a regression in current code; mark it `blocked-by-design-not-implemented`.
6. Preserve exact Decimal values and compare financial outcomes without float conversion.
7. Record observed behaviour, not expected labels alone.
8. A passing scenario must prove the business invariant, not merely an HTTP status or absence of an exception.

## Required investigation and execution

### 1. Existing automated test baseline

Run the current relevant test suites and record:

- command
- environment/database
- total passed/failed/skipped
- runtime
- failure details
- whether failures are deterministic
- whether tests mutate persistent data

At minimum include:

- full backend test suite where feasible
- payroll calculation tests
- retry tests
- snapshot tests
- reconciliation tests
- state-machine/lifecycle tests
- export tests
- tenant/workspace scoping tests, if any

Do not update tests during this stage.

### 2. `04-001` snapshot-first retry regression

Re-run or faithfully reproduce the approved controlled scenario:

1. create/use a run with a frozen statutory-rule snapshot;
2. introduce a later live statutory rule/tax-band change;
3. retry a failed employee;
4. prove retry uses the frozen snapshot, not the later live rule;
5. compare PAYE and relevant trace/result fields;
6. verify legacy/incomplete snapshots hard-fail without live fallback;
7. verify zero residue.

Expected invariant:

- original and retry statutory calculation basis remains identical for the same run;
- live statutory changes after run creation do not affect retry;
- incomplete legacy snapshots are rejected before mutation.

### 3. `05-001` snapshot-failure visibility regression

Force snapshot creation failure safely and verify:

- run becomes terminal `FAILED`;
- `error_message` is populated;
- calculation/result persistence does not begin;
- inputs are not linked/claimed after failure;
- audit/event transition is written;
- API returns `FAILED` and `error_message`;
- current frontend handling remains documented as incomplete (`06-001`/`06-004`), not mistaken for backend failure;
- zero residue.

### 4. Outer background-task failure (`07-003`)

Where possible without production-code modification, induce an unexpected failure after snapshot creation but outside contained per-employee failures.

Verify:

- final run status
- persisted error message
- result/input residue
- audit/event rows
- execution trace
- server log output
- API/UI visibility

If safe injection is impossible without code changes, document the exact blocked test seam and specify the future fault-injection test required. Do not monkey-patch production source files on disk.

### 5. Retry behaviour matrix

Test current retry behaviour across:

- valid `PARTIAL` run with one failed employee
- multiple failed employees
- mixed retry success/failure
- invalid status
- complete snapshot
- incomplete/legacy snapshot
- repeated retry request
- result uniqueness after DELETE+INSERT replacement
- total recomputation from result rows
- final transition to `CALCULATED` or remaining `PARTIAL`
- preservation of successful original employee results

Record current `execution_trace` output explicitly: zero retry rows is expected current behaviour and a confirmed gap, not a surprise failure.

### 6. Financial calculation scenarios

Execute representative scenarios covering at least:

- salaried monthly employee
- joiner proration
- leaver proration
- unpaid leave or absence adjustment
- pension employee/employer portions
- NHF
- PAYE
- rent relief where applicable
- arrears/reference-period handling
- timesheet/shift employee
- regular overtime
- weekend/public-holiday work
- paid/unpaid attendance codes
- zero-value and ineligible components

For each scenario capture:

- configuration
- inputs
- expected calculation reasoning
- actual result
- component trace
- rounding
- pass/fail

Reuse known client comparison fixtures where trustworthy, but do not fabricate expected values from the implementation under test.

### 7. Payroll arithmetic and aggregate invariants

Verify:

- `gross_pay - deductions - tax = net_pay` under the platform’s defined classification rules;
- run totals equal the sum of successful employee-result rows;
- failed rows do not contribute financial totals unexpectedly;
- retry recomputation removes stale totals;
- Decimal precision and rounding are stable;
- repeated reads return identical values.

### 8. Employee and contract integrity scenarios

Test:

- duplicate non-null `employee_number` in one workspace is rejected;
- same employee number across different workspaces behaves as designed;
- `NULL employee_number` is currently accepted by schema (`08-001` confirmation);
- overlapping contracts are rejected by the GIST constraint;
- multiple open-ended contracts are rejected;
- valid sequential contracts are accepted;
- payroll selects the contract effective for the run period;
- joiner/leaver dates influence inclusion and proration correctly.

Do not repair nullable rows.

### 9. Lifecycle and immutability scenarios

Test allowed and forbidden transitions:

- DRAFT → CALCULATING
- CALCULATING → CALCULATED/PARTIAL
- PARTIAL → CALCULATED
- CALCULATED → APPROVED
- APPROVED → LOCKED
- LOCKED → PAID
- illegal skips and reversals

Test mutation attempts against:

- `payroll_result` at `CALCULATED`, `APPROVED`, `LOCKED`, `PAID`
- `payroll_run` totals/period at `APPROVED` and `LOCKED` (`08-002`)
- `payroll_run` at `PAID`
- snapshot columns/tables according to their current triggers

Confirm actual DB enforcement, not only repository behaviour.

### 10. Reconciliation scenarios

Verify:

- only `LOCKED` runs can be reconciled;
- MATCHED requires equal totals;
- MISMATCH requires unequal totals;
- RESOLVED requires audit fields;
- duplicate reconciliation is rejected;
- reconciliation cannot coexist with a retry-eligible `PARTIAL` state;
- resolution behaviour and local notes/resolved-by fields;
- absence of unified audit/event entries (`07-002`) remains observable.

Do not reopen rejected `04-004` unless execution contradicts the structural proof.

### 11. Statutory-component disablement (`08-003`)

In a disposable workspace:

1. disable a statutory component through the supported configuration path or controlled DB setup;
2. calculate payroll;
3. verify the component is omitted;
4. verify no guard blocks the run;
5. verify current component/execution traces contain no explicit omission signal;
6. restore state and verify zero residue.

Do not decide whether the behaviour should be allowed. Test only the current mechanism and evidence gap.

### 12. Security and tenant-isolation scenarios

Because authentication does not exist, separate current-exposure scenarios from future post-remediation specifications.

Current executable scenarios:

- unauthenticated workspace enumeration
- cross-workspace access using another workspace’s `run_id`
- retry/approve/lock/pay by direct ID
- legacy reconciliation route access
- nominally workspace-scoped reconciliation with mismatched path workspace
- timeline with mismatched path workspace
- global legacy-executor stats through a workspace path
- unauthenticated admin/operator dashboards
- export access across workspaces

Record only the minimum evidence necessary; do not extract or retain sensitive datasets.

Future blocked scenarios from Stage 10:

- authenticated unauthorized trace request returns non-disclosing `404`
- read-only auditor can view authorized traces
- platform-administrator access is explicit and audited
- direct-client user is restricted to permitted workspace

Mark these as blocked until Stage 09 remediation exists.

### 13. Raw exception and error-sanitization scenarios

Select representative Group A and Group B routes from `07-001`/Stage 09.

Verify:

- whether raw DB/schema/constraint details reach the response;
- whether developer-authored `ValueError` messages remain controlled;
- frontend error extraction behaviour where practical;
- no test evidence file stores secrets or personal data.

Do not attempt to trigger destructive database errors.

### 14. CSV formula-injection scenario (`09-008`)

Using synthetic employee-controlled text beginning with `=`, `+`, `-`, or `@`:

- generate each relevant CSV export;
- inspect the exact cell output;
- determine whether spreadsheet formula execution would be possible on open;
- avoid opening the file in a spreadsheet application;
- delete generated files and verify cleanup.

### 15. Stage 10 trace-design scenario disposition

For each of Stage 10’s 12 scenarios, classify it as:

- executable now and passed
- executable now and failed
- partially executable
- blocked by unimplemented Stage 10 schema/write/API design
- blocked by unimplemented Stage 09 authentication/RBAC
- deferred because it requires future direct-client functionality

Do not claim Stage 10 design acceptance criteria pass merely because the design is internally coherent.

### 16. Test-coverage gap analysis

Map every confirmed S0–S2 finding to:

- existing automated regression test
- controlled audit-only scenario
- no coverage
- coverage blocked by missing architecture

Identify the minimum new permanent tests required during remediation, including:

- schema assertions
- migration upgrade/downgrade checks
- tenant-ownership tests
- lifecycle/immutability tests
- background-failure fault injection
- retry trace and statutory identity tests
- export sanitization tests

## Required outputs

At minimum produce:

1. Automated test baseline
2. Scenario execution register
3. `04-001` regression evidence
4. `05-001` regression evidence
5. `07-003` fault-injection result or blocked-test specification
6. Retry behaviour matrix
7. Financial scenario matrix
8. Arithmetic/aggregate invariant matrix
9. Employee/contract integrity results
10. Lifecycle/immutability results
11. Reconciliation results
12. Statutory-component omission result
13. Security/tenant exposure scenario results
14. Raw-exception disclosure results
15. CSV formula-injection result
16. Stage 10 12-scenario disposition matrix
17. Confirmed-finding-to-test coverage map
18. Permanent regression-test recommendations
19. Positive controls
20. Findings using `_core/finding-schema.md`
21. Evidence under `docs/audit-program/11-scenario-testing/evidence/`
22. Handoff notes for Stages 12 and 13

## Finding rules

Use exactly one valid status per finding:

- confirmed
- plausible
- unconfirmed
- rejected
- human decision required

Additionally, scenario rows may use these execution dispositions without treating them as finding statuses:

- passed
- failed
- blocked-by-unimplemented-design
- blocked-by-missing-auth
- not-executed-with-reason

A failed scenario is not automatically a new defect if it reproduces an already-confirmed finding. Link it to the existing finding unless it reveals a distinct mechanism or severity.

A passing scenario does not prove absence of defects outside its tested boundary.

## Constraints

- Do not modify production backend/frontend code.
- Do not modify migrations.
- Do not repair data.
- Do not commit permanent test changes during this audit stage.
- Temporary local harnesses may be created only under the Stage 11 evidence directory when necessary, must be self-contained, and must not alter application behaviour.
- Do not use real production or client data.
- Do not perform destructive security testing, brute force, credential attacks, or bulk extraction.
- Do not start Stage 12.
- Do not reopen `04-001`/`05-001` without regression evidence.
- Do not represent Stage 10’s unimplemented design as current behaviour.

## Completion criteria

Stage 11 is ready for human review only when:

- the relevant current automated suite has been run and recorded;
- `04-001` and `05-001` remediation regressions are revalidated;
- current retry behaviour is tested across success and failure cases;
- representative financial, lifecycle, integrity, reconciliation, and export scenarios are executed;
- known S0–S2 security exposure is demonstrated minimally or explicitly marked unsafe/unnecessary to repeat;
- Stage 10’s 12 scenarios have a complete disposition matrix;
- every database scenario verifies cleanup/zero residue;
- test-coverage gaps are mapped to future permanent tests;
- findings and later-stage handoffs are complete.

## Publication

When the investigation is complete:

1. Create `findings.md` and evidence under this stage.
2. Update `docs/audit-program/audit-state.md`:
   - mark Stage 11 `in-progress`
   - set opened date to today
   - set next action to human review of Stage 11
   - preserve all completed stages and remediation records
3. Leave Stage 11 `in-progress, awaiting review`; do not self-close.
4. Commit and push only Stage 11 audit documentation/evidence and the audit-state update to `uat`.
5. Return only:

```text
Stage: 11 — Scenario testing
Status: in-progress, awaiting review
Primary file: docs/audit-program/11-scenario-testing/findings.md
Audit state: docs/audit-program/audit-state.md
Commit: <SHA>

Important decisions required:
- <decision or none>

Headline test results:
- Automated tests: <passed/failed/skipped>
- Executed audit scenarios: <passed/failed>
- Reproduced confirmed findings: <count>
- New distinct findings: <count>
- Stage 10 scenarios blocked by unimplemented design/auth: <count>
```
