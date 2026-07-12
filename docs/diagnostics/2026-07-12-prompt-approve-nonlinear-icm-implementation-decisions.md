# Approve Non-Linear ICM Implementation Decisions and Finalise the Execution Plan

Read:

- `docs/diagnostics/2026-07-12-nonlinear-icm-sprint-workflow-implementation-plan.md`
- `docs/diagnostics/2026-07-11-sprint-workflow-icm-diagnostic.md`
- `docs/diagnostics/2026-07-11-prompt-revise-sprint-workflow-icm-target-model.md`

Do not implement the workflow yet.

## Human decision

Approve Casper's recommended option for decisions D1 through D9 in the implementation plan.

Record the decisions as follows:

- **D1 — Pilot sprint:** approve option **(b)**. Use a deliberately small, low-risk sprint chosen to exercise the workflow mechanics independently of feature complexity. Do not select the actual pilot item yet unless one is already explicitly agreed in repository state.
- **D2 — Applicability authority:** approve option **(a)**. `docs/sprints/STAGE-REGISTRY.md` will be the authoritative source for formal stage applicability and entry conditions. Avoid maintaining duplicate applicability rules in prose elsewhere.
- **D3 — Architecture personas:** approve option **(b)** for the pilot. Keep `senior-architect.md` and `principal-reviewer.md` in `~/.claude/agents/`. Record this as a known portability limitation to revisit before another operator or remote agent must run `/arch-council`.
- **D4 — CLAUDE.md changes:** approve option **(b)**, but keep the project `CLAUDE.md` consolidation as its own isolated changeset after the core pilot structure is established.
- **D5 — Plan persistence:** approve option **(a)**. Copy approved plan-mode output into `docs/sprints/<id>/plan.md`; never move or delete the harness-owned original from `~/.claude/plans/`.
- **D6 — Stale committed memory:** approve option **(b)**. Archive the stale committed `.claude/memory/` folder under a clearly dated archived name rather than deleting it.
- **D7 — Mandatory artefact writers:** approve option **(a)**. For the pilot, make durable sprint-workspace writing mandatory for `/arch-council` and `/tester`; introduce the other command integrations incrementally as defined in the plan.
- **D8 — Workflow linting:** approve option **(b)** for the pilot. Implement linting as a standalone script run before `/retro`. Do not add a hook until the script has been proven on at least one complete pilot sprint.
- **D9 — Active sprint count:** approve option **(a)**. Support one active sprint initially, while still supporting multiple active stages within that sprint. Preserve the `active_sprints` list shape so future multi-sprint support does not require a schema redesign.

## Required work

Revise `docs/diagnostics/2026-07-12-nonlinear-icm-sprint-workflow-implementation-plan.md` so that:

1. D1–D9 are marked `APPROVED` with the selected option and date.
2. The document contains no remaining unresolved design decision that blocks implementation.
3. Any issue that is deliberately deferred is moved to a clearly labelled **Post-pilot decisions** section and is not presented as a current blocker.
4. The changeset sequence is implementation-ready and ordered to minimise risk.
5. Every changeset states:
   - exact files created, updated, moved or archived;
   - preconditions;
   - implementation actions;
   - validation steps;
   - rollback steps;
   - expected commit boundary;
   - whether further human approval is required before that changeset starts.
6. Clearly distinguish repository changes from user-home changes under `~/.claude/`.
7. Identify which changes Casper can commit to the repository and which user-home changes must be applied locally by Casper in the active environment.
8. Do not choose or create the pilot sprint workspace until the pilot sprint itself is explicitly selected.
9. Do not modify application code, migrations, domain rules or production configuration.

## Implementation gate

This prompt approves the design decisions and authorises revision of the implementation plan only.

It does **not** authorise implementation of the changesets.

At the end, report using this exact format:

```text
ICM implementation decision pass complete

Primary file:
docs/diagnostics/2026-07-12-nonlinear-icm-sprint-workflow-implementation-plan.md

Status:
implementation-ready, awaiting run approval

Commit SHA:
<sha>

Decisions still requiring human direction:
<none, or list only genuine remaining blockers>

Recommended first implementation changeset:
<changeset ID and title>
```
