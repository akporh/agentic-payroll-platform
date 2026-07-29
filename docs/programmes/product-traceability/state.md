# State — Product Traceability Programme

*Last updated: 2026-07-29 — **Phase 5 complete (D-029). Every defined phase is now closed and the programme is in steady state.** Migration finished at 157 of 157 (100%) under Phase 4D (critic PASS). Authoritative snapshot — see `runs/discovery-run-001.md`, `runs/hierarchy-approval-run-001.md`, `runs/structure-implementation-run-001.md`, `runs/historical-migration-pilot-run-001.md`, `runs/historical-migration-confirmed-batch-run-001.md`, `runs/hierarchy-completion-run-001.md`, `runs/historical-migration-cap6-run-001.md` and `runs/historical-migration-remainder-run-001.md` for full run records.*

## Current phase

`sprint-workflow integration` — **Phase 5**, authorised 2026-07-29 by **D-029**. **Complete.** The last defined phase; the programme now moves to steady state under `PHASES.md` § "Steady state".

Traceability is wired into the sprint workflow at two points: `pm` allocates the `STORY-<nnnn>` when scope is agreed, and `retro` completes the registry row at close under its existing Close Gate. Amendments were confined to the `pm` and `retro` rows of `STAGE-REGISTRY.md` and one new subsection in `WORKFLOW.md` — no stage added, no dependency, gate or ordering changed. The skill-side handover (`~/.claude/skills/`, which stayed forbidden by explicit choice) **was applied by the human on 2026-07-29 and verified.** Nothing outstanding.

### Previously — `historical migration`, Phase 4D (remainder, all 103 items), authorised by **D-027**. Complete.

**Coverage: 157 of 157 (100%)**, up from 54 of 157. Every capability with allocated items is fully migrated. `CAP-12` Agent Layer holds zero items by design (D-023, OQ-6) and stays visibly empty.

**Phase 4 as a whole is now closed.** There is no further migration authorisation to give — 4A (2), 4B (19), 4C (33) and 4D (103) exhaust the inventory.

### What Phase 4D changed, beyond the count

While the registry was partial, a story's absence meant either "not yet migrated" or "no such work exists", and nothing distinguished them. It now means the second. That is the property the programme was commissioned to produce, and it is the first point at which `docs/product/` can be used as evidence rather than as a partial index.

D-027 also retired capability-shaped batching. Phases 4A/4B/4C existed to prove the mechanism at increasing scale — 2 items, then 19, then a whole 33-item capability — and that proof was complete. The controls were not retired with the batching: the same template, validator, verbatim-confidence rule and evidence discipline applied to 103 items as to 33, and caught two real defects in the process.

## Executor status

`complete` for discovery, hierarchy-approval, structure-implementation, Phase 4A pilot, Phase 4B confirmed-batch, Phase 3B hierarchy completion, Phase 4C `CAP-6` batch, and **Phase 4D remainder**.

**157 stories migrated** into `docs/product/`:
- 2 from Phase 4A · 19 from Phase 4B · 33 from Phase 4C (`CAP-6` in full) · **103 from Phase 4D**

Registry-wide composition: 150 `delivered`, 6 `backlog`, 1 `in-flight`; 68 `confirmed`, 66 `strongly inferred`, 17 `tentative`, 6 `requires human classification`.

## Critic status

`complete` for every phase run to date.

**Prior verdicts:** Discovery `approve-for-human-review`. Hierarchy approval `approve`. Structure implementation `approve-with-amendments`. Phase 4A pilot `approve-with-amendments`. Phase 4B confirmed-batch — see its review. Phase 3B **PASS**. Phase 4C **PASS**. **Phase 4D `PASS`** (`critic-review-phase-4d-remainder.md`) with three non-blocking observations (O-1 evidence-strength profile, O-2 the `STORY-0054`/`STORY-0055` double record, O-3 no staleness marker in the registry header).

## Human-gate status

All decisions to date **received and recorded**: D-001–D-029.

**No open human gate.** D-029 authorised Phase 5 and satisfied its *before* gate by naming the exact allowed-path expansion prior to any file being written.

