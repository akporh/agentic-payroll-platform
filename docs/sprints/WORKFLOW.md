# Sprint Workflow

**Static, cross-sprint, reusable.** This file defines the transition, parallel, skip, and rework rules that operate over `STAGE-REGISTRY.md`. It does not restate stage-specific detail (purpose, entry conditions, dependencies, parallel compatibility, mandatory status) — that lives only in `STAGE-REGISTRY.md`, per D2. This file states the general rules; the registry states the per-stage specifics those rules operate on.

Modeled on `docs/audit-program/WORKFLOW.md`'s stage-lifecycle section and the non-linear execution model approved in `docs/diagnostics/2026-07-11-sprint-workflow-icm-diagnostic.md` §7.

---

## Why non-linear

Stages are skipped (`security` when no routes changed), run out of order (a design question surfaced during implementation can send work back to `architecture`), and run concurrently (`verification` and `security` both start once `implementation` lands, without waiting on each other). This workflow models sprint state as a **graph** — an active stage *set*, not a single "current stage" scalar — because that is how the work actually happens, not because non-linearity is a goal in itself.

## Stage status values

Every stage in a sprint's `state.md` carries exactly one of these statuses:

| Status | Meaning |
|---|---|
| `not-started` | Registered in the sprint but no entry condition has been evaluated yet |
| `eligible` | Entry conditions and dependencies are satisfied; not yet activated |
| `active` | Currently being worked |
| `blocked` | Cannot proceed — `waiting_for` names the unmet dependency |
| `complete` | Completion criteria met, evidence recorded |
| `skipped` | Deliberately not run this sprint — reversible; may be activated later if conditions change |
| `not-applicable` | Structurally does not apply to this sprint's type — not merely deferred, and not reversible without a scope change |
| `needs-rework` | Was `complete`, reopened by a recorded human decision; downstream dependents revert to `blocked` |

`skipped` vs. `not-applicable` is a real distinction, not a style choice. A `skipped` stage remains a candidate for later activation if new evidence changes the picture (e.g. implementation turns out to touch a status enum after all, so `arch-council` — previously thought not-applicable — must be re-evaluated). `not-applicable` means the stage's precondition structurally cannot occur this sprint and does not need re-evaluating unless the sprint's scope itself changes.

**Update `state.md` in the same turn the work finishes, not later.** The turn that completes a stage's substantive work (writing the code, running the review, producing the evidence) must also write that stage's terminal status into `state.md` — do not defer this as bookkeeping to "do later." A stage left at `eligible`/`active`/`not-started` after its work is actually done is invisible to every downstream dependency check and to `retro`'s Sprint Workspace Close Gate, which will then have to catch and correct it retroactively (`dev-levy-rule-pct` sprint, 2026-07-17 — `implementation` and `verification` were both found stale this way).

## Eligibility rule

A stage becomes `eligible` the moment every stage ID in its `depends_on` list is `complete`, `skipped`, or `not-applicable` — **never** on `active` or `blocked`. This is the only eligibility rule; there is no separate "soft" eligibility.

**Default routing when no decision is recorded is always `blocked`, never silently `not-applicable`.** A stage does not become `not-applicable` by omission — it requires an explicit decision (see Skip and not-applicable rules, below) with a `decision_ref` that resolves in `decisions.md`. Absence of a decision leaves a stage `blocked`, which is visible and inspectable, rather than silently skipped.

## Parallel stage rules

- A stage may declare `may_run_with: [<stage-id>, ...]` in its sprint's `state.md` **only if** that pairing appears in that stage's `Parallel compatibility` column in `STAGE-REGISTRY.md`. A sprint cannot invent a parallel pairing the registry doesn't allow.
- Per the registry as currently drafted: `verification` and `security` may run concurrently. `implementation` and `audit` must never run concurrently.
- Parallel stages write evidence to isolated subfolders — `evidence/<stage>/` — so two stages running at once never overwrite each other's artefacts.
- A parallel stage still needs its own dependencies satisfied independently; `may_run_with` only says two eligible/active stages don't block each other — it does not mean they share entry conditions.

## Skip and not-applicable rules

Every `skipped` or `not-applicable` entry in a sprint's `state.md` **must** carry, at minimum:

```yaml
status: skipped            # or not-applicable
reason: <one sentence, specific>
decision_owner: <name>
decision_ref: DEC-<sprint>-<seq>   # must resolve to an entry in decisions.md
date: YYYY-MM-DD
compensating_control: <optional — what covers the risk instead, if anything>
```

`STAGE-REGISTRY.md`'s `Mandatory status` column governs whether skipping is even a legal move:

- A **mandatory** stage (e.g. `arch-council` when its entry condition holds) cannot be marked `skipped` — only `not-applicable`, and only if the entry condition genuinely does not hold, with a `decision_ref`.
- A **conditional** stage (e.g. `verification`, `security`, `audit`, `architecture` — each conditional on a specific trigger in the registry) may be `skipped` when its trigger doesn't apply, or marked `not-applicable` if the trigger structurally cannot occur — the reason is mandatory either way; no empty reasons.
- There are currently no stages registered as `optional` in `STAGE-REGISTRY.md`; if one is added later, an `optional` stage may be `skipped` freely, same reason requirement.

## Rework loop rules

