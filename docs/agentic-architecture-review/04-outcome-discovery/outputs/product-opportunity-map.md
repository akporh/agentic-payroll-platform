# Stage 04 Output: Product Opportunity Map

Maps the full payroll operating lifecycle (15 areas, per `CONTEXT.md` §Required investigation 1) to desired outcomes, grounded in Stage 01–03 evidence. Each area lists: primary user, current problem/friction, desired outcome, current evidence, best intervention type, contributing approved capability, platform prerequisite, control/compliance prerequisite, measurable outcome, and risk of false confidence/harmful incentives.

---

## 1. Workspace and client setup

- **Primary user**: bureau operator onboarding a new client workspace
- **Current problem/friction**: workspace creation is a simple deterministic form (name/country/currency); no friction beyond what Stage 01 already confirmed works (F-01-01/02)
- **Desired outcome**: fast, correct workspace creation with no invalid states reachable
- **Current evidence**: Stage 01 F-01-01 (unused `account_id`), F-01-02 (LIVE-gate trigger) — both already sound or low-severity
- **Best intervention type**: no new capability — existing deterministic flow is adequate
- **Contributing capability**: none of C1–C15 directly; C1 (auth foundation) is a prerequisite for *who* can create a workspace, not the creation flow itself
- **Platform prerequisite**: none beyond C1 (auth) landing
- **Control/compliance prerequisite**: none
- **Measurable outcome**: N/A — no outcome gap identified here
- **Risk of false confidence/harmful incentives**: none identified

## 2. Structural configuration (pay cycles, grades, designations, salary definitions, rules, components)

- **Primary user**: bureau operator configuring a client's payroll structure during onboarding
- **Current problem/friction**: two parallel entry points (bulk onboarding commit vs. individual per-entity routes, Stage 01 F-01-05) create a duplication risk; component metadata's dual `is_active`/`active` flags (F-01-06) are a latent confusion source
- **Desired outcome**: an operator can configure structure once, correctly, without needing to know which of two paths is authoritative
- **Current evidence**: Stage 01 F-01-04, F-01-05, F-01-06, F-01-09, F-01-12
- **Best intervention type**: product UX (consolidate or clearly differentiate the two entry points) — not an AI problem
- **Contributing capability**: none of C1–C15 — this is a UX/product-design gap, not a capability gap
- **Platform prerequisite**: none
- **Control/compliance prerequisite**: none
- **Measurable outcome**: reduction in structural-configuration errors traceable to using the "wrong" entry point (no baseline currently exists — see baseline gap note in `outputs/onboarding-outcome-baseline.md`)
- **Risk of false confidence/harmful incentives**: none from AI (none proposed here); the two-entry-point duplication itself is a risk Stage 09 should pick up, not Stage 04's to resolve

## 3. Employee registration and enrolment

