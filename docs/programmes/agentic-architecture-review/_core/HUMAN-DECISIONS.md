# Human Decisions

Log of every point in the review where a human judgment call, scope decision, severity call, gate approval, or contested-evidence adjudication was required. This is the master log; each stage's `decisions.md` holds the stage-local copy of decisions made during that stage, and should link back here.

Nothing in this file is inferred by the AI agent on the human reviewer's behalf — every entry corresponds to an actual statement or approval from the human reviewer (Michael Emedo, or a designated delegate).

## Log format

```markdown
### HD-<n>: <short title>
- **Date**: YYYY-MM-DD
- **Stage**: <stage number/name, or "cross-cutting">
- **Decision**: <what was decided>
- **Made by**: <who>
- **Context**: <why this required a human call rather than being derivable from evidence>
- **Affects**: <finding IDs, stage gates, or roadmap items this decision touches>
```

## Gate approvals

Stage gate approvals (permission to move a stage from `in-progress` to `gated-closed`, and to begin the next stage) are logged here as `HD-GATE-<stage#>` entries, in addition to being reflected in `review-state.md`.

## Decisions log

### HD-GATE-01: Stage 01 (Current Operating Model) gate approved
- **Date**: 2026-07-12
- **Stage**: 01 — Current Operating Model
- **Decision**: Approved closing Stage 01's gate. 46 confirmed findings (0 draft, 0 parked) are now citable by Stage 02 onward.
- **Made by**: Michael Emedo, via direct response to an explicit gate-approval question
- **Context**: `WORKFLOW.md` requires explicit human approval before a stage gate closes; this was obtained directly rather than inferred from the user directing work toward Stage 02.
- **Affects**: Stage 01 status (`review-state.md`), Stage 02 eligibility to begin

### HD-2: Architecture document remains unapproved pending this review
- **Date**: 2026-07-12
- **Stage**: cross-cutting (raised Stage 02, binds Stage 12/13)
- **Decision**: `docs/architecture/agent-layer-architecture.html`'s `NEEDS REVISION` status remains open. This review is the formal revision path; the document is not approved until Stage 12 synthesises the target direction and Stage 13 records approval.
- **Made by**: Michael Emedo, via `docs/programmes/agentic-architecture-review/02-product-thesis/stage-02-review-decision-prompt.md` (D-02-01)
- **Context**: Only the human reviewer can determine whether "NEEDS REVISION" reflects a still-open objection or stale labelling; this could not be derived from evidence alone.
- **Affects**: F-02-02; Stage 12 (must treat the document as revisable input, not settled design); Stage 13 (sole stage authorized to record approval)

### HD-3: Reconciliation workspace scoping — repository fix mandatory, tool-layer check is defence-in-depth only
- **Date**: 2026-07-12
- **Stage**: cross-cutting (raised Stage 02, binds Stage 03/05/07)
- **Decision**: `payroll_reconciliation` repository-level workspace scoping (F-01-33) must be corrected before `get_reconciliation` is exposed as an agent tool. Tool-layer workspace-ownership validation is additionally mandatory as defence in depth, but is explicitly not an acceptable permanent substitute for the repository-level fix.
- **Made by**: Michael Emedo, via `stage-02-review-decision-prompt.md` (D-02-02)
- **Context**: A sequencing/risk-acceptance tradeoff between a platform-level data fix and a compensating control — a product/engineering priority call, not derivable from evidence alone.
- **Affects**: F-02-06; Stage 03 (`get_reconciliation` tool blocked until this is fixed); Stage 05 (repo-level fix is now a named precondition); Stage 07 (defence-in-depth requirement)

