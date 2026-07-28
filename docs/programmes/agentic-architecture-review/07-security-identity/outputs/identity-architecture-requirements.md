# Stage 07 Output: Identity & Auth Architecture Requirements (C1)

Requirements-level design for the identity/auth foundation, reviewing the source document's Track P design (`docs/architecture/agent-layer-architecture.html:643-723`, stories P1–P6) against the approved portfolio (D-03-01) and Stage 06's binding requirements R1–R6 (`06-compliance-controls/outputs/attribution-identity-requirements.md`). Track P is the design under review, not authority. Stage 08 owns wiring and mechanism build; library/framework choices are left open except where security-load-bearing.

Framing carried from Stage 06 (F-06-05): this is **remediation of an absent control environment** for a multi-client bureau — compliance urgency, not feature work.

## 1. Principal model

Two principal classes, both first-class and both enumerable from the database:

1. **Human operators** — Track P's P1 `operator` table is the right anchor (id, email, role, password_hash), **with one required correction** (§2).
2. **Named service principals** (R3) — e.g. `svc:scheduler`, `svc:event-consumer`, `svc:compliance-monitor`. Requirements: (a) each is a named row in the same principal store (or a dedicated table — Stage 08 choice) so audit joins resolve uniformly; (b) non-interactive — no password login path; credentialed by deployment configuration, not user flows; (c) distinguishable by type from human operators in every audit record; (d) created per named workload — never a shared `svc:system` catch-all, which would recreate today's `"system"` placeholder problem (F-06-01).

Today's literals (`"admin@internal"`, `"system@internal"`, `"system"` — evidence file §6) are eliminated: after C1, no code path may construct an actor identity from a constant, header, or request body.

## 2. Required correction to Track P: operator↔workspace is a membership, not a column

