# Non-Linear ICM Sprint Workflow — Implementation Plan

**Date:** 2026-07-12 (decisions approved 2026-07-12)
**Status:** IMPLEMENTATION-READY, AWAITING RUN APPROVAL — design decisions D1–D9 are approved (§3). No changeset has been executed. No file listed in §4/§5 has been created, moved, archived, or modified as a result of this plan.
**Scope:** Introduces `docs/sprints/` as repository-based state for the sprint workflow, per the non-linear target model approved in `docs/diagnostics/2026-07-11-sprint-workflow-icm-diagnostic.md` (Sections 7–8, revised 2026-07-11 per `docs/diagnostics/2026-07-11-prompt-revise-sprint-workflow-icm-target-model.md`), with decisions finalized per `docs/diagnostics/2026-07-12-prompt-approve-nonlinear-icm-implementation-decisions.md`.
**Inputs read:** the three documents above; `~/.claude/CLAUDE.md`, `.../2.OnAiR/CLAUDE.md`, `.../Sandy/CLAUDE.md`, this repo's `CLAUDE.md`; `~/.claude/skills/{roadmap,pm,architect,arch-council,security,auditor,tester,retro}/SKILL.md`; `~/.claude/settings.json` hooks; `~/.claude/agents/{senior-architect,principal-reviewer}.md`; `docs/audit-program/{WORKFLOW.md,audit-state.md}` and `docs/agentic-architecture-review/{WORKFLOW.md,review-state.md}` as the working precedent; the project auto-memory index and the stale committed `.claude/memory/` folder.

---

## 1. Executive summary

This plan introduces a small set of static files (`docs/sprints/CURRENT.md`, `WORKFLOW.md`, `STAGE-REGISTRY.md`, `README.md`) plus a per-sprint workspace, piloted on exactly one deliberately small sprint rather than backfilled across sprint history. It does **not** redesign the reusable skill files, the hooks, or CLAUDE.md's substantive rules — those stay exactly where they are; the new files formalize *when* those rules apply and *what happened* each time they were checked, which is the gap the original diagnostic identified (G1–G3, G9).

All nine open design decisions from the prior draft are now resolved (§3) — this document blocks on exactly one remaining input, which is not a design decision but a scheduling one: **which sprint is the pilot.** Per the approval, that sprint is deliberately not selected here, and Changeset 2 (the only changeset that needs it) does not start until it is.

The riskiest open question is not technical, it's behavioral: whether `state.md` and `decisions.md` actually get written *during* a live sprint, under time pressure, rather than reconstructed afterward from memory (the same failure mode that produced G1–G3 in the first place). Changeset 7 (mechanical linting, script-first per D8) exists specifically to make that failure visible immediately rather than discovered three sprints later — it is the load-bearing changeset, not a nice-to-have.

A second, structural point carried through every changeset below: roughly half of this plan's file changes are **repository changes** (committed, visible on GitHub, portable to any machine or session) and roughly half are **user-home changes** (`~/.claude/skills/`, `~/.claude/settings.json`) that Casper can apply locally in the active environment but that do **not** appear in this git history and do **not** propagate anywhere else automatically. §6 makes this split explicit changeset by changeset, because it's the direct, practical consequence of D3 (personas stay user-home) and a fact this plan must not obscure.

---

## 2. Assumptions

- The existing SKILL.md files, hooks, and CLAUDE.md hierarchy are correct and are **not** being redesigned here — this plan only adds the missing state layer around them.
- Exactly one sprint pilots the new structure. No historical sprint (1 through the current in-flight work) is backfilled into `docs/sprints/`.
- "Fresh-session resumability" means: a new Casper session, given only repository access (no chat history, no auto-memory), can answer every question in the diagnostic's §5 reconstruction test for the pilot sprint.
- `docs/audit-program/` and `docs/agentic-architecture-review/` remain independent workspaces with their own `WORKFLOW.md` — this plan does not merge them with `docs/sprints/`, only reuses their proven conventions (named stage status, append-only decision log, evidence-cites-findings discipline).
- No CI system currently runs in this repository. Per D8, linting starts as a standalone script; a hook or CI is a post-pilot decision (§3.1), not part of this implementation pass.
- The two prior diagnostic documents are treated as already-approved direction for the *target model*. This plan does not re-litigate that model — it plans and now authorizes the build sequence only, pending run approval and pilot selection.

