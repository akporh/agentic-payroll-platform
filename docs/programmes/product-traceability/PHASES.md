# Phases — Product Traceability Programme

All phases are defined here in advance for planning visibility. No phase may begin without a recorded human decision in `decisions.md` authorising it.

**Authorisation state as at 2026-07-29:**

| Phase | Status |
|---|---|
| 1 — `discovery` | complete |
| 2 — `hierarchy approval` | complete — **partial scope**: model and IA approved; the populated hierarchy was never produced or approved (see the scope note below) |
| 3 — `structure implementation` | complete (D-014) |
| 3B — `hierarchy completion` | complete, critic **PASS** (D-022; hierarchy signed off at D-023) |
| 4A — pilot / 4B — confirmed batch / 4C — `CAP-6` batch | complete for authorised scope (D-015, D-016, D-025/D-026) |
| **4D — `historical migration` (all 103 remaining items)** | **authorised and active (D-027)** — this closes Phase 4 in full |
| 5 — `sprint-workflow integration` | not authorised |

*The original line "Only `discovery` is authorised" was accurate at bootstrap and is superseded by this table. Phase 3B is numbered as a peer of Phase 3 rather than as Phase 6 because it completes Phase 3's structural work; it runs after 4A/4B only because the gap it closes was identified after those batches ran.*

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

**Scope note added 2026-07-28 (D-017 / D-022) — this phase's approval was *partial*:** what was approved here was the hierarchy **model and terminology** (D-007–D-009) and the **repository information architecture** (Model A). What was **not** approved — because it was never produced — is the populated hierarchy itself: the discovery document's Sections 7 and 8 explicitly declined to define the feature layer or map stories to it until the model was approved, and no later phase went back and did so. Phase 4A/4B consequently invented hierarchy rows on demand to hold each batch. **Phase 3B (`hierarchy completion`) exists to close that gap.** This note records the boundary accurately; nothing in Phase 2's own record below has been retro-edited to claim a wider approval than it gave.

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

## Phase 3B — `hierarchy completion`

**Status:** authorised and active (2026-07-28, via D-022 — see `decisions.md`)

**Position:** a peer of Phase 3 (`structure implementation`), executed **after** Phase 4A/4B (which ran before this gap was identified) and **before** any further Phase 4 batch. Full Phase 4 is now gated behind this phase's human sign-off in addition to its own separate authorisation.

**Purpose:** Define the complete product hierarchy — outcomes, capabilities and features — across the **entire 148-item discovery inventory**, top-down and as a single proposal; present it for human sign-off as a visual artefact; and, only after approval, apply it together with the story re-key (D-020) and the readability corrections. **No story is migrated by this phase.**

**Problems this phase closes** (identified 2026-07-28 on human review of the Phase 4A/4B batches):

| # | Problem | Fix |
|---|---|---|
| P1 | Provenance is one-way — no source → migrated-story lookup, no coverage view | A `SOURCE-INDEX.md` reverse index inside `docs/product/` (never by editing `docs/stories/**`, which remains forbidden) |
| P2 | Migrated stories carry no acceptance criteria; `POLICY.md` and D-009 appeared to contradict each other | D-018 retro/forward split, applied to `POLICY.md`, `PROGRAMME.md` and `stories/TEMPLATE.md` |
| P3 | `PT-A1-22` encodes the programme name and a one-off inventory position; decode written nowhere | D-019 `STORY-<nnnn>` scheme + mandatory `origin_code` + scheme documented in `README.md` |
| P4 | `FEATURES.md` shows `story_count` but never which stories | A `stories` column listing member IDs, validator-enforced against `STORY-REGISTRY.md` both ways |
| P5 | Story files show bare `OUT-3`/`CAP-3`/`FEAT-4`; live `OUT-1/2/3` collide with the discovery document's `OUT-1/2/3` | Complete D-016's ID+name convention into story files; resolve the outcome-ID collision explicitly |
| P6 | **Root cause** — hierarchy built bottom-up, one batch at a time | D-017: full tree defined and approved as a whole before migration resumes |

**Allowed paths (as authorised by D-022):**
```text
docs/product/
docs/programmes/product-traceability/
```
No other path.

