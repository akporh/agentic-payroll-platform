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
| DQ-006 | Tier-1 authoritative-source allowlist for FIRS/PenCom regulatory monitoring — which sources are *legally sufficient* requires human + professional legal/tax sign-off (`06-compliance-controls/outputs/compliance-monitoring-source-policy.md` §4). Hard gate before C11 build authorisation | 06 | human reviewer (pre-C11 build; surfaces at Stage 11/13) | **forwarded — surfaced in the Stage 13 pack as DP-4** (`13-approved-roadmap/outputs/final-decision-pack.md`): bundled with DQ-008 into one professional engagement, initiate at/after approval; concludes before any C11 sprint (Tranche 5). Not resolved by the executor |
| DQ-007 | Single-operator segregation-of-duties waiver for C12 statutory approvals — proposer ≠ approver may be operationally impossible for a small bureau; options incl. compensating controls (`06-compliance-controls/outputs/statutory-change-control-design.md` §8). Must resolve before C12 build authorisation. **Context amendment (Stage 07, 2026-07-17):** decide together with whether MFA enrollment for approval-capable operators becomes a *hard* C12 launch gate — R5 is resolved as step-up re-auth (DEC-07-03, `07-security-identity/outputs/approval-security-design.md` §3); password-only step-up is the floor, and both questions are risk-appetite calls on the same approval action | 06 (amended 07) | human reviewer (pre-C12 build; surfaces at Stage 13) | **forwarded — surfaced in the Stage 13 pack as DP-1** (`13-approved-roadmap/outputs/final-decision-pack.md`): options A1/A2 (waiver vs hold, A2 promotes multi-operator to a C12 prerequisite) + B1/B2 (MFA hard gate vs password-only floor), consequences shown. Earliest human gate; gates Tranche 2 (C12). Not resolved by the executor |
| DQ-008 | Legal confirmation of audit/evidence retention period — source document asserts 7 years without cited basis; statutory minimum and any data-protection maximum need professional confirmation (`06-compliance-controls/outputs/agent-tool-audit-standard.md` §2). Gates retention-enforcing mechanisms only; "keep at least 7y" is the working floor meanwhile | 06 | human reviewer + Stage 08 | **forwarded — surfaced in the Stage 13 pack as DP-4** (`13-approved-roadmap/outputs/final-decision-pack.md`): bundled with DQ-006; blocks retention-enforcement tooling only (O9); "keep at least 7y, no purge" is the working floor. Not resolved by the executor |

## Visibility items (not queued decisions)

- **DEC-07-04** — audit-tamper residual-risk acceptance (in-DB controls don't bind a DB superuser; external anchoring judged disproportionate) — flagged for review at Stage 10/13. **Stage 10 review performed 2026-07-18: reaffirmed on unchanged facts (DEC-10-16, `10-evaluation-assurance/outputs/residual-risk-register.md` §3), explicitly bounded to the current deployment shape — multi-tenant commercialisation re-opens it as a human decision (RR-1 trigger (c)). Stage 13 visibility touchpoint stands.**
- **DEC-08-09** — Stage 08's C12 correction mechanics commit Phase 3 to proposing a **data-contract change**: `statutory_rule` UNIQUE widens from `(country_code, effective_from)` to `(country_code, effective_from, version)` (resolution stays total-ordered; the tie-break already exists in code, F-08-01). Flagged by the Stage 08 critic for the next human-reviewer touchpoint, pre-build authorisation; goes through the repo's standing `/arch-council` gate at Phase 3.

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
| EG-001 | Onboarding mapping time and error-rate baseline | 04/05 | no — instrument before C13/C14 launch. **Capture protocol designed 2026-07-18 (Stage 10, baseline B1: `10-evaluation-assurance/outputs/evidence-chain-and-baselines.md` B §2) — requires a real onboarding under the current flow; unrecoverable if the next onboarding happens after C13 ships (Stage 11 sequencing note)** |
| EG-002 | Parallel-run agreement-rate baseline | 04/05 | no — instrument before C13/C14 launch. **Capture protocol designed 2026-07-18 (Stage 10, baseline B2, same doc) — same real-onboarding dependency as EG-001** |
| EG-003 | Time-to-go-live baseline | 04/05 | no — instrument before C13/C14 launch. **Capture protocol designed 2026-07-18 (Stage 10, baseline B3, same doc) — retrospectively computable now from engagement records + `payroll_run` history** |
| EG-004 | **Next-onboarding timing** — whether/when Sandy expects the next new payroll client. The single scheduling fact the unrecoverable B1/B2 baseline window (W2) hinges on; only Michael can supply it (evidence type 5) | 11 | no — but must resolve before C13/C14 sprint planning; **surfaced in the Stage 13 pack as DP-7** (`13-approved-roadmap/outputs/final-decision-pack.md`) — explicit ask at the touchpoint; if an onboarding is plausible in the C13/C14 horizon, arm the B1/B2 protocol ahead of it regardless of build order |
| EG-005 | **Commercial demand / willingness-to-pay evidence** — no registered source or logged human statement records client demand for any capability or for SaaS commercialisation (F-11-02). Value-map "differentiation" rows mean *claimable*, not *market-verified*, until this closes | 11 | no — needed before external-facing claims or a SaaS decision; type-5 statements or registered external sources only, never invented; **surfaced in the Stage 13 pack as DP-8** (`13-approved-roadmap/outputs/final-decision-pack.md`) — no action required to approve the roadmap; feeds the SaaS fork (DP-3) |

## Rules

- Add an item when it is discovered; do not stop unless it is classified `blocking-human-decision`.
- Remove nothing silently. Mark resolved items with the decision/evidence reference.
- Later-stage implementation specifications are not human decisions unless they require a product, risk or compliance choice.
- The controller checks this file before advancing and before presenting a decision pack to the human reviewer.
