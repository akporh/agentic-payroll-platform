# Casper Prompt — Close Stage 05: Snapshot Integrity

Close Stage 05 — Snapshot Integrity.

## Human decisions to record

Record the following decisions in `docs/audit-program/_core/human-decisions.md`:

1. `05-001` is included in the immediate post-Stage-05 remediation sprint alongside `04-001`.
2. Rationale: snapshot creation is part of the retry guarantee. Silent background-task failure can leave a completed run permanently non-retryable and requires a correction run with no operator-visible cause.
3. The remediation must make snapshot-creation failure fail visibly and prevent the run from proceeding as successfully retryable when the required snapshot was not persisted.
4. `05-004` is not included in the immediate remediation sprint as a broad cross-snapshot hardening exercise.
5. Rationale: `05-004` is a confirmed defence-in-depth inconsistency, but no current update path mutates the unprotected snapshots, and `payroll_run.rules_context_snapshot` — the snapshot required by the `04-001` fix — already has DB-level immutability enforcement.
6. `05-004` remains a Stage 13 backlog item, with Stage 12 input where relevant, unless implementation of `04-001` or `05-001` introduces or changes any snapshot mutation path. Any snapshot touched by the remediation must preserve or strengthen immutability; it must not weaken existing DB guarantees.
7. The `04-001` remediation specification is approved as ready for implementation after Stage 05 closes.

## Before closing

Read:

- `docs/audit-program/05-snapshot-integrity/CONTEXT.md`
- `docs/audit-program/05-snapshot-integrity/findings.md`
- all Stage 05 evidence
- `docs/audit-program/_core/evidence-standard.md`
- `docs/audit-program/_core/finding-schema.md`
- `docs/audit-program/_core/severity-model.md`
- `docs/audit-program/_core/human-decisions.md`
- `docs/audit-program/audit-state.md`

Verify:

- every Stage 05 completion criterion is satisfied by an explicit output
- the v2 statutory snapshot sufficiency conclusion is evidence-backed
- the canonical retry contract contains no fallback to live statutory resolution
- legacy v1/incomplete snapshots hard-fail and require a correction run
- `05-001` and `05-004` each use a single valid status and justified severity
- the `04-001` remediation specification has no blocking gaps
- no production code, tests, migrations, scripts, or frontend files were modified

## Close the stage

Update:

- `docs/audit-program/05-snapshot-integrity/findings.md`
  - change the stage status from `in-progress` to `complete`
  - add a final decision section containing the decisions above
  - state clearly that `05-001` is bundled with the immediate remediation sprint
  - state clearly that the broad `05-004` hardening is deferred to Stage 13
- `docs/audit-program/audit-state.md`
  - mark Stage 05 `complete`
  - set the closed date to today
  - preserve `04-001` as an S0 release blocker
  - state that the immediate remediation sprint is now unblocked and must occur before Stage 06 or any live payroll processing/production release
  - list the remediation scope as `04-001` + `05-001`
  - list `05-004` as deferred to Stage 13
  - leave Stage 06 not started

## Immediate remediation handoff

Add a concise implementation handoff that includes:

### `04-001`

- read `rules_context_snapshot["statutory_rule"]` for v2 runs
- remove live statutory-rule/tax-band re-resolution from retry
- hard-fail legacy/incomplete snapshots
- add the specified regression tests

### `05-001`

- do not swallow snapshot-creation exceptions
- ensure a run cannot proceed into normal calculation/persistence while required snapshot creation has failed silently
- surface an operator-visible failure state or error
- preserve self-cleaning and transactional guarantees
- add a regression test proving snapshot-creation failure does not yield a silently non-retryable completed run

Do not include the broad `05-004` immutability-trigger harmonisation in this sprint. Record it for Stage 13, while requiring that any snapshot schema or write path touched by the immediate remediation retains existing immutability guarantees.

## Constraints

- Do not implement the remediation in this stage.
- Do not start Stage 06.
- Do not modify application code, migrations, tests, scripts, or frontend files.
- Do not downgrade `04-001`, `05-001`, or `05-004`.
- Do not add live-query fallback for legacy snapshots.

## Publish

After closing Stage 05:

1. Commit only the audit documentation changes relevant to closing the stage.
2. Push to `uat`.
3. Return only:

```text
Stage: 05 — Snapshot integrity
Status: complete
Primary file: docs/audit-program/05-snapshot-integrity/findings.md
Audit state: docs/audit-program/audit-state.md
Commit: <SHA>

Decision:
- 05-001 bundled into immediate remediation with 04-001
- 05-004 deferred to Stage 13

Remediation status:
- Specification ready: yes
- Scope: 04-001 + 05-001
- Blocking gaps: none

Next action:
Immediate remediation sprint before Stage 06
```
