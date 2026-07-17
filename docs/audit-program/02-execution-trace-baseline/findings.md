# Stage 02 — Findings

Status: **in-progress**. All entries below use the template in
[`../_core/finding-schema.md`](../_core/finding-schema.md).

---

## Production execution-flow map (reference, not a finding)

```
API route (payroll.py, POST /payroll/run)
  └─ backend/application/payroll_run_service.py :: execute_and_persist()
       tracer = ExecutionTracer(payroll_run_id)          [persisted step rows begin]
       ├─ with tracer.step("Execute payroll engine"):
       │    └─ backend/domain/payroll/run_executor.py :: execute_payroll_run_pure()
       │         ├─ with tracer.step("Transition: DRAFT → CALCULATING")
       │         ├─ with tracer.step("Batch process: N employees (mode=...)")
       │         │    └─ backend/domain/payroll/batch_processor.py :: process_payroll_run()
       │         │         for each employee (tracer.info() only — NOT persisted):
       │         │           └─ backend/domain/payroll/executor.py :: execute_single_employee_payroll()
       │         │                if component_metadata:      → _run_sequential()  [PRODUCTION PATH]
       │         │                     └─ sequential_executor.py :: run_sequential_payroll()
       │         │                          → returns {"results", "trace"} — this "trace" becomes
       │         │                            component_trace_jsonb (per-employee, NOT in execution_trace table)
       │         │                else:                        → legacy fallback [DEPRECATED PATH]
       │         │                     tracer.warn_persist("legacy_executor_fallback", ...)  [1 persisted row]
       │         │                     └─ result_builder.py :: build_payroll_result()
       │         │                          ├─ salary.py :: calculate_gross()      [@trace_step, dead in prod path]
       │         │                          └─ calculator.py :: calculate_net_pay() [@trace_step, dead in prod path]
       │         │                          component_trace_jsonb = None
       │         └─ with tracer.step("Transition: CALCULATING → CALCULATED|PARTIAL")
       └─ with tracer.step("Persist results"):
            └─ backend/application/payroll_run_persister.py :: persist_payroll_run_execution()
                 ├─ with tracer.step("Save payroll run header")   → payroll_run_repo.finalise_payroll_run()
                 ├─ with tracer.step("Save N employee results")   → payroll_result_repo.save_payroll_results_bulk()
                 │      (component_trace_jsonb written here, per employee, as a payroll_result column)
                 ├─ with tracer.step("Save N audit entries")
                 └─ with tracer.step("Save N events")
```

Retry (`backend/application/payroll_retry_service.py :: retry_failed_payroll_employees()`)
instantiates its own `ExecutionTracer(payroll_run_id)` but never calls `tracer.step(...)`
anywhere in the function body (confirmed by grep — zero matches, see
`evidence/2026-07-11-trace-persistence-gap-retry.txt`). It calls
`execute_single_employee_payroll()` directly per failed employee, always with
`component_metadata` populated from the run's own snapshot tables (never `None`), so
retry always uses the sequential/production path and always produces
`component_trace_jsonb` — it just never produces any `execution_trace` step rows.

---

## Execution-trace lifecycle map (reference, not a finding)

Two independent trace mechanisms exist. They do not share a table, a schema, or a
population path.

| | `execution_trace` table (via `ExecutionTracer`) | `component_trace_jsonb` (via `run_sequential_payroll`) |
|---|---|---|
| **Scope** | Run-level orchestration steps (state transitions, batch processing, persistence phases) | Per-employee, per-component calculation trace |
| **Created by** | `backend/application/execution_tracer.py` (`ExecutionTracer.step()`, `.warn_persist()`) | `backend/domain/payroll/sequential_executor.py :: run_sequential_payroll()` |
| **Enriched by** | Nothing — each row is a terminal step/warn event | `apply_payroll_rules()` supplemental traces merged in via `_supplemental_traces`; hire-proration entries appended |
| **Persisted by** | `backend/infra/repositories/execution_trace_repo.py :: save_trace_step()` — one `INSERT` per `.step()` exit or `.warn_persist()` call | `backend/infra/repositories/payroll_result_repo.py` — written as a JSONB column on the `payroll_result` row itself, inside `save_payroll_results_bulk()` / `save_payroll_result()` |
| **Exposed by** | `GET /{workspace_id}/payroll/ops/legacy-executor-stats` (aggregate); `get_trace_steps(run_id)` at `payroll.py:1312` | `payroll.py:1069`, `payroll.py:1376` (read directly off `payroll_result.component_trace_jsonb`) |
| **Failure isolation** | Wrapped in `try/except: pass` inside `_persist()` — a DB failure here never interrupts the run | Not separately isolated — it is part of the same `payroll_result` row write as `net_pay`/`gross_components_jsonb`; a failure here fails the whole employee result |
| **Coverage in original run** | ~7–9 rows per run (transitions, batch step, persistence steps) plus 1 row per legacy-fallback employee if any | 1 row per employee (contains many trace entries internally) |
| **Coverage in per-employee retry** | **Zero rows** — `tracer.step()` is never called in the retry function body | 1 entry per retried employee (same mechanism as original run, since retry always passes `component_metadata`) |
| **Console-only, never persisted** | `tracer.info()` and `tracer.warn()` (not `.warn_persist()`) — used extensively inside `batch_processor.py` and `executor.py::_run_sequential` for per-employee detail (component breakdown, period resolution, rule application, hire proration) | N/A |

