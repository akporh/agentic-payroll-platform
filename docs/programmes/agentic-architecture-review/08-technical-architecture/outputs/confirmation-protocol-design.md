# Stage 08 Output: Confirmation Protocol Design (C10)

Answers Stage 08 Q4 / DQ-002 (expiry, conflict, idempotency, run-state invalidation — carried from F-02-13) within the security constraints of `07-security-identity/outputs/approval-security-design.md` §4 (payload freezing, expiry records, idempotent execution) and §2 (R4-grade records). C10 is deterministic platform infrastructure (D-03-01); no LLM participates in confirmation or execution.

## 1. `pending_action` schema

| Column | Type / notes |
|---|---|
| `pending_action_id` | UUID PK |
| `workspace_id` | UUID NOT NULL |
| `action_type` | VARCHAR(50) — registered enum of executable actions (each maps to exactly one deterministic service function; unregistered types cannot be proposed) |
| `target_entity_type` / `target_entity_id` | what the action mutates |
| `proposed_by_kind` | `AGENT` / `OPERATOR` |
| `proposed_by_ref` | agent session id (`session_ref`) or operator UUID — verified context, never self-asserted |
| `payload_jsonb` | **frozen as-presented**: the exact record id, field, old value, new value the confirmation UI will render — written once at proposal, immutable thereafter (append-only trigger on this column, `event-audit-foundation-design.md` §5) |
| `payload_hash` | SHA-256 of `payload_jsonb` — embedded in the confirmation record (R4 item 4) |
| `target_state_snapshot_jsonb` | the target's load-bearing state at proposal time (e.g. `{run_status: "CALCULATED", updated_at: ...}`) — the invalidation comparand (§4) |
| `status` | state machine (§2) |
| `expires_at` | TIMESTAMPTZ NOT NULL (proposal time + TTL) |
| `decided_by` | UUID NULL — verified principal of confirm/reject |
| `decided_at` | TIMESTAMPTZ NULL (DB clock) |
| `decision_session_id` | UUID NULL — auth-context reference (R4 item 2) |
| `outcome_detail_jsonb` | execution result linkage (rows written), or invalidation/expiry reason |
| `created_at` | TIMESTAMPTZ DEFAULT now() |

## 2. State machine

```
PROPOSED ──confirm──▶ EXECUTED
   │ ├──reject──────▶ REJECTED
   │ ├──expiry──────▶ EXPIRED
   │ └──state-change▶ INVALIDATED
```

- All transitions out of `PROPOSED` are **compare-and-set**: `UPDATE pending_action SET status = :new, ... WHERE pending_action_id = :id AND status = 'PROPOSED'` — zero rows updated means another transition won; the caller re-reads and reports the actual terminal state. This single guard is the concurrency backbone for §3–§5.
- Confirmation and execution are one transaction through the C2 persistence facade: the CAS transition, the target mutation, the domain audit record, and any outbox rows commit atomically. If execution fails, the transaction rolls back — the action stays `PROPOSED` (retryable) with the failure recorded as an `audit_log` `PENDING_ACTION`/`EXECUTION_FAILED` row written in its own transaction.
- Every terminal transition (including `EXPIRED` and `INVALIDATED`) writes an R4-grade audit record — silence is an audit gap (approval-security §4). Terminal rows are immutable.

## 3. DQ-002 answers

### 3.1 Expiry
- Default TTL **7 days**, set per `action_type` at registration (a proposal about a run mid-cycle should not outlive the cycle; 7 days is the ceiling, action types may declare shorter). Rationale: pending actions are workspace-blast-radius (approval-security §1) and sit behind an authenticated UI; the operational risk of a stale proposal is confirming against changed context, and §4's invalidation — not the clock — is the primary defence. The TTL is a backstop for proposals whose target never changes.
- The C2 consumer worker sweeps `PROPOSED` rows with `expires_at < now()` each cycle → CAS to `EXPIRED` + audit record. An expired action is never executable; re-proposing creates a new record referencing the expired one in `outcome_detail_jsonb`.

