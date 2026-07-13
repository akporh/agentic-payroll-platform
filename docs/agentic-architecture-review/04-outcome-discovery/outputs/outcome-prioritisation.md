# Stage 04 Output: Outcome Prioritisation

Classifies every outcome identified in `product-opportunity-map.md` and `outcome-capability-matrix.md` as: **pursue now** / **pursue after platform prerequisite** / **defer** / **reject** / **research further**. This is a prioritisation lens, not a roadmap — Stage 13 owns roadmap approval.

Assessed against: user value, payroll-risk reduction, compliance value, frequency of the problem, measurable operational impact, platform readiness, implementation complexity, learning value, commercial differentiation.

## Existing-capability outcomes

| Outcome (capability) | Classification | Rationale |
|---|---|---|
| C3 — current-state operator assistance | **Pursue after platform prerequisite** | High user value, low payroll-risk (read-only), but depends on C1 (auth) and C2 (PII-sanitizing tool layer) landing first — not yet buildable |
| C5 — trace explanation | **Pursue after platform prerequisite** | High user value, evidence-linked by design; depends only on the null-trace refusal spec (Stage 08) — low complexity once specified |
| C6 — payroll readiness service | **Pursue now** (as deterministic engineering, not agent work) | High frequency (every run), low complexity (already computed by existing service), no AI risk — this is close to a pure engineering/UX task |
| C7 — input anomaly detection | **Research further** | Value is plausible but the calibration question (what counts as anomalous) is unresolved and materially affects both value and harmful-incentive risk (false positive fatigue) — needs product/statistical input before committing engineering time |
| C11 — compliance monitoring (narrowed) | **Pursue after platform prerequisite** | High compliance value, but has no functioning outcome until C12 exists — sequencing dependency, not a reason to defer C11's own design work |
| C12 — statutory-rule change management | **Pursue now** | Purely deterministic, addresses a confirmed current gap (F-01-45/46) independent of any AI capability, unlocks C11 |
| C13 — onboarding mapping assistant | **Pursue after platform prerequisite** | Clear, well-bounded value; blocked on C14 existing as its hard safety gate |
| C14 — deterministic import validation & dry-run | **Pursue now** | Deterministic, unlocks C13, and the dry-run mechanism itself is valuable even before any AI mapping assistant exists |
| C4 — historical payroll explanation | **Defer** | Genuinely valuable but explicitly blocked (D-02-03) — do not commit engineering time until Stage 05 confirms the reproducibility gaps have closed |
| C8 — reconciliation investigation | **Defer** | Same reasoning as C4 — blocked on two independent preconditions (D-02-02, D-02-03) |
| C9 — trace agent | **Reject** | Already rejected in Stage 03 for duplicating C5/existing UI with no distinct outcome |
| C1 — auth foundation | **Pursue now** | Blocks everything else; highest sequencing priority in the entire portfolio |
| C2 — event/tool/notification foundation | **Pursue now** | Blocks C3, C6's notification surfacing, C7's exception-queue delivery |
| C10 — confirmation protocol | **Defer** | No active consumer yet (every write-capable capability is blocked or restricted) — design it when C8/C11-with-writes actually need it, not speculatively now |
| C15 — email notifications | **Defer** | Explicitly sequenced after C2 is proven in production, per the source document's own logic, unchanged by this review |

## Newly identified outcome opportunities

| Outcome | Classification | Rationale |
|---|---|---|
| Exception resolution workflow (area 8) | **Pursue now** | This is arguably the single highest-leverage gap in the entire map — C6 and C7 both produce flagged items with no defined resolution path today; fixing this multiplies the value of capabilities already being pursued |
| Two-entry-point structural-configuration duplication (area 2) | **Research further** | Real risk (Stage 01 F-01-05) but this stage cannot determine whether operators actually experience this as friction in practice — needs a small operator-facing investigation, not a large engineering commitment yet |
| `shift_type` NULL-handling divergence (area 4) | **Pursue now** (as a small deterministic fix) | Low complexity, removes a genuine correctness-adjacent inconsistency (Stage 01 F-01-16); does not require this review's further involvement — a normal bug-fix sprint item |
| Recurring-error root-cause reporting | **Defer** | Depends on the audit-coverage fix (F-01-40) as a hard prerequisite — pursuing this before that fix would mean building reporting on an incomplete data foundation |
| Payroll deadline-risk visibility | **Research further** | Plausible value, but no current evidence of how bureaus currently track deadlines or where the risk actually manifests — needs direct product research before scoping |
| Control-completion evidence | **Defer** | Same audit-coverage dependency as recurring-error reporting |
| Client profitability/operational-cost insight | **Defer** | Commercially interesting but squarely Stage 11's remit to assess against business strategy, not a Stage 04 evidence-driven prioritisation call |
| Support-response drafting | **Research further** | Plausible extension of C3, but no evidence yet of support-response volume/pattern to justify prioritizing over the exception-resolution-workflow gap |
| Configuration-drift detection | **Defer** | Related to the area-2 duplication risk; pursue only after that's researched further |
| Unresolved-input visibility | **Pursue after platform prerequisite** | Meaningfully overlaps with the exception-resolution-workflow outcome — should be designed together, not as a separate initiative, once C2 (notification foundation) lands |
| Pre-approval assurance packs | **Research further** | Plausible commercial/compliance value (a bundled evidence package before sign-off) but no current evidence of demand or format — needs product research |

## Summary sequencing signal (not a roadmap)

The evidence points toward one clear near-term sequence, independent of any single capability's individual merit: **C1 → C2 → (C6, C12, C14 in parallel, all deterministic) → exception-resolution-workflow design → C3/C5/C13/C11 (AI capabilities, each individually gated on its own prerequisite) → C4/C8 only once Stage 05 closes their blockers.** This is offered as a prioritisation signal for Stage 11/13 to weigh, not a committed plan.