---

## 3. Decisions — APPROVED (2026-07-12)

All nine decisions are approved per `docs/diagnostics/2026-07-12-prompt-approve-nonlinear-icm-implementation-decisions.md`. No open design decision remains blocking implementation.

| ID | Decision | Approved option | Approved 2026-07-12 as recorded |
|---|---|---|---|
| **D1** | Pilot sprint ID and scope | **(b)** | A deliberately small, low-risk sprint chosen specifically to exercise workflow mechanics independently of feature complexity. **Not yet selected** — this is a precondition on Changeset 2 (§5.2), not a reopened design question. |
| **D2** | Authoritative source for stage applicability rules | **(a)** | `docs/sprints/STAGE-REGISTRY.md` is authoritative for formal stage applicability and entry conditions. CLAUDE.md's auto-invoke table is trimmed to a pointer (Changeset 10); no duplicate applicability rules are maintained in prose elsewhere. |
| **D3** | Architecture personas location | **(b)**, for the pilot | `senior-architect.md` / `principal-reviewer.md` stay in `~/.claude/agents/`. Recorded as a known portability limitation — revisit before a second operator or a remote/cloud agent must run `/arch-council` (tracked in §3.1, Post-pilot decisions). |
| **D4** | CLAUDE.md changes | **(b)**, isolated | Project `CLAUDE.md`'s restated 17-step sequence is trimmed to reference the global sequence + `STAGE-REGISTRY.md`. Runs as its own changeset (10) after the core pilot structure is established — not bundled into Changesets 1–8. |
| **D5** | Plan-mode persistence | **(a)** | Approved plan-mode output is copied into `docs/sprints/<id>/plan.md`. The harness-owned original in `~/.claude/plans/` is never moved or deleted. |
| **D6** | Stale committed `.claude/memory/` folder | **(b)** | Archived under a clearly dated name (`.claude/memory-archived-2026-07/`), not deleted. |
| **D7** | Mandatory artefact writers | **(a)** | For the pilot, durable sprint-workspace writing is mandatory only for `/arch-council` (writes `architecture.md` + `decisions.md`) and `/tester` (updates `state.md` in addition to its existing `docs/test-reports/` habit). `/roadmap`, `/pm`, `/architect`, `/verify`, `/security`, `/auditor`, `/retro` gain best-effort integration per §5, introduced incrementally rather than mandated on day one. |
| **D8** | Workflow-state linting mechanism | **(b)**, for the pilot | Implemented as a standalone script (`scripts/lint_sprint_state.py`) run manually before `/retro`. No `~/.claude/settings.json` hook is added until the script has run clean on at least one complete pilot sprint (tracked in §3.1, Post-pilot decisions). |
| **D9** | Active sprint count | **(a)** | One active sprint initially. `CURRENT.md`'s `active_sprints` field is preserved as a **list shape** (`active_sprints: [sprint-id]`) even though exactly one entry is supported and enforced for this implementation — this means multi-sprint support later is a validation-rule change, not a schema migration. Multiple **stages** within that one sprint may still be active/parallel simultaneously (§7.3–7.4 of the diagnostic) — D9 constrains sprint count, not stage concurrency. |

### 3.1 Post-pilot decisions (deliberately deferred — not implementation blockers)

These are real, tracked follow-ups, not open questions this plan needs answered before Changeset 1 can start:

| ID | Deferred item | Reactivation trigger |
|---|---|---|
| PP-1 | Promote the lint script (Changeset 7) from standalone script to a `~/.claude/settings.json` PostToolUse hook | Script has run clean (no false positives) across one complete pilot sprint, per D8 |
| PP-2 | Copy `senior-architect.md` / `principal-reviewer.md` into the repository | A second human operator, or a scheduled/remote cloud agent, needs to run `/arch-council` without access to this machine's `~/.claude/agents/` |
| PP-3 | Support more than one concurrently active sprint | The team's actual delivery pattern changes from one-sprint-at-a-time (per D9); `active_sprints`' list shape already accommodates this without a schema change |
| PP-4 | Extend mandatory artefact-writing beyond `/arch-council` and `/tester` to the remaining seven commands | The pilot demonstrates the best-effort integrations (§5, Changesets 3/5) are being followed reliably without a hard mandate |

---

## 4. Exact target file inventory

