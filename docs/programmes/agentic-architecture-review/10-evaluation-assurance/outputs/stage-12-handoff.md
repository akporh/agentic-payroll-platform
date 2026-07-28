# Stage 10 → Stage 12 Handoff (Target Direction)

Assurance-posture summary as a target-direction input: what the evaluated platform *is*, assurance-wise, and the constraints any target direction inherits.

## 1. The assurance posture in one paragraph

The platform's safety story is **determinism-first**: nearly every guarantee that matters (tenant isolation, no hallucinated numbers, no unconfirmed mutations, attributable approvals, deterministic anomaly detection) is enforced in code and proven by committed tests generated from the system's own structure (route table, tool registry) — LLM evaluation covers only genuinely behavioural residue (refusal quality, injection *attempt* behaviour, narration honesty). Assurance runs on the repo's existing CI spine (fresh-DB pytest, pre-push gate) extended by one frontend harness, one eval runner, and a small scheduled-job seam; every standing control is scripted to fit a single-operator cadence (~one monthly + one quarterly session). Launch "done" is checkable, not asserted: one evidence register maps every CG/SG/SS gate and Stage 08 hook to a named artifact.

## 2. Structural properties for direction-setting

1. **The framework scales by pattern, not per-capability invention.** New capabilities inherit the machinery: a registry entry (auto-covered by uniformity/negative-path tests), a session-registry equality test, a corpus in the established format, register rows. The marginal assurance cost of capability N+1 is content, not infrastructure — relevant when Stage 12 weighs portfolio expansion.
2. **Generated-from-structure tests are the platform's antibody to its own recurring failure mode** (decorative scoping, five routes across two rounds — F-05-03/F-07-01). Any target direction that adds surface area (more routes, more tools) is automatically covered *only if* the generation points (route table, tool registry) remain the single choke points — an architectural property worth naming as a direction constraint.
3. **Calibration governance makes C7-class features slow-burn by design** (shadow ≥ 3 cycles, metric-gated exit). Direction options built on "fast AI wins" in the detection space conflict with the platform's own governance; direction options built on *trust* (auditable, calibrated, evidence-linked automation for bureaus) are what this posture is optimized for.
4. **The evidence register is a sellable artifact in itself** for a compliance-sensitive market: it is the difference between claiming controls and demonstrating them (Stage 11 handoff §3 lists the claimable set and the overclaim boundaries).

## 3. Constraints any target direction inherits (binding, with sources)

- **Measurement prohibitions** (Stage 04, binding): chat/usage volume never a success metric; dry-run-pass and client-validated accuracy never collapsed; C11 success is precision, never detection volume. Any Stage 12 KPI proposal is checked against these.
- **Gate ratchet**: gates and their evidence may tighten freely; weakening anything requires a recorded human decision (CG/SG registers; evidence register §5; eval bars §4).
- **Residual-risk boundaries** (`residual-risk-register.md`): in-DB tamper-evidence only (RR-1, reaffirmed for the *current* deployment shape — multi-tenant SaaS re-opens it as a human decision); no cryptographic approval signing (RR-3); pre-epoch identity permanently unverified (RR-4); retention basis pending DQ-008 (RR-5). Direction narratives must stay inside these.
- **Blocked/rejected capabilities stay blocked**: C4/C8 (D-02-03/D-02-02 preconditions), C9 rejected — the register defines no launch evidence for them by design; a direction that needs them first needs their preconditions closed.
- **Pending human decisions on the critical path**: DQ-006 (C11 source authority), DQ-007 (C12 segregation + MFA), DQ-008 (retention basis) — all pre-build gates surfacing at Stage 13.

## 4. Open items relevant to Stage 12

- Stage 11 receives the cost/sequencing detail (`stage-11-handoff.md`); Stage 12 should consume its §2 sequencing facts (C7 shadow lag; baseline-before-build windows) when framing the pace of any target narrative.
- F-10-01 (no frontend harness) and F-10-02 (no CI schedule seam) are the only infrastructure gaps Stage 10 confirmed — both small, both scheduled with named build items; neither constrains direction beyond timing.
