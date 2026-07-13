# Stage 04: Outcome Discovery — Decisions

Stage-local log of human decisions made during this stage. Master log: `_core/HUMAN-DECISIONS.md`. Format matches `_core/HUMAN-DECISIONS.md`.

## Gate

- **Gate opened**: 2026-07-13, by human reviewer (Michael Emedo) — populated `CONTEXT.md` directly on GitHub with the instruction "Execute Stage 04 from this CONTEXT.md, then stop at awaiting-review."
- **Gate closed**: not yet — investigation complete; per `CONTEXT.md`'s completion procedure, Stage 04 is marked `awaiting-review`, not `complete`.

## Inherited binding decisions applied (not re-litigated)

D-02-01 through D-02-04 and D-03-01 (`_core/HUMAN-DECISIONS.md` HD-2–HD-6) were treated as gates throughout — C4/C8 remain blocked, C9 remains rejected, C11 remains restricted, C1/C2/C6/C10/C12/C14 remain deterministic, per `CONTEXT.md`'s explicit "do not re-litigate" list. See F-04-08 for the explicit confirmation these were not reopened.

## Human decisions required (raised by this stage)

### HD-04-1: Input anomaly detection (C7) calibration approach
- **Raised by**: F-04-02
- **Question**: which calibration approach — absolute threshold, period-on-period variance, peer-pattern comparison, or a combination — should C7 use to determine what counts as an "anomalous" payroll input quantity?
- **Why this needs a human call**: this depends on the client base's actual data patterns and an acceptable false-positive/false-negative tradeoff — not derivable from repository evidence.
- **Affects**: C7's design (Stage 08), the anomaly-detection outcome policy (`outputs/anomaly-detection-outcome-policy.md`)

Per the finding-discipline principle applied consistently since Stage 03 ("do not create artificial human decisions where evidence and inherited principles already resolve the issue"), this is the **only** decision this stage found requiring human adjudication. Every other open question (the C11/C12 impact-assessment boundary, the structural-configuration research item) is forwarded to a later stage as a design/research task, not raised here as a decision needing this reviewer's judgment now.

## Next action

**Human review of Stage 04 outputs; gate approval required before Stage 05, and a calibration-approach decision (HD-04-1) before Stage 08 can design C7.**
