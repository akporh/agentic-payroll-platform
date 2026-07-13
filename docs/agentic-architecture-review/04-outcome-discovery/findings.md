# Stage 04: Outcome Discovery — Findings

Schema per `CONTEXT.md`'s finding discipline: finding ID / user or business problem / current evidence / desired outcome / approved capability(ies) involved / best intervention type / observed gap or overlap / consequence / metric or evidence of success / risk or harmful incentive / confidence / recommendation / required human decision / downstream dependency. Confirmed, draft, and parked findings are kept separate.

---

## Draft Findings

_None — every observation below reached a confirmed disposition, an explicitly logged human decision, or an explicit baseline-data-gap label (not a guessed number)._

---

## Confirmed Findings

### F-04-01: Exception resolution has no defined workflow anywhere in the approved portfolio — the single highest-leverage missing outcome
- **User/business problem**: an operator has no defined path from "an issue was flagged" (by C6, C7, or eventually C8) to "the issue is resolved and closed"
- **Current evidence**: Stage 03 F-03-14 (`portfolio-boundary-map.md` §8) already identified this gap for C7 specifically and for C11→C12's handoff; this stage confirms it generalizes across every current and prospective exception producer
- **Desired outcome**: every flagged exception has an owner, evidence, a recommended next action, a resolution record, and a closure state — see `outputs/exception-resolution-outcome.md`
- **Approved capability(ies)**: consumes output from C6, C7, and (once unblocked) C8; requires C2 as a platform prerequisite
- **Best intervention type**: product/workflow design (deterministic record-keeping + UI), with a narrow, bounded role for AI in recommending a next action from already-known facts
- **Observed gap/overlap**: a structural gap — three separate capabilities each produce exceptions with no shared destination
- **Consequence**: without this, the value of C6 and C7 (and future C8) is capped regardless of how good their detection is — a flagged issue nobody acts on has zero realized value
- **Metric/evidence of success**: exception time-to-resolution; rate of exceptions closed without a documented resolution (should be zero)
- **Risk/harmful incentive**: a queue could be "emptied" by dismissal rather than genuine resolution — the metric must track resolution quality, not just queue-clearing
- **Confidence**: High
- **Recommendation**: pursue now, designed once and shared across all exception producers, not rebuilt per-capability
- **Required human decision**: none — this is a design-priority recommendation, not an evidence-adjudication decision
- **Downstream dependency**: Stage 05 (C2 prerequisite), Stage 09 (UX design), Stage 11 (sequencing priority)

### F-04-02: Input anomaly detection's calibration approach is a genuine, unresolved human decision — not resolvable from evidence
- **User/business problem**: what counts as an "anomalous" payroll input quantity is a product/statistical judgment call, not derivable from the codebase
- **Current evidence**: Stage 01 F-01-17 confirms input history exists; no anomaly mechanism or historical-anomaly dataset exists to calibrate against
- **Desired outcome**: a calibration approach chosen deliberately, not defaulted to by omission — see `outputs/anomaly-detection-outcome-policy.md` for the three candidate approaches (absolute threshold, period-on-period variance, peer-pattern comparison)
- **Approved capability(ies)**: C7
- **Best intervention type**: deterministic/statistical detection; LLM narration optional, never the detector (Principle 9, applied per Stage 03 F-03-04)
- **Observed gap/overlap**: none — this is an explicit open question, not a contradiction
- **Consequence**: choosing a calibration approach without product/statistical input risks either missing real errors (too loose) or alert fatigue (too tight)
- **Metric/evidence of success**: precision/recall against a labelled anomaly test set (does not yet exist — baseline gap)
- **Risk/harmful incentive**: false-positive fatigue leading to reflexive dismissal — track dismiss-without-review rate as an early warning
- **Confidence**: High that this is genuinely undecidable from evidence; not an evasion of a decision this stage could make
- **Recommendation**: record as a required human decision (below), not resolved here
- **Required human decision**: which calibration approach (or combination) to pursue for C7 — logged in `decisions.md`
- **Downstream dependency**: Stage 08 (mechanism design once the approach is chosen)

