# Stage 10 — Execution-Trace Remediation Design

**Status:** complete
**Opened:** 2026-07-12
**Closed:** 2026-07-12
**Evidence:** `docs/audit-program/10-execution-trace-remediation-design/evidence/01-current-state-schema.txt`

This is a **design stage**. No code, migration, test, or data was changed. All schema/behaviour facts below are read directly from the current codebase and local `payroll_dev` schema (evidence file). Where this document proposes new fields, tables, or behaviour, it is explicitly marked **PROPOSED**, distinct from **CURRENT**.

---

## 1. Current-state trace architecture map

| Layer | Mechanism | Scope | Gaps |
|---|---|---|---|
| Orchestration trace | `ExecutionTracer.step()` → `execution_trace` table | Original run only; 9 call sites across `payroll_run_service.py`, `payroll_run_persister.py`, `run_executor.py` | No `workspace_id`, no `employee_id`, no stable event code, no correlation/invocation ID, no `operation_type` (original vs retry) column. Free-text `step_name` only. |
| Calculation/component trace | `payroll_result.component_trace_jsonb`, built per-employee inside `sequential_executor.py` | Per-employee, per-component | Unaffected by this stage's gaps — remains the correct authoritative fine-grained record. Excludes components filtered out before execution (08-003). |
| Lifecycle audit/event history | `audit_log` (workspace_id, entity_type, entity_id, action, old/new value JSONB, performed_by/at); `event_store` (aggregate_type/id, event_type, payload, workspace_id) | Written by `payroll_run_persister.py` for original runs (`Save N audit entries` / `Save N events` steps) | Not written by retry at all (confirmed absent this stage — retry has no equivalent persister call); not written by approve/lock/pay transitions in the same structured way (Stage 08's `08-002`/`07-002` findings apply here). |
| Per-result identity | none | n/a | `statutory_rule_id`/`statutory_version` are computed at run level (`executor.py:138`, `run_executor.py:134`) and folded into `payroll_run.rules_context_snapshot`, but never copied onto the per-employee `payroll_result` row. This is `04-002`, unchanged. |
| Timeline API/route | `GET /{workspace_id}/payroll/runs/{run_id}/timeline` → `get_trace_steps(run_id)` | Returns all `execution_trace` rows for a run, flat, ordered by `created_at` | `workspace_id` accepted but discarded before reaching the query (`09-005`, unchanged root cause). |
| Frontend timeline view | `PayrollTimeline.tsx`, `ExecutionTraceStep` type | Renders the flat step list returned by the API | No grouping by attempt/invocation possible today because no correlation ID exists in the data to group by. |

Retry's tracer gap, precisely: `payroll_retry_service.py:526` instantiates a real `ExecutionTracer(payroll_run_id)`, but no call site anywhere in that ~300-line module invokes `.step(...)` or `.warn_persist(...)` on it. The instantiation itself is dead code with respect to persistence — it produces console output (Rich formatting) but writes zero rows. This confirms `02-002`/`07-005` exactly as carried forward; no new fact beyond precisely pinpointing the dead instantiation.

---

## 2. Retry event model — PROPOSED

Per the binding `07-005` decision (minimal subset, not full parity, not zero), three event groups:

**Group A — Invocation/preflight (one row unless noted):**
1. `RETRY_INVOCATION_STARTED` — written first, before any validation. Carries `requested_employee_count` (from the caller-visible `FAILED`-status result set at invocation time) in structured metadata.
2. `RETRY_PREFLIGHT_RUN_STATUS_CHECK` — records whether the run was `PARTIAL` (pass) or not (fail, terminal).
3. `RETRY_PREFLIGHT_SNAPSHOT_VALIDATION` — records whether `rules_context_snapshot` completeness validation (the `04-001`/`05-001` remediation's `validate_snapshot_complete()` check) passed or failed, and which specific key was missing on failure.
4. `RETRY_PREFLIGHT_PASSED` or `RETRY_PREFLIGHT_FAILED` — terminal preflight outcome. On failure, no further events in Group B/C are written; the invocation ends here.

**Group B — Per-employee outcome (one terminal row per retried employee):**
5. `RETRY_EMPLOYEE_SUCCEEDED` — carries `employee_id`, previous `status` (`FAILED`), new `status` (`SUCCESS`).
6. `RETRY_EMPLOYEE_FAILED` — carries `employee_id`, the safe (non-`str(e)`) failure reason, consistent with `CLAUDE.md`'s standing `str(e)` prohibition and `07-001`'s findings — this design must not reintroduce that defect class in a new surface.

**Group C — Final outcome (one row):**
7. `RETRY_TOTALS_RECOMPUTED` — informational, run totals after replacement.
8. `RUN_STATUS_TRANSITIONED` — `PARTIAL → CALCULATED` or `PARTIAL → PARTIAL`, reusing the same event code original runs would use for status transitions (taxonomy consistency, §4).
9. `RETRY_COMPLETED` or `RETRY_FAILED` — terminal invocation-level outcome. `RETRY_FAILED` covers total-recomputation or final-transition failures that occur after individual employee outcomes are already durably recorded (so a late failure does not erase the per-employee evidence already written).

This is 4 + 1-per-employee + 3 rows per retry invocation — matches the "minimal subset" instruction; it does not reproduce every original-run persistence sub-step (e.g. no separate "save payroll run header" / "save results" / "save audit entries" / "save events" steps for retry, since retry's per-employee and totals events already cover that ground at retry's own granularity).

---

## 3. Execution-trace schema and field contract — PROPOSED migration

**CURRENT** `execution_trace` cannot support this design without a migration: it has no `workspace_id` (blocks `09-005`'s fix), no `employee_id` (blocks per-employee retry events), no stable `event_code` (blocks §4's taxonomy), no `operation_type` (blocks distinguishing original vs. retry rows), no correlation/invocation ID (blocks §5's grouping), and no `actor_id` (blocks Stage 09's authentication/audit requirement once auth exists).

**PROPOSED** new/changed columns on `execution_trace`:

| Column | Type | Nullable | Purpose |
|---|---|---|---|
| `workspace_id` | `UUID` | NOT NULL (backfilled from `payroll_run.workspace_id`, see §14) | Required for `09-005`'s tenant-safe query; must be a real queryable column, not JSON, per this stage's own finding rule. |
| `event_code` | `VARCHAR(64)` | NOT NULL | Stable machine-readable code, see §4. Replaces reliance on free-text `step_name` for semantics; `step_name`/`message` retained as the human-readable label. |
| `operation_type` | `VARCHAR(20)` | NOT NULL, default `'ORIGINAL_RUN'` for existing rows | `ORIGINAL_RUN` \| `RETRY`. Enables §9's grouping. |
| `invocation_id` | `UUID` | NULL (NULL for original-run rows unless §5 extends correlation to original runs too — not required by current scope) | One value per retry API call; groups Group A/B/C rows from §2 together. |
| `employee_id` | `UUID` | NULL | Set for per-employee events (Group B); NULL for run-level events. |
| `actor_id` | `VARCHAR(200)` | NULL (until Stage 09's auth work lands; becomes the authenticated user identity thereafter) | Carries `performed_by`/`X-Performed-By` today; will carry the real authenticated principal once Stage 09's remediation ships. |
| `metadata_jsonb` | `JSONB` | NULL | Structured, non-identity-critical detail (e.g. missing snapshot key name, requested employee count). Per this stage's finding rule, identity/tenant/correlation fields are never hidden only in here. |
| `error_class` | `VARCHAR(200)` | NULL | Python exception class name only (e.g. `ValueError`), never a raw message. |
| (existing) `error_message` | `TEXT` | NULL | Retained, but must carry only a sanitized, developer-authored message — never `str(e)` from an uncontrolled exception, consistent with `07-001`. |

Existing columns `id`, `run_id`, `step_name`, `status`, `duration_ms`, `created_at` are retained unchanged. `status` gains no new values beyond existing `success`/`error`/`warn` — retry's preflight/per-employee/final outcomes map onto this existing vocabulary (`RETRY_EMPLOYEE_FAILED` → `status='error'`, etc.) rather than inventing a parallel status field.

New indexes: `(workspace_id, run_id)` composite (tenant-safe primary access path), `(invocation_id)` (attempt grouping), `(run_id, employee_id)` (per-employee filtering).

---

## 4. Stable event taxonomy — PROPOSED

Format: `<SUBJECT>_<ACTION>[_<QUALIFIER>]`, upper snake case, stored verbatim in `event_code`.

**Original-run codes** (retrofitted onto existing `.step()` call sites, mapped 1:1, no behaviour change — only classification):
- `RUN_STATUS_TRANSITIONED` (covers both `DRAFT→CALCULATING` and `CALCULATING→{status}` steps in `run_executor.py`, distinguished by `metadata_jsonb.from_status`/`to_status`)
- `RUN_BATCH_PROCESSING_STARTED` / `RUN_BATCH_PROCESSING_COMPLETED`
- `RUN_ENGINE_EXECUTION_COMPLETED`
- `RUN_RESULTS_PERSISTED`
- `RUN_HEADER_PERSISTED`
- `RUN_AUDIT_ENTRIES_PERSISTED`
- `RUN_EVENTS_PERSISTED`
- `LEGACY_EXECUTOR_FALLBACK` (existing `warn_persist` call, unchanged code — already a de facto stable string used by `get_legacy_executor_stats()`'s `WHERE step_name = 'legacy_executor_fallback'` query; renaming it would break that query, so this one code is grandfathered as-is rather than renamed, and `get_legacy_executor_stats()` is updated to filter on `event_code` once the migration lands — see §14)

**Retry codes** (§2): `RETRY_INVOCATION_STARTED`, `RETRY_PREFLIGHT_RUN_STATUS_CHECK`, `RETRY_PREFLIGHT_SNAPSHOT_VALIDATION`, `RETRY_PREFLIGHT_PASSED`, `RETRY_PREFLIGHT_FAILED`, `RETRY_EMPLOYEE_SUCCEEDED`, `RETRY_EMPLOYEE_FAILED`, `RETRY_TOTALS_RECOMPUTED`, `RETRY_COMPLETED`, `RETRY_FAILED`.

**Component-visibility code** (§8): `COMPONENT_EXCLUDED_BY_CONFIGURATION`.

**Versioning/extension rule:** `event_code` values are additive-only and treated as a public contract once shipped — a code is never renamed or repurposed to mean something different (mirrors `CLAUDE.md`'s "new status/enum values are introduced, never overloaded" rule, applied here to trace event codes). New codes may be added freely. Consumers (API filters, UI grouping) must treat an unrecognized `event_code` as a generic informational row rather than failing, so new codes can ship without breaking older frontend deployments (see §14 rollout ordering).

---

## 5. Retry correlation and idempotency — PROPOSED

- One `invocation_id` (`UUID`, generated server-side) is minted at the top of `retry_failed_payroll_employees` for every API call to `POST /payroll/run/{run_id}/retry` (or its future authenticated/scoped successor), regardless of outcome.
- All events in that invocation (§2 Groups A/B/C) carry the same `invocation_id`.
- Failed-preflight invocations ARE persisted (the `RETRY_PREFLIGHT_FAILED` row itself, with its own `invocation_id`) — this is the durable record that an operator attempted a retry that could not proceed, which is itself audit-relevant (e.g. repeated failed attempts against a run with a broken snapshot).
- Repeated retries on the same run each get their own `invocation_id` and remain fully append-only — no row is ever updated or deleted, consistent with `execution_trace` having no existing update/delete path today and no reason to introduce one.
- Ordering: `(invocation_id, created_at)` within an invocation is sufficient; no explicit sequence column is needed since Postgres `timestamp with time zone` at insert time, combined with the append-only single-threaded-per-run nature of retry (the run-state guards already prevent concurrent retries on the same run), gives stable ordering in practice. If sub-millisecond ordering ambiguity is ever observed in Stage 11 testing, a `sequence_no INTEGER` column scoped to `invocation_id` is the fallback — not added preemptively.
- Duplicate client requests (e.g. a double-click retry): not specially detected at the trace layer. This is a pre-existing application-level concern (idempotency of the retry service call itself, e.g. via `payroll_run.status` no longer being `PARTIAL` on the second call) that already causes the second call to fail preflight legitimately (`RETRY_PREFLIGHT_RUN_STATUS_CHECK` fails because the run already transitioned) — no new trace-layer mechanism is required to handle this correctly.

---

## 6. Error and failure trace semantics — PROPOSED

| Failure | Durable trace row required? | Event code |
|---|---|---|
| Invalid run status (not `PARTIAL`) | yes | `RETRY_PREFLIGHT_FAILED` (metadata: `reason=invalid_status`) |
| Incomplete snapshot | yes | `RETRY_PREFLIGHT_FAILED` (metadata: `reason=incomplete_snapshot`, `missing_key`) |
| Invalid statutory snapshot | yes | `RETRY_PREFLIGHT_FAILED` (metadata: `reason=invalid_statutory_snapshot`) |
| Employee no longer retryable (e.g. status changed concurrently) | yes | `RETRY_EMPLOYEE_FAILED` (metadata: `reason=not_retryable`) |
| Result replacement failure | yes | `RETRY_EMPLOYEE_FAILED` (metadata: `reason=persistence_error`, `error_class`) |
| Result persistence failure | yes | same as above |
| Total recomputation failure | yes | `RETRY_FAILED` (metadata: `reason=totals_recomputation_failed`) |
| Final transition failure | yes | `RETRY_FAILED` (metadata: `reason=status_transition_failed`) |

**Trace-write failure itself:** preserves the existing principle (`ExecutionTracer._persist()` already swallows all exceptions so a trace write never corrupts payroll calculation) — this design keeps that behaviour unchanged for the calculation-critical path, but closes the *silent* half of it: a trace-write failure must additionally emit a structured server-side log line (`logger.error("trace_write_failed", extra={"run_id":..., "event_code":..., "invocation_id":...})`) and increment a counter/metric if a metrics sink exists in the deployment (not assumed to exist — the log line is the minimum, mandatory signal; a metric is additive if infrastructure supports it). This does not change API response behaviour — the client-facing operation still succeeds or fails on its own merits, independent of trace persistence, exactly as today.

`error_message`/`error_class` fields must never carry `str(e)` from an uncontrolled exception — only a developer-authored, pre-classified reason string plus the exception's *class name* (safe) go into the trace row. This mirrors the fix direction implied by `07-001` and must not become a second place that leaks the same class of detail Stage 09 flagged in HTTP responses.

---

## 7. Per-result statutory identity (`04-002`) — PROPOSED implementation design

**Migration:**
```sql
ALTER TABLE payroll_result ADD COLUMN statutory_rule_id UUID NULL;
ALTER TABLE payroll_result ADD COLUMN statutory_version INTEGER NULL;
```
(Guarded per `CLAUDE.md`'s ADD COLUMN convention — `DO $$ BEGIN ... EXCEPTION WHEN duplicate_column THEN NULL; END $$` — and with a matching `downgrade()` dropping both columns.) No `NOT NULL`, no `FOREIGN KEY` to `statutory_rule` — a legacy result's statutory rule may no longer exist as a live row, and the value here is a historical fact, not a live-referential one (consistent with `CLAUDE.md`'s snapshot-immutability philosophy).

**Backfill policy:** none. Existing rows are left `NULL`. This is explicitly required by the CONTEXT.md's constraint ("Legacy rows must not be backfilled from mutable current statutory tables. Define them as unknown/unavailable unless frozen historical evidence proves identity.") — and it is achievable here: for runs that already have a complete `rules_context_snapshot["statutory_rule"]` (post-`04-001`-remediation runs), a one-time backfill *could* technically derive the value from that already-frozen snapshot without touching live tables. This is recorded as an **optional**, non-blocking follow-up for Stage 13 to decide, not part of this migration's mandatory scope — the mandatory scope is NULL-for-existing, populate-going-forward.

**Write call sites:**
- Original run: at the same point `executor.py`/`run_executor.py` already computes `statutory_rule_id`/`statutory_version` for `build_rules_context_snapshot(...)` (`executor.py:138`, `run_executor.py:134`), the identical values are also attached onto the per-employee result dict before persistence, so `payroll_run_persister.py`'s "Save N employee results" step writes both columns in the same `INSERT` that already writes `component_trace_jsonb` etc. — no new round-trip.
- Retry: sourced from `rules_context_snapshot["statutory_rule"]["id"]`/`["version"]` on the run's own frozen snapshot (the exact same snapshot the `04-001` remediation already made retry read exclusively) — `payroll_retry_service.py:181` already extracts `statutory_snap["id"]` for its own use; the same extraction is reused to populate the new columns on the replaced result row.

**Null semantics:** `NULL` means "identity unknown/unavailable" — either a legacy pre-migration result, or (theoretically) a non-statutory jurisdiction/configuration where no statutory rule applies at all. The API/UI must render `NULL` as an explicit "not recorded" state, never as "no statutory deduction was applied" (a different, calculation-level fact visible via `deductions_jsonb` instead).

**API exposure:** added as two new optional fields on the existing per-employee result response (`GET /{workspace_id}/payroll/runs/{run_id}/results`), additive, no breaking change to existing consumers.

**UI/audit display:** result detail view shows "Statutory rule: `<id short-form>` (v`<version>`)" or "Statutory rule: not recorded (pre-`{migration date}` run)" when NULL.

**Indexing:** a non-unique index on `statutory_rule_id` supports future "which results used rule X" queries (e.g. impact analysis when a statutory rule is found to be wrong after the fact) — a plausible, low-cost, forward-looking addition; not required by any currently-open finding, flagged here rather than silently added.

**Validation/consistency:** at write time, a lightweight assertion (not a DB constraint, since legacy/NULL rows are valid) that `statutory_rule_id`/`statutory_version` — when both are being written — match the run's own `rules_context_snapshot["statutory_rule"]` values exactly; a mismatch would indicate a bug in the calculation path itself and should raise loudly in application code (fail the write, not silently diverge) rather than at the DB layer.

**Immutability:** once written, these columns fall under the *existing* `prevent_payroll_result_mutation()` / `prevent_result_modification_if_paid()` triggers automatically (they already guard the whole row on `UPDATE`), so no new trigger is required — confirmed by reading the existing trigger definitions in Stage 08, which guard the row generically rather than per-column.

---

## 8. Disabled/excluded component visibility (`08-003`) — PROPOSED design

Five distinct states must be distinguishable (per the CONTEXT.md's own taxonomy):

1. **Excluded — disabled by workspace/client override** (`is_active=False` in `client_component_metadata`)
2. **Skipped — eligibility condition evaluated false** (component was active and considered, but its rule-evaluation condition did not fire this period)
3. **Absent — not part of applicable configuration** (component was never configured for this workspace/salary definition at all)
4. **Executed and returned zero**
5. **Executed and failed**

**Recommended smallest design:** extend the existing `component_trace_jsonb` structure — which already records "one entry per **executed** component" (per its own docstring in `sequential_executor.py`) — to also record entries for components that were configured but *not* executed, tagged with an `outcome` discriminator, rather than inventing a parallel table:

```json
{
  "results": { "...": "..." },
  "trace": [
    {"component": "NHF", "method": "employee_rate", "result": "5000.00", "outcome": "executed"},
    {"component": "PENSION_ADD", "method": "fixed_amount", "outcome": "skipped_eligibility"},
    {"component": "HEALTH_INS", "method": "employee_amount", "outcome": "excluded_by_configuration"}
  ]
}
```

States 1 and 3 above are distinguished by whether the component appears in the workspace's `client_component_metadata` at all (state 3, absent) vs. appears with `is_active=False` (state 1, excluded) — this distinction is already fully determinable from existing configuration tables and does not need to be duplicated into the trace; only state 1 (excluded-by-configuration, the specific compliance-relevant case `08-003` is about) needs a positive trace entry, since it is the one case where a component *should* plausibly have run but was actively turned off.

**Why not a dedicated table:** the CONTEXT.md explicitly asks for "the smallest design that creates an unambiguous, durable record without duplicating all component metadata" — `component_trace_jsonb` is already the per-employee, per-run authoritative record of what happened to each component, is already queried per-result, and already has the correct immutability/versioning story (`trg_snapshot_immutable`-adjacent triggers cover `calculations_snapshot_json`; the same protection level should extend to `component_trace_jsonb` if it does not already — flagged as a verification item for implementation, not re-derived here since it is outside this stage's read-only remit to re-audit trigger coverage already covered in Stage 08).

**Run-level signal (secondary, recommended):** in addition to the per-result trace, `execution_trace` gains one `COMPONENT_EXCLUDED_BY_CONFIGURATION` row **per distinct excluded component per run** (not per employee — this would be extremely noisy at scale) at calculation start, recording which component codes were configured-but-disabled for that run's workspace at that point in time. This gives an operator/auditor a single run-level answer to "was anything statutory turned off for this run" without having to scan every employee's `component_trace_jsonb`.

This design is policy-neutral per the constraint: it works identically whether Stage 13 ultimately re-enables the `D-ARCH-2` guard (making exclusion of statutory components impossible) or formalizes it as a controlled, audited action — the visibility mechanism is orthogonal to whether the action is permitted.

---

## 9. Original-run and retry trace relationship — PROPOSED

- `execution_trace` rows for a given `run_id` now span both `operation_type='ORIGINAL_RUN'` (existing rows, backfilled with this value at migration time — see §14) and `operation_type='RETRY'` (new rows, one `invocation_id` per retry attempt).
- **Operator view:** one unified timeline per run, default view groups rows first by `operation_type`/`invocation_id` (original run as one group, each retry attempt as its own subsequent group in chronological order), not interleaved by raw timestamp alone — chronological interleaving would be confusing since retry events for attempt 2 could otherwise appear to overlap attempt 1's cleanup in the UI.
- `component_trace_jsonb` on each `payroll_result` row remains attached to that specific result row's *current* state (retry replaces the row, per the existing `04-001`-remediated DELETE+INSERT pattern) — it is not itself versioned across attempts; the `execution_trace` timeline is what carries attempt history, while `component_trace_jsonb` always reflects "how the currently-persisted result was computed," consistent with existing behaviour and not changed by this design.
- `audit_log`/`event_store`: retry's `RETRY_COMPLETED`/`RUN_STATUS_TRANSITIONED` events are the natural point to also write the audit_log/event_store entries retry currently lacks entirely (a gap this stage newly confirms by absence, related to but distinct from `07-002`'s reconciliation-specific finding) — recommended as part of the same implementation work since it reuses the identical trigger point, though the `audit_log`/`event_store` gap itself is not a new open finding requiring separate tracking; it is folded into this design's Group C write.
- Timeline endpoint (§10, §11) returns retry rows by default, grouped — no separate endpoint is needed for retry history; a single `GET .../timeline` remains the one source of truth, now richer.

---

## 10. Tenant isolation and authorization for trace access (`09-005`) — PROPOSED

This design is explicitly **blocked on Stage 09's authentication/RBAC work landing first** (see §14) — it specifies the target contract, not something implementable in isolation today.

**Target request chain:**
```
authenticated request (bearer/session, post-Stage-09)
→ resolve caller's bureau account + role
→ verify caller's account has membership/entitlement to {workspace_id}
→ SELECT ... FROM execution_trace et JOIN payroll_run pr
    ON et.run_id = pr.payroll_run_id
   WHERE et.run_id = :run_id AND et.workspace_id = :workspace_id
     AND pr.workspace_id = :workspace_id   -- redundant-but-defensive double check
→ 404 if the run+workspace pair doesn't match (see resource-concealment policy below)
```

- `get_trace_steps(run_id, workspace_id)` — signature gains a mandatory `workspace_id` parameter; the route is required to pass it, closing exactly the gap `09-005` identified (path parameter reaching the query, not merely appearing in the URL).
- Repository query scopes by **both** `run_id` and the new `execution_trace.workspace_id` column (§3) — not by joining through `payroll_run` alone, so a future bug that breaks the join cannot silently widen scope; the tenant predicate lives directly on the table being queried, per `CLAUDE.md`'s "workspace scoping enforced at the query level" rule.
- Direct child IDs (e.g. a specific `invocation_id` or `employee_id` filter, §11) never bypass the parent `run_id`+`workspace_id` check — all filters are applied as additional `AND` predicates on top of the mandatory tenant predicate, never as an alternative lookup path.
- Role access: read-only auditor/viewer, payroll operator, and payroll approver may all view traces for workspaces they have membership in (§ Stage 09 role model); platform administrator access is explicit (a distinct, logged code path, not merely "admin can always query everything" silently).
- **Resource-concealment policy (chosen):** `404 Not Found` for both "run does not exist" and "run exists but caller is not authorized for its workspace" — never `403` for the authorized-but-wrong-workspace case, so an unauthorized caller cannot distinguish "wrong workspace" from "run doesn't exist" and cannot use response codes to enumerate valid run IDs across tenants. `401` is reserved strictly for "no valid authenticated identity at all." This mirrors the general best-practice IDOR-response pattern and is the more conservative of the two options CONTEXT.md offered.
- Future direct-client users (deferred per Stage 09, but design must not preclude them): the same membership-check layer generalizes without modification — a client-scoped user simply has membership limited to exactly one workspace, and the identical query/predicate chain applies unchanged.

---

## 11. API contract design — PROPOSED (additive)

`GET /{workspace_id}/payroll/runs/{run_id}/timeline` (existing route, path unchanged):

**New optional query parameters** (all additive, backward compatible — omitting all of them reproduces today's full-run behaviour, just now correctly tenant-scoped):
- `invocation_id` — filter to one retry attempt (or the original run, using a reserved sentinel or `operation_type=ORIGINAL_RUN` filter instead — see below)
- `operation_type` — `ORIGINAL_RUN` | `RETRY`
- `employee_id` — filter to one employee's retry outcomes
- `event_code` — filter to a specific event type
- `status` — existing `success`/`error`/`warn` vocabulary, unchanged
- `since`/`until` — time range
- `cursor`/`limit` — pagination; default ordering `(created_at ASC, id ASC)` for a stable, deterministic tie-break (an equal-timestamp collision, which is possible per §5, is resolved by the arbitrary-but-stable `id` value rather than being ambiguous)

**Response shape** (additive fields on the existing per-row object; no field removed or renamed):
```json
{
  "invocation_id": "uuid|null",
  "operation_type": "ORIGINAL_RUN|RETRY",
  "event_code": "RETRY_EMPLOYEE_SUCCEEDED",
  "employee_id": "uuid|null",
  "step_name": "...",
  "status": "success|error|warn",
  "duration_ms": 120,
  "error_class": "string|null",
  "error_message": "sanitized string|null",
  "metadata": {"...": "..."},
  "created_at": "iso8601"
}
```
Existing frontend consumers reading only `step_name`/`status`/`duration_ms`/`error_message`/`created_at` continue to work unmodified against the new response shape (pure superset).

**Retry-invocation summary** — new lightweight derived endpoint, `GET /{workspace_id}/payroll/runs/{run_id}/retry-invocations`, returning one row per `invocation_id` with counts (`employees_succeeded`, `employees_failed`, final `status`) — a convenience aggregation over the same underlying data, not a new source of truth, to avoid the frontend having to compute per-invocation summaries client-side from the flat event list.

**Per-result statutory identity** and **excluded-component display**: exposed as additive fields on the existing results endpoint (`GET /{workspace_id}/payroll/runs/{run_id}/results`) and within the existing `component_trace_jsonb` shape (§7, §8) — no new endpoint required for either.

No raw exception, stack trace, SQL, or schema/constraint detail is ever included in any of the above — `error_class` is restricted to the Python exception class name; `error_message` is restricted to pre-classified, developer-authored strings, per §6.

---

## 12. Minimal UI/operator experience design — PROPOSED (requirements only, not implemented)

- Timeline groups visually by original run (collapsed by default if long) followed by each retry attempt as its own labeled sub-section ("Retry attempt — 2026-07-12 14:03, by admin@internal").
- Preflight failure renders as a distinct, prominent banner within its attempt's group (not buried among success rows).
- Per-employee retry outcomes render as a compact success/fail list within the attempt group, cross-linking to the employee's result detail view.
- Final retry transition summary is the closing row of each attempt group ("2 succeeded, 0 failed → run is now CALCULATED").
- Statutory rule ID/version renders in the existing per-employee result audit detail view, alongside `component_trace_jsonb`; NULL renders as "not recorded (legacy run)" per §7.
- Excluded/disabled components render as a distinct visual state (e.g. greyed row with an "excluded by configuration" tag) within the existing component-trace display, distinguishable from an executed-and-zero row.
- Role-based visibility: the timeline view itself doesn't need new UI chrome for roles beyond what Stage 09's broader RBAC UI work will already need to add platform-wide (login state, role badge) — this stage does not scope a trace-specific role UI, since the access control is enforced server-side (§10) and the UI need only handle a `404`/`401` gracefully, which is a general API-error-handling concern, not trace-specific.
- Clear empty state for legacy runs: "No structured retry trace available for runs created before `<date>`" rather than a blank list, whenever a run predates this design's migration.

This is a requirements list for a future UI story, not a redesign — no component library changes, no new page, only new sections within the existing `PayrollTimeline.tsx`/result-detail views.

---

## 13. Audit/event ownership boundary — PROPOSED (clarified, not restructured)

| Store | Owns | Does not own |
|---|---|---|
| `execution_trace` | Orchestration and attempt outcomes: did a step/attempt start, pass, fail, and how long did it take. Machine-oriented, high-volume, append-only. | Calculation values, business-meaning "what changed and why" for a human reader. |
| `component_trace_jsonb` | Calculation decisions and component-level values/outcomes per employee per run, including the new excluded/skipped states (§8). | Run-level orchestration, retry attempt grouping. |
| `audit_log` | Human/business lifecycle actions and before/after state (e.g. component override changed, run approved) — `entity_type`/`entity_id`/`action`/old-new value pairs. | High-frequency technical step timing; that belongs in `execution_trace`. |
| `event_store` | Domain events/integration history (`aggregate_type`/`event_type`/payload) — the append-only domain-event backbone already used by original runs. | Duplicate of `audit_log`'s human-readable before/after framing; the two remain distinct by design, unchanged from current architecture. |
| `payroll_result` identity columns (`statutory_rule_id`/`statutory_version`, §7) | Durable, queryable, per-result calculation identity. | Full snapshot content (that stays in `rules_context_snapshot`/`calculations_snapshot_json`) — the new columns are pointers/facts, not a duplicate of the snapshot. |

No new duplicate writes are introduced by this design beyond the necessary Group C `audit_log`/`event_store` entries for retry noted in §9 (currently entirely absent for retry, not a duplication of anything that already exists).

---

## 14. Migration and rollout design — PROPOSED sequence

This remediation is **not production-safe on its own** — see the explicit dependency statement below.

1. **Schema migration** (single migration, following `CLAUDE.md`'s guard/downgrade conventions):
   - `execution_trace`: add `workspace_id UUID`, `event_code VARCHAR(64)`, `operation_type VARCHAR(20) DEFAULT 'ORIGINAL_RUN'`, `invocation_id UUID NULL`, `employee_id UUID NULL`, `actor_id VARCHAR(200) NULL`, `metadata_jsonb JSONB NULL`, `error_class VARCHAR(200) NULL`; backfill `workspace_id` for existing rows via `UPDATE execution_trace et SET workspace_id = pr.workspace_id FROM payroll_run pr WHERE pr.payroll_run_id = et.run_id` (a one-time, bounded, non-destructive backfill of a nullable-then-required column — done in two steps: add nullable, backfill, then `ALTER COLUMN ... SET NOT NULL` guarded by a pre-check per `CLAUDE.md`'s migration conventions); backfill `event_code` for existing rows from a `step_name → event_code` lookup table covering the 9 known original-run step names, with an `'UNKNOWN_LEGACY_STEP'` fallback for anything unmatched (should be none, but must not fail the migration on an unexpected value); new indexes per §3.
   - `payroll_result`: add `statutory_rule_id UUID NULL`, `statutory_version INTEGER NULL` (§7), no backfill.
   - Both changes are additive-only; no destructive step, no data loss, straightforward downgrade (drop the added columns/indexes).
2. **Application writes before reads:** ship the write-side changes (retry event emission, per-result identity population, excluded-component trace entries) in the same deploy as the migration, before any UI change ships that depends on reading the new fields — otherwise the UI would show empty/incorrect grouping for a period. No dual-write period is needed since this is purely additive (old readers ignore new columns; no old writer needs to keep writing an old shape that a new reader depends on).
3. **API changes:** additive only (§11) — safe to ship ahead of or alongside the UI; existing frontend deployments continue to function unmodified against the enriched response.
4. **Frontend deployment order:** ship after the API/write-side changes are live and have accumulated at least one real retry invocation's worth of data in whichever environment is used for verification, so the new UI grouping can be checked against real rows rather than only against the empty/legacy state.
5. **Hard dependency on Stage 09:** `09-005`'s fix (§10 of this design) **cannot ship** until Stage 09's authentication, account/workspace membership, and RBAC infrastructure exists — this design's `workspace_id` predicate on `execution_trace` is necessary-but-not-sufficient; without an authenticated caller identity to check membership against, adding the predicate only closes the "decorative scoping" defect (`09-004`/`09-005`'s literal bug) while leaving `09-000`/`09-001`/`09-002`'s "no identity at all" gap fully open for this route, same as every other route. This design's schema/query changes are safe and valuable to ship regardless (they are strictly additive and improve the worst-case exposure even pre-auth, since the query becomes *capable* of enforcing tenancy the moment auth exists, rather than needing a second migration later) — but the route must not be represented as "fixed" or "secure" until Stage 09's dependency is actually satisfied. This is stated explicitly per the CONTEXT.md's own requirement.
6. **Rollback:** standard migration downgrade (drop added columns); application code rollback reverts to the current behaviour (silent retry tracing gap, decorative `workspace_id`) — no data is destroyed by rolling back, since all new columns are nullable/additive and no existing column's meaning changes.
7. **Data retention:** not addressed by this design beyond noting that `execution_trace` volume increases (roughly 4 + 1-per-retried-employee + 3 rows per retry invocation, on top of existing original-run volume) — a retention/archival policy for `execution_trace` is out of this stage's scope and not currently defined anywhere in the codebase; flagged as a Stage 13 backlog item if row growth becomes an operational concern, not a blocker for initial implementation.

---

## 15. Acceptance criteria — PROPOSED (testable, for future implementation)

1. A retry invocation writes exactly one `RETRY_INVOCATION_STARTED` row and, on success, exactly one `RETRY_PREFLIGHT_PASSED` row, both sharing the same `invocation_id`.
2. A retry invocation with an incomplete snapshot writes a durable `RETRY_PREFLIGHT_FAILED` row with `metadata.reason='incomplete_snapshot'` and performs zero employee-level mutation.
3. Each retried employee has exactly one terminal `RETRY_EMPLOYEE_SUCCEEDED` or `RETRY_EMPLOYEE_FAILED` row per invocation.
4. Every successful retry invocation writes exactly one `RUN_STATUS_TRANSITIONED` row reflecting the actual resulting status.
5. `component_trace_jsonb` continues to be produced correctly for retried employees, unchanged by this design (regression check against existing behaviour).
6. Every `payroll_result` row written by an original run or retry after this migration ships has non-NULL `statutory_rule_id`/`statutory_version` matching `rules_context_snapshot["statutory_rule"]`.
7. Legacy `payroll_result` rows (written before this migration) retain NULL `statutory_rule_id`/`statutory_version` — no backfill occurs automatically.
8. A run with a disabled statutory component produces at least one `COMPONENT_EXCLUDED_BY_CONFIGURATION` row (run level) and a corresponding `"outcome": "excluded_by_configuration"` entry in each affected employee's `component_trace_jsonb`.
9. `GET .../timeline` for `workspace_id=A`, `run_id` belonging to workspace `B`, returns `404` (post-Stage-09-auth) and, pre-Stage-09-auth, is explicitly documented as **not yet secure** (the schema/query readiness does not itself constitute the fix).
10. Timeline output for a run with 1 original execution + 2 retries is stably ordered and correctly attributable to the right `operation_type`/`invocation_id` for every row.
11. Simulated `execution_trace` write failure (e.g. forced DB error in the trace-write path) does not affect the retry's own success/failure outcome or corrupt `payroll_result`, and does produce a server-side log line.
12. No API response from the timeline or results endpoints contains a raw `str(e)`, SQL fragment, or stack trace under any tested failure condition.

---

## 16. Stage 11 regression scenario specification — PROPOSED

1. Successful retry, one employee: verify events 1/2/3/4(pass)/5/7/8/9(complete) per §2, `invocation_id` consistent.
2. Retry with multiple employees, mixed success/failure: verify one terminal event per employee, correct counts in the retry-invocation summary (§11).
3. Preflight failure — legacy/incomplete snapshot: verify `RETRY_PREFLIGHT_FAILED` with correct `reason`, zero employee-level events, run status unchanged.
4. Statutory snapshot validation failure: same shape as #3, distinct `reason` value.
5. Repeated retry attempts on the same run: verify each attempt gets a distinct `invocation_id`, prior attempts' rows are untouched (append-only), timeline groups them as separate attempts.
6. Original-run vs. retry timeline grouping: a run with one original execution and one retry renders as two distinct, correctly-labeled groups.
7. Statutory identity parity between original and retry results: an employee retried under the *same* statutory rule as their peers has an identical `statutory_rule_id`/`statutory_version` to those peers' original-run results.
8. Disabled statutory component recorded as excluded: workspace with `is_active=False` on a statutory component produces the run-level and per-result excluded-state evidence (§8), for a run created *before* and *after* the migration (verifying the pre-migration case correctly shows "not recorded" rather than fabricating history).
9. Cross-workspace timeline request denied: post-Stage-09-auth, a caller authenticated for workspace A requesting workspace B's `run_id` receives `404`, not the data.
10. Read-only auditor allowed to view an authorized trace: post-Stage-09-auth, confirms the role matrix (§10) is additive, not accidentally restrictive.
11. Unauthorized direct-client user denied: exercises the "future direct-client user" extensibility claim in §10 without requiring that feature to exist yet — can be scoped as a design-level scenario for Stage 13 rather than an executable test until direct-client users actually exist.
12. Trace-write failure containment: forced trace-write failure during a real (non-production) retry does not alter the retry's own success/failure outcome, and produces the expected server-side log line.

---

## 17. Risks, trade-offs, and alternatives considered

- **Alternative rejected — full original-run trace parity for retry.** Rejected by the binding `07-005` decision; would roughly double `execution_trace` volume for every retry and was explicitly judged unnecessary given `component_trace_jsonb` already carries the fine-grained calculation record.
- **Alternative rejected — separate `retry_trace` table instead of extending `execution_trace`.** A dedicated table would avoid the `operation_type`/nullable-`employee_id` mixed-shape row design, but would fragment the single-timeline requirement (§9's "operator should see one timeline") into a UNION query at read time for no real benefit — the CONTEXT.md's own instruction to "avoid reproducing every original-run persistence sub-step" argues for *fewer* moving parts, not more tables. Rejected in favor of one table with a discriminator column, a pattern the codebase already uses elsewhere (e.g. `payroll_run.run_type`).
- **Alternative rejected — dedicated `excluded_components` table for `08-003`.** Rejected in favor of extending `component_trace_jsonb` (§8) — the CONTEXT.md explicitly asks for the smallest design; a new table would need its own workspace/run/employee FK scoping, immutability triggers, and API surface for marginal benefit over an additive field on an already-existing, already-correctly-scoped structure.
- **Trade-off accepted — `execution_trace.workspace_id` denormalizes data already derivable via `JOIN payroll_run`.** Accepted deliberately per this stage's own finding rule ("do not store critical tenant... identity only inside unindexed free-form JSON") and per the direct lesson of `09-004`/`09-005` — a join-based tenant check is exactly the pattern that failed silently in this codebase already (the "path declares it, handler doesn't use it" bug class named in Stage 09); a denormalized, directly-queryable, indexed column on the table itself is judged safer against exactly this recurring failure mode, at the acceptable cost of a backfill and keeping the value in sync (which is trivial — `workspace_id` never changes for an existing run).
- **Risk — `event_code` taxonomy churn.** If future stages need materially different event semantics, the additive-only versioning rule (§4) could accumulate near-duplicate codes over time. Mitigated by the explicit "never rename or repurpose" rule plus documentation of the taxonomy as a first-class, reviewed artifact (this findings.md itself) rather than an implicit convention scattered across call sites.
- **Risk — retry trace volume growth without a retention policy** (§14 point 7). Accepted as out of scope for this design; flagged, not silently ignored.

---

## Handoff notes for Stages 11, 12, 13

- **Stage 11** (scenario testing): execute the 12 regression scenarios in §16 against a real, non-production implementation once built — this stage produces the specification only, no test was executed as part of Stage 10 itself (design-only constraint).
- **Stage 12** (code simplification): the retrofit of existing `.step()` call sites onto the new `event_code` taxonomy (§4) is a natural simplification-pass candidate — mapping 9 free-text strings to stable codes in one place rather than scattered literals.
- **Stage 13** (consolidated backlog): this design is not implementable end-to-end until Stage 09's authentication/RBAC work lands (§14 point 5) — the schema/write-side/API portions of this design (§3, §2, §7, §8, §11 minus the auth-dependent parts of §10) CAN ship independently and are recommended as an earlier, lower-risk increment; the tenant-safe query enforcement itself (§10's actual authorization check) must be sequenced after Stage 09's auth work, not before. Stage 13 should treat `04-002`, `08-003`, and `09-005`'s trace-specific remediation as one bounded package per this design, sequenced relative to (not blocked entirely behind) the broader Stage 09 authentication programme where the additive schema/write work is concerned. The optional legacy-backfill-from-frozen-snapshot idea (§7) and the `execution_trace` retention policy (§14 point 7) are both flagged as open, non-blocking backlog items for Stage 13 to prioritize or decline.

## Human decisions

None required to close Stage 10 as currently specified — every design choice above resolves against either a prior binding decision (`07-005`, Stage 09's auth/RBAC decisions) or this stage's own finding rules (smallest-additive-design preference, no backfill from mutable data, no network-controls-as-authorization). If review disagrees with a specific design choice (e.g. the resource-concealment policy in §10, or the "grandfather `legacy_executor_fallback`'s code" call in §4), that would surface as a targeted decision at close-review rather than a structurally open question left by this investigation.

---

## Stage 10 close — final review and closure summary

No new human decision was required to close Stage 10. The proposed design in §1–17 above is **approved as the canonical implementation specification** for the future remediation work — no section was revised at close review; all design choices held.

Review requirements verified at closure:

1. The retry event model (§2) implements the binding `07-005` minimal-subset decision exactly (invocation/preflight → one terminal outcome per retried employee → final transition) and does not expand to full original-run parity.
2. `execution_trace`'s proposed schema (§3) adds `workspace_id`, `event_code`, `operation_type`, `invocation_id`, `employee_id`, and `actor_id` as real queryable columns, not JSON-only fields — satisfying this stage's own "do not hide critical tenant/correlation identity only in JSON" rule.
3. Per-result statutory identity (§7) is sourced exclusively from the run's own frozen `rules_context_snapshot["statutory_rule"]`, for both original runs and retries — never from a live re-query of mutable `statutory_rule`/`tax_band` tables.
4. Existing `payroll_result` rows are explicitly left `NULL` with no automatic backfill from mutable live data — confirmed in §7's "Backfill policy: none" and restated in §14's migration sequence.
5. Excluded components (§8) are durably distinguishable from skipped-by-eligibility, absent, executed-zero, and executed-failed via the `outcome` discriminator on `component_trace_jsonb`, plus the run-level `COMPONENT_EXCLUDED_BY_CONFIGURATION` trace row.
6. The tenant-safe timeline design (§10) is explicitly stated as closing `09-005` **only once** Stage 09's authentication/membership/RBAC dependencies exist — §14 point 5 states this as a hard, non-negotiable dependency, not an assumption. The schema/write-side/API portions are correctly scoped as independently shippable ahead of that dependency.
7. Authorization semantics (§10) use `401` strictly for "no valid identity" and a non-disclosing `404` for both "run not found" and "run exists but caller lacks workspace authorization" — never `403` for the cross-tenant case, preventing response-code-based tenant enumeration.
8. Error semantics (§6, §11) prohibit uncontrolled `str(e)`/SQL/stack-trace/schema disclosure in both trace rows (`error_class` restricted to exception class name, `error_message` restricted to developer-authored text) and API responses — consistent with `07-001`'s standing prohibition and explicitly designed not to reintroduce that defect class on a new surface.
9. Migration/rollback (§14), API backward compatibility (§11), minimal UI requirements (§12), 12 acceptance criteria (§15), and 12 Stage 11 regression scenarios (§16) are all implementation-ready and specified in full.
10. Stage 10 remained design-only throughout — no `backend/`, `frontend/`, `migrations/`, `tests/`, or `scripts/` file was created, modified, or touched at any point in this stage; confirmed by `git status` showing only `docs/audit-program/` changes at every commit in this stage.

### Approved trace package — carried to Stage 13

The following bounded package is approved as a coherent unit for Stage 13's sequencing and eventual implementation:

- **`02-002`/`07-005`** — minimal retry event model and `execution_trace` schema extension (§2, §3, §4, §5, §6).
- **`04-002`** — per-result statutory identity (§7).
- **`08-003`** — excluded-component visibility (§8).
- **`09-005`** — tenant-safe timeline access (§10), **hard-blocked on Stage 09's authentication/RBAC remediation**; the schema/write-side/API portions of this same package may ship independently and earlier, per §14 and the Stage 13 handoff note already recorded above.

The Stage 09 S0 authentication/RBAC dependency (`09-000`/`09-001`/`09-002`) remains the controlling blocker for any claim that trace access is production-secure, regardless of how complete this stage's schema and query design is.
