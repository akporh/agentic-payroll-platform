# Stage 07 Output: Security Gate Register

Security **launch gates** per capability — additive to the compliance control-gate register (CG-1–15, `06-compliance-controls/outputs/control-gate-register.md`) and Stage 05's readiness/blocker registers. Security-specific criteria only; compliance gates are referenced, never restated or weakened (stage constraint). A capability launches only when its CG row, its SG row, and its technical-readiness gaps are all closed.

Standing security controls (every row; complement SC-1–4):

- **SS-1** — the two-layer tenant-isolation standard with its route-table verification test green (`tenant-isolation-verification-standard.md` §3.2–3.3)
- **SS-2** — the tool-guard wrapper pattern with its uniformity/negative-path/fail-closed tests green for every registered tool (`tool-layer-security-pattern.md` §3)
- **SS-3** — audit-store integrity protections live (append-only enforcement + outbox-coupled writes) before any capability whose value is its records (`audit-integrity-threat-model.md`)
- **SS-4** — capability-scoped tool registries: each session exposes its capability's minimum tool set (`agent-layer-threat-model.md` §3.1)

| Capability | Security launch gates (beyond SS-1..4 and its CG row) | Gate ID |
|---|---|---|
| C1 — Identity & Auth | Route-enumeration test proves 100% of routes authenticated or explicitly allowlisted (T4); membership model (not per-workspace accounts) live; R1 derivation path with caller-supplied actor inputs removed (grep-clean + tests); token claims/lifetime/revocation posture stated and tested; auth events audited (T6); step-up hook present in session model (T5); production CORS origin pinning confirmed in deployed config (F-07-03); `workspace_info()` `LIMIT 1` form retired or token-scoped (F-07-02) | SG-1 |
| C2 — Event/Tool/Notification | Outbox covers audit records (not just events) with the failed-write test green; tool serializer renders untrusted strings as data (threat model §3.4); PII sanitizer versioned and its version logged per invocation | SG-2 |
| C3 — Operator Assistant | Injection test set (T1/T2) committed and passing; session tool registry = C3's five tools only; per-tool negative-path tests green; rate limiting (W3) live | SG-3 |
| C4 — Historical Explanation | Blocked (D-02-03) — define SG when unblocked | SG-4 |
| C5 — Trace Explanation | Numeric-provenance check (CG-5) doubles as the T6 control — no additional gate; session registry = `get_run_results` path only | SG-5 |
| C6 — Readiness Service | Named service principal (R3) for any scheduled execution; no LLM in path — route-layer standard applies | SG-6 |
| C7 — Anomaly Detection | Detector remains deterministic (T6); if narration ships: injection test set + registry scoped to anomaly context | SG-7 |
| C8 — Reconciliation Investigation | Blocked (D-02-02/D-02-03). Security closure evidence for F-05-03 beyond the code fix: the CG-8 control-evidence set **plus** the route-table verification test (SS-1) green — proving the decorative-scoping pattern (F-07-01) is dead platform-wide, not just on reconciliation routes | SG-8 |
| C9 — Trace Agent | Rejected — no gates | SG-9 |
| C10 — Confirmation Protocol | R4-grade records incl. payload-as-presented freezing; idempotent execution tested; confirmation is an authenticated UI action distinct from chat; expiry/invalidation produce records (`approval-security-design.md` §4) | SG-10 |
| C11 — Compliance Monitoring | Context isolation: no workspace-scoped tool registered (threat model §3.2); Tier-1 allowlist enforced in fetch code (list itself gated on DQ-006); T5 injection test set incl. hostile-source fixtures; every proposal carries provenance fields | SG-11 |
| C12 — Statutory Change Mgmt | Step-up re-auth (R5, DEC-07-03) implemented with freshness window and one-approval-per-step-up; step-up events recorded and referenced from the approval record; MFA for approval-capable operators recommended pre-launch (decide with DQ-007); approval record meets `approval-security-design.md` §2 in full | SG-12 |
| C13 — Onboarding Mapping | Header-borne injection test fixtures (hostile spreadsheet content) committed and passing; proposals render only to uploading operator's session; catalog tool under SS-2 like any tool | SG-13 |
| C14 — Import Validation & Dry-Run | Dry-run executes under the operator's verified identity and workspace (R1/R2); dry-run artifacts workspace-scoped; no LLM — route-layer standard | SG-14 |
| C15 — Email Notifications | Deferred. Pre-launch: no tokens/links granting authenticated access without fresh login (no magic-link session bypass); CG-15's PII hygiene stands | SG-15 |

## Register maintenance

Same rules as the CG register: owned by this programme until Phase 3 adoption; Stage 13 consumes it for sequencing; a gate may only be weakened by a recorded human decision. SG gates add to CG gates — where both registers touch the same control (e.g. C12 approvals), the stricter reading governs.
