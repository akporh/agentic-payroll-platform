# Stage 03: Agent Portfolio — Findings

Schema per the Stage 03 prompt: current implementation / proposed design / observed overlap-gap-misclassification / consequence / evidence / confidence / recommendation / required human decision / downstream dependency. Full per-capability and per-tool detail lives in `outputs/agent-capability-matrix.md` and `outputs/tool-portfolio-matrix.md` — findings here are the consequential, evidence-backed conclusions, not a restatement of every field.

Per the prompt's finding-discipline instruction, no artificial human decisions are created where evidence and the inherited D-02-01–04 principles already resolve the issue — most findings below carry **no required human decision**, by design.

---

## Draft Findings

_None — every observation below reached a confirmed disposition, backed by Stage 01/02 evidence and/or a binding Stage 02 decision._

---

## Confirmed Findings

### F-03-01: Navigation Guide, State Explainer (current-state), and Action Planner are one assistant, not three agents
- **Current implementation**: N/A — not built.
- **Proposed design**: the source document names these as three separate "modes" under Track W, sharing one chat surface but described individually.
- **Observed overlap/gap/misclassification**: all three share the same trigger class (operator chat), the same read-only tool set, and the same current-state boundary (D-02-03). The only functional difference is question *type* (navigation vs. explanation vs. planning), not underlying mechanism.
- **Consequence**: treating them as three agents would triplicate infrastructure (rate limiting, PII stripping, refusal behavior) that should be shared, and risks inconsistent refusal behavior for the same historical-question boundary across "agents" that are really one conversation.
- **Evidence**: `docs/architecture/agent-layer-architecture.html:848-952`; Stage 01 F-01-13, F-01-14, F-01-19, F-01-20; Stage 02 F-02-11
- **Confidence**: High
- **Recommendation**: merge into one capability (C3, "Operator Assistant, Current-State Mode") with three internal modes.
- **Required human decision**: none.
- **Downstream dependency**: Stage 08 (single implementation), Stage 09 (single UX surface).

### F-03-02: Trace Agent (X4) is an undefined capability that duplicates C5 and existing UI
- **Current implementation**: N/A.
- **Proposed design**: named only in the source document's Track X architecture diagram, with no dedicated specification card (unlike X2/X3).
- **Observed overlap/gap/misclassification**: its evident purpose overlaps entirely with `explain_component_trace` (for current-run trace explanation, C5) and with the existing Timeline/Results tabs in `PayrollResults.tsx` (Stage 01 F-01-41, F-01-44), which already render trace and reconciliation-audit signals deterministically.
- **Consequence**: building this as a fourth separate agent would duplicate existing UI and C5's function with no defined incremental value, and risks inconsistent explanation behavior between two capabilities doing the same thing.
- **Evidence**: `docs/architecture/agent-layer-architecture.html:963-1012` (diagram only, no card); Stage 01 F-01-41, F-01-44
- **Confidence**: Medium (capped because the source is undefined, not because the merge recommendation is uncertain)
- **Recommendation**: reject as a standalone capability; if a future stage identifies a genuine gap C5 and the existing UI don't cover, re-propose it specifically rather than resurrecting the undefined name.
- **Required human decision**: none.
- **Downstream dependency**: Stage 12 (should not appear in the target architecture as a separate named agent).

### F-03-03: Three of Prep Agent's four checks are already fully deterministic and require no new detection logic
- **Current implementation**: `payroll_readiness_service.py` already computes missing-salary-definition detection (F-01-19/20); contract expiry is a plain date comparison against `employee_contract.end_date` (F-01-15); missing-timesheet detection is likewise a set-membership query.
- **Proposed design**: Track X2 bundles all four checks (including anomaly detection) as output of one "Prep Agent."
- **Observed overlap/gap/misclassification**: total overlap between 3 of 4 proposed "agent" checks and an existing deterministic service — this is a reclassification case (Stage 02 F-02-04, confirmed at capability-design level in this stage).
- **Consequence**: if built as an LLM-driven agent evaluating all four conditions itself, three 100%-reliable database queries would be converted into a probabilistic natural-language judgement — strictly worse reliability for no benefit.
- **Evidence**: Stage 01 F-01-19, F-01-20, F-01-15; Stage 02 F-02-04
- **Confidence**: High
- **Recommendation**: reclassify as C6 (Payroll Readiness Service — deterministic checks + notification/work-queue UI); split the fourth (anomaly) check into C7.
- **Required human decision**: none.
- **Downstream dependency**: Stage 08 (implementation as conventional service, not agent).

