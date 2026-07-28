# Stage 08 Output: Anomaly Detection Design (C7)

Answers Stage 08 Q7, resolving DQ-001 (concrete statistics, thresholds, minimum history window) **within** D-04-01's approved layered shape (`04-outcome-discovery/outputs/anomaly-detection-outcome-policy.md`): absolute thresholds at launch → period-on-period variance gated on a history window → peer-pattern deferred. The layering itself is not re-opened. Detection is fully deterministic; the LLM narrates only, optionally (T6/SG-7). C7 is hard-gated on the exception-resolution workflow existing (D-04-01 binding condition — substrate: `event-audit-foundation-design.md` §6).

## 1. Detection target and boundary

Detects on `payroll_input.quantity` per (employee, `input_code`) at input submission and at pre-run check, over unclaimed inputs for the upcoming period. **Boundary decision (Stage 04's flagged question)**: *missing/zero-when-expected* is assigned to **C6** (readiness), not C7 — it is an absence check over enrollment/expectation state, exactly C6's existing shape (missing timesheets), and folding it into C7 would give C7 two unrelated detection geometries. C7 v1 detects magnitude anomalies on *present* values only. Unit-confusion detection stays out of scope for v1 (per Stage 04 — needs semantic input typing that doesn't exist).

## 2. Layer 1 — absolute thresholds (launch layer)

- **Config table `anomaly_threshold`** (versioned, auditable — D-04-01): `threshold_id` UUID PK · `workspace_id` UUID NULL (NULL = platform default; workspace row overrides) · `input_code` VARCHAR(50) · `max_value` NUMERIC NULL · `min_value` NUMERIC NULL · `version` INT · `is_active` BOOL · `created_by` (verified principal) · `created_at`. Changes are domain-1 audit events (new row per change, prior versions retained — threshold history is calibration evidence). Resolution: workspace row for the input_code, else platform default, always the highest active version — and the flag records *which* threshold row/version fired.
- **Launch defaults** (platform rows, tuned per workspace during calibration): overtime-hours-class codes `max_value = 100` per period; day-count-class codes `max_value = 31`; monetary-amount-class codes `max_value = 5 × the workspace's highest salary-definition monthly gross` (computed at threshold-seeding time, stored as a concrete number, not a live formula — thresholds must be explainable constants per D-04-01). `min_value = 0` everywhere (negatives are already hard-rejected upstream, INP10).
- **Rule**: flag when `quantity > max_value` or `< min_value`. Severity `CRITICAL` when `quantity > 2 × max_value`, else `WARNING`.

## 3. Layer 2 — period-on-period variance (additive; activates per employee/input_code when history exists)

- **History basis**: the trailing series `h₁…hₙ` of the employee's *claimed* quantities for the same `input_code` from the most recent runs (claimed inputs only — unclaimed/abandoned rows are not history), summed per period, most-recent first, up to **n = 6** periods.
- **Minimum history window (DQ-001 parameter): 3 periods with a nonzero value for that (employee, input_code).** Below 3, only Layer 1 applies (a new employee has no baseline — D-04-01's own gating rationale). 3 is the smallest n where a median is meaningfully robust to one outlier period; waiting for 6 would leave most employees ungated for half a year.
- **Statistic (DQ-001)**: robust median-ratio test, not z-scores — with n ≤ 6 a standard deviation is dominated by single legitimate spikes, producing exactly the false-negative-after-one-odd-month failure z-scores are known for at tiny n. Let `m = median(h₁…hₙ)` (nonzero values only). Flag when:
  - `quantity ≥ R_high × m` with **R_high = 3.0** (`WARNING`), escalating to `CRITICAL` at `≥ 10 × m` (the order-of-magnitude typo class), or
  - `quantity ≤ R_low × m` with **R_low = 1/3** (`WARNING` only — under-entry is real but less damaging than over-entry, and zero/absent is C6's).
- **Worked example (Stage 04's canonical case)**: history 40, 42, 44 OT hours → `m = 42`; entry `400` → ratio 9.5 → `WARNING` at 3×, and `400 > 100` fires Layer 1 too → flag surfaces once (§4 dedup) at the max severity, evidence shows both bases: "400 entered; employee's 3-period median is 42 (9.5×); absolute ceiling 100."
- Layer 2 is **additive** — it never suppresses a Layer 1 flag (D-04-01: variance "never replaces the hard limits").

## 4. Flag lifecycle (into the exception workflow — nowhere else)

- One evaluation pass per input submission event (`PAYROLL_INPUT_SUBMITTED`, consumed by the C2 worker) and one sweep at pre-run readiness check (C6's trigger point, same detector code).
- A firing creates **one `exception_record`** (`source = C7_ANOMALY`) per (employee, input_code, period) — subsequent firings for the same tuple update nothing (the existing open record's evidence stands; a *changed* value after correction re-evaluates on the next submission event: if it still flags, a new record only if the prior one is terminal). `evidence_jsonb` carries: entered value, threshold row/version fired, history series, median, ratio, layer(s), detector version.
- **Detector versioning**: `detector_version` stamped on every flag; formula changes bump it (calibration governance — D-04-01).
- **Shadow mode**: a boolean platform config; when on, records are created with `severity = INFO` and a `shadow: true` marker — visible in the queue for calibration measurement but excluded from operator-facing counts. Launch runs shadow-first per D-04-01.

## 5. Calibration governance (D-04-01's three metrics — wired, not aspirational)

All three derive from `exception_record` fields, no extra instrumentation:

| Metric | Derivation |
|---|---|
| Confirmed-error capture | records with `resolution_code = CONFIRMED_ERROR_CORRECTED` / all C7 records |
| Confirmed-correct dismissal (false-positive rate) | `resolution_code = CONFIRMED_CORRECT_DISMISSED` / all C7 records |
| Later-discovered unflagged errors (false negatives) | retroactive: an entry error found via reconciliation/complaint is checked against the flag history for that (employee, input_code, period) — queryable because every evaluation stores its detector/threshold version even when it does **not** flag? No — storing every non-flag is disproportionate; instead the detector is **replayable**: given the period's inputs and the versioned thresholds, the evaluation is pure and reproducible, so "would this have flagged under version X" is answerable after the fact. Replayability, not exhaustive logging, is the mechanism |

Threshold/version changes are domain-1 audited (§2), satisfying "versioned and auditable threshold changes."

## 6. Optional narration layer

Off by default. When enabled: the LLM receives the already-created exception record's evidence (values, ratios — as strings) and writes `recommended_action` prose only. No tools in the narration session (`tool-contracts.md` §1 — C7's registry is empty); the detector's output is immutable input to it (T6: cannot flag or unflag). Ships only with SG-7's injection test set if enabled.

## 7. Requirements satisfaction and verification

| Requirement | Satisfied by | Verification |
|---|---|---|
| D-04-01 layered shape preserved | §2/§3 additive layers; peer-pattern absent | Design review; no peer-comparison code path exists |
| DQ-001 concrete parameters | R_high 3.0 / CRITICAL 10× / R_low ⅓ / n≤6 / min-window 3 / launch ceilings §2 | Worked-example fixture tests (400-vs-42 case et al.) pinning each formula — the Sprint 15 "derivation formula worked-example gate" applied to C7 |
| Deterministic detector (T6/SG-7) | §3 pure function, replayable | Same-input-same-output property test |
| Exception-workflow gate (D-04-01) | §4 — flags exist only as exception records | C7 launch checklist: exception workflow live first (CG/SG sequencing) |
| Shadow mode + calibration metrics | §4/§5 | Metric queries return values on fixture data |
| No LLM in detection | §6 isolation | Registry test: C7 detection path imports no LLM client |

DQ-001 is resolved by this design; final production values remain tunable through the versioned threshold table (product calibration per D-04-01), but launch numbers are now named.
