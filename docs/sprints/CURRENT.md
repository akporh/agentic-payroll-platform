# Current Sprint(s)

Names the active sprint workspace(s) — nothing else. See `README.md` for what this folder is, `WORKFLOW.md` for transition rules, `STAGE-REGISTRY.md` for stage definitions.

```yaml
active_sprints:
  - aud-q1-trace-source
```

`active_sprints` is a list shape by design (D9, `docs/diagnostics/2026-07-12-nonlinear-icm-sprint-workflow-implementation-plan.md`), even though exactly one entry is supported and enforced for now — one active sprint at a time. This means multi-sprint support later is a validation-rule change, not a schema migration.

**`aud-q1-trace-source`** — pilot sprint for the non-linear ICM workflow (Changeset 2, approved 2026-07-12). A real, bounded fix: add a `component_source` field to the `fixed_amount` rule's trace entry (ROADMAP Track Q, item Q1 / AUD-1). See `aud-q1-trace-source/CONTEXT.md`, `state.md`, and `decisions.md`.
