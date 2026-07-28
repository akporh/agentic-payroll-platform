# Stage 12 Output: Direction-Level Success Measures (Q5)

A deliberately small set of direction KPIs that tell the human reviewer whether the direction is *working* once builds land. K1–K5 are drawn from the Stage 04 measurement framework and the B1–B6 baseline set; K6 is drawn from the Stage 10 launch-gate evidence register and standing-controls artifacts (its row states its sources) — **selection and arrangement only; no new metric is invented here**. Every KPI honours the binding prohibitions; §3 restates them as hard guards.

## 1. The six direction KPIs

| # | KPI | What it tells the reviewer | Source metric(s) | Baseline / anchor | Measurable from |
|---|---|---|---|---|---|
| K1 | **Statutory-change response**: time-to-detection and time-to-apply for a real statutory change, vs the manual baseline | Whether the compliance story (Story 1) is real — the platform's strongest differentiator working | Measurement framework C11→C12; B5 | B5 retrospective (NTA 2025 publication → PAY-TAX-1 deploy) — capturable now (W5) | C12 live (apply half); C11 live (detection half) |
| K2 | **Onboarding confidence**: time-to-go-live (B3) and parallel-run agreement rate (B2), with mapping time/errors (B1) once C13 lands | Whether the onboarding story (Story 2) is real, and whether C13's AI actually improved on the deterministic flow | Measurement framework C13/C14; B1/B2/B3 | B3 retrospective capturable now; B1/B2 require the next real onboarding **before** C13 ships (W2, EG-004) | C14 launch onward; C13 comparison only if B1/B2 were captured |
| K3 | **Input-quality calibration**: confirmed-error capture rate, confirmed-correct-dismissal rate, later-discovered-unflagged-error rate | Whether C7 is a calibrated detector earning trust, or noise — the three D-04-01 governance metrics, plus dismiss-without-review as the fatigue early-warning | Measurement framework C7; `calibration-governance.md` | Shadow-mode data is its own baseline; tracked from shadow onward, reportable at exit | C7 shadow entry (values citable at shadow exit, W1) |
| K4 | **Exception resolution time-to-close**, and rate of exceptions closed without documented resolution (target: zero) | Whether flagging anything actually leads to it being fixed — the single most leverage-multiplying metric in the framework, cross-cutting C6/C7/(C8) | Measurement framework cross-cutting §; F-04-01 substrate | None exists (greenfield workflow) — first cycles establish it | Exception workflow live (with C2) |
| K5 | **Grounding integrity**: rate of AI-generated statements with a linked evidence source (target: 100%), zero unsourced numerics (C5 programmatic check), refusal correctness on out-of-boundary questions (C3) | Whether the "every AI action evidence-linked" posture holds in production, not just in eval | Measurement framework cross-cutting §; C3/C5 safety metrics; eval framework refusal classes | Eval corpora define the bar pre-launch | First LLM capability live (C3 or C5) |
| K6 | **Assurance-register greenness**: launch-gate register rows green for every live capability; standing controls (Classes A–D) executed on cadence within the capped sessions | Whether the platform's sellable proof layer is actually being maintained — the "demonstrate, don't claim" property as a number | Launch-gate evidence register ("done = row green"); `standing-assurance-controls.md` | Register exists now; greenness is checkable per row | C1 onward, cumulative |

## 2. How to read them as a *direction* signal

- K1/K2/K3 are the three sellable stories converted to numbers — if they move, the commercial thesis is working *as far as provability goes* (demand remains EG-005's separate question; no KPI here measures willingness-to-pay, and none should be read as market proof — F-11-02).
- K4/K5 are the trust mechanics — if K5 degrades, the AI boundary is leaking; if K4 degrades, flags are theatre (queue-empty without resolved-correctly is explicitly not success).
- K6 is the posture itself — a red register row under a live capability means the direction's core promise ("checkable, not asserted") is being broken, which outranks any feature progress.
- Direction review cadence: these six fit the existing quarterly scripted session (posture P-E) — no new standing obligation is created.

## 3. Prohibition guards (binding, restated as checks)

- **No usage-volume metric anywhere**: messages, sessions, engagement, session length never appear as success signals (Stage 04 principle; overclaim table).
- **No detection-volume metric**: C7/C11 success is precision and calibration quality, never "N anomalies/changes caught" (D-04-01).
- **Dry-run ≠ validated**: K2 keeps dry-run-pass and client-validated accuracy as separate series, never one "confidence" number.
- **No baseline, no improvement claim**: K1/K2 improvement language is unavailable where the corresponding B-series artifact was not captured in time (esp. B1/B2's unrecoverable window) — the KPI then reports absolute values only, labelled as anchorless.
- **Blocked capabilities have no KPI**: C4/C8/C9/C15 contribute no measure until their dispositions change; defining one would imply a launch path that does not exist (register rule).
