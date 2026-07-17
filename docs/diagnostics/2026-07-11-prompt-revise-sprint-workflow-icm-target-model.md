# Revise Sprint Workflow Target Model for Non-Linear Execution

Read:

- `docs/diagnostics/2026-07-11-sprint-workflow-icm-diagnostic.md`
- the current sprint workflow instructions and skills referenced by that diagnostic
- the existing ICM-style structures in:
  - `docs/audit-program/`
  - `docs/agentic-architecture-review/`

Do not modify application code.

## Objective

Revise the diagnostic’s recommended target model so it accurately supports a sprint workflow that is:

- non-linear;
- able to run multiple stages in parallel;
- able to skip stages when they are not applicable;
- able to revisit earlier stages;
- able to branch based on project type, risk, findings or human judgement;
- governed by explicit HITL decisions;
- resumable from repository state without relying on chat history or hidden memory.

The existing recommendation is too linear because it assumes:

```text
current sprint → current stage
```

Replace this with:

```text
current sprint
    → active stage set
    → dependency graph
    → gates
    → recorded routing decisions
    → completion and evidence state
```

## Required design principles

The revised model must preserve these principles:

1. ICM does not require a fixed sequential pipeline.
2. Numbered folders may be retained for readability, but must not imply mandatory execution order.
3. Each stage must define:
   - purpose;
   - entry conditions;
   - required inputs;
   - outputs;
   - completion criteria;
   - applicability rules;
   - dependencies;
   - permitted parallel stages;
   - human gates;
   - evidence requirements.
4. Stages may have statuses such as:
   - `not-started`;
   - `eligible`;
   - `active`;
   - `blocked`;
   - `complete`;
   - `skipped`;
   - `not-applicable`;
   - `needs-rework`.
5. Every skipped or not-applicable stage must record:
   - reason;
   - decision owner;
   - decision reference;
   - date;
   - any compensating control.
6. A human decision may:
   - activate a stage;
   - skip a stage;
   - require additional review;
   - return work to an earlier stage;
   - allow parallel execution;
   - block progression.
7. Stage outputs must remain explicit, inspectable repository artefacts.
8. The workflow must distinguish:
   - reusable skill instructions;
   - sprint-specific context;
   - current execution state;
   - human decisions;
   - generated evidence.

## Revise the target structure

Revise Section 7 of the diagnostic so the minimum target structure supports non-linear execution.

Use a structure similar to:

```text
docs/sprints/
├── CURRENT.md
├── WORKFLOW.md
├── STAGE-REGISTRY.md
└── <sprint-id>/
    ├── CONTEXT.md
    ├── state.md
    ├── decisions.md
    ├── plan.md
    ├── architecture.md
    ├── verification.md
    ├── audit.md
    ├── retrospective.md
    └── evidence/
```

Do not assume every file must exist for every sprint. The stage registry should define which artefacts are required by each activated stage.

### `CURRENT.md`

This file should only identify the active sprint workspace or workspaces.

It must not claim that there is always one current stage.

Example:

```yaml
active_sprints:
  - sprint-31
```

### `<sprint-id>/state.md`

This must be the authoritative execution-state record for the sprint.

It should support:

```yaml
sprint: sprint-31
status: active

stages:
  roadmap:
    status: complete

  architecture:
    status: skipped
    reason: isolated low-risk change
    decision_ref: DEC-031-01

  implementation:
    status: active
    depends_on:
      - approved-plan

  verification:
    status: active
    may_run_with:
      - implementation

  security:
    status: not-applicable
    reason: no security-sensitive surface changed
    decision_ref: DEC-031-02

  audit:
    status: blocked
    waiting_for:
      - implementation
      - verification
```

### `WORKFLOW.md`

Define:

- allowed stage transitions;
- dependency rules;
- parallel execution rules;
- rework loops;
- blocking conditions;
- approval gates;
- conditions under which stages may be skipped;
- conditions under which a skipped stage must later be activated.

Do not encode a single mandatory sequence.

### `STAGE-REGISTRY.md`

For every stage, define:

| Field | Meaning |
|---|---|
| Stage ID | Stable identifier |
| Purpose | What the stage achieves |
| Mandatory status | Mandatory, conditional or optional |
| Entry conditions | What must be true before activation |
| Inputs | Required artefacts |
| Outputs | Required artefacts |
| Dependencies | Stages or decisions required first |
| Parallel compatibility | Stages it may run alongside |
| Skip conditions | When it may be skipped |
| Completion criteria | Evidence required to close |
| Human gate | Required decision, if any |

## Required output

Update the diagnostic proposal only. Do not implement the target structure yet.

Produce:

1. A revised executive note explaining that ICM supports a directed stage graph rather than only a linear pipeline.
2. A revised target filesystem structure.
3. A stage-state model.
4. A routing and dependency model.
5. Rules for parallel stages.
6. Rules for skipped and not-applicable stages.
7. Rules for rework loops.
8. Rules for recording HITL decisions.
9. A revised migration plan.
10. A brief comparison:

| Current recommendation | Revised recommendation |
|---|---|
| Current sprint + current stage | Current sprint + active stage set |
| Sequential stage progression | Dependency-based routing |
| One stage at a time | Parallel stages allowed |
| Implicit skipping | Explicit skip decision |
| Linear completion | Graph completion criteria |

## Constraints

- Keep the solution minimal.
- Prefer Markdown and YAML over building a workflow engine.
- Do not duplicate rules already governed by `CLAUDE.md`.
- Do not move reusable skill logic into sprint files.
- Do not implement any repository changes beyond revising the diagnostic document.
- Clearly mark the revised model as a proposal requiring human approval.
