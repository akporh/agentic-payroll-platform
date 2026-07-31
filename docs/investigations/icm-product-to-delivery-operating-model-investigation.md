# ICM Product-to-Delivery Operating Model Investigation

## Purpose

Investigate the product hierarchy, repository structure, ICM sprint workflow and completed sprint evidence that currently exist in this repository.

The goal is to reconstruct the actual product-to-delivery operating model before proposing any new agents, workflow stages, governance controls or documentation structures.

This is an investigation and recommendation task only.

Do not implement changes, create new agents, modify the workflow, restructure files or update governance policies during this run.

## Background

The current ICM sprint process has recently been reviewed and its files and workflow have been structured.

Two possible governance capabilities have since been identified for consideration:

1. **Documentation stewardship**, potentially covering documentation drift, ADR maintenance, architecture documentation, roadmap updates, product hierarchy updates and API documentation.
2. **Release management**, potentially covering completed-story checks, test evidence, documentation readiness, changelogs, versioning, deployment readiness and post-deployment verification.

These must not be assumed to be missing.

The repository may already contain some or all of these responsibilities under existing stages, artefacts, checks, conventions or implicit practices.

The investigation must determine what actually exists before recommending changes.

## Primary question

Based on the product hierarchy, repository structure, workflow definitions and completed sprint evidence that exist today:

> How does work currently flow from product intent through delivery and towards release, where can traceability or governance drift occur, and what minimal enhancements, if any, are required to maintain a trustworthy product-to-delivery lifecycle?

## Investigation scope

### 1. Reconstruct the product hierarchy

Inspect how the repository currently represents and connects:

- product vision;
- strategy or product thesis;
- intended outcomes;
- roadmap items;
- initiatives or programmes;
- epics;
- features or capabilities;
- stories;
- acceptance criteria;
- implementation work;
- release or deployment artefacts;
- adoption and outcome evidence.

Determine:

- which of these levels actually exist;
- where they are stored;
- how they are named;
- how parent-child relationships are recorded;
- how status is represented;
- whether status updates propagate through the hierarchy;
- whether completed implementation can be traced back to product intent;
- whether product artefacts can become stale relative to delivery reality.

Do not impose a generic hierarchy where the repository uses a different model. Describe the model that actually exists.

### 2. Reconstruct the current ICM sprint workflow

Inspect the current workflow and stage definitions, including where applicable:

- roadmap;
- product management;
- architecture;
- architecture council or review;
- implementation;
- verification;
- security;
- audit;
- testing;
- retrospective;
- sprint closure;
- critic review;
- human decision gates;
- rework loops;
- skip and parallelisation rules.

For each stage, identify:

- its purpose;
- entry conditions;
- inputs;
- responsibilities;
- outputs;
- evidence produced;
- completion conditions;
- authority to block or return work;
- links to other stages;
- links to the product hierarchy;
- links to release or deployment activity.

### 3. Inspect real sprint evidence

Do not assess the process only from policy or template files.

Inspect completed and recent sprint artefacts to determine how the workflow has actually been used.

Review, where available:

- sprint context files;
- state files;
- decisions;
- implementation plans;
- architecture outputs;
- verification evidence;
- security and audit evidence;
- test results;
- retrospectives;
- closure evidence;
- commit references;
- story or feature mappings;
- release-related records.

Compare the documented workflow with actual execution.

Identify responsibilities that are described in theory but are not consistently evidenced in completed work.

### 4. Investigate documentation governance

Determine how the repository currently handles:

- documentation impact identification;
- documentation drift;
- ADR creation and maintenance;
- superseded architectural decisions;
- architecture diagrams and current-state documentation;
- API documentation;
- schemas and data contracts;
- product hierarchy status updates;
- roadmap updates;
- runbooks and operational documentation;
- obsolete or contradictory documents;
- links between code changes and affected documentation.

Assess whether these responsibilities are:

1. already implemented and explicit;
2. implemented but implicit;
3. partially implemented;
4. genuinely absent.

Determine whether documentation responsibilities currently sit within:

- individual sprint stages;
- story completion;
- sprint closure;
- architecture review;
- retrospective;
- programme governance;
- informal practice;
- or nowhere identifiable.

### 5. Investigate release and deployment governance

Determine what currently happens after implementation and sprint verification.

Inspect whether the repository defines or evidences:

- the distinction between story completion, sprint completion and release completion;
- release candidate assembly;
- release scope or manifests;
- dependency checks;
- integration and regression checks;
- migration readiness;
- compatibility checks;
- configuration and feature-flag readiness;
- changelog updates;
- release notes;
- version changes;
- deployment instructions;
- rollback or roll-forward planning;
- production approval;
- deployment evidence;
- smoke tests or post-deployment verification;
- monitoring and operational readiness;
- release-to-story and release-to-feature traceability.

Establish whether the current process assumes:

- every sprint is released;
- every completed story is released;
- release occurs outside the sprint;
- or release management is not formally represented.

Again, classify each responsibility as explicit, implicit, partial or absent.

### 6. Inspect adjacent lifecycle responsibilities

Assess whether the current operating model covers or omits:

- quality and verification ownership;
- security and compliance triggers;
- data migration and historical compatibility;
- dependency and integration governance;
- operational readiness;
- production support;
- post-release adoption measurement;
- outcome validation;
- feature deprecation and retirement;
- technical debt and architecture-health review.

Do not automatically recommend new agents for these areas.

Identify only responsibilities that are materially relevant to the current system and unsupported by existing controls.

## Required analysis

### A. Current-state operating model

Produce a grounded description of how work currently flows through the repository.

Show the actual path from the highest available level of product intent through:

- product hierarchy;
- story selection;
- sprint execution;
- architecture;
- implementation;
- verification;
- documentation;
- sprint closure;
- release or deployment, where present;
- post-release feedback, where present.

Clearly distinguish:

- formally defined behaviour;
- behaviour evidenced in completed sprints;
- inferred or informal practice;
- missing information.

### B. Responsibility coverage matrix

Create a matrix covering at least:

- product hierarchy maintenance;
- roadmap maintenance;
- architecture governance;
- ADR maintenance;
- API and technical documentation;
- implementation;
- verification;
- security;
- audit;
- test evidence;
- sprint closure;
- release readiness;
- deployment;
- post-deployment verification;
- operational readiness;
- adoption and outcome measurement.

For each responsibility, identify:

- current owner or stage;
- existing artefact or evidence;
- current trigger;
- status: explicit, implicit, partial or absent;
- risk if left unchanged.

### C. Documentation Steward assessment

Evaluate the proposed Documentation Steward capability.

Answer:

- Which proposed responsibilities already exist?
- Which are distributed across existing stages?
- Which lack a clear owner?
- Which require continuous activity rather than an end-stage review?
- Which could be automated?
- Would a separate agent add value, or would it duplicate existing responsibilities?
- Would the better solution be an existing-stage extension, a conditional review, a checklist, automated linting, a named responsibility or a dedicated agent?

Do not recommend a Documentation Steward solely because the name sounds appropriate.

### D. Release Manager assessment

Evaluate the proposed Release Manager capability.

Answer:

- What release responsibilities already exist?
- Is there a current release process, even if informal?
- Is sprint closure currently being treated as release readiness?
- Does every sprint currently correspond to a deployment in practice?
- Which release checks belong inside a sprint?
- Which belong at the sprint boundary?
- Which belong to a distinct release process?
- Would a dedicated agent add value, or could existing stages and automated checks provide sufficient control?

### E. Boundary analysis

Clearly distinguish the units of governance:

- product planning;
- story;
- sprint;
- release;
- deployment;
- production operation;
- outcome review;
- long-term platform governance.

For each unit, explain:

- what is currently in scope;
- what should reasonably remain out of scope;
- where hand-offs occur;
- where the current process has ambiguity or overlap.

### F. Gap classification

For every proposed gap, classify it as one of:

1. No gap — already implemented.
2. Naming or visibility gap.
3. Ownership gap.
4. Trigger gap.
5. Evidence gap.
6. Automation gap.
7. Workflow gap.
8. Lifecycle boundary gap.
9. Genuine missing capability.

Do not describe something as missing merely because it is not implemented as a dedicated stage or agent.

## Recommendation principles

Any recommendations must follow these principles:

- Preserve the current ICM structure where it already works.
- Avoid duplicate stages, checks and ownership.
- Prefer extending an existing control over creating a new agent.
- Prefer conditional triggers over mandatory heavyweight reviews.
- Separate responsibilities from the mechanism used to perform them.
- Treat agents, stages, checklists, automated validations and human gates as alternative implementation mechanisms.
- Introduce the smallest coherent change that closes a confirmed gap.
- Do not couple sprint completion and production release unless repository evidence supports that policy.
- Do not recommend a full programme unless the findings show that the required changes are sufficiently broad, risky or interdependent to justify one.

## Required output

Produce a single investigation report with the following sections:

1. Executive conclusion.
2. Repository sources inspected.
3. Current product hierarchy.
4. Current ICM sprint workflow.
5. Evidence from completed sprints.
6. Current product-to-delivery operating model.
7. Responsibility coverage matrix.
8. Documentation governance findings.
9. Release and deployment governance findings.
10. Adjacent lifecycle findings.
11. Confirmed gaps and their classifications.
12. Documentation Steward verdict.
13. Release Manager verdict.
14. Sprint-versus-release boundary recommendation.
15. Minimal-change enhancement options.
16. Recommended option and rationale.
17. Whether implementation should be:
    - a small direct workflow change;
    - a focused design task;
    - or a separate governed programme.
18. Human decisions required before any implementation.

For every material finding:

- cite the repository file or artefact that supports it;
- distinguish evidence from inference;
- identify when no evidence could be found;
- avoid claims based only on generic software-delivery practice.

## Constraints

- Read-only investigation.
- Do not modify files.
- Do not create or update agents.
- Do not alter the stage registry or workflow.
- Do not add new documentation structures.
- Do not commit or push changes.
- Do not assume the proposed Documentation Steward or Release Manager should exist.
- Do not design the future state before documenting the current state.
- Do not rely only on templates; inspect actual sprint execution evidence.
- Stop and report if the relevant product hierarchy or workflow sources cannot be located rather than inventing a structure.

The final report should be suitable for a human design decision on whether any change is needed and, if so, whether it should be handled as a small enhancement or a separate programme.
