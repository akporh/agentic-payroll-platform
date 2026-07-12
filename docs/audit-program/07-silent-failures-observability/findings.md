# Stage 07 — Findings

Status: **in-progress**. All entries below use the template in
[`../_core/finding-schema.md`](../_core/finding-schema.md). Status values
restricted to this stage's five-value set.

---

## Headline result

The single most significant new finding this stage is **07-001**: a
systemic, confirmed violation of `CLAUDE.md`'s own standing prohibition
("Never return `str(e)` in an HTTP response") — 21 occurrences across
`backend/api/routes/payroll.py` and `workspace.py`, each wrapping a broad
`except Exception` around a raw service/repository call and returning the
raw exception text verbatim to the client. `CLAUDE.md` already documents
this exact pattern recurring in Sprint 10 and Sprint 17; this stage
confirms it has recurred again, at greater scale than either prior
instance. This is an information-disclosure-flavoured silent-failure
variant: not silent to the client (they get *a* message), but the message
can leak internal schema details never intended for the client, and —
more relevant to this stage's remit — it means these 21 sites have no
consistent, sanitized, operator-authored error vocabulary at all; whatever
the underlying exception says is what the client sees.

---

## 1. Failure-surface catalogue (selective — full 16-domain sweep summarized, deep dives on the highest-value surfaces)

