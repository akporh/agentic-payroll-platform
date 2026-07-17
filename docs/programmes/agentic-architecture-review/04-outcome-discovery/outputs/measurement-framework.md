# Stage 04 Output: Measurement Framework

Defines success, safety, and harmful-incentive metrics per capability/outcome, per `CONTEXT.md` questions 6–7. Where no baseline currently exists, this is stated explicitly rather than a number invented.

## Principle: what this framework must not do

Per `CONTEXT.md`'s explicit constraint, chat/agent usage volume is never itself a success metric — a high chat-message count could equally mean the assistant is valuable or that the product is confusing enough to require constant hand-holding. Every metric below is an *outcome* metric (reduced friction, reduced risk, faster resolution), never a *usage* metric standing alone.

## Per-capability metrics

### C3 — Operator Assistant, Current-State Mode
- **Success**: reduction in support/navigation questions reaching a human; correct-answer rate on a labelled current-state Q&A test set
- **Safety**: refusal rate on historical/out-of-scope questions (should be ~100% for genuinely historical questions, not partial); zero instances of a fact not sourced from a tool call
- **Harmful incentive to avoid**: do not measure "messages per operator" or "session length" as a success signal — both reward unnecessary chat usage, which `CONTEXT.md` explicitly warns against

### C4 — Historical Payroll Explanation (blocked)
- **Success**: (deferred) historical-accuracy rate against known-good reconstructed cases, once unblocked
- **Safety**: zero instances of an explanation affected by an unresolved reproducibility gap (F-01-27/29/38) reaching an operator without a caveat
- **Harmful incentive to avoid**: shipping before Stage 05 confirms closure, under pressure to "finish the Track W story" — this is exactly the false-confidence risk named in `product-opportunity-map.md` area 9's analogue

### C5 — Trace Explanation
- **Success**: reduction in time-to-answer for "why was this employee paid X" questions
- **Safety**: zero instances of a number in the explanation not present in `component_trace_jsonb`; explicit refusal rate for null-trace cases (once specified, Stage 08)
- **Harmful incentive to avoid**: none identified — this capability is tightly bounded by design

### C6 — Payroll Readiness Service
- **Success**: reduction in run-creation failures/retries attributable to the three named conditions; reduction in time-to-detection vs. today's "found at run creation" baseline (currently unquantified — no baseline exists)
- **Safety**: N/A — no LLM in the critical path
- **Harmful incentive to avoid**: presenting the readiness panel as an exhaustive pre-flight check when it only covers 3 conditions — must not imply broader completeness than it has

### C7 — Input Anomaly Detection
- **Calibration approach approved 2026-07-13 (D-04-01)**: layered combination — absolute thresholds at launch, period-on-period variance as an additive second layer (gated on a minimum history window), peer-pattern comparison deferred. LLM restricted to optional narration only.
- **Success**: confirmed-error capture rate, confirmed-correct-dismissal rate, and later-discovered-unflagged-error rate — the three governance metrics named in D-04-01, tracked from shadow-mode rollout onward, not just at general availability; anomalies caught pre-run vs. today's baseline (caught only if a human notices, unquantified)
- **Safety**: if an LLM narration layer is added, a separate hallucination check on the narration text (the underlying flagged values must remain deterministic); threshold changes must be versioned and auditable per D-04-01
- **Harmful incentive to avoid**: false-positive fatigue leading operators to reflexively dismiss flags without checking — track dismiss-without-review rate as an early-warning signal, not just flag volume

### C8 — Reconciliation Investigation (blocked)
- **Success**: (deferred) causal-accuracy rate against known MISMATCH test cases, once unblocked
- **Safety**: same as C4 — zero instances affected by unresolved reproducibility/scoping gaps
- **Harmful incentive to avoid**: same as C4 — pressure to ship before both D-02-02 and D-02-03 preconditions close

### C11 — Compliance Monitoring (narrowed) → C12 — Statutory-Rule Change Management
- **Success**: time-to-detection and time-to-apply for a real statutory change, vs. today's manual-notice-then-migration baseline (baseline is qualitatively known — "next deployment cycle" — but not quantified in days; worth measuring the current baseline before C11/C12 ship, to have a real comparison)
- **Safety**: zero instances of a change applied without human approval (C12's hard invariant); citation/provenance completeness rate for every C11-drafted proposal (every claim must trace to a specific external source)
- **Harmful incentive to avoid**: measuring "number of changes detected" as success — this rewards over-flagging low-confidence, non-authoritative "changes" rather than accurate ones; measure precision (confirmed real changes / total flagged), not raw volume

### C13 — Onboarding Mapping Assistant → C14 — Deterministic Import Validation & Dry-Run
- **Success**: reduction in manual column-mapping time/errors vs. `NativeUploadFlow` baseline (currently unquantified — see `onboarding-outcome-baseline.md`); time-to-go-live for new clients; parallel-run agreement rate (currently unquantifiable — no baseline)
- **Safety**: zero bad-mapping commits reaching production payroll data (i.e., C14's dry-run gate must have a 100% catch rate for the specific error classes it's designed to catch — this needs Stage 08 to define what "dry-run" mechanically covers before this metric is even meaningful)
- **Harmful incentive to avoid**: treating a passing dry-run as equivalent to client-validated accuracy — track these as two distinct metrics, never collapse them into one "onboarding confidence" number

## Cross-cutting metrics (apply to the whole portfolio)

| Metric | Purpose |
|---|---|
| Rate of AI-generated statements with a linked evidence source | Operationalizes Principle 4 across every retained AI capability, not just the one currently measured per-capability |
| Rate of capabilities reclassified from "agent" to "deterministic" during design review (Stage 03's own pattern) | A meta-metric: if future capability proposals keep needing this correction, it signals the underlying design discipline (Principle 9) isn't being applied at proposal time |
| Exception-resolution time-to-close (once the exception-resolution-workflow outcome is built) | Cross-cuts C6, C7, and (later) C8 — the single most leverage-multiplying metric in this framework, since it measures whether flagging anything actually leads to it being fixed |

## Baseline-data gaps (explicit, not inferred)

The following metrics cannot be computed today because no baseline currently exists in the repository or product:
- Time-to-detection for readiness issues under today's manual process (C6)
- Manual column-mapping time/error rate under `NativeUploadFlow` (C13)
- Parallel-run agreement rate for any past onboarding (C13/C14)
- Time-to-apply for a historical statutory-rule change (C11/C12)
- Support/navigation question volume reaching a human today (C3)

Each of these should be measured *before* the corresponding capability ships, not only after — otherwise "improvement" claims have no anchor. This is flagged as a data-collection prerequisite, not resolved by this stage.
