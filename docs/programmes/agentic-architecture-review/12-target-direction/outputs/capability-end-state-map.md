# Stage 12 Output: Capability End-State Map (Q4)

The concrete "to-be" picture: what "the portfolio realised" looks like, capability by capability, **dispositions intact** (D-03-01 — nothing re-opened). This map replaces the source document's five-track structure (Tracks P/V/W/X/Y) as the target description; see `source-document-disposition.md`. For each capability: what exists at end-state, what it does, and what evidences it (launch-gate evidence register rows and ET-types, `10-evaluation-assurance/outputs/launch-gate-evidence-register.md`; mechanism designs, Stage 08; surfaces, Stage 09).

## 1. Realised end-state, by capability

### Foundations (deterministic platform — not agents)

**C1 — Identity & Auth Foundation** *(reclassified deterministic)*
Exists: operator/membership model, JWT sessions with token-derived `workspace_id`, `get_current_operator` on every route, real `performed_by` everywhere, step-up re-auth hook for approvals (DEC-07-03), auth-event audit (`auth-foundation-design.md`).
Does: verified identity and workspace isolation on every request; the precondition for every other row.
Evidenced by: route-enumeration auth test, R1 grep-clean check, per-mutating-route audit-actor tests, SS-1 route-table-generated isolation tests (ET-1; CG-1/SG-1). Frontend test harness lands with this build item (F-10-01 cost placement).

**C2 — Event / Tool / Notification Foundation** *(reclassified deterministic)*
Exists: transactional outbox, the four missing events, consumer worker, `workspace_notification`, exception data model, `tool_call_log`, PII-sanitising tool serialisation, the declarative tool-guard wrapper + capability-scoped registries (`event-audit-foundation-design.md`, `tool-layer-security-pattern.md`, `tool-contracts.md` — 11 tool contracts).
Does: the reliable event stream, notification surface, exception substrate, and audited tool layer everything else rides on.
Evidenced by: SC-2/SC-3/SS-2/SS-3/SS-4 test sets, forced-failure outbox atomicity test, epoch-labelling fixture test (ET-1); SC-4 design-absence check — no purge mechanism (ET-2).

**C6 — Payroll Readiness Service** *(reclassified deterministic)*
Exists: the existing readiness checks surfaced proactively through C2's notification/work queue.
Does: missing timesheets, missing salary definitions, expiring contracts surfaced before run creation — never presented as an exhaustive pre-flight check.
Evidenced by: standard QA fixtures (ET-1); B4 baseline (3-cycle observation pre-ship, W4) anchoring its time-to-detection claim (ET-6).

**C10 — Structured Confirmation / Pending-Action Protocol** *(reclassified deterministic; built when a write-capable consumer exists)*
Exists (when triggered): the pending-action state machine (proposed → confirmed/rejected/expired; 7-day TTL ceiling, one-live-proposal rule, CAS idempotency, execution-time re-check — DEC-08-08) plus the structured confirmation UI (Stage 09 `confirmation-experience.md`).
Does: makes "AI proposes, human approves" mechanically true; no financial mutation on a natural-language "yes."
Evidenced by: state-machine correctness tests (ET-1); zero-unconfirmed-mutation invariant tests.

