# Stage 05 Output: Frontend/Backend Alignment Reassessment

Reassesses confirmed mismatches from Stage 01/02 against current committed code. Each classified as **blocker** / **launch-risk** / **usability gap** / **normal implementation work**.

## 1. `RunPayroll.tsx` still offers `FULL_RUN` retry, despite DB/API rejecting it

**Status: STILL PRESENT.** `frontend/src/pages/RunPayroll.tsx:48,235-240` still presents both `PER_EMPLOYEE` and `FULL_RUN` as selectable radio options. The backend `_VALID_RETRY_STRATEGIES` allowlist and the DB CHECK constraint both reject anything but `PER_EMPLOYEE` (Stage 01 F-01-30/31, unchanged).

**Classification: launch-risk.** An operator can select an option that will always be rejected by the backend — not a data-integrity risk (nothing bad happens to data), but a confirmed broken UI path that produces a rejected request every time it's used. Independently confirmed by `docs/audit-program/06-ui-api-backend-wiring/findings.md` (finding 06-003), matching this stage's own citation.

## 2. `run_type` CORRECTION is API-only, not exposed in the UI dropdown

**Status: STILL PRESENT.** `backend/api/routes/payroll.py:76` still allows `CORRECTION` at the API layer; `frontend/src/pages/RunPayroll.tsx:45,199-202` still only offers `REGULAR`/`ADJUSTMENT` in its dropdown.

**Classification: usability gap**, not a blocker — this doesn't produce broken behavior (an operator simply cannot reach a supported backend capability through the normal UI), but it does mean the designed correction path (per Stage 01 F-01-43) is only reachable via direct API call, which is inconsistent with this being the stated correction mechanism for anything beyond per-employee retry.

## 3. `component_trace_jsonb` null handling

**Status: FIXED at the HTTP/UI surface — genuine progress.** `payroll.py:1129` now coerces a null trace to `[]` before it reaches the frontend; `PayrollResults.tsx:686-690` has an explicit empty-state UI for this case. This closes the specific gap Stage 02 (F-02-07) and Stage 03 (F-03-15) flagged as an unspecified edge case — it is no longer unspecified at this layer.

**Remaining gap, newly identified in this stage**: this fix lives at the HTTP/UI boundary, not at the data-access layer. `payroll_result_repo.py:63` and `payroll_retry_service.py:418` still have no null-guard. A future tool reading `payroll_result` directly (not through the existing HTTP route) would not inherit this protection — see `tool-readiness-baseline.md`.

**Classification: normal implementation work** for the HTTP-layer fix (already done); the data-access-layer gap is a **launch-risk** specifically for the future tool layer, not for today's operators.

## 4. `employee.status` has no DB CHECK constraint

**Status: STILL PRESENT.** Confirmed via `docs/schema_dump.sql:558-566` — enforcement remains Python-only (`backend/api/routes/employees.py:32-134`).

**Classification: normal implementation work.** Consistent with Stage 01's original assessment (Low severity) — no observed path writes an invalid value, but nothing at the DB layer prevents it. Not urgent relative to the other findings in this stage.

## 5. Configuration values written to one representation, read from another

Not independently re-verified as a new item in this stage beyond what's captured above; no new instance was surfaced by the research clusters dispatched for this stage. If this is a live concern, it should be raised as a specific, evidence-backed finding in a future stage rather than left as an unverified carryover here.

## Summary table

| Mismatch | Classification | Change since Stage 01/02/03 |
|---|---|---|
| FULL_RUN in UI, rejected by backend | Launch-risk | Unchanged |
| CORRECTION API-only | Usability gap | Unchanged |
| `component_trace_jsonb` null handling | Fixed (HTTP layer); launch-risk (tool layer, new) | **Improved**, with a newly-identified residual gap |
| `employee.status` no DB CHECK | Normal implementation work | Unchanged |