### HD-4: Historical reproducibility is a launch precondition, not a disclosed residual risk
- **Date**: 2026-07-12
- **Stage**: cross-cutting (raised Stage 02, binds Stage 03/05/08)
- **Decision**: Historical reproducibility (F-01-27, F-01-29, F-01-38) is a launch precondition for any capability that explains, traces, or investigates historical payroll outcomes. Track W may proceed selectively for current-state navigation/assistance not dependent on historical truth. Historical explanation and all of Track X's reconciliation/trace investigation remain blocked until these gaps are resolved. This is explicitly not to be treated as a general accepted residual risk disclosed to operators.
- **Made by**: Michael Emedo, via `stage-02-review-decision-prompt.md` (D-02-03)
- **Context**: A risk-acceptance decision balancing delivery speed against the risk of an agent generating a plausible-but-wrong historical explanation — not derivable from evidence alone.
- **Affects**: F-02-09, F-02-05, F-02-11; Stage 03 (splits Track W scope; blocks Track X investigation agents); Stage 05 (F-01-27/29/38 closure now a named launch precondition); Stage 08

### HD-5: Statutory-rule change management scoped independently of Y1; Y1 may never author/deploy migrations
- **Date**: 2026-07-12
- **Stage**: cross-cutting (raised Stage 02, binds Stage 03/05/06/08)
- **Decision**: Statutory-rule change management is scoped as a separate deterministic platform and compliance capability, independent of Y1 (Compliance Monitoring). Y1 may later detect external regulatory changes, compare evidence, and prepare proposals — it must never directly author, execute, or deploy production Alembic migrations.
- **Made by**: Michael Emedo, via `stage-02-review-decision-prompt.md` (D-02-04)
- **Context**: A roadmap-prioritization/build-vs-defer decision with compliance risk-appetite implications — not derivable from evidence alone.
- **Affects**: F-02-12; Stage 05 (new deterministic capability to scope); Stage 06 (compliance-owned change-management workflow); Stage 08 (mechanism design); Stage 03/11 (Track Y sequencing)

### HD-GATE-02: Stage 02 (Product Thesis) gate approved
- **Date**: 2026-07-12
- **Stage**: 02 — Product Thesis
- **Decision**: Approved closing Stage 02's gate following resolution of HD-2 through HD-5. 14 confirmed findings (0 draft, 0 parked) are now citable by Stage 03 onward.
- **Made by**: Michael Emedo, via `stage-02-review-decision-prompt.md`
- **Context**: `WORKFLOW.md` requires explicit human approval before a stage gate closes.
- **Affects**: Stage 02 status (`review-state.md`), Stage 03 eligibility to begin

### HD-6: Revised 15-capability portfolio approved as the reference portfolio
- **Date**: 2026-07-12
- **Stage**: cross-cutting (raised Stage 03, binds Stage 04/05/06/07/08/09/11/12)
- **Decision**: The revised 15-capability portfolio (`03-agent-portfolio/outputs/agent-capability-matrix.md`) is approved as the reference portfolio, replacing the source architecture document's original five-track/named-agent structure for the purposes of this review. The document remains a preserved source input (still "NEEDS REVISION" per HD-2/D-02-01), but its original grouping is no longer the target. All 14 approved conditions from `stage-03-review-decision-prompt.md` (preserving every Stage 02 blocker/precondition, plus capability-specific constraints on C3, C5–C7, C10–C14, and the tool-scoping requirement) are binding and unchanged from Stage 03's own findings.
- **Made by**: Michael Emedo, via `03-agent-portfolio/stage-03-review-decision-prompt.md` (D-03-01)
- **Context**: Approving a consolidated capability portfolio that replaces a previously-circulated architecture document's structure is a product-direction call requiring explicit human sign-off, not something a review stage can self-approve.
- **Affects**: F-03-01 through F-03-16; all 9 Stage 03 outputs; Stages 04, 05, 06, 07, 08, 09, 11, 12 (all now consume the approved portfolio)

### HD-GATE-03: Stage 03 (Agent Portfolio) gate approved
- **Date**: 2026-07-12
- **Stage**: 03 — Agent Portfolio
- **Decision**: Approved closing Stage 03's gate following HD-6/D-03-01. 16 confirmed findings (0 draft, 1 parked note) are now citable by Stage 04 onward.
- **Made by**: Michael Emedo, via `stage-03-review-decision-prompt.md`
- **Context**: `WORKFLOW.md` requires explicit human approval before a stage gate closes.
- **Affects**: Stage 03 status (`review-state.md`), Stage 04 eligibility to begin

