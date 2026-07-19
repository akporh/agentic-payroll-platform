# Stage 13 Output: Proposed Roadmap (Q1 + Q2)

The sequenced build roadmap toward the Stage 12 approved direction (`12-target-direction/outputs/capability-end-state-map.md`), assembled **inside** the Stage 11 constraint set (`11-commercial-product-strategy/outputs/sequencing-economics.md`) and never against it. This is a proposal for human approval — it authorises no build (see `final-decision-pack.md` §Q5 phase boundary). Every item traces to a design/remediation/register source; every constraint placement cites its O/W row; per-item "done" is the launch-gate register's **"done = row green"** rule (`10-evaluation-assurance/outputs/launch-gate-evidence-register.md`, DEC-10-02).

**No dates, velocities, or capacity are stated anywhere in this roadmap** — tranche *ordering* and calendar *windows* only. Build capacity is Michael's to state; where the roadmap needs a scheduling fact it is an explicit ask in `final-decision-pack.md`, never an assumption (CONTEXT §Constraints; Stage 12 handoff §5).

---

## 0. How to read this roadmap

- **Order is fixed; timing is not.** Tranches run in the order shown because O1–O9 (register-enforced orderings) and the value-priority signal require it. Within-tranche item order follows the value signal but is not itself register-enforced except where an O-row says so.
- **The value-priority sequence is the direction's own order.** `C1 → C2(+exception substrate) → C12 & C14 → C6/C3/C5 → C7 shadow → C11 → C13` (Stage 11 →13 handoff §4; Stage 12 handoff §2). Deterministic-first value matches readiness (DEC-11-03) — so no direction-vs-constraint trade-off exists, and this roadmap makes none.
- **Every O/W constraint is honoured with zero departures** (§4 audit). No item breaks an ordering or window, so no roadmap-driven human decision is required *by the sequencing rules*. The human decisions in `final-decision-pack.md` are the pre-build gates (DQ-006/007/008), the source-document disposition, the SaaS fork, and the visibility/evidence-gap items — not sequencing departures.
- **Held positions are not tranches.** C4, C8 (capability), C9, C15, and multi-tenant SaaS are deliberately absent from the build sequence (§3); their remediation-only work (C8) rides Tranche 1 as plumbing.

---

## 1. Pre-build near-term actions (Tranche 0) — no build authorisation required

These are the calendar-bound, near-zero-cost actions that do not need Phase 2/3 authorisation to *schedule* and that de-risk later tranches. Detailed in `baseline-and-near-term-plan.md`; listed here so the roadmap's dependency spine is complete.

| # | Action | Why it sits before the build tranches | Source |
|---|---|---|---|
| T0.1 | Capture **B3** (time-to-go-live) and **B5** (statutory time-to-apply) retrospectives now | W5 — retrospectively computable from engagement records + `payroll_run` history + NTA 2025/PAY-TAX-1 evidence; anchors C14 (B3) and C12/C11 (B5) before either ships; first two "measured, not asserted" artifacts (Stage 12 handoff §4) | W5; `evidence-chain-and-baselines.md` B§3 |
| T0.2 | Resolve **EG-004** (next-onboarding timing) | The single scheduling fact the **unrecoverable** B1/B2 window (W2) hinges on; determines whether the B1/B2 protocol must be armed ahead of the next onboarding regardless of C13's build order | EG-004; W2 |
| T0.3 | Initiate the **DQ-006 + DQ-008** professional (Nigerian tax/legal) engagement | External-adviser lead time is the risk, not cost; starting at/after approval gives DQ-006 the longest runway before C11 (Tranche 5) and DQ-008's answer before anyone builds retention tooling | W6; `pre-build-decision-logistics.md` §2 (DEC-11-05) |
| T0.4 | Package **DQ-007 (+ MFA hard-gate)** into this approval pack | Earliest human gate any build sequence hits; gates Tranche 2 (C12); zero external dependency (`final-decision-pack.md`) | O8; `pre-build-decision-logistics.md` §1 |
| T0.5 | Flag **FULL_RUN dead-option removal** to the standing maintenance workflow | Trivial frontend fix; outside this programme's write authority — carried as a handoff item, executed via the repo's normal maintenance slot | Stage 09 handoff §2; `sequencing-economics.md` §5.6 |

---

## 2. Build tranches

