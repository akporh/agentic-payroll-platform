# Phases — Product Traceability Programme

All five phases are defined here in advance for planning visibility. **Only `discovery` is authorised.** No later phase may begin without a recorded human decision in `decisions.md` authorising it.

---

## Phase 1 — `discovery`

**Status:** complete (2026-07-15 — see `runs/discovery-run-001.md`; critic verdict `approve-for-human-review`)

**Purpose:** Inventory delivered work from repository evidence, propose (not adopt) a product hierarchy model and repository structure, and produce a decision pack of genuine open questions for human approval.

**Allowed paths (read-write):**
```text
docs/diagnostics/
docs/programmes/product-traceability/
```

**Forbidden paths (read-only inputs; no writes):**
```text
backend/
frontend/
migrations/
docs/ROADMAP.md
docs/sprints/
docs/stories/
docs/audit/
docs/audit-program/
docs/agentic-architecture-review/
docs/security/
docs/test-reports/
docs/retro-reports/
docs/design/
docs/analysis/
docs/planning/
~/.claude/ (user-home skills)
requirements.txt, package.json, and all lockfiles
```
All paths not explicitly listed under "Allowed paths" are implicitly forbidden for writes.

**Required inputs:** `docs/ROADMAP.md`, `docs/stories/`, `docs/sprints/`, `docs/audit-program/`, `docs/agentic-architecture-review/`, `docs/audit/`, `docs/test-reports/`, `docs/retro-reports/`, `docs/security/`, `docs/design/ui-decisions.md`, `docs/analysis/`, `docs/planning/`, git history, associated backend/frontend source and tests cited as evidence.

**Required outputs:**
- `docs/programmes/product-traceability/PROGRAMME.md`, `POLICY.md`, `PHASES.md` (this file), `state.md`, `decisions.md`, `exceptions.md`.
- `docs/diagnostics/2026-07-15-retrospective-product-story-and-hierarchy-discovery.md`.
- `docs/programmes/product-traceability/decision-pack.md`, `phase-inputs.yaml`.
- `docs/programmes/product-traceability/critic-review.md`.
- `docs/programmes/product-traceability/runs/discovery-run-001.md`.

**Required validations:** see `runs/discovery-run-001.md` for the executed checklist — no production code changed; no existing sprint workspace changed; `docs/ROADMAP.md` unmodified; no user-home skill changed; cited repository paths exist; `git diff --check` clean; decision pack contains recommendations only, no false approvals; `phase-inputs.yaml` grants no new permissions; critic ran after executor outputs existed; programme state remains at the human gate.

**Human gate:** **after** — the phase completes discovery and a decision pack, then stops. The human reviews the decision pack and critic verdict before Phase 2 may begin.

**Executor responsibilities:** inventory delivered work with cited evidence and explicit confidence; propose (not adopt) hierarchy models; write the decision pack; do not authorise continuation.

**Critic responsibilities:** independently, read-only, review all discovery-phase outputs against this policy and the fixed rubric in the bootstrap prompt; produce `critic-review.md` with a verdict; may not edit executor artefacts; may request amendments, which the executor applies within discovery scope only, followed by critic re-review.

---

## Phase 2 — `hierarchy approval`

**Status:** authorised and complete (2026-07-15, via `docs/diagnostics/2026-07-15-prompt-record-product-traceability-decisions-and-close-phase-2.md`; decisions D-007–D-013 recorded in `decisions.md`; critic verdict recorded in `critic-review-phase-2.md`)

**Purpose:** Human reviews the discovery document and decision pack; approves, amends, or rejects the hierarchy terminology/model and the repository information architecture (Model A / Model B / hybrid / alternative).

**Allowed paths (as executed):**
```text
docs/programmes/product-traceability/
```

**Forbidden paths (as executed):** `docs/product/`, `docs/ROADMAP.md`, `docs/stories/`, `docs/sprints/`, `docs/audit/`, `docs/audit-program/`, `docs/agentic-architecture-review/`, `docs/security/`, `docs/test-reports/`, `docs/retro-reports/`, `backend/`, `frontend/`, `migrations/`, `~/.claude/` — none of these were touched by this phase.

**Required inputs:** Phase 1 outputs (discovery document, decision pack, critic review) — used as the basis for the human decisions.

**Required outputs (delivered):** DP-01–DP-07 recorded as D-007–D-013 in `decisions.md`; `decision-pack.md` annotated with resolutions (original questions/options/recommendations preserved, not erased); `state.md`, `phase-inputs.yaml`, `exceptions.md` updated to reflect Phase 2 closure; `phase-3-inputs.md` created (factual only, no permission granted); `runs/hierarchy-approval-run-001.md` created; `critic-review-phase-2.md` created.

