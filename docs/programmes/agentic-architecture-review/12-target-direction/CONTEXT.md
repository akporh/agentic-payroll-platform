# Stage 12: Target Direction — Context

## Status

context-ready (populated 2026-07-18 by the controller on Stage 11's closure — critic PASS, zero required corrections, report in `11-commercial-product-strategy/outputs/critic-review.md`)

## Objective

Synthesise the diagnostic stages (01–11) into **one coherent target direction**: what the platform is becoming, stated precisely enough that Stage 13 can sequence a roadmap toward it and the human reviewer can approve or amend it. This is the first synthesis stage — it produces no new diagnosis. Concretely: a target-direction statement (operating model + product identity); the target architecture posture (the structural properties the direction commits to preserving); the product-direction narrative built from Stage 11's positioning inputs; the capability end-state picture (what "the portfolio realised" looks like, dispositions intact); direction-level success measures consistent with the measurement framework; and the explicit statement of the single-bureau/SaaS fork. This stage resolves *what the revision of the source architecture document says* — formal approval of it remains Stage 13's human gate (D-02-01).

## Binding decisions inherited (pre-scope — do not re-litigate)

- **D-02-01** (HD-2): `docs/architecture/agent-layer-architecture.html` "NEEDS REVISION" remains open — **this stage's synthesis is the formal revision path**; the document is not approved until Stage 13 records approval. The synthesis replaces the document's five-track structure with the approved portfolio's; it does not restate the document.
- **D-03-01** (HD-6): the 15-capability portfolio with all dispositions (7 deterministic, C4/C8 blocked, C9 rejected, C15 deferred, C11 restricted) and all 14 conditions is the reference. The target direction reflects the dispositions; it does not re-open them.
- **D-02-02/03/04**: tool-layer independence, current-state-only assistant boundary, C12 scoped independently of Y1 — direction statements must embed these, not soften them.
- **D-04-01**: layered C7 calibration gated on the exception workflow; measurement prohibitions (usage volume never success; dry-run ≠ validated; C11 precision never volume) bind any KPI this stage proposes.
- **Gate ratchet + registers fixed**: CG/SG/SS registers, the launch-gate evidence register, and the residual-risk register are constraints; only a recorded human decision weakens anything.
- **RR-1 trigger (c) discipline** (DEC-10-16, DEC-11-04): if the direction adopts an active multi-tenant SaaS trajectory, that is the human decision bundle — this stage may *frame* the fork, never resolve it.

## Confirmed facts to consume (do not re-verify)

- **`11-commercial-product-strategy/outputs/stage-12-handoff.md`** — the compressed value map (three sellable stories + the assurance posture as cross-capability differentiator; deterministic-first value reality DEC-11-03), positioning inputs with the overclaim table as hard boundary, boundary classifications (DQ-005 closed; multi-operator later-increment; **the SaaS fork this stage must state explicitly**: "single-bureau excellence, SaaS-ready posture" is executor-safe, "active SaaS trajectory" needs the human bundle per F-11-01), constraints inherited whole, EG-004/EG-005 discipline (capability-led language, not demand-led).
- **`10-evaluation-assurance/outputs/stage-12-handoff.md`** — the assurance posture paragraph (determinism-first, generated-from-structure tests, single-operator cadence) and its four structural properties for direction-setting (pattern-scaling assurance; route-table/tool-registry choke points as an architectural property the direction must preserve; C7-class slow-burn by design → trust-led not speed-led; the evidence register as sellable artifact).
- **Stage 02 outputs** — the retained thesis (AI for judgement/interpretation, deterministic for calculation/state/mutation) and the 11 principles (esp. 8: platform-with-assistant; 9: deterministic-first; 11: independent tool-layer scoping) — the direction is these principles projected forward.
- **Stage 04** `outcome-capability-matrix.md` / `product-opportunity-map.md` — the outcome landscape incl. the genuinely missing lifecycle area (F-04-06, operational reporting — classified later-increment by Stage 11).
- **Stage 05 readiness + Stage 08 designs** — the mechanism-level reality the direction builds on (readiness matrix; C1/C2 designs; remediation set).
- **Stage 09 IA/surface designs** — the experience shape (queue/panel/approval surfaces, chrome additions, platform-level area) the direction's product identity rests on.

## Required inputs

Read: `README.md`, `WORKFLOW.md`, `review-state.md`, `decision-queue.md`; all files under `_core/`; the two stage-12 handoffs above; Stage 11's other outputs as needed (`commercial-value-map.md`, `positioning-and-claims.md`, `product-scope-boundaries.md`); Stage 02's `product-thesis-assessment.md` + `non-negotiable-product-principles.md`; Stage 03's `agent-capability-matrix.md`; the source document S-04 (`docs/architecture/agent-layer-architecture.html`) **only** to state precisely what the revision changes about it (D-02-01) — it remains stated intent, not authority. Business facts remain type-5/registered-source-or-gap (EG-004/EG-005 open — the critic's Stage 11 note applies: keep competitor characterisations conditional/definitional, no unregistered competitive-landscape claims).

