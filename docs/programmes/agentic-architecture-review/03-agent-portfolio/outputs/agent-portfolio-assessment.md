# Stage 03 Output: Agent Portfolio Assessment

**Status: the 15-capability portfolio below was approved by the human reviewer on 2026-07-12 (D-03-01, `_core/HUMAN-DECISIONS.md` HD-6) as the reference portfolio for all downstream stages, with all 14 conditions in `stage-03-review-decision-prompt.md` preserved unchanged from this document's own analysis.**

## Approach

This stage reviewed the source document's 5 tracks (P, V, W, X, Y) and their ~24 fine-grained capabilities (per Stage 02's classification) at capability level rather than accepting the document's track/agent grouping. The result is a consolidated 15-capability portfolio (`outputs/agent-capability-matrix.md`), a tool-by-tool contract review (`outputs/tool-portfolio-matrix.md`), an overlap/UX/coherence analysis (`outputs/portfolio-boundary-map.md`), and a clear blocked/deferred/rejected register (`outputs/blocked-and-deferred-register.md`).

## Headline result

Of 15 consolidated capabilities:

- **7 reclassified** as deterministic platform/workflow engineering, not agent work: Identity & Auth (C1), Event/Tool/Notification Foundation (C2), Payroll Readiness Service (C6), Structured Confirmation Protocol (C10), Statutory-Rule Change Management (C12, newly named), Deterministic Import Validation & Dry-Run (C14), Email Notifications (C15).
- **2 blocked** pending platform prerequisites already decided in Stage 02: Historical Payroll Explanation (C4, D-02-03), Reconciliation Investigation (C8, D-02-02 + D-02-03).
- **1 rejected** as a standalone capability: Trace Agent (C9) — duplicates Trace Explanation (C5) and existing UI.
- **1 restricted** in scope: Compliance Monitoring (C11) — detect/compare/propose only, per D-02-04.
- **1 deferred**: Email Notifications (C15) — per the source document's own stated sequencing.
- **5 remain as genuine AI-assistance capabilities** at some point in the roadmap: Operator Assistant Current-State Mode (C3), Trace Explanation (C5), Input Anomaly Detection narration (C7, optional), Compliance Monitoring detection/drafting (C11, narrowed), Onboarding Mapping Assistant (C13).

No functional capability described in the source document is dropped — every one is retained, either as AI assistance or correctly reclassified as deterministic engineering. This is a relabeling and precision exercise, not a scope cut.

## Agent boundaries resolved

Three separate "agents" (Navigation Guide, State Explainer, Action Planner) are recommended as one bounded assistant with three modes (C3), sharing tooling, rate limiting, PII handling, and — critically — the same current-state/historical-state refusal boundary. A fourth undefined "agent" (Trace Agent, X4) is rejected outright as duplicating existing capability. Full detail in `outputs/portfolio-boundary-map.md` §1.

## Deterministic-vs-probabilistic responsibility (Stage 02 Principle 9, applied actively)

Every capability in the portfolio was tested against "is an LLM actually necessary here." The result: Prep checks (3 of 4), reconciliation causal diffing, enrollment-status "why" narratives, and dry-run validation are all confirmed to require zero LLM involvement in their core mechanism — the LLM's legitimate role, where one exists, is narration/interpretation layered on top of a deterministic result, never the computation itself. This mirrors the pattern the source document already applies correctly to `explain_component_trace` (Blocking Condition #4); this stage's contribution is applying that same discipline uniformly across the whole portfolio rather than to one tool in isolation.

## Track W launch boundary

Defined explicitly: current-state navigation/explanation/planning is in scope for initial launch; any question requiring reconstruction of a historical payroll outcome is out of scope until Stage 05 closes the reproducibility gaps (F-01-27/29/38). Refusal behavior for five distinct failure conditions (missing facts, historical-reconstruction request, cross-workspace request, ambiguous tool result, null trace) is specified in `outputs/portfolio-boundary-map.md` §3 — not left implicit.

## Tool portfolio

All 10 originally-proposed tools reviewed individually; one (`get_reconciliation`) is blocked outright pending a repository-level fix; all others require independent workspace-ownership verification regardless of the underlying repository function's current correctness — this cannot be assumed, since it was found to be false for `get_reconciliation` specifically. One new tool (a workspace grade/designation/salary-definition catalog reader) is identified as needed for the Onboarding Mapping Assistant (C13) and was not in the original 10.

## UX surface

Chat is recommended as the primary surface for exactly one capability (C3) — the one place open-ended natural-language interaction is the actual product value. Every other retained capability gets a purpose-built surface (readiness panel, exception queue, evidence drawer, comparison view, approval panel, configuration-mapping workspace) rather than defaulting to chat, per the prompt's explicit instruction and Stage 02's Principle 8.

## Portfolio coherence

The revised portfolio covers all seven named operating-model stages (preparation, exception detection, investigation, explanation, decision support, onboarding, compliance) with only two accepted gaps (reconciliation-adjacent exception detection and historical explanation, both explicitly blocked by Stage 02 decisions, not oversights) and two identified missing handoffs (compliance detection→application, anomaly-flagging→resolution) forwarded to Stage 04/09 as design tasks rather than resolved here.

## What this stage does not do

Per the prompt's constraints, this stage does not: design the confirmation protocol fully (only records Stage 08 questions), design the dry-run mechanism (same), perform full Stage 04 outcome discovery (only records newly-noticed opportunities as handoff items), or produce an implementation roadmap. See the four stage handoff documents for what's carried forward to each specific later stage.