Track P's P1 puts `workspace_id` as a **column on `operator`** — one operator, one workspace, permanently. That model cannot serve the platform's own primary user: Sandy is a bureau whose operators administer **many client workspaces** (business-context fact, per `06-compliance-controls/outputs/tenant-isolation-control-assessment.md` §1; the platform's own `GET /workspaces` list route and multi-workspace schema confirm the deployment shape). Under P1-as-drawn, a bureau operator needs one account per client — defeating attribution (R1: which human acted?) and making the audit trail per-workspace pseudonymous.

**Requirement:** an **operator–workspace membership** relation (many-to-many), checked at token issuance. This is an executor conclusion from evidence and inherited principles, not a human decision — no reasonable single-workspace reading of the bureau model exists (recorded in stage `decisions.md`, DEC-07-02).

Track P's P6 (session locked to one workspace, new session on switch) then **generalises correctly**: a token/session carries exactly **one active workspace** claim, selected at login/switch from the operator's memberships. The single-active-workspace-per-token property is what makes R2 enforcement simple and is retained as a requirement, not just a convenience.

## 3. Token and session requirements

Mechanism-agnostic requirements (signed JWT per Track P P2 is an acceptable mechanism; these properties are what the build must guarantee):

- **T1 — Integrity**: tokens are integrity-protected (signed) with server-held key material; secrets/keys never in the repo; rotation possible without a schema change.
- **T2 — Claims**: `operator_id` (or service-principal id), exactly one `workspace_id` (the active workspace, §2), principal type, issuance and expiry timestamps, and a unique token/session identifier (needed by R4 records to reference the auth context).
- **T3 — Lifetime**: short-lived access tokens (order of hours, not days). Whatever refresh/re-login model Stage 08 picks, the design must state the maximum time a stolen token remains usable and the revocation posture (accept expiry-only revocation with short TTL, or maintain a server-side denylist — Stage 08 choice; "no stated posture" is not acceptable).
- **T4 — Verification everywhere**: a single shared dependency (Track P P3's `get_current_operator`) applied to **every** route; allowlist of unauthenticated endpoints is explicit, reviewed, and minimal (login, health). CG-1's "100% of routes authenticate" is the gate; the closure evidence is a test that enumerates the app's routes and asserts each is protected or explicitly allowlisted — not a per-route sample.
- **T5 — Step-up context**: the token/session model must support recording a **fresh re-authentication event** at a point in time (for R5/C12 — see `approval-security-design.md`), referenceable by ID from an approval record.
- **T6 — Auth events are audited**: login success/failure, token issuance, step-up events, and membership changes are themselves audit records under the Stage 06 integrity properties (append-only, attributable, reliably written). An identity system whose own changes are unlogged undermines every record depending on it.
- **T7 — Password handling**: modern adaptive hash (bcrypt/argon2 class), no plaintext or reversible storage, no password in logs. (Standard hygiene; stated because the platform has no existing precedent to inherit.)

Deferred, consistent with Track P's own scope discipline: RBAC beyond a minimal role field, MFA enrollment, SSO. Deferral is acceptable **except** where R5 resolves to step-up auth — see `approval-security-design.md` for what C12 requires before it launches (C12 is itself gated on DQ-007, so MFA/step-up capability arrives with C12, not necessarily with C1).

## 4. R1 — Audit-actor derivation path (route → record)

The satisfaction path, stated end-to-end:

1. Route handler receives the verified principal from the shared dependency (T4) — never from a header or body.
2. The principal (id + type) is passed as an explicit parameter through the service layer to every audit/event builder. The existing caller-supplied inputs are **removed**: `X-Performed-By` headers (payroll.py:1180, 1207, 1227), body `actor_id` (payroll.py:1255-1259), free-text `resolved_by` (payroll.py:1356-1365), and all hardcoded defaults (payroll.py:992, 1009; `payroll_retry_service.py:510`) — evidence file §6.
3. Audit builders reject a missing actor rather than defaulting — a write without a verified principal is a bug surfaced loudly, not a row attributed to `admin@internal`.
4. `resolved_by` on reconciliation resolution becomes the verified principal; if a free-text "resolved on behalf of" note is operationally wanted, it is a separate annotation field, never the actor field.

**Verification:** grep-clean check (no `X-Performed-By`, no actor defaults) + committed tests asserting each mutating route's audit record carries the authenticated principal, per F-06-01's closure evidence.

## 5. R2 — Token-derived workspace identity

- Every workspace-scoped query derives its `workspace_id` from the verified token claim. Path parameters remain for routing/REST shape but are **checked against the claim — mismatch returns 404** (not 403: a cross-workspace prober learns nothing about resource existence; consistent with the tool matrix's 404/refusal convention). This check lives in the shared dependency layer, not per-handler discretion.
- No request body, header, or query parameter is ever read as a workspace identity. The frontend's stored workspace selection becomes display/navigation state only.
- The five decorative routes (evidence file §1, F-07-01) are covered automatically once path-vs-claim checking is centralised — but their underlying data paths must also enforce workspace at the query level per the two-layer standard (`tenant-isolation-verification-standard.md`).

**Verification:** the per-route negative-path standard in `tenant-isolation-verification-standard.md` §3.

## 6. R3/R5/R6 satisfaction paths

- **R3**: §1's service-principal model; every scheduled/autonomous code path (today: none confirmed beyond service defaults; future: C2 consumer, C6 checks, C11 monitoring) is assigned a named principal at build time. Verification: a test asserting no audit record carries a non-enumerated actor.
- **R5**: resolved as step-up re-authentication for platform-blast-radius approvals — design and reasoning in `approval-security-design.md` §3.
- **R6**: restated as a launch gate, not a code property: no compliance-evidence capability (C10, C12, agent tool logging) ships before C1 is live — `security-gate-register.md` SG-1 and standing control SC-1 already carry this; nothing here weakens it.

## 7. Deployment-surface requirements

- **CORS**: `ALLOWED_ORIGINS` defaults to `*` (`backend/api/main.py:36-45`, evidence file §7). At C1 launch, production origin pinning becomes mandatory configuration, and the check belongs in a deployment checklist with closure evidence (deployed config inspection), not code review alone. With header-borne tokens and `allow_credentials=False` this is hardening, not a launch blocker — recorded as F-07-03.
- **Transport**: tokens only over TLS; no token in URL/query strings (they persist in logs).

## 8. What Track P got right (kept unchanged)

P2 (login → JWT), P3 (single shared dependency), P4 (workspace from token only — "non-negotiable invariant" per the document), P5 (performed_by from verified identity across all audit writes), P6 (session workspace lock), and the scope discipline note (minimum viable auth first). The corrections this review adds: the membership model (§2), service principals (§1/R3 — absent from Track P), token lifetime/revocation posture (T3 — unstated in Track P), auth-event auditing (T6 — unstated), and the step-up hook (T5).
