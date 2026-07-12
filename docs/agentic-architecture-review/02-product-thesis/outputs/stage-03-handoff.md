# Stage 02 → Stage 03 Handoff

## What Stage 03 is inheriting

The product boundary is **approved** (Stage 02 gate closed 2026-07-12, HD-GATE-02): AI for judgement/investigation/interpretation/coordination, deterministic services for calculations/statutory rules/state transitions/mutation. Stage 03 reviews the individual agent portfolio in detail — this handoff is what to carry in, not what to re-derive. Four binding decisions (D-02-01 through D-02-04, `_core/HUMAN-DECISIONS.md` HD-2–HD-5) constrain Stage 03's scope directly — these are not recommendations Stage 03 may re-weigh, they are decided.

## Binding scope constraints from Stage 02 decisions (apply before scoping any Stage 03 work)

- **D-02-02 (reconciliation scoping)**: `get_reconciliation` (and any tool touching `payroll_reconciliation`) may not be built or shipped until the repository-level workspace-scoping fix (F-01-33) lands. Tool-layer validation is additionally mandatory, as defence in depth, not instead. Stage 03 should treat this tool as **blocked**, not merely flagged.
- **D-02-03 (historical reproducibility)**: **Blocked** until F-01-27/F-01-29/F-01-38 close: Track X's Reconciliation Investigation Agent (X3) and Trace Agent (X4), and any Track W behavior that explains/reconstructs a *historical* payroll outcome. **Not blocked**: Track W's current-state navigation/assistance (Navigation Guide; State Explainer answers about the *current* run/employee state). Stage 03 must design Track W's initial scope to exclude historical-outcome explanation explicitly, not leave the line implicit.
- **D-02-04 (statutory-rule change management)**: Y1 is restricted to detect/compare/propose only — it must never author, execute, or deploy a production Alembic migration. The change-management/application mechanism is a separate deterministic capability Stage 03 should not fold into Y1's scope; if Stage 03 wants to scope that separate capability, it does so as its own deliverable, not as part of "the compliance agent."
- **D-02-01 (document status)**: the source architecture document is still not an approved design. Stage 03 should treat every Track P–Y section as a proposal Stage 03 is reviewing, not a spec to implement as written.

## Required design constraints, by agent/tool

1. **Prep Agent (X2)** — must separate its four checks into a deterministic detection layer (missing timesheets, missing salary definition, contract expiry — all plain queries) and an optional LLM narration/prioritization layer. Only the fourth check (anomalous input quantities) is genuine analytics, and even that should have a deterministic detection rule with the LLM used only for narration. Not blocked by D-02-03 (these are current-state checks, not historical). (F-02-04)

2. **Reconciliation Investigation Agent (X3)** — **blocked outright by D-02-03** until F-01-27/F-01-29/F-01-38 close. Once unblocked: the causal diff (which employee, which component, which amount caused a MISMATCH) must be computed deterministically from `component_trace_jsonb`/`payroll_reconciliation`; the LLM's role is limited to composing the plain-English explanation from that pre-computed result — the same slot-filling pattern already specified for `explain_component_trace`. (F-02-05)

3. **`get_reconciliation` tool (and any tool touching `payroll_reconciliation`)** — **blocked by D-02-02** until the repository-level workspace-scoping fix lands; tool-layer enforcement required in addition, not instead. This is the single highest-severity item in this handoff. (F-01-33 / F-02-06)

4. **`explain_component_trace`** — needs an explicit, specified behavior for when `component_trace_jsonb` is null (the legacy-executor case). Currently unspecified; low likelihood of firing but the failure mode should be defined rather than left implicit. (F-02-07)

5. **Onboarding Agent (Y2)** — well-justified as an AI-assistance capability, not blocked by any Stage 02 decision (it does not touch historical-outcome explanation or reconciliation). Before relying on its "dry-run payroll" safety gate, get a concrete answer from Stage 08 on what "dry-run" means mechanically (does it exercise the real sequential executor/snapshot path, or a separate simulation) — an unverified safety gate is not a safety gate. (F-02-10)

