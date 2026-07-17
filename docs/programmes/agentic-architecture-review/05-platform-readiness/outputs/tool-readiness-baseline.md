# Stage 05 Output: Tool-Readiness Baseline

Assesses whether existing read paths that a future agent tool layer might wrap directly already enforce workspace ownership safely, independent of any new tool layer being built. Per this stage's scope, final tool contracts are Stage 08's to write — this is the technical-readiness baseline they'll build on.

## Per-endpoint/function assessment

| Path | Workspace scoping today | Safe to wrap directly? |
|---|---|---|
| `backend/api/routes/employees.py` (get employee/employees) | Explicit `workspace_id` filter at query level | Safe |
| `backend/api/routes/payroll.py` `get_payroll_run` (line ~1037-1047) | Explicit `WHERE payroll_run_id = :rid AND workspace_id = :wid` | Safe |
| `backend/api/routes/payroll.py` `get_payroll_run_results` (line ~1071-1079) | Same pattern — explicit workspace filter | Safe |
| `backend/infra/repositories/payroll_input_repo.py` (unclaimed-input functions) | Explicit workspace filter on the functions checked | Safe |
| `backend/api/routes/workspace.py` (salary definitions, enrollment-status-equivalent reads) | Explicit workspace filter | Safe |
| `payroll_reconciliation` (any future `get_reconciliation` tool) | **No scoping at all** — see `reconciliation-scoping-assessment.md` | **Not safe — blocked (D-02-02)** |
| `backend/infra/repositories/payroll_input_repo.py:82` `load_inputs_for_run(payroll_run_id)` | **No `workspace_id` parameter or filter at all** — newly identified in this stage | **Not safe if wrapped directly** — currently safe only because its one caller already validated run ownership upstream before calling it; a future tool calling this function directly would inherit no such guarantee |
| `backend/api/routes/workspace.py:133-134` `workspace_info()` | **Picks an arbitrary workspace with `LIMIT 1` and no scoping parameter at all** — newly identified in this stage | **Not safe under any circumstances** — this function structurally cannot distinguish between workspaces; it must never be wrapped as a tool as currently written |

## Two new findings from this stage's tool-readiness pass

Neither of the two "not safe" rows above (beyond the already-known reconciliation gap) was previously identified in Stage 01 — they surfaced specifically from this stage's tool-wrapping-risk lens, which asks a different question than Stage 01's general workspace-scoping sweep did ("is this query correct for its current caller" vs. "would this be correct if called directly by something new").

1. **`load_inputs_for_run(payroll_run_id)`** — safe today by construction (caller already validated ownership), unsafe as a direct tool target. Any future tool must add its own workspace check before calling this function, or the function itself should be extended to accept and enforce `workspace_id`.
2. **`workspace_info()`** — structurally unsafe; picks an arbitrary workspace. This function should not exist in its current form as a candidate for any tool wrapper, and its current (non-tool) callers should be reviewed separately to confirm it isn't already producing wrong results for a multi-workspace deployment.

## Cross-cutting requirement, reaffirmed

Consistent with Stage 02/03's binding principle (independent workspace-ownership enforcement per tool, not inherited from the underlying function): this stage's evidence shows that principle is not theoretical caution — it is the only thing that would have caught both of the newly-identified gaps above, neither of which a naive "the existing function already works, just wrap it" approach would have surfaced.

## Additional tool-readiness dimensions (per this stage's investigation scope)

- **Current-state vs. historical-state guarantee**: all "safe" rows above serve current-state data; none currently distinguish historical snapshots, which is consistent with C4/C8 remaining blocked.
- **Null/ambiguous-result behaviour**: `component_trace_jsonb` null handling is confirmed **fixed at the HTTP/UI surface** (`payroll.py:1129` coerces to `[]`; `PayrollResults.tsx:686-690` has an explicit empty-state UI) — this is genuine, verified progress since Stage 01/02's framing of this as an open specification gap. However, a **latent gap remains for a tool layer reading `payroll_result` directly**, bypassing the HTTP coercion — `payroll_result_repo.py:63` and `payroll_retry_service.py:418` have no null-guard at the data-access layer itself. A future tool built directly against the repository (not the HTTP route) would need its own null handling; it cannot assume the HTTP-layer fix protects it.
- **PII exposure**: not independently re-assessed in this stage beyond what Stage 02/03 already established (no PII-sanitizing tool layer exists yet, since no tool layer exists yet at all).
- **Pagination/result bounds**: not yet relevant — no tool implementation exists to check bounds against.

## Summary for Stage 08

Building the tool layer on top of these existing read paths is largely safe, with three confirmed exceptions requiring attention before or during tool construction: `payroll_reconciliation` (blocked per D-02-02, unchanged), `load_inputs_for_run` (needs its own workspace check added), and `workspace_info()` (should not be wrapped as-is). The `component_trace_jsonb` null-handling fix at the HTTP layer is good news but must be independently re-implemented at the tool/repository layer if any future tool reads `payroll_result` directly rather than through the existing route.
