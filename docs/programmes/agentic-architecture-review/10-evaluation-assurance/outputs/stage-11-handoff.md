# Stage 10 → Stage 11 Handoff (Commercial & Product Strategy)

Assurance cost and dependency implications for commercial sequencing. Stage 10 designed *how* launch gates are evidenced and kept true (`launch-gate-evidence-register.md` and companions); this handoff extracts what that framework costs, what it sequences, and what it makes sellable. Nothing here re-opens a gate or a design.

## 1. Assurance costs that belong in sequencing decisions

| Cost item | Shape | When it lands |
|---|---|---|
| **Frontend test harness** (F-10-01) | One-off setup (Vitest + RTL + CI job) with the first frontend-touching build item (C1), then cheap per-behaviour tests. The alternative is recurring: ~18 of Stage 09's 25 behaviours fall to scripted-manual per release. Setup cost is small; *not* building it converts a fixed cost into a permanent per-release tax and leaves behaviour 21 (the standing `grade_code` rule) unprotected indefinitely | C1 |
| **LLM eval infrastructure** (corpus format, runner, report convention) | One-off with the first LLM capability (C3); each later capability adds corpus content only. API spend at corpus scale is trivial; the real cost is corpus authorship (bounded: 70-case launch floor per capability) | C3 |
| **Scheduled-job CI seam** (F-10-02) | Trivial one-off (workflow triggers) with the first Class B control | First eval or sweep landing |
| **Standing cadence** (operator time) | Steady state ≈ one monthly + one quarterly scripted session (`standing-assurance-controls.md` §6) — deliberately capped; any proposal that grows this needs to displace something | From C2/C3 onward |
| **Baseline captures** (`evidence-chain-and-baselines.md` Part B) | Near-zero for B3/B5 retrospectives (computable now from git/engagement records); B6 is a 4-week tally; B1/B2 require a **real onboarding** — see §2 | Before each capability's launch |

## 2. Hard sequencing facts assurance adds

1. **C7's GA lags its deploy by ≥ 3 payroll cycles** (shadow-mode minimum, `calibration-governance.md` §2). A commercial timeline that shows C7 value in month one is wrong by construction — plan shadow entry ≥ one quarter before claimed GA.
2. **B1/B2 baselines need a real client onboarding under the current flow** — they cannot be synthesized. If the next onboarding happens *after* C13 ships, the baseline is unrecoverable and C13's improvement claims are permanently anchorless (measurement framework, binding). Sequencing implication: schedule the next onboarding's observation protocol *before* C13's build, or accept C13 launches without a defensible before/after story.
3. **B6 (support-question tally) needs a 4-week pre-C3 window** — cheap but calendar-bound; start it when C3 enters a sprint plan, not when it ships.
4. **Register sequencing preconditions are load-bearing**: C7-after-C2 (exception workflow), C13-after-C14, C11-with-C12 — the evidence register enforces these as row-closure preconditions (§5); Stage 11's sequencing must not assume they are soft.
5. **DQ-006/DQ-007 are pre-build human gates** (CG-11/CG-12 rows) — the register cannot close those capabilities' rows without the recorded decisions; put them on the critical path early, since both may need professional (legal/tax) input with lead time.
6. **DEC-08-09's data-contract change** (statutory UNIQUE widening) goes through `/arch-council` at Phase 3 — already a visibility item; budget the review.

## 3. What the assurance posture makes commercially claimable (input, not copy)

Grounded claims Stage 11 may build offers on — each is backed by a named standing artifact, which is exactly what makes them credible to a bureau's clients or an auditor:

- "Tenant isolation is continuously verified" (route-table-generated tests, SS-1 — not a point-in-time pentest claim)
- "Every AI action is logged, attributed, and evidence-linked" (SC-3 + chain-completeness sweeps)
- "Statutory changes apply only through recorded, re-authenticated human approval" (CG-12/SG-12 evidence set)
- "Anomaly detection is calibrated against measured false-positive/negative rates, not vibes" (calibration reports)

Boundaries that must **not** be overclaimed (residual-risk register): tamper-evidence is in-DB, not cryptographic/external (RR-1/RR-3); pre-2026-epoch audit identity is unverified (RR-4); retention basis pending DQ-008 (RR-5). Marketing copy that implies "tamper-proof" or "cryptographically signed" would outrun the accepted posture.

## 4. Items remaining with Stage 11

- **DQ-005** (CORRECTION run-type UI exposure): Stage 09's recommendation stands (contextual "Create correction run" CTA with/after C12, no generic dropdown — `09-human-experience/outputs/stage-11-handoff.md` §1); Stage 10 adds only that if/when adopted, its behaviours join the UX plan as a Phase 3 addendum (per Stage 09's carried context). Joint disposition remains yours.
- **Browser-e2e automation** for the two scripted-manual behaviours (7's two-tab race, 22's teardown sweep) — optional cost line; the safety halves are already automated (`ux-verification-plan.md` §3).
- **Multi-tenant commercialisation check**: if Stage 11 proposes SaaS multi-tenancy, RR-1's trigger (c) fires — the audit-tamper reaffirmation does not carry over and must return as a human decision (`residual-risk-register.md` §3).