6. **Compliance Monitoring (Y1)** — **restricted by D-02-04**: detect/compare/propose only, never author/execute/deploy a migration. Do not scope the "operator approves, then applies" half as part of Y1 — that is a separate deterministic platform/compliance capability Stage 03 should scope independently if it chooses to scope it at all this stage. (F-02-12)

7. **Structured confirmation protocol (`pending_action_id`, Track X/2B)** — when specified, must explicitly state its interaction with `payroll_run` state transitions: what happens to a pending action if the target run transitions to `APPROVED`/`LOCKED`/`PAID` before the operator confirms. (F-02-13)

8. **State Explainer mode (Track W)** — its tool set must include each individual deterministic fact (status, enrollment, contract window, salary-definition presence) rather than a single pre-packaged "why excluded" tool that would embed unreviewed logic of its own. **Per D-02-03**: scope this mode to current-state facts only at launch; a request to explain a past run's exclusion is historical explanation and is blocked. (F-02-11)

## Principles to apply during agent-by-agent review

All 10 original candidate principles, plus the newly proposed #11 (independent workspace-scoping enforcement per tool) — see `outputs/non-negotiable-product-principles.md`. Principle #9 ("AI should not be used where deterministic software is sufficient") should be applied as an active test during Stage 03, not just cited — the capability classification matrix already found 10 of 24 proposed capabilities fail this test as currently scoped. Principles #3 and #7 now carry decided, non-negotiable launch preconditions (D-02-02, D-02-03) rather than open questions — treat them as gates, not discussion points.

## What Stage 03 does NOT need to re-derive

- The overall boundary soundness assessment (done, see `product-thesis-assessment.md`) — Stage 03 can proceed from "the boundary is sound," and focus on whether each individual agent honors it.
- Capability classification for the 24 items already classified in `capability-classification-matrix.md` — reuse, don't redo.
- The general platform-trustworthiness cross-check against Stage 01 — already narrowed to the three findings that materially matter at the thesis level (F-02-06, F-02-09, F-02-12); the other seven areas from the prompt are real but agent-design-level, not thesis-level, concerns and are listed in `product-thesis-assessment.md` §5 for Stage 03 to pick up directly.

## Compliance questions forwarded to Stage 06

- F-02-12 / D-02-04: statutory-rule change management is now decided to be a separate deterministic platform/compliance capability — Stage 06 should design/own the review-and-approval workflow itself (how any statutory rate change, AI-detected or human-detected, is reviewed, approved, and applied), given Y1 is now explicitly barred from applying changes itself.
- F-02-02 / D-02-01: the architecture document's "NEEDS REVISION" status is confirmed still open by the human reviewer — Stage 06 does not need to separately chase this; it's resolved (this review is the formal revision path).

## Platform-readiness dependencies forwarded to Stage 05

- F-02-06 / D-02-02 (reconciliation workspace scoping) — now a **named precondition**, not an open question: the repository-level fix must land before `get_reconciliation` exists as a tool.
- F-02-09 / D-02-03 (historical reproducibility gaps: F-01-27, F-01-29, F-01-38) — now a **named launch precondition** for Track X investigation agents and Track W's historical-explanation mode.
- F-02-12 / D-02-04 (statutory-rule change-management mechanism) — now decided to be its own deterministic capability; Stage 05 should assess what it takes to build, independent of Y1.
- The seven platform-trustworthiness areas named in the Stage 02 prompt but found not to be thesis-level blockers (parallel configuration entry points, silent employee exclusion, sequential/legacy executor divergence, snapshot completeness, retry behaviour, audit coverage, frontend/backend mismatches) — all previously confirmed in Stage 01, relevant to Stage 05's full readiness review.
