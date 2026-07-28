# Stage 11 Output: Positioning & Claims Inputs (Q5)

What the trust/assurance posture supports leading with, and what it forbids. **Inputs for Stage 12's narrative synthesis — not marketing copy**, and no claim below may be used externally before the artifact backing it exists and is green.

## 1. The organizing frame (Principle 8, operationalised)

**"A payroll platform with an assistant" — never "a chat product."** Stage 02's Principle 8 (retained unchanged) and Stage 09's surface reality agree: chat is one capability's surface (C3); the differentiation is visible in the queue, approval, and evidence surfaces. Demo and narrative sequencing should therefore lead with the **exception queue, approval screens, and audit surfaces** — where "AI you can audit" is something a viewer can *see* — and treat the assistant as supporting cast.

## 2. Claimable properties (each backed by a named standing artifact)

From Stage 10 §3, restated with their commercial reading:

| Claim (grounded form) | Standing artifact | Commercial reading |
|---|---|---|
| "Tenant isolation is continuously verified" | Route-table-generated isolation tests (SS-1) — regenerated from the live route table every CI run | Stronger than a point-in-time pentest claim; credible to a client's auditor |
| "Every AI action is logged, attributed, and evidence-linked" | SC-3 tool-call audit standard + chain-completeness sweeps (zero-orphan checks) | The direct answer to the first objection any bureau client has about AI near payroll |
| "Statutory changes apply only through recorded, re-authenticated human approval" | CG-12/SG-12 evidence set (step-up linkage, atomic approval records) | The compliance-trust anchor; claimable deterministically once C12 ships |
| "Anomaly detection is calibrated against measured false-positive/negative rates" | Calibration reports per `calibration-governance.md` | The anti-"AI vibes" differentiator; claimable only post-shadow-exit (W1) |

Plus two **measured-baseline claims** that become available as B-series artifacts land:

- **Compliance-response speed**: time-to-detection / time-to-apply for statutory changes vs the manual baseline (B5 — retrospectively capturable now for NTA 2025). Stage 04 flagged this as a genuine bureau differentiator; the claim form is "measured at N days, from a published baseline of M," never an unanchored "fast."
- **Onboarding speed/confidence**: time-to-go-live (B3) and parallel-run agreement (B2) — same measured-claim form; unavailable if W2's window is missed.

## 3. Overclaim boundaries (each maps to an accepted residual or standing prohibition)

| Never claim | Why (source) |
|---|---|
| "Tamper-proof" / "cryptographically signed" / "immutable ledger" | Tamper-evidence is in-DB, not cryptographic or external (RR-1, RR-3); DEC-07-04 acceptance is bounded |
| Anything implying verified identity of pre-2026-epoch audit history | Pre-epoch identity is permanently unverified (RR-4); reports/surfaces label it |
| "Compliant retention" as a settled property | Retention basis pending professional confirmation (RR-5/DQ-008); "7-year floor" is a working posture, not a certified one |
| "You'll never miss a statutory change" in unbounded form | C11's guarantee is exactly as strong as the Tier-1 allowlist and cadence (source policy §5); the claim must carry that boundary |
| Any usage-volume success story (messages, sessions, engagement) | Measurement-framework prohibition — usage volume is never a success metric |
| "Dry-run passed = accurate payroll" | Dry-run-pass ≠ client-validated accuracy — two metrics, never collapsed |
| Detection-volume claims for C11 or C7 ("caught N changes/anomalies") | Precision, never volume, is the success metric (D-04-01); volume claims reward over-flagging |
| Any capability value ahead of its gate evidence (esp. C7 before shadow exit; C4/C8 at all) | Register "done = row green" rule; blocked capabilities have no claimable value |
| AI capabilities beyond the current-state boundary | D-02-03 binding; commercial narratives must not assume blocked capabilities unblock |

## 4. Positioning asymmetry worth naming for Stage 12

The overclaim table is not a marketing handicap — it is the position. Competitors (manual bureaus, or AI products without assurance discipline) can say "AI-powered" louder; none can say **"here is the standing test suite, the audit chain, and the calibration report — check them."** The platform's honest boundaries (in-DB tamper-evidence, bounded compliance-monitoring guarantee, measured-not-asserted improvement claims) read as credibility to exactly the audience a payroll bureau serves. Stage 12's narrative should treat the evidence artifacts themselves as the product's proof layer, and the *pace* of claims (post-gate, post-baseline) as a feature of the trust story, not a delay to apologise for.

## 5. Evidence constraint on all of the above

No claim in §2 has demand-side validation (F-11-02): "claimable" means *provable and credible*, not *proven to sell*. Before any external-facing use, the demand question (EG-005) is Michael's to answer from client conversations — this document only guarantees that what is said can be backed.
