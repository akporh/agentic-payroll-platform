# Stage 07: Security & Identity — Context

## Status
not-started

## Binding decisions inherited from Stage 02 (pre-scope — do not re-litigate)

Recorded 2026-07-12, full detail in `_core/HUMAN-DECISIONS.md` HD-3:

- **D-02-02**: `payroll_reconciliation` repository-level workspace-scoping fix (F-01-33) is mandatory and is a precondition for any agent tool touching it (e.g. `get_reconciliation`). Tool-layer workspace-ownership validation is additionally mandatory as defence in depth — explicitly not an acceptable permanent substitute for the repository-level fix. This stage should verify both layers are actually in place before any agent tool goes live, not just one.

## Binding decisions inherited from Stage 03 (pre-scope — do not re-litigate)

Recorded 2026-07-12, full detail in `_core/HUMAN-DECISIONS.md` HD-6 (D-03-01) and `03-agent-portfolio/outputs/tool-portfolio-matrix.md`:

- The revised 15-capability portfolio (`03-agent-portfolio/outputs/agent-capability-matrix.md`) is **approved** — this stage reviews security against that portfolio, not the source architecture document's original tracks.
- **Condition 14**: every tool must have independent workspace-ownership verification — this stage should verify the actual implementation pattern (e.g. a shared decorator/middleware, per Stage 03's `stage-08-handoff.md` recommendation) is applied consistently across all 11 tools in `03-agent-portfolio/outputs/tool-portfolio-matrix.md` (the original 10 plus the new workspace-catalog tool for C13).
- **Conditions 2–3**: `get_reconciliation` and any tool touching `payroll_reconciliation` remain blocked until the repository-level fix lands; this stage should verify tool-layer enforcement specifically once that fix is confirmed by Stage 05.

## Scope

_To be defined when this stage is opened. Do not populate ahead of the gate — scope defined in advance of the prior stage closing risks anchoring on assumptions instead of the prior stage's confirmed findings. The binding decision above is a constraint, not the scope itself._

## Questions this stage answers

_To be defined at stage start._

## Explicitly out of scope

_To be defined at stage start._

## Inputs consumed

_Confirmed findings (F-) from prior gated-closed stages, plus any new sources — recorded in `_inputs/source-register.md`._

## Next action

**Await approval to begin Stage 07 (Stages 03–06 come first).**