Each build item states: **scope** (designs/mechanisms/surfaces it lands), **placement** (O/W rows + value signal), **one-off cost** attached per the cost-placement table, and **definition of done** (the launch-gate register rows/artifacts it closes — "done = row green"), with B-series baselines threaded at their windows.

### Tranche 1 — Deterministic foundations (C1 → C2)

*Deterministic platform engineering, sequenced and staffed separately from AI-capability work (O3, D-03-01 condition 12). Nothing else — no capability, surface, or claim — launches before this tranche closes (O1).*

#### Item 1.1 — C1 Identity & Auth Foundation

- **Scope**: operator/membership model; JWT sessions with token-derived `workspace_id`; `get_current_operator` on every route; real `performed_by` everywhere; step-up re-auth hook for approvals (DEC-07-03, mechanism present before C12 consumes it); auth-event audit; production CORS origin pinning (F-07-03); `workspace_info()` `LIMIT 1` retired or token-scoped (F-07-02); R1 caller-supplied-actor rewiring. **Plus the SS-1 route-table-generated isolation harness** and the decorative-scoping remediations it proves dead (five routes, F-05-03/F-07-01).
  - Source: `08-technical-architecture/outputs` C1 auth design; `auth-foundation-design.md`; `tenant-isolation-verification-standard.md` §3.2–3.3; end-state map C1.
- **Placement**: **O1** (C1 before everything — zero auth exists today); **O3** (deterministic, separately staffed). First item in the value sequence.
- **One-off cost attached**: **Frontend test harness** (Vitest + RTL + CI job) — lands with C1 as the first frontend-touching build (F-10-01; `sequencing-economics.md` §3). Deferring it converts a small fixed cost into a permanent per-release manual-testing tax.
- **Definition of done (rows green)**: CG-1 / SG-1 register block —
  - route-enumeration auth test (100% routes authenticate, ET-1);
  - R1 grep-clean check + per-route cross-workspace-404 negative-path tests (ET-1);
  - audit cut-over epoch fixture test (pre/post-epoch labelling, ET-1);
  - token tamper/expiry/revocation tests, membership fixture test, auth-event write test, step-up freshness/single-consumption tests (ET-1);
  - production CORS origin-pinning deployed-config inspection (ET-3);
  - `workspace_info()` surviving-form test or removal-by-route-enumeration (ET-1);
  - **SS-1** route-table-generated isolation test green (mismatched-token rejection + cross-workspace 404 across every `{workspace_id}` route; unscoped-surface allowlist asserted).
  - **Remediation rows also closed here** (register §4 / C8 block): reconciliation workspace-scoping fix (F-01-33, cross-workspace regression test); five decorative routes fixed (SS-1 proves the pattern dead platform-wide); isolation control statement (ET-5).
- **Baselines**: none.

#### Item 1.2 — C2 Event / Tool / Notification Foundation (+ exception substrate + tool layer)

- **Scope**: transactional outbox; the four missing events; consumer worker (advisory-lock single-worker + idempotency); `workspace_notification`; **the exception data model and exception-resolution workflow** (create/own/resolve/verify/close); `tool_call_log`; versioned PII-sanitising tool serialisation; the declarative tool-guard wrapper + capability-scoped registries with 11 tool contracts (SS-2/SS-4); SC-4 no-purge floor.
  - Source: `08-technical-architecture/outputs` C2 unit-of-work/outbox/exception model + `tool_call_log`; 11 tool contracts + decorator-registry wrapper; `event-audit-foundation-design.md`; `tool-layer-security-pattern.md`; `tool-contracts.md`; end-state map C2.
- **Placement**: **O2** (C2 before C3/C6-surfacing/C7/C11-alerting and before the exception workflow); **O3** (deterministic, separately staffed). Second in the value sequence.
- **One-off cost attached**: **Exception-workflow substrate** — lands with C2 (`sequencing-economics.md` §3). Without it C7 cannot launch (O4) and C6/C7's flag-with-resolution value multiplier is lost (F-04-01, D-04-01).
- **Definition of done (rows green)**: CG-2 / SG-2 register block —
  - forced-failure outbox atomicity test (audit/outbox failure rolls back the state change, ET-1);
  - sanitizer-version-on-every-`tool_call_log`-row test; untrusted-strings-as-data serialization property test (ET-1);
  - four per-event emission tests; two-instance single-worker + consumer-idempotency tests (ET-1);
  - append-only floor: UPDATE/DELETE rejection per protected table + step-up single-transition exception + **SC-4 no-purge design-absence check** (ET-1 + ET-2);
  - **exception-workflow substrate** create/own/resolve/verify/close end-to-end test + per-transition audit row (ET-1);
  - SC-2 tool-registry uniformity + per-tool negative-path + wrapper-independence + fail-closed-startup tests; SC-3 tool-log field-presence test; SS-3 audit-store integrity set; SS-4 per-capability session-registry equality tests (ET-1).
  - **Remediation rows also closed here** (register §4): `component_trace_jsonb` null guard; `salary_definition` edit-lock (D-ARCH-1 in-progress-run PATCH rejection); D-ARCH-1 dead-branch/status-drift enum-iteration test; `load_inputs_for_run` closure (F-05-11).
