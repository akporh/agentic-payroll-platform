# Stage 11: Commercial & Product Strategy — Context

## Status

context-ready (populated 2026-07-18 by the controller on Stage 10's closure — critic PASS, zero required corrections, report in `10-evaluation-assurance/outputs/critic-review.md`)

## Objective

Assess the commercial and product-strategy dimension of the approved 15-capability portfolio — the last diagnostic stage before synthesis. Concretely: map where each capability's value actually lands (Sandy's internal bureau efficiency vs client-visible service quality vs future sellable differentiation); consolidate the binding sequencing constraints and their costs into one economics picture Stage 13 can sequence from; dispose DQ-005 jointly with Stage 09's recorded recommendation; classify the product scope boundaries that are commercial decisions in disguise (multi-operator workspaces, multi-tenant SaaS, C15 email); and state what the assurance/trust posture supports claiming — and forbids overclaiming — in positioning. This stage produces strategy *inputs* for Stage 12 (target direction) and Stage 13 (roadmap); it decides neither.

## Binding decisions inherited (pre-scope — do not re-litigate)

- **D-03-01** (recorded 2026-07-12, `_core/HUMAN-DECISIONS.md` HD-6): the 15-capability portfolio is approved — strategy is built on these capabilities and their dispositions (7 reclassified deterministic, C4/C8 blocked, C9 rejected, C15 deferred), not the source document's five tracks. Conditions 12, 9–11: C1/C2 are deterministic platform engineering, sequenced/staffed separately from AI-capability work; C11+C12 sequenced together; C13 never ahead of C14.
- **D-02-01–04** (thesis boundaries): current-state-only assistant boundary (D-02-03), independent tool-layer enforcement (D-02-02) — commercial narratives must not assume blocked capabilities unblock.
- **D-04-01**: layered C7 calibration, gated on the exception workflow; measurement-framework prohibitions (chat/usage volume never a success metric; dry-run-pass ≠ client-validated accuracy; C11 success is precision, never detection volume) apply to any commercial KPI this stage proposes.
- **Stage 06/07/10 registers are fixed**: CG/SG/SS gates and the launch-gate evidence register (incl. its sequencing preconditions: C7-after-C2, C13-after-C14, C11-with-C12) are constraints on any commercial timeline — a gate may only be weakened by a recorded human decision.
- **RR-1 trigger (c)** (`10-evaluation-assurance/outputs/residual-risk-register.md` §3): if this stage proposes multi-tenant SaaS commercialisation, the audit-tamper residual reaffirmation does not carry over — it must be flagged as re-opening a human risk decision, not absorbed silently.
- **DEC-08-09** visibility item: C12's statutory UNIQUE widening is a data-contract change going through `/arch-council` at Phase 3 — budget it, don't re-decide it.

## Confirmed facts to consume (do not re-verify)

