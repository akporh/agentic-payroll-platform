# Stage 02: Product Thesis — Context

## Status
complete (gate closed 2026-07-12, HD-GATE-02) — 14 confirmed findings, 0 draft, 0 parked; all 4 human decisions resolved (D-02-01–04) via `stage-02-review-decision-prompt.md`. Stage 03 not started.

## Scope

Evaluate whether the proposed product boundary is sound: *"AI supports judgement, investigation, interpretation and coordination, while deterministic platform services remain responsible for payroll calculations, statutory rules, authoritative state transitions and financial record mutation."*

This stage determines where AI is justified, where conventional automation is safer, and where the proposed direction (as captured in `docs/architecture/agent-layer-architecture.html`, the Phase 2 Agent Layer architecture document, status "NEEDS REVISION," arch-council reviewed 2026-06-11) is unclear or unsound. Individual agent-by-agent review is Stage 03's remit, not this stage's.

Six required investigations (per the prompt): (1) reconstruct the intended product thesis, separating stated principles / implied assumptions / current implementation / future intent / unresolved decisions; (2) classify every proposed capability by type; (3) test the deterministic/AI boundary against the Stage 01 evidence base; (4) test whether "agentic" framing is actually warranted for each proposed capability; (5) evaluate whether the thesis depends on platform foundations Stage 01 found not yet reliable; (6) evaluate the 10 candidate non-negotiable product principles.

## Questions this stage answers

- What does the current architecture document actually propose AI should and should not do, and how much of that is implemented vs. aspirational?
- For each proposed capability, is an LLM necessary, or would a simpler mechanism (validation, deterministic automation, analytics) be safer?
- Is the deterministic/AI boundary the document draws consistent with what Stage 01 found to actually be true of the deterministic core?
- Does the proposed thesis assume platform foundations (workspace scoping, event completeness, trace completeness, historical reproducibility) that Stage 01 found to be incomplete?
- Which of the 10 candidate non-negotiable principles should be retained, revised, removed, or is something missing?

## Explicitly out of scope

- Detailed review of individual agents/tools (Stage 03)
- Full platform-readiness assessment (Stage 05) — this stage only flags where a Stage 01 gap materially undermines the thesis itself
- Designing the target architecture (Stage 12) or roadmap (Stage 13)
- Legal/compliance conclusions (Stage 06 receives compliance questions raised here)
- Assuming AI is required anywhere, or treating conversational UI as inherently agentic
- Modifying production code

## Inputs consumed

- Stage 01 (gated-closed 2026-07-12, HD-GATE-01): all 46 confirmed findings in `01-current-operating-model/findings.md`, especially F-01-19/20 (readiness pre-check vs. silent exclusion), F-01-24/28 (legacy executor gap), F-01-33 (reconciliation workspace-scoping gap), F-01-38 (dead status branches), F-01-40 (audit coverage gap), F-01-45/46 (statutory-rule maintenance is migration-only)
- `docs/architecture/agent-layer-architecture.html` — the current agent-layer architecture proposal (treated as stated intent, not proof of implementation — nothing in Tracks P/V/W/X/Y is built yet, per its own phase-timeline)
- `Clients/Sandy/_PRODUCT/EP-004_phase2-agentic/` (`_epic.md`, `FEAT-020`, `FEAT-021`) — confirmed as stub/TBD-status product docs, not additional design detail beyond the architecture document
- New sources recorded in `_inputs/source-register.md`

## Next action

**Await approval to begin Stage 03 — Agent Portfolio.**
