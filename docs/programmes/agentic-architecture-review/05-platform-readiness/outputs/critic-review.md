# Stage 05 (Platform Readiness) — Independent Critic Review

*Critic run 2026-07-15 as an independent read-only review pass (separate role from the primary executor, per D-003's safety condition). Report saved verbatim by the controller; the critic edited no files.*

## Verdict: PASS

With 0 blocking human decisions recorded, this PASS permits automatic closure of Stage 05 and opening of Stage 06 per the D-003 lifecycle.

## Scope reviewed

I read the binding contract (`CRITIC.md`), all five `_core/` standards, and `HUMAN-DECISIONS.md` (HD-2 through HD-7 / D-02-01..04, D-03-01, D-04-01). I then read Stage 05's `CONTEXT.md`, `findings.md`, `decisions.md`, `review-state.md`, and all 15 output files. I independently verified findings against live code at the reviewed commit (`65e87aa`) and current HEAD (`fd70e2b`), confirming via `git log`/`git diff` that the only intervening production change is `be337aa` (SEC-S7 timesheet upload limit) — unrelated to any finding and not bundled into this stage.

I spot-checked 7 of the 12 confirmed findings against source (exceeding the 5 required): F-05-01 (auth), F-05-02 (event foundation), F-05-03 (reconciliation scoping), F-05-06 (D-ARCH-1 lock check), F-05-08 (retry snapshot-first), F-05-11 (tool-wrapping risks), and the F-01-40 audit-coverage reconfirmation.

## Strengths

- **The two headline claims are true and precisely stated.** Zero authentication: no `operator` model, and no `jwt`/`Bearer`/`oauth2`/`HTTPBearer`/`api_key`/`get_current_operator`/`current_user` reference exists anywhere in `backend/api/` — grep returns empty. F-05-01 does not overclaim; it correctly frames every workspace-scoping guarantee as holding "only against an honest caller."
- **The "decorative workspace-scoped routes" claim (F-05-03) is exactly right and is the stage's strongest original contribution.** `backend/api/routes/payroll.py:1293-1334` declare `workspace_id: str` and then call `get_reconciliation_status(run_id)` / `reconcile_payroll_run(run_id, ...)` / `resolve_reconciliation(run_id, ...)` — the parameter is genuinely discarded. `reconciliation_repo.get_reconciliation` scopes solely `WHERE payroll_run_id = :rid`. The observation that a false impression of isolation is arguably worse than an honest absence, and could pass a superficial "does the route accept a workspace_id" review, is a legitimate escalation, not rhetoric.
- **The F-05-08 improvement is honestly separated from the gaps and is real.** `tests/test_payroll_retry_snapshot_first.py` exists with 5 tests; the stage credits genuine progress (commit `68e9307`) rather than only cataloguing defects, and did not let the improvement soften an adjacent blocker.
- **Committed-vs-uncommitted discipline was honored.** The stage refused to treat working-tree remediation as closure and confined its evidence to committed code, per CONTEXT constraints.

Additional verifications that held: F-05-06 — `PayrollRunStatus` contains DRAFT/FAILED/CALCULATING/CALCULATED/APPROVED/LOCKED/PARTIAL/PAID, so the lock-check allowlist `('SUBMITTED','PROCESSING','CALCULATED','PARTIAL','APPROVED')` at `workspace.py:1540` does contain two dead values and omits `LOCKED`. F-05-02 — `event_store_repo.py` exposes only `save_event` (write); no consumer/reader and no `workspace_notification` model exist. F-05-11 — `workspace_info()` runs `SELECT workspace_id, name FROM workspace LIMIT 1` (no scoping) and `load_inputs_for_run(payroll_run_id)` takes no workspace parameter. F-01-40 — `audit_events.py` is explicitly scoped to PAYROLL_RUN transitions only.

## Required corrections

None. No substantive gap rises to REVISE, and no evidence/scope/authority issue rises to STOP.

## Decision classification (every open question found)

- **F-05-09 — "what does 'safely separated from production state' mean operationally (does a dry run create a `payroll_run` row)?"** → `implementation-specification`. Correctly forwarded to Stage 08; not a Stage 05 gate question.
- **F-05-12 — "should `run_type = CORRECTION` remain API-only or be exposed in the UI?"** → `non-blocking-forwarded-decision`. A genuine product choice, correctly forwarded to Stage 09/11, not decided here.
- **F-05-07 — severity downgrade of F-01-29 (a finding HD-4/D-02-03 named as a launch precondition) to Low / "not a blocker."** → `not-a-decision` (evidence-grounded reassessment explicitly requested by CONTEXT §3). This does **not** overturn D-02-03: the capability-readiness matrix (C4 row) and closure plan still list "F-01-29 resolution or removal" as required closure evidence for C4. The downgrade reflects verified unreachability (no production caller of the ambiguous `save_payroll_result` fallback; only `save_payroll_results_bulk` is used), is justified inline, and preserves the binding decision rather than re-litigating it. I flag it only so the human reviewer is aware the severity was re-graded on new evidence — it is not a required correction.

No `blocking-human-decision` was found. The "0 human decisions at this gate" claim is correct.

## Evidence-quality assessment

Strong. Findings cite this stage's output files, and those outputs in turn carry precise `file:line` citations into live code; I traced the chain to source for the sampled findings and every citation resolved accurately. The empty `evidence/` folder is compliant — the stage relied entirely on stable code `path:line` references, which `EVIDENCE-STANDARD.md` §Evidence-storage explicitly exempts from duplication (only transient artifacts must be copied in). Confidence and severity are tracked separately per the schema. No finding rests on naming inference, memory, or unverified prior-stage assumptions; the stage re-derived F-01-27/29/33/38/40 against current code rather than assuming Stage 01 still held, which is exactly the discipline the standard requires.

## Consistency assessment

Internally coherent. All 15 required outputs are present and match the CONTEXT output list exactly. All 15 capabilities carry a readiness classification (2 ready-with-work, 2 conditionally ready, 8 blocked, 2 deferred, 1 rejected). The blocker register's severity tallies match the findings (4 Critical / 4 High / 3 Medium / narrowed-Low). The Stage 06/07/08 handoffs are mutually non-contradictory and consistent with `findings.md`: Stage 06 gets C12 + audit + tenant-isolation-as-control-failure; Stage 07 gets auth + reconciliation + the two new tool risks; Stage 08 gets the eight mechanism-design tasks. Inherited binding decisions (D-02-02, D-02-03, D-02-04, D-04-01) are treated as gates and preserved, not re-opened. Draft/parked sections are correctly empty and no draft/parked finding is cited cross-stage.

## Advancement recommendation

Stage 05 may advance. The investigation is thorough, in-scope, and evidence-backed; the headline conclusions (zero auth; unbuilt event/notification/exception foundation; still-open and now-worse reconciliation scoping; C12 greenfield) are independently confirmed against committed code. No manufactured blockers were found, and no genuine blocking human decision remains at this gate. On this PASS, with 0 human decisions recorded, the controller may close Stage 05 and open Stage 06. I recommend the controller surface the single informational note above (F-05-07's evidence-based downgrade of F-01-29, with D-02-03's closure requirement still intact) to the human reviewer for visibility — not as a blocker, but so the reassessment is acknowledged rather than absorbed silently.
