# Stage 03 Output: Agent Capability Matrix

**Approved 2026-07-12 (D-03-01, `_core/HUMAN-DECISIONS.md` HD-6) as the reference portfolio for all downstream stages**, replacing the source architecture document's original five-track/named-agent structure for the purposes of this review.

Consolidates Stage 02's 24 fine-grained capability items (`02-product-thesis/outputs/capability-classification-matrix.md`) into 15 portfolio-level capabilities, reviewed at capability level rather than accepting the architecture document's track grouping (per the Stage 03 prompt). Each capability carries the full required-assessment field set.

Portfolio decision legend: **keep** / **revise** / **merge** / **split** / **defer** / **block** / **reject** / **reclassify** (as deterministic platform capability).

---

## C1 — Identity & Auth Foundation
*(was: Track P in full)*

- **Current track/label**: Track P — "Authentication"
- **Target user**: every operator and every downstream agent/tool call
- **User problem**: no verified identity exists today; `performed_by` is hardcoded, `workspace_id` comes from request body
- **Desired outcome**: verified operator identity and workspace isolation on every request
- **Trigger**: N/A — foundational, always active
- **Required authoritative data**: new `operator` table
- **Required tools**: N/A — this *is* infrastructure, not a tool consumer
- **Current-state vs. historical-state**: N/A
- **Deterministic detection/computation required**: entirely deterministic (JWT verify, claims extraction)
- **LLM role**: none
- **Permitted reads/writes**: writes the `operator` table and JWT issuance; not agent-relevant
- **Prohibited actions**: N/A
- **Human decision/approval required**: none — engineering delivery, not a product judgment call
- **Evidence shown to operator**: N/A
- **Failure modes**: auth bypass, token forgery, workspace_id spoofing if `workspace_id` is ever accepted from anywhere but the JWT
- **Platform prerequisites**: none — this is itself the prerequisite for everything else
- **Compliance/control prerequisites**: none beyond standard auth hygiene
- **Evaluation requirement**: standard security testing (Stage 07's remit), not agent evaluation
- **Measurable product outcome**: 100% of routes reject unauthenticated requests; 0 routes accept workspace_id from body
- **Portfolio decision**: **reclassify** — this is deterministic platform engineering, not agent portfolio work. It should not appear on an "agent roadmap" at all.
- **Rationale/confidence**: High confidence. Nothing in Track P involves an LLM anywhere in the document (F-02-03). Framing it under "Agent Foundation" risks mis-scoping conventional auth work as AI-project work.

---

## C2 — Event / Tool / Notification Foundation
*(was: Track V minus the read-only tool contracts, which are reviewed individually in `outputs/tool-portfolio-matrix.md`)*

- **Current track/label**: Track V — "Agent Foundation" (outbox, new events, PII sanitizer, event consumer, notification table)
- **Target user**: indirectly, every future agent; directly, no end user yet
- **User problem**: event store is write-only with no consumer; several state changes (reconciliation MISMATCH, enrollment, status change, input submitted) emit no event at all
- **Desired outcome**: a reliable, complete event stream any future agent can subscribe to, plus a PII-safe tool-serialization contract
- **Trigger**: N/A — infrastructure
- **Required authoritative data**: outbox table, `event_store`, `workspace_notification` table
- **Required tools**: N/A — this builds the substrate tools run on
- **Current-state vs. historical-state**: N/A
- **Deterministic detection/computation required**: fully deterministic (transactional outbox pattern, polling worker)
- **LLM role**: none
- **Permitted reads/writes**: writes new event rows in the same transaction as the state change; no LLM involvement
- **Prohibited actions**: N/A
- **Human decision/approval required**: none — engineering delivery
- **Evidence shown to operator**: N/A directly; this is what later evidence-showing capabilities depend on
- **Failure modes**: single-worker constraint noted by the document itself (no distributed lock in multi-uvicorn deployment) — an engineering risk, not an AI risk
- **Platform prerequisites**: Track P (workspace_id/operator_id must be real before `agent_session_log`/notifications attribute correctly)
- **Compliance/control prerequisites**: none beyond standard data-handling hygiene for the PII-sanitizing serializer
- **Evaluation requirement**: standard integration testing, not agent evaluation
- **Measurable product outcome**: zero missing-event gaps (GAP-3 in the document's own As-Is register); zero silent event loss (GAP-4)
- **Portfolio decision**: **reclassify** — deterministic platform/workflow-automation engineering, not agent capability, same reasoning as C1 (F-02-03).
- **Rationale/confidence**: High. The PII-sanitizing serializer is a rules-based allowlist/denylist, not a model.

---

## C3 — Operator Assistant, Current-State Mode
*(merges: Navigation Guide + State Explainer [current-state only] + Action Planner)*

- **Current track/label**: Track W, three separately-named "modes"
- **Target user**: payroll operator, day-to-day
- **User problem**: operators don't know where to go in the product, don't understand why the *current* run/employee state is what it is, and don't know the right sequence of steps for a situation they haven't handled before
- **Desired outcome**: a single conversational assistant that answers "how do I...", "why is [current state] X...", and "what do I do for..." questions grounded in live workspace data
- **Trigger**: operator-initiated chat message
- **Required authoritative data**: employee/contract/enrollment status (F-01-13/14), run status (F-01-22), current pay-cycle/rule-set config (F-01-10/11)
- **Required tools**: `get_employee`, `get_employees`, `get_payroll_run`, `get_enrollment_status`, `get_salary_definitions` (all current-state facts, per `tool-portfolio-matrix.md`)
- **Current-state vs. historical-state**: **current-state only** — this is the D-02-03 launch boundary. No mode in C3 may answer a question that requires reconstructing what a *past* run did or why.
- **Deterministic detection/computation required**: all underlying facts (status, enrollment, contract dates, cycle/rule config) are deterministically retrieved; the LLM's role is interpreting the natural-language question and composing the narrative from those facts — never inventing a fact not returned by a tool
- **LLM role**: natural-language question interpretation; multi-fact narrative composition; step-sequence suggestion (Action Planner) grounded in current workspace state
- **Permitted reads**: the five tools listed above, PII-stripped
- **Permitted writes**: none
- **Prohibited actions**: reconstructing or asserting facts about a specific past payroll run's outcome; must refuse and redirect (see refusal behavior in `portfolio-boundary-map.md`)
- **Human decision/approval required**: none for read-only current-state Q&A
- **Evidence shown to operator**: names of the tools/facts consulted, surfaced inline (e.g. "based on this employee's current status and contract dates")
- **Failure modes**: hallucinated fact not sourced from a tool call; silently answering a historical question as if it were current; ambiguous tool result (e.g. multiple open contracts, which shouldn't exist per F-01-15's exclusion constraint, but the refusal path should exist regardless)
- **Platform prerequisites**: C1 (auth), C2 (PII-sanitizing tool layer), rate limiting (W3, called out by the source document as "non-negotiable, not deferred")
- **Compliance/control prerequisites**: none beyond standard PII handling
- **Evaluation requirement**: accuracy eval against a labelled set of current-state Q&A pairs; refusal-rate eval for out-of-scope (historical) questions
- **Measurable product outcome**: reduction in support/navigation questions reaching a human; correct refusal rate on historical-question test set
- **Portfolio decision**: **keep, merge** — Navigation Guide, State Explainer's current-state behavior, and Action Planner are recommended as three *modes* of one bounded assistant, not three separate agents (see `portfolio-boundary-map.md` §1).
- **Rationale/confidence**: High. All three modes share the same trigger (operator chat), the same tool set, the same current-state boundary, and the same failure modes — treating them as one assistant avoids duplicated infrastructure and inconsistent refusal behavior across "agents" that are really facets of one conversation.

---

## C4 — Historical Payroll Explanation
*(was: State Explainer's historical mode)*

- **Current track/label**: Track W (State Explainer, historical sub-case)
- **Target user**: payroll operator investigating a past pay period
- **User problem**: "why did employee X get paid Y in March" — requires reconstructing historical truth
- **Desired outcome**: accurate historical explanation, once the platform can guarantee reproducibility
- **Trigger**: operator-initiated chat message about a past run
- **Required authoritative data**: historical `payroll_result`/`component_trace_jsonb`, `salary_definition` state *as of the run date* — currently not fully guaranteed reproducible (F-01-27, F-01-29, F-01-38)
- **Required tools**: none defined yet — blocked before tool design is warranted
- **Current-state vs. historical-state**: historical
- **Deterministic detection/computation required**: N/A until unblocked
- **LLM role**: N/A until unblocked
- **Permitted reads/writes**: N/A
- **Prohibited actions**: must not ship in the initial Track W launch
- **Human decision/approval required**: none — D-02-03 already resolved this as a launch precondition, not a judgment call for this stage to re-open
- **Evidence shown to operator**: N/A until unblocked
- **Failure modes**: a plausible-sounding but factually wrong explanation of a historical outcome affected by F-01-27 (salary_definition edited between the run and the explanation request) or F-01-29 (ambiguous trace-persistence fallback)
- **Platform prerequisites**: F-01-27, F-01-29, F-01-38 must close (Stage 05)
- **Compliance/control prerequisites**: none beyond the reproducibility guarantee itself
- **Evaluation requirement**: once unblocked, historical-accuracy eval against known-good reconstructed cases
- **Measurable product outcome**: N/A until unblocked
- **Portfolio decision**: **block**, per D-02-03
- **Rationale/confidence**: High. Directly decided by the human reviewer in Stage 02; not re-litigated here.

---

## C5 — Trace Explanation (`explain_component_trace`)

- **Current track/label**: Track V tool / Track W feature (Blocking Condition #4 in the source document)
- **Target user**: payroll operator reviewing a specific employee's calculated result within the *current* (already-calculated) run
- **User problem**: `component_trace_jsonb` is a structured but not human-readable breakdown of how gross/net pay was derived
- **Desired outcome**: plain-English narration of an already-computed trace, with zero invented numbers
- **Trigger**: operator requests an explanation for a specific employee's result in a specific run
- **Required authoritative data**: `payroll_result.component_trace_jsonb` for the target run (F-01-28, F-01-29)
- **Required tools**: `get_run_results` (to obtain the trace)
- **Current-state vs. historical-state**: works for a *just-calculated* run's own trace (current-state, since the run being explained is the one just produced, not a historically-reconstructed one) — see distinction from C4 in `portfolio-boundary-map.md` §1
- **Deterministic detection/computation required**: the entire numeric content — the LLM only fills named prose slots from trace values already present, per the source document's own Blocking Condition #4
- **LLM role**: slot-filling prose only, strictly bounded — no arithmetic, no invented values
- **Permitted reads**: `component_trace_jsonb` for the specific run/employee requested
- **Permitted writes**: none
- **Prohibited actions**: introducing any numeric value not present in the trace source (already specified by the document); must not silently degrade to a generic/fabricated explanation when the trace is null
- **Human decision/approval required**: none — this is a specification gap (F-02-07), not a judgment call
- **Evidence shown to operator**: the trace itself, alongside the narration
- **Failure modes**: `component_trace_jsonb` is null (legacy-executor path, F-01-28) — currently unspecified behavior; must be an explicit refusal, not a fabricated explanation
- **Platform prerequisites**: none beyond the trace field being reliably populated by the production (sequential) executor path
- **Compliance/control prerequisites**: none
- **Evaluation requirement**: zero-hallucination eval — every numeric value in output must trace back to the source JSON, checked programmatically
- **Measurable product outcome**: zero instances of a number in the explanation not present in the trace; explicit refusal rate for null-trace cases
- **Portfolio decision**: **keep, revise** — sound design, needs the null-trace refusal behavior specified (F-02-07)
- **Rationale/confidence**: High. This is the one capability in the entire document the authors already designed correctly by constraint (slot-filling); it just needs the missing edge case closed.

---

## C6 — Payroll Readiness Service (deterministic checks + notification/work queue)
*(was: Prep Agent X2, minus the anomaly-detection check, split out as C7)*

- **Current track/label**: Track X2 — "Payroll Prep Agent"
- **Target user**: payroll operator about to create a new run
- **User problem**: missing timesheets, unenrolled employees, and expiring contracts currently surface only if the operator manually checks or the run fails at creation
- **Desired outcome**: proactive surfacing of these three conditions before run creation, as a notification/work queue
- **Trigger**: operator navigates to New Run, or a scheduled/event-driven pre-check
- **Required authoritative data**: `payroll_readiness_service.py`'s existing logic (F-01-19/20), `employee_contract.end_date` (F-01-15)
- **Required tools**: none needed beyond direct service calls — this does not need an LLM tool-calling loop at all
- **Current-state vs. historical-state**: current-state
- **Deterministic detection/computation required**: all three checks (missing timesheets, missing salary definition, contract expiry) are already deterministic today; no new computation needed, only new *surfacing* (notification/work-queue UI) of existing checks
- **LLM role**: **none required** for detection; an optional narration/prioritization layer may summarize a list of already-detected issues in plain English, but is not necessary for the capability to function
- **Permitted reads**: employee/contract/enrollment/timesheet-derivation-status tables (existing service already reads these)
- **Permitted writes**: writes to `workspace_notification` (via C2)
- **Prohibited actions**: none specific — this is low-risk by construction (read-only detection, notification-only output)
- **Human decision/approval required**: none — no financial mutation, no ambiguity to resolve
- **Evidence shown to operator**: the specific employee/condition flagged (name, missing field, or expiry date) — already fully determinable today
- **Failure modes**: stale notification if the underlying condition changes after the notification fires (a UX/timing question, not a correctness question)
- **Platform prerequisites**: C2 (notification layer)
- **Compliance/control prerequisites**: none
- **Evaluation requirement**: standard QA (precision/recall against known readiness-check test fixtures), not an LLM eval — because there is no LLM in the critical path
- **Measurable product outcome**: reduction in run-creation failures due to these three conditions; time-to-detection improvement vs. today's "found at run-creation time" baseline
- **Portfolio decision**: **reclassify** as a deterministic readiness service + notification/work-queue UI. Not an "agent" in any meaningful sense — see investigation §4 rationale.
- **Rationale/confidence**: High. Confirmed directly against Stage 01's evidence that all three checks are already deterministic computations today (F-01-19/20, F-01-15); wrapping them in an "agent" framing adds latency, cost, and a new failure mode for zero functional gain (F-02-04).

---

## C7 — Input Anomaly Detection
*(split out from Track X2's fourth check: "input quantities anomalous vs previous period")*

- **Current track/label**: Track X2 — bundled with C6 in the source document
- **Target user**: payroll operator reviewing submitted payroll inputs before a run
- **User problem**: a data-entry error (e.g. 400 overtime hours instead of 40) currently has no automated flag
- **Desired outcome**: statistically-flagged anomalies surfaced before they enter a run
- **Trigger**: input submission or pre-run check
- **Required authoritative data**: `payroll_input.quantity` history per employee/input_code (F-01-17)
- **Required tools**: none beyond a statistical computation over existing input history
- **Current-state vs. historical-state**: current-state (comparing this period's inputs to recent history)
- **Deterministic detection/computation required**: **yes, as the primary mechanism** — a threshold or z-score rule over quantity history; this is a statistics problem, not a language problem
- **LLM role**: optional — narrating/prioritizing a list of already-flagged anomalies (e.g. "3 unusual entries this period, largest is...") is a reasonable secondary use; the LLM must not be the detector
- **Permitted reads**: `payroll_input` history for the workspace
- **Permitted writes**: none (flags for review only)
- **Prohibited actions**: none specific
- **Human decision/approval required**: threshold-tuning (what counts as "anomalous") is a product/statistics calibration decision, not resolvable from evidence alone — flagged for Stage 04/08
- **Evidence shown to operator**: the flagged value plus the historical comparison basis (e.g. "40 → 400, prior 3-period average 42")
- **Failure modes**: false positives/negatives from threshold miscalibration — a tuning problem, not an architectural one
- **Platform prerequisites**: none beyond existing `payroll_input` data
- **Compliance/control prerequisites**: none
- **Evaluation requirement**: precision/recall against a labelled anomaly test set; if an LLM narration layer is added, a separate hallucination check on the narration
- **Measurable product outcome**: anomalies caught before run creation vs. today's baseline (caught only if a human happens to notice)
- **Portfolio decision**: **split** from C6 (already reflected above) and **keep** as a deterministic-detection-plus-optional-narration capability
- **Rationale/confidence**: Medium-high. The detection mechanism is well-understood (statistical); the calibration question (what threshold) needs a product decision this stage cannot make from evidence alone.

---

## C8 — Reconciliation Investigation
*(was: Track X3, "Reconciliation Investigation Agent")*

- **Current track/label**: Track X3
- **Target user**: payroll operator resolving a reconciliation MISMATCH
- **User problem**: identifying which employee/component caused a MISMATCH currently requires manual inspection
- **Desired outcome**: automatic root-cause identification once unblocked
- **Trigger**: `reconciliation.MISMATCH` event
- **Required authoritative data**: `payroll_reconciliation`, `component_trace_jsonb` — both implicated in blocking decisions (F-01-33/F-02-06 for the data layer, F-01-27/29/38 for historical reproducibility)
- **Required tools**: a future `get_reconciliation` tool — itself blocked (D-02-02)
- **Current-state vs. historical-state**: the run being reconciled has already completed (LOCKED, per F-01-36) by the time MISMATCH fires — this is effectively investigating a completed, not live, run, and depends on the same reproducibility guarantees as C4
- **Deterministic detection/computation required**: **yes, entirely** — the causal diff (which employee, which component, which amount) must be computed deterministically from trace/reconciliation data; the LLM's role, once unblocked, is narration only (F-02-05)
- **LLM role**: narration of a pre-computed diff only, once unblocked
- **Permitted reads/writes**: N/A while blocked
- **Prohibited actions**: must not ship until both D-02-02 (tool scoping) and D-02-03 (reproducibility) are resolved
- **Human decision/approval required**: none — already resolved by D-02-02/D-02-03
- **Evidence shown to operator**: once unblocked, the specific employee/component/amount diff, not just a narrative conclusion
- **Failure modes**: (once unblocked) same as C4 — a wrong causal attribution if reproducibility gaps aren't actually closed; (while blocked) the primary risk is scope creep — someone building this before the preconditions close
- **Platform prerequisites**: F-01-33 (repo-level reconciliation scoping fix), F-01-27/29/38 (reproducibility)
- **Compliance/control prerequisites**: none beyond the above
- **Evaluation requirement**: once unblocked, causal-accuracy eval against known MISMATCH test cases
- **Measurable product outcome**: N/A while blocked
- **Portfolio decision**: **block**, per D-02-02 and D-02-03. Document future design constraints (done above) without treating as launch-ready.
- **Rationale/confidence**: High. Directly decided in Stage 02.

---

## C9 — Trace Agent (X4)

- **Current track/label**: Track X4 — named only in the architecture diagram, no dedicated card in the source document (F-02 capability #17)
- **Target user**: undefined in the source — presumably overlaps with C5/C8's users
- **User problem**: undefined — the document gives this agent a box in a diagram but no specification
- **Desired outcome**: undefined
- **Trigger**: undefined (the diagram shows it downstream of the dispatcher but without a named triggering event, unlike X2/X3)
- **Required authoritative data**: presumably `component_trace_jsonb`, i.e. the same data C5 already serves
- **Required tools**: presumably `explain_component_trace`, i.e. the same tool C5 already uses
- **Current-state vs. historical-state**: ambiguous — undefined in the source
- **Deterministic detection/computation required**: undefined
- **LLM role**: undefined
- **Permitted reads/writes**: undefined
- **Prohibited actions**: undefined
- **Human decision/approval required**: whether to build this as a distinct capability at all (see recommendation)
- **Evidence shown to operator**: undefined
- **Failure modes**: undefined — the biggest risk here is building an undefined "agent" that duplicates C5 and/or the existing run-results/timeline UI (Stage 01 F-01-41, which already has a Timeline tab)
- **Platform prerequisites**: same as C5/C8
- **Compliance/control prerequisites**: none identified
- **Evaluation requirement**: N/A pending a decision on whether this exists at all
- **Measurable product outcome**: N/A
- **Portfolio decision**: **reject** as a standalone capability — **merge** its evident intent into C5 (`explain_component_trace`) for current-run trace explanation, and treat any trace investigation of a *past* run as already covered by C8 (Reconciliation Investigation), which is blocked. Recommend removing "Trace Agent" as a separate named box in any future architecture revision.
- **Rationale/confidence**: Medium — confidence is capped because the source document never defines this capability beyond a diagram label, so this is a recommendation to *not build an undefined thing separately* rather than a rejection of a well-specified proposal. Investigation §1 (Trace Agent vs. State Explainer, Trace Agent vs. existing Timeline UI) supports this.

---

## C10 — Structured Confirmation / Pending Action Protocol
*(was: Track X/2B write-confirmation mechanism)*

- **Current track/label**: cross-cutting Track X/2B requirement, not a named agent
- **Target user**: payroll operator confirming or rejecting a proposed write action
- **User problem**: natural-language "yes" in chat is not adequate confirmation for a financial mutation
- **Desired outcome**: a structured UI component showing exact record/field/new-value, backed by a `pending_action_id` state machine
- **Trigger**: any proactive agent (once any exist) proposing a write
- **Required authoritative data**: whatever record the pending action targets
- **Required tools**: N/A — this is UI/state-machine infrastructure, not an agent
- **Current-state vs. historical-state**: N/A
- **Deterministic detection/computation required**: entirely deterministic — a state machine (proposed → confirmed/rejected/expired) and a UI component
- **LLM role**: none in the confirmation mechanism itself (an upstream agent may have proposed the action, but confirming/executing it is deterministic)
- **Permitted reads/writes**: writes the target record only after explicit structured confirmation
- **Prohibited actions**: executing on a natural-language "yes" alone; auto-expiring without an explicit rule
- **Human decision/approval required**: none — this stage does not fully design the protocol (per the prompt's explicit instruction); the open questions are Stage 08's to resolve (expiry, conflicting pending actions on the same entity, idempotency, invalidation on concurrent state transition — F-02-13)
- **Evidence shown to operator**: the exact record/field/new-value being proposed
- **Failure modes**: a pending action outliving the state of the run it targets (e.g. run becomes LOCKED between proposal and confirmation) — explicitly forwarded to Stage 08, not resolved here
- **Platform prerequisites**: C1 (auth, for who confirmed), C2 (notification, to alert the operator a confirmation is pending)
- **Compliance/control prerequisites**: an audit record of every pending-action proposal/confirmation/rejection (Stage 06 to confirm requirements)
- **Evaluation requirement**: standard state-machine correctness testing, not an LLM eval
- **Measurable product outcome**: zero write mutations executed without structured confirmation
- **Portfolio decision**: **reclassify** as deterministic platform capability (a workflow/state-machine mechanism), not an agent itself — it is what any future write-capable agent depends on.
- **Rationale/confidence**: High.

---

## C11 — Compliance Monitoring (narrowed)
*(was: Track Y1, restricted per D-02-04)*

- **Current track/label**: Track Y1 — "Compliance Monitoring"
- **Target user**: compliance-responsible operator/administrator
- **User problem**: FIRS/PenCom statutory changes must currently be noticed and applied manually via a developer-authored migration
- **Desired outcome**: automated detection of external regulatory changes, comparison against the current `statutory_rule` table, and a drafted proposal for human review
- **Trigger**: scheduled or externally-triggered monitoring check
- **Required authoritative data**: current `statutory_rule`/`tax_band` (F-01-45/46), external regulatory source (undefined provenance — see below)
- **Required tools**: a future `get_statutory_rules` tool (see `tool-portfolio-matrix.md`)
- **Current-state vs. historical-state**: current-state (comparing live rules against current external reality)
- **Deterministic detection/computation required**: the diff against `statutory_rule` is deterministic; interpreting *external* regulatory text for what changed is not — that part is where an LLM may add value, at real risk given the legal stakes
- **LLM role**: summarizing/interpreting external source text and drafting a proposal — **strictly limited to detection, evidence comparison, impact summary, and proposal drafting**, per D-02-04
- **Permitted reads**: `statutory_rule`/`tax_band` (read-only), external regulatory sources
- **Permitted writes**: **none** — must never author, execute, or deploy a migration (D-02-04)
- **Prohibited actions**: authoring, executing, or deploying any production Alembic migration; applying a rate change directly
- **Human decision/approval required**: every proposed rate change requires human review and approval, applied through C12 (a separate mechanism), not through this capability
- **Evidence shown to operator**: the external source citation, the specific diff against current `statutory_rule`, and the drafted proposal — never applied automatically
- **Failure modes**: misinterpreting ambiguous or non-authoritative external source text as an authoritative change (a legal-risk failure mode, forwarded to Stage 06); stale/unreliable external source
- **Platform prerequisites**: C12 must exist for any detected change to actually be applied — otherwise this capability produces proposals with nowhere to go (F-02-12)
- **Compliance/control prerequisites**: external-source trust, freshness, and provenance policy (forwarded to Stage 06/08)
- **Evaluation requirement**: precision/recall on known historical regulatory changes; human-review-acceptance rate of drafted proposals
- **Measurable product outcome**: time-to-detection of a real statutory change vs. today's manual-notice baseline
- **Portfolio decision**: **revise** — retain only detect/compare/summarize/draft; explicitly reject the migration-authoring/execution/deployment scope that was implicit in the original Y1 description
- **Rationale/confidence**: High on the restriction (directly decided, D-02-04); medium on external-source reliability, which needs Stage 06/08 input before this is buildable end-to-end.

---

## C12 — Statutory-Rule Change Management
*(new capability, split from Y1 per D-02-04 — not an AI capability itself)*

- **Current track/label**: not named in the source document at all — a gap this stage's split makes explicit
- **Target user**: compliance-responsible operator/administrator
- **User problem**: today, applying any statutory-rule change requires a developer to write and deploy an Alembic migration (F-01-45) — there is no operator-facing path at all, AI-detected or otherwise
- **Desired outcome**: a structured, human-approved workflow for reviewing and applying a statutory-rule change, independent of how the need for the change was identified
- **Trigger**: any proposed statutory-rule change — from C11's output, or from a human noticing a change independently
- **Required authoritative data**: `statutory_rule`/`tax_band` (F-01-45/46)
- **Required tools**: none requiring an LLM — this is a deterministic approval/application workflow
- **Current-state vs. historical-state**: current-state (applying a new effective-dated rule going forward)
- **Deterministic detection/computation required**: entirely — this is a workflow and data-write mechanism, not a reasoning task
- **LLM role**: none
- **Permitted writes**: new `statutory_rule`/`tax_band` rows, following the existing `(country_code, effective_from)` uniqueness invariant (F-01-45), through an application-level mechanism rather than only a migration
- **Prohibited actions**: bypassing human approval for any rate change
- **Human decision/approval required**: mandatory approval step before any change is applied — by design, not a question this stage needs to resolve
- **Evidence shown to operator**: the proposed change, its source/rationale, and its effective date, before approval
- **Failure modes**: same class of risk as any admin-write capability — needs the same rigor as any other financially-critical mutation path (workspace scoping N/A here since `statutory_rule` is platform-level, not workspace-scoped, per F-01-45's decoupling migration)
- **Platform prerequisites**: none beyond ordinary application development
- **Compliance/control prerequisites**: this *is* a compliance-control mechanism — Stage 06 should own its approval-workflow design
- **Evaluation requirement**: standard QA; no LLM eval needed since no LLM is in this capability's critical path
- **Measurable product outcome**: reduction in time-to-apply a statutory change from "next deployment" to "next approval cycle"
- **Portfolio decision**: **split** out as its own deterministic platform/compliance capability, independent of C11 — per D-02-04
- **Rationale/confidence**: High. Directly follows from D-02-04 and F-01-45/46.

---

## C13 — Onboarding Mapping Assistant
*(was: part of Track Y2 — the genuinely AI-appropriate half)*

- **Current track/label**: Track Y2 — "Onboarding Agent" (bundled with C14 in the source document)
- **Target user**: operator performing bulk employee onboarding via Excel/CSV upload
- **User problem**: arbitrary, human-authored spreadsheet column headers must currently be mapped manually (`NativeUploadFlow`, F-01-13)
- **Desired outcome**: AI-assisted interpretation of messy headers, proposing a column mapping and salary-definition/grade/designation assignment for human confirmation
- **Trigger**: operator uploads a file during onboarding
- **Required authoritative data**: the workspace's existing grade/designation/salary-definition codes (F-01-08, F-01-13) to map against
- **Required tools**: a read-only tool exposing the workspace's current grade/designation/salary-definition catalog
- **Current-state vs. historical-state**: current-state
- **Deterministic detection/computation required**: none for the interpretation step itself — this is the one place in the whole portfolio where the task (fuzzy matching of arbitrary natural-language column headers) is inherently ambiguous and not reducible to a fixed deterministic rule (F-02-10)
- **LLM role**: proposing a column-to-field mapping and a plausible grade/designation/salary-definition assignment, always as a **proposal**, never applied directly
- **Permitted reads**: workspace catalog (grades, designations, salary definitions)
- **Permitted writes**: none — proposals only, applied through the existing deterministic Upload/Enroll mechanism (F-01-13) after human confirmation
- **Prohibited actions**: directly writing `employee`/`employee_contract` rows itself
- **Human decision/approval required**: operator confirms or corrects every proposed mapping before it is applied
- **Evidence shown to operator**: the proposed mapping alongside the original header text, so the operator can see exactly what was matched to what
- **Failure modes**: incorrect mapping proposal — mitigated by requiring confirmation and, per C14, a deterministic dry-run before commit
- **Platform prerequisites**: C14 (the dry-run mechanism) must exist as the safety backstop before this ships
- **Compliance/control prerequisites**: none beyond standard data-handling
- **Evaluation requirement**: mapping-accuracy eval against a labelled set of real-world messy spreadsheets
- **Measurable product outcome**: reduction in manual column-mapping time/errors vs. today's `NativeUploadFlow` baseline
- **Portfolio decision**: **keep, split** from the original Y2 bundle (separated from C14)
- **Rationale/confidence**: High — this is one of the clearest cases in the entire portfolio where AI use is justified (F-02-10).

---

## C14 — Deterministic Import Validation & Dry-Run
*(was: the non-AI half of Track Y2)*

- **Current track/label**: Track Y2 — bundled with C13 in the source document
- **Target user**: same as C13 — operator performing bulk onboarding
- **User problem**: an AI-proposed mapping (C13) needs a hard safety gate before it can affect real payroll data
- **Desired outcome**: schema validation, tenant validation, rule validation, and a dry-run payroll execution that verifies the proposed mapping produces sane results before committing
- **Trigger**: after C13 produces a confirmed mapping, before commit
- **Required authoritative data**: same deterministic validation logic the platform already has for direct uploads (F-01-13, onboarding hard-validator F-01-04)
- **Required tools**: none requiring an LLM
- **Current-state vs. historical-state**: current-state
- **Deterministic detection/computation required**: entirely — schema/tenant/rule validation and payroll execution are exactly the deterministic mechanisms Stage 01 already confirmed exist (F-01-04, F-01-21–39)
- **LLM role**: **none** — this is explicitly the backstop that must not be AI-mediated
- **Permitted reads/writes**: reads the proposed import; writes only after a successful dry-run and explicit commit action
- **Prohibited actions**: committing without a successful dry-run
- **Human decision/approval required**: none beyond the final commit action, which is a normal operator action, not a special approval flow
- **Evidence shown to operator**: dry-run results (e.g. what payroll would look like for the imported cohort) before commit
- **Failure modes**: "dry-run" is currently an undefined mechanism (F-02-10) — does it reuse the real sequential executor/snapshot path, or a separate simulation? This is unresolved and forwarded to Stage 08.
- **Platform prerequisites**: a defined dry-run mechanism (Stage 08 question)
- **Compliance/control prerequisites**: none beyond standard onboarding validation
- **Evaluation requirement**: standard QA; no LLM eval needed
- **Measurable product outcome**: zero bad-mapping commits reaching production payroll data
- **Portfolio decision**: **keep, reclassify** as deterministic platform capability (not agent work) — it is the safety mechanism C13 depends on, not itself AI
- **Rationale/confidence**: High on the split; the dry-run mechanism itself needs Stage 08 definition before this is fully specified.

---

## C15 — Email Notifications
*(was: Track Y3)*

- **Current track/label**: Track Y3
- **Target user**: operator, outside the app
- **User problem**: in-app notifications (C2) are missed if the operator isn't actively in the product
- **Desired outcome**: email delivery of the same notification content
- **Trigger**: same triggers as C2's in-app notifications
- **Required authoritative data**: `workspace_notification` (C2)
- **Required tools**: none requiring an LLM
- **Current-state vs. historical-state**: N/A
- **Deterministic detection/computation required**: entirely — this is an email-delivery extension of C2
- **LLM role**: none
- **Permitted reads/writes**: reads `workspace_notification`, writes to an email queue/service
- **Prohibited actions**: none specific
- **Human decision/approval required**: none
- **Evidence shown to operator**: the notification content itself
- **Failure modes**: standard email-delivery failure modes, not AI-specific
- **Platform prerequisites**: C2, and (per the source document's own stated sequencing) proven in-app notification usage first
- **Compliance/control prerequisites**: none beyond standard email-content hygiene (no PII leakage in email subject lines, etc.)
- **Evaluation requirement**: standard QA
- **Measurable product outcome**: notification open/response rate
- **Portfolio decision**: **defer** (per the source document's own stated sequencing — "deferred until in-app notifications are proven in production") and **reclassify** as a deterministic extension of C2, not a distinct agent capability
- **Rationale/confidence**: High.

---

## Summary: portfolio dispositions

| Capability | Disposition |
|---|---|
| C1 — Identity & Auth Foundation | Reclassify (deterministic platform) |
| C2 — Event/Tool/Notification Foundation | Reclassify (deterministic platform) |
| C3 — Operator Assistant, Current-State Mode | Keep, merge (3 modes → 1 assistant) |
| C4 — Historical Payroll Explanation | Block (D-02-03) |
| C5 — Trace Explanation (`explain_component_trace`) | Keep, revise (null-trace spec needed) |
| C6 — Payroll Readiness Service | Reclassify (deterministic + notification) |
| C7 — Input Anomaly Detection | Split (from C6), keep (deterministic + optional narration) |
| C8 — Reconciliation Investigation | Block (D-02-02 + D-02-03) |
| C9 — Trace Agent (X4) | Reject as standalone; merge intent into C5 |
| C10 — Structured Confirmation Protocol | Reclassify (deterministic platform) |
| C11 — Compliance Monitoring (narrowed) | Revise (detect/compare/propose only) |
| C12 — Statutory-Rule Change Management | Split (new, from Y1), deterministic |
| C13 — Onboarding Mapping Assistant | Keep, split (from Y2) |
| C14 — Deterministic Import Validation & Dry-Run | Keep, reclassify (deterministic), split (from Y2) |
| C15 — Email Notifications | Defer, reclassify (deterministic) |

**Net effect**: of 15 portfolio-level capabilities, 7 are reclassified as deterministic platform/workflow work (C1, C2, C6, C10, C12, C14, plus C15 which is both deferred and reclassified), 2 are blocked pending platform prerequisites (C4, C8), 1 is rejected as a standalone capability (C9), and only 5 remain as genuine AI-assistance capabilities at any stage: C3 (current-state assistant), C5 (trace explanation), C7 (anomaly narration, optional), C11 (compliance detection/drafting, narrowed), C13 (onboarding mapping assistance).
