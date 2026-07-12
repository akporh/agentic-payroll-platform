# Stage 02 Output: Deterministic / AI Boundary Assessment

## Areas where AI must be (and per Stage 01 evidence, currently is) excluded

For each area, "sound" means: Stage 01 confirmed the mechanism is fully deterministic today, and nothing in the architecture proposal claims to change that.

| Area | Boundary status | Evidence |
|---|---|---|
| Payroll calculations | Sound | Stage 01 F-01-24, F-01-25, F-01-28 — sequential executor is deterministic; no track proposes AI involvement in the calculation itself |
| Statutory-rule execution (PAYE, pension, NHF, levy) | Sound | Stage 01 F-01-45, F-01-46 — rates are DB/migration-driven; Track Y1 proposes AI only for *detecting* an external change, never for computing or applying tax logic |
| Tax-band selection | Sound | Stage 01 F-01-46 — deterministic `tax_band` table lookup; not touched by any proposed capability |
| Component ordering | Sound | Stage 01 F-01-25 — DB-data-driven `execution_priority`; not touched |
| Rounding | Not independently re-verified in Stage 01 or Stage 02 (rounding behavior specifically was not a named Stage 01 investigation area); no proposed capability claims to touch it. Flagged as a gap in coverage, not a boundary violation. | — |
| Eligibility enforcement (who gets paid) | Sound in principle, but see caveat below | Stage 01 F-01-14, F-01-19, F-01-20 — deterministic inner-join exclusion; State Explainer (Track W) only narrates existing facts, does not decide eligibility |
| Run-state transitions | Sound | Stage 01 F-01-22, F-01-39 — DB-trigger-enforced rank-based state machine; no track proposes AI-driven transitions |
| Locking | Sound | Stage 01 F-01-37 — DB trigger; not touched |
| Payment-related actions | Sound | No track proposes AI-initiated payment; Track X requires structured human confirmation for any write, and payment marking specifically remains behind `payroll_approval_service.py`'s existing guarded transitions (Stage 01 F-01-39) |
| Authoritative data mutation | Sound as stated, one confirmed gap | Track X/Y require human confirmation for writes — but see F-02-06: the read path feeding these agents (`get_reconciliation`) currently lacks workspace scoping at the data layer, which is a boundary-adjacent integrity risk even though it's a read, not a write |
| Final compliance decisions | Sound as stated, one confirmed viability gap | Track Y1 requires operator approval before applying a compliance-rule change — but F-02-12 found no current mechanism exists to apply such a change other than a developer-authored migration, so "final compliance decision" currently has no non-engineering path regardless of who or what proposes it |

**Caveat on eligibility enforcement**: the boundary is sound in the sense that AI never decides who is paid. But Stage 01 F-01-14/F-01-19/F-01-20 found the *reason* an employee is excluded is not always explicitly recorded by the deterministic system itself (it's inferable from status/enrollment/contract facts, not stated outright at exclusion time) — meaning a State Explainer agent narrating "why" is synthesizing an explanation from raw facts, not reading a ground-truth reason field. This is a legitimate and appropriate use of AI (see F-02-11) but is worth naming explicitly: the AI is not deciding eligibility, but it is the first thing in the system that will ever state an eligibility *reason* in words.

## Areas where AI is potentially appropriate

| Area | Assessment |
|---|---|
| Explanation | Appropriate — Track W's three modes, `explain_component_trace`, and the narration half of the Reconciliation Investigation Agent (F-02-05) all fit here, provided the underlying facts are deterministically sourced |
| Investigation | Appropriate in the narrow sense of *composing* an investigation narrative over deterministically-computed facts (F-02-05); not appropriate for *performing* the causal computation itself |
| Ambiguity resolution | Appropriate — Y2's Excel/column-mapping interpretation (F-02-10) is the clearest case; genuinely ambiguous input with no fixed deterministic mapping possible |
| Evidence assembly | Appropriate — any agent that gathers multiple deterministic tool results before presenting a conclusion (Prep Agent, once separated per F-02-04; Reconciliation Agent, once separated per F-02-05) |
| Exception triage | Partially appropriate — flagging (X2/X3 triggers) should be deterministic; prioritizing/summarizing multiple flagged exceptions for an operator is a reasonable AI-assistance task |
| Recommendation | Appropriate, always paired with required human confirmation per the document's own stated Phase 2B invariant |
| Drafting | Appropriate — e.g., Y1's proposed migration description, Y2's proposed mapping — provided the draft is always reviewed/applied by a human or a separate deterministic mechanism, never self-applied |
| Natural-language interaction | Appropriate — this is Track W's entire purpose, correctly scoped read-only |
| Interpretation of unstructured inputs | Appropriate — Y2 is the clear example; nothing else in the proposal currently claims this |
| Coordination across workflows | Partially demonstrated — the event-dispatcher-to-agent routing in Track X is coordination, but it's deterministic dispatch (event type → agent), not AI-driven coordination; no proposed capability currently has an AI making coordination decisions across workflows |

## Where the current boundary is ambiguous or internally inconsistent

1. **Track X's "identifies root cause" language (F-02-05)** — ambiguous between AI-computed and AI-narrated causal identification. This is the single most consequential ambiguity found, because it sits exactly on the line the whole product thesis depends on ("AI supports investigation... deterministic services remain responsible for calculations") — if the causal diff itself becomes LLM-computed, the thesis's own boundary is violated in substance even though no calculation or state-mutation code changes.
2. **Track X2's bundling of three deterministic checks with one genuine analytics check (F-02-04)** — internally inconsistent in the sense that four checks of different fundamental character are presented as outputs of one undifferentiated "agent."
3. **Track Y1's detection-vs-application split (F-02-12)** — the boundary between "AI proposes" and "human/deterministic system applies" is stated but the "applies" side has no implementation path today, making the boundary currently theoretical for this capability specifically.
4. **`get_reconciliation` tool workspace scoping (F-02-06)** — not an inconsistency in the stated boundary, but a confirmed implementation gap that would violate the boundary's security-invariant twin ("workspace_id from JWT only... every tool call scoped") if built directly on today's data layer.

## Overall assessment

The stated boundary is sound as written and is not contradicted by anything currently deterministic in the codebase. The material risks are not in the boundary's *statement* but in three places: (1) ambiguity about whether specific proposed agents perform judgement/computation the boundary reserves for deterministic services (Track X, F-02-04/F-02-05), (2) a confirmed data-layer gap that would carry into the boundary's security-invariant twin if not independently fixed (F-02-06), and (3) a capability (Y1) whose "human approves, deterministic system applies" half has no product mechanism to stand on yet (F-02-12).