- A `complete` stage may be reopened to `needs-rework` only via a recorded decision in `decisions.md` — never silently.
- The moment a stage moves to `needs-rework`, every stage whose `depends_on` includes it automatically reverts to `blocked` in `state.md` — this is a mechanical consequence of the eligibility rule above, not a separate rule to remember or apply by hand.
- Prior evidence is never deleted. A second pass writes to `evidence/<stage>/attempt-2/`; `state.md` records `attempt: 2` so it's visible which pass produced the artefact currently governing the stage's `complete` status.
- Rework does not restart the whole sprint — only the reopened stage and its dependents change status. Independent stages (e.g. `retro`, if it hasn't started yet) are unaffected.

## Recording HITL decisions

`<sprint-id>/decisions.md` is an append-only log — one entry per human decision, in the order they were made:

```yaml
- id: DEC-<sprint>-<seq>
  date: YYYY-MM-DD
  decision_owner: <name>
  stage: <stage-id>
  decision_type: skip | not-applicable | activate | allow-parallel | rework | block
  reason: <specific, one sentence minimum>
  reference: <conversation date/context, or a linked artefact>
```

Every `decision_ref` cited anywhere in a sprint's `state.md` must resolve to an `id` here. A reason with no matching `decisions.md` entry is a lint failure (`scripts/lint_sprint_state.py`, once introduced), not a valid state — this is what makes gate outcomes durable: an `arch-council` verdict, for instance, becomes a `decisions.md` entry, not a chat message that evaporates when the session ends.

## Product traceability

Every sprint records what it built into `docs/product/`, the durable product hierarchy, as part of running — not as a clean-up afterwards. This exists because the alternative has already failed: the hierarchy was built from a discovery pass with a **2026-07-15 horizon**, and three sprints closed after it without registering anything. They were recovered by chance, not by process (D-024, D-026 in `docs/programmes/product-traceability/decisions.md`). Authorised by **D-029**.

**`story_refs`** — a sprint-instance field in `CONTEXT.md`, listing the `STORY-<nnnn>` identifiers this sprint delivers:

```yaml
story_refs:
  - id: STORY-0158
    title: <short title, matching the registry row>
    status_at_close: delivered | backlog     # written by retro, not pm
```

**Allocated at `pm`, completed at `retro`.** The split is deliberate. At `pm` the scope is known and the evidence does not exist yet, so the stage reserves the next free ID in `docs/product/ID-ALLOCATION.md` and writes `story_refs`. At `retro` the sprint's test, audit and security evidence finally exists, so that stage writes the full `STORY-REGISTRY.md` row and story file — including `evidence_refs`, `sprint_refs` and `confidence`. Allocating only at close would mean a sprint runs start to finish with nothing to reference; completing only at `pm` would mean inventing evidence that doesn't exist.

**Rules:**

- IDs are **strictly sequential on allocation, never renumbered, never reused** (D-019). A story dropped from scope mid-sprint keeps its ID; the ID is retired, not recycled.
- `confidence` at close is set from *this sprint's own evidence*, and a sprint with a passing test report and audit review should be recording `confirmed`. Do not write `strongly inferred` for work you just built and verified — that value exists for retro-migrated history, not for new work.
- A story that was scoped but **not** delivered closes as `status: backlog`, never silently dropped. A reader must not be able to mistake abandoned scope for delivered work by its absence (D-011).
- This applies to **new** sprints only. Closed sprint workspaces are history and are not retrofitted.

**Close gate.** `retro` cannot reach `complete` while any `story_ref` is unresolved — this is part of the same Sprint Workspace Close Gate that already requires every stage to be terminal. That is what makes traceability a condition of closing rather than a habit that decays.

*Known gap (D-029):* the `/pm` and `/retro` skills in `~/.claude/skills/` perform this work, and that path is outside this programme's authorised scope. The obligation above is enforced by the close gate; the skill-side prompts were handed over for manual application.

## Sprint completion

A sprint is done when every activated stage in its `state.md` is `complete`, `skipped`, or `not-applicable` — not when some fixed final stage number is reached. `retro` checks this explicitly before allowing sprint close (see `STAGE-REGISTRY.md`'s `retro` entry): no stage may be left `active` or `blocked` at close, and no `story_ref` may be left unresolved.

## Separation of concerns

| Concern | Lives in | Reused across sprints? |
|---|---|---|
| Reusable skill instructions (how to run a stage, what to check) | `~/.claude/skills/*/SKILL.md` — unchanged by this workflow | Yes |
| Stage metadata (purpose/inputs/outputs/dependencies/mandatory-ness) | `docs/sprints/STAGE-REGISTRY.md` | Yes |
| Transition/parallel/skip/rework rules | `docs/sprints/WORKFLOW.md` (this file) | Yes |
| Which sprint(s) are active | `docs/sprints/CURRENT.md` | Yes (points at whichever sprint is current) |
| Sprint-specific context (goal, scope, AC) | `docs/sprints/<id>/CONTEXT.md` | No — one per sprint |
| Current execution state | `docs/sprints/<id>/state.md` | No — one per sprint, mutated in place |
| Human decisions | `docs/sprints/<id>/decisions.md` | No — append-only per sprint |
| Generated evidence | `docs/sprints/<id>/evidence/` | No — per sprint, per stage, per attempt |
| Durable record of what was built (story → sprint → evidence) | `docs/product/` — written by `pm` (ID) and `retro` (full row) | Yes — the permanent cross-sprint record |

Skill logic stays in `~/.claude/skills/` exactly where it is today — this workflow does not ask any sprint file to restate a checklist. `CONTEXT.md` / `state.md` / `decisions.md` hold only sprint-instance data; `STAGE-REGISTRY.md` / `WORKFLOW.md` (this file) hold only the rules, once.