**Forbidden paths:** `backend/`, `frontend/`, `migrations/`, `docs/ROADMAP.md`, `docs/stories/`, `docs/sprints/`, `docs/audit/`, `docs/security/`, `docs/test-reports/`, `docs/retro-reports/`, `docs/audit-program/`, `docs/programmes/agentic-architecture-review/`, `~/.claude/`, and all original historical sources generally (read-only inputs, never rewritten). Unchanged from Phase 4.

**Required inputs:** `docs/diagnostics/2026-07-15-retrospective-product-story-and-hierarchy-discovery.md` Sections 3.1–3.11 (all 148 items), 5 (proposed outcomes), 6 (proposed capabilities), 7–8 (features — deferred, never produced); the Phase 3 scaffold; the Phase 4A/4B outputs and conventions; D-017–D-022.

**Required outputs:**

*Stage 1 — proposal (no `docs/product/` write):* a complete hierarchy proposal under `docs/programmes/product-traceability/` containing the reconciled outcome set (with the `OUT-1/2/3` collision resolved explicitly), the full durable capability set, the complete feature set defined across all capability areas at once, a full 148-item → feature assignment map, a `STORY-<nnnn>` ID allocation table carrying every legacy code, and an open-questions list.

*Stage 2 — sign-off surface:* a visual artefact rendering the tree outcome → capability → feature → story, each feature listing its stories by name, coverage against the 148, the ID mapping table, open questions inline, and a chronological alternate sort.

*Stage 3 — apply, only after human approval:* approved rows written into `OUTCOMES.md`/`CAPABILITIES.md`/`FEATURES.md`; `stories` column added to `FEATURES.md`; parent display names added to `TEMPLATE.md` and all 21 story files; the 21 stories re-keyed with `origin_code` populated and files renamed; `SOURCE-INDEX.md` created; ID scheme, allocation rules and reference-path convention written into `README.md`; `validate_registry.py` extended; run record and critic review.

**Reference-path convention (fixed by this phase, documented in `README.md`):** references *within* `docs/product/` are relative (`../FEATURES.md`) so the tree survives being moved; references *outside* it are repo-root-relative (`docs/stories/foo.md`) because `../../` chains are unreadable, ungreppable and break whenever a file moves *within* `docs/product/`. Absolute and `~/` paths are never used. The residual risk — relocating `docs/product/` itself — is handled by the validator's link-existence check, not by path style.

**Required validations:** `python3 docs/product/validate_registry.py` passes against the extended schema (including `origin_code` presence, `stories`/`feature_id` round-trip, display-name matching, no surviving live `PT-*` identifier, and link existence); `git diff --check`; `git status --short` confirms only `docs/product/` and programme-control files changed; every one of the 148 inventory items appears exactly once in the allocation table with a unique ID; no forbidden path modified.

**Human gate:** **after Stage 2, before Stage 3** — the human signs off the visual hierarchy artefact. Stage 3 may not begin without it. Completion of this phase does **not** auto-authorise any Phase 4 migration batch.

**Executor responsibilities:** define the hierarchy top-down across the whole inventory rather than batch-shaped; never present a recommendation as an approval; do not migrate any story; do not touch a forbidden path; halt at the Stage 2 human gate; record any genuinely ambiguous feature assignment as `requires human classification` rather than guessing.

**Critic responsibilities:** independently, read-only, verify — the feature set covers all 148 items with no overlap and no orphan; the `OUT-1/2/3` collision is genuinely resolved rather than papered over; the ID allocation table is complete, unique, and preserves every legacy code; no story content was migrated; write scope was honoured; the Stage 2 human gate was respected; P1–P6 are each actually closed rather than asserted closed. Produces `critic-review-phase-3b-hierarchy-completion.md`.

---

## Phase 4 — `historical migration`

**Status (as at 2026-07-29): authorised in full and closed by Phase 4D (D-027)** — see the Phase 4D section below. The paragraph that follows records the position as it stood while Phase 4 was still being authorised batch by batch; it is retained as history, not as a live constraint.