## Questions this stage must answer

1. **Target-direction statement**: one page — what the platform is (product identity), for whom, operated how (single-operator bureau reality), with what boundary between deterministic core and AI assistance — synthesised from the thesis, portfolio, and value map. Must state the fork: the direction this synthesis commits to absent a human decision is **single-bureau excellence with a SaaS-ready posture**; an active SaaS trajectory is framed as the alternative requiring the F-11-01 decision bundle.
2. **Target architecture posture**: the structural properties the direction commits to preserving as it grows (determinism-first guarantees; route-table/tool-registry as generation choke points; append-only evidence chain; independent tool-layer scoping; capped operating cadence) — stated as direction constraints future work is checked against, citing the Stage 10 handoff's four properties.
3. **Product-direction narrative**: the coherent story from Stage 11's positioning inputs (platform-with-assistant frame; three sellable stories paced by gates/baselines; overclaim boundaries as the position) — the narrative Stage 13's roadmap tells time over, and the substance of the source document's revision.
4. **Capability end-state map**: the 15 capabilities' realised end-state (what exists, what it does, what evidences it) with dispositions intact — including what the platform deliberately does *not* do (C4/C8 until preconditions, C9 never, boundaries from D-02-03). The concrete "to-be" picture replacing the source document's five tracks.
5. **Direction-level success measures**: a small set of direction KPIs (drawn from the measurement framework and B1–B6 baselines, honouring every prohibition) that tell the human reviewer whether the direction is *working* once builds land.
6. **Source-document disposition**: precisely what the revision changes about `agent-layer-architecture.html` (structure, capabilities, sequencing, claims) — as a recommendation for Stage 13's approval, resolving D-02-01's open status.
7. **Handoff**: Stage 13 (the direction as roadmap input: statement + end-state map + KPIs + the decision items already staged — DQ-007 pack, DQ-006/008 engagement, EG-004/005, SaaS fork, RR-1 visibility).

## Required outputs

Create under `outputs/`: `target-direction-statement.md` (Q1), `target-architecture-posture.md` (Q2), `product-direction-narrative.md` (Q3), `capability-end-state-map.md` (Q4), `direction-kpis.md` (Q5), `source-document-disposition.md` (Q6), `stage-13-handoff.md` (Q7). Update: `findings.md` (F-12-*, if any repo-state findings arise), `decisions.md`, `review-state.md`, `decision-queue.md` and `_inputs/source-register.md` as required. (`outputs/critic-review.md` is the critic's.)

## Finding discipline

Per `_core/FINDING-SCHEMA.md`. This is a synthesis stage — new findings are expected to be rare and only where synthesis exposes a genuine inconsistency between confirmed prior findings (a mismatch → finding, not a silent fix). The Stage 11 exposure carries over: no invented business/market facts; the fork framing uses only registered intent (F-11-01) and recorded gaps.

## Explicitly out of scope

- The roadmap, sequencing, and sprint shapes (Stage 13) — the direction says *where*, never *when*
- Deciding the SaaS fork, DQ-006/007/008, or any human decision — framing only
- Re-opening portfolio dispositions, gates, mechanisms, surfaces, assurance framework, or Stage 11's boundary classifications
- Editing `docs/architecture/agent-layer-architecture.html` or any path outside this programme (the revision is *described*, not applied — application is a Phase 3 act after Stage 13 approval)
- Marketing copy; Phase 2/3 authorisation; starting Stage 13

## Constraints

- Read-only with respect to production code and the source document; writes stay inside `docs/programmes/agentic-architecture-review/`.
- Every direction claim must trace to a confirmed finding, binding decision, or recorded handoff fact — synthesis adds arrangement, never new facts.
- No KPI may contradict the measurement-framework prohibitions; no narrative claim may cross the overclaim table (`11-commercial-product-strategy/outputs/positioning-and-claims.md` §3).
- Classify every real choice per `CRITIC.md`'s taxonomy; the executor decides none of them.

## Completion criteria

Ready for the critic only when: every Q1–Q7 has an answer; the fork is stated with the executor-safe default and the human alternative cleanly separated; the source-document disposition is concrete enough for Stage 13 to approve or amend; Stage 13 handoff is complete and consistent with `sequencing-economics.md` and the decision-logistics placements; decisions recorded and classified; non-blocking questions queued.

## Completion procedure (D-003 lifecycle)

1. Mark Stage 12 `awaiting-critic` in `review-state.md` and this file.
2. Independent critic per `CRITIC.md` → `outputs/critic-review.md`.
3. On `PASS` with no blocking human decision, close and open Stage 13 automatically per `RUNBOOK.md`. (Stage 13 itself always ends at a human approval gate.)

## Next action

**Run the Stage 12 primary-executor pass per `RUNBOOK.md`.** Recommend a fresh session (D-004).
