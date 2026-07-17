# Casper Prompt — Close Stage 04: Original-run and Retry Parity

Close Stage 04 — Original-run and Retry Parity.

## Human decisions to record

Record the following decisions in `docs/audit-program/_core/human-decisions.md`:

1. Finding `04-001` is a confirmed S0 release blocker.
2. Because the platform is not currently live, do not interrupt the audit for an emergency production patch during this stage.
3. Do not wait until Stage 13 to begin remediation planning. Stage 05 must validate the snapshot contract and define the canonical fix, after which `04-001` should move into an immediate remediation sprint before any live payroll processing or production release.
4. Retry should consume the frozen statutory-rule content from `payroll_run.rules_context_snapshot["statutory_rule"]` rather than re-resolving mutable live `statutory_rule` and `tax_band` tables.
5. The fix must preserve support for legacy runs explicitly: runs without the required frozen statutory content must hard-fail with a clear correction-run instruction rather than silently falling back to live statutory data.
6. `04-002` remains a separate S1 observability finding. The remediation design should record which statutory rule/version was actually used for each calculation or make that identity directly derivable from immutable persisted data.

## Before closing

Read:

- `docs/audit-program/04-original-run-retry-parity/CONTEXT.md`
- `docs/audit-program/04-original-run-retry-parity/findings.md`
- all Stage 04 evidence
- `docs/audit-program/_core/evidence-standard.md`
- `docs/audit-program/_core/finding-schema.md`
- `docs/audit-program/_core/severity-model.md`
- `docs/audit-program/_core/human-decisions.md`
- `docs/audit-program/audit-state.md`

Verify:

- `04-001` is supported by the controlled non-production reproduction and cleanup evidence.
- The evidence demonstrates an original run and retry within the same `payroll_run` using different statutory-rule content.
- The S0 severity is consistent with the severity model.
- `04-002`, `04-003`, and `04-004` each use a single valid status value and compliant evidence for the claim being made.
- Every completion criterion in Stage 04 `CONTEXT.md` is satisfied by an explicit output.
- The controlled test left no test data residue.

## Close the stage

Update:

- `docs/audit-program/04-original-run-retry-parity/findings.md`
  - change the stage heading/status from `in-progress` to `complete`
  - add a final decision and handoff section containing the decisions above
- `docs/audit-program/audit-state.md`
  - mark Stage 04 `complete`
  - set the closed date to today
  - leave Stage 05 not started
  - set the next action to open Stage 05 — Snapshot Integrity
  - identify `04-001` as an S0 release blocker requiring remediation immediately after Stage 05 design validation and before any live payroll processing or production release

## Stage 05 handoff

State explicitly that Stage 05 must:

- validate the completeness and stability of `rules_context_snapshot.statutory_rule`
- confirm it contains every statutory value and tax-band field required by retry
- define the exact snapshot-first retry contract
- define behaviour for legacy runs lacking v2 statutory snapshot content
- assess whether statutory identity should also be persisted per result to address `04-002`
- produce a bounded remediation specification for `04-001`, but make no production-code changes during Stage 05

Carry forward:

- `04-004` to Stage 08 for reconciliation-refresh verification
- `04-002` to Stages 07 and 10
- the controlled reproduction script to Stage 11 as the basis for a regression test

## Constraints

- Do not modify application code, frontend code, migrations, scripts, or tests.
- Do not implement the fix in this stage.
- Do not start Stage 05.
- Do not downgrade `04-001`.
- Do not remove or weaken the controlled reproduction evidence.

## Publish

After closing the stage:

1. Commit only the audit documentation changes relevant to closing Stage 04.
2. Push to the `uat` branch.
3. Return only:

```text
Stage: 04 — Original-run and retry parity
Status: complete
Primary file: docs/audit-program/04-original-run-retry-parity/findings.md
Audit state: docs/audit-program/audit-state.md
Commit: <SHA>

Decision:
04-001 is an S0 release blocker. Stage 05 validates the snapshot-first fix; remediation follows immediately afterward and before any live payroll processing or production release.

Next stage:
05 — Snapshot integrity
```