### HD-7: C7 anomaly-detection calibration approach — layered, staged combination approved
- **Date**: 2026-07-13
- **Stage**: cross-cutting (raised Stage 04, binds Stage 08)
- **Decision**: A layered combination for C7 (Input Anomaly Detection): (1) launch baseline of configurable, explainable absolute thresholds, never LLM-generated/adjusted; (2) period-on-period variance as a second, additive layer, gated on a minimum employee-history window, alerting with current value/baseline/variance shown; (3) peer-pattern comparison explicitly deferred, never cross-tenant if reconsidered later; (4) C7 must not ship without the exception-resolution workflow (`04-outcome-discovery/outputs/exception-resolution-outcome.md`); (5) shadow-mode rollout, versioned/auditable threshold changes, and LLM restricted to optional narration only. Final formulas, numeric thresholds, and the minimum-history-window value are explicitly deferred to Stage 08/product calibration, not invented at this stage.
- **Made by**: Michael Emedo, via `04-outcome-discovery/stage-04-review-decision-prompt.md` (D-04-01)
- **Context**: The specific calibration approach depends on the client base's real data patterns and an acceptable false-positive/false-negative tradeoff — not derivable from repository evidence, which is why Stage 04 raised it rather than resolving it.
- **Affects**: F-04-02; `04-outcome-discovery/outputs/anomaly-detection-outcome-policy.md`, `outcome-prioritisation.md`, `measurement-framework.md`; Stage 08 (mechanism design within this decided approach)

### HD-GATE-04: Stage 04 (Outcome Discovery) gate approved
- **Date**: 2026-07-13
- **Stage**: 04 — Outcome Discovery
- **Decision**: Approved closing Stage 04's gate following HD-7/D-04-01. 8 confirmed findings (0 draft, 0 parked) are now citable by Stage 05 onward.
- **Made by**: Michael Emedo, via `stage-04-review-decision-prompt.md`
- **Context**: `WORKFLOW.md` requires explicit human approval before a stage gate closes.
- **Affects**: Stage 04 status (`review-state.md`), Stage 05 eligibility to begin

