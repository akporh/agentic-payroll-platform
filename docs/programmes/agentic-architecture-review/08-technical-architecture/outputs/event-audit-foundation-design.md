# Stage 08 Output: Event & Audit Foundation Design (C2 + audit generalisation)

Answers Stage 08 Q2 within the binding requirements: Stage 06 audit-expansion requirements (four domains, four integrity properties, mechanism generalisation), the agent/tool audit standard (SC-3), Stage 07's audit-integrity threat model §4 (append-only floor, outbox covers audit records, no purge path pending DQ-008), and Stage 05's minimum-viable-closure list. Evidence pinned at `573be0d`.

## 1. The transactional write problem, grounded

Today every persistence repo opens its own `SessionLocal` and commits independently: `save_audit_log` (`audit_log_repo.py:35-75`), `save_event` (`event_store_repo.py:8-40`), `finalise_payroll_run` (`payroll_run_repo.py:94`), `save_payroll_results_bulk` (`payroll_result_repo.py:37`). `persist_payroll_run_execution` (`payroll_run_persister.py:70-110`) therefore runs **four or more separate transactions per run** — the state change, its audit records, and its events can each independently fail after the others committed (F-06-02's fire-and-forget failure generalises to the whole persister; recorded as F-08-02). Any design that keeps per-repo sessions cannot satisfy the "reliably written" property.

## 2. Mechanism: one transaction, outbox inside it

**Design: a unit-of-work persistence facade.** One SQLAlchemy session per state-changing operation; all rows — domain rows, `audit_log` rows, and `outbox` rows — are inserted through that session and committed **once**. Audit records are written *directly* in the state-change transaction (the strongest form of "outbox covers audit records": the record cannot be lost unless the state change itself rolls back). The outbox carries everything that needs *post-commit delivery* — event-store projection, notification fan-out, and any future email (C15).

### 2.1 `outbox` table

| Column | Type |
|---|---|
| `outbox_id` | UUID PK |
| `topic` | VARCHAR(50) — `EVENT` (project to `event_store`), `NOTIFICATION` (write `workspace_notification`) |
| `payload_jsonb` | JSONB — for `EVENT`: the full event-store payload; for `NOTIFICATION`: the notification row content |
| `workspace_id` | UUID NULL (platform-level events carry NULL) |
| `created_at` | TIMESTAMPTZ DEFAULT now() |
| `processed_at` | TIMESTAMPTZ NULL |
| `attempts` | INT DEFAULT 0 |
| `last_error` | TEXT NULL |

Inserted in the same transaction as the state change. At-least-once delivery; consumers are idempotent (event projection keys on `outbox_id` carried into `event_store.event_payload` so a redelivered row upserts, not duplicates).

### 2.2 The facade contract

```
persist(session, *, domain_writes, audit_records: list[AuditRecord], events: list[DomainEvent], notifications: list[Notification])
```

- `audit_records` → `audit_log` INSERTs in-transaction.
- `events`/`notifications` → `outbox` INSERTs in-transaction.
- One `commit()`. The existing `save_audit_log`/`save_event` free functions are retired; the persister (`payroll_run_persister.py`) is reworked onto the facade so the run header, results, audit rows, and outbox rows commit atomically. This closes F-06-02 and F-08-02 together.
- `event_store` becomes a **projection target only** — written by the consumer from outbox rows, never directly by request paths.

### 2.3 Consumer worker

- APScheduler polling loop (source document's own technology decision, kept), running as named service principal `svc:event-consumer` (R3).
- **Single-worker constraint enforced, not documented**: the poll cycle takes a Postgres advisory lock (`pg_try_advisory_lock` on a fixed key); a second uvicorn/scheduler instance skips the cycle. This converts the source document's "document and enforce before deploy" warning into a mechanical guarantee.
- Cycle: `SELECT ... WHERE processed_at IS NULL ORDER BY created_at LIMIT N FOR UPDATE SKIP LOCKED` → dispatch by `topic` → set `processed_at`. Failures increment `attempts`, record `last_error`, and leave the row unprocessed; rows exceeding a retry ceiling surface as an exception record (§6) rather than silently looping.

## 3. Audit-mechanism generalisation (Q2's signature-vs-parallel choice)

**Choice: signature generalisation — one builder, entity-typed.** Parallel builders per entity type would re-create today's problem (each new domain needs new plumbing and can silently diverge on field discipline). One builder enforces the actor rule in one place:

```
build_audit(*, entity_type: str, entity_id: str, action: str, old_value: dict|None, new_value: dict|None, performed_by: VerifiedActor) -> AuditRecord
build_event(*, aggregate_type: str, aggregate_id: str, event_type: str, payload: dict) -> DomainEvent
```

- `VerifiedActor` is constructible **only** from a `Principal` (auth dependency) or a named service principal constant — no bare-string constructor (R1; audit builders reject missing actors by type signature).
- `entity_type` values come from a registered enum (`PAYROLL_RUN`, `SALARY_DEFINITION`, `PAY_CYCLE`, `PAYROLL_RULE`, `EMPLOYEE_CONTRACT`, `COMPONENT_METADATA`, `RECONCILIATION`, `STATUTORY_CHANGE`, `EXCEPTION`, `TOOL_CALL`, `AUTH`, `PENDING_ACTION`, `DRY_RUN`) — unregistered types fail at build time, keeping the audit vocabulary enumerable for consumers.
- The existing `build_transition_audit`/`build_transition_event` (`audit_events.py:16-67`, hardcoded `"PAYROLL_RUN"` at lines 34/60) become thin wrappers during migration and are deleted once all 6+6 call sites move.

### 3.1 The four new events (Stage 05 closure list, unchanged)

`RECONCILIATION_MISMATCH`, `EMPLOYEE_ENROLLED`, `EMPLOYEE_STATUS_CHANGED`, `PAYROLL_INPUT_SUBMITTED` — each emitted via the facade in the same transaction as its state change. Each has a committed emission test (Stage 05 closure evidence).

### 3.2 Audit domain coverage (audit-expansion domains 1–4)

| Domain | Mechanism |
|---|---|
| 1 — Domain-config change | PATCH/POST routes for `salary_definition`, `pay_cycle`, `payroll_rule`, employee contract, component-metadata overrides call the facade with old/new values and the verified principal |
| 2 — Statutory approval | C12 writes its approval record + an `audit_log` row (`STATUTORY_CHANGE`) through the same facade (`statutory-change-mechanism-design.md` §5) |
| 3 — Exception lifecycle | Every `exception_record` transition (§6) writes an audit row; **immediately buildable case**: reconciliation resolution becomes a durable `RECONCILIATION`/`RESOLVED` audit record, not just row columns |
| 4 — Agent/tool | The tool-guard wrapper writes the SC-3 record per invocation (`tool-contracts.md` §2, P7) into `tool_call_log` (§7) via the facade |

## 4. `workspace_notification`

Per Track V7's shape, plus severity and typed entity reference:

`notification_id` UUID PK · `workspace_id` UUID NOT NULL · `operator_id` UUID NULL (NULL = all workspace operators) · `type` VARCHAR(50) · `severity` VARCHAR(10) (`INFO`/`WARNING`/`CRITICAL`) · `message` TEXT · `entity_type` VARCHAR(50) · `entity_id` UUID NULL · `exception_id` UUID NULL FK · `read_at` TIMESTAMPTZ NULL · `created_at` TIMESTAMPTZ.

In-app only (C15 deferred). Written by the consumer from `NOTIFICATION` outbox rows. Not audit-class: ordinary retention, `read_at` is mutable — notifications are pointers to records, never the record of anything.

## 5. Append-only enforcement (immutability choice)

**Choice: trigger-based enforcement (the floor), role separation deferred.** The deployment has a single DB role today and gains nothing else that would justify introducing role separation now; DEC-07-04 already records the accepted residual (app-credential `DISABLE TRIGGER`, DB superuser). Pattern precedent `3da637afb11b`.

- One shared trigger function `prevent_append_only_violation()` raising on UPDATE and DELETE, attached per protected table: `audit_log`, `event_store`, `auth_event`, `step_up_event` (UPDATE allowed **only** on `consumed_by` NULL→non-NULL — enforced in the trigger, preserving one-approval-per-event), `statutory_change_proposal` (status-machine columns only, via trigger comparing immutable columns), `statutory_change_approval`, `pending_action` (same immutable-columns pattern), `tool_call_log`, `dry_run_execution`.
- Corrections to wrong audit rows are new correction records referencing the wrong row (threat-model §4) — no edit path exists.
- **Retention (DQ-008 posture confirmed):** keep-at-least-7-years; **no deletion/archival/purge mechanism is designed anywhere in this stage's schemas** — no TTL columns, no archival jobs, no partition-drop plans. Nothing here pre-empts the legal determination (Q9 answered: verified by absence across all Stage 08 designs).
- Insertion timestamps everywhere use DB `now()`, never app-supplied; record shapes are flat rows that do not preclude later hash-chaining (threat-model §5 forward hooks).

## 6. Exception data model (D-04-01's workflow substrate)

`exception_record`:

| Column | Notes |
|---|---|
| `exception_id` UUID PK | |
| `workspace_id` UUID NOT NULL | |
| `source` VARCHAR(20) | `C6_READINESS`, `C7_ANOMALY`, `RECONCILIATION`, (future) `C8` — one shared workflow for all producers (Stage 04's binding "one workflow, not three") |
| `exception_type` VARCHAR(50) | e.g. `MISSING_TIMESHEET`, `ANOMALOUS_INPUT`, `RECON_MISMATCH` |
| `severity` VARCHAR(10) | producer-assigned; prioritisation signal (proximity to cutoff / magnitude) lives in `evidence_jsonb` for Stage 09 to render |
| `status` VARCHAR(15) | state machine below |
| `owner_operator_id` UUID NULL | exactly one owner once assigned |
| `entity_type` / `entity_id` | what the exception is about |
| `evidence_jsonb` JSONB | the triggering data, frozen at creation (the anomalous value + comparison basis; the missing-timesheet employee/period; the reconciliation delta) — an exception without evidence is an assertion (Stage 04) |
| `recommended_action` TEXT NULL | producer-supplied; may be LLM-narrated *from known facts* for C7, never for detection |
| `resolution_code` VARCHAR(30) NULL | `CONFIRMED_ERROR_CORRECTED`, `CONFIRMED_CORRECT_DISMISSED`, `ESCALATED`, `SUPERSEDED` — the codes C7's calibration metrics need (`anomaly-detection-design.md` §5) |
| `resolution_note` TEXT NULL | |
| `resolved_by` UUID NULL / `resolved_at` | verified principal |
| `verified_at` TIMESTAMPTZ NULL | re-check pass timestamp (state machine below) |
| `closed_at` / `created_at` | |

**State machine** (mapping Stage 04's eight outcome stages): `OPEN` →(assign)→ `ASSIGNED` →(resolve with code)→ `RESOLVED` →(automatic re-check where applicable — e.g. the anomalous value no longer flags, the timesheet now exists)→ `VERIFIED` → `CLOSED`. Dismissal (`CONFIRMED_CORRECT_DISMISSED`) short-circuits `RESOLVED → CLOSED` (nothing to verify). No DELETE; terminal records keep full history (append-only trigger on terminal states not required — history integrity comes from domain-3 audit rows on every transition). Creation, assignment, resolution, verification, closure each write an audit record (domain 3).

Prioritisation, queue UI, and severity rendering are Stage 09's (`stage-09-handoff.md`).

## 7. `tool_call_log` (SC-3 record store)

One row per tool invocation, written by the guard wrapper via the facade, append-only, 7-year-floor retention:

`tool_call_id` UUID PK · `session_ref` UUID (agent session / job identity) · `workspace_id` UUID NULL (NULL for platform-level tools) · `operator_id` UUID NOT NULL (verified principal or service principal) · `tool_name` VARCHAR(50) · `tool_version` VARCHAR(20) · `params_jsonb` (post-PII-policy) · `outcome` VARCHAR(10) (`SUCCESS`/`EMPTY`/`REFUSED`/`ERROR`) · `result_digest_jsonb` (digest + row identifiers/counts; full payload where not reconstructible) · `pii_ruleset_version` VARCHAR(20) · `created_at` TIMESTAMPTZ DEFAULT now().

`agent_session_log` (source document S-04 shape) is retained as the session-narrative table; `tool_call_log` rows link to it via `session_ref`. Splitting tool calls into their own table (vs the document's `tool_calls_jsonb` column) is the mechanism change that makes per-call append-only enforcement and outcome-class querying possible; retention is identical (7-year floor), so the Stage 06 uniform-chain requirement holds.

## 8. Requirements satisfaction and verification

| Requirement | Satisfied by | Verification |
|---|---|---|
| Reliably written (property 2, SG-2) | §2 single-transaction facade | **Forced-failure test**: audit/outbox insert made to fail → the state change rolls back too; no committed state change without its records |
| Attributable (property 1) | §3 `VerifiedActor` | Type-level + per-route audit-actor tests (`auth-foundation-design.md` §6) |
| Immutable (property 3, SS-3) | §5 triggers | UPDATE/DELETE rejection test per protected table |
| Retained (property 4) | §5 no-purge posture | Design-review absence check (no deletion mechanism exists to test) |
| Generalisation (audit-expansion §2) | §3 | Registered-entity-type test; a domain-1 config PATCH produces a correctly-typed audit row |
| Event completeness | §3.1 | Per-event emission tests (Stage 05 closure evidence) |
| Consumer single-worker | §2.3 advisory lock | Two-instance test: second poller skips |
| Exception workflow substrate | §6 | Create/own/resolve/verify/close end-to-end test (Stage 05 closure evidence) |
| SC-3 fields | §7 | Registry uniformity test asserts every wrapper invocation writes the row (P7) |
