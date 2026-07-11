# Sprint Workflow — ICM Diagnostic

**Date:** 2026-07-11
**Scope:** Repository diagnostic, read-only — no application code, migrations, or workflow files were modified in the course of this inspection.
**Question:** Is the sprint workflow (`/roadmap` → `/pm` → `/architect` → `/arch-council` → plan mode → implementation → `/verify`/`/security` → `/auditor`/`/tester` → `/retro` → push) implemented as an Interpretable Context Methodology (ICM) workspace, or does it only appear as one because it's a disciplined sequence of slash commands?

---

## 1. Executive conclusion

> **Sequential workflow, not ICM-structured**

The workflow is a well-disciplined *sequence of skill invocations*, not a workspace. Every stage's instructions live in one shared, always-loaded prompt (three stacked `CLAUDE.md` files plus whichever `SKILL.md` is active) rather than in a stage-scoped folder the stage reads on entry. There is no folder boundary per stage, no `CONTEXT.md` contract, and — critically — no single directory that answers "what sprint is active, what stage is it in, what was approved" by itself. That answer currently lives across three places that don't reference each other: `docs/ROADMAP.md` (backlog state), `~/.claude/plans/*.md` (plan artefacts, outside the repo, unlinked from anything), and a per-project auto-memory index (`handoff_note.md`) that is itself a duplicate of a second, stale, in-repo memory folder.

Tellingly, two *other* workspaces in this same repository — `docs/agentic-architecture-review/` and `docs/audit-program/`, both freshly created — already implement the exact pattern this diagnostic is checking for: numbered stage folders, a `CONTEXT.md` contract per stage, a `findings.md`/`decisions.md` handoff, a single `*-state.md` tracker, and an explicit gate rule ("a stage may not begin until the prior stage's gate has been explicitly passed"). The sprint workflow that ships product code has none of this. The capability to build ICM structure clearly exists in this environment; it was simply never applied to the workflow that matters most.

---

## 2. Current context map

| Stage | Command | Governing source | Inputs | Outputs | Gate | State location | Hidden dependencies |
|---|---|---|---|---|---|---|---|
| **Roadmap** | `/roadmap` | SKILL.md `roadmap` | `docs/ROADMAP.md` | Terminal text only | None | `docs/ROADMAP.md` (self-admittedly can go stale) | Skill tells the model to trust ROADMAP.md, but also says "may be stale" and to defer to `/brief` — no automatic check |
| **PM** | `/pm` | SKILL.md `pm` | Conversation only | Story text in chat; sometimes a file under `docs/stories/` | None enforced by tooling | No dedicated file — story creation is a human/model judgment call each time | Memory feedback file requires PM to "read existing stories" first — a rule that lives in memory, not in the skill itself |
| **Architect** | `/architect` | SKILL.md `architect` (218 lines, mostly retro-derived checklists) | Conversation, plan draft | Design decisions in chat | None | None — decisions only persist if manually copied into a plan file or memory | Most of the file's checking power is 15 sprint-specific "retro" addenda appended over time — undiscoverable without reading the whole file top to bottom |
| **Arch-council** | `/arch-council` | SKILL.md + two persona files | `~/.claude/agents/senior-architect.md`, `principal-reviewer.md`, `docs/architecture/extraction-signals.md` | Verdict text in chat (APPROVED / NEEDS REVISION / …) | **Human**, informal | Extraction-signals.md is updated; the council verdict itself is **not written anywhere** | Persona files live in `~/.claude/agents/` — user-home, not repo — so a fresh clone of the repo cannot reconstruct who "the architect" is |
| **Plan mode** | `EnterPlanMode` / `ExitPlanMode` | Harness built-in | Everything discussed so far | `~/.claude/plans/<random-name>.md` | **Human** approval via ExitPlanMode prompt | `~/.claude/plans/` — **outside the git repo**, randomly named, not linked from ROADMAP or any story file | Nothing in the repo points to the plan file that was approved. Approval is a UI event, not a record. |
| **Implementation** | direct edits | 3 stacked `CLAUDE.md` files + PostToolUse hooks | Approved plan (from memory of the conversation) | Code diff | None besides the hooks firing reminders | Git history | Hooks are configured in `~/.claude/settings.json`, a user-level file — not visible from the repo itself |
| **Verify / Security** | `/verify`, `/security` | Global `verify` skill (bootstraps a project-local one if absent — **none exists yet**); `security` SKILL.md | Running app, changed routes | Findings in chat; security review sometimes written to `docs/security/YYYY-MM-DD-*.md` | None enforced | `docs/security/` exists but is written inconsistently — only 3 dated files across 30+ sprints | The project has no project-scoped `verify` skill despite the global one expecting to bootstrap one — first invocation would silently create it ad hoc |
| **Audit / Test** | `/auditor`, `/tester` | SKILL.md per skill | Running app, sprint AC | `docs/audit/`, `docs/test-reports/YYYY-MM-DD-sprint-N.md` | Tester's own PASS/FAIL taxonomy (LIVE vs STATIC vs CODE REVIEW) | Consistently written — **the one stage with a real, disciplined artefact convention** | None major — this is the strongest link in the chain |
| **Retro / Push** | `/retro` | SKILL.md `retro` | `git log`, `MEMORY.md`, plan file "if it still exists" | Edits to SKILL.md files, memory files, sometimes CLAUDE.md | "With user confirmation" | Diffuse — spread across skill files, memory files, and CLAUDE.md with no single retro log | Retro step itself notes the plan file "if it still exists" — an acknowledgment that plan-file persistence is already known to be unreliable |

