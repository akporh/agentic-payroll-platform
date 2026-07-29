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
- Where does a given story's authoritative acceptance criteria live?

On that last question, the answer differs by how the story came into existence (D-018, 2026-07-28): a **retro-migrated** story's authoritative acceptance criteria stay in its original sprint story file, and the hierarchy record summarises and links to them; a **forward-authored** story — written by the PM into the hierarchy, with no prior sprint file — carries its acceptance criteria natively in its own record. Retro records are therefore deliberately not standalone-complete; forward records are.

The programme also retrospectively reconstructs delivered stories from repository evidence (roadmap, story files, test reports, audit reports, git history) without rewriting history and without presenting inference as fact.

## Scope

In scope:

- Establishing programme governance controls (this file, `POLICY.md`, `PHASES.md`, `state.md`, `decisions.md`, `exceptions.md`).
- Running a read-only discovery phase that inventories delivered work and proposes (but does not adopt) a product hierarchy and repository structure.
- Producing a decision pack of genuine human decisions required before any structural change is made.

Out of scope for this programme's current authorised phase (`hierarchy completion`, D-022):

- Migrating any further historical story into `docs/product/`. Phase 4 remains unauthorised and is additionally gated behind Phase 3B's human sign-off.
- Modifying production code, `docs/ROADMAP.md`, existing sprint workspaces, or existing historical story files.
- Rewriting any historical record.

*Amendment note (2026-07-28):* this list previously also excluded "creating the final `docs/product/` hierarchy or individual story files," which was accurate at bootstrap but superseded by Phase 3 (D-014) and Phases 4A/4B (D-015, D-016). The live scope constraint is always the active phase's `allowed paths` in `PHASES.md`.

## Current phase

`hierarchy completion` (Phase 3B) — authorised 2026-07-28 by D-022.

*Amendment note (2026-07-28):* this field read `discovery` until now, having never been advanced as the programme moved through Phases 2, 3, 4A and 4B. `state.md` and `phase-inputs.yaml` carried the accurate position throughout. Corrected here; `state.md` remains the authoritative phase-state file.

## Status

`active`

## Intended phases

1. **discovery** — inventory delivered work from repository evidence; propose (not adopt) a hierarchy model and repository structure. *Authorised.*
2. **hierarchy approval** — human reviews the decision pack and approves (or amends) the terminology, model, and repository information architecture. *Not authorised.*
3. **structure implementation** — create the approved `docs/product/` (or equivalent) structure and registries, empty of historical content. *Complete (D-014).*
3B. **hierarchy completion** — define the complete outcome/capability/feature hierarchy across the whole 148-item inventory, top-down, and get it signed off; then apply it with the story re-key and readability fixes. Added 2026-07-28. *Authorised and active (D-022).*
4. **historical migration** — populate the approved structure with reconstructed historical stories, under the approved confidence and classification rules. *Phases 4A (D-015) and 4B (D-016) complete for their bounded scope; the remainder is **not authorised**, and is additionally gated behind Phase 3B's human sign-off.*
5. **sprint-workflow integration** — wire the new product layer into the ICM sprint workflow (`docs/sprints/`) so future sprints write traceability links as a normal part of sprint closure. *Not authorised.*

Each phase requires an explicit human authorisation recorded in `decisions.md` before it may begin. *(This originally read "Only phase 1 is authorised by this bootstrap" — accurate at bootstrap, superseded by the authorisation table in `PHASES.md`.)*

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
