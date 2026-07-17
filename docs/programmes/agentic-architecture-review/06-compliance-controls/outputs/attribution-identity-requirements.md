# Stage 06 Output: Attribution & Identity Requirements — Binding on Stage 07

States the identity guarantees compliance controls require. Consumes F-05-01 (zero authentication exists anywhere; `workspace_id` is a caller-supplied string — not re-verified here, per stage context). Stage 07 owns the security architecture that satisfies these; Stage 08 owns wiring. This stage's own contribution is the *audit-record-content* evidence: even the audit trail that does exist today records self-asserted identity (F-06-01).

## 1. Requirements

**R1 — Verified actor on every mutating action.** Every state-changing request (run transitions, reconciliation resolution, configuration changes, future C12 approvals, future C10 confirmations) must execute under an authenticated principal, and the audit record's actor field must be derived from that principal server-side. It must be impossible for a caller to assert an arbitrary actor identity. Current violations, confirmed by direct code read (evidence file §1): `X-Performed-By` header (default `"admin@internal"`) on retry/approve/lock; request-body `actor_id` (default `"system@internal"`) on pay; free-text request-body `resolved_by` on reconciliation resolution.

**R2 — Workspace identity from the token only.** `workspace_id` must come from the verified token/claims, never from path/body/header trust. (Path parameters may remain for routing, but must be checked against the token's workspace — a mismatch is a 403/404, not silently honoured.) This is the enforcement layer beneath every workspace-scoping fix; without it, even correctly-scoped queries only protect against honest callers (Stage 05's framing, consumed).

**R3 — Named service principals for system actions.** Autonomous actions (scheduled jobs, event consumers, future C11 monitoring runs) are attributed to distinct, named service principals — e.g. `svc:reconciliation-worker` — never to a shared placeholder. Today's `"system"` / `"admin@internal"` / `"system@internal"` strings are indistinguishable from "unknown" and from each other's origins.

**R4 — Non-repudiation for approval-class actions.** For C12 statutory approvals, C10 confirmations, and reconciliation resolutions: the record must be sufficient to establish *after the fact, against a disputing party* who approved what, when, having been shown what. Minimum: verified principal, auth-session/token identity, decision timestamp, and the decision payload as presented (content or immutable reference). Full cryptographic signing is not required at requirements level; what is required is that the platform operator can stand behind the record's integrity (append-only storage per `audit-expansion-requirements.md` §3.3 + verified identity). Stage 07 decides whether stronger mechanisms are warranted.

**R5 — Re-authentication context for high-blast-radius approvals.** A C12 approval (platform-wide effect) must at minimum re-confirm the approver's live session at decision time (not act on a long-lived stale token). Whether step-up/re-auth (password/2FA re-prompt) is required is a Stage 07 design choice; the control requirement is that a hijacked idle session must not be sufficient to approve a statutory change silently.

**R6 — No placeholder-identity operation of compliance features.** Any capability whose value is its audit/approval record (C12, C10, agent tool logging) must not ship in a placeholder-identity mode. This generalises the architecture document's own W5 rule ("placeholder operator_id audit trail is worse than none," line 496) from `agent_session_log` to all compliance-evidence writes. Corollary: C1 (auth) precedes every compliance-evidence capability — consistent with Stage 05's readiness matrix, restated here as a control obligation rather than a sequencing observation.

## 2. Explicitly not decided here

- Token technology, session model, operator-account lifecycle, 2FA policy — Stage 07.
- Whether existing *historical* audit rows (with self-asserted identity) need remediation or just a documented cut-over date once real identity ships — forwarded to Stage 07/08 as an implementation specification; the plausible answer is a documented epoch ("records before date X carry unverified identity"), since the past cannot be re-attributed.

## 3. Traceability

| Requirement | Grounded in |
|---|---|
| R1 | F-06-01 (this stage); F-05-01 |
| R2 | F-05-01; Stage 05 tool-readiness findings (F-05-11) |
| R3 | F-06-01 evidence (`"system"`, `"admin@internal"` literals) |
| R4 | C12/C10 control designs (this stage); D-02-04's mandatory human gate |
| R5 | C12's platform-level blast radius (F-01-45 decoupling, consumed) |
| R6 | S-04 line 496 (intended design); F-06-01 (current gap) |