**Status (historical, superseded 2026-07-29):** not authorised as a whole. **Phase 4A — bounded two-story pilot — authorised and complete** (2026-07-15, via D-015). **Phase 4B — bounded confirmed-story batch (capability area A1+A2) — authorised and complete for its authorised scope** (2026-07-15, via D-016, `docs/diagnostics/2026-07-15-prompt-authorise-phase-4b-confirmed-capability-batch.md`). The remaining historical items — every other capability area's confirmed items, and every strongly-inferred/tentative/requires-human-classification item anywhere — are **not** authorised for migration; a separate, explicit human decision is required before any further batch begins.

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

## Phase 4D — `historical migration` (remainder — all 103 items)

**Status:** authorised and active (2026-07-29, via D-027 — direct human chat instruction, *"proceed with migrating all other capabilities no need to process in batch"*). **This phase closes Phase 4 in full.** On its completion the migration backlog is zero and no further Phase 4 authorisation exists to give.

**Position:** the final Phase 4 sub-phase, after 4A (2 items), 4B (19) and 4C (33). It deliberately does **not** decompose further into capability-shaped batches — see D-027 for why that pattern is retired rather than continued.

**Purpose:** Migrate every one of the 103 items that currently hold a reserved identifier and a feature assignment in `../product/ID-ALLOCATION.md` and nothing else, so that `STORY-REGISTRY.md` and `ID-ALLOCATION.md` finally answer the same question with the same number, and the absence of a story from the registry becomes meaningful evidence that no such work exists.

**Scope:** all ten capabilities with a non-zero remainder — `CAP-5` (18), `CAP-4` (15), `CAP-3` (14), `CAP-9` (11), `CAP-1` (10), `CAP-7` (9), `CAP-10` (9), `CAP-2` (7), `CAP-8` (7), `CAP-11` (3). `CAP-6` is already 33/33; `CAP-12` Agent Layer holds zero items by design (D-023, OQ-6) and stays empty.

**Confidence composition (carried verbatim, never upgraded):** 33 `confirmed`, 53 `strongly inferred`, 12 `tentative`, 5 `backlog`.

**Allowed paths (as authorised by D-027):**
```text
docs/product/
docs/programmes/product-traceability/
```
No other path. Unchanged from every prior Phase 4 sub-phase.

**Forbidden paths:** `backend/`, `frontend/`, `migrations/`, `docs/ROADMAP.md`, `docs/stories/`, `docs/sprints/`, `docs/audit/`, `docs/security/`, `docs/test-reports/`, `docs/retro-reports/`, `docs/audit-program/`, `docs/programmes/agentic-architecture-review/`, `~/.claude/`, and all original historical sources generally (read-only inputs, never rewritten). Unchanged.

**Required inputs:** `../product/ID-ALLOCATION.md` (the authoritative remainder list); `docs/diagnostics/2026-07-15-retrospective-product-story-and-hierarchy-discovery.md` §3.1–3.11 for per-item actor/problem/behaviour/evidence; the Phase 4A/4B/4C conventions and `../product/stories/TEMPLATE.md`; `docs/ROADMAP.md`, `docs/stories/`, `docs/test-reports/`, `docs/audit/`, `docs/security/`, `docs/retro-reports/` as read-only evidence; D-011, D-018, D-019, D-023, D-025, D-027.

**Required outputs:** 103 story files under `../product/stories/`; 103 rows added to `STORY-REGISTRY.md` (table rebuilt in ID order); `FEATURES.md` `stories`/`migrated` updated on every feature with a remainder; `ID-ALLOCATION.md` all 157 rows marked migrated and its coverage tables rewritten to 157/157; `SOURCE-INDEX.md` extended so every one of the 157 stories is reachable by legacy code and by source/evidence file; `README.md` status updated; `runs/historical-migration-remainder-run-001.md`; `critic-review-phase-4d-remainder.md`.

**Required validations:** `python3 docs/product/validate_registry.py` passes (including the `stories`/`feature_id` round-trip, display-name matching, the legacy-`PT-*` sweep, link existence, and SOURCE-INDEX reachability); `git diff --check` clean; `git status --short` shows only `docs/product/` and programme-control files changed; every `○` in `ID-ALLOCATION.md` becomes `●` with **no** identifier renumbered, reused or invented; migrated confidence matches the allocation table row-for-row; every `backlog` item carries `status: backlog`; no forbidden path modified.

