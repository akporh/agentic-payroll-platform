# Stage 03 Output: Portfolio Boundary Map

Covers required investigations §1 (agent boundaries/overlap), §3 (Track W launch boundary detail), §7 (UX/product surface), and §8 (portfolio coherence).

## §1 — Agent boundary and overlap analysis

| Pair named in the prompt | Overlap found | Resolution |
|---|---|---|
| Navigation Guide vs. State Explainer | Both are read-only, tool-mediated, chat-triggered, current-state-grounded. No meaningful boundary between "where do I go" and "why is this the current state" — both are natural-language Q&A over the same underlying facts. | **Merged into C3** (Operator Assistant, Current-State Mode) as two modes of one assistant, not two agents. |
| State Explainer vs. Trace Agent | State Explainer's current-state mode explains *why* (eligibility, enrollment) using facts outside the trace; Trace Agent (X4, undefined) appears to target the *trace* specifically, overlapping heavily with C5 (`explain_component_trace`). | State Explainer's current-state half → C3. Its historical half and any trace-specific narration → C5 (if current-run) or blocked C4/C8 (if historical). Trace Agent (X4) is **rejected as standalone** and merged into C5's intent (see §1 row below). |
| Action Planner vs. Prep Agent | Action Planner responds to an operator's stated intent ("I need to process a mid-month joiner"); Prep Agent (C6) proactively surfaces issues before the operator asks. Different trigger (pull vs. push) but the same underlying facts and the same current-state boundary. | **Not merged** — kept as a mode of C3 (Action Planner, pull-triggered) distinct from C6 (Prep Service, push-triggered/proactive). The distinction is trigger direction, not capability — worth keeping separate for UX reasons (see §7) even though both could share tooling. |
| Prep Agent vs. deterministic readiness validation | Total overlap for 3 of 4 checks — `payroll_readiness_service.py` already computes exactly what Prep Agent's first three checks propose to detect (F-01-19/20). | **Resolved**: C6 reclassified as a thin notification/work-queue layer over the *existing* deterministic service, not a new detection mechanism. No agent needed for this part. |
| Reconciliation Investigation vs. deterministic reconciliation diagnostics | The causal diff X3 proposes to "identify" is itself a deterministic computation over existing trace/reconciliation data (F-02-05) — there is no separate "deterministic reconciliation diagnostics" capability today to overlap with; the overlap is between X3-as-conceived and what X3 *should* be (a thin narration layer over a new deterministic diff function). | **Resolved**: C8's design constraint (once unblocked) requires the diff to be built as a deterministic function first; X3 the "agent" is only the narration layer on top. |
| Trace Agent vs. existing run-results/timeline UI | Stage 01 (F-01-41) confirmed `PayrollResults.tsx` already has a Timeline tab rendering `ExecutionTraceStep[]`, and a Results tab rendering the component trace with an existing `current_fallback` audit-signal icon (F-01-44) — i.e. a working, deterministic UI for exactly what Trace Agent (X4) seems intended to do. | **Resolved**: no gap for X4 to fill beyond what C5 (narration on top of already-displayed trace data) already covers. X4 rejected as redundant (C9 disposition). |
| Compliance Monitoring vs. statutory-rule administration | Y1 as originally described conflated "detect a change" with "apply a change" — there is no existing statutory-rule administration capability at all (F-01-45), so the overlap is actually a **missing capability**, not a duplicated one. | **Resolved by D-02-04**: split into C11 (detection/proposal only) and C12 (a new administration capability, not previously named anywhere). |
| Onboarding Agent vs. deterministic import validation/mapping UI | The existing `NativeUploadFlow` (F-01-13, Stage 01 Cluster B/E) already requires manual column mapping — Y2 proposes automating exactly this step with AI, while the deterministic validation that already exists downstream (onboarding hard-validator, F-01-04) should remain untouched. | **Resolved**: split into C13 (AI mapping proposal, new capability layered *in front of* the existing manual step) and C14 (the existing deterministic validation, extended with a dry-run gate, unchanged in kind). |

## §3 — Track W launch boundary (current-state only)

**In scope for initial launch** (C3, current-state modes):
- Navigation Guide: "how do I do X" — grounded in product navigation facts, no payroll data dependency
- State Explainer, current-state: "why is employee X in/not in the current run", "what is employee X's current status/contract/enrollment" — grounded in `get_employee`, `get_enrollment_status`, `get_payroll_run`
- Action Planner, current-state: "what do I do for situation Y" — grounded in the same current-state facts plus product-navigation knowledge

**Out of scope for initial launch** (blocked, C4):
- Any question requiring reconstruction of a *past* run's outcome or a historical eligibility/contract state as it existed at a prior date

**Per-mode facts and tools required** (also captured in `agent-capability-matrix.md` C3):
| Mode | Facts needed | Tools |
|---|---|---|
| Navigation Guide | Product structure/routes (not payroll data) | none beyond a static navigation map, or none at all if hardcoded |
| State Explainer (current) | employee status, enrollment state, contract window, salary-definition presence, current run status | `get_employee`, `get_enrollment_status`, `get_payroll_run`, `get_salary_definitions` |
| Action Planner (current) | same as State Explainer, plus the workspace's current onboarding/config state (F-01-04) | same, plus a workspace-status-check tool (not in the original 10, needed for accurate step sequencing) |