### 3.2 Conflicts (two proactive agents, same entity)
- **One live proposal per target and action type**: partial unique index `ON pending_action (workspace_id, target_entity_type, target_entity_id, action_type) WHERE status = 'PROPOSED'`.
- A second overlapping proposal is **rejected at creation** (the proposing agent receives a structured refusal naming the existing `pending_action_id`). Rejection-not-supersession is deliberate: silent supersession would let a later (possibly injected — T7) proposal replace content an operator may already be reviewing. An agent that genuinely needs to replace a proposal must first have it withdrawn — an explicit operator action, recorded.
- Proposals on the *same entity with different action types* may coexist; §4's re-validation at execution time resolves any semantic interference (the second executes against post-first state or invalidates).

### 3.3 Idempotency (a security property — approval-security §4)
- Double-submit of the same confirmation: the CAS guard makes the second submit a zero-row update; the API returns the recorded outcome (`EXECUTED`, with `decided_at`/`decided_by` of the first submit) — it never re-executes. HTTP semantics: 200 with the terminal record, not an error — retried requests (network replay) converge on one execution.
- The execution layer additionally derives its idempotency key from `pending_action_id` for any downstream write that needs one, so even a crash between CAS and commit cannot double-apply after rollback (the transaction boundary already prevents partial application; the key covers future non-transactional side effects, of which v1 has none).

### 3.4 Run-state invalidation (F-02-13's core case)
Two layers, both required:

1. **Eager (event-driven)**: the C2 consumer, on processing any state-change event, marks `PROPOSED` actions targeting that entity `INVALIDATED` (CAS) when the new state conflicts with `target_state_snapshot_jsonb` — e.g. any pending action targeting a `payroll_run` invalidates when the run transitions to `APPROVED`, `LOCKED`, or `PAID` (the run becomes immutable per the platform's own D-ARCH-1 lock; a proposal against it is definitionally stale). Invalidation writes the audit record with old/new state.
2. **Mandatory re-check at execution (the guarantee)**: inside the confirmation transaction, before mutating, the executor re-reads the target and compares against `target_state_snapshot_jsonb`. Mismatch → CAS to `INVALIDATED`, no mutation, operator sees "the underlying record changed since this was proposed" with both states. The eager layer is UX (the operator sees invalidation promptly); the execution-time check is the correctness boundary — the protocol is safe even if the consumer is down.

## 4. Confirmation surface (security constraints applied)

- Confirmation is an **authenticated UI action** (distinct endpoint, `POST /{workspace_id}/pending-actions/{id}/confirm`), never a chat reply (T7; source document's own rule kept). The UI renders exclusively from `payload_jsonb` — never from chat text or an agent's restatement (T6).
- Workspace-blast-radius: an ordinary verified session suffices (approval-security §1) — no step-up. The R4 record: verified principal, `decision_session_id`, DB-clock timestamp, `payload_hash` (of what was shown — frozen at proposal, so shown == stored by construction), outcome + row linkage.
- Reject requires no reason in v1 (recommended field offered); expiry/invalidation reasons are machine-generated.

## 5. Requirements satisfaction and verification

| Requirement | Satisfied by | Verification |
|---|---|---|
| Payload freezing (SG-10) | §1 `payload_jsonb` write-once + trigger | Mutation-attempt test rejected at DB layer |
| Idempotent execution (SG-10) | §3.3 CAS + transaction | Double-confirm test: one mutation, second returns recorded outcome |
| Expiry/invalidation records (SG-10) | §2 terminal audit records | Sweep test + event-invalidation test assert audit rows exist |
| Run-state invalidation (DQ-002) | §3.4 two layers | Test: propose → transition run to APPROVED → confirm attempt → `INVALIDATED`, no mutation |
| Conflict handling (DQ-002) | §3.2 partial unique index | Concurrent-proposal test: second insert refused |
| R4 record completeness | §4 | Field-presence assertions on every terminal record |
| No-LLM execution path | §1 registered `action_type` → deterministic function | Registry test: every action type maps to a service function; no free-form execution |

DQ-002 is resolved by this design (recorded in `decision-queue.md`).
