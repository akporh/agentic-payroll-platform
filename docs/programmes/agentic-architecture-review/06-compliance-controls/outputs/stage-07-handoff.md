# Stage 06 → Stage 07 Handoff (Security & Identity)

## Binding requirements this stage places on the security architecture

`outputs/attribution-identity-requirements.md` R1–R6 are compliance obligations, not suggestions: verified actor on every mutating action (R1); workspace identity from the token only (R2); named service principals for system actions (R3); non-repudiation-grade records for approval-class actions (R4); live-session confirmation for platform-blast-radius approvals, with step-up auth as a Stage 07 design choice (R5); no placeholder-identity operation of compliance features (R6).

## New evidence Stage 07 should start from (this stage's code reads, not Stage 05 restated)

- **F-06-01**: the audit trail that *does* exist records self-asserted identity — `X-Performed-By` header (default `admin@internal`) on retry/approve/lock; body `actor_id` (default `system@internal`) on pay; free-text body `resolved_by` on reconciliation resolution. Evidence: `evidence/06-attribution-and-audit-integrity-excerpts.md` §1. Auth design must include the audit-actor derivation path, not just route protection.
- **F-06-02/03**: audit writes are post-commit fire-and-forget in separate sessions; no immutability trigger or retention mechanism protects `audit_log`/`event_store`. Integrity of the audit store is a security property too (an attacker who can UPDATE audit rows defeats non-repudiation) — DB-layer protection is in scope for Stage 07's threat model.

## Classification upgrade to carry

`outputs/tenant-isolation-control-assessment.md`: the reconciliation scoping gap is a **compliance control failure** (false attestation of isolation), and the platform-wide auth absence is a **control-environment failure** for a multi-client bureau. Stage 07 should treat auth as compliance remediation, with the urgency framing that implies. F-05-11's two internal functions remain "weakness, fix-before-wrapping" — not upgraded.

## Open items forwarded

- Historical audit rows carry unverified identity permanently; recommended treatment is a documented cut-over epoch (past records labelled "identity unverified"), since the past cannot be re-attributed — confirm or improve in Stage 07/08. Implementation specification, not a human decision.
- R5's step-up-auth question (re-prompt vs live-session check for C12 approvals) — Stage 07 design choice within the stated control requirement.

## Out of scope claims this stage did NOT make

No mechanism choices (token tech, session model, 2FA) were made; no new severity was assigned to F-05-01 (Stage 05's Critical framing stands); C12/C10/C11 remain unbuilt — the requirements above bind their future builds.