### 4.1 New files — static, cross-sprint, repository (created once, in Changeset 1)

| Path | Purpose | Location |
|---|---|---|
| `docs/sprints/CURRENT.md` | Names the active sprint workspace(s) via `active_sprints: [...]` — nothing else. Per D9, exactly one entry enforced for now. | Repository |
| `docs/sprints/WORKFLOW.md` | Static transition/parallel/skip/rework rules — modeled on `docs/audit-program/WORKFLOW.md`'s stage-lifecycle section. | Repository |
| `docs/sprints/STAGE-REGISTRY.md` | One row per stage (`roadmap`, `pm`, `architecture`, `arch-council`, `implementation`, `verification`, `security`, `audit`, `test`, `retro`) — purpose, mandatory status, entry conditions, inputs, outputs, dependencies, parallel compatibility, skip conditions, completion criteria, human gate. Per D2 (approved), this is the authoritative source; CLAUDE.md's auto-invoke table is trimmed to point here (Changeset 10). | Repository |
| `docs/sprints/README.md` | One paragraph: what this folder is, links to the diagnostic documents as design rationale, and to `docs/audit-program/` / `docs/agentic-architecture-review/` as the precedent this reuses. | Repository |

### 4.2 New files — per-sprint, repository (created in Changeset 2, **only once the pilot sprint is selected** — not created by this plan)

| Path | Purpose | Mandatory or conditional? |
|---|---|---|
| `docs/sprints/<pilot-sprint-id>/CONTEXT.md` | Goal, in-scope stories, out-of-scope, acceptance criteria | Mandatory — created the moment `/pm` produces stories for the pilot |
| `docs/sprints/<pilot-sprint-id>/state.md` | Authoritative per-stage status (diagnostic §7.2) | Mandatory |
| `docs/sprints/<pilot-sprint-id>/decisions.md` | Append-only HITL decision log | Mandatory |
| `docs/sprints/<pilot-sprint-id>/evidence/` | Raw artefacts, one subfolder per stage | Mandatory folder, contents conditional |
| `docs/sprints/<pilot-sprint-id>/plan.md` | Copy of the approved plan from `~/.claude/plans/`, per D5 | Conditional — only if plan mode ran |
| `docs/sprints/<pilot-sprint-id>/architecture.md` | Arch-council Council Summary verdict | Conditional — only if `/architect` or `/arch-council` ran; mandatory once it does, per D7 |
| `docs/sprints/<pilot-sprint-id>/verification.md` | `/verify` findings | Conditional |
| `docs/sprints/<pilot-sprint-id>/audit.md` | `/auditor` findings (in addition to, not instead of, `docs/audit/`) | Conditional |
| `docs/sprints/<pilot-sprint-id>/retrospective.md` | Pointer to the sprint's entry in `docs/retro-reports/` — not a duplicate | Mandatory (thin — Changeset 8) |

### 4.3 New files — repository, not sprint-scoped

| Path | Purpose | Changeset |
|---|---|---|
| `scripts/lint_sprint_state.py` | Mechanical validator (§5.7) | 7 |
| `scripts/lint_sprint_state.fixtures/{bad-decision-ref,illegal-parallel,clean}.md` | Three synthetic test fixtures the script must be proven against before pilot use | 7 |

### 4.4 Existing files/sources that must change