### F-03-04: Input anomaly detection is a statistics problem; LLM narration is optional, not the detection mechanism
- **Current implementation**: `payroll_input.quantity` history exists per employee/input_code (F-01-17), but no anomaly-flagging mechanism exists today.
- **Proposed design**: bundled into Prep Agent (X2) as its fourth check, with no distinction from the other three deterministic checks.
- **Observed overlap/gap/misclassification**: this check is genuinely different in kind from the other three (F-02-04) — it requires a statistical rule (threshold/z-score), not a boolean condition, but the document doesn't distinguish it.
- **Consequence**: without separating this from the deterministic checks, the whole Prep Agent risks being built as one undifferentiated LLM-driven pipeline, when only this one check has any plausible LLM-relevant role (optional narration on top of a statistical detector).
- **Evidence**: Stage 01 F-01-17; Stage 02 F-02-04
- **Confidence**: Medium-high (detection mechanism is clear; calibration threshold is a product decision, not resolvable from evidence)
- **Recommendation**: split out as C7; require deterministic/statistical detection as the primary mechanism, LLM narration as optional.
- **Required human decision**: threshold/calibration policy — forwarded to Stage 04/08, not resolved here (not a Stage 03-appropriate decision; it needs product/statistical input, not evidence review).
- **Downstream dependency**: Stage 04 (outcome framing), Stage 08 (mechanism design).

### F-03-05: Reconciliation Investigation Agent's causal diff must be deterministic; this is now a decided design constraint, not an open question
- **Current implementation**: `component_trace_jsonb` already contains the structured data needed to compute a causal diff deterministically (Stage 01 F-01-28/29).
- **Proposed design**: X3 "identifies" the causal employee/component — ambiguous between LLM-computed and LLM-narrated, per Stage 02 F-02-05.
- **Observed overlap/gap/misclassification**: none remaining — Stage 02's ambiguity is resolved by this stage's design constraint (deterministic diff, LLM narrates only), consistent with the same pattern already correctly applied to `explain_component_trace`.
- **Consequence**: if this constraint isn't enforced when C8 eventually unblocks, the same failure mode Blocking Condition #4 was written to prevent for trace explanation would recur in reconciliation investigation.
- **Evidence**: Stage 01 F-01-28, F-01-29; Stage 02 F-02-05
- **Confidence**: High
- **Recommendation**: record as a binding design constraint for C8, to apply once D-02-02/D-02-03 preconditions clear.
- **Required human decision**: none — already resolved by the slot-filling pattern's precedent and D-02-03's blocking decision.
- **Downstream dependency**: Stage 08 (mechanism design, once unblocked).

### F-03-06: `get_reconciliation` and any tool touching `payroll_reconciliation` must not be built before the repository-level fix lands
- **Current implementation**: `payroll_reconciliation` repository functions scope solely by `payroll_run_id`, with no workspace check (Stage 01 F-01-33).
- **Proposed design**: `get_reconciliation` is listed as one of the document's 10 core read-only tools.
- **Observed overlap/gap/misclassification**: none — this is a direct, decided blocker (D-02-02), not a new ambiguity this stage introduces.
- **Consequence**: if built as a thin wrapper today, an agent authenticated to Workspace A could retrieve reconciliation data belonging to Workspace B.
- **Evidence**: Stage 01 F-01-33; Stage 02 F-02-06; `_core/HUMAN-DECISIONS.md` HD-3
- **Confidence**: High
- **Recommendation**: block tool construction until the repository-level fix lands; require independent tool-layer verification in addition once built.
- **Required human decision**: none — already resolved (D-02-02).
- **Downstream dependency**: Stage 05 (repo fix), Stage 07 (tool-layer verification).

### F-03-07: Every tool in the portfolio needs independent workspace-ownership verification — this is not limited to `get_reconciliation`
- **Current implementation**: Stage 01 confirmed workspace scoping is present on most, but not all, domain tables/queries (F-01-03, F-01-33).
- **Proposed design**: the source document states "workspace_id from JWT only... every tool call scoped" as a blanket security invariant, without specifying an implementation-level check per tool.
- **Observed overlap/gap/misclassification**: the invariant is stated once, generally; the actual enforcement mechanism needs to be verified tool-by-tool, since "the query already scopes correctly" cannot be assumed as a blanket fact (confirmed false for at least one case).
- **Consequence**: any future tool built as a thin wrapper over an as-yet-unaudited repository function risks silently inheriting a scoping gap, the same way `get_reconciliation` would have.
- **Evidence**: Stage 01 F-01-03, F-01-33; Stage 02 F-02-06, Principle 11
- **Confidence**: High
- **Recommendation**: require independent workspace-ownership verification as a mandatory, per-tool checklist item — captured in `outputs/tool-portfolio-matrix.md`'s cross-cutting requirements.
- **Required human decision**: none — Principle 11 already establishes this as a standing rule.
- **Downstream dependency**: Stage 07 (security review of each tool as built), Stage 08 (implementation pattern).

