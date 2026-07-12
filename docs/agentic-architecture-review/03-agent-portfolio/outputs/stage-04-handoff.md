# Stage 03 → Stage 04 Handoff (Outcome Discovery)

Stage 03 did not perform outcome discovery in full — these are newly-noticed opportunities and open framing questions to expand, not resolved conclusions.

## New outcome opportunities noticed during portfolio review

1. **Input anomaly detection (C7)** — needs a calibration/threshold policy (what counts as "anomalous" vs. previous-period quantities). This is a product decision requiring data (how much variance is normal across the client base) that this stage cannot supply from code/migration evidence alone. Frame as an outcome: reduction in payroll-input errors reaching a run, measured against today's baseline (caught only if a human happens to notice).

2. **Exception queue resolution workflow (C7's output surface)** — flagging an anomaly is only half the outcome; what happens next (dismiss, correct, escalate) needs a defined workflow. Currently unspecified in the source document and not designed by this stage.

3. **Compliance detection → application handoff (C11 → C12)** — these are separate capabilities with separate owners, but the operator-facing outcome ("a statutory change gets applied correctly and on time") spans both. Consider framing this as one end-to-end outcome metric even though it's built as two capabilities.

4. **Onboarding Mapping Assistant (C13) measurable outcome** — reduction in manual column-mapping time/errors vs. today's `NativeUploadFlow` baseline (Stage 01 F-01-13). Worth quantifying the current baseline before building C13, to have a real "before" number.

5. **Operator Assistant (C3) adoption/deflection metric** — reduction in support/navigation questions reaching a human, plus a refusal-rate metric for out-of-scope (historical) questions — the latter matters because a *high* refusal rate on legitimately current-state questions would indicate the tool set is incomplete, not that the boundary is working.

## Capabilities with defined measurable outcomes already (see `outputs/agent-capability-matrix.md` for each)

C3, C5, C6, C7, C11, C13, C14 each have a proposed measurable-outcome statement in the capability matrix — Stage 04 should treat these as starting hypotheses to validate/refine, not settled targets.

## What Stage 04 should NOT re-derive

The capability portfolio itself (`outputs/agent-capability-matrix.md`) and its dispositions — Stage 04's job is outcome framing for the *retained* capabilities, not re-deciding what's in the portfolio.
