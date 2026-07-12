# Stage 02 Output: Product Thesis Assessment

## 1. Reconstructed product thesis

**Explicitly stated design principles** (from `docs/architecture/agent-layer-architecture.html`):
- Agents reason over engine outputs; they do not replace deterministic rules.
- `workspace_id` comes from the JWT only, never from message content or request body.
- PII (name, TIN, RSA pin, bank account, employee number) is stripped before reaching the LLM; only UUIDs, amounts-as-strings, component names, dates/status, and run IDs are sent.
- Tool results are structured JSON envelopes, not raw string interpolation into a system prompt.
- No write tools in Phase 2A; write capability arrives only in Phase 2B behind a structured confirmation mechanism.
- Decimal values sent to an LLM are serialized as strings, explicitly breaking from the project's existing JSONB-float convention because float precision loss is unacceptable in LLM-visible context.
- Tools are narrow and domain-shaped, not generic SQL-like access.
- Autonomy is phased and earned: 2A (read-only chat) → 2B (confirmed writes) → 2C (autonomous), with 2C explicitly deferred until 2B is proven in production.

**Implied assumptions** (present in the document's structure but not stated as explicit principles):
- That the existing deterministic engine's outputs (trace, reconciliation, status) are complete and correct enough to be explained/investigated without independent re-verification by the agent layer. Stage 01 found this assumption holds in most but not all cases (F-02-06, F-02-07, F-02-09).
- That "agent" is the right framing for every capability in Tracks P–Y, when several (see `outputs/capability-classification-matrix.md`) are conventional infrastructure or rules-engine work (F-02-03, F-02-04).
- That a statutory-rule change-management mechanism will exist by the time Y1 is built — assumed but not designed anywhere found in this review (F-02-12).

**Current implementation**: none of Tracks P–Y exist yet. The document's own phase-timeline marks Track P as "current" (not started) and everything else as future. This is a proposal, not a built system — a fact this stage was specifically instructed not to blur.

**Future intent**: a five-phase build-out (auth → event/tool foundation → read-only chat → confirmed-write proactive agents → autonomous agents), gated at each transition on the prior phase being complete and, for 2C, "proven in production."

**Unresolved product decisions** (identified in this stage, logged in `decisions.md`):
- Whether the document's "NEEDS REVISION" status reflects concerns already addressed elsewhere, or is still open (F-02-02).
- Whether the `payroll_reconciliation` workspace-scoping gap is a precondition for Track V, or something the tool layer is expected to compensate for independently (F-02-06).
- Whether Stage 01's reproducibility-relevant gaps (F-01-27, F-01-38) must close before Track W/X ship, or are accepted residual risk (F-02-09).
- Whether a statutory-rule change-management mechanism is scoped as its own deliverable, independent of Y1's AI-detection capability (F-02-12).

## 2. Capability classification

See `outputs/capability-classification-matrix.md` for the full 24-capability breakdown. Headline: of 24 identified capabilities across all five tracks, 10 are plain deterministic software, 3 are workflow automation, 2 are analytics/anomaly-detection, 5 are retrieval-and-explanation, and only 2–3 are capabilities where an LLM does something no deterministic mechanism reasonably could (Y2's Excel interpretation being the clearest case). One capability (Y1's migration-application step) currently has no viable implementation path at all.

## 3. Deterministic/AI boundary test

See `outputs/deterministic-ai-boundary.md` for the full area-by-area assessment. Summary: every area the prompt asked this stage to check AI is excluded from (calculations, statutory execution, tax bands, ordering, eligibility, state transitions, locking, payment, mutation, compliance decisions) is, per Stage 01 evidence, currently fully deterministic and not contradicted by any proposed capability. The boundary's *statement* is sound. The risk is concentrated in three specific, named ambiguities (Track X's causal-identification language, Track X2's bundling of deterministic and analytics checks, and Y1's detection-without-application-path design) rather than in the boundary's overall shape.

## 4. Is "agentic" actually required?

For 10 of 24 classified capabilities (see matrix), the answer is no — a validation rule, a scheduled query, or ordinary workflow automation is both sufficient and, per the principle "AI should not be used where deterministic software is sufficient," preferable. This is not a criticism unique to this proposal; it is a common and correctable pattern in early agent-architecture drafts, and the document's own careful treatment of `explain_component_trace` (slot-filling, not free generation) shows the authors already understand and apply the right discipline in at least one place — it simply isn't applied uniformly across every capability yet.

## 5. Platform-trustworthiness dependencies

Of the ten platform-foundation areas the Stage 02 prompt asked this stage to weigh against Stage 01's findings, three are confirmed to materially affect the thesis's validity (not merely to exist as background risk):

- **Reconciliation scoping** (F-02-06) — directly undermines a stated non-negotiable security invariant if the tool layer is built naively.
- **Statutory-rule representation** (F-02-12) — a named Track Y capability (Y1) has no product-side application mechanism at all under current platform design.
- **Incomplete historical reproducibility** (F-02-09) — undermines the factual grounding of a candidate non-negotiable principle (#7) that several agents (explanation, investigation) implicitly depend on.

The remaining seven areas listed in the prompt (parallel configuration entry points, silent employee exclusion, sequential/legacy executor divergence, snapshot completeness, retry behaviour, audit coverage, frontend/backend mismatches) were reviewed against the thesis and found *not* to materially change its validity at the thesis level — they are real Stage 01 findings, but they affect specific future tool/agent designs (Stage 03's remit) rather than the soundness of the boundary itself. They are carried forward to Stage 03/05 rather than re-litigated here, per the prompt's instruction not to perform the full Stage 05 readiness review in this stage.

## 6. Non-negotiable product principles

See `outputs/non-negotiable-product-principles.md`. All 10 candidate principles are recommended for retention; three (#4, #7, #9) are recommended for a scope revision or added enforcement teeth rather than a change in substance; one new principle (#11, on independent workspace-scoping enforcement at the tool layer) is proposed as an addition, directly motivated by F-02-06.

## Overall conclusion

The proposed product boundary — AI for judgement/investigation/interpretation/coordination, deterministic services for calculation/statutory execution/state/mutation — is sound as stated and is not contradicted by Stage 01's evidence of the current deterministic core. It should be retained as the organizing thesis for Phase 2. The material risks found in this stage are not boundary-shape risks; they are (a) three specific ambiguities where a proposed agent's actual behavior could cross the boundary in substance even while the document's prose respects it (Track X2/X3), (b) one confirmed implementation gap that would violate the boundary's own security-invariant twin if not independently addressed (`get_reconciliation` workspace scoping), and (c) one capability (Y1) that is currently unbuildable as scoped because its non-AI half has no product mechanism yet. None of these require redesigning the thesis; all are addressable at the individual-agent design level, which is exactly what Stage 03 exists to do.
