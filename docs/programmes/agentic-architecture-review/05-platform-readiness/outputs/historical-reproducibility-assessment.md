# Stage 05 Output: Historical Reproducibility Assessment (F-01-27, F-01-29, F-01-38)

Re-verified against current committed code. **All three remain open**, unchanged since Stage 01 (2026-07-11). One unrelated remediation (commit `68e9307`, the `FAILED` status addition) touched two of the same files but does not close, worsen, or interact with any of these three findings — noted below for completeness only.

## F-01-27 — `salary_definition` edit-lock only at PAID

**Status: STILL OPEN.**

- `migrations/versions/f45614d5aa92_lock_salary_definition_when_paid.py:20-65` — `prevent_salary_definition_change_if_used()` trigger is unchanged; still only fires `WHERE run.status = 'PAID'` (line 32). No DB-level lock exists for `DRAFT`/`CALCULATING`/`CALCULATED`/`APPROVED`/`LOCKED`.
- The application-layer partial mitigation (`backend/api/routes/workspace.py:1529-1541`, D-ARCH-1 check in `patch_salary_definition`) is unchanged — no commits to this file since Stage 01.
- Net: a `salary_definition` referenced by an in-progress (not-yet-PAID) run can still be edited at the DB level with no guarantee, only a single application-layer route check covering `CALCULATED`/`PARTIAL`/`APPROVED` (and nominally, uselessly, `SUBMITTED`/`PROCESSING` — see F-01-38).

**Evidence required to close**: either (a) extend the DB trigger's `WHERE` clause to cover the full in-progress status range, or (b) if the application-layer check is deemed sufficient, extend it to cover every write path to `salary_definition` (confirmed today to cover only the one `patch_salary_definition` route) and add a regression test proving a direct-SQL or alternate-route edit is still blocked.

## F-01-29 — `component_trace_jsonb` dual fallback-precedence ambiguity

**Status: STILL OPEN — and now further narrowed.**

- `backend/infra/repositories/payroll_result_repo.py:37-115` (`save_payroll_results_bulk`) still takes the trace solely from `pr.get("component_trace_jsonb")` (line 63) — no fallback parameter in this function at all.
- `backend/infra/repositories/payroll_result_repo.py:118-211` (`save_payroll_result`) still has the ambiguous precedence: `component_trace = payroll_result.get("component_trace_jsonb") or component_trace` (lines 151-154).
- **New in this stage's re-verification**: no production caller of `save_payroll_result` was found anywhere in `backend/application/` — its only reference is `backend/scripts/test_persist.py:21`, a developer script, not a live application path. This means the fallback-precedence ambiguity, while still present in the code, is confirmed **not currently reachable from any production flow** — `save_payroll_results_bulk` (the bulk path, called from `payroll_run_persister.py:89`) is the only function actually exercised in production, and it has no such ambiguity.

**Practical implication**: this finding's severity is lower than Stage 01's framing suggested, now that the dead caller is confirmed. It remains open as a code-hygiene item (an unreachable function with ambiguous logic sitting in the repository layer) but is not currently an active reproducibility risk.

**Evidence required to close**: either remove `save_payroll_result` if it's confirmed dead code with no intended future caller, or if it's intended for a future single-employee-write path (e.g. retry), resolve the fallback ambiguity explicitly and add a test exercising that specific caller.

## F-01-38 — D-ARCH-1 lock check has dead `SUBMITTED`/`PROCESSING` branches; status vocabulary drift

**Status: STILL OPEN — confirmed against the current enum, which changed but did not close this gap.**

- `backend/api/routes/workspace.py:1540` still checks `pr.status IN ('SUBMITTED','PROCESSING','CALCULATED','PARTIAL','APPROVED')` — identical to Stage 01.
- `backend/domain/payroll/status.py:16-37` (`PayrollRunStatus`) now includes `FAILED` (added by commit `68e9307` / migration `b8c9d0e1f2a3_add_failed_payroll_run_status.py`) — full set: `DRAFT, FAILED, CALCULATING, CALCULATED, APPROVED, LOCKED, PARTIAL, PAID`. `SUBMITTED` and `PROCESSING` are still not members.
- `backend/domain/payroll/state_machine.py:15-24` (`ALLOWED_TRANSITIONS`) was updated by the same commit (`DRAFT → [CALCULATING, FAILED]`, `FAILED → []`) — again, no `SUBMITTED`/`PROCESSING`.
- **New in this stage's re-verification**: the lock-check's allowlist also omits `LOCKED` itself — consistent with F-01-27's framing that the in-progress window it covers stops short of `LOCKED`. (Separately, `payroll_result` immutability at `LOCKED` is enforced by a different, DB-level mechanism per F-01-37 — but that protects `payroll_result`, not `salary_definition` edits, which is what this check gates.)

**Evidence required to close**: replace the hardcoded status list with a reference to the canonical `PayrollRunStatus` enum (or an explicit "in-progress" subset derived from it) so the two can never drift again, and add `LOCKED` to the guarded range if that's the intended coverage.

## Cross-check: the FAILED-status migration is orthogonal, correctly scoped

`migrations/versions/b8c9d0e1f2a3_add_failed_payroll_run_status.py` is a real, committed, correctly-scoped remediation (part of the 04-001/05-001 snapshot-failure-visibility fix) — it adds `payroll_run.error_message` and a new `FAILED` status reachable only from `DRAFT`. It does not touch `salary_definition`, the D-ARCH-1 lock check, or `SUBMITTED`/`PROCESSING`, and does not supersede any of the three findings above. It surfaced in this stage's git-log search only because it happens to touch two of the same files (`status.py`, `state_machine.py`).

## Overall conclusion for C4/C8 launch readiness

All three findings remain open. Per the binding decision (D-02-03), **C4 (Historical Payroll Explanation) and C8 (Reconciliation Investigation) remain blocked** — this stage's re-verification found no basis to change that status. F-01-27 and F-01-38 are the two still-active blockers requiring remediation; F-01-29 is downgraded in practical severity (unreachable in production) but not fully closed.
