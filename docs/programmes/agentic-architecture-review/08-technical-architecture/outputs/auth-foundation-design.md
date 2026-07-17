# Stage 08 Output: Auth Foundation Design (C1)

Mechanism design answering Stage 08 Q1, within the binding requirements of `07-security-identity/outputs/identity-architecture-requirements.md` (T1–T7, R1/R2, DEC-07-02 membership model), `stage-08-handoff.md` items 1–3/6–7/10, and the Stage 06 integrity properties. Design level — no code. Evidence pinned at `573be0d` (all `ea1590a` citations re-resolved unchanged; see `findings.md` F-08-03).

## 1. Schema

### 1.1 `operator` (principal store — humans and service principals in one table)

| Column | Type | Notes |
|---|---|---|
| `operator_id` | UUID PK | |
| `email` | VARCHAR(255) UNIQUE NOT NULL | For service principals, a conventional non-routable identifier (`svc-event-consumer@service.local`) — kept in the same column so audit joins resolve uniformly (identity-arch §1a) |
| `display_name` | VARCHAR(100) NOT NULL | e.g. `svc:event-consumer` for service principals |
| `principal_type` | VARCHAR(10) NOT NULL CHECK IN ('HUMAN','SERVICE') | Satisfies §1c — distinguishable in every audit record via join |
| `role` | VARCHAR(30) NOT NULL DEFAULT 'OPERATOR' | Minimal: `OPERATOR`, `PLATFORM_ADMIN`. `PLATFORM_ADMIN` gates the C12 surface and platform-ops routes (F-07-01's `legacy_executor_stats` disposition). RBAC beyond this is deferred per Track P scope discipline |
| `password_hash` | VARCHAR(255) NULL | Argon2id (T7). NULL for service principals — **no password login path for `SERVICE` rows is enforced in the login route** (`principal_type = 'HUMAN'` filter), satisfying §1b |
| `is_active` | BOOLEAN NOT NULL DEFAULT true | Deactivation, not deletion — audit joins must survive |
| `created_at` / `updated_at` | TIMESTAMPTZ | |

Service principals are created per named workload by migration/seed, never a shared catch-all (§1d). Initial set: `svc:event-consumer` (C2 worker). Future: `svc:readiness-check` (C6), `svc:compliance-monitor` (C11) — added when those capabilities are built.

### 1.2 `operator_workspace_membership` (DEC-07-02 — membership, not a column)

| Column | Type |
|---|---|
| `operator_id` | UUID FK → operator, part of PK |
| `workspace_id` | UUID FK → workspace, part of PK |
| `created_at` | TIMESTAMPTZ |
| `created_by` | UUID FK → operator (who granted it — membership changes are audited, T6) |

Checked at token issuance and at workspace switch. Service principals get memberships only where their workload requires workspace-scoped writes (the C2 consumer writing `workspace_notification` acts platform-wide and is instead authorised by principal type in the worker code path — it never authenticates over HTTP).

### 1.3 `auth_session` (revocation posture — T3)

| Column | Type |
|---|---|
| `session_id` | UUID PK (the JWT `sid` claim) |
| `operator_id` | UUID FK NOT NULL |
| `workspace_id` | UUID FK NOT NULL (the active workspace this session is locked to — P6 generalised) |
| `issued_at` / `expires_at` | TIMESTAMPTZ NOT NULL |
| `revoked_at` | TIMESTAMPTZ NULL |

**Revocation posture (T3, stated):** access tokens are signed JWTs with **8-hour lifetime** (one working day; order-of-hours per T3). Verification checks signature + `exp` + `auth_session.revoked_at IS NULL`. This is a server-side session check on every request — chosen over expiry-only revocation because the deployment is a single Postgres-backed API where one indexed lookup is cheap, and it gives immediate revocation (compromised account, offboarding) without a denylist cache. Maximum stolen-token usability: until revocation, at most 8h. No refresh tokens in v1 — re-login after expiry (bureau working pattern makes this acceptable; refresh flow is additive later without schema change).

### 1.4 `auth_event` (T6 — auth events are audited)

Append-only table under the full Stage 06 integrity properties (trigger-protected, see `event-audit-foundation-design.md` §5):

| Column | Type |
|---|---|
| `auth_event_id` | UUID PK |
| `event_type` | VARCHAR(30): `LOGIN_SUCCESS`, `LOGIN_FAILURE`, `TOKEN_ISSUED`, `WORKSPACE_SWITCH`, `STEP_UP_SUCCESS`, `STEP_UP_FAILURE`, `SESSION_REVOKED`, `MEMBERSHIP_GRANTED`, `MEMBERSHIP_REVOKED` |
| `operator_id` | UUID NULL (NULL only for `LOGIN_FAILURE` on unknown email — record the attempted email in `detail_jsonb`) |
| `session_id` | UUID NULL FK |
| `detail_jsonb` | JSONB (IP/user-agent optional; never passwords) |
| `created_at` | TIMESTAMPTZ NOT NULL DEFAULT now() (DB clock — threat-model §5 forward hook) |

### 1.5 `step_up_event` (T5 — first-class, referenceable; consumer arrives with C12)

| Column | Type |
|---|---|
| `step_up_event_id` | UUID PK |
| `operator_id` | UUID FK NOT NULL |
| `session_id` | UUID FK NOT NULL |
| `method` | VARCHAR(10): `PASSWORD` (floor), `TOTP` (slot for MFA — DEC-07-03) |
| `created_at` | TIMESTAMPTZ NOT NULL DEFAULT now() |
| `consumed_by` | VARCHAR(100) NULL — reference to the single approval that consumed it (set atomically at approval commit; a non-NULL value makes the event unusable for any further approval — one-approval-per-event by compare-and-set) |

**Freshness window: 5 minutes** (Stage 08 parameter per handoff item 7 — "minutes, not hours"; 5 minutes comfortably covers reading an approval screen after re-authenticating while keeping the hijacked-idle-session exposure negligible at C12's few-events-per-year frequency). The approval commit rejects a step-up event older than 5 minutes or already consumed.

### 1.6 `platform_metadata` (cut-over epoch as data — handoff item 6)

Simple key-value table: `key VARCHAR(100) PK`, `value_jsonb JSONB`, `updated_at`. Row `auth_cutover_epoch = {"at": "<deploy timestamp>"}` written once at C1 cut-over deployment, platform-wide. Every consumer rendering/exporting audit history compares `audit_log.performed_at` (and equivalents) against this value and labels pre-epoch actors `identity_unverified` mechanically (threat-model §6 hardenings 1–2). The table is generic on purpose — it also later holds the PII sanitizer version history pointer if needed.

## 2. Token design (T1/T2)

- **Mechanism:** HS256-signed JWT; signing key from environment/secret store, never in repo; key rotation = new key + accept-old-during-overlap list, no schema change (T1).
- **Claims (T2):** `sub` (operator_id), `ptype` (`HUMAN`/`SERVICE`), `wid` (exactly one active workspace_id — P6 generalised per DEC-07-02), `sid` (session_id — the unique auth-context identifier R4 records reference), `iat`, `exp`.
- Tokens travel in the `Authorization: Bearer` header only — never URL/query (identity-arch §7). `allow_credentials` stays false; CORS `ALLOWED_ORIGINS` pinning is a C1 deployment-checklist item with deployed-config inspection as closure evidence (F-07-03).
- Workspace switch = new session: revoke old `auth_session` row, issue new token with the new `wid` after a membership check, both recorded as `auth_event`s.

## 3. The shared dependency and the unauthenticated allowlist (T4, R2)

One dependency chain in `backend/api/deps.py` (new module):

1. **`get_current_principal`** — extracts Bearer token, verifies signature/expiry/session-not-revoked, loads the operator row, returns a `Principal(operator_id, principal_type, role, workspace_id, session_id)` value object. Failure → 401. Applied at the **router level** (`APIRouter(dependencies=[...])`) so a newly added route is protected by default — per-route opt-*out* only via the explicit allowlist, never opt-in.
2. **`get_workspace_principal`** — for every route with a `{workspace_id}` path parameter: depends on `get_current_principal`, compares path `workspace_id` to the token's `wid`; **mismatch → 404** (R2 — no existence disclosure). Returns the principal; handlers and services receive `workspace_id` only from this object. Path parameters remain for REST shape; request body/header/query workspace values are never read (the frontend's stored selection becomes navigation state only).
3. **Unauthenticated allowlist (explicit, minimal, reviewed):** `POST /auth/login`, `GET /health`. Nothing else — including the legacy admin HTML routes, which either gain auth or are removed with `workspace_info()` (see `remediation-designs.md` §4).

The five decorative routes (F-05-03 + F-07-01) get real enforcement automatically from step 2, **and** their data paths gain query-level workspace filters per the two-layer standard — the route fix does not substitute for the repo fix (`remediation-designs.md` §1–2).

## 4. R1 rewiring plan (caller-supplied actor inputs removed)

All confirmed at `573be0d` (identical to the `ea1590a` evidence, F-08-03):

| Site | Today | After C1 |
|---|---|---|
| `payroll.py:1180` retry | `X-Performed-By` header, default `admin@internal` | header parameter deleted; `performed_by = principal.identity` |
| `payroll.py:1207` approve | same | same |
| `payroll.py:1227` lock | same | same |
| `payroll.py:1257` pay | body `actor_id`, default `system@internal` | body field deleted; principal |
| `payroll.py:1359-1365` resolve reconciliation | free-text body `resolved_by` (required) | field deleted as actor; `resolved_by = principal.identity`. If an "on behalf of" note is wanted operationally it is a new, separate `resolution_note` annotation — never the actor field |
| `payroll.py:992` (`_calculate_and_persist`) | literal `performed_by="system"` | principal threaded from the calling route |
| `payroll.py:1009` | literal `"admin@internal"` | same |
| `payroll_retry_service.py:510` | hardcoded default | `performed_by` becomes a required parameter with no default |

**Audit builders reject missing actors**: the generalised builder (`event-audit-foundation-design.md` §3) takes a required `performed_by: VerifiedActor` value object constructed only from a `Principal` — there is no string-typed escape hatch and no default. A missing actor is a `TypeError` at the call site, not a row attributed to a placeholder.

The actor identity persisted in audit records is the **operator UUID** (stable across email changes), with `performed_by` display resolution via join. Pre-epoch rows keep their legacy strings and are labelled per §1.6.

## 5. Login and step-up routes

- `POST /auth/login` — email + password → argon2 verify (`HUMAN` rows only) → create `auth_session` + `auth_event(LOGIN_SUCCESS/TOKEN_ISSUED)` → JWT. Requires a `workspace_id` selection from the operator's memberships (single-membership operators auto-select). Login failures recorded; uniform error message regardless of which check failed.
- `POST /auth/step-up` — authenticated route; re-verifies the password (TOTP when enrolled), writes `step_up_event` + `auth_event(STEP_UP_SUCCESS)`, returns `step_up_event_id` for the approval UI to attach to the C12 approval call. Rate-limited.
- `POST /auth/switch-workspace`, `POST /auth/logout` — session lifecycle per §2.

## 6. Requirements satisfaction and verification

| Requirement | Satisfied by | Verification (Stage 10 detail in `stage-10-handoff.md`) |
|---|---|---|
| T1/T2/T3 | §2, §1.3 | Token tampering/expiry/revocation unit tests |
| T4 / CG-1 / SG-1 | §3 router-level dependency + allowlist | **Route-enumeration test**: iterate `app.routes`, assert every route carries the auth dependency or is in the literal allowlist constant — generated from the route table, not a sample (tenant-isolation-verification-standard §3.2) |
| T5 | §1.5 | Step-up freshness + single-consumption tests |
| T6 | §1.4 + append-only triggers | Auth-event write asserted per auth flow test |
| T7 | Argon2id, no plaintext, no password logging | Code review + grep gate |
| R1 | §4 | Grep-clean check (`X-Performed-By`, `actor_id`, actor defaults) + per-mutating-route test asserting the audit record carries the authenticated principal |
| R2 | §3 step 2 | Per-route negative-path standard (§3.3 of the verification standard): cross-workspace request → 404 |
| DEC-07-02 | §1.2 | Membership fixture test: one operator, two workspaces, both accessible via separate sessions; non-member workspace → 404 |
| Epoch (item 6) | §1.6 | Pre-epoch fixture renders `identity_unverified`; post-epoch row carries verified principal |
| F-07-03 CORS | §2 + deployment checklist | Deployed-config inspection recorded at C1 launch |

## 7. Build-order note (consumed from Stage 05, not re-derived)

C1 is the first build item; everything in `event-audit-foundation-design.md` §3's actor model depends on the `Principal` object existing. The R1 rewiring and the decorative-route enforcement land in the same build as the dependency layer — shipping the dependency without deleting the caller-supplied actor inputs would leave two parallel actor paths (the exact drift risk R1 forbids).
