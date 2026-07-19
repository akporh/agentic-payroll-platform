# Decision Queue — Agentic Architecture Review Programme

This file tracks unresolved questions without turning every question into a human stop.

## Blocking human decisions

_None currently recorded._

## Non-blocking forwarded decisions

| ID | Question | Source stage | Target stage | Status |
|---|---|---|---|---|
| DQ-001 | Concrete C7 statistical formulas, numeric thresholds and minimum history window | 04 | 08 | **resolved 2026-07-17** — `08-technical-architecture/outputs/anomaly-detection-design.md` §§2–3 (DEC-08-12): median-ratio test, R_high 3.0 / CRITICAL 10×, R_low ⅓, min history 3 nonzero periods, window ≤ 6; launch absolute ceilings named |
| DQ-002 | Confirmation-protocol expiry, conflict, idempotency and run-state invalidation rules | 03 | 08 | **resolved 2026-07-17** — `08-technical-architecture/outputs/confirmation-protocol-design.md` §3 (DEC-08-08): 7-day TTL ceiling, one-live-proposal conflict rule, CAS idempotency, two-layer invalidation with mandatory execution-time re-check |
| DQ-003 | Deterministic onboarding dry-run mechanism | 03/04 | 08 | **resolved 2026-07-17** — `08-technical-architecture/outputs/dry-run-mechanism-design.md` §1 (DEC-08-11): real executor path (`run_sequential_payroll`), not a separate simulation |
| DQ-004 | What "safely separated from production state" means operationally for a dry run (does it create a `payroll_run` row?) — refines DQ-003; classified `implementation-specification` by the Stage 05 critic (F-05-09) | 05 | 08 | **resolved 2026-07-17** — same design §2: **no** `payroll_run` row (nor result/claiming/event writes); dedicated workspace-scoped `dry_run_execution` artifact with input-hash commit linkage |
| DQ-005 | Should `run_type = CORRECTION` remain API-only by design or be exposed in the UI — classified `non-blocking-forwarded-decision` by the Stage 05 critic (F-05-12) | 05 | 09/11 | **resolved 2026-07-18** — joint disposition complete: Stage 11 concurs with Stage 09's recommendation (DEC-11-02, `11-commercial-product-strategy/outputs/product-scope-boundaries.md` §1). Closed as an agreed **implementation-specification** bound to the C12 build: context-launched "Create correction run" CTA with/after C12, no generic dropdown exposure; API-only state persists deliberately until then |
| DQ-006 | Tier-1 authoritative-source allowlist for FIRS/PenCom regulatory monitoring — which sources are *legally sufficient* requires human + professional legal/tax sign-off (`06-compliance-controls/outputs/compliance-monitoring-source-policy.md` §4). Hard gate before C11 build authorisation | 06 | human reviewer (pre-C11 build) | **engagement APPROVED to initiate 2026-07-19 (DP-4 → HD-11)** — the bundled NG tax/legal advisory (with DQ-008) is authorised to start; **still forwarded**: DQ-006 itself concludes before any C11 sprint (Tranche 5) and remains the hard gate before C11 build authorisation. The advisory's conclusion is the adviser's + reviewer's, not the executor's |
| DQ-007 | Single-operator segregation-of-duties waiver for C12 statutory approvals + MFA hard-gate question (Stage 07 amendment) | 06 (amended 07) | human reviewer (pre-C12 build) | **RESOLVED 2026-07-19 (DP-1 → HD-8): A1 + B2.** Same operator may propose AND approve for v1 (A1 — waiver, with compensating controls in the C12 story); password re-auth required at approval; MFA deferred, NOT a v1 launch gate (B2 — password-only step-up floor, DEC-07-03), design stays MFA-compatible. **Recorded as A1 + B2 — not A2**, so C12 stays a single-operator workflow (no multi-operator prerequisite) |
| DQ-008 | Legal confirmation of audit/evidence retention period — source document asserts 7 years without cited basis; statutory minimum and any data-protection maximum need professional confirmation (`06-compliance-controls/outputs/agent-tool-audit-standard.md` §2). Gates retention-enforcing mechanisms only; "keep at least 7y" is the working floor meanwhile | 06 | human reviewer + professional advice | **engagement APPROVED to initiate 2026-07-19 (DP-4 → HD-11)** — same bundled NG tax/legal advisory as DQ-006; **still forwarded**: blocks retention-enforcement tooling only (O9); "keep at least 7y, no purge" remains the working floor until the adviser confirms the basis |

## Visibility items (not queued decisions)

