# Stage 02 Output: Non-Negotiable Product Principles

Each of the 10 candidate principles from the Stage 02 prompt, classified `retain` / `revise` / `remove` / `add`, with the evidence behind the classification. One principle is proposed as an addition.

## 1. Payroll calculations remain deterministic
**Classification: retain, unchanged.**
Fully supported — Stage 01 found no AI touchpoint anywhere in the calculation path, and no proposed capability (Tracks P–Y) claims to change that. See F-02-01.

## 2. The LLM is never the source of truth
**Classification: retain, unchanged.**
Matches the document's own PII-stripping, structured-JSON-envelope, and slot-filling design choices. See F-02-01, F-02-07.

## 3. Agents use controlled tools rather than database access
**Classification: retain, with an explicit addition (see Principle 11 below).**
Sound as a general principle, but insufficient on its own: Stage 02 confirmed at least one case (F-02-06, `get_reconciliation`) where a "controlled tool" built as a thin wrapper over an existing, unscoped repository function would silently fail to deliver the isolation the principle promises. The principle needs to be paired with an explicit requirement that tool implementations independently verify workspace scoping rather than assuming the underlying query already does.

## 4. Generated explanations must link to evidence
**Classification: retain, revise scope.**
The document currently states this constraint only for `explain_component_trace` (Blocking Condition #4). Stage 02 found the same requirement is equally necessary for the Reconciliation Investigation Agent's causal narrative (F-02-05) and, by extension, any future explanation-generating tool. Revise the principle's wording from "generated explanations must link to evidence" (already good) to make explicit that this applies to *every* agent output that states a fact, number, or cause — not only the one tool currently named in the document.

## 5. High-risk mutations require structured approval
**Classification: retain, unchanged, with one dependency noted.**
Matches Track X/Y's stated confirmation-protocol requirement. Dependency: the confirmation protocol's interaction with concurrent state transitions is not yet specified (F-02-13) — this doesn't weaken the principle, but the principle can't be verified as *implemented* until that specification exists.

## 6. Agent memory must not become a shadow system of record
**Classification: retain, unchanged.**
Already reflected in the document's own design (`agent_session_log`: ephemeral session + 7-year audit-only retention, "no full replay"). No contradicting evidence found.

## 7. Historical payroll outcomes must remain reproducible
**Classification: retain, but flag as currently only partially satisfied.**
See F-02-09. The principle is correct and important — it should not be weakened — but it should be adopted with an explicit note that Stage 01 found specific gaps (F-01-27, F-01-29, F-01-38) that mean the platform does not yet fully satisfy it. Adopting the principle without that note risks the review implicitly certifying a property that isn't yet true.

## 8. Chat is an interface, not the product strategy
**Classification: retain, unchanged.**
Consistent with the document's own phased approach — chat (Track W) is one of five tracks, not the organizing structure, and the deterministic engine remains the product's core.

## 9. AI should not be used where deterministic software is sufficient
**Classification: retain, strengthen with an enforcement mechanism.**
This stage's own capability classification (`outputs/capability-classification-matrix.md`) found 10 of 24 identified capabilities are plain deterministic software associated with an "agent" track, and at least two proposed agents (Track X2, X3) bundle deterministic checks with genuinely AI-appropriate ones without distinguishing them (F-02-04, F-02-05). The principle as stated is correct but currently unenforced — as evidence, the very document under review doesn't consistently apply it. Recommend strengthening it operationally: every future agent/capability proposal should be required to state, capability-by-capability, why a deterministic or simpler mechanism was insufficient — not just assert the principle in the abstract.

## 10. Autonomy must be earned through measured performance
**Classification: retain, unchanged.**
Matches the phased structure (2A read-only → 2B confirmed-write → 2C autonomous, explicitly gated on "2B proven in production" per the document). No proposed capability in the current document actually claims autonomy yet — Track Y still requires operator approval for its most consequential actions (Y1's rule change, Y2's commit).

## Proposed addition

### 11. Every agent-facing data path must independently enforce workspace scoping — inheriting it from an underlying query is not sufficient
**Classification: add.**
Directly motivated by F-02-06: Stage 01 confirmed at least one existing data path (`payroll_reconciliation`) has no workspace scoping at all, and the architecture document's stated security invariant ("workspace_id from JWT only... every tool call scoped") would not automatically hold if new tools are built as thin wrappers over such paths. This isn't fully covered by Principle 3 as originally worded (which addresses *how agents access data*, not *whether the data access path itself is safe to wrap*). Recommend adding this as an explicit, separately-testable principle so that every future tool definition has a concrete acceptance check: "does this tool independently verify workspace ownership, regardless of what the underlying function does?"

## Summary table

| # | Principle | Classification |
|---|---|---|
| 1 | Payroll calculations remain deterministic | Retain |
| 2 | LLM is never the source of truth | Retain |
| 3 | Agents use controlled tools rather than database access | Retain (paired with #11) |
| 4 | Generated explanations must link to evidence | Retain, revise scope (all outputs, not just one tool) |
| 5 | High-risk mutations require structured approval | Retain |
| 6 | Agent memory must not become a shadow system of record | Retain |
| 7 | Historical payroll outcomes must remain reproducible | Retain, flag partial current satisfaction |
| 8 | Chat is an interface, not the product strategy | Retain |
| 9 | AI should not be used where deterministic software is sufficient | Retain, strengthen with enforcement mechanism |
| 10 | Autonomy must be earned through measured performance | Retain |
| 11 (new) | Every agent-facing data path must independently enforce workspace scoping | Add |