**Refusal/limitation behavior required**:

| Condition | Required behavior |
|---|---|
| Facts missing (e.g. tool returns empty/null for a required field) | State plainly that the fact is unavailable; do not infer or guess a value |
| Requested answer requires historical reconstruction | Explicit refusal: state that historical explanation is not yet supported, and why (platform limitation, not permission-denial) — do not silently answer using current-state data as if it applied historically |
| Employee/run outside the caller's workspace | Refuse — a 404-equivalent response from the tool layer should propagate as "not found," never as a fabricated answer or a cross-workspace leak |
| Tool result is ambiguous (e.g. an unexpected multiple-match case that the DB's own constraints — F-01-15's active-contract exclusion, for instance — should prevent, but the agent should not assume never happens) | Surface the ambiguity explicitly rather than picking one result silently |
| Relevant trace is null (legacy-executor case, F-01-28) | Explicit refusal for any trace-dependent question, same as C5's requirement |

## §7 — UX/product surface recommendations

Chat is **not** the default surface — per the prompt's explicit instruction and consistent with Stage 02 Principle 8 ("chat is an interface, not the product strategy").

| Capability | Recommended primary surface | Why |
|---|---|---|
| C3 — Operator Assistant, current-state | Chat (floating bubble/panel, as the source document proposes) | This is the one capability where open-ended natural-language interaction is the actual product value — a fixed UI can't anticipate arbitrary "how do I..." phrasing |
| C4 — Historical Payroll Explanation (blocked) | Investigation workspace (once unblocked) — not chat alone; historical explanation needs a structured evidence view, not just prose | A historical claim needs to show its supporting evidence prominently, not bury it in a chat transcript |
| C5 — Trace Explanation | Evidence drawer, attached to the existing Results tab (F-01-41) | Already has a natural home in the current UI; a drawer/expansion on the existing trace row is more discoverable and auditable than a chat answer |
| C6 — Payroll Readiness Service | Readiness panel + notification | This is a checklist, not a conversation |
| C7 — Input Anomaly Detection | Exception queue | A list of flagged items to triage, not a chat |
| C8 — Reconciliation Investigation (blocked) | Investigation workspace (once unblocked) | Same reasoning as C4 — needs structured evidence, not prose alone |
| C9 — Trace Agent | N/A (rejected) | — |
| C10 — Structured Confirmation Protocol | Approval panel (explicitly not chat reply, per the source document's own correct instinct here) | Already correctly specified as non-chat in the source document |
| C11 — Compliance Monitoring | Notification + comparison view (external source vs. current rule) | A diff needs a comparison view, not prose |
| C12 — Statutory-Rule Change Management | Approval panel | Same reasoning as C10 |
| C13 — Onboarding Mapping Assistant | Configuration-mapping workspace (extending the existing `NativeUploadFlow` mapping panel, F-01-13) | Already has a natural home in the existing upload UI |
| C14 — Deterministic Import Validation & Dry-Run | Comparison view (dry-run results vs. expected) | Not a conversation — a validation report |
| C15 — Email Notifications | Notification (external channel) | N/A — not an in-app surface question |

## §8 — Portfolio coherence

Mapping the retained/revised capabilities against the operating-model stages named in the prompt:

| Operating-model stage | Capability coverage | Gaps/observations |
|---|---|---|
| Preparation | C6 (readiness), C7 (anomaly detection) | Well covered; both reclassified as largely deterministic |
| Exception detection | C7, C11 (compliance) | Covered for input anomalies and compliance; **no capability covers reconciliation-adjacent exception detection while C8 is blocked** — this is an accepted gap per D-02-02/03, not an oversight |
| Investigation | C5 (current-run trace), C8 (blocked) | Once C8 unblocks, investigation coverage becomes reasonably complete; until then, investigation is limited to C5's narrower current-run scope |
| Explanation | C3 (current-state), C4 (blocked), C5 | Current-state explanation is well covered; historical explanation is the named, accepted gap |
| Decision support | C3 (Action Planner mode), C11/C12 (compliance approval flow) | Adequate |
| Onboarding | C13, C14 | Well covered, cleanly split between AI-assistance and deterministic safety gate |
| Compliance | C11, C12 | Well covered once C12 (previously unnamed) is built — this was a genuine missing-owner gap in the source document, now named |

**Missing handoffs identified**: 
1. Between C11 (detects/proposes a compliance change) and C12 (applies it) — these must be designed together even though they are separate capabilities, or C11's output has nowhere to go (same issue as F-02-12).
2. Between C13 (proposes a mapping) and C14 (validates it) — must share a common "proposed import" data structure so C14 can validate exactly what C13 proposed, not a re-derived version of it.
3. Between C7 (flags an anomaly) and any human review surface — the exception queue (§7) needs a defined resolution path (dismiss, correct, escalate), not just a display of flagged items. This is a UX detail forwarded to Stage 04/09 rather than resolved here.

**Duplicated responsibility resolved**: Trace Agent (C9) duplicating C5 and the existing Timeline UI (F-01-41) — rejected, see §1.

**Capabilities with no clear owner, now named**: statutory-rule change management (C12) had no owner in the source document at all; this stage's split gives it one (Stage 06, per the C12 disposition).