---

## 3. Authority map

| Instruction source | Scope | Loaded by | Authority | Conflicts | Recommendation |
|---|---|---|---|---|---|
| `~/.claude/CLAUDE.md` | All projects | Always, automatically | governing | None found | Retain as-is |
| `.../2.OnAiR/CLAUDE.md` | All onAiR work | Always, automatically | governing | None found | Retain |
| `.../Sandy/CLAUDE.md` | Sandy client | Always, automatically | workflow-level | None found | Retain |
| `.../agentic-payroll-platform/CLAUDE.md` | This codebase | Always, automatically | workflow-level | Duplicates the global "Sprint Sequence" almost verbatim — same 17 steps restated with local auto-invoke triggers layered on | Consolidate: reference the global sequence, hold only auto-invoke triggers + data-contract table |
| `~/.claude/skills/*/SKILL.md` (9 files) | One stage each | On explicit invocation only | stage-level | `architect` and `arch-council` overlap heavily — both claim data-contract review | Keep, but split architect's 15 appended retro sections into a separate "lessons" reference |
| `~/.claude/agents/senior-architect.md`, `principal-reviewer.md` | arch-council only | Spawned by arch-council skill | stage-level | User-home scoped — not visible to anyone cloning the repo | Relocate persona definitions (or a copy) into the repo if verdicts must be reproducible by another operator |
| `docs/ROADMAP.md` | Backlog state | Manually, by `/roadmap` | task-specific | Roadmap skill itself documents known staleness risk | Retain, but wire the "post-sprint accuracy check" into a script instead of a manual grep list |
| `~/.claude/plans/*.md` | One plan each | Manually, must know exact filename | generated | Not referenced from anywhere in the repo once written | Copy the approved plan into `docs/planning/` or `docs/stories/` at ExitPlanMode time so it survives outside harness-local state |
| `.claude/memory/project_sprint13_m3_arch_decisions.md` (repo-committed) | Appears project-wide | Nothing — orphaned | **stale** | **Directly conflicts** with the real, current memory store below — same-looking path, one file, frozen at Sprint 13 | Deprecate / delete; dead weight that could mislead a future session or tool that globs `.claude/memory/` |
| `~/.claude/projects/.../memory/*.md` (75 files, MEMORY.md index) | This project, cross-session | Auto-loaded at session start | task-specific | Same nominal purpose as the file above, different location, no cross-link | This is the real, live store — keep, but resolve the name collision with the dead in-repo folder |
| `docs/security/`, `docs/audit/`, `docs/test-reports/`, `docs/retro-reports/` | Per-sprint evidence | Manually, written inconsistently | reference-only | Coverage is uneven — test-reports has 20+ files, security has 3, retro-reports has 1 | Make one of these mandatory-on-close (test-reports already functions this way) and apply the same discipline elsewhere |
| `~/.claude/settings.json` hooks | All Sandy work, user-level | Fires automatically on Edit/Write/Bash | governing (mechanical) | None — the one deterministic, always-on part of the system | Retain; this is the model for what stage gates should look like everywhere else |

