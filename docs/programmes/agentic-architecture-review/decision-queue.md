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
| DQ-005 | Should `run_type = CORRECTION` remain API-only by design or be exposed in the UI — classified `non-blocking-forwarded-decision` by the Stage 05 critic (F-05-12) | 05 | 09/11 | **Stage 09 recommendation recorded 2026-07-17** (`09-human-experience/outputs/stage-11-handoff.md` §1): no generic dropdown exposure; introduce as a context-launched "Create correction run" CTA with/after the C12 build (grounded in F-09-02 re-verification). Remains with Stage 11 for joint disposition |
| DQ-006 | Tier-1 authoritative-source allowlist for FIRS/PenCom regulatory monitoring — which sources are *legally sufficient* requires human + professional legal/tax sign-off (`06-compliance-controls/outputs/compliance-monitoring-source-policy.md` §4). Hard gate before C11 build authorisation | 06 | human reviewer (pre-C11 build; surfaces at Stage 11/13) | forwarded |
| DQ-007 | Single-operator segregation-of-duties waiver for C12 statutory approvals — proposer ≠ approver may be operationally impossible for a small bureau; options incl. compensating controls (`06-compliance-controls/outputs/statutory-change-control-design.md` §8). Must resolve before C12 build authorisation. **Context amendment (Stage 07, 2026-07-17):** decide together with whether MFA enrollment for approval-capable operators becomes a *hard* C12 launch gate — R5 is resolved as step-up re-auth (DEC-07-03, `07-security-identity/outputs/approval-security-design.md` §3); password-only step-up is the floor, and both questions are risk-appetite calls on the same approval action | 06 (amended 07) | human reviewer (pre-C12 build; surfaces at Stage 13) | forwarded |
| DQ-008 | Legal confirmation of audit/evidence retention period — source document asserts 7 years without cited basis; statutory minimum and any data-protection maximum need professional confirmation (`06-compliance-controls/outputs/agent-tool-audit-standard.md` §2). Gates retention-enforcing mechanisms only; "keep at least 7y" is the working floor meanwhile | 06 | human reviewer + Stage 08 | forwarded |

## Visibility items (not queued decisions)

- **DEC-07-04** — audit-tamper residual-risk acceptance (in-DB controls don't bind a DB superuser; external anchoring judged disproportionate) — flagged for review at Stage 10/13. **Stage 10 review performed 2026-07-18: reaffirmed on unchanged facts (DEC-10-16, `10-evaluation-assurance/outputs/residual-risk-register.md` §3), explicitly bounded to the current deployment shape — multi-tenant commercialisation re-opens it as a human decision (RR-1 trigger (c)). Stage 13 visibility touchpoint stands.**
- **DEC-08-09** — Stage 08's C12 correction mechanics commit Phase 3 to proposing a **data-contract change**: `statutory_rule` UNIQUE widens from `(country_code, effective_from)` to `(country_code, effective_from, version)` (resolution stays total-ordered; the tie-break already exists in code, F-08-01). Flagged by the Stage 08 critic for the next human-reviewer touchpoint, pre-build authorisation; goes through the repo's standing `/arch-council` gate at Phase 3.

## Evidence gaps

| ID | Gap | Owner stage | Blocking? |
|---|---|---|---|
| EG-001 | Onboarding mapping time and error-rate baseline | 04/05 | no — instrument before C13/C14 launch. **Capture protocol designed 2026-07-18 (Stage 10, baseline B1: `10-evaluation-assurance/outputs/evidence-chain-and-baselines.md` B §2) — requires a real onboarding under the current flow; unrecoverable if the next onboarding happens after C13 ships (Stage 11 sequencing note)** |
| EG-002 | Parallel-run agreement-rate baseline | 04/05 | no — instrument before C13/C14 launch. **Capture protocol designed 2026-07-18 (Stage 10, baseline B2, same doc) — same real-onboarding dependency as EG-001** |
| EG-003 | Time-to-go-live baseline | 04/05 | no — instrument before C13/C14 launch. **Capture protocol designed 2026-07-18 (Stage 10, baseline B3, same doc) — retrospectively computable now from engagement records + `payroll_run` history** |

## Rules

- Add an item when it is discovered; do not stop unless it is classified `blocking-human-decision`.
- Remove nothing silently. Mark resolved items with the decision/evidence reference.
- Later-stage implementation specifications are not human decisions unless they require a product, risk or compliance choice.
- The controller checks this file before advancing and before presenting a decision pack to the human reviewer.