**Required validations:** `git diff --check`; `git status --short`; `find docs/programmes/product-traceability -maxdepth 2 -type f`; `test ! -e docs/product` (confirms Phase 3's structure was never created); direct inspection confirming DP-01–DP-07 each appear exactly once as resolved, all control files agree Phase 2 is complete, Phase 3 remains unauthorised, and DP-04/DP-06 remain visible as open follow-up investigations rather than silently resolved.

**Human gate:** **before** — the human's decisions (recorded in the bootstrap-decision prompt) were the trigger for this phase's execution; the executor recorded them faithfully rather than proposing or reinterpreting them.

**Executor responsibilities:** record the exact decisions supplied; close programme control files accurately; do not erase the historical decision-pack trail; do not authorise Phase 3; prepare factual (not permission-granting) Phase 3 inputs.

**Critic responsibilities:** independently, read-only, verify the 9-point rubric in the decision-recording prompt (decisions recorded exactly; recommendations kept distinct from approvals; Phase 3 not accidentally authorised; `docs/product/` uncreated; source-of-truth rules match the approved proposal; DP-04/DP-06 visible as follow-ups; control files agree on phase/gate; write scope respected; Phase 3 inputs factual-only). Produces `critic-review-phase-2.md`.

---

## Phase 3 — `structure implementation`

**Status:** not authorised. Phase 2's decisions (D-007–D-013) fix *what* Phase 3 would build; they do not authorise *building* it. Factual inputs are compiled in `docs/programmes/product-traceability/phase-3-inputs.md` for the human's future authorisation decision — that file grants no permission on its own.

**Purpose:** Create the approved `docs/product/` (or equivalent) structure and registries per the Phase 2 decisions (D-008 Model A, D-009 source-of-truth rules), empty of historical story content.

**Allowed paths:** to be defined at authorisation time — proposed (not granted) in `phase-3-inputs.md` as a new `docs/product/` tree only.

**Forbidden paths:** `backend/`, `frontend/`, `migrations/`, all existing sprint/story/audit history, `docs/ROADMAP.md`, and (until Phase 3 is authorised) `docs/product/` itself — confirmed absent by `test ! -e docs/product` at the end of both the discovery and hierarchy-approval runs.

**Required inputs:** Phase 2 decision record (D-007–D-013); `phase-3-inputs.md`.

**Required outputs:** the approved registry/hierarchy scaffold, empty of historical content, plus validation that it matches the approved model exactly.

**Required validations:** to be defined at authorisation time; expected to include schema/format validation of any registry files.

**Human gate:** **before** — an explicit authorisation of Phase 3's scope and controls specifically (per D-013), not merely a continuation of Phase 2's approval. **After** authorisation, human also confirms the scaffold matches the approved decision before any historical content is migrated into it.

**Executor / critic responsibilities:** to be scoped at authorisation time.

---

## Phase 4 — `historical migration`

**Status:** not authorised

**Purpose:** Populate the approved structure with the discovery phase's reconstructed historical stories, under the confidence and classification rules established in Phase 1, with any Phase 1 `requires human classification` items resolved by explicit human decision first.

**Allowed paths:** to be defined at authorisation time — expected to be limited to the `docs/product/` tree created in Phase 3.

**Forbidden paths:** `backend/`, `frontend/`, `migrations/`, `docs/ROADMAP.md`, and all original historical sources (read-only inputs, never rewritten).

**Required inputs:** Phase 1 discovery document (as amended by any Phase 2 human decisions), Phase 3 scaffold.

**Required outputs:** populated product hierarchy with every migrated item traceable back to its original evidence source; a migration log.

**Required validations:** to be defined at authorisation time; expected to include a reconciliation check that every `confirmed`/`strongly inferred` Phase 1 item has a corresponding entry, and that no `tentative`/`requires human classification` item was migrated without a resolving human decision.

**Human gate:** **after** — human spot-checks the migration before Phase 5 integration work begins.

**Executor / critic responsibilities:** to be scoped at authorisation time.

---

## Phase 5 — `sprint-workflow integration`

**Status:** not authorised

**Purpose:** Wire the new product layer into the ICM sprint workflow (`docs/sprints/`) so future sprints write traceability links (story → sprint → evidence) as a normal part of sprint closure, without altering the sprint workflow's existing stage/gate mechanics defined in `docs/sprints/STAGE-REGISTRY.md`.

**Allowed paths:** to be defined at authorisation time — expected to touch `docs/sprints/STAGE-REGISTRY.md`, `docs/sprints/WORKFLOW.md`, and sprint templates, which are currently forbidden paths for this programme and would require explicit re-scoping.

**Forbidden paths:** `backend/`, `frontend/`, `migrations/`, `docs/ROADMAP.md`, all completed sprint history.

**Required inputs:** Phase 4 populated product hierarchy.

**Required outputs:** an updated (not rewritten) sprint-workflow integration point, e.g. an additional field or step in the `retro` stage that records the traceability link.

**Required validations:** to be defined at authorisation time; expected to include running the updated workflow against a real or synthetic sprint to confirm it does not break existing stage/gate mechanics.

**Human gate:** **before** — because this phase is the only one that touches the existing sprint-workflow control files, it requires explicit human authorisation of the exact allowed-path expansion before any file is written, not just approval of the general phase.

**Executor / critic responsibilities:** to be scoped at authorisation time.

---

## Cross-phase note

Phases 2–5 are placeholders for planning visibility only. Their "Allowed paths," "Required validations," and responsibility sections are deliberately left as "to be defined at authorisation time" rather than pre-populated, so that authorising a phase is always an explicit, current decision — not a rubber stamp of a scope written before the prior phase's findings were known.
