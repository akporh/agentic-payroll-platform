# Stage 11 — Scenario Testing

**Status:** in-progress (see [`../audit-state.md`](../audit-state.md))

## Purpose

Validate the platform’s critical payroll guarantees through controlled, evidence-backed scenarios rather than static code inspection alone.

This stage must:

- execute the highest-value scenarios supported by the current implementation;
- re-run the `04-001`/`05-001` remediation regressions;
- test known integrity, lifecycle, retry, observability, export, and tenant-scoping hypotheses where safe;
- distinguish current executable scenarios from future scenarios blocked by unimplemented Stage 09/10 work;
- convert coverage gaps into implementation-ready Stage 13 acceptance criteria.

This is an audit/testing stage, not remediation. Do not alter production behaviour to make scenarios pass.

## Confirmed handoff state

- Stages 01–10 are complete.
- `04-001` and `05-001` are remediated.
- Stage 10’s trace-remediation design is approved but unimplemented; its 12 scenarios must be graded against current behaviour.
- Stage 09’s authentication, membership, RBAC, and tenant-ownership controls are also unimplemented; secure post-auth scenarios are blocked.
- `07-003`, `08-001`, `08-002`, `08-003`, `09-008`, and the Stage 09 security findings remain open as documented.
- `04-004` is rejected and must not be reopened without contradictory evidence.
- `CLAUDE.md` is authoritative; `docs/wrapper-command/` is reference-only.

## Testing principles

1. Use local, non-production data only.
2. Prefer existing tests, transaction rollback, and read-only live checks.
3. Document cleanup or prove zero residue for every scenario.
4. Do not weaken guards or modify production code for testability.
5. Do not treat unimplemented design requirements as current regressions.
6. Preserve Decimal precision.
7. Record observed behaviour, not expected labels alone.
8. Passing evidence proves only the tested boundary.

## Required investigation

At minimum cover:

1. Current automated test baseline.
2. `04-001` snapshot-first retry regression.
3. `05-001` snapshot-failure visibility regression.
4. `07-003` fault-injection result or blocked seam specification.
5. Retry behaviour matrix.
6. Representative financial-calculation coverage.
7. Arithmetic and run-total invariants.
8. Employee/contract integrity.
9. Lifecycle and immutability.
10. Reconciliation.
11. Statutory-component omission.
12. Security and tenant-isolation exposure.
13. Raw exception/error sanitization.
14. CSV formula injection.
15. Complete disposition of Stage 10’s 12 scenarios.
16. S0–S2 finding-to-test coverage map and permanent-test recommendations.

## Required outputs

- automated test baseline
- scenario execution register
- remediation regression evidence
- retry/financial/integrity/lifecycle/reconciliation matrices
- security and export evidence
- Stage 10 scenario disposition matrix
- permanent regression-test recommendations
- positive controls
- findings and evidence
- handoffs to Stages 12 and 13

## Finding rules

Use one valid finding status:

- confirmed
- plausible
- unconfirmed
- rejected
- human decision required

Scenario dispositions may additionally use:

- passed
- failed
- blocked-by-unimplemented-design
- blocked-by-missing-auth
- not-executed-with-reason

A failed scenario that reproduces an existing finding is not a new finding unless it reveals a distinct mechanism or severity.

## Constraints

- No production backend/frontend changes.
- No migration changes.
- No permanent test changes.
- No data repair.
- No destructive security testing or bulk extraction.
- Do not start Stage 12.
- Do not reopen `04-001`/`05-001` without regression evidence.
- Do not represent Stage 10’s design as current behaviour.

## Completion criteria

Stage 11 is ready for human review only when:

- the current automated suite is run and recorded;
- `04-001` and `05-001` are revalidated;
- retry, financial, lifecycle, integrity, reconciliation, and export coverage is documented;
- security exposure is minimally demonstrated or explicitly not repeated for safety;
- all Stage 10 scenarios have dispositions;
- cleanup/zero residue is verified;
- coverage gaps map to future permanent tests;
- findings and later-stage handoffs are complete.

---

## Close-review instruction

Use this section after Stage 11 findings and evidence have been committed for review.

### Review conclusion

No new human decision is required.

Accept the following conclusions:

- Full backend suite passed: **306 passed, 1 skipped**.
- `04-001` and `05-001` regressions passed and remain remediated.
- No new distinct defect mechanism was discovered.
- `04-004` remains rejected.
- `07-003` remains untested because the required safe fault-injection seam does not exist; the blocked-test specification is sufficient for this audit stage.
- Current retry behaviour remains correct apart from the already-known zero-row retry `execution_trace` gap.
- Financial, arithmetic, lifecycle, result immutability, contract-overlap, and reconciliation controls remain green through the existing suite and targeted checks.
- `08-001` nullable `employee_number` remains live in the local schema and has no permanent regression test.
- Live execution materially strengthens the Stage 09 findings:
  - unauthenticated workspace enumeration succeeds;
  - mismatched-workspace timeline and reconciliation requests return the same data as correctly scoped requests;
  - the legacy unscoped reconciliation route is reachable;
  - global legacy-executor statistics ignore workspace scope;
  - unauthenticated admin dashboards are reachable.
- `09-008` CSV formula injection is confirmed by a synthetic zero-residue reproduction.
- Stage 10 scenarios remain correctly classified as executable, partial, blocked by unimplemented trace design, blocked by missing authentication, or deferred.
- The absence of permanent authentication/tenant/security regression tests is the largest test-coverage gap.

### Review requirements

Before closing Stage 11, verify that:

1. all live evidence uses non-production/dev-fixture data only;
2. the local server was stopped and zero residue is documented;
3. no Stage 10 acceptance criterion is represented as implemented when it is not;
4. no previous finding is duplicated as a new Stage 11 defect;
5. `04-001` and `05-001` remain closed/remediated;
6. all unexecuted scenarios include a clear reason;
7. the eight permanent-test recommendations are preserved as acceptance criteria for their associated remediation items rather than a generic test backlog;
8. all completion criteria are satisfied.

### Close the stage

Update:

- `docs/audit-program/11-scenario-testing/findings.md`
  - change status to `complete`
  - add final review/closure summary
  - preserve the result that no new distinct defect was found
- `docs/audit-program/audit-state.md`
  - mark Stage 11 `complete`
  - set the closed date to today
  - set next action to open Stage 12 — Code simplification
  - leave Stage 12 not started
  - preserve all prior completed stages and remediation records
  - carry the eight permanent-test recommendations into the related Stage 13 remediation entries
  - carry `07-003`, `08-001`, `08-002`, `08-003`, `09-008`, the Stage 09 security package, and the Stage 10 trace package to Stage 13 with their Stage 11 test evidence/status
  - preserve `04-004` as rejected with no action

### Constraints during close review

- Do not modify application code, migrations, tests, or data.
- Do not implement the blocked Stage 09/10 scenarios.
- Do not begin Stage 12.
- Do not create a separate close-review prompt file.

### Publish

Commit and push Stage 11 closure documentation to `uat`.

Return only:

```text
Stage: 11 — Scenario testing
Status: complete
Primary file: docs/audit-program/11-scenario-testing/findings.md
Audit state: docs/audit-program/audit-state.md
Commit: <SHA>

Result:
- Automated tests: 306 passed, 1 skipped.
- 04-001 and 05-001 regressions passed.
- Live security scenarios reaffirmed Stage 09 findings.
- CSV formula injection reproduced.
- New distinct findings: none.

Next stage:
12 — Code simplification
```
