# `docs/sprints/`

Repository-based state for the sprint delivery workflow: which sprint is active (`CURRENT.md`), the static rules governing stage transitions/parallelism/skips/rework (`WORKFLOW.md`), and the authoritative per-stage metadata — purpose, entry conditions, dependencies, mandatory status (`STAGE-REGISTRY.md`). Each sprint gets its own `<sprint-id>/` workspace once created (not yet — no pilot sprint has been selected).

This does not replace `~/.claude/skills/*/SKILL.md` — those keep the reusable instructions for *how* to run each stage. This folder formalizes *when* a stage applies and *what happened* each time it ran, which is the gap identified in the design rationale below.

## Design rationale

- `docs/diagnostics/2026-07-11-sprint-workflow-icm-diagnostic.md` — the original diagnostic: is the sprint workflow an ICM workspace, or just a disciplined sequence of slash commands? (Conclusion: the latter — this folder exists to close that gap.) Section 7 (revised) contains the approved non-linear target model this folder implements.
- `docs/diagnostics/2026-07-11-prompt-revise-sprint-workflow-icm-target-model.md` — the request that produced the non-linear revision (stages are skipped, reordered, and run concurrently in practice; a single-scalar "current stage" model doesn't fit).
- `docs/diagnostics/2026-07-12-nonlinear-icm-sprint-workflow-implementation-plan.md` — the approved implementation plan (decisions D1–D9, ordered changesets, rollback plan, pilot acceptance criteria). This folder's four static files are Changeset 1 of that plan.

## Precedent this reuses

This structure is not new invention — it reuses conventions already proven in two other workspaces in this repository:

- `docs/audit-program/` — named stage status, an explicit human-decisions log, evidence-cites-findings discipline, a single state tracker (`audit-state.md`).
- `docs/programmes/agentic-architecture-review/` — numbered stage folders, a `CONTEXT.md` contract per stage, `findings.md`/`decisions.md` per stage, a single `review-state.md` tracker, and an explicit gate rule (a stage does not begin until the prior stage's gate is explicitly passed).

`docs/sprints/` generalizes the same primitives (named status + recorded reason + dependency check) to the many-short-sprints delivery workflow, where stages branch, skip, and run in parallel far more than in those two single long-running investigations — hence one folder per sprint rather than one folder per stage.
