# Casper Prompt — Immediate Remediation Sprint: 04-001 + 05-001

Execute the immediate remediation sprint for audit findings `04-001` and `05-001`.

This is an explicitly approved exception to the audit programme's normal "remediate after Stage 13" rule. It must complete before Stage 06, any live payroll processing, or any production release.

## Governing inputs

Read before changing code:

- `CLAUDE.md`
- `docs/audit-program/WORKFLOW.md`
- `docs/audit-program/audit-state.md`
- `docs/audit-program/04-original-run-retry-parity/findings.md`
- all evidence under `docs/audit-program/04-original-run-retry-parity/evidence/`
- `docs/audit-program/05-snapshot-integrity/findings.md`
- all evidence under `docs/audit-program/05-snapshot-integrity/evidence/`
- `_core` evidence, severity, and decision records referenced by those findings

Treat the approved Stage 05 canonical contract as authoritative for this sprint.

## Fixed sprint scope

Implement only:

1. `04-001` — retry must use the frozen v2 statutory-rule snapshot instead of re-resolving mutable live statutory tables.
2. `05-001` — snapshot creation failure must become visible and must prevent calculation/result persistence from continuing with an incomplete snapshot.
3. Tests, documentation, and operationally useful errors required to prove these two fixes.

Do not include `05-004` broad immutability harmonisation. It is deferred to Stage 13.

Do not add the optional `04-002` per-result statutory identity migration in this sprint unless it is technically unavoidable for the two approved fixes. It remains a separate follow-up concern.

## Remediation A — 04-001 snapshot-first statutory retry

### Required behaviour

For retry-eligible runs:

- Read statutory content only from:
  `payroll_run.rules_context_snapshot["statutory_rule"]`
- Require:
  - `snapshot_version == 2`
  - non-null `id`
  - non-null `version`
  - non-null `rules_jsonb`
  - non-null `tax_bands`
- Apply the existing deterministic `Decimal(str(...))` extraction and normalization logic to the frozen `rules_jsonb` content.
- Preserve the frozen tax-band ordering and values.
- Remove the live `statutory_rule` and `tax_band` queries from the retry-eligible path in `_build_shared_context`; do not merely leave them as a silent fallback.

### Legacy and malformed snapshots

Runs with any of the following must hard-fail before calculating or writing a retried result:

- absent `rules_context_snapshot`
- snapshot version 1 or missing version
- malformed v2 statutory content
- frozen date without full frozen statutory content
- pre-snapshot-engine runs

Use a clear operator-facing error consistent with the existing correction-run pattern, for example:

`Run {payroll_run_id} predates the v2 statutory snapshot — open a correction run.`

Never fall back to a live statutory query.

### Validation placement

Extend `validate_snapshot_complete()` or add a directly adjacent, single retry preflight validation invoked at the same point.

The validation must run before:

- deleting any failed `payroll_result` row
- calculating any employee
- writing any new result
- changing run status

## Remediation B — 05-001 fail-visible snapshot creation

### Current defect

`create_payroll_snapshot()` runs in the background calculation task. Its exception is currently logged and swallowed, after which calculation and result persistence continue.

### Required behaviour

- Snapshot creation failure must abort the run's calculation flow.
- Do not call `execute_and_persist(...)` after snapshot creation fails.
- Persist an operator-visible failed state or error using the existing run failure/audit/event conventions where available.
- Ensure the API/UI can retrieve a meaningful error rather than requiring server-log access.
- Do not leave the run appearing successfully calculated or silently retry-ineligible.
- Preserve the snapshot service's existing all-or-nothing transaction across its three snapshot tables.

Choose the smallest design consistent with existing run-state and background-task failure patterns. Do not invent a new state unless existing states cannot represent the failure safely.

### Recovery behaviour

Document whether the failed run may be safely retried/restarted after the underlying snapshot failure is corrected, or whether a new/correction run is required. Implement only behaviour supported by current lifecycle invariants.

## Immutability constraint

Although `05-004` is out of scope:

- preserve the existing DB immutability trigger on `payroll_run.rules_context_snapshot`
- do not weaken any current immutability trigger or application guard
- do not add update-in-place behaviour for snapshot content
- use existing insert/delete-reinsert conventions where relevant

## Required tests

Add or update tests that exercise the real current production paths.

### 04-001 regression tests

1. **Frozen statutory parity test**
   - Create an original run under statutory rule A.
   - Leave one employee failed so the run becomes `PARTIAL`.
   - Insert statutory rule B afterward with an intervening `effective_from` that the old retry logic would select.
   - Retry the failed employee.
   - Assert the retried calculation uses rule A from the frozen snapshot, not rule B.
   - Assert PAYE and every affected statutory component match the frozen rule.

2. **Legacy hard-fail test**
   - Construct a retryable run with a v1 or incomplete statutory snapshot.
   - Assert retry fails with the correction-run error.
   - Assert no failed result is deleted/replaced and no new result is written.
   - Assert run status remains consistent.

3. **No live statutory query on v2 retry**
   - Prove via mocking/spying or a database condition that the retry path does not query live `statutory_rule`/`tax_band` for a valid v2 run.

### 05-001 regression tests

4. **Snapshot creation failure aborts calculation**
   - Force `create_payroll_snapshot()` to raise.
   - Assert `execute_and_persist(...)` is not invoked.
   - Assert no payroll results are written.
   - Assert the run records an operator-visible failure/error using the selected lifecycle mechanism.

5. **Successful snapshot creation continues normally**
   - Assert the normal path remains unchanged when snapshot creation succeeds.

All controlled database tests must be non-production, self-cleaning, and verify zero residue where applicable.

## Verification

Run the focused tests first, then the relevant broader payroll/retry test suite.

At minimum report:

- focused test commands and results
- broader regression command and results
- whether the Stage 04 controlled reproduction now passes in fixed-behaviour form
- schema/migration impact: expected to be none for the approved scope
- any lifecycle behaviour chosen for snapshot creation failure

## Documentation and audit handback

Update relevant code comments and technical documentation so the following are explicit:

- v2 frozen statutory snapshot is the sole retry authority
- legacy/incomplete snapshots hard-fail and require a correction run
- snapshot creation is a calculation precondition and failure is not swallowed

Add a remediation record under:

`docs/audit-program/remediation/04-001-05-001/`

At minimum create:

- `summary.md`
- `verification.md`

Record:

- files changed
- implemented behaviour
- tests and outputs
- acceptance criteria results
- any residual risks
- commit SHA

Update `docs/audit-program/audit-state.md` only after implementation and verification:

- mark the immediate remediation sprint complete or in-progress awaiting review, as appropriate
- keep Stage 06 blocked until review confirms all acceptance criteria
- do not mark Stage 06 started

## Acceptance criteria

The sprint is ready for review only when all are true:

1. A v2 retry never queries live statutory rule/tax-band data.
2. A retried employee uses the exact frozen statutory content from the original run.
3. A legacy or malformed statutory snapshot fails before result deletion, calculation, or persistence.
4. Snapshot creation failure prevents calculation and result persistence.
5. Snapshot creation failure is operator-visible outside server logs.
6. Existing snapshot immutability guarantees are preserved.
7. Focused and broader regression tests pass.
8. No production/shared data is modified.
9. Remediation documentation and audit-state handback are complete.

## Commit and publish

After implementation and verification:

1. Review the complete diff for scope creep.
2. Commit the code, tests, and remediation documentation intentionally.
3. Push to the `uat` branch.
4. Return only:

```text
Remediation: 04-001 + 05-001
Status: in-progress, awaiting review
Primary record: docs/audit-program/remediation/04-001-05-001/summary.md
Verification: docs/audit-program/remediation/04-001-05-001/verification.md
Audit state: docs/audit-program/audit-state.md
Commit: <SHA>

Implementation summary:
- <04-001 result>
- <05-001 result>

Tests:
- Focused: <pass/fail>
- Broader regression: <pass/fail>

Decisions or blockers:
- <none or concise list>
```