- **`10-evaluation-assurance/outputs/stage-11-handoff.md`** (assurance economics): cost table (frontend harness one-off with C1; eval infra one-off with C3; capped operator cadence), hard sequencing facts (C7 GA lags deploy ≥3 cycles; B1/B2 baselines need a real onboarding *before* C13's build or they are unrecoverable; B6 needs a 4-week pre-C3 window; DQ-006/007 are pre-build human gates with professional-advice lead time), and the claimable-vs-overclaim boundary list (§3).
- **`09-human-experience/outputs/stage-11-handoff.md`** (surface economics + DQ-005): the DQ-005 recommendation (contextual "Create correction run" CTA with/after C12 — §1) awaiting this stage's joint disposition; the FULL_RUN dead-option cheap fix (§2); surface scope facts (§3: C1-first UI order, three-chrome-additions scope, C12 as the first platform-level area = one-off structural cost, C13/C14 extend three-consumer shared components, single-operator v1 posture means "multi-operator bureau" is a distinct product increment, "platform with an assistant" not "chat product"); deferred-by-design items not to re-open as gaps (§4).
- **Stage 04**: `outcome-prioritisation.md` (pursue-now ordering incl. exception-resolution workflow first) and `measurement-framework.md` (per-capability success/safety metrics — the value claims this stage makes must be measurable under it).
- **Stage 05**: `capability-readiness-matrix.md` and blocker findings (zero auth; event/notification/exception foundation unbuilt — the readiness reality any commercial timeline starts from).
- **Stage 02**: product thesis outputs (assessment, capability matrix, boundary doc, principles — esp. Principle 8's positioning implication).

## Required inputs

Read: `README.md`, `WORKFLOW.md`, `review-state.md`, `decision-queue.md`; all files under `_core/`; the two stage-11 handoffs above; Stage 04's `outcome-prioritisation.md` + `measurement-framework.md`; Stage 05's `capability-readiness-matrix.md`; Stage 02's outputs as needed; `10-evaluation-assurance/outputs/launch-gate-evidence-register.md` (the sequencing-precondition rows). **Business/market facts** (client intent, willingness to pay, competitive context) that cannot be independently observed require either a registered external source or a human-reviewer statement logged per `_core/EVIDENCE-STANDARD.md` type 5 — never invented; where a needed business fact is unavailable, record it as an evidence gap rather than assuming it. Record any new source in `_inputs/source-register.md`.

## Questions this stage must answer

1. **Commercial value map**: for each of the 15 capabilities (and the blocked/rejected/deferred ones as explicit non-value rows), where does the value land — Sandy's internal efficiency, bureau-client-visible service quality, or future sellable differentiation — grounded in Stage 04's outcomes and the Stage 10 §3 claimable-posture list. Which capabilities are commercially load-bearing vs enabling plumbing.
2. **Sequencing economics**: consolidate every binding sequencing constraint (D-03-01 conditions; evidence-register preconditions; assurance windows — C7 shadow lag, baseline capture windows; surface costs — platform-level area, three-surface regression obligation; DQ-006/007 professional-advice lead times) into one costed dependency picture with the calendar-bound items called out. Not a roadmap — the constraint set Stage 13 sequences within.
3. **DQ-005 joint disposition**: concur with, amend, or escalate Stage 09's recommendation (contextual correction-run CTA with/after C12; no generic dropdown exposure). If concurring, classify and close the queue item; if a commercial need for earlier standalone correction runs exists, that is a scope decision to surface to the human reviewer with Stage 09's reasoning attached.
4. **Product scope boundaries as commercial decisions**: multi-operator workspaces (a distinct UX/product increment, Stage 09 §3), multi-tenant SaaS (arms RR-1 trigger (c) + FEAT-021's unscoped status), C15 email, and any boundary this stage's value analysis surfaces — classify each as in-scope-now / later-increment / requires-human-decision, with reasoning. Do not decide the human ones.
5. **Positioning and claims inputs**: what the trust/assurance posture supports leading with (auditable-AI queue/approval surfaces per Stage 09 §3; the four claimable properties per Stage 10 §3) and the overclaim boundaries (RR-1/3/4/5); consistency with Principle 8 ("platform with an assistant"). Inputs for Stage 12's narrative — not marketing copy.
6. **Pre-build decision logistics**: the concrete path to resolving DQ-006/DQ-007/DQ-008 (who provides professional input, what lead time, what build items they block) so Stage 13 can place them on the critical path deliberately.
7. **Near-term commercial windows**: the baseline-capture scheduling facts (B1/B2 need the next real onboarding under the current flow; B3/B5 retrospectives capturable now; B6's 4-week window) turned into concrete "do before X" items for Stage 13.
8. **Handoffs**: Stage 12 (strategy synthesis input: value map + positioning + boundary classifications) and Stage 13 (the sequencing-economics register + decision-logistics items).

## Required outputs

Create under `outputs/`: `commercial-value-map.md` (Q1), `sequencing-economics.md` (Q2+Q7), `product-scope-boundaries.md` (Q3+Q4 — incl. the DQ-005 disposition), `positioning-and-claims.md` (Q5), `pre-build-decision-logistics.md` (Q6), `stage-12-handoff.md`, `stage-13-handoff.md`. Update: `findings.md` (F-11-*), `decisions.md`, `review-state.md`, `decision-queue.md` (DQ-005 disposition), `_inputs/source-register.md` as required. (`outputs/critic-review.md` is the critic's.)

## Finding discipline

Per `_core/FINDING-SCHEMA.md` with the extended field pattern. This stage's exposure is inventing business facts: any claim about client behaviour, market demand, or willingness to pay must cite a registered source or a logged human statement — otherwise it is recorded as an assumption/evidence gap, never as a finding. Repo-state claims are verified against current source and pinned to a named commit as usual.

## Explicitly out of scope

- The roadmap itself (Stage 13) and target-direction synthesis (Stage 12)
- Re-opening the portfolio, dispositions, gates, mechanisms, surfaces, or assurance framework (mismatches → findings)
- Pricing *decisions*, client commitments, or any external communication (option framing is in scope; deciding is human)
- Marketing copy; Phase 2/3 authorisation; starting Stage 12

## Constraints

- Read-only with respect to production code; writes stay inside `docs/programmes/agentic-architecture-review/`.
- This is the stage most adjacent to genuine product/scope choices: classify every real choice per `CRITIC.md`'s taxonomy and forward human ones with options — the executor decides none of them (POLICY). DQ-005 is the one queue item this stage co-owns and may close, if concurring with Stage 09 turns it into an agreed implementation-specification rather than a choice.
- No commercial claim may contradict the measurement-framework prohibitions or the residual-risk overclaim boundaries.

## Completion criteria

Ready for the critic only when: every Q1–Q8 has an answer or explicitly-classified open item; every business fact is sourced, human-logged, or recorded as a gap; DQ-005 is dispositioned; Stage 12/13 handoffs are complete and consistent; decisions recorded and classified; non-blocking questions queued.

## Completion procedure (D-003 lifecycle)

1. Mark Stage 11 `awaiting-critic` in `review-state.md` and this file.
2. Independent critic per `CRITIC.md` → `outputs/critic-review.md`.
3. On `PASS` with no blocking human decision, close and open Stage 12 automatically per `RUNBOOK.md`.

## Next action

**Run the Stage 11 primary-executor pass per `RUNBOOK.md`.** Recommend a fresh session (D-004).