**C12 — Statutory-Rule Change Management** *(split from Y1; deterministic)*
Exists: application-level proposal/approval/apply workflow for `statutory_rule`/`tax_band` (correction-by-version-row, DEC-08-09's UNIQUE widening via the standing `/arch-council` gate), step-up re-authenticated approvals, atomic approval records, the platform's first platform-level frontend area (Stage 09 `statutory-approval-experience.md`, C11→C12 one-workflow IA), context-launched CORRECTION run CTA (DQ-005 closed, DEC-11-02).
Does: statutory changes applied through recorded human approval — no developer migration required, no bypass path; the strongest deterministic differentiator in the portfolio.
Evidenced by: CG-12/SG-12 evidence set (ET-1 + ET-3); B5 baseline (retrospective, capturable now) for time-to-apply claims (ET-6). **Pre-build human gate: DQ-007 (+ MFA hard-gate question).**

**C14 — Deterministic Import Validation & Dry-Run** *(reclassified deterministic)*
Exists: dry-run endpoint reusing the real executor path (`run_sequential_payroll`, DEC-08-11) with **no** `payroll_run` row (DQ-004 resolution), workspace-scoped `dry_run_execution` artifact with input-hash commit linkage; schema/tenant/rule validation riding the existing hard-validator.
Does: the hard safety gate for onboarding — dry-run evidence before any commit; claimable before any AI mapping exists.
Evidenced by: dry-run mechanism tests (ET-1); B2/B3 baselines at launch (ET-6); dry-run-pass and client-validated accuracy tracked as two metrics, never collapsed.

### AI assistance capabilities (the five retained)

**C3 — Operator Assistant, Current-State Mode** *(keep, merged: navigation + state explanation + action planning as modes of one assistant)*
Exists: one conversational assistant over the five current-state read tools, PII-stripped, rate-limited, with the current-state-only boundary enforced by refusal behaviour (D-02-03; Stage 09 `assistant-boundary-experience.md`).
Does: "how do I…", "why is [current state] X…", "what do I do for…" — grounded in tool-returned facts only; refuses historical questions and redirects.
Evidenced by: ET-4 eval reports (correct-answer rate on labelled current-state Q&A; ~100% refusal on historical/out-of-scope; zero unsourced facts — refusal-correctness classes per `llm-evaluation-framework.md`); SS-4 session-registry equality test; B6 baseline (4-week tally pre-launch, W3). LLM eval infrastructure lands with this build item.

**C5 — Trace Explanation (`explain_component_trace`)** *(keep, revised)*
Exists: slot-filling narration of `component_trace_jsonb`, with the null-trace refusal specified and a data-access-layer null-guard (Stage 05 gap, closed by the Stage 08 remediation set).
Does: plain-English narration of an already-computed trace for the current run — zero invented numbers, trace shown alongside.
Evidenced by: programmatic zero-hallucination check (every numeric value traces to source JSON) + explicit null-trace refusal tests (ET-1 + ET-4).

**C7 — Input Anomaly Detection** *(split from C6; deterministic detection + optional narration)*
Exists: the layered D-04-01 calibration (absolute thresholds → period-on-period variance; median-ratio test, R_high 3.0 / CRITICAL 10×, min history 3 nonzero periods — DEC-08-12), versioned auditable thresholds, shadow-mode rollout governed by `calibration-governance.md`, resolution through the exception queue (hard gate O4), LLM restricted to narration of already-flagged anomalies.
Does: data-entry errors flagged before they enter a run, with the flagged value and its historical comparison basis shown.
Evidenced by: the three governance metrics from shadow onward (confirmed-error capture, correct-dismissal, later-discovered-unflagged-error); calibration reports (ET-5/ET-6); narration hallucination check if the narration layer ships (ET-4); ET-2 check that no LLM sits in the detection path. GA lags deploy by ≥ 3 cycles + ≥ 20 terminal records (W1).

**C11 — Compliance Monitoring (narrowed)** *(revise: detect/compare/summarise/draft only)*
Exists: scheduled monitoring of the Tier-1 authoritative-source allowlist (DQ-006 — human + professional sign-off precedes build authorisation), deterministic diff against `statutory_rule`, LLM-drafted proposals with full source citations, feeding C12's approval workflow — never writing anything itself (D-02-04).
Does: time-to-detection of statutory changes shrinks from "manual notice" to the policy's monitored cadence — the guarantee exactly as strong as the allowlist and cadence, stated with that boundary.
Evidenced by: CG-11 evidence set; precision (confirmed real changes / total flagged), never volume (D-04-01); citation/provenance completeness per proposal (ET-4); B5 comparison baseline (ET-6).

**C13 — Onboarding Mapping Assistant** *(keep; never ahead of C14)*
Exists: AI-proposed column mapping and salary-definition/grade/designation assignment over the existing `NativeUploadFlow`/`ColumnMappingPanel` components (three consuming surfaces — regression obligation), proposals only, applied through the deterministic Upload/Enroll path after operator confirmation, C14's dry-run as the hard backstop.
Does: messy-spreadsheet onboarding accelerated with every proposal visible against the original header text.
Evidenced by: mapping-accuracy eval on labelled messy spreadsheets (ET-4); improvement claims anchored to B1/B2 — which must be captured on a real onboarding *before* C13 ships (unrecoverable window W2; EG-004 is the scheduling fact).

### Held positions (deliberate, binding)

**C4 — Historical Payroll Explanation**: **blocked** (D-02-03) until F-01-27/29/38 close with regression evidence. No launch evidence is definable while blocked; no narrative assumes it.
**C8 — Reconciliation Investigation**: **blocked** (D-02-02 + D-02-03). Its *remediations* (repo-level reconciliation scoping fix) proceed as plumbing regardless; the capability waits for both preconditions.
**C9 — Trace Agent**: **rejected, permanently** — its intent is covered by C5 (current-run traces) and, once unblocked, C8 (investigation). Design-absence is itself register evidence (ET-2). The end-state contains no "Trace Agent."
**C15 — Email Notifications**: **deferred** until C2's in-app notifications are proven in production; a deterministic delivery extension of C2 when it comes, never an agent.

## 2. What the platform deliberately does not do (end-state boundaries)

- **No AI in calculation, statutory execution, state, mutation, or compliance decisions** — permanent (Principle 1/9; posture P-A).
- **No historical explanation or investigation** until reproducibility preconditions close (D-02-03) — the assistant refuses rather than approximates.
- **No autonomous agents**: the source document's "Phase 2C autonomous" layer is not part of the direction. The most autonomous behaviour at end-state is C11 drafting a proposal for C12's human-approved workflow; every mutation everywhere has a human decision in front of it (C10/C12; Principle 10 — autonomy would have to be *earned and separately decided*, and nothing in the approved portfolio claims it).
- **No write tools for any LLM capability** — writes happen in deterministic workflows (C12, Upload/Enroll, C10-mediated execution); AI proposes only.
- **No usage-volume, detection-volume, or dry-run-equals-accuracy success measures** — measurement prohibitions bind every KPI (D-04-01; `direction-kpis.md`).
- **No multi-operator workflows in v1** — later increment with named triggers; promoted to prerequisite only if DQ-007 resolves to proposer ≠ approver.
- **No multi-tenant SaaS operation absent the human decision bundle** (F-11-01; RR-1 trigger (c)).
- **No operational-reporting capability yet** (opportunity area 15, F-04-06) — later increment; re-enters assessment only after audit-coverage and exception substrate exist (`product-scope-boundaries.md` §2.4).
- **No retention-enforcement mechanism** until DQ-008 resolves (SC-4; O9).

## 3. Reading this map

Dispositions and their conditions are D-03-01-fixed with all 14 approved conditions preserved; readiness and build order live in Stage 05's matrix and the O1–O9/W1–W6 constraint set (`sequencing-economics.md`); Stage 13 sequences. This map says what "arrived" looks like — every row's "evidenced by" is the launch-gate register's "done = row green" rule made concrete.
