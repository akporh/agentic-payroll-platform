# Programme — Product Traceability

## Programme ID

`product-traceability`

## Objective

Create a durable product-management and traceability layer above the existing ICM sprint workflow (`docs/sprints/`, `docs/sprints/STAGE-REGISTRY.md`, `docs/sprints/WORKFLOW.md`) so that the repository can answer, at any time, without relying on a single person's memory:

- What outcomes are we pursuing?
- Which epics or capabilities support those outcomes?
- Which features belong to those epics or capabilities?
- Which stories make up each feature?
- Which stories have been delivered?
- In which sprint or sprints were they delivered?
- What evidence proves delivery?

The programme also retrospectively reconstructs delivered stories from repository evidence (roadmap, story files, test reports, audit reports, git history) without rewriting history and without presenting inference as fact.

## Scope

In scope:

- Establishing programme governance controls (this file, `POLICY.md`, `PHASES.md`, `state.md`, `decisions.md`, `exceptions.md`).
- Running a read-only discovery phase that inventories delivered work and proposes (but does not adopt) a product hierarchy and repository structure.
- Producing a decision pack of genuine human decisions required before any structural change is made.

Out of scope for this programme's current authorised phase:

- Creating the final `docs/product/` hierarchy or individual story files.
- Modifying production code, `docs/ROADMAP.md`, existing sprint workspaces, or existing historical story files.
- Migrating or rewriting any historical record.

## Current phase

`discovery`

## Status

`active`

## Intended phases

1. **discovery** — inventory delivered work from repository evidence; propose (not adopt) a hierarchy model and repository structure. *Authorised.*
2. **hierarchy approval** — human reviews the decision pack and approves (or amends) the terminology, model, and repository information architecture. *Not authorised.*
3. **structure implementation** — create the approved `docs/product/` (or equivalent) structure and registries, empty of historical content. *Not authorised.*
4. **historical migration** — populate the approved structure with reconstructed historical stories, under the approved confidence and classification rules. *Not authorised.*
5. **sprint-workflow integration** — wire the new product layer into the ICM sprint workflow (`docs/sprints/`) so future sprints write traceability links as a normal part of sprint closure. *Not authorised.*

Only phase 1 is authorised by this bootstrap. Each subsequent phase requires an explicit human authorisation recorded in `decisions.md` before it may begin.

## Success criteria

- Programme control files exist and are internally consistent with each other and with this prompt's policy.
- The discovery document inventories delivered work with explicit confidence levels and cites verifiable evidence for every item marked `confirmed` or `strongly inferred`.
- No item is classified `confirmed` without direct evidence (code, test, audit report, or explicit roadmap ✅ entry cross-checked against at least one other source).
- The decision pack contains only genuine open decisions, each with options, evidence, and consequences — no recommendation is presented as an approved decision.
- An independent critic reviews the package before it is handed to the human, and the critic's verdict and any resulting amendments are recorded.
- The programme does not authorise its own continuation — `state.md` at the end of discovery names the human gate as the next required action, not an executor-authored next step.

## Relationship to the existing ICM sprint workflow

The ICM sprint workflow (`docs/sprints/STAGE-REGISTRY.md`, `docs/sprints/WORKFLOW.md`) governs how a single sprint's work moves through roadmap → pm → architecture → arch-council → implementation → verification → security → audit → test → retro, and owns sprint-level execution state (`docs/sprints/<sprint>/state.md`, `decisions.md`, `evidence/`).

This programme sits **above** that workflow, not inside it. It does not change sprint-workflow stages, gates, or evidence rules. Its purpose is to answer a question the sprint workflow does not answer on its own: which product-level outcome, epic/capability, feature, and story does a given sprint's delivered work belong to, and where is the cumulative record of that mapping kept. Phase 5 (sprint-workflow integration, not yet authorised) is where a future sprint's `retro` stage would be extended to write a traceability link into the approved product layer — it will be designed and approved separately, not assumed here.
