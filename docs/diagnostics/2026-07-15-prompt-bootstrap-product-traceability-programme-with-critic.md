# Prompt — Bootstrap the Product Traceability Programme with an Independent Critic Gate

Begin the Product Traceability Programme.

Important status:

- No product-traceability prompt has yet been run.
- Do not execute the earlier retrospective discovery prompt directly.
- This prompt supersedes it by establishing the programme controls first, then running the discovery phase under those controls.

Repository:

`agentic-payroll-platform`

## Objective

Create a durable product-management and traceability layer above the existing ICM sprint workflow so that the repository can answer:

- What outcomes are we pursuing?
- Which epics or capabilities support those outcomes?
- Which features belong to those epics or capabilities?
- Which stories make up each feature?
- Which stories have been delivered?
- In which sprint or sprints were they delivered?
- What evidence proves delivery?

The programme must also retrospectively reconstruct delivered stories from repository evidence without rewriting history or presenting inference as fact.

## Operating model

Use **phase-level autonomy with an independent critic gate**.

The executor may complete the entire authorised discovery phase without requesting intermediate confirmation.

The executor must not write its own unrestricted continuation prompt, approve its own recommendations, or execute the next phase.

The critic must be read-only and independent from the executor role. The critic reviews the executor's outputs against fixed programme policy and a fixed rubric. The critic does not edit the executor's artefacts and does not authorise execution.

The human remains the final approver for consequential product and governance decisions.

## Required programme structure

Create:

```text
docs/programmes/product-traceability/
├── PROGRAMME.md
├── POLICY.md
├── PHASES.md
├── state.md
├── decisions.md
├── exceptions.md
├── decision-pack.md
├── phase-inputs.yaml
├── critic-review.md
└── runs/
    └── discovery-run-001.md
```

Do not create the final `docs/product/` hierarchy or individual story files in this phase.

## Source-of-truth boundaries

The following ownership model is fixed for this programme unless the human later approves a change:

- Product hierarchy owns long-lived intent, relationships and status.
- Story records own story definition and authoritative acceptance criteria.
- Sprint `CONTEXT.md` owns selected execution scope for that sprint.
- Sprint `state.md` owns workflow-stage state.
- Sprint `decisions.md` owns HITL routing and skip decisions.
- Sprint evidence and stage outputs own delivery proof.
- Completed sprint history must not be rewritten to make the new model appear to have existed earlier.

## File 1 — PROGRAMME.md

Define:

- programme ID: `product-traceability`
- objective;
- scope;
- current phase: `discovery`;
- status: `active`;
- intended phases:
  1. discovery;
  2. hierarchy approval;
  3. structure implementation;
  4. historical migration;
  5. sprint-workflow integration;
- success criteria;
- relationship to the existing ICM sprint workflow.

## File 2 — POLICY.md

This is the fixed execution policy. The executor must not weaken it.

### Autonomy mode

`phase-autonomous-with-exception-escalation`

### Executor may

- inspect repository evidence;
- read git history;
- create programme-control and discovery documents under the approved paths;
- create provisional classifications with explicit confidence levels;
- run read-only searches and validation commands;
- correct formatting and mechanical defects within the approved files;
- commit and push authorised discovery-phase outputs;
- continue through the discovery phase without intermediate confirmation.

### Executor may not

- modify production code;
- modify frontend or backend application code;
- modify existing sprint history;
- modify `docs/ROADMAP.md`;
- modify existing historical story files;
- create the final `docs/product/` structure;
- classify tentative items as confirmed without evidence;
- merge or split historical stories as a final decision;
- modify user-home skills;
- add dependencies;
- expand the authorised file scope;
- write a free-form next-run prompt;
- execute a later phase;
- treat its recommendation as human approval.

### Human approval required for

- the hierarchy terminology and model;
- the repository information architecture;
- source-of-truth changes;
- ambiguous story classification;
- merges or splits of historical stories;
- migration scope;
- any production-code or user-home-skill changes;
- authorisation to begin the next phase.

### Stop conditions

Stop and record an exception only when:

