# Stage 08: Technical Architecture — Context

## Status
not-started

## Binding decisions inherited from Stage 02 (pre-scope — do not re-litigate)

Recorded 2026-07-12, full detail in `_core/HUMAN-DECISIONS.md` HD-3–HD-5:

- **D-02-02**: any tool touching `payroll_reconciliation` requires both the repository-level workspace-scoping fix and independent tool-layer validation — design both, not either/or.
- **D-02-03**: historical reproducibility (F-01-27/29/38) must be resolved before designing any mechanism that explains/reconstructs historical payroll outcomes (Track X investigation agents, Track W historical-explanation mode). Design work for these can proceed on the resolution mechanism itself, but the agent-facing capability built on top is launch-blocked until it's resolved.
- **D-02-04**: design the statutory-rule change-management mechanism as its own deterministic capability, separate from any AI compliance-detection design (Y1). Y1's design must not include migration-authoring/execution/deployment capability.
- Also carried from Stage 02: what "dry-run payroll" means mechanically for the Onboarding Agent (Y2) safety gate — does it exercise the real sequential executor/snapshot path, or a separate simulation (F-02-10)? This needs a concrete answer, not an assumption.

## Scope

_To be defined when this stage is opened. Do not populate ahead of the gate — scope defined in advance of the prior stage closing risks anchoring on assumptions instead of the prior stage's confirmed findings. The binding decisions above are constraints, not the scope itself._

## Questions this stage answers

_To be defined at stage start._

## Explicitly out of scope

_To be defined at stage start._

## Inputs consumed

_Confirmed findings (F-) from prior gated-closed stages, plus any new sources — recorded in `_inputs/source-register.md`._

## Next action

**Await approval to begin Stage 08 (Stages 03–07 come first).**