### F-03-08: `get_enrollment_status` and any similar tool should return facts, not a pre-packaged conclusion
- **Current implementation**: N/A — not built; Stage 01 confirmed the underlying facts (status, enrollment state, contract window, salary-definition presence) are each independently queryable today (F-01-13, F-01-14, F-01-15).
- **Proposed design**: the document lists `get_enrollment_status` without specifying whether it returns raw facts or a synthesized "enrolled/not enrolled + why" conclusion.
- **Observed overlap/gap/misclassification**: if it returns a canned "why" conclusion, that conclusion embeds unreviewed logic inside a "tool" (nominally deterministic) rather than making the LLM responsible for (and accountable for) composing the explanation from visible facts, undermining Principle 4 (generated explanations must link to evidence).
- **Consequence**: an operator asking "why isn't Adaobi in this run" would receive an explanation whose reasoning chain isn't inspectable, since it would live inside opaque tool logic rather than the LLM's visible reasoning over retrieved facts.
- **Evidence**: Stage 01 F-01-13, F-01-14, F-01-15; Stage 02 F-02-11, Principle 4
- **Confidence**: Medium-high
- **Recommendation**: revise `get_enrollment_status` to return the individual facts; the "why" narrative is C3's job, composed from those facts.
- **Required human decision**: none.
- **Downstream dependency**: Stage 08 (tool contract design).

### F-03-09: Compliance Monitoring (Y1) is buildable for detect/compare/propose today; its output has nowhere to go until C12 exists
- **Current implementation**: statutory-rule maintenance is migration-only, no admin route or UI (Stage 01 F-01-45/46).
- **Proposed design**: Y1 "proposes migration... requires operator approval" — implying an application mechanism that doesn't exist.
- **Observed overlap/gap/misclassification**: D-02-04 already resolved the scope question (Y1 restricted to detect/compare/propose); the remaining gap is that C12 (the application mechanism) is a new, previously-unnamed capability this stage had to invent an owner for.
- **Consequence**: Y1 could technically ship its detection/proposal half in isolation, but would produce proposals an operator has no structured way to act on, defeating the purpose.
- **Evidence**: Stage 01 F-01-45, F-01-46; Stage 02 F-02-12; `_core/HUMAN-DECISIONS.md` HD-5
- **Confidence**: High
- **Recommendation**: sequence C11 and C12 together, even though they are separate capabilities/owners.
- **Required human decision**: none on the restriction itself (decided); sequencing priority is forwarded to Stage 11.
- **Downstream dependency**: Stage 06 (C12 design ownership), Stage 11 (sequencing).

### F-03-10: Onboarding Agent (Y2) splits cleanly into a genuinely AI-appropriate mapping-assistance capability and a deterministic safety-gate capability
- **Current implementation**: `NativeUploadFlow` already requires manual column mapping (Stage 01 F-01-13); dry-run payroll execution does not exist as a named mechanism.
- **Proposed design**: Y2 bundles messy-Excel interpretation, column mapping, salary-definition-assignment proposal, and dry-run verification as one "agent."
- **Observed overlap/gap/misclassification**: the interpretation/mapping half is inherently ambiguous (genuinely AI-appropriate, Stage 02 F-02-10); the dry-run/validation half is exactly the kind of deterministic safety mechanism that must not be AI-mediated (Stage 02 Principle 1/9).
- **Consequence**: bundling them risks either under-specifying the dry-run's reliability (since it's presented as part of an "AI agent" rather than a hard deterministic gate) or under-using AI where it would genuinely help (mapping).
- **Evidence**: Stage 01 F-01-13; Stage 02 F-02-10
- **Confidence**: High
- **Recommendation**: split into C13 (AI mapping assistant) and C14 (deterministic validation + dry-run); require C14 to exist as C13's hard backstop before C13 ships.
- **Required human decision**: none.
- **Downstream dependency**: Stage 08 (dry-run mechanism definition — what exactly "dry-run" means mechanically is still an open Stage 08 question, carried from Stage 02 F-02-10).