- authoritative sources materially contradict one another;
- sensitive or personal information is discovered;
- the phase cannot be completed within the authorised paths;
- a destructive or irreversible change would be required;
- the requested evidence cannot be accessed;
- more than 10% of identified items cannot be classified even provisionally;
- validation fails and cannot be corrected within scope.

Routine naming, formatting, evidence collection and provisional classification questions are not stop conditions.

## File 3 — PHASES.md

Define the full programme phases in advance, but authorise only `discovery`.

For each phase record:

- phase ID;
- purpose;
- allowed paths;
- forbidden paths;
- required inputs;
- required outputs;
- required validations;
- human gate before or after;
- executor and critic responsibilities.

The discovery phase may modify only:

```text
docs/diagnostics/
docs/programmes/product-traceability/
```

All application-code paths, existing sprint workspaces and existing product-history documents are read-only inputs.

## File 4 — state.md

Record:

- current phase;
- executor status;
- critic status;
- human-gate status;
- completed outputs;
- blocked or outstanding decisions;
- next permitted action.

The final discovery state must not claim the next phase is authorised.

## File 5 — decisions.md

Create a programme-level decision register.

Record only actual approved decisions. Recommendations must remain in `decision-pack.md` until human approval.

At initialisation, record the approved governance decisions contained in this prompt, including:

- phase-level autonomy;
- executor/critic separation;
- no free-form executor-authored continuation prompt;
- human authority over consequential decisions;
- fixed source-of-truth boundaries;
- discovery-only authorisation.

## File 6 — exceptions.md

Use a structured schema for any stop-condition event:

- exception ID;
- phase;
- type;
- evidence;
- affected items;
- options;
- executor recommendation;
- effect of deferral;
- exact human decision required.

If no exception occurs, state that explicitly.

## Discovery work

After the controls above are created, execute the retrospective product-story discovery phase.

Inspect at least:

- `docs/ROADMAP.md`
- `docs/stories/`
- `docs/sprints/`
- `docs/audit-program/`
- `docs/agentic-architecture-review/`
- `docs/audit/`
- `docs/test-reports/`
- `docs/retro-reports/`
- implementation plans;
- relevant architecture documents;
- git history;
- associated backend and frontend changes;
- associated tests.

Do not rely on commit titles alone.

Create:

`docs/diagnostics/2026-07-15-retrospective-product-story-and-hierarchy-discovery.md`

Required sections:

1. Executive summary
2. Current product-documentation landscape
3. Delivered-work inventory
4. Candidate reconstructed stories
5. Proposed outcomes
6. Proposed epics or capabilities
7. Proposed features
8. Story-to-feature mapping
9. Recommended repository structure
10. Source-of-truth rules
11. Historical migration plan
12. Future sprint integration
13. Human decisions required
14. Risks and unresolved classification questions

## Delivered-work inventory requirements

For every candidate item record:

- provisional story ID;
- title;
- plain-language description;
- likely actor;
- problem addressed;
- delivered behaviour;
- source requirement, finding or roadmap reference;
- implementation evidence;
- test or review evidence;
- delivery sprint or commit references;
- current status;
- classification:
  - user-facing story;
  - operational story;
  - compliance story;
  - platform capability;
  - technical enabler;
  - defect/remediation;
  - discovery or architecture item;
- confidence:
  - confirmed;
  - strongly inferred;
  - tentative;
  - requires human classification;
- unresolved questions.

Do not invent quantified benefits, original user intent or business outcomes that are not supported by evidence.

Do not force every technical change into fictional user-story wording. Use a job story, platform-capability statement, remediation record or technical-enabler form where more accurate.

## Hierarchy analysis

Assess at least these models:

- Outcome → Epic → Feature → Story
- Outcome → Capability → Feature → Story
- a hybrid where epic is a delivery construct and capability is a durable product construct.

Recommend one model for this repository and explain the trade-offs.

Compare at least:

### Model A — flat registries plus individual story files

```text
docs/product/
├── README.md
├── OUTCOMES.md
├── CAPABILITIES.md or EPICS.md
├── FEATURES.md
├── STORY-REGISTRY.md
└── stories/
```

### Model B — deeply nested outcome/capability/feature/story folders

Evaluate:

