# Stage 03: Agent Portfolio — Context

## Status
complete (gate closed 2026-07-12, HD-GATE-03) — 16 confirmed findings, 0 draft, 1 parked note (P-03-1); the 15-capability portfolio was approved (D-03-01) via `stage-03-review-decision-prompt.md`. Stage 04 not started.

## Binding decisions inherited from Stage 02 (pre-scope — do not re-litigate)

Recorded 2026-07-12, full detail in `_core/HUMAN-DECISIONS.md` HD-2–HD-5 and `02-product-thesis/outputs/stage-03-handoff.md`:

- **D-02-01**: the agent-layer architecture document remains unapproved; review every track as a proposal under revision, not a spec.
- **D-02-02**: `get_reconciliation` (and any tool touching `payroll_reconciliation`) is blocked until the repository-level workspace-scoping fix (F-01-33) lands; tool-layer validation is required in addition, not instead.
- **D-02-03**: historical reproducibility (F-01-27/29/38) is a launch precondition. Track X's reconciliation/trace investigation agents and any historical-outcome explanation in Track W are blocked until resolved. Track W's current-state navigation/assistance is not blocked.
- **D-02-04**: statutory-rule change management is a separate deterministic capability, independent of Y1. Y1 may detect/compare/propose only — never author, execute, or deploy a migration.

## Scope

Review the proposed agent/tool portfolio (Tracks P, V, W, X, Y plus their tool contracts) in full detail and produce a coherent recommended portfolio — not a critique of the existing document's labels. For every capability, determine a portfolio disposition: keep / revise / merge / split / defer / block / reject / reclassify as deterministic platform work. Review at capability level, not accepting the document's track grouping as fixed.

Eight required investigations: (1) agent boundary/overlap analysis across 8 named pairs; (2) deterministic-vs-probabilistic responsibility, applying Stage 02 Principle 9 actively; (3) Track W's safe current-state launch boundary, explicitly excluding historical explanation per D-02-03; (4) full Track X portfolio review (Prep, Reconciliation, Trace, proactive/event automation, write-capable behavior); (5) full Track Y portfolio review (Compliance Monitoring restricted per D-02-04; Onboarding Assistance split between AI-appropriate and deterministic parts); (6) tool-contract-by-tool-contract review, requiring independent workspace-ownership enforcement per tool; (7) UX/product-surface recommendation per retained capability (chat not default); (8) portfolio coherence across preparation/exception-detection/investigation/explanation/decision-support/onboarding/compliance.

## Questions this stage answers

- Which of the document's proposed "agents" are actually one operator assistant with multiple modes, which are genuinely independent, and which are deterministic services mislabeled as agents?
- For each retained capability: exact data/tools required, LLM role (if any), permitted reads/writes, prohibited actions, required human approval, evidence shown to the operator, failure modes.
- What is Track W's safe, current-state-only launch scope, and what does each mode refuse/limit and why?
- Which Track X/Y capabilities are blocked by D-02-02/D-02-03/D-02-04, and what are their future design constraints (not full designs)?
- For every proposed tool: should it exist, is it read-only or mutating, what's its workspace-scoping mechanism, does it return facts-only or also conclusions that should be computed deterministically instead?
- What UX surface (chat, dashboard, readiness panel, exception queue, etc.) fits each retained capability?
- Does the resulting portfolio form a coherent operating model, or are there missing handoffs / duplicated ownership / orphaned capabilities?

## Explicitly out of scope

- Designing the final target architecture (Stage 12) or the approved roadmap (Stage 13)
- Full outcome discovery (Stage 04) — new outcome opportunities noticed here are handed off, not expanded
- Full platform-readiness review (Stage 05) — platform prerequisites are handed off, not resolved here
- Fully designing the structured confirmation/pending-action protocol — only required Stage 08 specification questions are recorded
- Legal/compliance conclusions (Stage 06 receives compliance questions)
- Re-opening or re-litigating D-02-01 through D-02-04 — these are binding gates
- Modifying production code

## Inputs consumed

- Stage 01 (gated-closed): all 46 confirmed findings, especially F-01-27, F-01-29, F-01-33, F-01-38, F-01-41, F-01-44, F-01-45, F-01-46
- Stage 02 (complete, gated-closed): all 14 confirmed findings, all 5 outputs (especially `stage-03-handoff.md`, `capability-classification-matrix.md`, `deterministic-ai-boundary.md`, `non-negotiable-product-principles.md`), and binding decisions D-02-01–04 (`_core/HUMAN-DECISIONS.md` HD-2–HD-5)
- `docs/architecture/agent-layer-architecture.html` — treated as a proposal under revision (D-02-01), not a spec to implement as written
- New sources recorded in `_inputs/source-register.md`

## Next action

**Await approval to begin Stage 04 — Outcome Discovery.**