**Human gate:** **after** — the human spot-checks the completed registry. There is no further Phase 4 batch to gate; the next decision is whether to authorise Phase 5.

**Executor responsibilities:** migrate every remaining item and no more; carry confidence verbatim and never upgrade an item on migration; record a source contradiction (Gate 4 ✅-vs-pending, the two Sprint 17 BLOCKED verifications) inside the story record rather than resolving it silently; cite only evidence files that exist on disk; do not modify any historical source; do not authorise Phase 5.

**Critic responsibilities:** independently, read-only, verify — all 103 migrated with none missed, duplicated, renumbered or invented; confidence carried verbatim against `ID-ALLOCATION.md`; `backlog` items not presented as delivered; every cited evidence path exists; coverage arithmetic reconciles to 157/157 across `ID-ALLOCATION.md`, `FEATURES.md` and `STORY-REGISTRY.md`; write scope honoured; no forbidden path touched. Produces `critic-review-phase-4d-remainder.md`.

---

## Phase 5 — `sprint-workflow integration`

**Status:** **authorised and complete** (2026-07-29, via D-029 — direct human chat instruction following a plain-language scope walkthrough, with "Option A" chosen for the skill files). The `before` gate below was satisfied by D-029 naming the exact path expansion prior to any file being written.

**Purpose:** Wire the new product layer into the ICM sprint workflow (`docs/sprints/`) so future sprints write traceability links (story → sprint → evidence) as a normal part of sprint closure, without altering the sprint workflow's existing stage/gate mechanics defined in `docs/sprints/STAGE-REGISTRY.md`.

**Allowed paths (as authorised by D-029, exhaustive):** `docs/sprints/STAGE-REGISTRY.md` (**amend only** — the `Inputs`/`Outputs`/`Completion criteria` fields of the `pm` and `retro` rows, nothing else); `docs/sprints/WORKFLOW.md` (**amend only** — one new subsection plus one table row); `docs/product/**`; `docs/programmes/product-traceability/**`. Read-only inputs: `docs/sprints/CURRENT.md`, `docs/sprints/README.md`, and the three existing sprint workspaces as validation material.

**Forbidden paths:** `backend/`, `frontend/`, `migrations/`, `docs/ROADMAP.md`, `docs/stories/`, `docs/audit/`, `docs/audit-program/`, `docs/security/`, `docs/test-reports/`, `docs/retro-reports/`, `docs/programmes/agentic-architecture-review/`, **`~/.claude/`**, and `docs/sprints/<id>/**` for every existing sprint workspace — closed sprints are history and are not retrofitted.

**Required inputs:** Phase 4 populated product hierarchy.

**Required outputs (as delivered):** a `story_refs` field and a `## Product traceability` subsection in `WORKFLOW.md`; traceability lines added to the `pm` (allocate ID) and `retro` (complete row, gated) stage entries; the steady-state maintenance provision below. **Two touchpoints, not the single `retro` step this definition originally anticipated** — see D-029 for why one is insufficient.

**Required validations (as run):** the amended fields exercised against the closed, fully-evidenced `dev-levy-rule-pct` sprint as a synthetic case, without modifying that workspace; `python3 docs/product/validate_registry.py` at PASS; confirmation that no stage's `Dependencies`, `Parallel compatibility`, `Mandatory status`, `Skip conditions`, `Entry conditions` or `Human gate` changed, and that the 10-stage set and its ordering are untouched.

**Human gate:** **before** — because this phase is the only one that touches the existing sprint-workflow control files, it requires explicit human authorisation of the exact allowed-path expansion before any file is written, not just approval of the general phase. *Satisfied by D-029.*

**Known gap carried, not closed:** the `/pm` and `/retro` skills that perform this work live in `~/.claude/skills/`, which stays forbidden by explicit choice. The skill-side text was handed to the human for manual application; the close gate in `STAGE-REGISTRY.md` is what enforces the obligation regardless.

---

## Phase 6 — `feature-42 addition`

**Status:** **authorised** (2026-07-29, via D-030 — direct human chat instruction, `AskUserQuestion` answer "Add FEAT-42 under CAP-11"). Recorded before any file in scope was written.

