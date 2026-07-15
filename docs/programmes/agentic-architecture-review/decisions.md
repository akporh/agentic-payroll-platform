# Decisions — Agentic Architecture Review Programme

Programme-level decisions only (D-*). Review-internal human decisions (stage gates, finding resolutions) live in `_core/HUMAN-DECISIONS.md` (HD-*) and are not duplicated here.

---

## D-001 — Register the review as a programme, full-arc scope (2026-07-15)

**Decided by:** Michael (chat, 2026-07-15).

**Decision:** The agentic architecture review is registered as a programme under `docs/programmes/`, with **full-arc scope**:

- Phase 1 `review-execution` — finish the review (Stage 05 gate → Stage 13), authorised retrospectively (the review began before programme registration; its stage governance — `WORKFLOW.md`, `review-state.md`, `_core/` — is unchanged).
- Phase 2 `roadmap-consolidation` — placeholder, **not authorised**: cross-reference the Stage 13 approved roadmap with the audit programme's 8 remediation programmes and `docs/ROADMAP.md` into one build order.
- Phase 3 `adoption` — placeholder, **not authorised**: adopt the approved build order into `docs/product/` and `docs/ROADMAP.md`.

**Alternative considered and rejected:** review-only scope (programme ends at Stage 13; consolidation as a separate future programme).

---

## D-002 — Physical move under `docs/programmes/`, with a living-files-only path rewrite (2026-07-15)

**Decided by:** Michael (chat, 2026-07-15 — "convert paths and move to programme folder" in response to a wrapper-vs-move question).

**Decision:** `docs/agentic-architecture-review/` is physically moved to `docs/programmes/agentic-architecture-review/` via `git mv` (history preserved). Because cross-references are repo-relative path strings in prose (not resolvable links), the accompanying rewrite is a recorded mechanical search-and-replace of `docs/agentic-architecture-review` → `docs/programmes/agentic-architecture-review`, applied to **living files only**:

- All files inside the moved review workspace itself.
- Four living external files: `docs/sprints/README.md`, `docs/product/README.md`, `docs/programmes/product-traceability/PHASES.md` (forbidden-path lists still governing future phases), `docs/programmes/product-traceability/phase-inputs.yaml`.

**Deliberately NOT rewritten** (historical records citing the path as it correctly existed at the time; per the established principle that completed history is never rewritten): the `docs/diagnostics/` prompt/plan/retrospective records, `docs/programmes/product-traceability/runs/*`, `critic-review-phase-2.md`, and `phase-3-inputs.md`. Old-path mentions in those files are expected and correct; `git log --follow` resolves them.

**Consequence accepted:** any future reader of a historical record must know the review moved on 2026-07-15 — recorded here, in the review `README.md`, and in the `docs/programmes/README.md` index.
