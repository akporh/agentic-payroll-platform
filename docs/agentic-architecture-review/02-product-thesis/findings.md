# Stage 02: Product Thesis — Findings

Schema: `_core/FINDING-SCHEMA.md`, extended per the Stage 02 prompt's required finding structure (adds `consequence`, `confidence`, `recommendation`, `required human decision`, `downstream stage dependency` fields). Draft and confirmed findings are kept in separate sections — never merged.

This stage is evaluative by design (the prompt asks whether AI is justified, not just what exists), so — unlike Stage 01 — findings here legitimately carry a `recommendation`. Recommendations are about the product thesis's soundness, not implementation instructions; no code is proposed or changed.

---

## Draft Findings

(none — every observation below either met the evidence bar as a confirmed finding, or is explicitly logged in `decisions.md` as an unresolved human decision rather than left as an unlabelled guess)

---

## Confirmed Findings

### F-02-01: The core deterministic/AI boundary, as stated, is not contradicted by anything Stage 01 found
- **Statement**: The architecture document's central claim — deterministic services retain sole authority over payroll calculations, statutory rules, state transitions, and financial record mutation, while AI is scoped to judgement/investigation/interpretation/coordination — is consistent with Stage 01's evidence of the current engine.
- **Current implementation**: Stage 01 confirmed the calculation, statutory-rule, state-transition, and locking mechanisms are entirely deterministic, DB/Python-enforced, with no AI touchpoint anywhere in that path (F-01-21 through F-01-39 collectively). No proposed agent track (P/V/W/X/Y) claims write access to `payroll_result`, `payroll_run.status`, or statutory tables — Track W is explicitly read-only; Track X requires structured human confirmation for any write; Track Y requires operator approval before applying a compliance-rule change.
- **Intended design**: Matches — this is the architecture document's own stated invariant ("Agents reason over engine outputs — they do not replace deterministic rules"), and the document's own Security Invariants table restates it ("No write tools in Phase 2A... Write capability introduced only in Phase 2B with pending_action_id + structured confirmation").
- **Observed gap or ambiguity**: None at the level of stated principle. Gaps exist at the level of specific mechanisms depended upon (see F-02-06, F-02-07, F-02-09).
- **Consequence**: The high-level boundary is sound as a starting thesis; the risk is entirely in the implementation details of individual tools/agents built on top of it, which is Stage 03's remit.
- **Evidence**: `docs/architecture/agent-layer-architecture.html` (Overview, Security Invariants sections); Stage 01 F-01-21–F-01-39
- **Confidence**: High
- **Severity**: Informational
- **Recommendation**: Retain the boundary as stated; carry the specific mechanism-level gaps below into Stage 03.
- **Required human decision**: None.
- **Downstream stage dependency**: Stage 03 should verify each individual tool/agent against this boundary at implementation-design granularity.

### F-02-02: The architecture document is not an approved design — it is explicitly marked "NEEDS REVISION"
- **Statement**: The document that this stage (and Stage 03) draws on is self-labelled as unapproved.
- **Current implementation**: N/A (documentation artifact, not code).
- **Intended design**: The document's own header status pill reads "● NEEDS REVISION" (not "approved" or "planned"), dated "Arch-council reviewed 2026-06-11." This means an arch-council pass already happened and did not result in approval.
- **Observed gap or ambiguity**: Neither the document nor any file found in this stage's search states what specifically needs revision, or whether a subsequent revision round occurred. This stage did not locate a follow-up arch-council record.
- **Consequence**: Any principle or design choice in the document should be treated as "current proposed thesis, previously found to need revision" rather than "settled decision" — this matters directly for how much weight Stage 12 (Target Direction) should give to accepting the document's structure wholesale versus treating it as one input among several.
- **Evidence**: `docs/architecture/agent-layer-architecture.html:397-403` (header status pill)
- **Confidence**: High (the label itself is unambiguous); the reason for the "needs revision" label is not established by this stage's evidence.
- **Severity**: Not rated — this is a process/provenance fact, not a defect.
- **Recommendation**: Do not treat this document as a finished design in Stage 12; treat it as the primary but revisable input this review is itself helping to revise.
- **Required human decision**: Confirm whether a specific "what needs revision" record exists outside this document and should be pulled into this review. Logged in `decisions.md`.
- **Downstream stage dependency**: Stage 12 (Target Direction).

