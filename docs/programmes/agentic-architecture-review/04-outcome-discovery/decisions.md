# Stage 04: Outcome Discovery — Decisions

Stage-local log of human decisions made during this stage. Master log: `_core/HUMAN-DECISIONS.md`. Format matches `_core/HUMAN-DECISIONS.md`.

## Gate

- **Gate opened**: 2026-07-13, by human reviewer (Michael Emedo) — populated `CONTEXT.md` directly on GitHub with the instruction "Execute Stage 04 from this CONTEXT.md, then stop at awaiting-review."
- **Gate closed**: 2026-07-13 — HD-04-1 resolved via `stage-04-review-decision-prompt.md` (D-04-01, `_core/HUMAN-DECISIONS.md` HD-7). Stage 04 marked `complete`.

## Inherited binding decisions applied (not re-litigated)

D-02-01 through D-02-04 and D-03-01 (`_core/HUMAN-DECISIONS.md` HD-2–HD-6) were treated as gates throughout — C4/C8 remain blocked, C9 remains rejected, C11 remains restricted, C1/C2/C6/C10/C12/C14 remain deterministic, per `CONTEXT.md`'s explicit "do not re-litigate" list. See F-04-08 for the explicit confirmation these were not reopened.

## HD-04-1 → resolved by D-04-01: C7 calibration approach — layered, staged combination approved
- **Raised by**: F-04-02
- **Decision**: A layered combination, introduced in stages: (1) launch baseline of configurable, explainable absolute thresholds (never LLM-generated/adjusted); (2) a second layer of period-on-period variance comparison, added only where a minimum history window exists, as an additional flag alongside hard limits (not a replacement), with the alert showing current value/baseline/variance; (3) peer-pattern comparison explicitly deferred — not part of the initial design, reconsidered only with sufficient comparable employee volume and reliable grade/role grouping, and never comparing employees across tenants/workspaces; (4) C7 must not ship without the exception-resolution workflow (F-04-01) to assign/review/confirm/dismiss/close alerts; (5) calibration governance requires shadow-mode rollout where practical, measurement of confirmed-error capture / confirmed-correct-dismissal rate / later-discovered unflagged errors, versioned and auditable threshold changes, and LLM use restricted to optional narration only — never detection or threshold selection.
- **Made by**: Michael Emedo, via `stage-04-review-decision-prompt.md` (D-04-01)
- **Context**: This is exactly the calibration question F-04-02 identified as undecidable from repository evidence alone — final statistical formulas, numeric thresholds, and the minimum-history-window value are explicitly preserved for Stage 08 design and later product calibration, not invented here.
- **Affects**: F-04-02; `outputs/anomaly-detection-outcome-policy.md`, `outputs/outcome-prioritisation.md`, `outputs/measurement-framework.md` (all updated); Stage 08 (mechanism design within this decided approach)

## Next action

**Stage 04 is complete. Await approval to begin Stage 05 — Platform Readiness.**
