# Plan the Non-Linear ICM Sprint Workflow Implementation

Read:

- `docs/diagnostics/2026-07-11-sprint-workflow-icm-diagnostic.md`
- `docs/diagnostics/2026-07-11-prompt-revise-sprint-workflow-icm-target-model.md`
- the current sprint workflow instructions, skills, hooks and memory files referenced by the diagnostic
- the existing ICM-style structures in:
  - `docs/audit-program/`
  - `docs/agentic-architecture-review/`

Do not implement the workflow yet. Do not modify application code.

## Objective

Produce a concrete, minimal implementation plan for the approved non-linear ICM sprint-workflow target model.

The implementation must support:

- multiple active stages;
- dependency-based routing;
- parallel-compatible stages;
- conditional and optional stages;
- explicit `skipped` and `not-applicable` states;
- rework loops;
- durable HITL decisions;
- repository-based fresh-session resumability;
- stage-specific evidence without building a workflow engine.

## Planning scope

Plan the introduction of:

```text
docs/sprints/
├── CURRENT.md
├── WORKFLOW.md
├── STAGE-REGISTRY.md
└── <pilot-sprint-id>/
    ├── CONTEXT.md
    ├── state.md
    ├── decisions.md
    └── evidence/
```

Add conditional artefacts such as `plan.md`, `architecture.md`, `verification.md`, `audit.md` and `retrospective.md` only when their stages run.

Use the next real sprint as the pilot. Do not plan a historical backfill of all previous sprints unless required for correctness.

## Required analysis

Identify:

1. Every new file to create.
2. Every existing file, skill, hook or instruction source that must change.
3. Which rules currently exist only in memory, conversation history or user-home files.
4. Which of those rules must become repository-visible for correct fresh-session execution.
5. Which rules should remain in reusable skills rather than sprint files.
6. How each existing command interacts with the new workspace, including:
   - `/roadmap`
   - `/pm`
   - `/architect`
   - `/arch-council`
   - plan mode
   - implementation
   - `/verify`
   - `/security`
   - `/auditor`
   - `/tester`
   - `/retro`
7. How state transitions and HITL decisions are recorded.
8. How parallel stages avoid overwriting evidence.
9. How skipped stages are reactivated when scope or evidence changes.
10. How rework blocks only dependent stages.
11. How the system behaves when state is missing, inconsistent or stale.
12. Which checks should be deterministic scripts or hooks rather than model judgement.

## Required implementation plan

Produce an ordered, reviewable plan with small changesets.

For each changeset provide:

| Field | Required content |
|---|---|
| Changeset ID | Stable identifier |
| Purpose | Outcome of the changeset |
| Files created | Exact paths |
| Files updated | Exact paths |
| Behaviour introduced | What changes operationally |
| Dependencies | Earlier changesets or decisions required |
| Validation | How the change will be verified |
| Rollback | How to revert safely |
| Risk | Low, medium or high |

The plan should separate at least:

1. Shared static workflow definitions.
2. Pilot sprint workspace creation.
3. Command and skill integration.
4. Plan and architecture verdict persistence.
5. Verification, audit and evidence persistence.
6. HITL decision recording.
7. Mechanical validation or linting.
8. Pilot execution and retrospective.

## Human decisions required

Explicitly call out every decision that requires approval before implementation.

At minimum assess whether approval is required for:

- the pilot sprint ID and scope;
- the authoritative source for stage applicability rules;
- whether persona files must be copied into the repository;
- whether global or project `CLAUDE.md` files are changed;
- whether user-home plan files are copied or moved;
- whether the stale committed `.claude/memory/` folder is deleted or archived;
- which commands must write mandatory artefacts;
- whether workflow-state linting is implemented as a hook, script or CI check;
- whether more than one active sprint is supported in the first implementation.

Use this table:

| Decision ID | Decision required | Options | Recommendation | Consequence of deferral |
|---|---|---|---|---|

## Pilot acceptance criteria

Define acceptance criteria proving that a fresh Casper session can determine from the repository alone:

- which sprint is active;
- which stages are active, blocked, complete, skipped or not applicable;
- what has been approved;
- what evidence exists;
- what decisions were made and by whom;
- what work may proceed in parallel;
- what is currently blocked;
- what the next permitted actions are.

Also require a test scenario covering:

- one skipped stage;
- one not-applicable stage;
- two parallel stages;
- one rework loop;
- one unresolved dependency;
- one invalid `decision_ref` caught mechanically.

## Output

Create a new implementation-plan document in `docs/diagnostics/` with `implementation-plan` in the filename.

The document must include:

1. Executive summary.
2. Assumptions.
3. Decisions requiring human approval.
4. Exact target file inventory.
5. Ordered changesets.
6. Command/skill integration matrix.
7. Validation plan.
8. Rollback plan.
9. Pilot acceptance criteria.
10. Explicit statement that no implementation has occurred.

Do not implement any proposed changes until the plan has been reviewed and approved.