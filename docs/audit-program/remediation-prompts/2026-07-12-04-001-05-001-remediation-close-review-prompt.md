# Casper Prompt — Close Immediate Remediation Sprint: 04-001 + 05-001

Close and approve the immediate remediation sprint for findings `04-001` and `05-001`.

## Review inputs

Read:

- `docs/audit-program/remediation/04-001-05-001/summary.md`
- `docs/audit-program/remediation/04-001-05-001/verification.md`
- `docs/audit-program/audit-state.md`
- `docs/audit-program/04-original-run-retry-parity/findings.md`
- `docs/audit-program/05-snapshot-integrity/findings.md`
- all changed code, migration, and test files in commit `68e9307`

## Required review conclusions

Verify and record that:

1. `04-001` is remediated:
   - retry reads statutory content only from the frozen v2 `rules_context_snapshot`
   - live `statutory_rule`/`tax_band` queries are absent from the retry-eligible path
   - legacy or malformed snapshots hard-fail before any result deletion, calculation, or persistence
   - the Stage 04 controlled reproduction now returns `REJECTED`

2. `05-001` is remediated:
   - snapshot creation failure aborts calculation and result persistence
   - the run becomes terminal `FAILED`
   - `error_message` is persisted and visible through the run API
   - audit/event records are written using existing mechanisms

3. The blocking implementation gap discovered during remediation is valid and correctly handled:
   - v2 snapshot emission is no longer coupled to `rule_set_id` presence
   - workspaces without a published rule set still receive a complete v2 statutory snapshot with `rule_set: null`
   - this change is in scope because the approved `04-001` fix would otherwise fail for the majority of observed workspaces

4. Existing immutability guarantees remain intact.

5. Migration `b8c9d0e1f2a3` is reversible and consistent with the project's migration conventions.

6. All acceptance criteria are met:
   - focused tests: 5/5 pass
   - broader suite: 291 pass, 1 unrelated pre-existing skip
   - zero test-data residue

## Close the remediation sprint

Update:

- `docs/audit-program/remediation/04-001-05-001/summary.md`
  - set status to `complete`
  - add a final approval section
  - preserve the blocking-gap analysis and the 47/70 workspace evidence

- `docs/audit-program/remediation/04-001-05-001/verification.md`
  - add final review approval and commit reference

- `docs/audit-program/audit-state.md`
  - mark the immediate remediation sprint `complete`
  - mark `04-001` and `05-001` as remediated
  - remove the Stage 06 blocker
  - set next action to open Stage 06 — UI/API/backend wiring
  - leave Stage 06 not started
  - keep `05-004` deferred to Stage 13
  - keep `04-002` open for Stages 07/10

Do not alter the completed status of Stages 01–05.

## Final verification before publish

Run or confirm the latest recorded results for:

```text
python -m pytest tests/test_payroll_retry_snapshot_first.py -v
python -m pytest tests/ -q
```

If code has changed since commit `68e9307`, re-run both commands. If only documentation changes are made, do not rerun unnecessarily; state that the verified results from `68e9307` remain current.

## Constraints

- Do not start Stage 06.
- Do not add `04-002` schema work.
- Do not broaden into `05-004` immutability harmonisation.
- Do not modify the remediation implementation unless review finds a concrete defect.
- Do not downgrade the historical severity of `04-001`; mark it remediated, not reclassified.

## Commit and publish

Commit and push the closure documentation to `uat`.

Return only:

```text
Remediation: 04-001 + 05-001
Status: complete
Primary record: docs/audit-program/remediation/04-001-05-001/summary.md
Verification: docs/audit-program/remediation/04-001-05-001/verification.md
Audit state: docs/audit-program/audit-state.md
Commit: <SHA>

Result:
- 04-001: remediated
- 05-001: remediated
- Acceptance criteria: 9/9 met

Next stage:
06 — UI/API/backend wiring
```
