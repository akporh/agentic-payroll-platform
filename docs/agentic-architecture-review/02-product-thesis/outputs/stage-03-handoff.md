# Stage 02 → Stage 03 Handoff

## What Stage 03 is inheriting

The product boundary is approved-in-principle (pending your gate review): AI for judgement/investigation/interpretation/coordination, deterministic services for calculations/statutory rules/state transitions/mutation. Stage 03 reviews the individual agent portfolio in detail — this handoff is what to carry in, not what to re-derive.

## Required design constraints, by agent/tool

1. **Prep Agent (X2)** — must separate its four checks into a deterministic detection layer (missing timesheets, missing salary definition, contract expiry — all plain queries) and an optional LLM narration/prioritization layer. Only the fourth check (anomalous input quantities) is genuine analytics, and even that should have a deterministic detection rule with the LLM used only for narration. (F-02-04)

2. **Reconciliation Investigation Agent (X3)** — the causal diff (which employee, which component, which amount caused a MISMATCH) must be computed deterministically from `component_trace_jsonb`/`payroll_reconciliation`; the LLM's role is limited to composing the plain-English explanation from that pre-computed result — the same slot-filling pattern already specified for `explain_component_trace`. (F-02-05)

3. **`get_reconciliation` tool (and any tool touching `payroll_reconciliation`)** — must independently enforce workspace scoping at the tool-serialization layer. Do not build this as a thin wrapper over the existing repository functions; Stage 01 confirmed those functions have no workspace-scoping check at all (F-01-33 / F-02-06). This is the single highest-severity item in this handoff.

4. **`explain_component_trace`** — needs an explicit, specified behavior for when `component_trace_jsonb` is null (the legacy-executor case). Currently unspecified; low likelihood of firing but the failure mode should be defined rather than left implicit. (F-02-07)

5. **Onboarding Agent (Y2)** — well-justified as an AI-assistance capability. Before relying on its "dry-run payroll" safety gate, get a concrete answer from Stage 08 on what "dry-run" means mechanically (does it exercise the real sequential executor/snapshot path, or a separate simulation) — an unverified safety gate is not a safety gate. (F-02-10)

6. **Compliance Monitoring (Y1)** — do not scope this as a near-term deliverable. Its "operator approves, then applies" half has no product mechanism today (statutory-rule changes are migration-only, F-01-45/46). Recommend treating "statutory-rule change-management workflow" as its own deliverable, independent of whether Y1's AI-detection half is ever built. (F-02-12)

7. **Structured confirmation protocol (`pending_action_id`, Track X/2B)** — when specified, must explicitly state its interaction with `payroll_run` state transitions: what happens to a pending action if the target run transitions to `APPROVED`/`LOCKED`/`PAID` before the operator confirms. (F-02-13)

8. **State Explainer mode (Track W)** — its tool set must include each individual deterministic fact (status, enrollment, contract window, salary-definition presence) rather than a single pre-packaged "why excluded" tool that would embed unreviewed logic of its own. (F-02-11)

## Principles to apply during agent-by-agent review

All 10 original candidate principles, plus the newly proposed #11 (independent workspace-scoping enforcement per tool) — see `outputs/non-negotiable-product-principles.md`. Principle #9 ("AI should not be used where deterministic software is sufficient") should be applied as an active test during Stage 03, not just cited — the capability classification matrix already found 10 of 24 proposed capabilities fail this test as currently scoped.

## What Stage 03 does NOT need to re-derive

- The overall boundary soundness assessment (done, see `product-thesis-assessment.md`) — Stage 03 can proceed from "the boundary is sound," and focus on whether each individual agent honors it.
- Capability classification for the 24 items already classified in `capability-classification-matrix.md` — reuse, don't redo.
- The general platform-trustworthiness cross-check against Stage 01 — already narrowed to the three findings that materially matter at the thesis level (F-02-06, F-02-09, F-02-12); the other seven areas from the prompt are real but agent-design-level, not thesis-level, concerns and are listed in `product-thesis-assessment.md` §5 for Stage 03 to pick up directly.

## Compliance questions forwarded to Stage 06

- F-02-12 (Y1): statutory-rule change management has no current application mechanism — a compliance-controls question about how any statutory rate change (AI-detected or human-detected) should be reviewed, approved, and applied.
- F-02-02: the architecture document's "NEEDS REVISION" status and unclear resolution history — Stage 06 may want to confirm this doesn't reflect an unresolved compliance objection.

## Platform-readiness dependencies forwarded to Stage 05

- F-02-06 (reconciliation workspace scoping)
- F-02-09 (historical reproducibility gaps: F-01-27, F-01-29, F-01-38)
- F-02-12 (statutory-rule change-management mechanism)
- The seven platform-trustworthiness areas named in the Stage 02 prompt but found not to be thesis-level blockers (parallel configuration entry points, silent employee exclusion, sequential/legacy executor divergence, snapshot completeness, retry behaviour, audit coverage, frontend/backend mismatches) — all previously confirmed in Stage 01, relevant to Stage 05's full readiness review.
