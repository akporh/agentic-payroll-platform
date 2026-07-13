# Casper Prompt — Retrospective Product Story and Hierarchy Discovery

Begin retrospective product-story discovery and product hierarchy design.

Repository:
`agentic-payroll-platform`

## Purpose

Build a durable product-management layer above the existing sprint workflow.

The existing ICM sprint structure records execution:

`docs/sprints/<sprint-id>/`
- `CONTEXT.md`
- `state.md`
- `decisions.md`
- `plan.md`
- `evidence/`
- stage outputs

The new product layer must record long-lived product intent and relationships:

Outcome
→ Epic or capability
→ Feature
→ User story
→ Delivery sprint(s)

Do not create the final `docs/product` hierarchy or individual story files during this discovery pass.

## Primary objectives

1. Identify product work already delivered.
2. Reconstruct the likely user stories represented by that work.
3. Group stories into coherent features, epics/capabilities and outcomes.
4. Design a sustainable repository structure for future product management.
5. Clearly distinguish confirmed information from inferred classification.

## Sources to inspect

- `docs/ROADMAP.md`
- `docs/stories/`
- `docs/sprints/`
- `docs/audit-program/`
- `docs/agentic-architecture-review/`
- `docs/audit/`
- `docs/test-reports/`
- `docs/retro-reports/`
- implementation plans
- relevant architecture documents
- git history
- product-code changes and associated tests

Do not rely on commit titles alone.

## Part 1 — Delivered-work inventory

Create an inventory of delivered product changes.

For every candidate item record:

- provisional story ID;
- title;
- plain-language description;
- likely user or actor;
- problem addressed;
- delivered behaviour;
- source requirement, finding or roadmap reference;
- implementation evidence;
- test or review evidence;
- delivery sprint or commit references;
- current status;
- confidence:
  - confirmed
  - strongly inferred
  - tentative
  - requires human classification;
- unresolved questions.

Do not invent quantified benefits or user needs that are not supported by evidence.

## Part 2 — Story reconstruction

For each delivered product change, draft a candidate user story:

As a `<user or actor>`,
I want `<capability or behaviour>`,
so that `<supported outcome>`.

Where that format would be artificial or misleading, use a job story or technical-enabler format instead.

Classify each item as one of:

- user-facing story;
- operational story;
- compliance story;
- platform capability;
- technical enabler;
- defect/remediation;
- discovery or architecture item.

Do not force every technical change into a fictional end-user story.

## Part 3 — Hierarchy proposal

Propose the product hierarchy:

Outcome
→ Epic or capability
→ Feature
→ Story

For each proposed outcome provide:

- ID;
- name;
- business intent;
- measurable or observable result;
- included epics/capabilities.

For each epic/capability provide:

- ID;
- name;
- scope;
- parent outcome;
- included features.

For each feature provide:

- ID;
- name;
- product behaviour;
- parent epic/capability;
- included stories;
- status summary.

Identify any stories that could reasonably belong to more than one feature and explain the preferred ownership.

## Part 4 — Repository information architecture

Compare at least two storage models:

### A. Flat registries plus individual story files

`docs/product/`
- `README.md`
- `OUTCOMES.md`
- `EPICS.md`
- `FEATURES.md`
- `STORY-REGISTRY.md`
- `stories/`

### B. Deeply nested outcome/epic/feature/story folders

Recommend one model for this repository.

The recommendation must consider:

- navigation by a product owner;
- agent discoverability;
- stories delivered across multiple sprints;
- features spanning several releases;
- stable identifiers;
- avoiding duplicated sources of truth;
- ease of automated validation;
- migration cost for existing work.

## Part 5 — Source-of-truth rules

Define ownership clearly:

- product hierarchy owns intent, scope and long-lived status;
- story file owns story definition and acceptance criteria;
- sprint `CONTEXT.md` owns the selected execution scope;
- sprint `state.md` owns workflow stage state;
- sprint `decisions.md` owns HITL routing decisions;
- sprint evidence owns delivery proof.

Define how a sprint references stories and how a story records multiple delivery sprints.

## Part 6 — Retrospective migration plan

Propose a phased migration:

### Phase 1
Create product registries and classify confirmed delivered stories.

### Phase 2
Review inferred stories with the human product owner.

### Phase 3
Create approved individual story files.

### Phase 4
Link historical sprint workspaces and implementation evidence.

### Phase 5
Update `/pm` and sprint `CONTEXT.md` conventions so future sprints reference stable story IDs.

Include safeguards:

- do not rewrite completed sprint history;
- do not change original acceptance criteria silently;
- preserve original roadmap/audit references;
- mark uncertain classifications explicitly;
- allow stories to be split or merged only through recorded decisions.

## Output

Create:

`docs/diagnostics/2026-07-13-retrospective-product-story-and-hierarchy-discovery.md`

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

Do not modify:

- `docs/sprints/`
- `docs/ROADMAP.md`
- production code
- user-home skills
- existing historical story files

Commit and push only the discovery document to `origin/uat`.

## Report

Retrospective product-story discovery complete

Primary file:
`<path>`

Delivered items identified:
`<count>`

Confirmed stories:
`<count>`

Inferred stories:
`<count>`

Proposed outcomes:
`<count and names>`

Proposed epics/capabilities:
`<count>`

Proposed features:
`<count>`

Recommended structure:
`<summary>`

Highest-priority human decisions:
`<list>`

Repository commit SHA:
`<sha>`

Next gate:
Product hierarchy and migration approval