- product-owner navigation;
- agent discoverability;
- stable identifiers;
- stories delivered across multiple sprints;
- features spanning several releases;
- duplication risk;
- automated validation;
- migration cost.

## Decision pack

Create:

`docs/programmes/product-traceability/decision-pack.md`

It must contain only genuine human decisions, grouped and prioritised.

For each decision include:

- decision ID;
- question;
- available options;
- executor recommendation;
- supporting evidence;
- consequences of each option;
- default outcome if deferred;
- whether it blocks the next phase.

Do not ask the human to approve routine formatting or mechanical details.

## Phase inputs

Create:

`docs/programmes/product-traceability/phase-inputs.yaml`

This file may contain factual parameters only:

- recommended next phase ID;
- authoritative input files;
- proposed allowed paths;
- proposed outputs;
- discovered counts;
- confirmed, inferred and unresolved item counts;
- approved decision IDs;
- unresolved decision IDs;
- proposed validation commands;
- exception IDs, if any.

It must not:

- redefine policy;
- weaken stop conditions;
- grant new permissions;
- convert recommendations into approval;
- contain a prose continuation prompt.

## Independent critic review

After the executor completes all discovery outputs, run a separate critic role.

The critic must be read-only.

The critic must review:

- `PROGRAMME.md`
- `POLICY.md`
- `PHASES.md`
- `state.md`
- `decisions.md`
- `exceptions.md`
- the discovery document;
- `decision-pack.md`;
- `phase-inputs.yaml`;
- repository evidence cited by the executor.

The critic must check for:

- scope expansion;
- missing guardrails;
- contradictions with programme policy;
- unsupported claims;
- weak or missing evidence;
- recommendations presented as approved decisions;
- confidence inflation;
- forced user-story wording for technical work;
- omitted migration risks;
- duplicated sources of truth;
- missing validation;
- unnecessary human gates;
- unresolved decisions hidden in implementation detail;
- proposed permissions broader than the approved phase.

Create:

`docs/programmes/product-traceability/critic-review.md`

Required critic format:

```text
Verdict:
approve-for-human-review | approve-with-amendments | reject

Critical issues:
...

Evidence gaps:
...

Guardrail gaps:
...

Unsupported assumptions:
...

Required amendments before human review:
...

Human decisions still required:
...
```

The critic may not edit the executor's artefacts. If amendments are required, the executor may make only the critic-requested amendments within discovery scope, after which the critic must re-review and record the final verdict.

The critic does not approve the next phase. A positive verdict means only that the package is suitable for human review.

## Run record

Create:

`docs/programmes/product-traceability/runs/discovery-run-001.md`

Record:

- start and end state;
- files inspected;
- files created;
- validation commands;
- executor findings;
- critic verdict;
- amendments made after criticism;
- commit SHA or SHAs;
- outstanding human decisions;
- next permitted action.

## Validation

Before completion:

- confirm no production code changed;
- confirm no existing sprint workspace changed;
- confirm `docs/ROADMAP.md` was not modified;
- confirm no user-home skill changed;
- confirm all cited repository paths exist where practical;
- run `git diff --check`;
- verify the decision pack contains recommendations, not false approvals;
- verify `phase-inputs.yaml` contains no new permissions;
- verify the critic was run after executor outputs existed;
- verify programme state remains at the human gate.

## Commit and push

Commit and push authorised discovery-phase outputs to `origin/uat` in coherent commit boundaries.

Do not request intermediate commit confirmation.

Do not execute the next phase.

## Final report

Report once at the end unless a stop condition occurs.

Use:

```text
Product traceability discovery phase complete

Programme controls created:
<paths>

Primary discovery file:
<path>

Delivered items identified:
<count>

Confidence summary:
<confirmed / strongly inferred / tentative / human-classification counts>

Proposed hierarchy:
<summary>

Recommended repository structure:
<summary>

Critic verdict:
<verdict and key amendments>

Exceptions:
<none or IDs>

Human decisions required:
<decision IDs and short descriptions>

Repository commit SHA(s):
<sha(s)>

Programme state:
awaiting human decision-pack approval

Next permitted action:
human review only — no implementation authorised
```