- **Primary user**: bureau operator registering and enrolling employees, individually or in bulk
- **Current problem/friction**: bulk registration requires manual column mapping (`NativeUploadFlow`, Stage 01 F-01-13); silent exclusion of unenrolled/inactive employees from runs with no per-employee reason surfaced (F-01-14)
- **Desired outcome**: faster, less error-prone bulk registration; clear visibility into why a specific employee isn't in payroll
- **Current evidence**: Stage 01 F-01-13, F-01-14; Stage 03 F-03-08 (facts-only tool design), F-02-10 (C13's justification)
- **Best intervention type**: AI assistance for column mapping (ambiguous/unstructured input); deterministic facts + AI narration for "why not enrolled"
- **Contributing capability**: C13 (Onboarding Mapping Assistant), C3 (State Explainer mode, current-state "why" narrative)
- **Platform prerequisite**: C14 (dry-run gate) must exist before C13 ships (per Stage 03 disposition)
- **Control/compliance prerequisite**: none beyond standard PII handling
- **Measurable outcome**: reduction in manual column-mapping time/errors vs. `NativeUploadFlow` baseline (baseline currently unquantified — see `outputs/onboarding-outcome-baseline.md`); reduction in "why isn't X in this run" support questions
- **Risk of false confidence/harmful incentives**: an AI-proposed mapping accepted without real scrutiny because "the AI already checked it" — mitigated only if C14's dry-run gate is real and visible, not decorative

## 4. Employment/contract configuration

- **Primary user**: bureau operator managing contract changes (grade/salary changes, contract end, shift type)
- **Current problem/friction**: `shift_type` NULL handling differs between the payroll-run path (defaults to DAY) and the timesheet path (hard rejects), Stage 01 F-01-16 — an operator can be confused about which behavior applies
- **Desired outcome**: consistent, predictable contract-field handling regardless of which downstream path consumes it
- **Current evidence**: Stage 01 F-01-15, F-01-16
- **Best intervention type**: deterministic/product fix (unify the NULL-handling rule or make the divergence visible in the UI) — not an AI problem
- **Contributing capability**: none of C1–C15
- **Platform prerequisite**: none
- **Control/compliance prerequisite**: none
- **Measurable outcome**: elimination of shift-type-divergence-caused calculation surprises (no current count exists — Stage 08/10 territory to quantify)
- **Risk of false confidence/harmful incentives**: none from AI; this is a pure product-consistency gap, noted here so it isn't lost, but the fix path is deterministic, not agentic

## 5. Timesheet and payroll-input collection

- **Primary user**: bureau operator or client-side timekeeper submitting inputs
- **Current problem/friction**: manual data-entry errors (e.g. 400 vs. 40 overtime hours) have no automated flag today (Stage 01 F-01-17 confirms input history exists but no anomaly mechanism)
- **Desired outcome**: catch input errors before they enter a run, not after
- **Current evidence**: Stage 01 F-01-17, F-01-18; Stage 02 F-02-04; Stage 03 F-03-04, C7
- **Best intervention type**: deterministic/statistical detection, optional AI narration — see `outputs/anomaly-detection-outcome-policy.md` for the full framing
- **Contributing capability**: C7 (Input Anomaly Detection)
- **Platform prerequisite**: none beyond existing `payroll_input` history
- **Control/compliance prerequisite**: none
- **Measurable outcome**: anomalies caught before run creation vs. today's baseline (caught only if a human happens to notice) — see measurement framework
- **Risk of false confidence/harmful incentives**: false negatives create false confidence ("the system would have caught it"); false positives create alert fatigue that leads operators to rubber-stamp flags — both are named risks in the measurement framework

## 6. Payroll readiness

- **Primary user**: bureau operator preparing to create a run
- **Current problem/friction**: missing timesheets, unenrolled employees, and expiring contracts surface only at run-creation time or via manual checking (Stage 01 F-01-19/20)
- **Desired outcome**: proactive surfacing of these conditions before the operator attempts run creation
- **Current evidence**: Stage 01 F-01-19, F-01-20; Stage 03 F-03-03, C6
- **Best intervention type**: deterministic readiness service + notification/work-queue — explicitly not an AI-driven agent (Stage 03 already established this)
- **Contributing capability**: C6 (Payroll Readiness Service)
- **Platform prerequisite**: C2 (notification layer)
- **Control/compliance prerequisite**: none
- **Measurable outcome**: reduction in run-creation failures/retries due to these three conditions; reduction in time-to-detection vs. today's "found at run-creation" baseline
- **Risk of false confidence/harmful incentives**: none from AI (none used here); the risk would be treating the readiness panel as exhaustive when it only covers 3 named conditions — the panel should not imply a broader completeness guarantee than it has

## 7. Run creation and calculation

- **Primary user**: bureau operator creating and running a payroll cycle
- **Current problem/friction**: none in the calculation core itself (fully deterministic, Stage 01 F-01-21–39); the operator-facing friction is asynchronous creation requiring polling (F-01-23) and the legacy-executor edge case (F-01-24/28)
- **Desired outcome**: reliable, explainable calculation with no silent behavior divergence between execution paths
- **Current evidence**: Stage 01 F-01-21 through F-01-39 (extensive); Stage 02 F-02-01
- **Best intervention type**: deterministic — this is the platform's core strength and must remain so (Principle 1)
- **Contributing capability**: C5 (Trace Explanation) is the AI-relevant layer *on top of* this stage's output, not a change to the calculation itself
- **Platform prerequisite**: legacy-executor retirement (not this stage's decision, but worth naming as a standing platform-health item)
- **Control/compliance prerequisite**: none beyond what already exists
- **Measurable outcome**: N/A for the calculation itself (already deterministic and correct per Stage 01); C5's outcome is covered separately below
- **Risk of false confidence/harmful incentives**: none — this area should stay exactly as deterministic as it is; any temptation to make calculation "smarter" via AI must be rejected per Principle 1/9

## 8. Exception handling

- **Primary user**: bureau operator triaging flagged issues (readiness gaps, anomalies, reconciliation mismatches)
- **Current problem/friction**: no defined resolution workflow exists for *any* flagged exception today — Stage 03 (F-03-14) already identified this as a missing handoff
- **Desired outcome**: every flagged issue has an owner, a resolution path, and a closure record
- **Current evidence**: Stage 03 F-03-14, `portfolio-boundary-map.md` §8
- **Best intervention type**: product UX / workflow design (exception queue) — see `outputs/exception-resolution-outcome.md` for the full framing
- **Contributing capability**: consumes output from C6, C7, and (once unblocked) C8
- **Platform prerequisite**: C2 (notification layer)
- **Control/compliance prerequisite**: an audit trail of exception resolution (currently not covered by `audit_log`/`event_store`, Stage 01 F-01-40) — forward to Stage 06
- **Measurable outcome**: time-to-resolution for flagged exceptions; rate of exceptions closed without documented resolution (should be zero)
- **Risk of false confidence/harmful incentives**: exceptions dismissed without genuine resolution just to clear a queue — the measurement framework must not reward "queue empty" without also tracking "resolved correctly"

## 9. Reconciliation and investigation

- **Primary user**: bureau operator resolving a reconciliation MISMATCH
- **Current problem/friction**: manual investigation today; the intended automation (C8) is blocked (Stage 02 D-02-02/D-02-03)
- **Desired outcome**: automatic, deterministic root-cause identification with AI narration, once unblocked
- **Current evidence**: Stage 01 F-01-33 through F-01-38; Stage 02 F-02-05, F-02-06, F-02-09; Stage 03 F-03-05, F-03-06, C8
- **Best intervention type**: deterministic diff computation + AI narration, per Stage 03's binding design constraint — not to be reopened here (per CONTEXT.md's explicit instruction)
- **Contributing capability**: C8 (blocked)
- **Platform prerequisite**: repository-level `payroll_reconciliation` workspace-scoping fix (F-01-33); historical reproducibility closure (F-01-27/29/38) — both Stage 05's remit
- **Control/compliance prerequisite**: none beyond the platform fixes above
- **Measurable outcome**: (deferred until unblocked) causal-accuracy rate against known MISMATCH test cases, once C8 ships
- **Risk of false confidence/harmful incentives**: shipping C8 before both preconditions close would be the single worst outcome in this entire map — an incorrect causal attribution on a financial mismatch is a severe trust failure; this risk is exactly why D-02-02/03 block it

## 10. Approval and assurance

- **Primary user**: bureau operator/manager approving a calculated run
- **Current problem/friction**: none identified — the approval mechanism is deterministic and DB-enforced (Stage 01 F-01-37, F-01-39), stricter than documented
- **Desired outcome**: continued deterministic, tamper-evident approval — no change needed
- **Current evidence**: Stage 01 F-01-37, F-01-39
- **Best intervention type**: no new capability
- **Contributing capability**: none — C10 (confirmation protocol) is relevant only once write-capable proactive agents exist (C8/C11, both currently blocked/restricted), not to today's human-driven approval flow
- **Platform prerequisite**: none
- **Control/compliance prerequisite**: none
- **Measurable outcome**: N/A — no gap identified
- **Risk of false confidence/harmful incentives**: none

## 11. Locking and payment preparation

- **Primary user**: bureau operator locking a run before payment
- **Current problem/friction**: none identified — deterministic and correctly enforced (Stage 01 F-01-37, F-01-39); one dead-code concern (F-01-38's unreachable status branches) is a code-hygiene item, not an operator-facing outcome gap
- **Desired outcome**: continued reliability — no change needed
- **Current evidence**: Stage 01 F-01-38, F-01-39
- **Best intervention type**: no new capability (the dead-branch cleanup is a Stage 08 code-quality item, not an outcome)
- **Contributing capability**: none
- **Platform prerequisite**: none
- **Control/compliance prerequisite**: none
- **Measurable outcome**: N/A
- **Risk of false confidence/harmful incentives**: none

## 12. Post-payroll support and explanation

- **Primary user**: bureau operator explaining a run's results to a client or fielding "why" questions
- **Current problem/friction**: no natural-language explanation capability exists today; operators manually read `component_trace_jsonb` or the Results/Timeline UI (Stage 01 F-01-41, F-01-44)
- **Desired outcome**: fast, accurate, evidence-linked explanation of current-run results; (future) historical explanation once platform gaps close
- **Current evidence**: Stage 01 F-01-41, F-01-44; Stage 02 F-02-07, F-02-09, F-02-11; Stage 03 F-03-01, F-03-13, F-03-15, C3, C5
- **Best intervention type**: AI assistance (retrieval and explanation), tightly bounded to evidence already computed deterministically
- **Contributing capability**: C3 (current-state assistant), C5 (trace explanation); C4 (historical explanation) blocked, not reopened here
- **Platform prerequisite**: null-trace refusal spec for C5 (Stage 08); historical-reproducibility closure for C4 (Stage 05)
- **Control/compliance prerequisite**: none beyond evidence-linking (Principle 4)
- **Measurable outcome**: reduction in support/navigation questions reaching a human; time-to-answer for "why" questions; zero instances of an unsourced number in an explanation
- **Risk of false confidence/harmful incentives**: an operator trusting a plausible-sounding AI explanation without checking the underlying evidence — mitigated only if evidence is always shown alongside the explanation, never in place of it

## 13. Statutory-rule monitoring and maintenance

- **Primary user**: compliance-responsible operator/administrator
- **Current problem/friction**: statutory-rule changes require a developer-authored migration; no operator-facing detection or application mechanism exists (Stage 01 F-01-45/46)
- **Desired outcome**: automated detection of external regulatory changes, with a real, human-approved application path (not migration-only)
- **Current evidence**: Stage 01 F-01-45, F-01-46; Stage 02 F-02-12; Stage 03 F-03-09, C11, C12
- **Best intervention type**: AI assistance for detection/comparison/drafting (C11, narrowly scoped); deterministic workflow for application (C12) — full chain in `outputs/compliance-outcome-chain.md`
- **Contributing capability**: C11 → C12
- **Platform prerequisite**: C12 must exist for C11's output to be actionable
- **Control/compliance prerequisite**: external-source trust/freshness/provenance policy (Stage 06); approval-workflow design (Stage 06)
- **Measurable outcome**: time-to-detection and time-to-apply for a real statutory change, vs. today's manual-notice-then-migration baseline
- **Risk of false confidence/harmful incentives**: misinterpreting non-authoritative external source text as an authoritative legal change — a genuine legal-risk failure mode, forwarded to Stage 06, not adjudicated here

## 14. New-client onboarding and parallel-run validation

- **Primary user**: bureau operator onboarding a new client, often running the new system in parallel with a legacy system before cutover
- **Current problem/friction**: manual column mapping (F-01-13); no formal "dry-run" or parallel-run confidence mechanism exists; the existing "Reconcile with old system" tool (Stage 01 F-01-41/44's `ReconSlideOver`) is a client-side-only, non-persisted comparison tool
- **Desired outcome**: faster, higher-confidence go-live with quantified parallel-run agreement
- **Current evidence**: Stage 01 F-01-13, F-01-41; Stage 02 F-02-10; Stage 03 F-03-10, C13, C14
- **Best intervention type**: AI assistance for mapping (C13) + deterministic validation/dry-run (C14, needs Stage 08 mechanism definition)
- **Contributing capability**: C13 → C14
- **Platform prerequisite**: dry-run mechanism definition (Stage 08); a persisted (not client-side-only) parallel-run comparison mechanism would materially improve this outcome but does not exist today — see `outputs/onboarding-outcome-baseline.md`
- **Control/compliance prerequisite**: none beyond standard onboarding validation
- **Measurable outcome**: time-to-go-live; parallel-run agreement rate (currently unquantifiable — no baseline exists, see baseline-gap note)
- **Risk of false confidence/harmful incentives**: treating a passing dry-run as equivalent to a passing parallel run against the client's real legacy system — these are different confidence levels and must not be conflated in messaging to the operator or client

## 15. Operational reporting and continuous improvement

- **Primary user**: bureau management, seeking operational/commercial insight across clients and periods
- **Current problem/friction**: no capability in the approved portfolio addresses this at all — confirmed absent from all 15 capabilities in `03-agent-portfolio/outputs/agent-capability-matrix.md`
- **Desired outcome**: visibility into recurring errors, deadline risk, control-completion status, and (commercially) client profitability/operational cost
- **Current evidence**: none — this is a genuinely missing outcome area, not evidenced by Stage 01–03 because no capability touches it
- **Best intervention type**: primarily analytics/reporting (deterministic aggregation), with AI potentially useful for narrative summarization on top — see `outputs/outcome-capability-matrix.md`'s "missing" row and `outcome-prioritisation.md`
- **Contributing capability**: none currently — a genuine portfolio gap
- **Platform prerequisite**: an audit/event trail complete enough to aggregate from (Stage 01 F-01-40's audit-coverage gap is directly relevant — you cannot report on what isn't recorded)
- **Control/compliance prerequisite**: none beyond the audit-coverage fix
- **Measurable outcome**: not yet definable — this area needs Stage 04's own prioritisation treatment before a metric can be proposed
- **Risk of false confidence/harmful incentives**: none yet, since nothing is built — the risk to flag is scope creep if this area is pursued before the more foundational gaps (exception handling, audit coverage) are closed
