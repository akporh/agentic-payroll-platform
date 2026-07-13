# Current Sprint(s)

Names the active sprint workspace(s) — nothing else. See `README.md` for what this folder is, `WORKFLOW.md` for transition rules, `STAGE-REGISTRY.md` for stage definitions.

```yaml
active_sprints: []
```

`active_sprints` is a list shape by design (D9, `docs/diagnostics/2026-07-12-nonlinear-icm-sprint-workflow-implementation-plan.md`), even though exactly one entry is supported and enforced for now — one active sprint at a time. This means multi-sprint support later is a validation-rule change, not a schema migration.

**No sprint currently active.** `aud-q1-trace-source` — the pilot sprint for the non-linear ICM workflow (Changeset 2, approved 2026-07-12; closed Changeset 8, 2026-07-13) — reached `status: complete` in its `state.md`: the product fix (`component_source` in the `fixed_amount` trace entry, ROADMAP Track Q / Q1 / AUD-1) passed audit and test with 0 regressions. Its workspace remains fully readable at `aud-q1-trace-source/` (`CONTEXT.md`, `state.md`, `decisions.md`, `retrospective.md`) as the worked example for the next sprint to use this structure. Its ICM §9 workflow-mechanics validation is PARTIAL — see `aud-q1-trace-source/retrospective.md` and `docs/retro-reports/2026-07-13-aud-q1-trace-source.md` for which scenarios still need a future pilot to exercise them.