- **DEC-07-04** — audit-tamper residual-risk acceptance (in-DB controls don't bind a DB superuser; external anchoring judged disproportionate) — flagged for review at Stage 10/13. Stage 10 review 2026-07-18: reaffirmed on unchanged facts (DEC-10-16), bounded to the current deployment shape. **Stage 13 touchpoint completed 2026-07-19: NOTED (accepted) by the human reviewer (DP-5 → HD-12)** for the current single-bureau managed-Postgres deployment; revisit only on an existing trigger (material deployment change, SaaS expansion, regulatory demand, suspected tampering — RR-1 trigger (c) armed for any SaaS move under DP-3/HD-10).
- **DEC-08-09** — Stage 08's C12 correction mechanics commit Phase 3 to proposing a **data-contract change**: `statutory_rule` UNIQUE widens from `(country_code, effective_from)` to `(country_code, effective_from, version)` (resolution stays total-ordered; the tie-break already exists in code, F-08-01). **Stage 13 touchpoint completed 2026-07-19: NOTED by the human reviewer (DP-6 → HD-13)** — handled via the normal arch-council + implementation governance when C12 is authorised; no implementation authorised now; rides the repo's standing `/arch-council` gate inside the C12 build (Tranche 2).

### Stage 13 decisions recorded (2026-07-19)

At the Stage 13 touchpoint the human reviewer (Michael Emedo) recorded seven of the nine pack items; two remain pending. Master entries: `_core/HUMAN-DECISIONS.md` HD-8…HD-16.

- **Recorded**: DP-1 → HD-8 (**A1 + B2**, not A2); DP-3 → HD-10 (single-bureau, SaaS-ready); DP-4 → HD-11 (advisory engagement approved to initiate); DP-5 → HD-12 (RR-1 noted/accepted); DP-6 → HD-13 (DEC-08-09 noted); DP-7 → HD-14 (EG-004 resolved with the controlled-benchmark amendment); DP-8 → HD-15 (EG-005 approach approved).
- **PENDING** (both await human review of the Architecture Baseline Pack): DP-2 → HD-9 (source-document disposition — HTML + mirror NOT superseded); DP-9 → HD-16 (final roadmap approval — closes Phase 1).
- **Stage 13 remains OPEN (`awaiting-human-decision`); Phase 1 is not complete.** No implementation, supersession, or programme closure is authorised.

### Stage 13 touchpoint note (2026-07-18)

The Stage 13 executor pass has assembled the roadmap and consolidated **all** decision-pack items into `13-approved-roadmap/outputs/final-decision-pack.md` (backing) and `stage-13-approval-prompt.md` (the self-contained pack the human responds to). Mapping of queue items to pack items (executor resolves none — options + consequences only):

- **DQ-007 (+ MFA) → DP-1**; **DQ-006/DQ-008 → DP-4**; **EG-004 → DP-7**; **EG-005 → DP-8** (statuses updated in the tables above).
- **RR-1 visibility (DEC-07-04) → DP-5** — presented for visibility, reaffirmed at Stage 10 (DEC-10-16), bounded to the current deployment shape; re-opens as a human decision only on a trigger (notably multi-tenant SaaS).
- **DEC-08-09 → DP-6** — visibility only; rides the C12 build item's standing `/arch-council` review (Tranche 2).
- **Source-document disposition (D-02-01) → DP-2** — approve/amend the supersede-and-replace recommendation.
- **SaaS fork (F-11-01) → DP-3** — single-bureau default carries unless the reviewer takes up the SaaS bundle (which then re-opens RR-1).
- **Roadmap approval → DP-9.**

No new queue item is opened by Stage 13. These items resolve at the human approval gate and are recorded in `_core/HUMAN-DECISIONS.md`; the queue rows above are updated with the decision reference at that point.

## Evidence gaps

| ID | Gap | Owner stage | Blocking? |
|---|---|---|---|
| EG-001 | Onboarding mapping time and error-rate baseline (B1) | 04/05 | no — instrument before C13. **Amended 2026-07-19 (DP-7 → HD-14):** the prior "requires a real onboarding, unrecoverable if it lands after C13" framing is replaced — B1 may be captured via a **controlled onboarding benchmark** from representative historical/synthetic data (manual vs platform-supported, measured consistently), with live evidence collected opportunistically. Simulated data labelled as controlled-benchmark evidence, never live-performance proof |
| EG-002 | Parallel-run agreement-rate baseline (B2) | 04/05 | no — instrument before C13. **Amended 2026-07-19 (DP-7 → HD-14):** same controlled-benchmark approach as EG-001; the hard real-onboarding-before-C13 dependency is removed while evidence integrity + labelling are preserved |
| EG-003 | Time-to-go-live baseline (B3) | 04/05 | no — instrument before C14 launch. **Capture protocol designed 2026-07-18 (Stage 10, baseline B3) — retrospectively computable now from engagement records + `payroll_run` history** (Tranche 0 T0.1) |
| EG-004 | **Next-onboarding timing** — whether/when Sandy expects the next new payroll client | 11 | **RESOLVED with amended evidence approach 2026-07-19 (DP-7 → HD-14).** Timing is unknown and no longer load-bearing: a future live onboarding is not the only acceptable evidence. B1/B2 are captured via a **controlled onboarding benchmark** (historical/synthetic data, consistent manual-vs-platform measurement), with live evidence collected opportunistically; replay data isolated, governed, and safely removed/retained per the evidence protocol. Simulated onboarding labelled as controlled-benchmark evidence, never live-performance proof |
| EG-005 | **Commercial demand / willingness-to-pay evidence** — no registered source or logged human statement records client demand for any capability or for SaaS commercialisation (F-11-02) | 11 | **Approach APPROVED 2026-07-19 (DP-8 → HD-15).** Distinguish validated capability from validated demand: external claims may describe evidence-supported capabilities, but demand/WTP/adoption/SaaS-viability are not "validated" without customer/market evidence. Still an open evidence gap: needed before external demand claims or any SaaS step (feeds DP-3); type-5 statements or registered external sources only, never invented |

## Rules

- Add an item when it is discovered; do not stop unless it is classified `blocking-human-decision`.
- Remove nothing silently. Mark resolved items with the decision/evidence reference.
- Later-stage implementation specifications are not human decisions unless they require a product, risk or compliance choice.
- The controller checks this file before advancing and before presenting a decision pack to the human reviewer.