| Path | Change | Location | Changeset |
|---|---|---|---|
| `~/.claude/skills/roadmap/SKILL.md` | Add one step: after presenting the roadmap, read `docs/sprints/CURRENT.md` and report the active sprint/stage-set alongside the backlog view | **User-home** | 3 |
| `~/.claude/skills/pm/SKILL.md` | Add: on story approval for the pilot sprint, create `docs/sprints/<id>/CONTEXT.md` from the agreed stories/AC | **User-home** | 3 |
| `~/.claude/skills/architect/SKILL.md` | No content change to the 15 retro addenda — only a pointer added: "if a sprint workspace exists under `docs/sprints/`, log decisions there per `STAGE-REGISTRY.md`" | **User-home** | 3 |
| `~/.claude/skills/arch-council/SKILL.md` | Step 4 ("Synthesise and Present") gains a mandatory final step: write the Council Summary to `docs/sprints/<id>/architecture.md` and append a `decisions.md` entry with the verdict | **User-home** | 4 |
| `~/.claude/skills/security/SKILL.md`, `auditor/SKILL.md`, `tester/SKILL.md` | Each gains one line: "if `docs/sprints/<id>/` exists, also update `state.md` for this stage and write findings to the corresponding `<stage>.md`" — existing `docs/security/`, `docs/audit/`, `docs/test-reports/` outputs are unchanged, this is additive | **User-home** | 5 |
| `~/.claude/skills/retro/SKILL.md` | Add: check every `state.md` entry for stages not yet `complete`/`skipped`/`not-applicable`; flag before allowing sprint close | **User-home** | 8 |
| `~/.claude/settings.json` | **Deferred to PP-1** — no change in this implementation pass | **User-home** (not actioned) | — |
| `.../agentic-payroll-platform/CLAUDE.md` | Trim "Automated Delivery Workflow" section to reference the global sequence + point to `docs/sprints/STAGE-REGISTRY.md` for entry conditions, per D2/D4 | **Repository** | 10 |
| `.claude/memory/` (stale committed folder) | Renamed to `.claude/memory-archived-2026-07/`, per D6 | **Repository** | 10 |

### 4.5 Explicitly not created

- No per-stage `CONTEXT.md` files inside `docs/sprints/<id>/` beyond the single sprint-level `CONTEXT.md` — stage-level detail lives in `STAGE-REGISTRY.md` (shared) plus `state.md` (per-sprint instance), not in per-stage folders. The sprint workflow runs many short sprints, so per-sprint (not per-stage) folders are the right grain — unlike `docs/audit-program/`'s 13 numbered stage folders, which fit its single long-running investigation.
- No workflow engine, no CI pipeline, no new slash commands, no `~/.claude/settings.json` hook (deferred to PP-1), no copied persona files (deferred to PP-2).

---

## 5. Ordered changesets

Each changeset states exact files, preconditions, implementation actions, validation, rollback, expected commit boundary, and whether it needs further human approval before it may start.

### 5.1 Changeset 1 — Shared static workflow definitions

- **Files created:** `docs/sprints/CURRENT.md`, `docs/sprints/WORKFLOW.md`, `docs/sprints/STAGE-REGISTRY.md`, `docs/sprints/README.md` (all repository)
- **Files updated / moved / archived:** none
- **Preconditions:** D2 approved (✅, this document)
- **Implementation actions:** (1) draft `STAGE-REGISTRY.md`'s 10 rows directly from CLAUDE.md's existing auto-invoke table and the SKILL.md descriptions, with no new rules invented; (2) draft `WORKFLOW.md`'s transition/parallel/skip/rework rules per diagnostic §7.3–7.6; (3) `CURRENT.md` created with `active_sprints: []` (empty — no pilot selected yet); (4) `README.md` linking the three diagnostic documents
- **Validation:** manual read-through confirming `STAGE-REGISTRY.md`'s 10 stages contradict nothing in CLAUDE.md's auto-invoke table (a contradiction here would itself be a G5-style duplication bug, caught before it ships)
- **Rollback:** delete the four files — nothing else references them yet, so this is a clean revert with zero blast radius
- **Expected commit boundary:** one commit, four new files, no other file touched
- **Further approval needed before starting:** **No** — D2 is resolved; this changeset can start immediately upon run approval

### 5.2 Changeset 2 — Pilot sprint workspace creation

