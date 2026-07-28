# Stage 10 Output: C7 Calibration Governance (Q4)

Governance for C7's calibration under D-04-01: shadow-mode duration and exit, review cadence and decision rules for the three fixed metrics, threshold-change audit flow, and detector-version replay discipline. The metric *definitions* are fixed (D-04-01 — not re-opened here); the detection formulas and launch parameters are fixed (DEC-08-12, `anomaly-detection-design.md` §§2–3). This document adds only cadence, decision rules, and evidence form. Gate: CG-7.

## 1. Fixed inputs (consumed, not re-derived)

- **Three governance metrics** (D-04-01): confirmed-error capture, confirmed-correct dismissal (false-positive rate), later-discovered unflagged errors (false negatives) — all derivable from `exception_record.resolution_code` + detector replayability, no extra instrumentation (`anomaly-detection-design.md` §5).
- **Shadow mode mechanics**: platform config flag; records created `severity = INFO` + `shadow: true`, excluded from operator-facing counts (design §4; UX behaviour 13 keeps the exclusion honest at the UI).
- **Threshold storage**: versioned `anomaly_threshold` rows, domain-1 audited, prior versions retained (design §2).
- **Early-warning signal**: dismiss-without-review rate (Stage 04's false-positive-fatigue guard; the UX dismiss-friction behaviour 16 is its interface counterpart).

## 2. Shadow mode: duration and exit criteria (DEC-10-08)

- **Entry**: C7 deploys shadow-on (D-04-01: shadow-first). Entry date recorded (config change = domain-1 audit event).
- **Minimum duration**: **3 full payroll cycles** AND **≥ 20 C7 exception records reaching a terminal resolution code**. Rationale: 3 cycles matches the detector's own minimum-history logic (below 3 data points a rate is an anecdote); 20 terminal records is the floor below which the false-positive rate has no meaningful denominator. Both conditions, not either.
- **Exit criteria** (all required):
  1. Confirmed-correct-dismissal (false-positive) rate ≤ **50%** over the most recent full cycle. Rationale: at launch thresholds are deliberately conservative; a flag stream where more than half of flags are noise trains reflexive dismissal (the harmful incentive Stage 04 names) and must be re-tuned *before* operators see it as non-shadow.
  2. Every later-discovered unflagged error during the shadow period has been replay-analysed (§5) and dispositioned: threshold/formula adjusted, or accepted with a recorded reason.
  3. Operator exit decision recorded: the shadow-flag flip is a config change → domain-1 audit event carries the decision note citing the metrics at exit.
- These governance values (3 cycles, 20 records, 50%) are launch values, adjustable through §4's own change flow — never silently.

## 3. Review cadence (DEC-10-09)

| Phase | Cadence |
|---|---|
| Shadow mode | Every payroll cycle (monthly): metrics computed, report committed |
| First 3 GA cycles | Every cycle |
| Steady state | Quarterly |
| Out-of-cycle mandatory review | Any confirmed false negative (a later-discovered entry error that reached a run unflagged) — reviewed within the cycle it is discovered, not deferred to the next scheduled review |

Each review produces the committed calibration report (Class B control, `standing-assurance-controls.md` §3): the three metrics, flag volume by layer/severity (context only — never a success metric), dismiss-without-review rate, threshold/detector versions in force, and any change decisions taken.

## 4. Threshold-change decision rules and audit flow

**When a change is considered** (decision rules — triggers, not automatisms; every change is an operator decision):

1. False-positive rate > 50% for a full cycle, attributable to a specific `input_code`/threshold row → targeted threshold raise (or ratio adjustment if Layer 2 is the source).
2. A false negative where replay (§5) shows a plausible threshold/ratio value would have flagged it without unacceptable false-positive cost on the same replay window → targeted tighten.
3. Workspace onboarding → seed workspace threshold rows (the monetary-class `5 × highest salary-definition monthly gross` rule recomputed and stored as a constant per design §2).
4. Salary-structure change in a workspace that invalidates the stored monetary ceiling → recompute and re-seed (same rule, new constant).

**Audit flow for every change** (mechanism fixed by design §2; restated as governance):

- New `anomaly_threshold` version row (never UPDATE-in-place); prior versions retained as calibration evidence.
- `created_by` = verified principal; the domain-1 audit event carries the reason (which decision rule fired, the metric evidence).
- Never LLM-generated or LLM-adjusted (D-04-01, binding).
- Effective from the next evaluation; no retroactive re-flagging of closed exception records (closed records are history; replay answers retrospective questions instead).

## 5. Detector-version replay discipline (DEC-10-10)

- **Version bump rule**: any formula/logic change bumps `detector_version` (design §4). Threshold row changes do **not** bump the detector version (they are data, versioned in their own table).
- **Pre-deploy replay**: before a new detector version deploys, replay it over the trailing 6 periods (the design's window) of each active workspace's claimed inputs and diff the flag sets old-vs-new. The diff report (flags gained/lost, by employee/input_code) is committed as calibration evidence — a formula change whose effect on real data nobody looked at is not calibrated, it's guessed.
- **False-negative investigation**: replay the period's inputs under the detector/threshold versions **in force at the time** (pinned — this is what replayability is for, design §5) to answer "was this a detector miss or a threshold miss," then under current versions to answer "would we catch it now." Both answers go in the out-of-cycle review record.
- **Replay is read-only**: it creates no exception records; its output is the report artifact.

## 6. Gate mapping

CG-7 rows in the evidence register (§3, C7 table): shadow-exit decision record + first calibration report are the ET-5 artifacts; threshold-versioning and shadow-exclusion tests are the ET-1 floor; this document is the methodology those rows cite. SG-7's determinism gate is untouched by governance — no decision here may introduce an LLM into the detection path.