### F-03-11: Tracks P and most of Track V are deterministic platform engineering with zero LLM involvement, mislabeled by association with "Agent Foundation"
- **Current implementation**: none of Track P/V exists yet (Stage 01 found no JWT auth, no operator table).
- **Proposed design**: labeled "Agent Foundation" (Track V) and grouped in the same phase-timeline as the AI-bearing tracks.
- **Observed overlap/gap/misclassification**: no LLM call, prompt, or model reference appears anywhere in either track's content (confirmed by direct read, Stage 02 F-02-03).
- **Consequence**: risk is organizational (mis-scoping/mis-staffing conventional backend engineering as an AI initiative), not technical.
- **Evidence**: `docs/architecture/agent-layer-architecture.html:643-846`; Stage 02 F-02-03
- **Confidence**: High
- **Recommendation**: reclassify C1/C2 as deterministic platform capabilities; scope and staff as conventional backend engineering.
- **Required human decision**: none.
- **Downstream dependency**: Stage 11 (sequencing/staffing implications).

### F-03-12: The confirmation/pending-action protocol is itself deterministic infrastructure, not an agent — and several specification questions remain genuinely open
- **Current implementation**: N/A — not built.
- **Proposed design**: `pending_action_id` + structured UI, explicitly required before any Phase 2B sprint planning (per the source document's own pre-condition).
- **Observed overlap/gap/misclassification**: the mechanism itself involves no LLM reasoning (a state machine + UI component); the open questions (expiry, conflicting pending actions, idempotency, invalidation on concurrent `payroll_run` state transition) were already flagged in Stage 02 (F-02-13) and remain unresolved — appropriately, since the source document itself treats this as a pre-condition to specify later, not a gap to silently paper over.
- **Consequence**: none yet — this is a specification task, not a defect, provided it's resolved before any write-capable agent (C11/C12, once they involve writes; today they don't beyond the approval-workflow context) ships.
- **Evidence**: Stage 01 F-01-37, F-01-39; Stage 02 F-02-13
- **Confidence**: High
- **Recommendation**: reclassify as deterministic platform capability (C10); forward the specification questions to Stage 08 unchanged.
- **Required human decision**: none — this stage is explicitly instructed not to fully design the protocol.
- **Downstream dependency**: Stage 08 (full specification).

### F-03-13: Track W's historical-explanation boundary (D-02-03) requires an explicit refusal design, not an implicit absence
- **Current implementation**: N/A — not built.
- **Proposed design**: the source document doesn't distinguish current-state from historical-state Q&A within State Explainer at all.
- **Observed overlap/gap/misclassification**: without an explicit refusal design, a naive implementation could silently answer a historical question using current-state data as if it applied historically — a correctness failure, not merely a missing-feature gap.
- **Consequence**: an operator could receive a confidently-stated but potentially wrong historical claim from a capability that was only ever verified for current-state accuracy.
- **Evidence**: Stage 02 D-02-03 (`_core/HUMAN-DECISIONS.md` HD-4); Stage 01 F-01-27, F-01-29, F-01-38
- **Confidence**: High
- **Recommendation**: require explicit historical-question detection and refusal as part of C3's initial launch scope, not an assumed absence.
- **Required human decision**: none — the boundary itself is decided; only the refusal-UX detail is a design task for Stage 08/09.
- **Downstream dependency**: Stage 08 (refusal-detection mechanism), Stage 09 (refusal-message UX).