---

### 02-001 — `execution_trace` and `component_trace_jsonb` are two independent trace systems with no shared schema or population path

- **stage:** 02-execution-trace-baseline
- **location:** `backend/application/execution_tracer.py` (all); `backend/infra/repositories/execution_trace_repo.py` (all); `backend/domain/payroll/sequential_executor.py:696-786` (`run_sequential_payroll` trace construction); `backend/infra/repositories/payroll_result_repo.py:63,103,153,174` (`component_trace_jsonb` persistence)
- **current implementation:** `execution_trace` is a dedicated DB table populated exclusively by `ExecutionTracer.step()`/`.warn_persist()` via `save_trace_step()`, scoped to coarse run-orchestration steps. `component_trace_jsonb` is a JSONB column on the `payroll_result` table, populated entirely inside `run_sequential_payroll()` and written as part of the normal per-employee result insert — it has no relationship to the `execution_trace_repo` module and is never read or written by `ExecutionTracer`.
- **intended behaviour:** No document (`CLAUDE.md` or elsewhere) states these are meant to be one system or asserts they are separate. `CLAUDE.md`'s Executor Paths section mentions `component_trace_jsonb` as a production-path artifact but does not mention `execution_trace` at all.
- **suspected or confirmed defect:** Not a defect — recorded because Stage 04 (retry parity) and any future audit-tooling work need to know these are two independently-scoped mechanisms, not one trace system viewed two ways. Confirmed by direct code citation, not inferred.
- **evidence:** `evidence/2026-07-11-component-trace-jsonb-mechanism.txt`, `evidence/2026-07-11-tracer-callers.txt`
- **status:** confirmed
- **severity:** S3
- **related invariant:** none

---

### 02-002 — Per-employee retry produces zero `execution_trace` rows; original runs produce ~7–9

- **stage:** 02-execution-trace-baseline
- **location:** `backend/application/payroll_retry_service.py:505-820` (`retry_failed_payroll_employees`); contrast with `backend/application/payroll_run_service.py:71-141` and `backend/domain/payroll/run_executor.py:65-129`
- **current implementation:** `retry_failed_payroll_employees()` creates `tracer = ExecutionTracer(payroll_run_id)` at line 523 and passes it into `execute_single_employee_payroll(..., tracer=tracer)` for each failed employee, but the function body never calls `tracer.step(...)` anywhere (confirmed by grep across the full 313-line function — zero matches). The only way a row reaches `execution_trace` from `ExecutionTracer` is via `.step()`'s context-manager exit or `.warn_persist()`; neither fires during retry. The original run, by contrast, produces a `.step()`-wrapped row for each of: "Execute payroll engine", "Transition: DRAFT → CALCULATING", "Batch process: N employees", "Transition: CALCULATING → X", "Persist results", "Save payroll run header", "Save N employee results", "Save N audit entries", "Save N events" — 9 rows minimum.
- **intended behaviour:** Not documented — no source states whether retry runs are expected to leave the same `execution_trace` audit footprint as original runs, or a lighter one, or none.
- **suspected or confirmed defect:** Confirmed as a behavioural fact (retry writes zero `execution_trace` rows). Whether this is a defect depends on intended audit-trail completeness for retries — flagged here as an asymmetry for a human/product decision, not assumed to be wrong. If Stage 04 (retry parity) or any future auditor expects `execution_trace` to reconstruct "what happened during this run" for a retried run, that reconstruction is currently unavailable — only `component_trace_jsonb` per employee and the plain audit_log/event_store rows exist for retries.
- **evidence:** `evidence/2026-07-11-trace-persistence-gap-retry.txt`
- **status:** confirmed
- **severity:** S2
- **related invariant:** none

---

### 02-003 — `@trace_step`-decorated legacy calculation functions are unreachable on the production (sequential-executor) path