- **Files created:** `docs/sprints/<pilot-id>/CONTEXT.md`, `state.md` (all stages `not-started`), `decisions.md` (empty), `evidence/` — **not created by this plan; blocked on pilot selection**
- **Files updated:** `docs/sprints/CURRENT.md` (`active_sprints` gains the pilot's ID)
- **Preconditions:** Changeset 1 merged; **pilot sprint explicitly selected** (per D1(b) and the drop-file's explicit instruction not to select or create the workspace prematurely)
- **Implementation actions:** once a pilot is named, scope it via `/pm` as normal, then materialize `CONTEXT.md` from the agreed AC, an empty `state.md` listing all 10 stages as `not-started`, an empty `decisions.md`, and an empty `evidence/` folder
- **Validation:** `state.md` validates against the schema in diagnostic §7.2 (manual for this changeset; automated from Changeset 7 onward)
- **Rollback:** remove the sprint folder; revert `CURRENT.md`'s `active_sprints` entry
- **Expected commit boundary:** one commit per pilot-workspace creation, separate from Changeset 1's commit
- **Further approval needed before starting:** **Yes — pilot sprint ID and scope.** This is the one open item this plan does not resolve; it is a scheduling input, not a re-opened design decision (D1's *option* is already approved).

### 5.3 Changeset 3 — Command/skill integration: roadmap, pm, architect

- **Files created:** none
- **Files updated:** `~/.claude/skills/roadmap/SKILL.md`, `~/.claude/skills/pm/SKILL.md`, `~/.claude/skills/architect/SKILL.md` (all **user-home**)
- **Preconditions:** Changesets 1–2 merged (needs a live pilot workspace to validate against)
- **Implementation actions:** append the additive steps described in §4.4; no existing checklist content in `architect/SKILL.md` is altered
- **Validation:** run `/roadmap` and `/pm` live against the pilot; confirm `CONTEXT.md` is created with the agreed AC and `/roadmap`'s output includes the pilot's active-stage set — a STATIC read of the SKILL.md diff does not count as validation, per this project's own LIVE/STATIC/CODE-REVIEW taxonomy
- **Rollback:** revert the three SKILL.md files to their pre-changeset content (these are **not** tracked in this git repository — reverting means restoring the local file content, since `~/.claude/` changes leave no commit history here)
- **Expected commit boundary:** none in this repository (user-home only); if `CONTEXT.md` is created for the pilot in the same work session, that is Changeset 2's commit, not this one
- **Further approval needed before starting:** No — D7 already scopes this as best-effort, non-mandatory integration

### 5.4 Changeset 4 — Plan and architecture-verdict persistence

- **Files created:** `docs/sprints/<pilot-id>/plan.md` (repository, copied from `~/.claude/plans/`), `docs/sprints/<pilot-id>/architecture.md` (repository)
- **Files updated:** `~/.claude/skills/arch-council/SKILL.md` (**user-home**); `docs/sprints/<pilot-id>/state.md` and `decisions.md` (repository, mandatory per D7)
- **Preconditions:** Changesets 1–2 merged; D3 and D5 approved (✅)
- **Implementation actions:** add the mandatory final step to `arch-council/SKILL.md`'s "Synthesise and Present" stage; establish the ExitPlanMode convention (documented here, not a harness change) that Casper copies the approved plan into `docs/sprints/<id>/plan.md` immediately upon approval
- **Validation:** run a real `/arch-council` pass on the pilot; confirm `architecture.md` and a `decisions.md` entry both exist **before** the skill reports its verdict to chat — this is the changeset that most directly closes G2/G3, so its validation must be a live run, not a read-through
- **Rollback:** revert `arch-council/SKILL.md` (user-home, no repo commit to revert); any `architecture.md`/`plan.md` already written during the pilot are left in place as historical record unless the pilot itself is abandoned
- **Expected commit boundary:** one repository commit per artefact write (`plan.md` at plan approval, `architecture.md` at council verdict) — these occur naturally during the pilot, not as a single upfront commit
- **Further approval needed before starting:** No — D3/D5 resolved; gated only on Changeset 2 (pilot exists)

### 5.5 Changeset 5 — Verification, audit, and test persistence

- **Files created:** `docs/sprints/<pilot-id>/verification.md`, `audit.md` (repository, conditional on `/verify` / `/auditor` actually running)
- **Files updated:** `~/.claude/skills/security/SKILL.md`, `auditor/SKILL.md`, `tester/SKILL.md` (**user-home**); `docs/sprints/<pilot-id>/state.md` (repository)
- **Preconditions:** Changesets 1–2 merged; D7 approved (✅ — mandatory for `/tester` only; `/security`/`/auditor` best-effort)
- **Implementation actions:** append the one-line integration described in §4.4 to each of the three SKILL.md files; existing `docs/security/`, `docs/audit/`, `docs/test-reports/` writing habits are untouched
- **Validation:** run each skill live against the pilot; confirm existing outputs are unaffected (regression check) and the new `state.md` entries appear correctly
- **Rollback:** revert the three SKILL.md files individually (user-home) — each is independent, partial rollback is safe
- **Expected commit boundary:** repository commits only for the conditional `verification.md`/`audit.md` files and `state.md` updates, as they're produced during the pilot
- **Further approval needed before starting:** No

### 5.6 Changeset 6 — HITL decision recording

- **Files created:** none beyond what Changesets 2/4/5 already create
- **Files updated:** `~/.claude/skills/retro/SKILL.md` (**user-home**) — adds a `decisions.md` completeness check (partial; the full retro gate lands in Changeset 8)
- **Preconditions:** Changesets 2, 4, 5 merged (there must be decisions to check)
- **Implementation actions:** formalize the `decisions.md` schema from diagnostic §7.7 as the target every skip/not-applicable/rework/parallel-allow decision writes to
- **Validation:** manually audit the pilot's `decisions.md` at this point — does every `decision_ref` cited anywhere in `state.md` resolve to an entry here? (Becomes automatic in Changeset 7.)
- **Rollback:** no file removal needed — this changeset is process discipline layered onto existing files, not new files of its own
- **Expected commit boundary:** none new in this repository beyond ongoing `decisions.md` entries already covered by Changesets 4/5's commit boundaries
- **Further approval needed before starting:** No

### 5.7 Changeset 7 — Mechanical validation / linting (load-bearing)

- **Files created:** `scripts/lint_sprint_state.py`, three fixture files under `scripts/lint_sprint_state.fixtures/` (all repository)
- **Files updated:** none in this changeset — **`~/.claude/settings.json` is explicitly not touched here**, per D8; hook promotion is PP-1, not part of this changeset
- **Preconditions:** Changesets 1, 2, 6 merged
- **Implementation actions:** write a script that (a) parses every `state.md` under `docs/sprints/`, (b) confirms every `decision_ref` resolves to a `decisions.md` entry, (c) confirms every `depends_on`/`may_run_with` pairing is legal per `STAGE-REGISTRY.md`, (d) flags orphaned `skipped`/`not-applicable` entries missing a reason
- **Validation:** run the script against the three synthetic fixtures created in this same changeset — (i) a `state.md` with a nonexistent `decision_ref` must fail, (ii) a `state.md` with an illegal `may_run_with` pairing must fail, (iii) a clean, consistent `state.md` must pass — **before** the script is ever run against the real pilot's live `state.md`
- **Rollback:** delete the script and fixtures; no hook exists yet to remove
- **Expected commit boundary:** one commit — script + fixtures together, since the fixtures are the script's own proof of correctness and should never be separated from it in history
- **Further approval needed before starting:** No — D8 resolved to script-first; this changeset *is* "script-first"

### 5.8 Changeset 8 — Pilot execution and retrospective

- **Files created:** `docs/sprints/<pilot-id>/retrospective.md` (thin pointer, repository)
- **Files updated:** `~/.claude/skills/retro/SKILL.md` (**user-home**, completes the state-completeness gate started in Changeset 6)
- **Preconditions:** Changesets 1–7 merged; pilot sprint has run its actual stages
- **Implementation actions:** `/retro` explicitly checks `docs/sprints/<pilot-id>/state.md` for any stage not in a terminal status (`complete`/`skipped`/`not-applicable`) before allowing sprint close; the pilot's six required test scenarios (diagnostic §9 / this plan's §9 below) are exercised during real execution, not simulated afterward
- **Validation:** the full §9 acceptance-criteria pass, executed against the real pilot
- **Rollback:** if the pilot is abandoned for reasons unrelated to workflow mechanics, delete the sprint folder and revert `CURRENT.md`'s `active_sprints` entry — Changesets 1, 3–7 remain merged and are exercised again by the next pilot attempt
- **Expected commit boundary:** final commit closing the pilot sprint's `docs/sprints/<pilot-id>/` workspace
- **Further approval needed before starting:** **Yes, implicitly** — this changeset cannot start until Changeset 2's pilot-selection gate is cleared; no separate approval beyond that

### 5.9 Changeset 10 — CLAUDE.md consolidation and memory archival

- **Files created:** `.claude/memory-archived-2026-07/` (rename target, repository)
- **Files updated:** `.../agentic-payroll-platform/CLAUDE.md` (repository); `.claude/memory/` renamed, not deleted, per D6
- **Preconditions:** none beyond D4/D6 approval (✅) — independent of the pilot's outcome, may run before, during, or after it
- **Implementation actions:** trim the project CLAUDE.md's "Automated Delivery Workflow" section to a pointer at the global sequence + `docs/sprints/STAGE-REGISTRY.md`; `git mv .claude/memory .claude/memory-archived-2026-07`
- **Validation:** diff CLAUDE.md before/after to confirm no substantive rule was dropped, only de-duplicated; confirm the archived folder still contains its one file, untouched
- **Rollback:** `git revert` this changeset's commit (both the CLAUDE.md trim and the rename are trivially reversible)
- **Expected commit boundary:** one commit, isolated from the pilot's own commits, so it can be reviewed and merged independently
- **Further approval needed before starting:** No — but recommended to run this in its own reviewed PR/commit given CLAUDE.md is loaded by every session (per the original plan's own risk note)

**Note on numbering:** Changeset 9 is intentionally unused, preserved from the prior draft to keep changeset IDs stable across this revision.

**Recommended execution order:** 1 → [pilot selection] → 2 → 3 → 4 → 5 → 6 → 7 → 8, with Changeset 10 run independently whenever convenient. Changeset 1 is the only changeset with zero remaining preconditions and can start immediately.

---

## 6. Repository vs. user-home changes — what Casper can commit vs. what must be applied locally

This split matters operationally, not just organizationally: **only the repository column below is visible in this git history, portable to another machine, or reviewable via `git diff`.** The user-home column is Claude Code configuration specific to this operator's machine — Casper can and will apply it directly in the active environment when a changeset calls for it, but it leaves no commit, no PR, and no trace for a second operator or a fresh clone of this repository to inspect.

| Changeset | Repository changes (committed, in `git log`) | User-home changes (`~/.claude/`, applied locally, not in git history) |
|---|---|---|
| 1 | `docs/sprints/{CURRENT,WORKFLOW,STAGE-REGISTRY,README}.md` | — |
| 2 | `docs/sprints/<pilot-id>/{CONTEXT,state,decisions}.md`, `evidence/` | — |
| 3 | — | `skills/{roadmap,pm,architect}/SKILL.md` |
| 4 | `docs/sprints/<pilot-id>/{plan,architecture}.md` | `skills/arch-council/SKILL.md` |
| 5 | `docs/sprints/<pilot-id>/{verification,audit}.md` | `skills/{security,auditor,tester}/SKILL.md` |
| 6 | (ongoing `decisions.md` entries, already tracked above) | `skills/retro/SKILL.md` (partial) |
| 7 | `scripts/lint_sprint_state.py` + fixtures | — |
| 8 | `docs/sprints/<pilot-id>/retrospective.md` | `skills/retro/SKILL.md` (completes gate) |
| 10 | `CLAUDE.md` (trimmed), `.claude/memory-archived-2026-07/` | — |
| PP-1 (deferred) | — | `settings.json` (new hook) |
| PP-2 (deferred) | possibly `docs/sprints/_personas/` if reactivated | `agents/{senior-architect,principal-reviewer}.md` (unchanged unless PP-2 fires) |

This is precisely the reproducibility gap the original diagnostic named in D3/G-findings: **a fresh clone of this repository, on a different machine or by a different operator, gets the repository column in full but none of the user-home column.** `/roadmap`, `/pm`, `/architect`'s pointer, `/arch-council`'s mandatory write, `/security`/`/auditor`/`/tester`'s integration, and `/retro`'s gate would all need to be re-applied locally on that machine before the workflow behaves as designed there — the `docs/sprints/` artefacts themselves would still be fully readable and correct, but the *behavior that produces new ones* would not yet exist on the new machine. This is accepted for the pilot (per D3's approval) and tracked for reactivation under PP-2 if a second operator or remote agent becomes a real requirement.

---

## 7. Validation plan

- **Per-changeset validation** is specified in each subsection of §5 and must pass before the next changeset merges — changesets are not batched into one review.
- **Schema validation**: the lint script from Changeset 7 must be run against its own three synthetic fixtures *before* being trusted against the real pilot — see §5.7.
- **Live-run validation**: every skill change (Changesets 3–6) is validated by actually invoking the command against the pilot sprint and inspecting the resulting file — not by reading the SKILL.md diff and assuming it works, per this project's own `/tester` LIVE/STATIC/CODE-REVIEW taxonomy. A SKILL.md edit that hasn't been exercised live is a STATIC check, not a PASS.
- **Regression validation**: every existing output convention (`docs/stories/`, `docs/security/`, `docs/audit/`, `docs/test-reports/`, `docs/retro-reports/`) must be confirmed unchanged after each relevant changeset.

---

## 8. Rollback plan

- **Changesets 1, 2, 10**: pure file addition/rename in the repository — `git revert` of the changeset's commit is sufficient and safe at any point.
- **Changesets 3, 5, 6, part of 8**: user-home SKILL.md edits are additive instructions (new steps appended, nothing existing removed) — restoring the pre-changeset file content locally reverses them; there is no repository commit to revert for these, per §6.
- **Changeset 4** (arch-council): higher risk because it modifies a *mandatory* gate. Rollback: restore `arch-council/SKILL.md`'s pre-changeset content locally; any `architecture.md`/`plan.md` already committed during the pilot are left in place as historical record rather than deleted, unless the pilot itself is abandoned.
- **Changeset 7** (linting): if the script produces false positives, the immediate mitigation is to stop invoking it — it is a script, not a hook, so no repository or user-home state needs to change to "turn it off."
- **Changeset 8** (pilot execution): if the pilot sprint itself is abandoned for reasons unrelated to workflow mechanics, delete the sprint folder and revert `CURRENT.md`'s `active_sprints` entry — Changesets 1, 3–7 remain merged (repository) or applied (user-home) regardless, and are exercised again by the next pilot attempt.
- **General principle**: no changeset performs a destructive operation on an existing file except Changeset 10's rename of `.claude/memory/` — and D6 specifies rename, not delete, so even that step is reversible.

---

## 9. Pilot acceptance criteria

A fresh Casper session, given repository access only (no chat history, no auto-memory loaded), must be able to answer each of the following from `docs/sprints/<pilot-id>/` and the static files alone — with the explicit caveat from §6 that the *behavior* producing new artefacts depends on user-home skill changes not present in that fresh clone, while the *artefacts already produced* remain fully readable:

| Question | Answered by |
|---|---|
| Which sprint is active? | `docs/sprints/CURRENT.md` |
| Which stages are active, blocked, complete, skipped, or not-applicable? | `<pilot-id>/state.md` |
| What has been approved? | `<pilot-id>/plan.md`, `<pilot-id>/architecture.md`, `<pilot-id>/decisions.md` |
| What evidence exists? | `<pilot-id>/evidence/<stage>/` |
| What decisions were made and by whom? | `<pilot-id>/decisions.md` — every entry has `decision_owner` |
| What work may proceed in parallel? | `<pilot-id>/state.md`'s `may_run_with` fields, cross-checked against `STAGE-REGISTRY.md` |
| What is currently blocked? | `<pilot-id>/state.md` entries with `status: blocked` and their `waiting_for` field |
| What are the next permitted actions? | Any stage in `<pilot-id>/state.md` with `status: eligible` |

### Required test scenarios (seeded deliberately, not left to chance)

1. **One skipped stage** — e.g. `/ux-designer` skipped because the pilot is backend-only; `decisions.md` entry present with reason and owner.
2. **One not-applicable stage** — e.g. `/security` marked `not-applicable` if the pilot touches no API route; distinguished in `state.md` from the skipped stage above.
3. **Two parallel stages** — e.g. `/verify` and `/security` both `active` at once, evidence written to separate `evidence/<stage>/` subfolders without collision.
4. **One rework loop** — a `complete` stage deliberately reopened to `needs-rework` via a recorded decision, confirming its dependents automatically revert to `blocked`.
5. **One unresolved dependency** — a stage left `blocked` on purpose, `waiting_for` correctly naming the unmet stage, later resolving to `eligible`.
6. **One invalid `decision_ref` caught mechanically** — a deliberately broken fixture (not real pilot data) run through the Changeset 7 lint script to confirm it fails loudly.

The pilot is not considered complete until all six scenarios have been exercised and every question above can be answered correctly by a reviewer reading only the repository files for `<pilot-id>`.

---

## 10. Statement of no implementation

No file listed in §4/§5 has been created, moved, archived, or modified as a result of this plan. `docs/sprints/` does not exist in this repository as of 2026-07-12. No `~/.claude/skills/*`, `~/.claude/settings.json`, or `~/.claude/agents/*` file has been changed in the active environment. Decisions D1–D9 are approved (§3); the plan is implementation-ready; **execution has not begun and requires separate run approval**, plus selection of the pilot sprint before Changeset 2 can start.