**Phase 5 is authorised and complete.** It was the last defined phase; the programme is now in steady state.

## Blocked or outstanding decisions

- **None blocking.** Every defined phase is closed, the deliverable exists in full, and the skill handover is applied.
- **Handover complete (2026-07-29).** The human applied the Phase 5 text to `~/.claude/skills/`: `/pm` now allocates the `STORY-<nnnn>` at scope, and `/retro` carries a **Part C — Product-traceability gate** (items 12–17) as a hard stop in its Sprint Workspace Close Gate. Verified in place.
- **A pre-existing defect was found and fixed in passing:** `/pm` declared `tools: Read, Glob, Grep` — no write access — while its own "Sprint Workspace Integration" section had long instructed it to create `docs/sprints/<id>/CONTEXT.md`. That instruction had never been executable, and any `/pm` run as a subagent silently skipped it. Now `tools: Read, Glob, Grep, Write, Edit`. **Unrelated to this programme** — surfaced only because Phase 5 needed `/pm` to write an ID. Worth a look at whether other skills carry the same mismatch between declared tools and instructed behaviour.
- Carried follow-ups, unchanged and owned outside this programme: PH_OT `is_pensionable` (D-010/DP-04, now `STORY-0036`) and the Gate 4 status contradiction (D-012/DP-06, now `STORY-0057`).

### Evidence weaknesses now visible in the completed registry

Recorded honestly inside the stories themselves; surfaced here because a complete-looking registry invites the assumption that completeness implies verification. It does not.

- **57% of the registry is not `confirmed`** — 68 `confirmed`, 66 `strongly inferred`, 17 `tentative`, 6 `requires human classification`. **45** items rest on `docs/ROADMAP.md` as their only source, concentrated in Sprint 0 and Sprints 1–6. *(Corrected 2026-07-29 from "53%" and "43 items" — both were understated; recounted directly from `STORY-REGISTRY.md`.)*
- **Three items carry an unresolved contradiction or a blocked verification:** `STORY-0057` (Gate 4 — ROADMAP ✅ against its own story file saying pending), `STORY-0103` (browser UAT BLOCKED), `STORY-0105` (multi-contract verification BLOCKED; fix applied but unverified). **All three now carry the verification state in their title** (D-028) — previously only `STORY-0105` did, so a reader scanning the registry table saw `status: delivered` on the other two with nothing but the `confidence` column to contradict it.
- **Two standing gaps recorded but not closed:** actor attribution (`STORY-0041` backend-only, `STORY-0153` deferred to Track P) and the `overrides_json` destruction path, which `STORY-0140` records as having zero test coverage.
- **`STORY-0148`** — the `agentic-architecture-review` programme — is `in-flight`, not delivered. Stage 13 is open awaiting DP-2 and DP-9.

## Next permitted action

**None — the programme is done.** Every defined phase is closed, the skill handover is applied, and no further phase exists. The next thing that touches this layer should be an ordinary sprint, via `/pm` and `/retro`.

**What Phase 5 changed.** The discovery inventory has a **2026-07-15 horizon** (D-026), and three sprints were found missing from it — two by method gap (D-024), one by recency (D-026). Each was recovered by chance. Traceability is now written *during* a sprint rather than reconstructed after one: `pm` allocates the `STORY-<nnnn>` when scope is agreed, `retro` completes the registry row at close, and `retro`'s existing Close Gate will not let a sprint finish with an unresolved `story_ref`. The decay described in the previous version of this section is closed at source — a sprint can no longer quietly fail to register itself.

**What it does not change.** Everything already in the registry keeps the evidence profile recorded above; wiring the intake does not retro-verify 45 rows whose only source is `docs/ROADMAP.md`, and closed sprints were deliberately not retrofitted. New work should enter as `confirmed` off its own test and audit evidence, so that profile improves going forward rather than retrospectively.

**Steady state.** `PHASES.md` § "Steady state" now governs: adding stories is routine sprint work needing no decision here; changing the *shape* of the hierarchy still requires a new phase and a decision in `decisions.md`.
