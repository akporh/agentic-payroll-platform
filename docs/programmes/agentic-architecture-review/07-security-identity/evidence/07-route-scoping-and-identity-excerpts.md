# Stage 07 Evidence: Route Scoping and Identity Excerpts

All code evidence read at git commit `ea1590a37b626545022470e709107e30bcf45f66` (branch `uat`, 2026-07-17) — committed state only; no working-tree observations were used. Code files are unchanged since `b398c72` (the two intervening commits are docs-only), so Stage 06 evidence pinned at `265db10` drifts only by the `b398c72` feature commit; all line numbers below are re-resolved at `ea1590a`.

## §1 Full sweep of workspace-scoped route surfaces (all `backend/api/routes/*.py`)

Method: every `@router.<method>` route whose path contains `{workspace_id}` was enumerated (70 routes across `employees.py` 4, `payroll.py` 19, `payroll_input.py` 8, `workspace.py` 39 — denominator corrected from an initially stated 72 per the critic's independent recount, 2026-07-17; the five decorative-route identifications are unaffected), and the number of `workspace_id` occurrences in each route's decorator+function block was counted. A count of 2 means the parameter appears **only** in the path template and the function signature — i.e. it is accepted and never used. Counts of 3+ were spot-checked to confirm the parameter is actually threaded into the underlying query/service call (confirmed for `get_employee`, `list_inputs`, `edit_input`, `remove_input`, `get_payroll_config`, `get_rate_codes`, `transition_workspace_endpoint`, `onboarding_status`, `export_bank_upload` — all pass `workspace_id` through).

**Routes with count 2 (accept and discard `workspace_id`) — five, not three:**

| Route | Handler | Line (`ea1590a`) |
|---|---|---|
| `GET /{workspace_id}/payroll/runs/{run_id}/reconciliation` | `get_reconciliation_scoped` | `backend/api/routes/payroll.py:1327` |
| `POST /{workspace_id}/payroll/runs/{run_id}/reconciliation` | `submit_reconciliation_scoped` | `backend/api/routes/payroll.py:1336` |
| `PATCH /{workspace_id}/payroll/runs/{run_id}/reconciliation` | `resolve_reconciliation_scoped` | `backend/api/routes/payroll.py:1352` |
| `GET /{workspace_id}/payroll/runs/{run_id}/timeline` | `get_run_timeline` | `backend/api/routes/payroll.py:1372` |
| `GET /{workspace_id}/payroll/ops/legacy-executor-stats` | `legacy_executor_stats` | `backend/api/routes/payroll.py:1378` |

The first three are F-05-03 (consumed; line numbers re-resolved from 1293–1334 at `265db10` to 1327–1369 at `ea1590a`). The last two are new observations of the same pattern — see §2, §3.

## §2 `get_run_timeline` — cross-workspace execution-trace read

`backend/api/routes/payroll.py:1372-1375`:

```python
@router.get("/{workspace_id}/payroll/runs/{run_id}/timeline")
def get_run_timeline(workspace_id: str, run_id: str):
    """Return all execution trace steps for a payroll run, ordered by time."""
    steps = get_trace_steps(run_id)
    return steps
```

`backend/infra/repositories/execution_trace_repo.py:102-115` — the underlying query filters on `run_id` only:

```python
def get_trace_steps(run_id: str) -> list[dict]:
    """Return all trace steps for a run, ordered by creation time."""
    ...
    SELECT step_name, status, duration_ms, error_message, created_at
    FROM   execution_trace
    WHERE  run_id = :run_id
    ORDER  BY created_at ASC
```

Any caller can read any run's execution-trace steps (step names, status, durations, error messages) regardless of workspace.

## §3 `legacy_executor_stats` — platform-wide aggregate under a workspace-scoped path

`backend/api/routes/payroll.py:1378-1394` (`legacy_executor_stats`): the handler takes `workspace_id` and calls `get_legacy_executor_stats()` — a function with **no parameters at all**. `backend/infra/repositories/execution_trace_repo.py:45-58` documents the return shape: `total_runs`, `runs_with_legacy`, `pct_runs_affected`, `total_legacy_events`, and `by_run` — a per-run breakdown carrying `run_id` values — computed across **all runs in all workspaces**. A caller supplying any workspace_id receives platform-wide statistics including run IDs belonging to other workspaces.

## §4 `workspace_info()` — arbitrary-workspace route and its actual callers

`backend/api/routes/workspace.py:133-146`:

```python
@router.get("/workspace/info")
def workspace_info():
    db = SessionLocal()
    workspace = db.execute(
        text("SELECT workspace_id, name FROM workspace LIMIT 1")
    ).fetchone()
```

Returns the arbitrary `LIMIT 1` workspace's name and active-employee count. **Caller check (the F-05-11 open question):**

- `frontend/src/api/workspace.ts:12` declares `getInfo: () => api.get<Workspace>('/workspace/info')` — but a repo-wide grep for `getInfo` finds **no consumer** anywhere else in `frontend/src/`; the React frontend does not call it.
- `backend/api/templates/payroll.html:30` fetches `/api/v1/workspace/info` directly; that template is served by the legacy admin routes (`backend/api/routes/admin.py:26-27`).
- No backend Python code calls `workspace_info()`.

So the function is live and reachable (legacy admin page), and in a multi-workspace deployment that page would display an arbitrary client's name and employee count. The modern React frontend is not affected.

## §5 `load_inputs_for_run` — caller-discipline claim re-verified

`backend/infra/repositories/payroll_input_repo.py:82` — signature unchanged: `load_inputs_for_run(payroll_run_id: str)`, query filters `WHERE payroll_run_id = :run_id` only. Sole caller remains `backend/application/payroll_retry_service.py:606`. The caller's entry point `retry_failed_payroll_employees` (`payroll_retry_service.py:510`) **derives** `workspace_id` from the run row itself (`SELECT workspace_id, status, retry_strategy FROM payroll_run WHERE payroll_run_id = :run_id FOR UPDATE`, lines ~538-551) — so the loaded inputs always belong to the run's own workspace and internal consistency holds. Nothing verifies the *caller* is entitled to that workspace (that is F-05-01, consumed). F-05-11's "safe today via caller discipline, unsafe to wrap" classification is confirmed unchanged at `ea1590a`.

## §6 Auth absence and audit-actor inputs at `ea1590a` (line re-resolution of F-06-01 evidence)

- Grep for `OAuth2|jwt|JWT|get_current|HTTPBearer|APIKey` across `backend/api/` returns only `get_current_contract` (a domain function in `employees.py` — not auth). No auth dependency, token verification, or session mechanism exists on any route.
- No `operator` table exists in `backend/infra/db/models/` or any migration — C1 is fully greenfield.
- Caller-supplied audit actor inputs at `ea1590a` (drifted from Stage 06's `265db10` pins):
  - `X-Performed-By` header, default `"admin@internal"`: `backend/api/routes/payroll.py:1180` (retry), `:1207` (approve), `:1227` (lock)
  - request-body `actor_id`, default `"system@internal"`: `payroll.py:1255-1259` (pay)
  - free-text request-body `resolved_by`: `payroll.py:1356-1365` (reconciliation resolution — both legacy and scoped PATCH routes)
  - hardcoded `performed_by="system"`: `payroll.py:992`; hardcoded `performed_by="admin@internal"`: `payroll.py:1009`; service-layer default `performed_by: str = "admin@internal"`: `payroll_retry_service.py:510`

## §7 CORS posture

`backend/api/main.py:36-45`: `ALLOWED_ORIGINS` env var, **defaulting to `*`** ("Defaults to `*` for UAT/preview. Tighten to the Vercel URL in production" — the intent is documented in the comment but unenforced), `allow_credentials=False`, all methods/headers allowed. With `allow_credentials=False` and header-borne bearer tokens (the C1 design direction), a wildcard origin does not enable cookie-credential CSRF, but it does allow any origin to call the API with a stolen/leaked token from any web context; origin pinning at C1 launch is a hardening requirement, not a blocker.