- **Baselines**: **K4 exception time-to-close** begins its first-cycle establishment once the workflow is live (no pre-existing baseline — greenfield, `direction-kpis.md` K4).

---

### Tranche 2 — Deterministic differentiators (C12 & C14)

*The two deterministic, claimable, load-bearing capabilities (value signal groups them together). Both ride entirely on Tranche 1.*

#### Item 2.1 — C12 Statutory-Rule Change Management

- **Scope**: application-level proposal/approval/apply workflow for `statutory_rule` / `tax_band`; correction-by-version-row (**DEC-08-09** UNIQUE widening `(country_code, effective_from)` → `(…, version)`, via the repo's standing `/arch-council` gate); step-up re-authenticated approvals; atomic approval records; **the platform's first platform-level frontend area** (route family, chrome, `PLATFORM_ADMIN` gating — scoped as its own story, not hidden inside "statutory UI"); context-launched CORRECTION-run CTA (DQ-005 closed → DEC-11-02); date-driven resolution only (`is_active` never sufficient).
  - Source: `08-technical-architecture` C12 proposal/approval mechanism; `09-human-experience` `statutory-approval-experience.md` (C11→C12 one-workflow IA); end-state map C12; Stage 09 handoff §3 (platform-level area).
- **Placement**: value signal (C12 & C14 after foundations); **O8** — DQ-007 (+ MFA) must resolve before build authorisation (this pack's earliest gate); **O5** — C12 exists before/with C11 (Tranche 5 rides on it).
- **One-off cost attached**: **Platform-level frontend area** (route family, chrome, `PLATFORM_ADMIN` gating) — scoped as its own story within C12 (F-09-04; `sequencing-economics.md` §3; Stage 09 handoff §3).
- **Pre-build human gate**: **DQ-007 (+ MFA hard-gate)** — see `final-decision-pack.md`. If resolved proposer ≠ approver, multi-operator capability is **promoted from later-increment to a C12 prerequisite** (a scope change this item inherits; `product-scope-boundaries.md` §2.1).
- **Definition of done (rows green)**: CG-12 / SG-12 register block — verified-identity approvals (no-auth/no-step-up rejected); atomic approval-record test; deterministic validation incl. graceful UNIQUE conflict + DB backstop; impact-preview presence + recompute-on-apply; append-only correction-by-version test (`superseded_by_rule_id`); step-up freshness/single-use + event reference; origin-equivalence test (C11-origin ≡ human-origin); date-driven-resolution grep/contract check; UX behaviours 8–12 (ET-1 + ET-3); **DQ-007 human decision record** (row cannot close without it); **DEC-08-09 `/arch-council` review budgeted**.
- **Baselines**: **B5** (time-to-apply, retrospective — capturable now, T0.1) anchors the K1 apply half (ET-6).

#### Item 2.2 — C14 Deterministic Import Validation & Dry-Run

- **Scope**: dry-run endpoint reusing the real executor path (`run_sequential_payroll`, DEC-08-11) with **no** `payroll_run` row (DQ-004); workspace-scoped `dry_run_execution` artifact with input-hash commit linkage; schema/tenant/rule validation on the existing hard validator.
  - Source: `08-technical-architecture` `dry-run-mechanism-design.md`; end-state map C14.
- **Placement**: value signal (with C12); **O6** — C14 before C13 (C13 in Tranche 6 may not ship ahead of it). The deterministic hard safety gate for onboarding, claimable before any AI mapping exists.
- **One-off cost attached**: none unique (rides Tranche 1's harness).
- **Definition of done (rows green)**: CG-14 / SG-14 register block — commit-gate hash test (missing/mismatched/failed `dry_run_id` rejected); commit audit-actor test; cross-workspace dry-run → 404 + verified-principal artifact rows; **DQ-004 non-mutation test** (row-count snapshots of `payroll_run`/`payroll_result`/`payroll_input.payroll_run_id`/`event_store` identical before/after — the load-bearing closure evidence); DQ-003 real-path equivalence test; input-non-consumption test; UX behaviours 19–20 (ET-1).
- **Baselines**: **B3** (time-to-go-live, retrospective — T0.1) and **B2** (parallel-run agreement) at launch (ET-6). B2 requires the next real onboarding (W2) — see Tranche 6 / T0.2. K2 keeps dry-run-pass and client-validated accuracy as **separate** series (never collapsed — D-04-01, `direction-kpis.md` K2).

---

### Tranche 3 — Readiness & assistance (C6, C3, C5)

*Value signal group `C6/C3/C5`. All ride on C2 (O2). This tranche introduces the first LLM capability and the first scheduled execution.*

#### Item 3.1 — C6 Payroll Readiness Service

- **Scope**: the existing readiness checks (missing timesheets, missing salary definitions, expiring contracts) surfaced proactively through C2's notification/work queue — never presented as an exhaustive pre-flight check; named service principal for scheduled execution (SG-6/R3).
  - Source: end-state map C6; `04-outcome-discovery` readiness outcome; C2 notification path.
- **Placement**: **O2** (needs C2's notification path). First in the `C6/C3/C5` group.
- **One-off cost attached**: **Scheduled-job CI seam** (workflow triggers) — the register attaches it to the "first Class B control" (F-10-02; `sequencing-economics.md` §3). C6 introduces the first **scheduled execution** and C3 introduces the first **Class B eval re-run**; whichever of C6/C3 a sprint plan builds first carries the seam. Trivial either way — flagged as an **implementation-specification to pin at sprint planning** (`final-decision-pack.md` §Q3 taxonomy), not a decision.
- **Definition of done (rows green)**: CG-6 / SG-6 register block — readiness-event emission through the outbox test; scheduled-run service-principal audit test (never a placeholder); standard QA fixtures (ET-1).
- **Baselines**: **B4** (time-to-detection, 3-cycle observation) must be captured **before** C6 ships (W4) — **start the observation at C6 sprint-planning time**, not at ship (ET-6; anchors K3-adjacent detection claims via the framework).

#### Item 3.2 — C3 Operator Assistant (current-state mode)

- **Scope**: one conversational assistant over the five current-state read tools, PII-stripped, rate-limited, with the current-state-only boundary enforced by refusal (D-02-03); navigation + state-explanation + action-planning as three modes of one assistant; assistant-boundary UX.
  - Source: end-state map C3; `09-human-experience` `assistant-boundary-experience.md`; `llm-evaluation-framework.md`.
- **Placement**: **O2** (needs C2's audited tool layer). Second in the `C6/C3/C5` group.
- **One-off cost attached**: **LLM eval infrastructure** (corpus format, runner, report convention) — lands with C3 as the first LLM capability (`sequencing-economics.md` §3). Later AI capabilities inherit it (P-F pattern-scaling); corpus authorship (~70 cases/capability) is the recurring cost either way.
- **Definition of done (rows green)**: CG-3 / SG-3 register block — SC-3 uniformity test green for C3's five tools; per-tool `REFUSED` audit test; C3 launch eval report (refusal-correctness on historical/out-of-scope/cross-workspace corpus, ~100% on the historical class, ET-4); injection corpus + eval report (ET-1 + ET-4); session-registry set-equality test (five tools only); rate-limiting test/config; UX behaviours 1–4.
- **Baselines**: **B6** (support-question 4-week tally) must exist pre-launch (W3) — **start the tally at C3 sprint-planning time** (ET-6; anchors the framework's support-question-reduction claim).

#### Item 3.3 — C5 Trace Explanation (`explain_component_trace`)

- **Scope**: slot-filling narration of `component_trace_jsonb` for the **current** run, with the null-trace refusal specified and a data-access-layer null-guard (Stage 05 gap, closed by the Stage 08 remediation set); trace shown alongside; zero invented numbers.
  - Source: end-state map C5; C5 remediation set; `llm-evaluation-framework.md`.
- **Placement**: **O2** (rides C2's tool layer + C3's eval infra). Third in the `C6/C3/C5` group. (Historical narration is C4 — **blocked**, D-02-03 — and is not part of C5.)
- **One-off cost attached**: none unique (rides C3's eval infra).
- **Definition of done (rows green)**: CG-5 / SG-5 register block — null-trace refusal test (legacy-executor result → verbatim `TRACE_UNAVAILABLE` + logged refusal, UX behaviour 1); **zero-hallucination provenance serialization property test** (every numeric token in output exists in source trace — code-enforced, the test *is* the evidence, doubles as SG-5/T6); SC-3 field-presence test on the C5 path; session-registry set-equality test (`get_run_results` path only); eval report for narration-refusal quality (ET-1 + ET-4).
- **Baselines**: none (grounding is code-enforced; feeds K5).

---

### Tranche 4 — Input anomaly detection (C7 shadow → GA)

#### Item 4.1 — C7 Input Anomaly Detection

- **Scope**: the layered D-04-01 calibration (absolute thresholds → period-on-period variance; median-ratio test, R_high 3.0 / CRITICAL 10× / R_low ⅓, min history 3 nonzero periods, window ≤ 6 — DEC-08-12); versioned auditable thresholds; **shadow-mode rollout governed by `calibration-governance.md`**; resolution through the exception queue; LLM restricted to narration of already-flagged anomalies (no LLM in the detection path).
  - Source: end-state map C7; `08-technical-architecture` `anomaly-detection-design.md`; `10-evaluation-assurance` `calibration-governance.md`; HD-7/D-04-01.
- **Placement**: **O4** (hard gate) — C7 launches only after C2's exception-resolution workflow is live (Tranche 1); register enforces C7's row may not close before C2's. Value signal places C7 after the C6/C3/C5 group.
- **Window**: **W1** — C7 GA lags its deploy by **≥ 3 full payroll cycles AND ≥ 20 terminal exception records** (shadow exit, both conditions, DEC-10-08). Plan shadow entry ≥ one quarter before any claimed GA; any month-one value claim is wrong by construction.
- **One-off cost attached**: none unique (narration rides C3's eval infra if the narration layer ships).
- **Definition of done (rows green)**: CG-7 / SG-7 register block — C2 exception end-to-end test green **before** C7 launch (sequenced); threshold-change versioning + domain-1 audit test; shadow-mode exclusion test (INFO + `shadow: true`, excluded from operator counts, UX behaviour 13) + calibration-metric queries; determinism property test + formula fixtures (the 400-vs-42 worked example); **ET-2 no-LLM-in-detection-path import test** (+ narration injection corpus + eval report *if* narration ships); calibration governance operating — shadow-exit decision record + first calibration report (ET-5).
- **Baselines**: shadow-mode data is its own baseline; the three D-04-01 governance metrics (confirmed-error capture, correct-dismissal, later-discovered-unflagged) are tracked from shadow onward, reportable at exit (K3).

---

### Tranche 5 — Compliance monitoring (C11)

#### Item 5.1 — C11 Compliance Monitoring (narrowed)

- **Scope**: scheduled monitoring of the Tier-1 authoritative-source allowlist; deterministic diff against `statutory_rule`; LLM-drafted proposals with full source citations, **feeding C12's approval workflow** — never writing anything itself (D-02-04); monitoring-stall alerting via C2. Detect / compare / summarise / draft only.
  - Source: end-state map C11; `06-compliance-controls` `compliance-monitoring-source-policy.md`; `08-technical-architecture` C11 mechanism; HD-5/D-02-04.
- **Placement**: **O5** — C11 with-or-after C12 (C12 built in Tranche 2; register row-closure precondition); **O8** — **DQ-006** resolved before C11 build authorisation (the Tranche 0 professional engagement must conclude first). Value signal places C11 after C7 shadow.
- **One-off cost attached**: none unique (scheduled seam from Tranche 3; eval infra from Tranche 3).
- **Pre-build human gate**: **DQ-006** (Tier-1 allowlist legal sufficiency) — see `final-decision-pack.md`. C11's guarantee, and Story 1's detection half, is exactly as strong as this allowlist.
- **Definition of done (rows green)**: CG-11 / SG-11 register block — source-policy-in-code test (non-Tier-1 source → no operative claim; provenance fields mandatory); monitoring-stall alerting test via C2; register sequencing check (C11 row may not close before C12 row); session-registry test (zero workspace-scoped tools — context isolation); T5 hostile-source injection corpus + eval report; per-proposal provenance field-presence test; **DQ-006 human decision record** (row cannot close without it). Precision, never volume (D-04-01).
- **Baselines**: **B5** (time-to-apply comparison, retrospective — T0.1) anchors the K1 detection-to-apply story (ET-6).

---

### Tranche 6 — Onboarding mapping (C13)

#### Item 6.1 — C13 Onboarding Mapping Assistant

- **Scope**: AI-proposed column mapping and salary-definition/grade/designation assignment over the existing `NativeUploadFlow` / `ColumnMappingPanel` components (**three consuming surfaces — three-surface regression obligation**, Stage 09 RC-1); proposals only, applied through the deterministic Upload/Enroll path after operator confirmation; C14's dry-run as the hard backstop; proposals render only to the uploader's session.
  - Source: end-state map C13; `09-human-experience` onboarding flow; `sequencing-economics.md` §4 (three-surface obligation).
- **Placement**: **O6** — C13 **never ahead of C14** (C14 built in Tranche 2; register row-closure precondition). Last in the value sequence.
- **Window**: **W2 (unrecoverable)** — **B1/B2 must be captured on a real onboarding under the *current* flow *before* C13 ships.** If the next onboarding lands after C13, C13's improvement claims are permanently anchorless. **EG-004 is the scheduling fact** (T0.2): if an onboarding is plausible in the C13/C14 horizon, arm the B1/B2 observation protocol *ahead of it* regardless of build order.
- **One-off cost attached**: none unique. **Recurring**: the three-surface regression obligation on every C13-adjacent change (P-E/§4 of sequencing-economics).
- **Definition of done (rows green)**: CG-13 / SG-13 register block — register sequencing check (C13 row may not close before C14 row); SC-3 test on the mapping-proposal tool path + queryable correction stream; no-direct-writes test (no mapping commits without operator confirmation, UX behaviour 18); C13 hostile-header corpus + eval report; session-scoping test; catalog tool under SS-2 (via SC-2 artifacts).
- **Baselines**: **B1** (mapping time/error) and **B2** (parallel-run agreement) — captured pre-C13 on a real onboarding (W2, unrecoverable). C13's improvement claims are available **only** if B1/B2 were captured in time; otherwise the KPI reports absolute values labelled anchorless (`direction-kpis.md` §3).

---

## 3. Held positions (deliberately not in the build sequence)

Dispositions are D-03-01-fixed; this roadmap re-opens none (CONTEXT §out-of-scope).

| Capability | Disposition | Roadmap treatment |
|---|---|---|
| **C4** Historical Explanation | **blocked** (D-02-03 until F-01-27/29/38 close with regression evidence) | No tranche; no launch evidence definable while blocked; no claim assumes it |
| **C8** Reconciliation Investigation | **blocked** (D-02-02 + D-02-03) | Capability waits for both preconditions. Its **remediations proceed as plumbing** in Tranche 1: reconciliation workspace-scoping fix (F-01-33) + five decorative routes (SS-1) — closed with C1's DoD |
| **C9** Trace Agent | **rejected, permanently** | No tranche, no session registry. Design-absence is itself register evidence (ET-2, checked by the SS-4 uniformity test's approved-list equality). Intent covered by C5 (and, once unblocked, C8) |
| **C10** Structured Confirmation Protocol | deterministic; **built when a write-capable consumer needs it** | Not pinned to a fixed tranche. C12 carries its own bespoke approval workflow and C13's proposals apply through Upload/Enroll confirmation — so no current portfolio item forces C10. **Placement is an implementation-specification** (`final-decision-pack.md` §Q3): built on-demand when a first write-capable AI-proposing consumer requires the generic protocol; DoD = CG-10/SG-10 rows at that point |
| **C15** Email Notifications | **deferred** until C2's in-app notifications are proven in production | No tranche; a deterministic delivery extension of C2 when scheduled (evidence rows defined then, ET-1) |
| **Multi-tenant SaaS** | requires the F-11-01 human decision bundle | Absent from the roadmap. If the roadmap is asked to serve SaaS ambition, that bundle (product + RR-1 re-open + scope) goes on the **critical path first** — see §4 RR-1 discipline and `final-decision-pack.md` |

---

## 4. Constraint audit — every O/W honoured, zero departures

| Constraint | Requirement | Roadmap placement | Honoured? |
|---|---|---|---|
| **O1** | C1 before everything | Tranche 1 Item 1.1 | ✅ |
| **O2** | C2 before C3/C6-surfacing/C7/C11-alerting + before exception workflow | C2 in Tranche 1; all consumers in Tranches 3–5; exception substrate ships *with* C2 | ✅ |
| **O3** | C1/C2 deterministic, staffed separately from AI work | Tranche 1 flagged deterministic + separately staffed | ✅ |
| **O4** | C7 after the exception-resolution workflow (hard gate) | Exception workflow in Tranche 1 (C2); C7 in Tranche 4 | ✅ |
| **O5** | C11 with/after C12 | C12 Tranche 2; C11 Tranche 5 | ✅ |
| **O6** | C13 never ahead of C14 | C14 Tranche 2; C13 Tranche 6 | ✅ |
| **O7** | C4/C8 blocked; no timeline assumes they unblock | Held (§3); C8 remediation-only in Tranche 1 | ✅ |
| **O8** | DQ-006 before C11 build; DQ-007 before C12 build | DQ-007 in this pack (gates Tranche 2); DQ-006 engagement T0.3 (concludes before Tranche 5) | ✅ |
| **O9** | No retention enforcement before DQ-008 | No roadmap item builds retention/purge tooling; SC-4 no-purge in Tranche 1; DQ-008 engagement T0.3 | ✅ |
| **W1** | C7 GA ≥ 3 cycles + ≥ 20 terminal records post-deploy | Tranche 4 window stated | ✅ |
| **W2** | B1/B2 need a real onboarding before C13 (unrecoverable) | T0.2 (EG-004) + Tranche 6 window stated | ✅ |
| **W3** | B6 4-week tally pre-C3 | Tranche 3 Item 3.2 — start at C3 sprint planning | ✅ |
| **W4** | B4 3-cycle observation pre-C6 | Tranche 3 Item 3.1 — start at C6 sprint planning | ✅ |
| **W5** | B3/B5 capturable now | Tranche 0 (T0.1) | ✅ |
| **W6** | DQ-006/008 professional lead time | Tranche 0 (T0.3) | ✅ |

**No departure breaks an O/W constraint**, so no roadmap-sequencing human decision is required (the register's own rule). Two placement details are left to sprint planning as **implementation-specifications, not decisions**: the CI schedule seam's exact host (C6 vs C3, Item 3.1) and C10's build trigger (§3).

**RR-1 trigger (c) discipline** (DEC-10-16 / DEC-11-04 / DEC-12-01): this roadmap is **single-bureau (SaaS-ready posture)**. **No roadmap item exists because of SaaS ambition** — the assurance substrate (SS-1 route-table isolation, tool-guard registries, evidence chain) is built for the single bureau and is merely *not throwaway* with respect to a future SaaS story. Therefore the F-11-01 bundle is **not** placed on the critical path. If the human reviewer takes up the SaaS trajectory at approval, that changes: the bundle (incl. RR-1 re-open) goes first (`final-decision-pack.md`).

---

## 5. Roadmap ↔ posture check (P-A…P-H)

Every tranche is checkable against the Stage 12 posture constraints (`target-architecture-posture.md`); none is violated:

- **P-A** (determinism-first): all calculation/statutory/state/mutation paths stay deterministic; C7's detector is deterministic (ET-2); no LLM proposed in any of those paths.
- **P-B** (single generation choke points): SS-1 route-table + tool-registry harness lands in Tranche 1 and every later surface/tool registers through it.
- **P-C** (append-only evidence): SS-3 + SC-4 no-purge in Tranche 1; no item mutates/deletes audit rows; retention enforcement waits for DQ-008 (O9).
- **P-D** (independent tool-layer scoping): every tool ships with its negative-path test + registry entry (Tranche 1 onward); C8's `get_reconciliation` stays blocked until the repo-level fix (Tranche 1) lands.
- **P-E** (capped cadence): the tranche count does not grow the standing monthly/quarterly session load beyond the cap; C7's calibration and the three-surface C13 obligation fit the capped sessions.
- **P-F** (pattern-scaling): capability N+1 (C5 after C3; C11/C13 after eval infra) reuses the machinery — no new assurance *infrastructure* per capability.
- **P-G** (trust-led pacing): B-series baselines precede every improvement claim; C7 shadow (W1) is honoured; "done = row green" throughout.
- **P-H** (residual-risk boundaries): no item claims a stronger property than the accepted residual set (RR-1–5); the overclaim table binds every claim.