---

## 4. Context provenance map

| Rule | Origin |
|---|---|
| 17-step sprint sequence, arch-council gate triggers, memory rules | **Repository file** — both CLAUDE.md layers, duplicated |
| Per-stage checklists (input validation, migration safety, trace completeness…) | **Repository file** — `~/.claude/skills/*/SKILL.md`, user-home but versioned by Claude Code tooling conventions |
| "is_active means not-withdrawn, always pair with effective_from" and 14 other data-contract invariants | **Repository file** — CLAUDE.md "Known Data Contract Rules" table (the single best piece of ICM-shaped state in the whole workflow) |
| Duplicate revision-ID check, str(e) reminder, tsc reminder, push reminder | **Hook** — `~/.claude/settings.json` PostToolUse/PreToolUse, mechanical and reliable |
| "PM must read docs/stories/ before generating stories"; "no blind implementation without a sprint"; "confirm scope before plan mode" | **Agent memory** only — not restated anywhere in CLAUDE.md or the pm/architect skill files. If auto-memory ever fails to load, this rule is gone with no fallback. |
| Which persona plays "Senior Architect" / "Principal Engineer" in arch-council | **Slash command** pointing at `~/.claude/agents/*.md` — user-home, unversioned relative to the repo |
| Whether a given roadmap item is actually done | **Unknown source** — the roadmap skill itself says to distrust the file and re-derive from grep; there is no authoritative record, only a re-derivation procedure |
| What the currently active sprint even is | **Conversation history** only. No file in the repo names "the current sprint." ROADMAP.md lists closed sprints; nothing marks one *open*. |
| Whether an arch-council verdict was APPROVED / NEEDS REVISION for a specific design | **Conversation history** only — printed to chat, never written to a file |
| Fix commits / retro lessons ("re-verify the fix touches the reported bug", etc.) | **Skill file**, correctly promoted from memory into `architect/SKILL.md` — this is the one place the loop from "caught late" to "written into governing instructions" visibly closes |

---

## 5. Fresh-session reconstruction test

Could a brand-new Casper session answer these from the repo alone?

