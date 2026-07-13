# Current Sprint(s)

Names the active sprint workspace(s) — nothing else. See `README.md` for what this folder is, `WORKFLOW.md` for transition rules, `STAGE-REGISTRY.md` for stage definitions.

```yaml
active_sprints:
  - sec-s7-timesheet-upload-guard
```

`active_sprints` is a list shape by design (D9, `docs/diagnostics/2026-07-12-nonlinear-icm-sprint-workflow-implementation-plan.md`), even though exactly one entry is supported and enforced for now — one active sprint at a time. This means multi-sprint support later is a validation-rule change, not a schema migration.

**`sec-s7-timesheet-upload-guard`** — follow-up ICM validation pilot (Candidate A, approved 2026-07-13 per `docs/diagnostics/2026-07-13-icm-follow-up-validation-pilot-scope.md` and the Validation-Pilot Scope Approval decisions D-VP-01 through D-VP-06). A real fix: 10 MB server-side size cap on the timesheet upload endpoint (Track S, item S7), chosen to genuinely exercise a `skipped` (not `not-applicable`) `architecture` stage and truly parallel `verification`+`security` stages. See `sec-s7-timesheet-upload-guard/CONTEXT.md`, `state.md`, and `decisions.md`.

`aud-q1-trace-source` — the prior pilot sprint (Changeset 2, approved 2026-07-12; closed Changeset 8, 2026-07-13) — remains `status: complete` and fully readable at `aud-q1-trace-source/` as the first worked example of this structure.
