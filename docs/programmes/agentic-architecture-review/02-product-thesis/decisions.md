# Stage 02: Product Thesis — Decisions

Stage-local log of human decisions made during this stage. Master log: `_core/HUMAN-DECISIONS.md`. Format matches `_core/HUMAN-DECISIONS.md`.

## Gate

- **Gate opened**: 2026-07-12, by human reviewer (Michael Emedo) — pointed to `stage-02-product-thesis-prompt.md` on GitHub as the instruction to begin Stage 02.
- **Gate closed**: 2026-07-12 — all 4 human decisions resolved via `stage-02-review-decision-prompt.md` (commit `dbbebae`). Stage 02 marked `complete` in `review-state.md`.

## Human decisions — resolved

### HD-02-1 → resolved by D-02-01: Architecture document status
- **Raised by**: F-02-02
- **Decision**: The architecture document's `NEEDS REVISION` status remains open. This review is the formal revision path. The document is not approved until Stage 12 synthesises the target direction and Stage 13 records approval.
- **Made by**: Michael Emedo, via `stage-02-review-decision-prompt.md` D-02-01
- **Affects**: F-02-02; Stage 12 (Target Direction — treats this document as a revisable input, not a settled design, until Stage 13); Stage 13 (Approved Roadmap — the only stage that may record approval)

### HD-02-2 → resolved by D-02-02: Reconciliation workspace scoping
- **Raised by**: F-02-06
- **Decision**: Correct repository-level `payroll_reconciliation` workspace scoping (F-01-33) *before* `get_reconciliation` is exposed as an agent tool. Tool-layer workspace-ownership validation is additionally mandatory as defence in depth — not a substitute for the repository-level fix, and not an acceptable permanent resolution on its own.
- **Made by**: Michael Emedo, via `stage-02-review-decision-prompt.md` D-02-02
- **Affects**: F-02-06; Stage 03 (Agent Portfolio — `get_reconciliation` tool blocked on this fix); Stage 05 (Platform Readiness — repo-level fix is now a scoped precondition, not an open question); Stage 07 (Security & Identity — defence-in-depth requirement)

### HD-02-3 → resolved by D-02-03: Historical reproducibility
- **Raised by**: F-02-09
- **Decision**: Historical reproducibility is a **launch precondition** for any capability that explains, traces, or investigates historical payroll outcomes — not a general accepted residual risk to disclose to operators. Track W may proceed *selectively* for current-state navigation/assistance that does not depend on reconstructing historical truth. Historical explanation and all of Track X's reconciliation/trace investigation must remain blocked until the relevant snapshot, mutation, and reproducibility gaps (F-01-27, F-01-29, F-01-38) are resolved.
- **Made by**: Michael Emedo, via `stage-02-review-decision-prompt.md` D-02-03
- **Affects**: F-02-09, F-02-05, F-02-11; Stage 03 (splits Track W into an unblocked current-state subset and a blocked historical-explanation subset; blocks all of Track X's investigation agents); Stage 05 (F-01-27/F-01-29/F-01-38 closure is now a named launch precondition, not a disclosed risk); Stage 08 (Technical Architecture)

### HD-02-4 → resolved by D-02-04: Statutory-rule change management
- **Raised by**: F-02-12
- **Decision**: Statutory-rule change management is scoped as a **separate deterministic platform and compliance capability**, independent of Y1. Y1 may later detect external regulatory changes, compare evidence, and prepare proposals — it must **not** directly author, execute, or deploy production Alembic migrations.
- **Made by**: Michael Emedo, via `stage-02-review-decision-prompt.md` D-02-04
- **Affects**: F-02-12; Stage 05 (Platform Readiness — new deterministic capability to scope); Stage 06 (Compliance & Controls — compliance-owned change-management workflow); Stage 08 (Technical Architecture — mechanism design); Track Y sequencing (Stage 03/11)

## Next action

**Stage 02 is complete. Await approval to begin Stage 03 — Agent Portfolio.**
