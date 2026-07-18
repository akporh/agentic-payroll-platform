# Stage 10: Evaluation & Assurance — Decisions

Stage-local log. Master log for human decisions: `_core/HUMAN-DECISIONS.md`.

## Gate

- **Stage opened**: 2026-07-17 (context-ready on Stage 09's closure, D-003 automatic progression)
- **Stage closed**: 2026-07-18 (critic PASS, zero required corrections — D-003 automatic closure)

## Human decisions made this stage

**None.** No blocking human decision surfaced. The one place `CONTEXT.md` allowed a genuine risk-acceptance choice to surface (the DEC-07-04 review, Q8) resolved as a reaffirmation on unchanged facts (DEC-10-16 below) — explicitly bounded so that the one scenario that *would* make it a human decision (multi-tenant commercialisation) re-opens it (RR-1 trigger (c), `outputs/residual-risk-register.md` §3).

## Executor design conclusions (DEC-10-01 – DEC-10-16)

Recorded per the extended-field pattern: design conclusions within inherited binding decisions, not product/risk choices. Each names its output location; none weakens a gate, metric definition, or prior decision.

| ID | Conclusion | Where |
|---|---|---|
| DEC-10-01 | Six-type evidence taxonomy (ET-1 committed test … ET-6 measured baseline); committed-test is the default form, lower forms need a stated reason | `launch-gate-evidence-register.md` §1 |
| DEC-10-02 | Register "done" rule (build item complete only when its register rows point at merged, green artifacts, updated in the same commit) + ratchet rule (tighten freely; weakening = recorded human decision) | `launch-gate-evidence-register.md` §5 |
| DEC-10-03 | Eval scope = behavioural residue only; deterministic (ET-1) floor is never substituted by an eval, and vice versa | `llm-evaluation-framework.md` §1 |
| DEC-10-04 | Corpus launch floors: ≥30 functional / ≥20 refusal (C3: ≥10 historical) / ≥20 adversarial per capability; floors rise freely, never fall | `llm-evaluation-framework.md` §2.2 |
| DEC-10-05 | Grading hierarchy: programmatic assertions first; rubric'd LLM-judge only for phrasing judgments with 10% human spot-check; safety-critical cases run 3×, worst result counts | `llm-evaluation-framework.md` §3.2 |
| DEC-10-06 | Pass-bar evolution rule: tightening free; loosening or reclassifying a safety criterion = recorded human decision | `llm-evaluation-framework.md` §4 |
| DEC-10-07 | Four-class standing-control model (A permanent CI gate / B triggered-scheduled / C periodic scripted review / D event-triggered inspection); Class A default | `standing-assurance-controls.md` §1 |
| DEC-10-08 | Shadow-mode minimum: 3 full payroll cycles AND ≥20 terminal C7 records; exit requires FP rate ≤50% last cycle + all false negatives replay-dispositioned + recorded operator exit decision | `calibration-governance.md` §2 |
| DEC-10-09 | Calibration review cadence: per-cycle (shadow + first 3 GA cycles), quarterly steady-state, mandatory out-of-cycle on any confirmed false negative | `calibration-governance.md` §3 |
| DEC-10-10 | Detector replay discipline: pre-deploy replay diff over trailing 6 periods committed as evidence; false-negative investigations replay at pinned then-current versions; replay is read-only | `calibration-governance.md` §5 |
| DEC-10-11 | Frontend component-test harness is an assurance prerequisite, built with C1 (first frontend-touching item); retires the T4.5 park via behaviour 21; Vitest+RTL recommended as implementation specification | `ux-verification-plan.md` §1 |
| DEC-10-12 | Chain integrity enforced at two layers: per-mechanism fixture resolvability tests + a six-check zero-orphan sweep (per release + monthly); nonzero → exception record | `evidence-chain-and-baselines.md` A §2 |
| DEC-10-13 | Epoch discipline for assurance reporting: all queries partition on `platform_metadata.auth_cutover_epoch` from the single data source; pre-epoch rows never counted as verified-identity evidence; every report states the epoch | `evidence-chain-and-baselines.md` A §3 |
| DEC-10-14 | Baselines B1–B6 defined with manual observation protocols as the honest pre-C2 instrument; instrumented capture upgrades post-C2; B3/B5 retrospectives computable now | `evidence-chain-and-baselines.md` B §2 |
| DEC-10-15 | Residual-register semantics: RR rows only for residuals accepted by a recorded conclusion; pending risk choices remain queue pointers — never silently converted to residuals | `residual-risk-register.md` §1–2 |
| DEC-10-16 | DEC-07-04 reviewed and **reaffirmed** on unchanged facts (deployment shape, no new obligation, forward hooks preserved in Stage 08 designs, proportionality holds); bounded to the current deployment shape — multi-tenant commercialisation re-opens it as a human decision | `residual-risk-register.md` §3 |

## Next action

**None — stage closed 2026-07-18 on critic PASS.**
