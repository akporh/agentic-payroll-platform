# State — `sec-s7-timesheet-upload-guard`

Authoritative per-stage status, per `WORKFLOW.md`. Stage IDs and dependency shapes are drawn from `STAGE-REGISTRY.md`. This file is mutated in place as the sprint progresses — it is not a historical log (see `decisions.md` for the append-only log).

```yaml
sprint: sec-s7-timesheet-upload-guard
status: active

stages:
  roadmap:
    status: complete
    note: >
      docs/ROADMAP.md Track S reviewed; S7 confirmed still open by reading
      the live file (backend/api/routes/payroll.py:1679-1692 had no byte
      limit before openpyxl parsing). S8 (adjacent Track S item) found
      already resolved (requirements.txt:15 already pins
      python-multipart==0.0.28) — ROADMAP is stale on that item, flagged
      for next /roadmap sync, not bundled into this sprint.

  pm:
    status: complete
    note: >
      Scope, source item, acceptance criteria, and out-of-scope agreed
      via the Validation-Pilot Scope Approval message (2026-07-13,
      decisions D-VP-01 through D-VP-06) — see CONTEXT.md. This
      exhaustive approval substitutes for a separate /pm chat pass; no
      additional scope discussion was needed beyond what D-VP-01/02
      already specify verbatim.

  architecture:
    status: skipped
    reason: >
      Genuine minor cross-layer question (where the max-upload-size
      value should live) exists and is being deliberately deferred, not
      structurally absent — see decisions.md for the full resolution
      (D-VP-02).
    decision_owner: Michael Emedo
    decision_ref: DEC-sec-s7-timesheet-upload-guard-01
    date: 2026-07-13

  arch-council:
    status: not-applicable
    reason: No status/enum, financially-critical DB constraint, API response-field meaning change, destructive migration, cross-workspace endpoint, or shared type/interface/service contract touched.
    decision_owner: Michael Emedo
    decision_ref: DEC-sec-s7-timesheet-upload-guard-02
    date: 2026-07-13

  implementation:
    status: complete
    depends_on: [pm, arch-council]
    evidence: evidence/implementation/size_guard.md
    note: >
      Both graph dependencies are terminal (pm: complete, arch-council:
      not-applicable). Scope approval (D-VP-01/02) is the equivalent of
      a plan-approval gate here — this sprint's size did not warrant a
      separate formal plan-mode/ExitPlanMode pass; that is recorded
      honestly here rather than fabricating a plan.md that was never
      produced through that mechanism. Code + tests committed (`be337aa`):
      MAX_TIMESHEET_UPLOAD_BYTES guard in payroll.py, advisory client
      check + toast in TimesheetUpload.tsx, 2 focused backend tests.
      Full suite 308 passed (306 pre-existing + 2 new), 1 pre-existing
      skip, 0 failed. Frontend tsc --noEmit clean.

  verification:
    status: active
    depends_on: [implementation]
    may_run_with: [security]
    note: >
      implementation is complete — dependency terminal. Entry condition
      holds (this sprint touches both backend/api/routes/payroll.py and
      frontend/src/pages/TimesheetUpload.tsx). Activated in this commit
      together with security, deliberately before either stage's review
      work has begun (no evidence: field populated yet) — this commit
      is the durable proof both stages were genuinely concurrent, not
      an artifact of batching convenience (the gap the
      aud-q1-trace-source retro found in its own audit/test transitions).

  security:
    status: active
    depends_on: [implementation]
    may_run_with: [verification]
    note: >
      implementation is complete — dependency terminal. Entry condition
      holds (backend/api/routes/payroll.py modified). Activated in this
      same commit as verification — see its note.

  audit:
    status: not-applicable
    reason: Neither sequential_executor.py, rule_evaluator.py, executor.py, nor a calculation-altering migration is touched — this is upload validation, not a calculation path.
    decision_owner: Michael Emedo
    decision_ref: DEC-sec-s7-timesheet-upload-guard-03
    date: 2026-07-13

  test:
    status: blocked
    depends_on: [implementation, verification, security, audit]
    waiting_for:
      - verification
      - security

  retro:
    status: blocked
    depends_on: [test]
    waiting_for:
      - test
```

## Reading this file

- `architecture` is `skipped` (not `not-applicable`) — the first real exercise of this distinction in this workflow's history. See `decisions.md`.
- `implementation` is `eligible` — both its dependencies (`pm`, `arch-council`) are terminal.
- `verification` and `security` are genuinely `blocked` pending `implementation` — once it completes, both become `eligible` together, and this sprint's evidence/commit strategy (per `docs/diagnostics/2026-07-13-icm-follow-up-validation-pilot-scope.md` §6/§8) will commit their `active` transition as its own dedicated commit, before either stage's actual review work begins — the specific gap the `aud-q1-trace-source` retro found (its `audit`/`test` transitions were squashed into one commit and never observed genuinely concurrent).
- `audit` is `not-applicable` from the start — this determination doesn't depend on any other stage's outcome.
- `test` and `retro` remain genuinely `blocked`, cascading behind `implementation`/`verification`/`security` actually reaching terminal status.
