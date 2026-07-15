# Decisions — Agentic Architecture Review Programme

Programme-level decisions only (D-*). Review-internal human decisions (material finding resolutions and final approvals) live in `_core/HUMAN-DECISIONS.md` (HD-*) and are not duplicated here.

---

## D-001 — Register the review as a programme, full-arc scope (2026-07-15)

**Decided by:** Michael (chat, 2026-07-15).

**Decision:** The agentic architecture review is registered as a programme under `docs/programmes/`, with **full-arc scope**:

- Phase 1 `review-execution` — finish the review (Stage 05 gate → Stage 13), authorised retrospectively.
- Phase 2 `roadmap-consolidation` — placeholder, **not authorised**.
- Phase 3 `adoption` — placeholder, **not authorised**.

**Alternative considered and rejected:** review-only scope.

---

## D-002 — Physical move under `docs/programmes/`, with a living-files-only path rewrite (2026-07-15)

**Decided by:** Michael (chat, 2026-07-15).

**Decision:** `docs/agentic-architecture-review/` was moved to `docs/programmes/agentic-architecture-review/` via `git mv`, with living-file path references updated and completed historical records left unchanged.

---

## D-003 — Decision-gated continuous execution with independent critic (2026-07-15)

**Decided by:** Michael (chat, 2026-07-15 — approved improvement of the programme operating model).

**Decision:** Phase 1 changes from manual approval at every routine stage boundary to **decision-gated continuous execution**.

- A primary executor runs the currently authorised stage from its populated `CONTEXT.md`.
- An independent critic reviews the stage context, findings, evidence, outputs, handoffs and completion criteria.
- When the critic returns `PASS` and there is no blocking human decision, the controller may close the stage, populate/open the next stage context and continue automatically.
- The programme stops for the human reviewer only when a material decision is required, evidence is irreconcilably contradictory or unavailable, scope/policy must change, a write would exceed authorised paths, or the final Stage 13 approval pack is ready.
- Non-blocking design questions and later-stage specifications are recorded in `decision-queue.md` and forwarded without stopping execution.
- The human reviewer retains approval of all material product/risk decisions, Phase 2/3 authorisation and final Stage 13 roadmap approval.

**Safety condition:** the critic must be independent of the primary stage execution pass. It may use the same model family only if run as a separate role with no authority to rewrite findings silently; all critic findings and disposition must be recorded.

---

## D-004 — Session independence of every loop iteration (2026-07-15)

**Decided by:** Michael (chat, 2026-07-15).

**Decision:** Every iteration of the Phase 1 continuous loop must be executable from repository state alone — no dependence on the conversational context of the session that ran the previous iteration.

- All state needed to resume (stage status, findings disposition, handoffs, open questions, critic reports) must be persisted to the programme's state files **before** a session ends or a stage is closed.
- A fresh session per stage or per critic pass is the preferred operating pattern, not an exception to be worked around.
- If a session discovers that resuming required information not present in the state files, that is a defect in the previous iteration's close-out and must be fixed by strengthening the persisted state, not by relying on session memory.

**Rationale:** long-running programme work spans many sessions; conversational context is lossy and non-auditable, while repository state is durable and reviewable.