- **stage:** 02-execution-trace-baseline
- **location:** `backend/domain/payroll/salary.py:16-17` (`calculate_gross`), `backend/domain/payroll/calculator.py:15-16` (`calculate_net_pay`), `backend/domain/payroll/result_builder.py:19-24` (`build_payroll_result`); sole caller `backend/domain/payroll/executor.py:131` inside the `else` (legacy) branch of `execute_single_employee_payroll` (`executor.py:108-132`)
- **current implementation:** All three functions carry the `@trace_step(...)` decorator (`backend/application/trace_decorators.py`), which — when a tracer is present — wraps the call in `tracer.step(...)`, producing a persisted `execution_trace` row. `build_payroll_result` (which calls the other two) is only invoked from `executor.py`'s legacy `else` branch, which itself only fires when `component_metadata` is falsy. No caller anywhere in the codebase invokes `build_payroll_result`, `calculate_gross`, or `calculate_net_pay` from the sequential (production) path — confirmed by grep, zero other call sites.
- **intended behaviour:** `CLAUDE.md`'s Executor Paths section states the legacy path "Logs a deprecation warning" and directs "Migrate all callers" — consistent with these functions being intentionally legacy-only. No document states the `@trace_step` decorators on them are dead weight, but no document states otherwise either.
- **suspected or confirmed defect:** Not a functional defect (the code runs correctly when it does run). Recorded because it means the "Calculate gross pay" / "Calculate net pay (PAYE)" / "Build payroll result" step labels that would appear in `execution_trace` (were a legacy-path run to fire) never appear for any current production run — an auditor searching `execution_trace` for these step names using CLAUDE.md's Executor Paths description as a guide would find them only on the rare legacy-fallback path (see 01-004), not on the standard path.
- **evidence:** `evidence/2026-07-11-dead-trace-step-decorators.txt`
- **status:** confirmed
- **severity:** S3
- **related invariant:** `CLAUDE.md` Executor Paths section

---

### 02-004 — Per-employee console detail (`tracer.info`/`tracer.warn`) is never persisted — only step-level and explicit `warn_persist` events reach the DB

