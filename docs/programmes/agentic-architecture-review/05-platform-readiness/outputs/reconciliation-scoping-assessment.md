# Stage 05 Output: Reconciliation Workspace Scoping Assessment (F-01-33)

**Verdict: STILL OPEN — unremediated, and one dimension is worse than Stage 01 found.** Re-verified directly against current committed code (git HEAD at time of this stage), not inferred from prior findings.

## Current scoping behaviour, exhaustively

| Layer | Current state | Evidence |
|---|---|---|
| Model | No `workspace_id` column on `payroll_reconciliation` | `backend/infra/db/models/payroll_reconciliation.py:7-24` — columns are `id`, `payroll_run_id` (FK, unique), `expected_total`, `actual_total`, `status`, `reconciled_at`, `created_at`, `notes`, `resolved_by`, `resolved_at` |
| Migrations | No migration ever adds `workspace_id` to this table | `migrations/versions/d1e2f3a4b5c6_add_payroll_reconciliation.py`, `migrations/versions/f7a8b9c0d1e2_add_reconciliation_resolution_fields.py` — neither touches workspace scoping |
| Repository | All three functions scope solely by `payroll_run_id` | `backend/infra/repositories/reconciliation_repo.py`: `insert_reconciliation` (15-79, no workspace_id param), `update_reconciliation` (82-144, `WHERE payroll_run_id = :rid AND status = 'MISMATCH'`, line 106-107), `get_reconciliation` (147-178, `WHERE payroll_run_id = :rid`, line 156) |
| Service | No function accepts a `workspace_id` parameter | `backend/application/reconciliation_service.py` — `reconcile_payroll_run`, `get_reconciliation_status`, `resolve_reconciliation` all call straight through to the unscoped repo functions |
| Legacy routes | No workspace_id in the path at all | `backend/api/routes/payroll.py` — `POST/GET /payroll/run/{run_id}/reconcile` (lines 1236, 1264) |
| "Workspace-scoped" routes | **Accept `workspace_id` but never use it** — worse than the legacy routes | `backend/api/routes/payroll.py:1293-1334` — `GET/POST/PATCH /{workspace_id}/payroll/runs/{run_id}/reconciliation` declare `workspace_id: str` as a path parameter, then discard it: `get_reconciliation_scoped` (1293-1299) calls `get_reconciliation_status(run_id)`; `submit_reconciliation_scoped` (1302-1315) calls `reconcile_payroll_run(run_id, ...)`; `resolve_reconciliation_scoped` (1318-1334) calls `resolve_reconciliation(run_id, ...)` — none pass `workspace_id` through |

## Why the "workspace-scoped" routes are a more severe finding than Stage 01 recorded

Stage 01 (F-01-33) found the underlying data path unscoped. This stage's re-verification adds a materially worse fact: **the API surface already presents a `workspace_id`-scoped-looking route to frontend/API consumers, creating a false impression of isolation while providing none.** Contrast with sibling endpoints in the same file that do enforce this correctly: `get_payroll_run` (line 1037-1047), `get_payroll_run_results` (line 1071-1079), and the `_guard_locked_or_paid`/`_guard_calculated_or_later` helpers (lines 1414-1434) all filter `WHERE payroll_run_id = :rid AND workspace_id = :wid`. The reconciliation routes were evidently scaffolded to match this pattern but the workspace check was never actually wired in.

## Cross-reference: docs/audit-program independently confirms this

`docs/audit-program/09-security-tenant-isolation/findings.md` documents the same gap under **09-002** (legacy unscoped route, severity S0) and **09-004** ("nominally-scoped reconciliation routes accept but discard `workspace_id`", severity S1), with matching line citations. This is independent corroboration, not this stage's only source — both were separately re-derived by direct code read in this stage's own investigation.

## Minimum code/test evidence required to close F-01-33

1. Add `workspace_id` (nullable initially, backfilled, then `NOT NULL`) to `payroll_reconciliation`, with a migration following this project's standing ADD COLUMN guard convention.
2. Update `insert_reconciliation`, `update_reconciliation`, `get_reconciliation` to accept and filter on `workspace_id`, joining through `payroll_run.workspace_id` at minimum for backward compatibility during migration, then directly once the column is populated.
3. Update `reconciliation_service.py`'s three functions to thread `workspace_id` through.
4. Fix the three "workspace-scoped" routes to actually pass and enforce the `workspace_id` they already accept — this alone (with no schema change) closes the "false impression of isolation" problem even before the column-level fix lands, and should be treated as the more urgent of the two fixes.
5. Add a regression test asserting cross-workspace access is rejected (a request with Workspace A's JWT/path param against Workspace B's `run_id` must 404 or 403, not succeed) — this project's standing rule that "every bug fix ships with a regression test named for the invariant it protects" applies directly here.

## Required defence-in-depth pattern for future tools

Per Stage 02/03's binding decision (D-02-02): even after the repository-level fix lands, any future `get_reconciliation`-style tool must independently re-verify workspace ownership at the tool-serialization layer — not trust the (now-fixed) repository function alone. This is unchanged by this stage's re-verification; it remains a required, separate layer.

## Treat as a hard blocker, not an accepted risk

Per this stage's explicit instruction: this finding is not downgraded to a documentation warning. `get_reconciliation` and any tool touching `payroll_reconciliation` remain blocked (per D-02-02) until both the repository-level fix (items 1-4 above) and the tool-layer check are demonstrated with committed code and a passing regression test — not merely planned.
