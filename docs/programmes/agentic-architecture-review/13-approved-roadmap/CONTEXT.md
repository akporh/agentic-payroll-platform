# Stage 13: Approved Roadmap — Context

## Status

context-ready (populated 2026-07-18 by the controller on Stage 12's closure — critic PASS, zero required corrections, report in `12-target-direction/outputs/critic-review.md`)

## Objective

Produce the **proposed roadmap** that sequences Phase 3 build work toward Stage 12's approved-direction outputs, inside Stage 11's constraint set, and assemble the **final human approval pack** — the mandatory Phase 1 end gate. This stage is the sole stage authorised to record approval of the target direction / source-document revision (D-02-01). Concretely: a sequenced, tranche-structured roadmap proposal with per-item definition-of-done tied to the launch-gate evidence register; the consolidated decision pack (DQ-007 + MFA options, visibility items, source-document disposition, evidence-gap asks); the baseline/near-term action plan; and the presentation of all of it to the human reviewer. **This stage always ends at the human approval gate — D-003 automatic closure does not apply to the final approval.** On critic PASS the stage moves to `awaiting-human-decision`, never to `closed`, until the human reviewer records the approval (or amendments) in `_core/HUMAN-DECISIONS.md`.

## Binding decisions inherited (pre-scope — do not re-litigate)

- **D-02-01** (HD-2): this stage records approval of the target direction and the source-document disposition (`12-target-direction/outputs/source-document-disposition.md` §1 recommends supersede-and-replace; approval or amendment is the human's).
- **D-03-01** (HD-6): the 15-capability portfolio with all dispositions and 14 conditions — the roadmap builds these, re-opens none.
- **O1–O9 / W1–W6** (`11-commercial-product-strategy/outputs/sequencing-economics.md`): register-enforced orderings and calendar windows — the roadmap sequences *within* them; any departure breaking one needs a recorded human decision.
- **Gate ratchet** (DEC-10-02): gates/evidence may tighten freely; weakening anything requires a recorded human decision. Per-item "done" = launch-gate register row green.
- **Measurement prohibitions** (D-04-01): no roadmap success language may use usage volume, detection volume, or collapse dry-run/validated.
- **RR-1 trigger (c) discipline** (DEC-10-16, DEC-11-04, DEC-12-01): the roadmap stays single-bureau (SaaS-ready posture) unless the human reviewer takes up the F-11-01 decision bundle — if any roadmap item exists *because of* SaaS ambition, the bundle goes on the critical path first.
- **DEC-11-05 logistics**: DQ-007 (+ MFA) resolves in this stage's decision pack; DQ-006/DQ-008 bundle into one professional engagement initiated at/immediately after approval; DEC-08-09 rides the C12 build item's `/arch-council` review.
- **DEC-12-04**: the source-document disposition is a recommendation to this stage — application (rewriting the HTML) is a Phase 3 act after approval.

## Confirmed facts to consume (do not re-verify)

- **`12-target-direction/outputs/stage-13-handoff.md`** — the direction as roadmap input (primary input): direction statement + posture constraints P-A–P-H + end-state map + KPIs K1–K6 + the consolidated decision-pack table (§3) + near-term items (§4).
- **`11-commercial-product-strategy/outputs/stage-13-handoff.md`** + `sequencing-economics.md` + `pre-build-decision-logistics.md` — the full constraint set, cost placements, value-priority signal (**C1 → C2(+exception substrate) → C12 & C14 → C6/C3/C5 → C7 shadow → C11 → C13**), and decision logistics.
- **`10-evaluation-assurance/outputs/launch-gate-evidence-register.md`** — per-capability closure evidence (the roadmap's definition-of-done source); `residual-risk-register.md` (RR-1 visibility item).
- **Stage 05 `capability-readiness-matrix.md` + Stage 08 designs** (`remediation-designs.md`, the C1/C2 foundation designs, tool contracts) — what each build item actually contains.
- **Stage 09 handoffs** — surface scope facts (platform-level area with C12; three-chrome additions; three-surface C13 regression obligation; FULL_RUN dead-option removal as standing-workflow maintenance).
- **`decision-queue.md`** — DQ-006/007/008 forwarded items, EG-001–005 evidence gaps, visibility items (DEC-07-04/RR-1, DEC-08-09).

## Questions this stage must answer

1. **Roadmap structure**: the sequenced tranches/build items toward the end-state map — each item named, scoped (which designs/mechanisms/surfaces it lands), placed within O1–O9/W1–W6, with its one-off costs attached per the cost-placement table (frontend harness with C1; LLM eval infra with C3; CI schedule seam with first Class B control; platform-level frontend area scoped as its own story within C12; exception substrate with C2).
2. **Definition of done per item**: the launch-gate register rows and evidence artifacts each item closes ("done = row green"), including baseline captures (B-series) threaded at their windows.
3. **The decision pack**: DQ-007 (+ MFA hard gate) as a genuine options pack with consequences (incl. multi-operator promotion if proposer ≠ approver); DQ-006/DQ-008 engagement line item; RR-1 and DEC-08-09 visibility items; the source-document disposition for approval/amendment; EG-004 (next-onboarding timing) and EG-005 (demand evidence) as explicit asks. Options presented, nothing resolved by the executor.
4. **Near-term/baseline plan**: B3/B5 retrospective capture now; EG-004 ask; B6/B4 tallies pinned to sprint-planning triggers; FULL_RUN removal flagged to the standing maintenance workflow; optional browser-e2e line — placed explicitly so none is lost.
5. **Phase boundary statement**: precisely what Stage 13 approval does and does not authorise (it approves the roadmap and direction; Phase 2/3 authorisation and every pre-build human gate remain separate, per POLICY).
6. **The approval pack presentation**: one consolidated, readable pack for the human reviewer (the programme's stage-status report convention applies — wrap the status report in a code block per the standing feedback rule).

## Required outputs

Create under `outputs/`: `proposed-roadmap.md` (Q1+Q2), `final-decision-pack.md` (Q3+Q5), `baseline-and-near-term-plan.md` (Q4), `stage-13-approval-prompt.md` (Q6 — the artifact the human responds to, following the Stage 02/03/04 review-decision-prompt pattern). Update: `findings.md` (F-13-*, if any), `decisions.md`, `review-state.md`, `decision-queue.md`, `_inputs/source-register.md` as required. (`outputs/critic-review.md` is the critic's.) Human approval, when given, is recorded in `_core/HUMAN-DECISIONS.md` (HD entry) and closes the stage and Phase 1.

## Finding discipline

Per `_core/FINDING-SCHEMA.md`. Like Stage 12, findings are expected to be rare — only where roadmap assembly exposes a genuine inconsistency between confirmed prior facts. No invented business facts; no invented capacity/velocity assumptions (build capacity is Michael's to state — if the roadmap needs one, it is an explicit ask in the pack, not an assumption).

## Explicitly out of scope

- Authorising or starting any build (Phase 2/3 authorisation is a separate human gate after approval)
- Resolving DQ-006/007/008, the SaaS fork, or any human decision — options and consequences only
- Editing `docs/architecture/agent-layer-architecture.html`, `docs/ROADMAP.md`, `docs/product/`, or any path outside this programme (adoption into repo/product roadmaps is Phase 2/3 work under its own grant)
- Re-opening portfolio dispositions, gates, designs, boundaries, or Stage 12's direction
- Inventing dates, velocities, or capacity — tranche ordering and windows only, unless Michael supplies scheduling facts

## Constraints

- Writes stay inside `docs/programmes/agentic-architecture-review/`.
- Every roadmap item traces to a design/remediation/register source; every constraint placement cites its O/W row.
- Classify every real choice per `CRITIC.md`'s taxonomy; the executor decides none of them.
- The stage ends at `awaiting-human-decision` after critic PASS — closing it is the human reviewer's act alone.

## Completion criteria

Ready for the critic only when: every Q1–Q6 has an answer; every O/W constraint is either honoured or its departure explicitly flagged as a decision; every decision-pack item from the two stage-13 handoffs appears exactly once; the approval prompt is self-contained (readable without opening other files); state files consistent.

## Completion procedure

1. Mark Stage 13 `awaiting-critic` in `review-state.md` and this file.
2. Independent critic per `CRITIC.md` → `outputs/critic-review.md`.
3. On `PASS`: mark `awaiting-human-decision` and **stop — present the approval pack to the human reviewer**. Never close automatically.

## Next action

**Run the Stage 13 primary-executor pass per `RUNBOOK.md`.** Recommend a fresh session (D-004).