- **stage:** 02-execution-trace-baseline
- **location:** `backend/application/execution_tracer.py:95-113` (`info`, `warn`, `warn_persist` — only the last calls `_persist`); call sites at `backend/domain/payroll/batch_processor.py:106,114,119,153,172` and `backend/domain/payroll/executor.py:184,192,226,313`
- **current implementation:** `ExecutionTracer.info()` and `.warn()` write only to the Rich console (`console.log(...)`), with no call to `_persist()`. Every per-employee detail line — component breakdown, input list, period resolution, rule application, hire-proration factors, and even the employee-calculation-failure warning at `batch_processor.py:172` (`tracer.warn(f"Employee {short_id} calculation failed: {e}")`) — is console-only. Only `.step()` completions and explicit `.warn_persist()` calls reach `execution_trace`.
- **intended behaviour:** `execution_tracer.py`'s own docstrings (`warn_persist`: "Unlike warn(), this writes a DB row so the event is queryable. Use for recurring degraded-path events") indicate this split is intentional — `warn()` is deliberately console-only and `warn_persist()` is the persisted variant, used today only for `legacy_executor_fallback`.
- **suspected or confirmed defect:** Not a defect against any stated intent — the module's own docstring describes this split as deliberate. Recorded as a boundary fact: an individual employee's calculation failure inside an **original** run (not retry — retry's FAILED/SUCCESS transitions are separately captured via `payroll_result.status` and `error_message` columns) is visible in `execution_trace` only if the whole run later shows a failure count in the "Batch process" step's surrounding context — the specific employee and error text are not queryable from `execution_trace` itself, only from server logs/console at run time or from `payroll_result.error_message` after persistence.
- **evidence:** `evidence/2026-07-11-tracer-callers.txt`, `evidence/2026-07-11-trace-persistence-gap-retry.txt`
- **status:** confirmed
- **severity:** S3
- **related invariant:** none

---

## Diagnostic-script catalogue

One row per file in `scripts/` and `backend/scripts/` (18 files total, excluding
`__pycache__` and `.DS_Store`, matching Stage 01's 01-006 count).

| Script | Uses production services directly? | Reimplements calc logic? | Executor path | DB writes? | Read-only? | Stale/broken? |
|---|---|---|---|---|---|---|
| `scripts/run_first_payroll_emp001.py` | Yes (`execute_single_employee_payroll`, no `component_metadata`) | No | **Legacy** (fallback fires — no metadata passed) | Yes, raw `psycopg2` INSERTs bypassing the repository layer | No | **Yes — confirmed broken** (see 02-005) |
| `scripts/run_first_payroll_emp001.local_backup.py` | Yes (older signature) | No | Legacy | Yes | No | Yes — already flagged stale/tracked-but-ignored in 01-007; not re-analyzed here beyond confirming it is untouched |
| `scripts/seed_payroll_inputs.py` | No (writes `payroll_input` rows directly via SQL) | N/A | N/A — does not invoke the executor at all | Yes, `payroll_input` INSERTs | No | Not stale — current schema (`input_code`/`input_category`/`quantity`/`rate`/`amount`) matches production `payroll_input` usage |
| `scripts/show_config_tables.py` | No (generic table dump) | N/A | N/A | No | **Yes** | Not stale — table-name-and-column-agnostic, adapts to current schema at runtime |
| `scripts/simulate_payroll_components.py` | Partial — imports individual rule functions (`nhf`, `paye`, `pension`, `rent_relief`) directly rather than the sequential executor | **Yes** — re-orchestrates component resolution order itself rather than calling `run_sequential_payroll` | Neither — bespoke re-implementation, not the production sequential path | No (docstring claims read-only; confirmed by grep — no `commit()`/`INSERT`/`UPDATE`/`DELETE`) | **Yes** | Not confirmed broken, but its own logic is a parallel reimplementation, not the production executor — see 02-006 |
| `scripts/simulate_stepthrough.py` | **Yes** — calls `run_sequential_payroll()` and `apply_payroll_rules()` directly, the real production functions | No | **Sequential** (production path) | No (confirmed by grep) | **Yes** | Not stale — drives the real engine |
| `scripts/export_linear_csv.py` | No — unrelated to payroll; exports `docs/ROADMAP.md` to CSV for Linear import | N/A | N/A | No (writes `docs/linear-import.csv`, not the payroll DB) | Yes (payroll-DB read-only; writes a local file) | N/A — out of payroll-execution scope |
| `scripts/import_linear.py` | No — unrelated to payroll; imports a CSV into Linear via GraphQL | N/A | N/A | No payroll DB writes (calls external Linear API) | Yes (payroll-DB read-only) | N/A — out of payroll-execution scope |
| `backend/scripts/backfill_rule_set_snapshots.py` | **Yes** — calls `rule_set_service.auto_publish()`, explicitly documented as "NOT a reimplementation of its query" | No | N/A — snapshot backfill, not payroll calculation | Yes, via `auto_publish()` (idempotent, documented safe to re-run) | No (idempotent write) | Not stale — most recently modified file in either directory (10 Jul 20:29), references current `rule_set`/`rule_set_item` mechanism |
| `backend/scripts/load_employee_contracts.py` | No — raw SQL against `employee_contract` | N/A | N/A | Yes | No | **Yes — confirmed broken** (see 02-007) |
| `backend/scripts/load_grades.py` | No — raw SQL against `grade` | N/A | N/A | Yes | No | **Yes — confirmed broken** (see 02-007), plus hardcoded `workspace_id` and `data/acme_grades.json` path from an earlier client scaffold |
| `backend/scripts/simulate_payroll.py` | **Yes** — calls `run_sequential_payroll()` and `apply_payroll_rules()` directly | No | **Sequential** (production path) | No (confirmed by grep; docstring states "Read-only: no database writes") | **Yes** | Not stale — drives the real engine, most fully-featured of the three simulation scripts |
| `backend/scripts/test_execute_and_persist.py` | Attempts to (imports a non-existent function) | No | N/A — cannot run | Would attempt to, if it ran | No | **Yes — confirmed broken** (see 02-008) |
| `backend/scripts/test_export_netpay.py` | No — calls `export_net_pay_csv` with hand-built dummy data | No | N/A | No (writes a local CSV file) | Yes (payroll-DB) | Not broken (function signature matches), but exercises code with zero production callers (see 02-009) |
| `backend/scripts/test_export_paye.py` | Same as above, `export_paye_summary_csv` | No | N/A | No (local CSV) | Yes | Not broken; same zero-production-caller caveat |
| `backend/scripts/test_export_register.py` | Same as above, `export_payroll_register_csv` | No | N/A | No (local CSV) | Yes | Dummy input data happens to already use the correct (list) shape for `gross_components_jsonb`, masking the schema mismatch documented in 02-009 |
| `backend/scripts/test_persist.py` | Attempts to (wrong call signature) | No | N/A — cannot run correctly | Would attempt to, if it ran | No | **Yes — confirmed broken** (see 02-008) |
| `backend/scripts/test_run_batch_persist.py` | Attempts to (imports a non-existent function) | No | N/A — cannot run | Would attempt to, if it ran | No | **Yes — confirmed broken** (see 02-008) |

---

### 02-005 — `run_first_payroll_emp001.py` cannot execute successfully against the current schema: it omits the NOT NULL `payroll_result.status` column

- **stage:** 02-execution-trace-baseline
- **location:** `scripts/run_first_payroll_emp001.py:262-281` (raw `INSERT INTO payroll_result` column list); `migrations/versions/f1107690f184_add_batch_execution_status_fields2.py:21-47` (`status` added `NOT NULL`, `server_default` explicitly dropped at line 43-47)
- **current implementation:** The script's raw `psycopg2` INSERT into `payroll_result` lists columns `payroll_result_id, payroll_run_id, employee_id, gross_components_jsonb, deductions_jsonb, net_pay, calculations_snapshot_json` — omitting `status`. Migration `f1107690f184` added `status` as `NOT NULL` with an initial `server_default="SUCCESS"`, then explicitly removed that default in the same migration ("Optional: remove server_default after backfill"). An INSERT omitting `status` with no default will raise a NOT-NULL-violation.
- **intended behaviour:** Not documented as intentional — the script's own header comment ("PHASE 1.5 — FIRST REAL PAYROLL RUN (LOCAL ONLY)") indicates it was written as a working, runnable smoke-test at some point; nothing marks it as deliberately non-functional.
- **suspected or confirmed defect:** Confirmed — the script cannot successfully insert a `payroll_result` row against the current schema. It also does not pass `component_metadata`, so any successful calculation portion (before the INSERT) would run the legacy executor path with no `component_trace_jsonb`, and it bypasses `payroll_run_persister.py`/`ExecutionTracer` entirely, so even a hypothetically-fixed version would produce zero `execution_trace` rows and no audit_log/event_store rows for the run it creates.
- **evidence:** `evidence/2026-07-11-run-first-payroll-broken-insert.txt`
- **status:** confirmed
- **severity:** S3 (unimported by any production code path per Stage 01's 01-006; cannot corrupt production data because it cannot run to completion)
- **related invariant:** none

---

### 02-006 — `simulate_payroll_components.py` reimplements component resolution order rather than calling the production sequential executor

- **stage:** 02-execution-trace-baseline
- **location:** `scripts/simulate_payroll_components.py:42-59` (imports `calculate_nhf`, `calculate_paye_for_period`, `calculate_pension`, `calculate_rent_relief_for_period`, `apply_payroll_rules` directly — not `run_sequential_payroll` or `build_runtime_component_registry`)
- **current implementation:** Unlike `simulate_stepthrough.py` and `backend/scripts/simulate_payroll.py`, this script does not call `run_sequential_payroll()`. It imports the same underlying pure calculation functions the sequential executor uses, but orchestrates their call order and eligibility logic itself, in script code separate from `sequential_executor.py`'s handler-registry dispatch (`_HANDLERS`, `execution_priority` ordering, eligibility gating via `_check_eligibility`).
- **intended behaviour:** The script's own docstring calls itself a "Developer Simulation Tool" for "Rule Engine Transparency" — a legitimate goal, but not equivalent to exercising the actual production code path.
- **suspected or confirmed defect:** Not a runtime defect (the script does not claim to call the production executor). Recorded as a safety-for-audit-use caveat: if `sequential_executor.py`'s handler dispatch order, eligibility gating, or component-class overrides (`client_component_metadata` overrides) diverge from what this script's own re-orchestration assumes, this script's output could silently diverge from the true production calculation without either script or engine raising an error — since it does not call the shared engine, a future engine change would not be reflected here until the script is manually updated. It is the one of the three simulation scripts (`simulate_payroll_components.py`, `simulate_stepthrough.py`, `backend/scripts/simulate_payroll.py`) that is NOT provably faithful to the current engine by construction.
- **evidence:** `evidence/2026-07-11-simulation-scripts-safety.txt`
- **status:** confirmed (as a structural fact — the reimplementation is confirmed; whether its output currently diverges from the engine was not tested in this stage, since that would require controlled execution against a live DB, which is out of this stage's read-only remit unless explicitly authorized)
- **severity:** S2
- **related invariant:** none

---

### 02-007 — `load_employee_contracts.py` and `load_grades.py` cannot execute: both import `get_session` from a module that does not export it

- **stage:** 02-execution-trace-baseline
- **location:** `backend/scripts/load_employee_contracts.py:4` (`from backend.infra.db import get_session`), `backend/scripts/load_grades.py:3` (same); `backend/infra/db/__init__.py` (confirmed empty — 0 lines); `backend/infra/db/session.py` (confirmed to export only `SessionLocal`, not `get_session`)
- **current implementation:** Both scripts import a symbol, `get_session`, from `backend.infra.db`. That package's `__init__.py` is empty and `backend/infra/db/session.py` (the only other module in that package) defines `SessionLocal`, not `get_session`. The import will raise `ImportError` before any script logic runs.
- **intended behaviour:** Not documented. `load_grades.py` additionally hardcodes `workspace_id="6b70612c-b2e1-4275-800c-33140e7f4ebd"` and `path="data/acme_grades.json"` in its `if __name__ == "__main__":` block — consistent with a one-off setup script for an earlier ("acme") demo/test workspace, not a general-purpose tool.
- **suspected or confirmed defect:** Confirmed — both scripts fail at import time and cannot run at all in the current codebase state.
- **evidence:** `evidence/2026-07-11-load-scripts-broken-import.txt`
- **status:** confirmed
- **severity:** S3
- **related invariant:** none

---

### 02-008 — Four `backend/scripts/test_*.py` files are non-functional against the current codebase (wrong function name or wrong call signature)

- **stage:** 02-execution-trace-baseline
- **location:** `backend/scripts/test_execute_and_persist.py:2` and `backend/scripts/test_run_batch_persist.py:3` (both `from backend.application.payroll_run_service import execute_and_persist_payroll_run` — the actual function is named `execute_and_persist`, confirmed by `grep -n "^def " backend/application/payroll_run_service.py`); `backend/scripts/test_persist.py:16` (`save_payroll_result(payroll_run_id, employee_id, dummy)` — 3 positional args; the actual function signature at `payroll_result_repo.py:118-127` requires `payroll_run_id, employee_id, status, payroll_output, error_message` as its first five parameters, with `payroll_output` expected to be a dict containing a nested `"payroll_result"` key, not the flat `dummy` dict the script passes)
- **current implementation:** As cited — `test_execute_and_persist.py` and `test_run_batch_persist.py` fail at import time (`ImportError: cannot import name 'execute_and_persist_payroll_run'`); `test_persist.py` fails at call time (`TypeError: save_payroll_result() missing 2 required positional arguments: 'status' and 'payroll_output'` under the current signature, or a `KeyError`/`TypeError` on `dummy["payroll_result"]` if positionally reinterpreted). None of the three has been kept in sync with the current `payroll_run_service.py` / `payroll_result_repo.py` APIs.
- **intended behaviour:** Not documented. These files are excluded from `pytest` collection by `pytest.ini`'s `norecursedirs = backend/scripts` (per Stage 01's 01-006), despite being named `test_*.py`, so their breakage is not caught by CI.
- **suspected or confirmed defect:** Confirmed — all three are non-functional smoke-test scripts, silently stale because nothing runs them.
- **evidence:** `evidence/2026-07-11-backend-scripts-test-broken-signatures.txt`
- **status:** confirmed
- **severity:** S3
- **related invariant:** none

---

### 02-009 — `export_payroll_register_csv` assumes `gross_components_jsonb` is a list; production writes it as a dict — the export function is confirmed unreachable code, but latently broken if ever wired up

- **stage:** 02-execution-trace-baseline
- **location:** `backend/application/exports/payroll_register_export.py:45-54` (`for c in gross_components: ... c["amount"]`, where `gross_components = payroll["gross_components_jsonb"]`); production shape at `backend/domain/payroll/executor.py:343-347` (`gross_components = {code: {"amount": value} for code, value in results.items() if class_map.get(code) == "earning"}` — a dict keyed by component code, not a list)
- **current implementation:** `export_payroll_register_csv` iterates `gross_components_jsonb` as if it were `list[dict]` (each item having an `"amount"` key). The production sequential executor builds and persists `gross_components_jsonb` as `dict[str, dict]` (component code → `{"amount": ...}`). Iterating a dict with `for c in gross_components` yields its string keys, and `c["amount"]` on a string raises `TypeError: string indices must be integers`. Confirmed by direct comparison of both code sites; not executed in this stage (would require either a controlled run or synthetic data, and the function has no reachable production caller to exercise it against real data).
- **intended behaviour:** The function's own docstring states `gross_components_jsonb (list[dict])`, matching an earlier data shape that no longer matches what `executor.py` produces. No document reconciles this drift.
- **suspected or confirmed defect:** Confirmed as a code-level mismatch by direct citation (evidence type 1, per `_core/evidence-standard.md`). Confirmed separately, by grep, that this function has **zero production callers** anywhere in `backend/` — so the mismatch cannot currently corrupt a live export, but would break immediately (crash, not silent wrong output) the moment any future work wires this export into an API route or the retry/original-run flow using current-shape `payroll_result` data, unless the caller pre-transforms the shape. `backend/scripts/test_export_register.py`'s own dummy data happens to already use the list shape, which is why that test script does not currently surface the mismatch — its dummy data does not reflect the real production shape.
- **evidence:** `evidence/2026-07-11-export-scripts-schema-mismatch.txt`
- **status:** confirmed
- **severity:** S2 (elevated above a typical dead-code finding because this specific export was already flagged in prior analysis — see `project_sprint6_backlog.md` memory, P0-3/P1-4/P1-5 — as a gap to be closed; if it is closed by simply wiring up the existing function without fixing the shape mismatch, it will ship broken)
- **related invariant:** none

---

## Original-run / retry / script trace comparison (summary table)

| Execution path | Executor used | `component_trace_jsonb` produced? | `execution_trace` rows produced? | Notes |
|---|---|---|---|---|
| Original run (API `/payroll/run`) | Sequential (production) — `component_metadata` always supplied by the route | Yes, 1 per employee | Yes, ~7–9 run-level rows + 1 per legacy-fallback employee (rare, see 01-004) | Full lifecycle map above |
| Per-employee retry (only enabled `retry_strategy`, per `CLAUDE.md`) | Sequential (production) — `component_metadata` always loaded from run snapshot tables | Yes, 1 per retried employee | **Zero** (02-002) | `payroll_result.status`/`error_message` and audit_log/event_store rows still capture retry outcomes; `execution_trace` does not |
| `scripts/run_first_payroll_emp001.py` | Legacy (no `component_metadata` passed) | No (`component_trace_jsonb = None`, by the legacy branch's own code) | Zero (bypasses `ExecutionTracer` and `payroll_run_persister.py` entirely via raw SQL) | Also cannot complete — see 02-005 |
| `backend/scripts/simulate_payroll.py` / `scripts/simulate_stepthrough.py` | Sequential (production) — calls `run_sequential_payroll()` directly | Yes, printed to console, not persisted (no DB writes at all) | Zero (no `ExecutionTracer` instantiated; these scripts print their own step-by-step console output independently) | Faithful to the engine but produces no DB trace footprint of any kind |
| `scripts/simulate_payroll_components.py` | Neither — bespoke reimplementation (02-006) | N/A — does not call `run_sequential_payroll`, has its own console trace format | Zero | Not provably faithful to the engine by construction |

**Field/step comparison, production vs. scripts:** The two engine-faithful scripts
(`simulate_stepthrough.py`, `backend/scripts/simulate_payroll.py`) reproduce every
field the sequential executor's `trace` list produces (`component`, `method`,
`component_class`, `result`, period-sensitive annotations, `_trace_extras`) because
they call the same function and print its return value — no field-level drift was
found between production `component_trace_jsonb` and these two scripts' displayed
trace. No script reproduces any `execution_trace` step-level field (`step_name`,
`status`, `duration_ms`, `error_message`) — none of the 18 scripts instantiate
`ExecutionTracer` or write to `execution_trace` at all, confirmed by grep (no
`ExecutionTracer` import appears in any file under `scripts/` or `backend/scripts/`).

---

### 02-010 — No diagnostic script in either directory ever exercises or writes to the `execution_trace` table

- **stage:** 02-execution-trace-baseline
- **location:** `scripts/`, `backend/scripts/` (all 18 files)
- **current implementation:** Confirmed by grep — no file in either directory imports `ExecutionTracer`, `execution_trace_repo`, or `trace_step`. Every script that exercises calculation logic either bypasses tracing entirely (writes/prints its own ad-hoc console output) or, in the one case that does call `execute_single_employee_payroll` (`run_first_payroll_emp001.py`), passes no `tracer` argument at all (defaults to `None`, which internally resolves to `NULL_TRACER` — a no-op).
- **intended behaviour:** Not documented — no source states diagnostic scripts are expected to integrate with `execution_trace`.
- **suspected or confirmed defect:** Not a defect — recorded as a completeness fact for the retain/repair/replace/retire assessment below and for Stage 10 (execution-trace remediation) to consider: if `execution_trace` is meant to become a general audit-trail mechanism (beyond its current "batch-run and legacy-fallback monitoring" scope, per 01-005), no existing script provides a template for how a controlled, non-production run would populate it.
- **evidence:** `evidence/2026-07-11-tracer-callers.txt` (no script paths appear among the callers listed)
- **status:** confirmed
- **severity:** S3
- **related invariant:** none

---

## Retain / repair / replace / retire assessment

| Script | Recommendation | Rationale |
|---|---|---|
| `scripts/run_first_payroll_emp001.py` | **Retire** | Confirmed non-functional (02-005); exercises the deprecated legacy path; duplicates persistence logic that already exists correctly in `payroll_run_persister.py` |
| `scripts/run_first_payroll_emp001.local_backup.py` | **Retire** | Already flagged stale in 01-007; a `.gitignore`-excluded-pattern file that is nonetheless tracked; superseded by the file above (which is itself broken) |
| `scripts/seed_payroll_inputs.py` | **Retain** | Functional, current-schema, workspace-scoped, read-then-write pattern is clean and documented |
| `scripts/show_config_tables.py` | **Retain** | Functional, generic, read-only, workspace-scoping-aware |
| `scripts/simulate_payroll_components.py` | **Repair or retire** | Not broken, but not provably faithful to the engine (02-006) — either repair it to delegate to `run_sequential_payroll()` (bringing it in line with the other two simulation scripts), or retire it in favour of `simulate_stepthrough.py` / `backend/scripts/simulate_payroll.py`, which already cover the same "transparency" goal faithfully |
| `scripts/simulate_stepthrough.py` | **Retain** | Faithful to the production engine, read-only, well-documented; strong candidate for reuse as audit instrumentation |
| `scripts/export_linear_csv.py` | **Retain (out of scope)** | Unrelated to payroll execution; a project-management utility, functioning as far as this stage's evidence shows |
| `scripts/import_linear.py` | **Retain (out of scope)** | Same as above |
| `backend/scripts/backfill_rule_set_snapshots.py` | **Retain** | Functional, documented, idempotent, delegates to a real production service rather than reimplementing |
| `backend/scripts/load_employee_contracts.py` | **Retire or repair** | Confirmed broken import (02-007); if still needed for onboarding-adjacent seeding, needs its `get_session` import fixed and its hardcoded assumptions reviewed |
| `backend/scripts/load_grades.py` | **Retire or repair** | Confirmed broken import (02-007) plus hardcoded workspace/path from an earlier client scaffold — lowest-value of the two `load_*` scripts to keep as-is |
| `backend/scripts/simulate_payroll.py` | **Retain** | Faithful to the production engine, read-only, the most fully-featured of the three simulation scripts; strong candidate for reuse as audit instrumentation |
| `backend/scripts/test_execute_and_persist.py` | **Retire** | Confirmed broken (02-008), excluded from CI, no evidence of recent use |
| `backend/scripts/test_export_netpay.py` | **Repair or retire** | Not broken, but exercises dead production code (zero callers, 02-009); keep only if the export functions themselves are scheduled for wiring-up, in which case update the dummy data to reflect the current `gross_components_jsonb` shape first |
| `backend/scripts/test_export_paye.py` | **Repair or retire** | Same rationale as above |
| `backend/scripts/test_export_register.py` | **Repair — priority** | Same rationale, but this one's dummy data is currently masking the schema-mismatch defect in `export_payroll_register_csv` (02-009); fixing the dummy data to match production shape would immediately surface the defect via a failing test, which is valuable even before the export is wired up |
| `backend/scripts/test_persist.py` | **Retire** | Confirmed broken (02-008), excluded from CI |
| `backend/scripts/test_run_batch_persist.py` | **Retire** | Confirmed broken (02-008), excluded from CI |

**Can current scripts be safely used as audit instrumentation without changing
production behaviour?** Two scripts — `scripts/simulate_stepthrough.py` and
`backend/scripts/simulate_payroll.py` — call the real `run_sequential_payroll()`
engine directly, are confirmed read-only (no `commit()`/`INSERT`/`UPDATE`/`DELETE`
found by grep), and would not alter production behaviour if run against a
non-production database. They are the only two of the 18 scripts that meet this
bar. `simulate_payroll_components.py` is read-only but not provably faithful to the
engine (02-006), so its output should not be treated as equivalent to a production
trace without further verification. All other scripts either write data, are
non-functional, or are unrelated to payroll execution.

---

## Human-decision candidates raised (logged separately)

See [`../_core/human-decisions.md`](../_core/human-decisions.md).

| Question | Finding(s) |
|---|---|
| Should per-employee retry produce the same `execution_trace` step-level audit footprint as an original run, or is the current asymmetry (component-level trace only) acceptable? | 02-002 |
| Should `export_payroll_register_csv` (and its siblings) be fixed and wired up as part of closing the Sprint 6 backlog's export gap, or retired if exports are being redesigned? | 02-009 |
