# Stage 07 → Stage 08 Handoff (Technical Architecture)

Security design decisions are made; Stage 08 builds the mechanisms. Binding items, with the deciding document in brackets:

## Mechanism build items with security constraints fixed

1. **C1 build shape** [identity-architecture-requirements.md]: operator table **plus operator–workspace membership relation** (§2 — Track P's single `workspace_id` column is corrected, not implemented as drawn); token claims per T2 incl. session/token ID; lifetime + revocation posture must be stated (T3); single shared route dependency with an explicit minimal unauthenticated allowlist (T4); step-up event objects in the session model now, consumed by C12 later (T5); auth-event audit records (T6).
2. **R1 rewiring** [identity-architecture-requirements.md §4]: remove `X-Performed-By` headers, body `actor_id`, free-text `resolved_by`-as-actor, and all hardcoded actor defaults (pinned at `ea1590a` in evidence §6); audit builders reject missing actors rather than defaulting.
3. **R2 enforcement point** [identity-architecture-requirements.md §5]: path-vs-claim check centralised in the dependency layer; mismatch → 404. The five decorative routes (evidence §1) get real enforcement as part of this — reconciliation trio first (F-05-03 Critical), then `get_run_timeline`/`legacy_executor_stats` (F-07-01); `legacy_executor_stats` must be either caller-scoped or moved to an explicit platform-ops surface.
4. **Tool-guard wrapper** [tool-layer-security-pattern.md]: declarative scoping config, fail-closed registration, P1–P8 properties, §3 verification tests. Decorator vs middleware is Stage 08's structural choice.
5. **Audit-store protection** [audit-integrity-threat-model.md §4]: append-only triggers as the floor (precedent `3da637afb11b`), role separation preferred if available; outbox explicitly covers audit records; no purge path pending DQ-008; correction-records pattern for wrong audit rows.
6. **Cut-over epoch** [audit-integrity-threat-model.md §6]: epoch persisted as data; pre-epoch rows mechanically labelled unverified in every consumer; one platform-wide epoch set at C1 cut-over.
7. **Step-up mechanism** [approval-security-design.md §3]: credential re-entry producing a recorded, referenceable step-up event; freshness window (minutes — Stage 08 sets the value); one approval per step-up event; TOTP slot when MFA exists.
8. **F-05-11 closures** [tenant-isolation-verification-standard.md §3.5]: `load_inputs_for_run` gains a `workspace_id` parameter+filter; `workspace_info()` `LIMIT 1` retired (token-scoped or removed with the legacy admin template).
9. **Serialization hardening** [agent-layer-threat-model.md §3.4]: untrusted DB strings rendered as data in tool output; PII sanitizer version stamped per invocation (joins SC-3's record fields).
10. **CORS pinning** [identity-architecture-requirements.md §7]: production `ALLOWED_ORIGINS` configuration item in the C1 deployment checklist.

## Verification standards Stage 08's builds must satisfy

- Route-table isolation test (every `{workspace_id}` route enforced or allowlisted — generated from the app's route table, CI-enforced) [tenant-isolation-verification-standard.md §3.2–3.3]
- Tool-registry uniformity/negative-path/wrapper-independence/fail-closed tests [tool-layer-security-pattern.md §3]
- Audit immutability + outbox-failure + epoch-labelling tests [audit-integrity-threat-model.md §7]
- Route-enumeration auth test for T4 [identity-architecture-requirements.md §3]

## Not re-opened here

DQ-001–005 (Stage 08's existing queue) are untouched. C10 protocol details (DQ-002) gain only the security constraints in `approval-security-design.md` §4 (idempotency, expiry records, payload freezing). The dry-run mechanism (DQ-003/004) gains SG-14's identity/scoping constraints. No new blocking human decisions were raised by this stage; DEC-07-03 (step-up) and the MFA-with-DQ-007 note are recorded in `decisions.md` and the decision queue respectively.
