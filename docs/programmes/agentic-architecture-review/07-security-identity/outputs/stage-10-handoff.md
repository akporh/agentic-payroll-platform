# Stage 07 → Stage 10 Handoff (Evaluation & Assurance)

Verification standards this stage defined, handed to Stage 10 as assurance inputs to evaluate against — per the stage boundary: Stage 07 hands verification standards, not eval design. Stage 10 designs how these are exercised, extended, and evidenced over time.

## 1. Standing verification artifacts Stage 10 should treat as assurance controls

| Artifact | Defined in | What it proves |
|---|---|---|
| Route-table isolation test (every `{workspace_id}` route enforced or allowlisted; generated from the live route table) | `tenant-isolation-verification-standard.md` §3.2–3.3 | Decorative scoping (F-05-03/F-07-01) cannot recur silently |
| Per-invariant regression tests + isolation control statement citing the route test | same, §3.1/3.4 | The bureau's client-facing isolation claim is continuously true, not point-in-time |
| Tool-registry uniformity + per-tool negative-path + wrapper-independence + fail-closed tests | `tool-layer-security-pattern.md` §3 | Condition 14 holds for every tool, including future ones |
| Route-enumeration authentication test (T4) | `identity-architecture-requirements.md` §3 | CG-1's "100% of routes authenticate" stays closed |
| Audit immutability, outbox-failure, epoch-labelling tests | `audit-integrity-threat-model.md` §7 | R4's storage floor; F-06-02/03 stay closed |
| Step-up flow test (freshness window, one-approval-per-event, record linkage) | `approval-security-design.md` §3 | R5 as implemented matches DEC-07-03 |

## 2. Security-adjacent evaluation requirements for the LLM capabilities

These are *launch-gate evidence* (SG rows) whose ongoing methodology is Stage 10's to design:

- **Adversarial/injection test sets** per LLM capability (T1/T2 generally; T5 hostile-source fixtures for C11; hostile spreadsheet headers for C13). Stage 07 fixes that the evidence must exist and pass at launch; Stage 10 decides corpus construction, refresh cadence, and pass criteria evolution.
- **Refusal-quality evaluation**: refusals are first-class audited outcomes (SC-3); Stage 10 should evaluate not just refusal *rate* (already in CG-3's framing for the D-02-03 boundary) but refusal *correctness* on cross-workspace and out-of-scope probes — the audit trail's `refused` records are the natural data source.
- **C5 numeric-provenance check** (CG-5) — already programmatic; Stage 10 owns keeping it meaningful as trace shapes evolve.
- **Session-scope conformance**: periodic verification that each capability's session registry matches its approved minimum tool set (SS-4) — drift here is a security regression that no functional eval would catch.

## 3. Facts Stage 10 should carry

- The platform's decorative-scoping habit is empirically recurrent (five routes across two discovery rounds — F-05-03, F-07-01). Assurance design should assume scaffolding-pattern regressions are *likely*, which is why the standing tests in §1 are route-table-generated rather than enumerated by hand.
- Audit records before the C1 cut-over epoch are permanently unverified-identity (`audit-integrity-threat-model.md` §6); any assurance reporting over historical audit data must respect the epoch boundary.
- Residual risks accepted at requirements level (DB-superuser tampering; no cryptographic signing of approvals; no external anchoring) are listed in `audit-integrity-threat-model.md` §5 and `approval-security-design.md` §2 — if Stage 10's assurance framework or a future client/regulator demand more, those are the two documents to revisit rather than re-deriving the posture.