| Failure point | Catch location | Swallowed/transformed/re-raised | Persisted? | Audit/event? | Trace? | API | UI | Classification |
|---|---|---|---|---|---|---|---|---|
| Snapshot creation (05-001) | `payroll.py::_calculate_and_persist` | Transformed → `FAILED` status + `error_message` (post-remediation) | Yes (`payroll_run.status`, `error_message`) | Yes (`build_transition_audit`/`event`) | No (no `execution_trace` step for this) | Yes (`error_message` in `GET .../runs/{id}`) | **No** (Stage 06 06-001) | Persisted+API, not UI |
| Background calculation failure (outer catch) | `payroll.py::_calculate_and_persist`'s outer `try/except Exception: logger.error(...)` | Swallowed — logged only, no status change, no re-raise | No | No | No | No | No | **Confirmed silent** — see 07-003 |
| Per-employee calculation | `batch_processor.py:170-185` | Transformed → `FAILED` `payroll_result` row (isolated mode) | Yes (`payroll_result.status`, `error_message`) | No (no per-employee audit_log row) | No (console-only `tracer.warn`, per Stage 02's 02-004) | Yes (`GET .../results`) | Yes (results table) | Persisted+API+UI; audit/trace layers absent (documented, Stage 02) |
| Retry preflight (04-001 hard-fail) | `payroll_retry_service.py::_build_shared_context` | Re-raised as `ValueError` | No new row (rejects before writing) | No | No | Yes (surfaces via the route's `except ValueError` → HTTP error) | Depends on frontend (not verified this stage — Stage 06 confirmed a "Cannot retry this run" modal exists for the *legacy-snapshot* case specifically, `EMP-UX-3`) | Correctly observable for the case Stage 06 already confirmed; not re-verified for every rejection reason |
| Retry per-employee calculation | `payroll_retry_service.py:669-693` | Transformed → `FAILED` `payroll_result` row | Yes | No (no audit_log row per retried employee) | Zero `execution_trace` rows (Stage 02 02-002) | Yes | Partial (Stage 06 06-004 — blank for `FAILED` *run*; per-employee `FAILED` *result* rows within a `PARTIAL` run are correctly shown, per Stage 06's positive-control confirmation) | Mixed |
| Reconciliation create/resolve | `reconciliation_service.py` | Re-raised as `ValueError` on error; success path has no audit/event write at all | Yes (`payroll_reconciliation` table itself, including `resolve_reconciliation`'s `notes`/`resolved_by`) | **No** `audit_log`/`event_store` entry for either `reconcile_payroll_run` or `resolve_reconciliation` | N/A | Yes (`GET .../reconciliation`) | Yes (`Reconciliation.tsx`, Stage 06 confirmed wired) | Confirmed audit/event gap — see 07-002 |
| Route-level generic exceptions (21 sites) | `except Exception as e/exc: raise HTTPException(..., detail=str(e))` | Transformed, but with an unsanitized, unpredictable message | No (varies by route) | No | No | Yes, but message quality is uncontrolled | Depends on frontend's `extractError` (confirmed in Stage 06 to surface `detail` verbatim) | Confirmed — see 07-001 |
| `execution_trace` write failure | `execution_trace_repo.py::save_trace_step` | **Deliberately, documentedly swallowed** ("a trace write failure never interrupts the payroll run") | No | No | No (self-referential — trace-of-trace) | No | No | **Intentional, documented, not a defect** |
| `ExecutionTracer._persist` | `execution_tracer.py:74-93` | Same as above, same justification | No | No | No | No | No | **Intentional, documented, not a defect** |

---

### 07-001 — 21 API routes return raw exception text (`str(e)`/`str(exc)`) directly in the HTTP response, violating `CLAUDE.md`'s standing prohibition

- **stage:** 07-silent-failures-observability
- **location:** `backend/api/routes/payroll.py:342,846,1161,1183,1203,1227,1333` (7 occurrences); `backend/api/routes/workspace.py:93,180,663,768,1022,1452,1477,1502,1598,1775,1788,1829,1842,2027` (14 occurrences). Representative full-context citation: `workspace.py:2020-2027` — `except Exception as exc: raise HTTPException(status_code=400, detail=str(exc))` wrapping a raw call to `_att_cfg_repo.upsert_attendance_policy(...)`, a repository function that can raise a raw `IntegrityError`/`DataError` from psycopg2/SQLAlchemy.
- **current implementation:** Confirmed by direct grep and spot-verification of surrounding code: 21 call sites across the two largest route files catch a broad `Exception` (in several cases wrapping a raw DB write, not a controlled `ValueError`) and return the exception's string representation verbatim as the HTTP `detail` field.
- **intended behaviour:** `CLAUDE.md`'s API Route Rules section states this explicitly and unconditionally: *"Never return `str(e)` in an HTTP response. All `except Exception as e` blocks in route files must log the raw exception server-side (`_log.error(...)`) and return a generic human-readable string to the client... This has appeared in new routes in Sprint 10 and Sprint 17 — it is a standing prohibition."*
- **suspected or confirmed defect:** Confirmed as a recurrence of an already-named, already-fixed-twice defect class, now at its largest observed scale (21 sites vs. whatever smaller number Sprint 10/17 fixed). Some of these 21 sites wrap a deliberately-raised, developer-authored `ValueError` with a safe message (e.g. `"Payroll run not found."`) — for those, `str(e)` happens to be harmless today, but the pattern itself provides no structural guarantee: the same `except Exception` will just as readily catch a raw `IntegrityError` whose message contains a table/column/constraint name, and several of the 21 (confirmed via the `workspace.py:2020-2027` citation) wrap calls that can plausibly raise exactly that. This stage did not individually classify all 21 as safe-vs-unsafe (that granularity is better suited to the remediation sprint that eventually fixes them); it confirms the pattern is systemic and the underlying risk is live, not hypothetical.
- **evidence:** `evidence/2026-07-12-str-e-leak-systemic.txt`
- **status:** confirmed
- **severity:** S1 (per `_core/severity-model.md`'s own S1 definition, which names "`str(e)` leaking to a client" as a defining example of this severity tier)
- **related invariant:** `CLAUDE.md` API Route Rules — "Never return `str(e)` in an HTTP response"

---

### 07-002 — Reconciliation create and resolve actions write no `audit_log`/`event_store` entry

- **stage:** 07-silent-failures-observability
- **location:** `backend/application/reconciliation_service.py` (entire file — confirmed via grep, zero imports of or calls to `save_audit_log`/`save_event`); contrast with `backend/application/payroll_approval_service.py:97-98,170-171,245-246` (approve/lock/pay — each writes both an audit-log and an event-store entry via the shared `build_transition_audit`/`build_transition_event` pattern)
- **current implementation:** `reconcile_payroll_run()` (creates a `MATCHED`/`MISMATCH` record) and `resolve_reconciliation()` (operator closes a `MISMATCH`) both persist directly to the `payroll_reconciliation` table (including `resolve_reconciliation`'s `notes` and `resolved_by` fields, which do capture *who* and *why* on that table itself) but neither calls the shared audit/event-writing functions every other significant lifecycle transition in this codebase uses.
- **intended behaviour:** Not documented as intentional. Every other business-state transition this stage checked (`DRAFT→CALCULATING`, `DRAFT→FAILED`, `CALCULATING→CALCULATED/PARTIAL`, `PARTIAL→CALCULATED` on retry, approve, lock, pay) writes to both `audit_log` and `event_store` via the same shared builder functions — reconciliation is the one exception found.
- **suspected or confirmed defect:** Confirmed as an inconsistency, not a complete absence of any record — the "who/why" for a reconciliation resolution is captured locally on the `payroll_reconciliation` row itself (`notes`, `resolved_by`), so this is not the same class of gap as a fully silent failure. It is a discoverability/consistency gap: an operator or auditor reviewing a workspace's unified `audit_log`/`event_store` history (e.g. via the `Audit` tab Stage 06 confirmed is wired) would see every other state change except reconciliation ones, which live only in a separate table not surfaced through that same view.
- **evidence:** Direct code citation above; `grep -c "save_audit_log\|save_event" backend/application/reconciliation_service.py` returns 0
- **status:** confirmed
- **severity:** S2 (a real observability/consistency gap touching a `CLAUDE.md`-documented invariant table, `payroll_reconciliation.status`, but the underlying data is captured somewhere, just not in the unified audit view — not a data-loss risk)
- **related invariant:** `CLAUDE.md` — `payroll_reconciliation.status = 'RESOLVED'` ("operator closed a MISMATCH — totals may differ")

---

### 07-003 — Background calculation failures outside the snapshot-creation step are logged only, with no persisted signal, no status change, and no audit/event record

- **stage:** 07-silent-failures-observability
- **location:** `backend/api/routes/payroll.py:971-972` (`_calculate_and_persist`'s outer `try/except Exception: logger.error("Background payroll calculation failed for run %s", payroll_run_id, exc_info=True)`)
- **current implementation:** The 05-001 remediation added fail-visible handling specifically for the snapshot-creation step (inner `try/except`, now `return`s with a `FAILED` status). The *outer* `try/except` wrapping the entire background task — which would catch any exception from `execute_and_persist(...)` or `link_inputs_to_run(...)` that isn't already contained by their own internal error handling — still only logs and does nothing else. A run whose background task fails at this outer level (e.g. an unexpected exception during persistence, not a per-employee calculation failure, which is already isolated and turned into a `FAILED` `payroll_result` row) would be left in whatever status it last reached (likely still `DRAFT` or `CALCULATING`, since the exception interrupted the normal flow before a final status write), with the true cause visible only in server logs.
- **intended behaviour:** Not documented as intentional — the 05-001 remediation's scope was explicitly narrow (snapshot creation only), so this outer catch was correctly left untouched by that remediation, per its own stated constraints. Whether it should receive the same `FAILED`-status treatment is an open question this stage surfaces but does not resolve.
- **suspected or confirmed defect:** Confirmed as a silent-failure mechanism by direct code citation — logging without any persisted signal is exactly the pattern `05-001` fixed for the narrower snapshot-creation case, still present one level up. Not yet observed to have fired in practice (no evidence of frequency), so its practical risk is unestablished, but the mechanism itself is a live gap.
- **evidence:** Direct code citation; `backend/api/routes/payroll.py:971-972`
- **status:** confirmed
- **severity:** S2 (same class of gap `05-001` addressed, narrower in scope, S2 rather than S2-escalated since it's a lower-probability path — most failures at this point in the flow are already caught by the more specific inner handlers)
- **related invariant:** none directly; structurally adjacent to `05-001`

---

### 07-004 — Stray module-level `print()` statement executes on every import of the PAYE calculation module

- **stage:** 07-silent-failures-observability
- **location:** `backend/domain/rules/paye.py:11` (`print("Loaded PAYE from:", __file__)`, at module scope, outside any function)
- **current implementation:** This line executes once per Python process the first time `backend.domain.rules.paye` is imported — i.e., on every server startup and in every test process that imports it (confirmed indirectly: this exact debug line appeared in this audit's own earlier session output, from `scripts/run_first_payroll_emp001.py`'s explicit debug import at Stage 02).
- **intended behaviour:** Reads as a leftover debug statement, not a deliberate logging mechanism (it uses `print`, not the `logging` module used everywhere else in the codebase, and its message format matches ad-hoc debugging, not structured operational logging).
- **suspected or confirmed defect:** Confirmed present; not a functional defect (does not affect calculation correctness or silence any real failure) but is exactly the category of finding the sprint's log-quality audit explicitly asks for ("`print()` statements in production paths").
- **evidence:** Direct code citation
- **status:** confirmed
- **severity:** S3
- **related invariant:** none

---

## 2. `04-002` statutory-identity observability recommendation

**Not re-derived — Stage 05 already produced this exact recommendation
in full** (`docs/audit-program/05-snapshot-integrity/findings.md` §10,
"Statutory identity observability recommendation (04-002)"). Restated
here per this stage's explicit requirement, unchanged:

> Add `payroll_result.statutory_rule_id` (UUID, nullable) and
> `payroll_result.statutory_version` (integer, nullable), populated at
> every insert (both original run and retry) from the same value used for
> that calculation. This directly closes `04-002`: any `payroll_result`
> row becomes independently auditable without forensic recomputation.
> Alternatives assessed and rejected as primary mechanisms: inclusion in
> `calculations_snapshot_json` (conflates a financial-summary field with
> an audit-identity field), `component_trace_jsonb` (useful as a
> *secondary* confirmation — it already has a natural home in the
> `_period_context` header entry — but is `None` on the legacy executor
> path and is a JSONB blob, not a queryable column), `execution_trace`
> (blocked on `02-002`'s zero-rows-on-retry gap, and not naturally scoped
> to a specific employee's result).

This stage adds one confirmation: independently re-checked that no
`payroll_result` schema change has occurred since Stage 05 (the `04-001`/
`05-001` remediation's migration, `b8c9d0e1f2a3`, touched only
`payroll_run`, not `payroll_result`) — the recommendation remains exactly
as valid and unimplemented as when Stage 05 wrote it. **Handoff to Stage
10, unchanged.**

---

## 3. `02-002` retry execution-trace parity assessment

- **Which original-run steps are absent on retry:** all of them. Stage 02
  confirmed `retry_failed_payroll_employees()` instantiates an
  `ExecutionTracer` but never calls `.step(...)` anywhere in its ~300-line
  body (re-confirmed by this stage — `grep -n "tracer\.step" backend/application/payroll_retry_service.py`
  returns zero matches, unchanged since Stage 02 and unaffected by the
  `04-001`/`05-001` remediation). An original run produces ~7-9 step rows
  (`Execute payroll engine`, `Transition: DRAFT→CALCULATING`, `Batch
  process: N employees`, `Transition: CALCULATING→X`, `Persist results`,
  `Save payroll run header`, `Save N employee results`, `Save N audit
  entries`, `Save N events`). Retry produces none of these.
- **Whether audit/event store compensates:** partially. Retry does write
  one `audit_log`/`event_store` pair for the run-level `PARTIAL→CALCULATED`
  (or `→PARTIAL`) transition (confirmed, `payroll_retry_service.py:794-804`,
  unchanged since Stage 04). It does **not** compensate for the missing
  per-employee-retry step detail (which components ran, in what order,
  with what period resolution) — that information exists only in
  `component_trace_jsonb` per retried employee (confirmed present and
  correct, since retry calls the same `run_sequential_payroll()` as the
  original run) — so the *calculation* detail is preserved, but the
  *orchestration* detail (which steps executed, in what order, how long
  each took) is not.
- **Whether a failed retry can be reconstructed from current persisted
  data:** partially. A retried employee's final calculation (or failure
  reason, via `payroll_result.error_message`) is fully persisted and
  queryable. What is *not* reconstructable: the exact sequence of
  preflight checks the retry performed before reaching that calculation
  (e.g. whether `validate_snapshot_complete()` passed, whether the new
  `04-001` statutory-snapshot validation passed) — these are pass/fail
  gates with no persisted trace of having run, only inferable from the
  fact that a result exists at all (if the retry had failed a gate, the
  `ValueError` would propagate to the API response but leave no persisted
  row, per `04-001`'s confirmed hard-fail behaviour).
- **Whether parity is required for every step or only a defined subset:**
  **not documented anywhere** — this stage found no source stating retry's
  intended trace-completeness level. Recorded as a human decision, per the
  sprint's own anticipation that this might be needed.
- **Minimum useful retry trace, recommended:** at minimum, one persisted
  `execution_trace` row per retry invocation recording whether the `04-001`
  statutory-snapshot validation passed, and one row per retried employee
  recording success/failure — mirroring the original run's granularity
  without requiring full step-by-step parity. This is a recommendation, not
  an implementation; left for Stage 10.

### 07-005 — `02-002`'s intended trace-parity level for retry is undocumented — human decision required

- **stage:** 07-silent-failures-observability
- **location:** No location — an absence-of-documentation finding, confirmed by searching `CLAUDE.md` and all prior audit-stage findings for any stated intent on this question
- **current implementation:** N/A
- **intended behaviour:** Not documented anywhere in this codebase or its accumulated audit findings.
- **suspected or confirmed defect:** Not a defect — a genuine open product/architecture question this stage cannot resolve from evidence alone, exactly as the sprint prompt anticipated ("This may require a human decision if the intended trace parity level is not documented").
- **evidence:** Absence confirmed by search; see §3 above for the full parity assessment
- **status:** human decision required
- **severity:** S3
- **related invariant:** none

---

## 4. `06-001`/`06-004` complete signal path for a `FAILED` run

```
background snapshot-creation failure (payroll.py::_calculate_and_persist)
  → mark_payroll_run_failed()                              [payroll_run.status='FAILED', error_message set]  ✓ persisted
  → build_transition_audit/event(DRAFT→FAILED)              [audit_log, event_store rows written]            ✓ audited
  → GET /{workspace_id}/payroll/runs/{run_id}                [returns status:'FAILED', error_message: '...']  ✓ API-exposed
  → frontend PayrollRunStatus type                          [type has no 'FAILED' member]                    ✗ STOPS HERE (06-001)
  → StatusBadge (PAYROLL_COLORS lookup)                      [no FAILED key, falls back to generic gray]       ✗ (06-001)
  → ActionPanel (run.status if-chain)                        [no FAILED branch, returns null]                 ✗ (06-004)
  → operator recovery guidance                               [none rendered — panel is blank]                 ✗ (consequence of 06-004)
```

**Observability stops precisely at the frontend type boundary.** Every
layer up to and including the API response is confirmed correct and
complete (backend remediation `05-001`, fully verified). Nothing about
this signal path implicates `04-001` or `05-001`'s correctness — both
remain sound; this stage's contribution is confirming the exact point of
failure is a frontend consumption gap, not a backend one, consistent with
Stage 06's original framing.

---

## 5. Persisted error-state inventory (summary)

| Field/table | Writer | Reader | Immutable? | API? | UI? | Captures cause or symptom? |
|---|---|---|---|---|---|---|
| `payroll_run.status` | Multiple (route, retry service, `mark_payroll_run_failed`) | Multiple | No (mutable by design — it's a state field) | Yes | Yes (except `FAILED`, 06-001) | Symptom (the state itself) |
| `payroll_run.error_message` | `mark_payroll_run_failed` only (05-001) | `GET .../runs/{id}` | Not explicitly protected (no trigger) — but only one writer exists today | Yes | **No** (06-001) | Cause |
| `payroll_result.status`/`error_message` | `payroll_result_repo.py`, retry service | Multiple | `calculations_snapshot_json` is DB-immutable (Stage 05); `status`/`error_message` are not separately protected but follow the DELETE+INSERT convention (never UPDATEd) | Yes | Yes | Both (status=symptom, error_message=cause) |
| `execution_trace` | `ExecutionTracer` (original run only, per Stage 02's 02-002) | `GET .../timeline` | No trigger; write-only, append-style in practice | Yes | Yes (Timeline tab, confirmed wired Stage 06) | Symptom (step-level, coarse) |
| `component_trace_jsonb` | `run_sequential_payroll()`, both original and retry | `GET .../results` | Yes (part of DB-immutable `payroll_result` row group by convention, not a separate trigger) | Yes | Yes | Cause (fine-grained, per-component) |
| `audit_log` | Multiple, via `save_audit_log` | `GET .../audit` | No trigger found; write-only in practice | Yes | Yes (confirmed wired Stage 06) | Symptom (old/new state) |
| `event_store` | Multiple, via `save_event` | Not directly exposed via a dedicated GET route found in this stage's search | No trigger found | Not confirmed exposed | Not confirmed exposed | Symptom |
| `payroll_reconciliation.notes`/`resolved_by` | `resolve_reconciliation` | `GET .../reconciliation` | Not checked for a trigger this stage | Yes | Yes | Cause (operator's own explanation) — but not in the unified audit view (07-002) |

---

## 6. Positive controls (confirmed correctly observable, recorded so this stage isn't read as all-gaps)

- **Approval/lock/pay transitions**: each writes both `audit_log` and
  `event_store` entries via the shared `build_transition_audit`/
  `build_transition_event` pattern — confirmed complete, consistent
  mechanism across all three.
- **Per-employee calculation failure within an original run**: correctly
  isolated (execution_mode="isolated"), correctly persisted
  (`payroll_result.status='FAILED'`, `error_message` populated),
  correctly API-exposed and UI-rendered (confirmed Stage 06) — the
  *individual employee* failure path is fully observable end to end; only
  the coarser step-level trace (02-002) and per-employee audit-log entries
  are absent.
- **`04-001`'s legacy-snapshot retry rejection**: confirmed by Stage 06 to
  have a dedicated, well-labeled frontend modal (`EMP-UX-3`, "Cannot retry
  this run") — a genuine example of a hard-fail condition with good
  operator-facing recovery guidance ("open a correction run"), the kind of
  observability this stage is otherwise finding gaps in.
- **`component_trace_jsonb`**: confirmed to give a complete, accurate,
  fine-grained record of every component's calculation method and result
  for both original runs and retries (unaffected by `02-002`'s step-level
  gap, which is a separate, coarser mechanism).

---

## Handoff notes for later stages

- **Stage 08 (data integrity):** `07-002` (reconciliation audit gap) is
  directly relevant — Stage 08 should assess whether any live workspace's
  reconciliation history is currently unreconstructable outside the
  `payroll_reconciliation` table itself.
- **Stage 09 (security and tenant isolation):** `07-001` (systemic `str(e)`
  leak) is the primary handoff — this is an information-disclosure-flavoured
  finding this stage deliberately did not expand into a full security
  audit of; Stage 09 should determine which of the 21 sites can leak
  genuinely sensitive schema/data details versus which happen to be safe
  today, and prioritize accordingly.
- **Stage 10 (execution-trace remediation):** both `04-002` (§2) and
  `02-002` (§3, plus new finding `07-005`) are direct inputs, both already
  bounded with concrete recommendations; `07-005`'s open question (intended
  retry-trace parity level) should be resolved before Stage 10 finalizes
  its design.
- **Stage 11 (scenario testing):** `07-003` (outer background-task
  exception handler) is a good candidate for a forced-failure scenario
  test once addressed, alongside the already-planned `05-001`/`04-001`
  regression scenarios (Stage 05's handoff).
- **Stage 12 (code simplification):** `07-004` (stray `print()` in
  `paye.py`) is a trivial, safe removal candidate.
- **Stage 13 (consolidated backlog):** `07-001` is likely the highest-
  severity new finding in this stage (S1, matching the severity model's
  named example) and should be prioritized accordingly alongside `04-001`'s
  historical S0 in the final backlog ordering. `07-002` and `07-003` are
  both S2, real but lower-urgency. `07-005` requires Michael's input before
  Stage 10 can proceed with a bounded design.

## Human decisions required

- **07-005** — what is the intended `execution_trace` parity level for
  retry (full step-by-step, a defined minimal subset, or none beyond what
  already exists)? Blocks Stage 10's `02-002` remediation design.
