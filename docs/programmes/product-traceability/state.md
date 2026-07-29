# State — Product Traceability Programme

*Last updated: 2026-07-29 — Phase 4D complete (critic PASS). **Migration is finished: 157 of 157 items (100%). Phase 4 is closed.** Authoritative snapshot — see `runs/discovery-run-001.md`, `runs/hierarchy-approval-run-001.md`, `runs/structure-implementation-run-001.md`, `runs/historical-migration-pilot-run-001.md`, `runs/historical-migration-confirmed-batch-run-001.md`, `runs/hierarchy-completion-run-001.md`, `runs/historical-migration-cap6-run-001.md` and `runs/historical-migration-remainder-run-001.md` for full run records.*

## Current phase

`historical migration` — **Phase 4D** (remainder, all 103 items), authorised 2026-07-29 by **D-027**. **Complete.**

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

All decisions to date **received and recorded**: D-001–D-027.

**No open human gate.** D-027 authorised Phase 4D; its human gate is *after* — a spot-check of the completed registry, with nothing blocked pending it.

**The next human decision is whether to authorise Phase 5 (`sprint-workflow integration`).** It is the only phase left, and the only defence against the decay described below.

## Blocked or outstanding decisions

- **None blocking.** The programme is at a clean stopping point, and a more meaningful one than the last: the deliverable it was commissioned to produce now exists in full.
- Phase 5 authorisation — not yet decided. It requires an explicit allowed-path expansion into `docs/sprints/`, currently a forbidden path for this programme.
- Carried follow-ups, unchanged and owned outside this programme: PH_OT `is_pensionable` (D-010/DP-04, now `STORY-0036`) and the Gate 4 status contradiction (D-012/DP-06, now `STORY-0057`).

### Evidence weaknesses now visible in the completed registry

Recorded honestly inside the stories themselves; surfaced here because a complete-looking registry invites the assumption that completeness implies verification. It does not.

- **53% of the registry is not `confirmed`** — 66 `strongly inferred`, 17 `tentative`. 43 items rest on `docs/ROADMAP.md` as their only source.
- **Three items carry an unresolved contradiction or a blocked verification:** `STORY-0057` (Gate 4 — ROADMAP ✅ against its own story file saying pending), `STORY-0103` (browser UAT BLOCKED), `STORY-0105` (multi-contract verification BLOCKED; fix applied but unverified).
- **Two standing gaps recorded but not closed:** actor attribution (`STORY-0041` backend-only, `STORY-0153` deferred to Track P) and the `overrides_json` destruction path, which `STORY-0140` records as having zero test coverage.
- **`STORY-0148`** — the `agentic-architecture-review` programme — is `in-flight`, not delivered. Stage 13 is open awaiting DP-2 and DP-9.

## Next permitted action

**Human decision: authorise Phase 5, or stop.** Nothing else in this programme is available to execute.

**Why Phase 5 now matters more than it did.** The discovery inventory has a **2026-07-15 horizon** (D-026), and three sprints have already been found missing from it — two by method gap (D-024), one by recency (D-026). Every sprint that closes without registering itself here makes the registry quietly wrong again, so the completeness achieved today decays from the day it was achieved. Wiring traceability into sprint closure is the only durable fix, and the one remaining thing between "the registry is complete" and "the registry stays complete."