**Why a phase exists for a single row.** The steady-state provision below draws a hard line: filling in the cabinet is routine, changing the shape of the cabinet is not, and "adding or retiring an outcome, capability or feature" is named explicitly as requiring **a new phase and a human decision**. Adding one leaf feature is the smallest possible shape change, but it is a shape change, and the rule admits no size exemption. Creating the phase is cheaper than eroding the rule — and this programme exists because things became permanent by default rather than by choice.

**Purpose:** Add `FEAT-42` — *Product record & roadmap structure* — under `CAP-11` Programme Governance & Assurance, giving the four `roadmap-split` sprint stories an honest home. `CAP-11`'s two existing features are scoped to independent review programmes (`FEAT-40`) and the ICM sprint workflow model (`FEAT-41`); neither covers the structure of the product record itself, and the traceability programme's own artefact (`PT-M-04`) was excluded from allocation rather than given a feature.

**Allowed paths (exhaustive):** `docs/product/FEATURES.md` (**amend only** — one new row plus its changelog line); `docs/programmes/product-traceability/**`.

**Forbidden paths:** everything forbidden to Phase 5, unchanged — plus `docs/product/OUTCOMES.md` and `docs/product/CAPABILITIES.md`, since no outcome or capability changes. `docs/ROADMAP.md` stays forbidden to this programme; the `roadmap-split` sprint edits it under its own separate authorisation (its `decisions.md` DEC-01), never under this phase.

**Required inputs:** the `roadmap-split` sprint's confirmed scope (`docs/sprints/roadmap-split/CONTEXT.md`) establishing that four stories need a feature that does not exist.

**Required outputs:** one `FEAT-42` row in `FEATURES.md` under `CAP-11`, `status: active`; the story-count columns left for the sprint's own `/retro` to complete, per the steady-state additions rule.

**Required validations:** `python3 docs/product/validate_registry.py` at PASS; confirmation that no outcome, capability, existing feature, or ID scheme changed, and that no existing story's feature assignment moved.

**Human gate:** **before** — satisfied by D-030.

**Boundary note.** This phase authorises the *feature row only*. Allocating `STORY-0158`–`0161` into it, and creating the ~14 backlog rows for previously untraced open roadmap items, are **additions** — routine sprint work under the steady-state provision, authorised by the `roadmap-split` sprint's own record, not by this phase.

---

## Steady state — maintaining `docs/product/` after Phase 5

*Added 2026-07-29 under D-029, closing the authorisation gap D-028 opened.*

With Phase 5 complete there is no further phase, and the programme's phase-based authorisation model no longer covers the ordinary upkeep of the layer it produced. That gap was real: between D-027 (Phase 4 closed) and D-029, no phase authorised writing to `docs/product/` at all, and correcting two story titles needed its own decision (D-028).

**Standing provision.** From this point, `docs/product/` is maintained under the sprint workflow rather than under this programme:

- **Additions** — new stories enter via `pm`/`retro` per `docs/sprints/WORKFLOW.md` § Product traceability. No programme decision required; the sprint's own record is the authorisation.
- **Corrections** — fixing a demonstrably wrong field (a broken evidence path, a title that contradicts its own record) is ordinary maintenance. Record it in the relevant sprint's `decisions.md`, not here.
- **Structural change** — adding or retiring an outcome, capability or feature; changing the ID scheme; changing what a registry column *means*; merging or splitting a story. **These still require a new phase and a human decision in this file.** Retiring an ID always requires human approval (D-019 rule 4).

The line: *filling in the cabinet is routine; changing the shape of the cabinet is not.*

---

## Cross-phase note

Phases 2–5 are placeholders for planning visibility only. Their "Allowed paths," "Required validations," and responsibility sections are deliberately left as "to be defined at authorisation time" rather than pre-populated, so that authorising a phase is always an explicit, current decision — not a rubber stamp of a scope written before the prior phase's findings were known.

*Added 2026-07-28:* Phase 3B was not anticipated at bootstrap. It was added under D-022 because Phase 4's stated purpose — "populate **the approved structure**" — rested on an approval that had never actually been given for the populated hierarchy. Adding a phase rather than stretching Phase 4's scope keeps the principle above intact: a phase's authorisation names what it may do, and work that falls outside every defined phase gets a new phase rather than a quiet reinterpretation of an existing one.