| Question | Answer |
|---|---|
| What sprint is active? | **No** — ROADMAP.md lists sprint history but has no "current sprint" marker. Answerable only via the auto-memory handoff note, which is outside the repo and can be stale or absent. |
| Which stage is active? | **No** — no file records "we are between arch-council and implementation." Only conversation history or an unwritten mental model carries this. |
| What has been approved? | **No** — plan-mode approval is a UI click, never persisted. Arch-council verdicts print to chat and vanish. The data-contract rules table in CLAUDE.md is the one exception: real, durable, repo-visible approvals. |
| What must be read? | **Partially** — CLAUDE.md's "Key Files to Read Before Planning" is a good static list, but nothing tells a fresh session which of the 30+ story files, 20+ test reports, or 3 security reviews are relevant to the item currently in flight. |
| What output is expected? | **Partially** — test-reports and stories have a clear naming/file convention a new session could infer and follow. Plans, arch-council verdicts, and PM stories do not. |
| What cannot be changed? | **Yes** — the "Known Data Contract Rules" and "API Route Rules" tables in CLAUDE.md are exactly this: durable, explicit, repo-visible constraints. The strongest part of the whole system. |
| What is the next allowed stage? | **No** — there is no stage-lifecycle concept at all (contrast with `docs/audit-program/WORKFLOW.md`'s explicit `not-started → in-progress → blocked → complete` lifecycle, which exists a few directories away in the same repo for a different workflow). |

---

## 6. Gap register

| ID | Gap | Evidence | Consequence | Severity | Recommended correction |
|---|---|---|---|---|---|
| G1 | No file names the currently active sprint or stage | `docs/ROADMAP.md` has no "current" marker; no `docs/sprints/<active>/` folder exists | A fresh session cannot self-orient; must reconstruct state from conversation or hope the memory handoff note is current | High | Add one file, `docs/sprints/CURRENT.md`, updated at each stage transition |
| G2 | Plan-mode output lives outside the repo and is never linked to | `~/.claude/plans/*.md` — randomly named, home-directory scoped | Approved plans cannot be audited later, cannot be diffed against implementation, invisible to any other tool or teammate | High | Copy the approved plan into `docs/planning/<sprint>.md` at ExitPlanMode time, referenced from the story file |
| G3 | arch-council verdicts are never written to a file | arch-council SKILL.md Step 4 ("Synthesise and Present") outputs only to chat | The one mandatory data-contract gate produces no durable evidence that it ran, or what it concluded — undermines the "RC5 lesson" the gate exists to prevent | High | Write the Council Summary to `docs/architecture/decisions/<date>-<topic>.md` as a mandatory last step |
| G4 | Two divergent memory stores with the same nominal purpose | `.claude/memory/` (1 stale file, committed to git) vs `~/.claude/projects/.../memory/` (75 files, live) | A future contributor or tool that reads the committed `.claude/memory/` folder gets a Sprint-13 snapshot presented as current | Medium | Delete the stale committed folder or clearly mark it archived; document the real store is user-home scoped |
| G5 | Project CLAUDE.md restates the global sprint sequence almost verbatim instead of referencing it | Compare "Sprint Workflow" in `~/.claude/CLAUDE.md` to "Automated Delivery Workflow" in the project file — same 17 steps, duplicated | Any future edit to the global sequence silently diverges from the project copy unless both are remembered and updated together | Medium | Project file should hold only local deltas (auto-invoke triggers, hook table) and link to the global sequence |
| G6 | Uneven evidence discipline across stages | `docs/test-reports/` has 20+ dated files; `docs/security/` has 3; `docs/retro-reports/` has 1; audit has 2 | Tester's stage is the only one that reliably leaves a trail — security, audit, and retro findings are largely reconstructable only from memory or chat | Medium | Apply the tester skill's "always write the file, even on failure" rule to security, auditor, and retro identically |
| G7 | Architect's checklist is 218 lines of accreted, undated retro addenda with no index | `~/.claude/skills/architect/SKILL.md` — 15+ sprint-specific sections appended chronologically | A check added in a Sprint 7 retro is discoverable only by reading the entire file; nothing signals which checks are "core" vs. situational | Medium | Split into a short core checklist plus a separate, searchable lessons file the skill links to by keyword |
| G8 | No project-scoped `verify` skill exists yet, despite the global skill assuming one | Global `verify` skill description: "bootstraps this repo's project verify skill if none exists yet" — none found under any expected path | First invocation silently creates ad hoc process instead of following a pre-agreed, reviewed procedure | Low | Bootstrap it deliberately once, in a reviewed session, rather than letting the first real verify pass improvise it |
| G9 | Two sibling workspaces in the same repo already solve this problem correctly, unreferenced by the sprint workflow | `docs/agentic-architecture-review/WORKFLOW.md`, `docs/audit-program/WORKFLOW.md` | Working ICM pattern exists a few directories away and is not being reused — proof the fix is cheap, not proof the gap is minor | Low (opportunity) | Lift the stage-folder + `CONTEXT.md` + state-tracker pattern from these two workspaces directly into a minimal sprint-workspace structure (see §7) |

---

## ICM criteria scoring (0–3 each)

| Criterion | Score | Notes |
|---|---|---|
| A — Visible stage structure | 1/3 | No stage folders. `docs/` subfolders exist per artefact type (stories, test-reports), not per stage. |
| B — Stage contracts | 1/3 | SKILL.md files are contracts for the *skill*, not the sprint stage — no per-sprint `CONTEXT.md`. |
| C — Context isolation | 1/3 | Every stage runs inside the same shared 3-layer CLAUDE.md + full conversation history. |
| D — Explicit handoffs | 2/3 | Test reports and stories hand off cleanly; plans and arch-council verdicts do not persist at all. |
| E — Filesystem state | 1/3 | No file answers "what stage, what's approved" without chat or memory. |
| F — Authority hierarchy | 2/3 | Global → project → local CLAUDE.md is a real, consistent hierarchy; undermined by duplication (G5) and the orphaned memory folder (G4). |
| G — Resumability | 1/3 | Depends entirely on the auto-memory handoff note being current and undamaged — a single point of failure, not a repo guarantee. |
| H — Human control | 2/3 | Gates are real (ExitPlanMode, arch-council, retro confirmation) but their outcomes aren't recorded — the gate fires, the record doesn't. |
| I — Mechanical vs. reasoning work | 3/3 | PostToolUse/PreToolUse hooks genuinely enforce migration-ID checks, push reminders, and tsc reminders deterministically. Best-scoring criterion. |
| J — Traceability | 1/3 | A roadmap item can be traced to a story and a test report by filename convention, but not through architecture, plan, or security/audit review — those links exist only in a human's memory of the sprint. |

**Total: 15/30** — informal-to-partial across the board, with one deterministic bright spot (I) and one structural strength worth preserving (F's hierarchy, once G4/G5 are cleaned up).

---

## 7. Recommended target structure

Not a framework — four additions, modeled directly on the pattern already proven in `docs/audit-program/` and `docs/agentic-architecture-review/` in this same repo:

| Addition | Purpose | Modeled on |
|---|---|---|
| `docs/sprints/<sprint-id>/CONTEXT.md` | One page: goal, in-scope stories, out-of-scope, acceptance criteria, current stage | `docs/audit-program/01-system-inventory/CONTEXT.md` pattern |
| `docs/sprints/<sprint-id>/plan.md` | The approved plan, copied out of `~/.claude/plans/` at ExitPlanMode — no longer harness-local, no longer randomly named | Closes G2 directly |
| `docs/sprints/<sprint-id>/arch-council.md` | The Council Summary verdict, written as the mandatory last step of the skill instead of printed only to chat | Closes G3 |
| `docs/sprints/CURRENT.md` | One line: which sprint-id folder is active and which stage it's in — the single file a fresh session reads first | `docs/audit-program/audit-state.md`'s stage-status table, shrunk to sprint scope |

Everything else already works well enough to retain: the three-layer CLAUDE.md hierarchy, the SKILL.md checklists, the hook-enforced mechanical checks, and the test-reports convention. This is deliberately small — four files, not a new methodology.

---

## 8. Migration plan

**Not to be implemented until approved.**

| Action | Item |
|---|---|
| Retain | Three-layer CLAUDE.md hierarchy; SKILL.md per stage; PostToolUse/PreToolUse hooks; test-reports naming convention; "Known Data Contract Rules" table |
| Relocate | Plan-mode output (`~/.claude/plans/` → `docs/sprints/<id>/plan.md` at approval time); arch-council persona files, if reproducibility across operators matters |
| Make explicit | Current sprint/stage (new `docs/sprints/CURRENT.md`); arch-council verdicts (write, don't just print); which memory items are process rules that belong in CLAUDE.md instead (PM/no-blind-implementation rules) |
| Consolidate | Project CLAUDE.md's restated 17-step sequence → reference the global one, keep only local deltas; architect skill's 15 retro addenda → core checklist + linked lessons file |
| Deprecate | The committed, stale `.claude/memory/` folder (1 file, frozen at Sprint 13) — superseded by the real auto-memory store |
| Automate | Roadmap's "post-sprint accuracy check" (currently a manual grep checklist) → a script; security/audit/retro report-writing → same "always write, even on fail" enforcement tester already has |
| Do not change | The underlying calculation/domain rules, hook logic, or skill content itself — this diagnostic is about workflow state architecture only |

---

*Companion visual report (same content, styled): rendered as a Claude Artifact during the diagnostic session.*
