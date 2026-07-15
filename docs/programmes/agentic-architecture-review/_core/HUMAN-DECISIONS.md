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

## Next action

**Stage 04 is complete. Await approval to begin Stage 05 — Platform Readiness.**
