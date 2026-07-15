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
docs/programmes/agentic-architecture-review/
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

**Required inputs:** `docs/ROADMAP.md`, `docs/stories/`, `docs/sprints/`, `docs/audit-program/`, `docs/programmes/agentic-architecture-review/`, `docs/audit/`, `docs/test-reports/`, `docs/retro-reports/`, `docs/security/`, `docs/design/ui-decisions.md`, `docs/analysis/`, `docs/planning/`, git history, associated backend/frontend source and tests cited as evidence.

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

**Forbidden paths (as executed):** `docs/product/`, `docs/ROADMAP.md`, `docs/stories/`, `docs/sprints/`, `docs/audit/`, `docs/audit-program/`, `docs/programmes/agentic-architecture-review/`, `docs/security/`, `docs/test-reports/`, `docs/retro-reports/`, `backend/`, `frontend/`, `migrations/`, `~/.claude/` — none of these were touched by this phase.

**Required inputs:** Phase 1 outputs (discovery document, decision pack, critic review) — used as the basis for the human decisions.

**Required outputs (delivered):** DP-01–DP-07 recorded as D-007–D-013 in `decisions.md`; `decision-pack.md` annotated with resolutions (original questions/options/recommendations preserved, not erased); `state.md`, `phase-inputs.yaml`, `exceptions.md` updated to reflect Phase 2 closure; `phase-3-inputs.md` created (factual only, no permission granted); `runs/hierarchy-approval-run-001.md` created; `critic-review-phase-2.md` created.