### F-02-03: Tracks P and most of Track V are infrastructure engineering, not AI capability — the "Agent Foundation" framing risks implying otherwise
- **Statement**: Authentication (Track P) and most of the event/tool/notification infrastructure (Track V) involve no LLM or AI reasoning at all; they are prerequisites that any agent would need, but are not themselves agentic.
- **Current implementation**: Per Stage 01, none of this exists yet (no JWT auth confirmed anywhere in Stage 01's evidence — Stage 01 did not find a `get_current_operator`-style dependency or an `operator` table; `audit_log.performed_by` is populated by application code, not verified identity).
- **Intended design**: Track P: JWT-based auth, `operator` table, `get_current_operator` dependency, workspace_id-from-JWT-only rule — plain authentication/authorization infrastructure. Track V: transactional outbox, new domain events, PII-sanitizing tool serializer, APScheduler-based event consumer, in-app notification table — deterministic software and workflow-automation infrastructure. None of these five items (outbox, new events, PII stripping, event consumer, notification table) require an LLM to implement or operate.
- **Observed gap or ambiguity**: The document's own tab label for Track V is "Agent Foundation," and the phase-timeline block calls it "Event + Tool Layer" under a timeline that otherwise labels every phase by its AI content. This is defensible as "the foundation agents will need," but the labeling could lead future readers (including a less careful Stage 03 review, or an engineering team scoping sprints) to treat this as AI-project work requiring AI-specific skills/evaluation, when it is conventional backend engineering (event sourcing, background workers, auth) that should be scoped, staffed, and reviewed as such.
- **Consequence**: Risk is organizational/process (mis-scoping, mis-staffing, applying AI-specific review rigor to code that doesn't need it, or conversely under-reviewing it as "just infra" when its correctness is a hard prerequisite for every later track's safety guarantees) rather than a technical defect.
- **Evidence**: `docs/architecture/agent-layer-architecture.html:408-417` (tab nav labels), `:429-456` (phase timeline), `:643-846` (Track P and Track V sections — no LLM call, prompt, or model reference anywhere in either section's content)
- **Confidence**: High
- **Severity**: Low — a labeling/framing observation, not a technical flaw.
- **Recommendation**: When this thesis is carried into Stage 12/13 scoping, treat Track P and Track V as conventional engineering work items, evaluated and sequenced like any other infrastructure sprint — not as "agent" sprints requiring AI-specific product judgment.
- **Required human decision**: None — recorded as an observation for how future stages/sprints should categorize this work.
- **Downstream stage dependency**: Stage 11 (Commercial & Product Strategy) and Stage 13 (Approved Roadmap), for sequencing/staffing implications.

### F-02-04: Several Track X "Prep Agent" checks are describable as plain deterministic validation queries, not tasks requiring an LLM
- **Statement**: Of the four checks listed for the Payroll Prep Agent (X2), at least three (missing timesheets for enrolled employees; employees enrolled but no salary definition; contracts expiring within the pay period) are boolean/set-membership conditions answerable by a SQL query with no interpretation, judgement, or natural-language reasoning involved.
- **Current implementation**: Stage 01 confirmed the underlying data these checks would query already exists in deterministic form — e.g. the exact "employee missing salary definition" condition is already computed deterministically today by `payroll_readiness_service.py` (F-01-19/F-01-20), and contract expiry is a plain date comparison against `employee_contract.end_date` (F-01-15).
- **Intended design**: The architecture document frames all four X2 checks together as output of a single "Prep Agent," using the same LLM-mediated pipeline (Dispatcher → PrepAgent → tools → in-app notification) shown in the Track X diagram.
- **Observed gap or ambiguity**: The fourth check ("input quantities anomalous vs previous period") is a genuine statistical/analytics task that could justify either a simple statistical rule (threshold/z-score) or an LLM-assisted narrative layer on top of a deterministic anomaly computation — but this is different in kind from the first three, and the document does not distinguish them. Bundling all four under one "agent" risks either (a) using an LLM to do what a query already does (unnecessary cost, latency, and a new failure mode for a previously-deterministic check), or (b) if the LLM is only asked to summarize pre-computed deterministic results, mislabeling ordinary workflow automation as an "agent."
- **Consequence**: If built as literally one LLM-driven agent evaluating all four conditions itself (rather than four deterministic checks whose *results* are handed to an LLM only for narration), the three purely-deterministic checks would be silently converted from a 100%-reliable database query into a probabilistic natural-language judgement — a strictly worse reliability profile for no benefit.
- **Evidence**: `docs/architecture/agent-layer-architecture.html:1014-1024` (X2 card); Stage 01 F-01-19, F-01-20, F-01-15
- **Confidence**: High that the first three checks are deterministic; medium on whether the document intends the LLM to compute or merely narrate them (the document does not specify this at the level of detail needed to be certain).
- **Severity**: Medium — a design ambiguity that, if resolved the wrong way, converts a reliable mechanism into an unreliable one for no functional gain.
- **Recommendation**: Stage 03 should require the Prep Agent's design to explicitly separate a deterministic detection step (SQL/service-layer checks, unconditionally reliable) from an optional LLM narration/prioritization step (turns the list of already-detected issues into a plain-English summary) — matching the pattern the document itself already applies correctly to `explain_component_trace` (slot-filling from pre-computed data, not free-form computation).
- **Required human decision**: None — a design-direction recommendation for Stage 03 to adjudicate at agent-design granularity.
- **Downstream stage dependency**: Stage 03 (Agent Portfolio).

### F-02-05: The Reconciliation Investigation Agent's design does not clearly separate deterministic root-cause computation from LLM narration
- **Statement**: X3 is described as querying the component trace, comparing expected vs. actual totals, and identifying "the specific employee + component that caused the delta" — a computation, not an act of judgement — before presenting a "plain-English root cause."
- **Current implementation**: Stage 01 confirmed `component_trace_jsonb` already contains the structured per-component breakdown needed to compute such a diff deterministically (F-01-28, F-01-29), and confirmed a specific existing UI signal for a related but distinct scenario — the `resolution_source === 'current_fallback'` flag (F-01-44) — which is itself a deterministically-computed audit signal, not an LLM output.
- **Intended design**: The document's Track X diagram routes `reconciliation.MISMATCH` through the Dispatcher to the Reconciliation Agent, which calls `get_reconciliation`/`explain_trace` tools and then, per the X3 card text, "identifies" the causal employee/component before presenting it to the operator.
- **Observed gap or ambiguity**: "Identifies" is ambiguous between "the LLM performs the diff/search itself" (probabilistic identification of a numeric root cause — exactly the failure mode Blocking Condition #4 was written to prevent for `explain_component_trace`) and "a deterministic diff is computed first, and the LLM only narrates the already-identified employee/component." The document does not state which.
- **Consequence**: If the LLM performs the identification itself (rather than narrating a pre-computed diff), this both duplicates Blocking Condition #4's failure mode in a new tool and reintroduces the risk Stage 01 flagged around `current_fallback` (F-01-44) being conflated with an LLM-generated explanation rather than an engine-computed fact.
- **Evidence**: `docs/architecture/agent-layer-architecture.html:1026-1030` (X3 card); Stage 01 F-01-28, F-01-29, F-01-44
- **Confidence**: Medium — genuinely ambiguous from the document text alone.
- **Severity**: Medium — same reasoning as F-02-04: the risk is a probabilistic mechanism silently replacing what should be a deterministic one.
- **Recommendation**: Require X3's actual causal diff (which employee, which component, which amount) to be computed by deterministic code reading `component_trace_jsonb`/`payroll_reconciliation`, with the LLM's role limited to composing the plain-English explanation from that pre-computed, structured result — the same slot-filling pattern already specified for `explain_component_trace`.
- **Required human decision**: None — forwarded to Stage 03 as a required design constraint to verify at agent-spec level.
- **Downstream stage dependency**: Stage 03 (Agent Portfolio).

### F-02-06: The proposed tool layer must independently (re-)implement workspace scoping — it cannot inherit it from the existing data layer for at least one confirmed case
- **Statement**: The architecture document treats "workspace_id from JWT only, tool calls scoped" as a non-negotiable security invariant, implemented via new "narrow domain-shaped tools." Stage 01 confirmed that at least one of the data sources these tools would plausibly wrap (`payroll_reconciliation`) has no workspace scoping at all in its current repository functions.
- **Current implementation**: Per Stage 01 F-01-33, `payroll_reconciliation` has no `workspace_id` column, and every existing repository function (`insert_reconciliation`, `update_reconciliation`, `get_reconciliation`) scopes solely by `payroll_run_id`. A `get_reconciliation` tool (listed explicitly in the document's Tool Definitions table) built as a thin wrapper over the existing repo function would inherit this gap.
- **Intended design**: The document's stated invariant is that workspace_id comes from the JWT and every tool call is workspace-scoped — this is listed as a "Security Invariant (non-negotiable)."
- **Observed gap or ambiguity**: The document does not state whether new tool implementations are required to add independent workspace-scoping enforcement at the tool layer (defense in depth) or are expected to call existing repository functions as-is. Given F-01-33, the latter would silently violate the document's own stated invariant for this one tool.
- **Consequence**: If unaddressed, a `get_reconciliation` tool call authenticated to Workspace A could, in principle, return reconciliation data for a `payroll_run_id` belonging to Workspace B, since nothing in the current data path checks workspace ownership of the run — a direct violation of the document's own "workspace_id from JWT only" invariant, at the one place in Stage 01's evidence where this was concretely confirmed as a current gap.
- **Evidence**: Stage 01 F-01-33; `docs/architecture/agent-layer-architecture.html:1198-1223` (Security Invariants), `:820-837` (Tool Definitions table, `get_reconciliation` row)
- **Confidence**: High — this is a direct, specific consequence of an already-confirmed Stage 01 finding, not a speculative concern.
- **Severity**: High — a confirmed data-layer gap that would carry directly into a stated non-negotiable security invariant of the proposed agent architecture if the tool layer is built as a thin pass-through.
- **Recommendation**: Require every Track V tool definition to independently verify/enforce workspace ownership at the tool-serialization layer, regardless of what the underlying repository function does — do not assume the data layer already enforces this. `get_reconciliation` specifically needs this fix before Track V ships.
- **Required human decision**: Whether closing the `payroll_reconciliation` workspace-scoping gap is a precondition for building the `get_reconciliation` tool, or whether the tool layer is expected to compensate independently. Logged in `decisions.md`.
- **Downstream stage dependency**: Stage 03 (Agent Portfolio — specific tool design), Stage 05 (Platform Readiness), Stage 07 (Security & Identity).

### F-02-07: The `explain_component_trace` anti-hallucination design depends on `component_trace_jsonb` being populated — which Stage 01 confirmed is not always true
- **Statement**: The document's Blocking Condition #4 requires `explain_component_trace` to fill named slots from structured trace data only, never inventing numbers. This design is sound, but assumes the trace data exists.
- **Current implementation**: Stage 01 confirmed the legacy calculation executor explicitly sets `component_trace_jsonb = None` (F-01-28) and is reachable code, currently not observed to fire in production (both live call sites always supply `component_metadata`), but not removed.
- **Intended design**: The document's constraint text: "The LLM fills named slots from structured trace data only. It cannot introduce numeric values not present in the `component_trace_jsonb` source." No fallback behavior is specified for when that source is null.
- **Observed gap or ambiguity**: The document does not address what `explain_component_trace` should do when `component_trace_jsonb` is `None` — refuse to answer, degrade to a generic explanation, or something else. This is an unspecified edge case, not a contradiction, since the legacy path is not currently observed to fire.
- **Consequence**: Low likelihood given F-01-24's finding that the legacy path isn't currently exercised by any live caller, but the risk is not zero (it remains reachable code with a monitoring endpoint specifically because it isn't fully retired), and the failure mode if it did fire (a trace-explaining tool given no trace) is unspecified.
- **Evidence**: Stage 01 F-01-24, F-01-28; `docs/architecture/agent-layer-architecture.html:949-951` (component trace note)
- **Confidence**: High on the dependency existing; low likelihood of it being triggered in current practice.
- **Severity**: Low — a specified-but-currently-unlikely edge case.
- **Recommendation**: Stage 03 should specify `explain_component_trace`'s behavior for a null/absent trace explicitly (e.g., a defined refusal message referencing the legacy-executor gap) rather than leaving it implicit.
- **Required human decision**: None.
- **Downstream stage dependency**: Stage 03 (Agent Portfolio).

### F-02-08: The architecture document's self-assessed "As-Is" gap register (GAP-1–GAP-6) is a different, narrower inventory than Stage 01's independently-derived findings — useful corroboration, not a substitute
- **Statement**: The document's own "As-Is Architecture" tab lists 6 gaps (no auth, write-only event store, missing events, fire-and-forget event writes, no background task infra, no notification layer). Stage 01 independently found a substantially larger and partially non-overlapping set of gaps (46 findings) using direct code/migration evidence.
- **Current implementation**: Confirmed by direct comparison: the document's GAP-1 (no auth) is outside Stage 01's scoped 20 areas (Stage 01 did not investigate authentication) and is not contradicted, but also not independently verified by Stage 01. The document's GAP-2/GAP-3 (event store) partially overlaps conceptually with Stage 01's audit-trail finding (F-01-40 — `audit_log`/`event_store` cover only `payroll_run` transitions) but describes it as an event-consumer gap rather than an audit-coverage gap — related but distinct framings of adjacent evidence.
- **Intended design**: The document presents its gap register as authoritative context for scoping Tracks P/V ("Documented from codebase audit 2026-06-11").
- **Observed gap or ambiguity**: Neither register supersedes the other — they were produced by different methods (the document's audit is undated in method/evidence detail; Stage 01's is fully cited to file:line). This stage did not find a reason to doubt either, but notes the two should be reconciled, not treated as duplicates or substitutes, when Stage 03/05 scope actual remediation work.
- **Consequence**: If Stage 03/05 reads only the architecture document's gap register and not Stage 01's findings, several confirmed Stage 01 gaps directly relevant to agent-layer safety (F-01-33 reconciliation scoping, F-01-45/46 statutory-rule maintenance, F-01-38 dead status branches) would be missed, since none of them appear in the document's own GAP-1–GAP-6 list.
- **Evidence**: `docs/architecture/agent-layer-architecture.html:526-641` (As-Is Architecture tab, full gap register); Stage 01 findings.md in full
- **Confidence**: High
- **Severity**: Informational — a coverage/completeness observation about the input documents, not a defect in either.
- **Recommendation**: Stage 03 and Stage 05 should treat Stage 01's findings as the authoritative, evidence-backed gap register and the document's GAP-1–GAP-6 as a partial, complementary list (particularly useful for the authentication gap, which is outside Stage 01's scope) — not read one in place of the other.
- **Required human decision**: None.
- **Downstream stage dependency**: Stage 03, Stage 05 (Platform Readiness).

### F-02-09: The "historical payroll outcomes must remain reproducible" candidate principle is only as strong as Stage 01's confirmed snapshot/lock gaps allow
- **Statement**: Candidate principle 7 ("Historical payroll outcomes must remain reproducible") is a sound principle in the abstract, but its current factual grounding is incomplete per Stage 01.
- **Current implementation**: Stage 01 confirmed `salary_definition` can be edited while a run referencing it is anywhere from DRAFT through LOCKED (not yet PAID) at the DB level, with the only application-layer backstop scoped to one specific route (F-01-27, F-01-38). Stage 01 also confirmed an unresolved ambiguity in trace-persistence fallback precedence (F-01-29).
- **Intended design**: If this principle is adopted as written, it implies every historical run's inputs and outputs should be re-derivable/explainable after the fact — which is exactly the property any Track W/X agent explaining "why did employee X get paid Y" depends on.
- **Observed gap or ambiguity**: The principle as stated is aspirational relative to current implementation; adopting it as "non-negotiable" without acknowledging the current gap risks the review approving a principle the platform cannot yet fully honor, which Stage 03/05 should not silently paper over when designing agents that will implicitly rely on this reproducibility.
- **Consequence**: An agent (e.g., a future Trace Agent, or Track Y's compliance monitor comparing historical runs against updated rules) that assumes full historical reproducibility could produce a plausible-sounding but factually wrong explanation for a run affected by one of these gaps, with no mechanism to detect the discrepancy.
- **Evidence**: Stage 01 F-01-27, F-01-29, F-01-38
- **Confidence**: High
- **Severity**: Medium — a real dependency the product principle would otherwise obscure.
- **Recommendation**: Adopt the principle (see `outputs/non-negotiable-product-principles.md`), but explicitly record it as currently only partially satisfied, with the specific Stage 01 findings that must be resolved (or explicitly accepted as residual risk) before any agent relies on full reproducibility.
- **Required human decision**: Whether closing F-01-27/F-01-38 is a precondition for Track W/X, or an accepted residual risk to be disclosed to operators. Logged in `decisions.md`.
- **Downstream stage dependency**: Stage 05 (Platform Readiness), Stage 08 (Technical Architecture).

### F-02-10: The Onboarding Agent (Y2) is one of the more clearly AI-justified proposed capabilities
- **Statement**: Interpreting arbitrary, human-authored Excel column headers and proposing salary-definition/grade/designation mappings is an inherently ambiguous natural-language/fuzzy-matching problem, unlike the largely deterministic checks discussed in F-02-04.
- **Current implementation**: Stage 01 confirmed the current bulk-upload path already requires a human-driven column-mapping step (`NativeUploadFlow`, per Stage 01 Cluster B/E evidence) and stores raw imported labels for later reference (`imported_grade_label`/`imported_designation_label`, F-01-13) precisely because automatic resolution isn't currently attempted.
- **Intended design**: Y2 proposes the agent interpret messy Excel, map columns, propose salary-definition assignments, and run a dry-run payroll before committing — i.e., a bounded, human-confirmed AI-assistance capability with a deterministic validation gate (the dry run) before any commit.
- **Observed gap or ambiguity**: None identified against the stated design — this is a coherent, appropriately-bounded proposal. The one open question is whether "dry-run payroll" as a pre-commit safety gate has anywhere near the reliability guarantees needed (i.e., does the dry run actually exercise the same deterministic engine path a real run would, including snapshot creation) — this touches Stage 01's snapshot/executor findings (F-01-24, F-01-26) but was not tested directly against a "dry run" concept, since no such mechanism currently exists.
- **Consequence**: If well-scoped as described, this is a case where AI use is justified rather than a case of "agent" terminology applied to ordinary automation — the underlying task (arbitrary spreadsheet interpretation) is not solvable by a fixed deterministic mapping table alone, which is exactly the class of problem the current manual `NativeUploadFlow` mapping step exists to handle today.
- **Evidence**: `docs/architecture/agent-layer-architecture.html:1101-1103` (Y2 card); Stage 01 F-01-13 (Cluster B), Cluster E evidence on `NativeUploadFlow`
- **Confidence**: Medium-high — sound in concept; the "dry-run payroll" mechanism itself doesn't exist yet, so its adequacy as a safety gate is unverified.
- **Severity**: Not rated — this is a positive finding (AI use appears justified here), not a defect.
- **Recommendation**: Retain Y2 as a case where AI assistance is appropriate; require Stage 03/08 to specify exactly what "dry-run payroll" means mechanically (does it reuse the real sequential executor and snapshot machinery, or a separate simulation path) before relying on it as the safety gate for AI-proposed mappings.
- **Required human decision**: None at this stage.
- **Downstream stage dependency**: Stage 03 (Agent Portfolio), Stage 08 (Technical Architecture — what "dry-run" means mechanically).

### F-02-11: Track W's three chat modes are a coherent, appropriately-bounded case for probabilistic AI assistance
- **Statement**: Navigation Guide, State Explainer, and Action Planner are read-only, tool-mediated, PII-stripped natural-language interfaces over existing deterministic data — a legitimate use of an LLM for interpretation of natural-language questions and retrieval/explanation of existing facts.
- **Current implementation**: N/A — not built. Stage 01 confirms the underlying data these modes would query (employee status/contract/enrollment state, run results) already exists in deterministic, queryable form (F-01-13, F-01-14, F-01-19–20), which is precisely what a retrieval/explanation-type agent should be built on top of, not around.
- **Intended design**: Read-only in Phase 2A; no write tools; PII stripped before LLM context; rate-limited from the first sprint (W3, explicitly called out as "non-negotiable, not deferred").
- **Observed gap or ambiguity**: None identified against the stated design for this specific track. The main dependency is that "State Explainer" answers (e.g., "why is Adaobi not in this run?") are only as correct as the underlying deterministic exclusion logic Stage 01 examined — F-01-14's finding that unenrolled/inactive employees are silently excluded by an inner join, with no per-employee reason surfaced anywhere in the current system, means a State Explainer agent would need new tooling to reconstruct "why," since the current system does not itself record a reason at exclusion time — it only allows the *fact* of exclusion to be queried (status, enrollment state), and the agent would need to infer the "why" narrative from those facts itself.
- **Consequence**: This is a legitimate design constraint to hand to Stage 03, not a flaw — the "why" narrative is a compound inference over several deterministic facts, which is exactly the kind of interpretation task AI assistance is well-suited for, provided the underlying facts (status, enrollment, contract dates) are each retrieved via read-only tools rather than invented.
- **Evidence**: `docs/architecture/agent-layer-architecture.html:848-952` (Track W); Stage 01 F-01-13, F-01-14, F-01-19, F-01-20
- **Confidence**: High
- **Severity**: Informational
- **Recommendation**: Retain Track W's scope and read-only/PII-stripped/rate-limited constraints as-is; ensure the "State Explainer" mode's tool set includes all the individual deterministic facts (status, enrollment, contract window, salary-definition presence) needed to compose an accurate exclusion narrative, rather than a single pre-packaged "why excluded" tool that itself embeds unreviewed logic.
- **Required human decision**: None.
- **Downstream stage dependency**: Stage 03 (Agent Portfolio).

### F-02-12: The Compliance Monitoring agent's (Y1) proposed output has no current product-side application mechanism — it would generate proposals with nowhere concrete to land
- **Statement**: Y1 proposes detecting FIRS/PenCom statutory changes, comparing against the current `statutory_rule` table, flagging deltas, and proposing a migration, subject to operator approval.
- **Current implementation**: Stage 01 confirmed statutory-rule maintenance today is exclusively migration-only — no admin route or UI exists for creating/editing `statutory_rule`/`tax_band` rows (F-01-45), and non-tax-band rates (pension, NHF, health, levy) remain unnormalized JSONB with silent defaults on missing keys (F-01-46).
- **Intended design**: Y1's stated mechanism is "proposes migration... requires operator approval before applying" — implying some structured proposal-and-approval UI/workflow that does not currently exist in any form; today, the only way a statutory rate is ever changed is a developer writing and deploying a new Alembic migration.
- **Observed gap or ambiguity**: The document does not specify what "proposes migration" means operationally — whether the agent would need to generate an actual Alembic migration file (requiring code-generation and deployment-pipeline capabilities well beyond the read-only/tool-mediated pattern used elsewhere), or whether a new, simpler operator-approval-then-apply mechanism is assumed to be built first. Given F-01-45/46, this gap is not incidental — it is a precondition gap between the proposed capability and the current platform's operational model for this exact class of change.
- **Consequence**: As scoped, Y1 cannot function without first building an entirely new statutory-rule change-management mechanism (something closer to Y1 is arguably impossible to ship safely on the current migration-only foundation without that mechanism existing first) — this is a materially significant dependency for the product thesis's Track Y viability, not a minor implementation detail.
- **Evidence**: Stage 01 F-01-45, F-01-46; `docs/architecture/agent-layer-architecture.html:1095-1099` (Y1 card)
- **Confidence**: High
- **Severity**: High — a proposed capability with no viable current application path, for one of the platform's most legally consequential data categories (statutory tax/pension/levy rates).
- **Recommendation**: Treat Y1 as blocked on a not-yet-designed statutory-rule change-management capability (which is itself a legitimate, valuable, and largely deterministic feature — an approval workflow over migration-style changes — independent of whether AI is involved in detecting the need for the change). Do not scope Y1 as a near-term Track Y deliverable until that foundation is designed.
- **Required human decision**: Whether a statutory-rule change-management mechanism should be scoped as platform work independent of the AI-detection capability, and if so, in which phase. Logged in `decisions.md`.
- **Downstream stage dependency**: Stage 05 (Platform Readiness), Stage 06 (Compliance & Controls — this is exactly the kind of compliance question the Stage 02 prompt asks to forward), Stage 11 (Commercial & Product Strategy).

### F-02-13: The Phase 2B write-confirmation protocol is specified conceptually but leaves concurrency/expiry questions unanswered — appropriately flagged by the document itself as a pre-condition, not yet resolved
- **Statement**: The document itself states the confirmation protocol "must be fully specified" before Phase 2B sprint planning begins — this stage confirms that specification gap still exists in the document as written.
- **Current implementation**: N/A — Phase 2B is not built.
- **Intended design**: `pending_action_id` + a structured confirmation UI component (not a chat reply) showing the exact record/field/new-value, for any financial mutation.
- **Observed gap or ambiguity**: No description of (a) what happens if an operator never confirms a pending action (expiry/cleanup), (b) how two proactive agents proposing conflicting pending actions on the same entity would be reconciled, or (c) whether `pending_action_id` participates in the same immutability/locking rules Stage 01 found govern `payroll_run`/`payroll_result` (F-01-37, F-01-39) if the pending action targets a run that transitions state while the confirmation is outstanding (e.g., a run gets `LOCKED` between an agent proposing an action and the operator confirming it).
- **Consequence**: This is explicitly pre-emptive — the document itself flags this as a gate condition ("Pre-condition before Phase 2B sprint planning") rather than a silent gap, so this finding mainly confirms the document's own self-identified gap is real and adds the specific race-condition/state-transition-interaction question Stage 01's approval/locking findings surface.
- **Evidence**: `docs/architecture/agent-layer-architecture.html:959-961` (Track X pre-condition callout); Stage 01 F-01-37, F-01-39
- **Confidence**: High
- **Severity**: Not rated — this is a self-acknowledged, not-yet-due design gap; rating it would imply it should already be resolved, which the document itself does not claim.
- **Recommendation**: When this protocol is specified (a Stage 03/08 task, not Stage 02's), require it to explicitly state its interaction with `payroll_run` state transitions — specifically, whether a pending action targeting a run is invalidated if that run transitions to `APPROVED`/`LOCKED`/`PAID` before confirmation.
- **Required human decision**: None yet — forwarded as a specification requirement, not a decision needed now.
- **Downstream stage dependency**: Stage 03 (Agent Portfolio), Stage 08 (Technical Architecture).

### F-02-14: "Agentic-readiness" claimed for the Phase 1 engine (immutable runs, component trace, rule versioning) supports Tracks W/X directly but does not extend to Track Y's external-facing capabilities
- **Statement**: `FEAT-020`'s note that "Phase 1 engine is deliberately agentic-ready (immutable runs, component trace, rule versioning)" is accurate for capabilities that read existing internal state (Tracks W, X) but the same claim does not automatically cover Track Y's compliance-monitoring (external regulatory sources) or onboarding (arbitrary external file interpretation) capabilities, which depend on entirely different foundations (external data ingestion, change-management workflow — see F-02-12) not addressed by "immutable runs, component trace, rule versioning."
- **Current implementation**: Stage 01 confirms immutable runs (F-01-37, F-01-39), component trace (F-01-28, F-01-29 — with caveats), and rule versioning (F-01-11) are real, implemented properties of the current engine.
- **Intended design**: `FEAT-020_ai-payroll-engine_FUTURE.md:16` states this "agentic-ready" property as the rationale for Phase 2 building on Phase 1.
- **Observed gap or ambiguity**: The stub feature doc makes a general claim ("Phase 2 builds the agentic layer on top") without distinguishing which Phase 2 capability actually depends on which Phase 1 property. This stage's classification work (see `outputs/capability-classification-matrix.md`) makes that distinction explicit where the source document does not.
- **Consequence**: Without this distinction, a reader could assume the whole of Track Y is equally well-supported by the current engine's readiness properties, when in fact Y1/Y2 depend on capabilities (external monitoring, file interpretation, change-management workflow) the current engine's cited properties don't touch at all.
- **Evidence**: `Clients/Sandy/_PRODUCT/EP-004_phase2-agentic/FEAT-020_ai-payroll-engine_FUTURE.md:16`; Stage 01 F-01-11, F-01-28, F-01-29, F-01-37, F-01-39
- **Confidence**: High
- **Severity**: Low — a documentation-precision observation, not a defect; addressed structurally in the capability classification output.
- **Recommendation**: When FEAT-020/021 are eventually scoped (they are currently TBD stubs), avoid a single blanket "agentic-ready" justification; state per-capability which Phase 1 property it depends on, if any.
- **Required human decision**: None.
- **Downstream stage dependency**: Stage 11 (Commercial & Product Strategy), when FEAT-020/021 move out of stub status.

---

## Parked / Rejected

_None — every lead investigated in this stage reached a confirmed finding or an explicitly logged human decision in `decisions.md`._

## Cross-references for later stages

- Stage 03 (Agent Portfolio): F-02-04, F-02-05, F-02-06, F-02-07, F-02-10, F-02-11, F-02-13 are direct design-constraint inputs for individual agent/tool review.
- Stage 05 (Platform Readiness): F-02-06, F-02-09, F-02-12 identify platform foundations the thesis depends on that Stage 01 found incomplete.
- Stage 06 (Compliance & Controls): F-02-12 (statutory-rule change-management gap) is a direct compliance-relevant input, as instructed by the Stage 02 prompt.
- Stage 07 (Security & Identity): F-02-06 (tool-layer workspace scoping) is a direct input.
- Stage 08 (Technical Architecture): F-02-09 (reproducibility dependency), F-02-10 (dry-run mechanism), F-02-13 (confirmation-protocol/state-transition interaction).
- Stage 11 (Commercial & Product Strategy): F-02-03 (Track P/V sequencing/staffing), F-02-12 (Y1 viability), F-02-14 (FEAT-020/021 scoping precision).
- Stage 12 (Target Direction): F-02-02 (document's unapproved status — do not treat as settled).