### HD-8: DP-1 — Statutory approval controls (DQ-007 + MFA) resolved as A1 + B2
- **Date**: 2026-07-19
- **Stage**: 13 — Approved Roadmap (decision-pack item DP-1; resolves DQ-007 + the Stage 07 MFA amendment)
- **Decision**: **Approved as Part A: A1 + Part B: B2.** The same authorised operator may propose AND approve a statutory rule change for v1 (Part A = A1 — waive proposer ≠ approver, with the compensating controls named in the C12 build story). Password re-authentication is required at approval. MFA is deferred and is **not** a v1 launch gate (Part B = B2 — password-only step-up is the floor, DEC-07-03). The design must remain compatible with introducing MFA later. **This is recorded as A1 + B2 — explicitly not A2.**
- **Made by**: Michael Emedo, 2026-07-19
- **Context**: A risk-appetite call on segregation of duties and step-up strength for the C12 statutory-approval action — not derivable from evidence; the executor recommended nothing.
- **Affects**: DQ-007 (resolved); C12 build scope stays single-operator (A2's multi-operator-prerequisite consequence does NOT apply); RR-2 step-up floor; Tranche 2 (C12) DoD (`13-approved-roadmap/outputs/proposed-roadmap.md` Item 2.1; `final-decision-pack.md` DP-1).

### HD-9: DP-2 — Source-document disposition remains PENDING human review
- **Date**: 2026-07-19
- **Stage**: 13 — Approved Roadmap (decision-pack item DP-2; bears on D-02-01/HD-2)
- **Decision**: **Pending human review — remains open.** `docs/architecture/agent-layer-architecture.html` and its frontend mirror are **not** superseded or retired. The disposition decision remains open until the consolidated Architecture Baseline Pack has been produced and reviewed. HD-2's "NEEDS REVISION / unapproved" status stands unchanged meanwhile.
- **Made by**: Michael Emedo, 2026-07-19
- **Context**: The reviewer chose to defer the supersede-and-replace decision until the baseline pack is available for review — a genuine sequencing choice that keeps the source document live.
- **Affects**: D-02-01/HD-2 (still open); DEC-12-04 recommendation (still a recommendation, not adopted); Stage 13 stays OPEN in part because of this.

### HD-10: DP-3 — Product direction: single-bureau, SaaS-ready — APPROVED
- **Date**: 2026-07-19
- **Stage**: 13 — Approved Roadmap (decision-pack item DP-3; resolves the F-11-01 fork's default)
- **Decision**: **Approved: single-bureau, SaaS-ready.** Optimise the platform for Sandy's bureau operations; preserve a credible future path to multi-bureau SaaS; do **not** put full SaaS capabilities on the current critical path. Active SaaS expansion requires separate commercial evidence (EG-005 / DP-8) AND human authorisation.
- **Made by**: Michael Emedo, 2026-07-19
- **Context**: Adopts the direction's executor-safe default (`target-direction-statement.md` §5) as a positive human decision; the active-SaaS alternative bundle (F-11-01) is not taken up.
- **Affects**: DP-5 stays a visibility item (RR-1 not re-opened); the roadmap as proposed carries; RR-1 trigger (c) remains armed for any future SaaS move.

### HD-11: DP-4 — Professional advice engagement (DQ-006 + DQ-008) — APPROVED
- **Date**: 2026-07-19
- **Stage**: 13 — Approved Roadmap (decision-pack item DP-4)
- **Decision**: **Approved.** Initiate, at the appropriate point, a Nigerian payroll / tax / legal / regulatory advisory engagement to validate: (1) authoritative statutory-monitoring sources and required monitoring cadence (DQ-006); (2) statutory and data-protection retention obligations (DQ-008). This is **preparatory work only and authorises no implementation.**
- **Made by**: Michael Emedo, 2026-07-19
- **Context**: A non-build lead-time action; external-adviser runway is the risk. The professional conclusions themselves remain the adviser's + reviewer's, gating C11 build (DQ-006) and retention-enforcement tooling (DQ-008) later.
- **Affects**: DQ-006 (engagement approved to initiate; still gates C11 build authorisation); DQ-008 (same engagement; still gates retention enforcement); Tranche 0 T0.3.

### HD-12: DP-5 — Audit-tamper residual risk (RR-1) — NOTED (accepted)
- **Date**: 2026-07-19
- **Stage**: 13 — Approved Roadmap (decision-pack item DP-5; the DEC-07-04/DEC-10-16 visibility touchpoint)
- **Decision**: **Noted — accepted.** Accept the documented residual audit-tamper risk (RR-1) for the current single-bureau managed-PostgreSQL deployment. Revisit only on an existing review trigger: a material deployment change, SaaS expansion, regulatory demand, or suspected tampering.
- **Made by**: Michael Emedo, 2026-07-19
- **Context**: The reviewer's explicit acceptance at the scheduled Stage 13 visibility touchpoint (RR-1 trigger (e)); bounded to the current deployment shape, consistent with DEC-10-16.
- **Affects**: RR-1 (`10-evaluation-assurance/outputs/residual-risk-register.md`); re-opens as a human decision only on a trigger (notably DP-3 SaaS).

### HD-13: DP-6 — Statutory-rule uniqueness change (DEC-08-09) — NOTED
- **Date**: 2026-07-19
- **Stage**: 13 — Approved Roadmap (decision-pack item DP-6; visibility)
- **Decision**: **Noted.** The proposed widening of the `statutory_rule` uniqueness constraint — `(country_code, effective_from)` → `(country_code, effective_from, version)` — will be handled via the normal arch-council + implementation governance when C12 is authorised. **No implementation is authorised now.**
- **Made by**: Michael Emedo, 2026-07-19
- **Context**: A pre-build awareness item so the data-contract change is not a surprise at build time; it rides the repo's standing `/arch-council` gate inside the C12 build item.
- **Affects**: DEC-08-09; Tranche 2 (C12) `/arch-council` budget.

### HD-14: DP-7 — Onboarding measurement evidence (EG-004) — RESOLVED with an amended evidence approach
- **Date**: 2026-07-19
- **Stage**: 13 — Approved Roadmap (decision-pack item DP-7; amends EG-004 and the prior B1/B2 "unrecoverable live window" framing)
- **Decision**: **Resolved with an amended evidence approach.** The timing of the next live onboarding is unknown, and a future live onboarding is **not** the only acceptable evidence. Create a **controlled onboarding benchmark** using representative historical client information or appropriately synthetic data based on previous onboarding cases; measure the existing/manual process and the platform-supported process consistently (time, effort, interventions, errors, completeness, and other relevant measures); collect live-onboarding evidence opportunistically when available; ensure test/replay data is isolated, governed, and safely removed or retained per the agreed evidence protocol. **Simulated onboarding must be labelled clearly as controlled benchmark evidence — never presented as proof of live operational performance.**
- **Made by**: Michael Emedo, 2026-07-19
- **Context**: The prior framing treated a real live onboarding before C13 as the sole B1/B2 source (an "unrecoverable window", EG-004/EG-001/EG-002). This decision replaces that with a controlled-benchmark path that removes the hard dependency on onboarding timing while preserving evidence integrity.
- **Affects**: EG-004, EG-001, EG-002; B1/B2 baseline capture protocol; K2 KPI (comparison claims may now rest on labelled controlled-benchmark evidence); `13-approved-roadmap/outputs/baseline-and-near-term-plan.md` (DP-7 amendment note added); the roadmap's W2 window framing (not rewritten — DP-9 pending).

### HD-15: DP-8 — Commercial-demand evidence (EG-005) — APPROVED
- **Date**: 2026-07-19
- **Stage**: 13 — Approved Roadmap (decision-pack item DP-8)
- **Decision**: **Approved.** Distinguish validated platform capability from validated market demand. External claims may describe capabilities where evidence-supported. Do **not** describe demand, willingness-to-pay, adoption, or SaaS commercial viability as validated without customer/market evidence. SaaS expansion remains subject to that evidence and separate human approval.
- **Made by**: Michael Emedo, 2026-07-19
- **Context**: Confirms the claims-discipline boundary (F-11-02, EG-005); no demand evidence is registered, so direction language stays capability-led.
- **Affects**: EG-005; `11-commercial-product-strategy/outputs/positioning-and-claims.md` overclaim discipline; feeds DP-3 (any future SaaS step).

### HD-16: DP-9 — Roadmap approval remains PENDING final human confirmation
- **Date**: 2026-07-19
- **Stage**: 13 — Approved Roadmap (decision-pack item DP-9)
- **Decision**: **Pending final human confirmation — remains open.** The roadmap (`13-approved-roadmap/outputs/proposed-roadmap.md`) may be treated as the current **proposed** implementation sequence but is **not** finally approved. Final approval depends on human review of the Architecture Baseline Pack and confirmation that the target architecture is understood and accepted, the roadmap implements that accepted architecture, and roadmap sequencing/dependencies/definitions of done remain appropriate.
- **Made by**: Michael Emedo, 2026-07-19
- **Context**: The reviewer chose to gate final roadmap approval on review of the consolidated baseline pack — keeping Phase 1 open. This is the sole decision that closes Phase 1, and it is not yet made.
- **Affects**: DP-9; Phase 1 closure (deferred); Stage 13 stays OPEN (`awaiting-human-decision`).

## Next action

**Stage 13 remains OPEN (`awaiting-human-decision`).** Seven decision-pack items are recorded above as human decisions dated 2026-07-19: DP-1 (HD-8, A1+B2), DP-3 (HD-10), DP-4 (HD-11), DP-5 (HD-12), DP-6 (HD-13), DP-7 (HD-14), DP-8 (HD-15). **Two remain PENDING**: DP-2 (HD-9, source-document disposition) and DP-9 (HD-16, final roadmap approval) — both awaiting human review of the **Architecture Baseline Pack** (`13-approved-roadmap/outputs/architecture-baseline-pack.md`). Recording DP-2 and DP-9 (which resolves roadmap approval and closes Phase 1) is the next expected entry in this log. Phase 1 is **not** complete; no implementation, supersession, or programme closure is authorised.