### F-04-03: C13/C14's onboarding outcomes have no quantified baseline anywhere in the current product
- **User/business problem**: claims of "reduced onboarding friction" would have no real comparison point without a baseline
- **Current evidence**: `outputs/onboarding-outcome-baseline.md` — four specific unquantified metrics (mapping time, mapping error rate, parallel-run agreement rate, time-to-go-live)
- **Desired outcome**: baseline measurement instrumented before C13/C14 ship, so improvement claims are demonstrable, not assumed
- **Approved capability(ies)**: C13, C14
- **Best intervention type**: measurement instrumentation (deterministic), independent of any AI capability
- **Observed gap/overlap**: none — a genuine data-collection gap
- **Consequence**: without a baseline, any future claim that C13 "reduced mapping time" is unverifiable
- **Metric/evidence of success**: the four baseline metrics named in `onboarding-outcome-baseline.md`, once instrumented
- **Risk/harmful incentive**: none directly, but shipping without a baseline risks over-claiming value later
- **Confidence**: High
- **Recommendation**: instrument baseline measurement (especially persisting `ReconSlideOver`'s existing comparison output, which is currently client-side-only and discarded, Stage 01 F-01-41) before or alongside C13/C14 development, not after
- **Required human decision**: none — a recommendation for prioritisation, not an evidence adjudication
- **Downstream dependency**: Stage 05 (platform readiness for instrumentation), Stage 11 (prioritisation)

### F-04-04: The compliance outcome chain (C11→C12) has one genuinely open design question this stage does not resolve
- **User/business problem**: "assess affected clients/runs" (step 4 of the compliance outcome chain) could plausibly belong to either C11 (pre-approval impact visibility) or C12 (post-approval application scoping)
- **Current evidence**: Stage 02 F-02-12, Stage 03 F-03-09 established the C11/C12 split; neither resolved this specific sub-step's ownership
- **Desired outcome**: the impact assessment happens somewhere in the chain before application — which capability owns it is undetermined
- **Approved capability(ies)**: C11, C12 (boundary between them)
- **Best intervention type**: N/A — this is a design-ownership question, not an intervention-type question
- **Observed gap/overlap**: a genuine, unresolved boundary ambiguity between two already-separated capabilities
- **Consequence**: if left undecided when C11/C12 are actually designed, the impact-assessment step could be silently dropped by both capabilities each assuming the other covers it
- **Metric/evidence of success**: N/A until resolved
- **Risk/harmful incentive**: a compliance change applied without anyone having assessed its blast radius — a genuine compliance risk if this ambiguity isn't closed before C11/C12 ship
- **Confidence**: High that the ambiguity exists; this stage takes no position on the resolution
- **Recommendation**: forward to Stage 06/08 as an explicit open design question, not adjudicated here
- **Required human decision**: none required at this stage — a design question for Stage 06/08, not a Stage 04 evidence-adjudication matter
- **Downstream dependency**: Stage 06 (compliance ownership), Stage 08 (mechanism design)

### F-04-05: Two lifecycle areas (structural configuration duplication, contract shift-type divergence) have deterministic fixes with no outcome-discovery work needed
- **User/business problem**: (1) two parallel structural-configuration entry points risk operator confusion (Stage 01 F-01-05); (2) `shift_type` NULL is handled inconsistently across two code paths (Stage 01 F-01-16)
- **Current evidence**: Stage 01 F-01-05, F-01-16
- **Desired outcome**: consistent behavior; for (2), a straightforward deterministic fix; for (1), further product research needed before committing to a specific fix
- **Approved capability(ies)**: none — neither is covered by any of the 15 approved capabilities
- **Best intervention type**: deterministic/product fix for both; no AI involvement in either
- **Observed gap/overlap**: both are portfolio gaps in the sense that no capability addresses them, but they are not AI-shaped problems at all
- **Consequence**: if untracked, both risk being lost between this AI-focused review and the ordinary product backlog
- **Metric/evidence of success**: (2) elimination of shift-type-divergence-caused calculation surprises; (1) not yet definable pending research
- **Risk/harmful incentive**: none — these are conventional product/engineering items
- **Confidence**: High
- **Recommendation**: (2) pursue now as a normal bug-fix item; (1) research further to confirm operators actually experience this as friction before committing engineering time
- **Required human decision**: none
- **Downstream dependency**: none within this review — ordinary product backlog items, noted here so they aren't lost

### F-04-06: Operational reporting and continuous improvement (lifecycle area 15) is entirely unaddressed by the approved portfolio
- **User/business problem**: bureau management has no visibility into recurring errors, deadline risk, control-completion status, or client profitability/operational cost
- **Current evidence**: confirmed absent from all 15 capabilities in `03-agent-portfolio/outputs/agent-capability-matrix.md`; no capability touches this area at all
- **Desired outcome**: reporting/analytics capability, once the underlying data foundation (audit coverage) supports it
- **Approved capability(ies)**: none — a genuine portfolio gap
- **Best intervention type**: primarily deterministic aggregation/analytics; AI potentially useful for narrative summarization on top, not for the underlying computation
- **Observed gap/overlap**: the clearest missing-outcome area identified in this stage
- **Consequence**: this is where several of the newly-proposed outcomes in `CONTEXT.md` §3 (recurring-error reporting, deadline-risk visibility, control-completion evidence, client profitability insight) all converge — they share a common prerequisite
- **Metric/evidence of success**: not yet definable — needs its own prioritisation pass before a metric is meaningful
- **Risk/harmful incentive**: none yet, since nothing is built; the risk to name is pursuing this before its prerequisite (audit-coverage fix, F-01-40) closes
- **Confidence**: High that the gap exists; the right response to it is explicitly deferred, not decided here
- **Recommendation**: defer until the audit-coverage gap (Stage 01 F-01-40) closes; treat as a distinct future initiative, not folded into the current 15-capability portfolio
- **Required human decision**: none at this stage
- **Downstream dependency**: Stage 05 (audit-coverage fix), Stage 11 (commercial framing of this whole area)

### F-04-07: The existing "Reconcile with old system" tool already solves part of the parallel-run-confidence outcome but discards its output
- **User/business problem**: onboarding needs a persisted, trackable parallel-run agreement rate; the closest existing mechanism (`ReconSlideOver`, Stage 01 F-01-41/44) produces exactly this comparison but never saves it
- **Current evidence**: Stage 01 F-01-41, F-01-44 (client-side-only comparison tool, XLSX export, no persistence)
- **Desired outcome**: the same comparison, persisted, so agreement rate becomes a trackable metric across an onboarding period rather than a one-time, throwaway view
- **Approved capability(ies)**: C13/C14 (adjacent — this is a lower-effort, higher-immediacy step than building the full AI mapping assistant)
- **Best intervention type**: deterministic (persist an existing computation) — no AI needed for this specific improvement
- **Observed gap/overlap**: a capability that already produces the needed data throwing it away — a low-cost, high-value fix hiding in plain sight
- **Consequence**: this could close part of the F-04-03 baseline gap (parallel-run agreement rate specifically) independent of and before C13/C14's larger build
- **Metric/evidence of success**: parallel-run agreement rate becomes measurable, retroactively from the point this fix ships
- **Risk/harmful incentive**: none
- **Confidence**: High
- **Recommendation**: persist `ReconSlideOver`'s comparison output as a standalone, low-complexity fix, independent of and prior to the larger C13/C14 build
- **Required human decision**: none — a prioritisation recommendation
- **Downstream dependency**: Stage 05 (platform readiness for the persistence mechanism), Stage 11 (sequencing)

### F-04-08: C4 and C8's future outcomes are well-defined but must not be scored or planned against as though they were current
- **User/business problem**: N/A — deliberately not reopened per `CONTEXT.md`'s explicit instruction
- **Current evidence**: Stage 02 D-02-03, D-02-02 (`_core/HUMAN-DECISIONS.md` HD-3, HD-4); Stage 03 blocked-and-deferred register
- **Desired outcome**: historical explanation (C4) and reconciliation investigation (C8), once Stage 05 confirms their preconditions have closed
- **Approved capability(ies)**: C4, C8
- **Best intervention type**: N/A — already decided (deterministic diff + AI narration once unblocked, per Stage 03 F-03-05)
- **Observed gap/overlap**: none — this finding exists to confirm the blockers were not re-litigated, per the explicit constraint
- **Consequence**: none — this is a compliance-with-constraint confirmation, not a new finding
- **Metric/evidence of success**: defined in `product-opportunity-map.md` area 9 and `measurement-framework.md`, deferred until unblocked
- **Risk/harmful incentive**: the single worst outcome in the entire map would be shipping either before both preconditions close — already named as the top risk in area 9
- **Confidence**: High
- **Recommendation**: no change — defer per existing decisions
- **Required human decision**: none — already resolved
- **Downstream dependency**: Stage 05 (the only stage that can change this)

---

## Parked / Rejected

_None — every lead investigated in this stage reached a confirmed finding, an explicit baseline-data-gap label, or an explicitly logged human decision._

## Human decisions required (raised by this stage)

Per the same finding-discipline principle Stage 03 applied ("do not create artificial human decisions where evidence and inherited principles already resolve the issue"), this stage identified exactly **one** genuine open decision requiring human adjudication:

- **HD-04-1** (F-04-02): which calibration approach — absolute threshold, period-on-period variance, peer-pattern comparison, or some combination — should C7's anomaly detection use? This cannot be resolved from repository evidence; it requires product/statistical judgment about the client base's actual data patterns. Logged in `decisions.md`.

Everything else in this stage (the C11/C12 boundary question, the structural-configuration research item, etc.) is recorded as a forwarded design/research question for a later stage, not a decision this reviewer needs to make now.

## Cross-references for later stages

- Stage 05 (Platform Readiness): F-04-01 (C2 prerequisite for exception workflow), F-04-03/F-04-07 (onboarding baseline instrumentation), F-04-06 (audit-coverage prerequisite for reporting), F-04-08 (C4/C8 unblock conditions, unchanged).
- Stage 06 (Compliance & Controls): F-04-04 (C11/C12 impact-assessment ownership).
- Stage 08 (Technical Architecture): F-04-02 (anomaly mechanism, once calibration is decided), F-04-04 (mechanism design once ownership is resolved).
- Stage 09 (Human Experience): F-04-01 (exception-resolution UX design).
- Stage 11 (Commercial & Product Strategy): F-04-03, F-04-06, F-04-07 (sequencing/prioritisation).