**Required validations:** `git diff --check`; `git status --short`; `find docs/programmes/product-traceability -maxdepth 2 -type f`; `test ! -e docs/product` (confirms Phase 3's structure was never created); direct inspection confirming DP-01–DP-07 each appear exactly once as resolved, all control files agree Phase 2 is complete, Phase 3 remains unauthorised, and DP-04/DP-06 remain visible as open follow-up investigations rather than silently resolved.

**Human gate:** **before** — the human's decisions (recorded in the bootstrap-decision prompt) were the trigger for this phase's execution; the executor recorded them faithfully rather than proposing or reinterpreting them.

**Executor responsibilities:** record the exact decisions supplied; close programme control files accurately; do not erase the historical decision-pack trail; do not authorise Phase 3; prepare factual (not permission-granting) Phase 3 inputs.

**Critic responsibilities:** independently, read-only, verify the 9-point rubric in the decision-recording prompt (decisions recorded exactly; recommendations kept distinct from approvals; Phase 3 not accidentally authorised; `docs/product/` uncreated; source-of-truth rules match the approved proposal; DP-04/DP-06 visible as follow-ups; control files agree on phase/gate; write scope respected; Phase 3 inputs factual-only). Produces `critic-review-phase-2.md`.

---

## Phase 3 — `structure implementation`

**Status:** authorised and active (2026-07-15, via D-014, direct human chat instruction — see `decisions.md`)

**Purpose:** Create the approved `docs/product/` structure and registries per the Phase 2 decisions (D-008 Model A, D-009 source-of-truth rules), empty of historical story content.

**Allowed paths (as authorised by D-014):**
```text
docs/product/
```
Write access is limited strictly to this path for this phase. Programme-control files under `docs/programmes/product-traceability/` may also be updated to record the phase's own governance state (decisions, state, run record) — this is the same programme-control write access every phase has had, not an expansion of the `docs/product/` scope.

**Forbidden paths:** `backend/`, `frontend/`, `migrations/`, all existing sprint/story/audit history (`docs/ROADMAP.md`, `docs/stories/`, `docs/sprints/`, `docs/audit/`, `docs/audit-program/`, `docs/programmes/agentic-architecture-review/`, `docs/security/`, `docs/test-reports/`, `docs/retro-reports/`), `~/.claude/`. No story content may be migrated into `docs/product/` in this phase — registries and `stories/` are created empty. Phase 4 (`historical migration`) is explicitly not begun.

**Required inputs:** Phase 2 decision record (D-007–D-013); `phase-3-inputs.md`; D-014.

**Required outputs (delivered):** `docs/product/README.md`, `OUTCOMES.md`, `CAPABILITIES.md`, `FEATURES.md`, `STORY-REGISTRY.md` (all empty registries — schema/instructions only, zero content rows), `docs/product/stories/` (empty except a template), `docs/product/stories/TEMPLATE.md`, `docs/product/validate_registry.py` (validation mechanism, dependency-free, operates only on files inside `docs/product/`).

**Required validations:** `git diff --check`; `git status --short` confirming only `docs/product/` and programme-control files changed; `test ! -e docs/product/stories/<any-non-template-file>` (confirms no story migrated); running `docs/product/validate_registry.py` itself and confirming it passes on the empty scaffold; confirming zero content rows in each registry file.

**Human gate:** **after** — human confirms the scaffold matches the approved decision before Phase 4 (historical migration) is separately authorised.

**Executor responsibilities:** build exactly the authorised scaffold, templates, and validation mechanism; do not populate any registry row or story file with historical content; do not touch any file outside `docs/product/` (other than this programme's own control files); do not begin Phase 4.

**Critic responsibilities:** independently, read-only, verify write scope was honoured, no historical files were touched, no story content was migrated, the scaffold matches the approved Model A structure and source-of-truth rules, and Phase 4 was not begun. Produces `critic-review-phase-3.md`.

---

## Phase 4 — `historical migration`

**Status:** not authorised as a whole. **Phase 4A — bounded two-story pilot — authorised and complete** (2026-07-15, via D-015). **Phase 4B — bounded confirmed-story batch (capability area A1+A2) — authorised and complete for its authorised scope** (2026-07-15, via D-016, `docs/diagnostics/2026-07-15-prompt-authorise-phase-4b-confirmed-capability-batch.md`). The remaining historical items — every other capability area's confirmed items, and every strongly-inferred/tentative/requires-human-classification item anywhere — are **not** authorised for migration; a separate, explicit human decision is required before any further batch begins.

**Purpose (Phase 4 as a whole):** Populate the approved structure with the discovery phase's reconstructed historical stories, under the confidence and classification rules established in Phase 1, with any Phase 1 `requires human classification` items resolved by explicit human decision first.

**Purpose (Phase 4A pilot, as authorised by D-015):** Migrate exactly two already-closed, well-evidenced ICM sprint-workflow stories (`aud-q1-trace-source` → `PT-A4-31`; `sec-s7-timesheet-upload-guard` → `PT-A4-32`) into the `docs/product/` scaffold created in Phase 3, proving the product layer carries the intended ICM disciplines (stable IDs, source-of-truth ownership, explicit state, evidence links, decision traceability, dependency visibility, append-only history, human-gate discipline) before any wider migration batch is considered.

**Purpose (Phase 4B confirmed-batch, as authorised by D-016):** Migrate every `confirmed`-confidence story from exactly one capability area (A1+A2 — Onboarding & Workforce Setup, 19 items) into `docs/product/`, proving the product layer scales past a two-item pilot to a real double-digit batch, and introduce a human-readable parent-name display convention (`outcome_name`/`capability_name`/`feature_name` columns) alongside the existing stable IDs, without weakening ID-based authority.

**Allowed paths (Phase 4A pilot, as authorised by D-015; Phase 4B batch, as authorised by D-016):**
```text
docs/product/
docs/programmes/product-traceability/
```
No other path. Neither batch required a `TEMPLATE.md` schema exception beyond the Phase 4A additive fields recorded in the template's own amendment note (Outcome/Capability, Decision references, Dependencies, Delivery history) — see `runs/historical-migration-pilot-run-001.md` and `runs/historical-migration-confirmed-batch-run-001.md`.

**Allowed paths (Phase 4 as a whole, remaining items):** to be defined at a future, separate authorisation time — expected to remain limited to the `docs/product/` tree created in Phase 3.

**Forbidden paths:** `backend/`, `frontend/`, `migrations/`, `docs/ROADMAP.md`, `docs/stories/`, `docs/sprints/`, `docs/audit/`, `docs/security/`, `docs/test-reports/`, `docs/retro-reports/`, `docs/audit-program/`, `docs/programmes/agentic-architecture-review/`, `~/.claude/`, and all original historical sources generally (read-only inputs, never rewritten).

**Required inputs (pilot):** Phase 1 discovery document; Phase 3 scaffold; the two named ICM sprint workspaces (`docs/sprints/aud-q1-trace-source/`, `docs/sprints/sec-s7-timesheet-upload-guard/`) and their linked audit/security/test/retro/implementation evidence.

**Required inputs (Phase 4B batch):** Phase 1 discovery document Section 3.1 (capability area A1+A2); Phase 3 scaffold; Phase 4A outputs and conventions; `docs/ROADMAP.md`, `docs/stories/track-j-workspace-config-management.md`, and the other cited historical evidence files (read-only); git history for commit-reference verification.

**Required outputs (pilot, delivered):** two populated `STORY-REGISTRY.md` rows; two story files (`stories/PT-A4-31-component-source-trace-fix.md`, `stories/PT-A4-32-timesheet-upload-size-guard.md`); the minimum `OUTCOMES.md`/`CAPABILITIES.md`/`FEATURES.md` rows needed to place them (`OUT-1`/`OUT-2`, `CAP-1`/`CAP-2`, `FEAT-1`/`FEAT-2`); `runs/historical-migration-pilot-run-001.md`; `critic-review-phase-4a-pilot.md`.

**Required outputs (Phase 4B batch, delivered):** 19 populated `STORY-REGISTRY.md` rows (`PT-A1-07/08/09/10/11/15/16/17/18/19/20/21/22/25/28/38/39/41/42`); 19 story files under `stories/`; one new outcome (`OUT-3`), one new capability (`CAP-3`), three new features (`FEAT-3`/`FEAT-4`/`FEAT-5`); the `outcome_name`/`capability_name`/`feature_name` schema amendment applied to all existing and new rows across `CAPABILITIES.md`, `FEATURES.md`, `STORY-REGISTRY.md`; an extended `validate_registry.py` (name-matching, duplicate-ID, and ambiguous-prefix checks); `runs/historical-migration-confirmed-batch-run-001.md`; `critic-review-phase-4b-confirmed-batch.md`.

**Required validations (pilot):** `python3 docs/product/validate_registry.py` passes; `git diff --check` clean; exactly two non-template story files exist; `STORY-REGISTRY.md` has exactly two content rows; every referenced outcome/capability/feature ID exists; every story file has one matching registry row and vice versa; no forbidden path modified; critic review passes.

**Required validations (Phase 4B batch):** `python3 docs/product/validate_registry.py` passes against the extended schema; selected count is 1–20 and all are `confirmed`; every story filename begins with its full exact ID and no ambiguous prefix exists; every hierarchy ID resolves and every display name matches its parent's authoritative name; the two pre-existing Phase 4A rows still validate; no forbidden path modified; critic review passes.

**Required validations (Phase 4 as a whole, remaining items):** to be defined at a future authorisation time; expected to include a reconciliation check that every `confirmed`/`strongly inferred` Phase 1 item has a corresponding entry, and that no `tentative`/`requires human classification` item was migrated without a resolving human decision.

**Human gate:** **after** — human spot-checks each batch (Phase 4A, Phase 4B) before any further Phase 4 batch is separately authorised; human also spot-checks any future full-Phase-4 migration before Phase 5 integration work begins.

**Executor / critic responsibilities (pilot):** migrate exactly the two authorised stories; create only the minimum hierarchy rows needed; do not migrate any other historical item; do not modify `stories/TEMPLATE.md` beyond a recorded, justified schema-defect fix; do not authorise or begin any broader Phase 4 batch. Critic independently verifies the 12-point rubric in the D-015 authorising prompt and produces `critic-review-phase-4a-pilot.md`.

**Executor / critic responsibilities (Phase 4B batch):** select exactly one capability area per the batch-selection rule; migrate confirmed-only items from it (≤20); exclude and document any item that direct inspection weakens rather than silently downgrading and migrating it; implement the human-readable-name schema amendment without weakening ID authority; do not authorise or begin any further Phase 4 batch. Critic independently verifies the 13-point rubric in the D-016 authorising prompt and produces `critic-review-phase-4b-confirmed-batch.md`.

**Executor / critic responsibilities (Phase 4 as a whole, remaining items):** to be scoped at a future, separate authorisation time.

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
