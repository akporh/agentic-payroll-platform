# Stage 12 Output: Source-Document Disposition (Q6)

Precisely what the revision changes about `docs/architecture/agent-layer-architecture.html` (S-04; also mirrored at `frontend/public/architecture/agent-layer-architecture.html`) — **as a recommendation for Stage 13's approval, resolving D-02-01's open status**. The document was re-read live 2026-07-18 for this disposition (header: "Arch-council reviewed 2026-06-11", status pill "NEEDS REVISION"). Per D-02-01 this synthesis is the formal revision path; the document is not approved until Stage 13 records approval, and **nothing is edited here** — application of the revision is a Phase 3 act after approval (writes outside this programme's authorised paths).

## 1. Disposition recommendation (DEC-12-04)

**Supersede-and-replace, preserving what survived review.** The document's five-track/three-phase structure is retired as the target description; its still-valid content (security invariants, several design constraints, the As-Is diagnosis where confirmed) is carried into the revision rather than re-derived. The revision's substance is this stage's outputs: `target-direction-statement.md` (identity + fork), `target-architecture-posture.md` (structural commitments), `product-direction-narrative.md` (the story), `capability-end-state-map.md` (the to-be picture replacing the five tracks). On Stage 13 approval, the "NEEDS REVISION" status resolves by the document being replaced/rewritten from these outputs — not by the existing HTML being stamped approved as-is.

## 2. What the revision changes — structure

| Source document | Revision |
|---|---|
| Five tracks: P (Auth) / V (Agent Foundation) / W (Chat, 2A) / X (Proactive, 2B) / Y (Autonomous, 2C) | **15-capability portfolio with dispositions** (D-03-01/HD-6, which already replaced the track grouping as the reference): 5 AI capabilities (C3, C5, C7-narration, C11, C13), 7 deterministic platform capabilities (C1, C2, C6, C10, C12, C14, C15), C4/C8 blocked, C9 rejected |
| Phase ladder 2A → 2B → 2C (read-only chat → confirmed writes → autonomous) | **No phase ladder and no autonomous layer.** Sequencing is the O1–O9/W1–W6 constraint set + readiness order; the maximum autonomy at end-state is C11 drafting proposals for C12's human-approved workflow. A future autonomy step would be a new human decision (Principle 10), not a planned phase |
| "Track Y — Autonomous Agents (Phase 2C). Future state… minimal operator prompting" | Removed as a target. Y1 → C11 (narrowed: detect/compare/summarise/draft only, D-02-04) + C12 (new deterministic statutory change management — a capability the source document does not name at all). Y2 → C13 + C14 (split). Y3 → C15 (deferred, deterministic) |
| Proactive Agents diagram: Prep Agent X2, Recon Agent X3, Trace Agent X4 | X2 → C6 (deterministic readiness service — no LLM in the critical path) + C7 (split-out anomaly detection, deterministic detector + optional narration). X3 → C8 (**blocked** until D-02-02/D-02-03 preconditions close). **X4 (Trace Agent) is removed entirely** — C9 rejected as a standalone capability; its intent is covered by C5 and (once unblocked) C8 |
| Track W: three agent modes (Navigation Guide / State Explainer / Action Planner) | C3 — one assistant with three modes, **current-state only**; the State Explainer's historical sub-case is carved out as C4 and blocked (D-02-03) |

## 3. What the revision changes — capabilities and claims

- **"Agent" framing corrected**: 7 of the document's capability areas are conventional deterministic engineering and are no longer described as agent work (F-02-03/F-02-04; the Stage 03 reclassification). Track P and Track V content survives almost intact as C1/C2 — but as platform engineering, not "Agent Foundation."
- **The As-Is gap register (GAP-1–6) is superseded** by the programme's confirmed findings and Stage 05's readiness matrix. The document's self-assessment was directionally right (cross-checked in F-02-08) but is no longer the authority; e.g. its "no consumer" event-store diagnosis stands, while the reconciliation workspace-scoping gap (F-01-33/D-02-02) and decorative-scoping pattern (F-05-03/F-07-01) are review findings the document never contained.
- **The tool list (V5, 10 read-only tools) is superseded** by Stage 08's `tool-contracts.md` (11 contracts) under the declarative wrapper/registry pattern (SS-2/SS-4), with `get_reconciliation` blocked until the D-02-02 repo-level fix lands.
- **Blocking Conditions 1–5 survive, strengthened**: (1) auth → C1 with membership/step-up designs; (2) PII sanitisation → C2 serialisation contract + SC-3 audit standard; (3) outbox/event gaps → C2 with forced-failure atomicity evidence; (4) `explain_component_trace` slot-filling → C5 with the null-trace refusal specified (the document's known gap, F-02-07) and a programmatic zero-hallucination check; (5) `agent_session_log` after auth → subsumed into the C2/tool-layer audit standard with the 7-year retention floor carrying DQ-008's caveat (the document's uncited "7yr retention" is now "keep at least 7y pending legal confirmation").
- **Security invariants are retained verbatim in substance** (workspace_id from JWT only; PII stripped; structured envelopes; no write tools; Decimal-as-string) and **extended** by Principle 11 (independent tool-layer scoping — inheriting scoping from an underlying query is never sufficient) and step-up re-auth on approvals (DEC-07-03).
- **Claims discipline added**: the revision embeds the overclaim table and measurement prohibitions (`positioning-and-claims.md` §3; D-04-01) — the source document made no claims-governance statement at all.

## 4. What the revision changes — sequencing

- The document's ordering rules (Track P first; V1+V2 together; rate limiting in the first chat sprint; session log after auth; confirmation protocol before write planning) are **preserved and absorbed** into the O1–O9 constraint set, which extends them with the review's additions: C7 behind the exception workflow (O4), C11 with/after C12 (O5), C13 never ahead of C14 (O6), the DQ-006/007/008 pre-build human gates (O8/O9), and the baseline-before-build windows W1–W6.
- Sprint labels (A2/A3/A4) and the phase timeline are dropped; Stage 13 owns sequencing within the constraint set.

## 5. What the revision carries forward without re-deciding (flagged, not endorsed)

The **Technology Decisions** table (primary/fallback LLMs, Vercel AI Gateway routing, APScheduler, ephemeral-session + audit-log history, narrow tool granularity) was locked by the repo's arch-council on 2026-06-11 and was **not re-litigated by this review** (DEC-12-05). Nothing in Stages 01–11 contradicts these choices; the workspace-id/tool-granularity/history rows are independently re-affirmed by the review's own designs. The model/routing/scheduler rows are dated pre-review operational choices — the revision carries them as standing intent **subject to normal re-validation at Phase 3 build time** (model availability, pricing, and gateway posture are environment facts this programme did not verify). This is a currency flag, not a proposal to change them.

## 6. For Stage 13

Approve (or amend) this disposition as part of roadmap approval. On approval: (a) D-02-01/HD-2 resolves — the record should state the document is superseded by the approved direction outputs; (b) a Phase 3 work item rewrites/replaces the HTML (both copies — `docs/architecture/` and the `frontend/public/` mirror) from the four direction outputs; (c) until that lands, the existing file keeps its "NEEDS REVISION" pill and remains stated intent only, per the source register's standing treatment.