### F-03-14: The portfolio, once revised, still has a genuine coherence gap between compliance detection and compliance application (C11/C12), and between anomaly flagging and its resolution path (C7)
- **Current implementation**: N/A for both — neither capability exists.
- **Proposed design**: the source document treats Y1 as self-contained; it does not address what happens after an anomaly (X2's fourth check) is flagged.
- **Observed overlap/gap/misclassification**: two missing handoffs, distinct from the blocked/rejected findings above — these are gaps in an otherwise-coherent portfolio, not disqualifying flaws.
- **Consequence**: without a defined resolution path, flagged anomalies could accumulate with no operator workflow to act on them, and compliance proposals could similarly stall.
- **Evidence**: `outputs/portfolio-boundary-map.md` §8
- **Confidence**: Medium (these are UX/workflow design gaps, not evidence-verifiable facts)
- **Recommendation**: Stage 04/09 should define the resolution workflow for C7's exception queue and confirm C11→C12's handoff is designed as one combined workflow even though they remain separate capabilities.
- **Required human decision**: none — a design task, not a decision needing evidence adjudication.
- **Downstream dependency**: Stage 04 (outcome framing), Stage 09 (UX design).

### F-03-15: `explain_component_trace` needs an explicit null-trace refusal behavior before it can be considered launch-ready
- **Current implementation**: the legacy calculation executor sets `component_trace_jsonb = null` and is reachable (though not currently observed to fire) code (Stage 01 F-01-28).
- **Proposed design**: the source document's slot-filling constraint (Blocking Condition #4) doesn't address the null case.
- **Observed overlap/gap/misclassification**: a specification gap, not a contradiction — carried forward unchanged from Stage 02 F-02-07, now with a concrete required fix (explicit refusal, not silent degradation).
- **Consequence**: low likelihood given the legacy path isn't currently exercised, but the failure mode (a trace-explaining tool given no trace) is unspecified and should not be left implicit before this capability ships.
- **Evidence**: Stage 01 F-01-24, F-01-28; Stage 02 F-02-07
- **Confidence**: High
- **Recommendation**: specify explicit refusal behavior for null `component_trace_jsonb` as part of C5's launch-readiness criteria.
- **Required human decision**: none.
- **Downstream dependency**: Stage 08 (implementation).

### F-03-16: The revised portfolio removes "agent" framing from the majority of proposed capabilities without reducing the platform's actual functional scope
- **Current implementation**: N/A — portfolio-level synthesis.
- **Proposed design**: the source document frames all 5 tracks (P–Y) as part of one "Agent Layer."
- **Observed overlap/gap/misclassification**: of 15 consolidated capabilities, 7 are reclassified as deterministic platform/workflow work, 2 are blocked, 1 is rejected as standalone, and only 5 remain as genuine AI-assistance capabilities at any point in the roadmap (`agent-capability-matrix.md` summary table).
- **Consequence**: this is a positive finding, not a criticism of scope — every functional capability the source document described is retained in the revised portfolio (as either an AI capability or a reclassified deterministic one); nothing described as valuable to the operator is dropped, only relabeled to match what it actually is.
- **Evidence**: `outputs/agent-capability-matrix.md` (full matrix and summary table)
- **Confidence**: High
- **Recommendation**: adopt the revised 15-capability portfolio as the reference structure for Stage 04 (outcome discovery), Stage 11 (commercial framing), and Stage 12 (target direction) — not the source document's original 5-track/named-agent structure.
- **Required human decision**: none — this is the stage's own synthesis, offered as a recommendation for later stages to adopt or challenge, not a claim requiring separate human sign-off beyond the stage gate itself.
- **Downstream dependency**: Stage 04, Stage 11, Stage 12.

---

## Parked / Rejected

### P-03-1: Whether to build a dedicated "why unenrolled" narrative-conclusion tool
- **Reason parked/rejected**: rejected in favor of the facts-only design (F-03-08) — recorded here only to make explicit that the alternative (a conclusion-returning tool) was considered and declined, not merely absent from discussion.

## Cross-references for later stages

- Stage 04 (Outcome Discovery): F-03-04 (anomaly-threshold calibration), F-03-14 (exception-queue resolution workflow, compliance handoff) — new outcome opportunities to expand, not resolved here.
- Stage 05 (Platform Readiness): F-03-06 (`get_reconciliation` repo-level fix), C4/C8 unblock conditions (`outputs/blocked-and-deferred-register.md`).
- Stage 06 (Compliance & Controls): F-03-09 (C12 ownership and design), external-source trust/freshness/provenance for C11 (`outputs/stage-06-handoff.md`).
- Stage 07 (Security & Identity): F-03-06, F-03-07 (per-tool workspace-ownership verification).
- Stage 08 (Technical Architecture): F-03-04 (anomaly mechanism), F-03-05 (reconciliation diff mechanism), F-03-08 (tool contract revision), F-03-10 (dry-run mechanism), F-03-12 (confirmation protocol specification), F-03-13, F-03-15.
- Stage 09 (Human Experience): F-03-01 (single assistant UX), F-03-13 (refusal UX), F-03-14 (exception-queue UX), `outputs/portfolio-boundary-map.md` §7.
- Stage 11 (Commercial & Product Strategy): F-03-09, F-03-11 (sequencing/staffing).
- Stage 12 (Target Direction): F-03-02, F-03-16 (adopt revised portfolio structure).
