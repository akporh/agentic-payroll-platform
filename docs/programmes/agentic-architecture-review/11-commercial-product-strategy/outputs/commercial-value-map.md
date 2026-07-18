# Stage 11 Output: Commercial Value Map (Q1)

Where each of the 15 approved capabilities' value actually lands, across three destinations:

- **INT** — Sandy's internal bureau efficiency (operator time, error avoidance, run reliability)
- **CLI** — bureau-client-visible service quality (what Sandy's payroll clients experience)
- **DIF** — future sellable differentiation (what could be led with commercially, against manual or less-instrumented competitors)

Grounded in Stage 04's outcome work (`outcome-prioritisation.md`, `measurement-framework.md`) and bounded by Stage 10's claimable-posture list (`10-evaluation-assurance/outputs/stage-11-handoff.md` §3). **Evidence discipline**: every value statement below is an operational-outcome inference from confirmed programme evidence or documented intent — *no capability has registered client-demand or willingness-to-pay evidence* (F-11-02, EG-004/EG-005). "DIF" therefore means "credibly claimable and measurable once built," never "demand-verified."

## 1. Value map

| Capability | Disposition | Value destination(s) | Commercial role | Grounding |
|---|---|---|---|---|
| C1 — Identity & Auth Foundation | pursue now (deterministic) | none directly; trust prerequisite for every CLI/DIF claim | **Enabling plumbing** — nothing is claimable (or launchable) without it; zero standalone sellable value | Stage 05: zero auth exists; blocks the majority of the portfolio |
| C2 — Event/Tool/Notification Foundation | pursue now (deterministic) | none directly; substrate for C6/C7/C11 surfacing + the exception workflow | **Enabling plumbing** — same as C1 | Stage 05 readiness matrix; F-04-01 |
| C3 — Operator Assistant (current-state) | after C1/C2 | INT (support/navigation questions ↓, B6-measured) | Enabling for operator efficiency; deliberately **not** the commercial lead (Principle 8; Stage 09: "platform with an assistant, not a chat product") | Measurement framework C3; B6 baseline |
| C4 — Historical Explanation | **blocked** (D-02-03) | **non-value row** — no claimable value until reproducibility gaps close | None until unblocked; must not appear in any commercial narrative (D-02-01–04 binding) | Stage 05: F-01-27/29/38 still open |
| C5 — Trace Explanation | conditionally ready (after C1/C2) | INT + CLI (faster, evidence-linked answers to "why was this employee paid X") | Supporting differentiator — feeds the "every AI statement evidence-linked" claim | Measurement framework C5; Stage 10 §3 claim 2 |
| C6 — Payroll Readiness Service | pursue now (deterministic) | INT (fewer failed run creations); CLI indirectly (reliability) | Internal value, real but **not differentiating** — must not be presented as an exhaustive pre-flight check (framework's harmful-incentive note) | Measurement framework C6; B4 baseline |
| C7 — Input Anomaly Detection | after exception workflow (D-04-01 hard gate) | CLI (input errors caught pre-run) + **DIF** ("calibrated against measured FP/FN rates, not vibes") | **Commercially load-bearing** — but value claims lag deploy by ≥ 3 payroll cycles + ≥ 20 terminal records (shadow exit, DEC-10-08); month-one C7 value claims are wrong by construction | Stage 10 handoff §2.1; calibration-governance §2 |
| C8 — Reconciliation Investigation | **blocked** (D-02-02 + D-02-03) | **non-value row** | None until both preconditions close; its *remediations* (scoping fix) proceed as plumbing | Stage 05 readiness matrix |
| C9 — Trace Agent | **rejected** | **non-value row** | None — permanently; design-absence is itself register evidence (ET-2) | Stage 03 disposition, reconfirmed Stage 05 |
| C10 — Structured Confirmation Protocol | deferred (no consumer yet) | none directly; trust infrastructure | **Enabling plumbing** for the auditable-AI posture — it is what makes "AI proposes, human approves" mechanically true when write-capable capabilities arrive | Stage 04 prioritisation; Stage 08 design |
| C11 — Compliance Monitoring (narrowed) | conditionally ready (with C12) | **DIF** (time-to-detection of statutory changes) + CLI (compliance confidence) | **Commercially load-bearing** — but the claim is only as strong as the Tier-1 allowlist and cadence (source policy §5: "do not market beyond the policy's actual guarantee"); success is precision, never detection volume (D-04-01 prohibition) | Stage 04 handoff (compliance-response speed as differentiator); compliance-monitoring-source-policy §5 |
| C12 — Statutory-Rule Change Management | pursue now (deterministic) | CLI (statutory changes applied correctly, recoverably) + **DIF** ("statutory changes apply only through recorded, re-authenticated human approval") | **Commercially load-bearing** — the strongest deterministic differentiator in the portfolio; also unlocks C11's entire value | Stage 10 §3 claim 3; Stage 04: fixes confirmed gap F-01-45/46 independent of AI |
| C13 — Onboarding Mapping Assistant | after C14 (binding) | INT (mapping time/errors ↓) + **DIF** (faster, evidence-backed client onboarding as a sales asset) | **Commercially load-bearing** — but improvement claims are permanently anchorless unless B1/B2 baselines are captured on a real onboarding *before* it ships (unrecoverable window, Stage 10 handoff §2.2) | Stage 04 handoff; B1–B3 baselines |
| C14 — Deterministic Import Validation & Dry-Run | pursue now (deterministic) | CLI (onboarding confidence: dry-run evidence, parallel-run agreement) + INT | **Commercially load-bearing** — the dry-run mechanism is valuable and claimable before any AI mapping exists; prohibition: dry-run-pass ≠ client-validated accuracy, never collapse the two | Stage 04 prioritisation (C14 "valuable even before any AI assistant"); measurement framework C13/C14 |
| C15 — Email Notifications | **deferred** (after C2 proven in production) | **non-value row now**; later CLI reach (notifications beyond the app) | None until its sequencing condition is met — reconfirmed, not re-opened (§4 of Stage 09 handoff) | Stage 04 prioritisation |

## 2. Load-bearing vs enabling — the shape of the portfolio's commercial value

**Commercially load-bearing (what a future offer would actually lead with):**

1. **C12 + C11 — the compliance story**: recorded human-approved statutory change management plus monitored detection, measurable as time-to-detection/time-to-apply (B5). C12 alone already carries claimable value deterministically.
2. **C14 + C13 — the onboarding story**: dry-run-evidenced, faster client onboarding, measurable as B1/B2/B3. C14 alone already carries claimable value deterministically.
3. **C7 — the input-quality story**: calibrated anomaly detection with published FP/FN discipline; the platform's clearest "AI that earns trust" exhibit — on a structurally lagged timeline.
4. **The assurance posture itself** — the four Stage 10 §3 claims (continuously verified isolation; evidence-linked AI actions; human-approved statutory change; measured calibration) are a cross-capability differentiator: they are properties of the *platform*, not of any one capability, and they are exactly what a bureau's clients or an auditor can check.

**Enabling plumbing (indispensable, not sellable):** C1, C2, C10, the exception-resolution workflow, and the remediation set. C3, C5 and C6 sit between: genuine INT/CLI value, wrong as commercial leads.

**Structural observation (recorded as a conclusion, DEC-11-03):** every load-bearing AI differentiator sits behind unbuilt deterministic foundations, and the two deterministic load-bearing capabilities (C12, C14) are buildable sooner and carry claimable value on their own. The commercial value sequence therefore *matches* the technical readiness sequence (Stage 04's signal: C1 → C2 → C6/C12/C14 → gated AI capabilities) — there is no tension between "build what's ready" and "build what's valuable," which is itself a useful strategic fact for Stage 12/13.

## 3. What this map must not be read as

- Not a demand assessment: no row has client-demand evidence (F-11-02); B-series baselines give *measurability*, not *market proof*.
- Not a roadmap: ordering lives in `sequencing-economics.md` as constraints; Stage 13 sequences.
- Not a re-opened portfolio: dispositions are D-03-01-fixed; the non-value rows stay non-value until their own conditions change.
