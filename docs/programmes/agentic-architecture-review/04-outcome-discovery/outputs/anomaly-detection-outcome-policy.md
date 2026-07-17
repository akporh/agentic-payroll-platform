# Stage 04 Output: Input Anomaly Detection (C7) — Outcome Policy

This is an outcome and calibration-approach framing, not a final production algorithm — that belongs to Stage 08, per `CONTEXT.md`'s explicit instruction.

**Calibration approach approved 2026-07-13 (D-04-01, `_core/HUMAN-DECISIONS.md` HD-7)**: a layered combination, introduced in stages — (1) absolute thresholds at launch, configurable and explainable, never LLM-generated/adjusted; (2) period-on-period variance as a second, additive layer once a minimum history window exists, alerting with current value/baseline/variance shown, never replacing the hard limits; (3) peer-pattern comparison explicitly deferred, reconsidered only with sufficient comparable employee volume and reliable grade/role grouping, and never cross-tenant; (4) C7 must not ship without the exception-resolution workflow; (5) shadow-mode rollout where practical, with confirmed-error-capture / confirmed-correct-dismissal / later-discovered-unflagged-error measurement, versioned and auditable threshold changes, and LLM use restricted to optional narration only. Final statistical formulas, numeric thresholds, and the minimum-history-window value remain for Stage 08 design and later product calibration — not invented here.

## The user outcome, defined before any threshold

The outcome is: **an operator is warned about a payroll input that looks like a data-entry error, before it reaches a run, with enough context to decide in seconds whether it's real.** This is deliberately not framed as "detect anomalies" in the abstract — anomaly detection is the mechanism, not the outcome. The outcome is *catching entry errors early enough that they never become a payroll mistake*, which reframes the success metric away from "how many anomalies were flagged" and toward "how many entry errors reached a run undetected" (ideally zero, measured as a negative/absence metric — see `measurement-framework.md`).

## What kinds of anomalies matter operationally

Based on the payroll domain (Stage 01's confirmed `payroll_input` model — quantities for overtime, allowances, deductions, per employee per period, F-01-17):

1. **Magnitude errors** — a value an order of magnitude off from the employee's own history (400 hours instead of 40) — the highest-value case, since it's usually an unambiguous typo
2. **Unit-confusion errors** — a value plausible in the wrong unit (e.g. an amount entered where a quantity was expected) — harder to detect without knowing the input's semantic type, and likely out of scope for a first version
3. **Missing/zero-when-expected** — an employee who reliably has overtime every period suddenly has none — a different detection shape (absence, not magnitude) and arguably belongs more naturally with the readiness service (C6) than with anomaly detection; flagged here as a boundary question for Stage 08, not resolved

## Distinguishing three calibration approaches (not deciding between them)

| Approach | What it catches | Tradeoff |
|---|---|---|
| **Absolute threshold** (e.g. "flag any OT quantity > 100 hours") | Extreme, unambiguous errors regardless of history | Simple, explainable, but blind to an employee whose normal pattern is already unusual (either direction) |
| **Period-on-period variance** (e.g. "flag if > 3x the employee's own trailing average") | Errors relative to the individual's own pattern | Needs a minimum history window (a new employee has no baseline); more sensitive to genuine, legitimate changes (a one-off large OT period) |
| **Peer-pattern comparison** (e.g. "flag if far outside the range for this employee's grade/role") | Errors an individual-history approach would miss for a new employee | Requires enough peer volume per grade/role to be statistically meaningful — likely not viable for small client workspaces |

**Resolved (D-04-01, 2026-07-13)**: a layered combination of (1) absolute threshold at launch and (2) period-on-period variance as a second layer, with (3) peer-pattern comparison explicitly deferred — see the approval note above and `decisions.md` for full detail. This was exactly the kind of threshold/calibration question that could not be resolved by evidence review alone.

## False positives and false negatives — how to measure, not yet how to tune

- **False positive**: a flagged value that was, in fact, correct. Measured by tracking dismiss-with-confirmation-correct rate on the exception queue (once built — see `exception-resolution-outcome.md`).
- **False negative**: an actual entry error that reached a run without being flagged. Harder to measure directly; the practical proxy is *retroactive*: does a later-discovered entry error (found via reconciliation, client complaint, or manual review) show up in the flagged history for that period? If not, it was a false negative. This requires the exception-resolution workflow to exist first, so there's a record to check against.
- Neither metric is measurable today because no anomaly-detection mechanism or exception-tracking record exists yet — this is a genuine baseline gap (see `measurement-framework.md`).

## What happens after an anomaly is flagged

This is the single most important open question, and it is *not* a Stage 04 or Stage 08 question alone — it depends entirely on the exception-resolution-workflow outcome defined in `exception-resolution-outcome.md`. An anomaly with nowhere to go (no owner, no resolution path, no closure record) has no value regardless of how good the detection algorithm is. This dependency is the primary reason `outcome-prioritisation.md` classifies the exception-resolution-workflow outcome as **pursue now**, ahead of C7's own detection mechanism.

## Summary for Stage 08

- Build deterministic/statistical detection first (Principle 9); LLM narration is optional and secondary, never the detector.
- The calibration approach is decided (D-04-01): absolute thresholds at launch, period-on-period variance as a second layer once a minimum history window exists, peer-pattern comparison deferred. Stage 08 designs the mechanism within this approved shape — final formulas, numeric thresholds, and the minimum-history-window value are Stage 08's/product calibration's to set, not re-open the approach itself.
- Do not build C7 in isolation from the exception-resolution-workflow — sequence them together (now a binding condition of D-04-01, not just a recommendation) or C7's output has nowhere to go, the same coherence gap Stage 03 flagged for C11→C12.
- Shadow-mode rollout, versioned/auditable threshold changes, and the three named calibration-governance metrics (confirmed-error capture, confirmed-correct-dismissal rate, later-discovered unflagged errors) are binding per D-04-01, not optional refinements.
