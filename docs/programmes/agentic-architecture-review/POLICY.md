# Policy — Agentic Architecture Review Programme

Fixed execution policy for the `agentic-architecture-review` programme. The executor must not weaken it. Any change to this file requires human approval and is itself a consequential decision under `decisions.md`.

## Autonomy mode

`stage-gated` (Phase 1) / `phase-gated` (Phases 2–3)

Phase 1 inherits the review's own gating, which is **stricter** than phase-level autonomy: a stage may be investigated autonomously, but no stage begins until the prior stage's gate is explicitly passed by a human (see `WORKFLOW.md`). Phases 2 and 3 may not begin at all without a recorded human authorisation in `decisions.md`.

## Executor may

- Investigate within the currently open review stage per `WORKFLOW.md` and the stage's `CONTEXT.md`.
- Read repository evidence (source code, migrations, tests, docs, git history) read-only.
- Write within `docs/programmes/agentic-architecture-review/` only, respecting the review's own stage/finding rules.
- Record findings as draft and promote them only per `_core/EVIDENCE-STANDARD.md` and `_core/FINDING-SCHEMA.md`.
- Update `review-state.md` (stage-level) and `state.md` (phase-level) to reflect actual state.

## Executor may not

- Modify production code (`backend/`, `frontend/`, `migrations/`) — hard rule inherited from the review's README.
- Modify `docs/audit-program/` (closed record), `docs/ROADMAP.md`, `docs/product/`, `docs/sprints/**`, `docs/stories/**`, or any other tree outside this programme's folder — until and unless a later phase's authorisation explicitly grants a named path.
- Begin a review stage whose predecessor's gate has not been explicitly passed.
- Begin Phase 2 or Phase 3, or treat its own recommendation as human approval.
- Weaken the review's evidence standard, finding schema, or severity model (`_core/`).
- Modify user-home skills (`~/.claude/**`) or add dependencies.

## Human approval required for

- Every stage gate (the existing `HD-GATE-*` pattern in `_core/HUMAN-DECISIONS.md`).
- Authorisation of Phase 2 (`roadmap-consolidation`) and Phase 3 (`adoption`), including their exact allowed-path grants.
- Any change to this file, `PROGRAMME.md`, or the review's `_core/` binding standards.
- Any conflict between the Stage 13 approved roadmap and the audit programme's backlog that cannot be resolved by evidence (Phase 2 surfaces these as decisions, never resolves them silently).

## Stop conditions

Stop and record an exception in `exceptions.md` when:

- Authoritative sources materially contradict one another and reading further cannot resolve it.
- A required write falls outside the authorised paths.
- A destructive or irreversible change would be required.
- Sensitive or personal information is discovered.
- Evidence needed to meet the review's confirmation standard cannot be accessed.

Routine naming, formatting, and evidence-collection questions are **not** stop conditions.

## Source-of-truth boundaries (fixed for this programme)

- `review-state.md` owns stage-level review state.
- `state.md` owns phase-level programme state.
- `_core/HUMAN-DECISIONS.md` owns review-internal human decisions (HD-*).
- `decisions.md` owns programme-level decisions (D-*).
- `docs/audit-program/audit-state.md` owns the audit programme's record — read-only here.
- `docs/product/` registries own product-hierarchy truth — writable only under a Phase 3 grant, under the product-traceability programme's conventions.

This boundary list may only be changed by explicit human approval recorded in `decisions.md`.
