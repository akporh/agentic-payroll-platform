# Stage 08 Output: Remediation Designs

Answers Stage 08 Q8: concrete fix designs, each with closure evidence, for the remediation items the closure plan (`05-platform-readiness/outputs/readiness-closure-plan.md`) and Stage 07 fixed. Priorities are the closure plan's, not re-litigated. Evidence pinned at `573be0d` (Stage 05/07 line citations re-verified unchanged — `findings.md` F-08-03).

## 1. Reconciliation workspace scoping (Critical — F-01-33 / D-02-02, Stage 05's five items)

Design per `reconciliation-scoping-assessment.md`'s minimum-evidence list, sequenced so the most urgent closure lands first:

1. **Route fix first (no schema change)**: the three scoped routes (`payroll.py:1327-1369` — `get_reconciliation_scoped`, `submit_reconciliation_scoped`, `resolve_reconciliation_scoped`) verify run ownership before delegating: one guard query `SELECT 1 FROM payroll_run WHERE payroll_run_id = :rid AND workspace_id = :wid` (the exact pattern their siblings at `payroll.py:1071-1079` already use); miss → 404. Under C1 this arrives automatically for the path-vs-claim half via `get_workspace_principal`, but the run-ownership guard is still required (the claim proves the caller's workspace; the guard proves the *run* is in it).
2. **Schema**: `ALTER TABLE payroll_reconciliation ADD COLUMN workspace_id UUID NULL` (standing ADD COLUMN guard convention), backfill `UPDATE ... SET workspace_id = r.workspace_id FROM payroll_run r WHERE ...`, then `SET NOT NULL` + FK — three-step migration with pre-checks and working downgrade per repo convention.
3. **Repository**: `insert_reconciliation`/`update_reconciliation`/`get_reconciliation` (`reconciliation_repo.py:15-178`) gain a required `workspace_id` parameter; every `WHERE` adds `AND workspace_id = :wid` (direct column post-backfill). No default value — callers must supply it (the `feedback_constraint_violations` principle: no silent masking).
4. **Service**: `reconciliation_service.py`'s three functions thread `workspace_id` through; the legacy unscoped routes (`payroll.py:1270-1312`) are **removed** (they duplicate the scoped surface; keeping an unscoped twin defeats the fix — frontend already has the scoped paths).
5. **Regression test** named for the invariant: Workspace A session + Workspace B `run_id` → 404 on all three routes; repo-level cross-workspace call returns nothing.

**Closure evidence**: the committed migration + the regression test green + (for D-02-02's tool half, when C8 unblocks) the wrapper-independence test. Tool remains unregistered until both layers are demonstrated (P8).

## 2. The five decorative routes (F-05-03 Critical + F-07-01)

Same guard-query pattern as §1.1, per route:

| Route | Fix |
|---|---|
| Reconciliation trio (`payroll.py:1327-1369`) | §1 above — first |
| `get_run_timeline` (`payroll.py:1371-1376`) | Add the run-ownership guard before the timeline query; its underlying audit query also gains `AND workspace_id = :wid` (two-layer standard) |
| `legacy_executor_stats` (`payroll.py:1378-1394`) | **Moved to the platform-ops surface** (`/platform/ops/legacy-executor-stats`, `PLATFORM_ADMIN` role, no `{workspace_id}` in path) — the handoff's either/or resolved toward platform-ops because the statistic is a platform-wide executor-migration metric, not workspace data; leaving a workspace-shaped path that returns platform-wide data would preserve the decorative pattern in disguise |

**Closure evidence**: per-route negative-path tests + the route-table-generated isolation test (SS-1) green — proving the decorative pattern is dead platform-wide, not just on the five known routes (SG-8's framing).

## 3. `load_inputs_for_run` (Medium — F-05-11)

`payroll_input_repo.py:82` gains a required `workspace_id` parameter; query becomes `WHERE payroll_run_id = :rid AND workspace_id = :wid`. Its existing caller passes the run's verified workspace. No optional-parameter grace period — one caller exists (Stage 05), so the breaking signature change is trivial and removes the unsafe-if-wrapped state permanently.
**Closure evidence**: repo-level test — mismatched `workspace_id` returns zero rows.

## 4. `workspace_info()` (Medium — F-05-11 / F-07-02)

Stage 07 answered the caller question: legacy admin template only, React unaffected. **Design: retire.** The `LIMIT 1` function (`workspace.py:133-134`) and the legacy admin HTML routes that consume it are deleted at C1 cut-over (they cannot survive the auth allowlist anyway — `auth-foundation-design.md` §3.3). Any residual operational need is served by the authenticated `GET /workspaces` list + token-scoped workspace reads.
**Closure evidence**: grep-clean (no `workspace_info` references) + route-enumeration test shows no unauthenticated admin HTML routes.

## 5. Audit-store append-only protection (SS-3)

Designed in `event-audit-foundation-design.md` §5 (trigger floor, DEC-07-04 residual accepted, no purge path). Listed here for Q8 completeness.
**Closure evidence**: UPDATE/DELETE rejection tests per protected table + the §2 forced-failure outbox test.

## 6. `component_trace_jsonb` repo-layer null guard (Medium)

`payroll_result_repo.py:63` (and the retry-service read at `payroll_retry_service.py:418`) return trace as a typed result: `trace: list | None` with an explicit `trace_available: bool` — never coercing null to `[]` at the data layer (the HTTP layer's `payroll.py:1129` coercion is a presentation choice; the data layer must preserve the distinction so tools and future callers can implement the refusal contract, `tool-contracts.md` §3.4–3.5).
**Closure evidence**: repository-layer unit test on a null-trace fixture, no HTTP route involved (closure plan's stated form).

## 7. `salary_definition` in-progress edit-lock (High — D-ARCH-1 family)

**Design: application-layer lock extension, not trigger extension.** The existing DB trigger precedent protects `payroll_result` for PAID; the salary-definition risk is live-read divergence during `DRAFT/CALCULATING/…` (`feedback_salary_def_live_read`: `components_jsonb` is read live at run start). The check belongs where every write path already passes — the service layer guard — extended to reject salary-definition PATCHes for definitions referenced by any run in the full in-progress status range, with the range **derived from the canonical `PayrollRunStatus` enum** (§8's fix pattern), not a hand-copied list. A DB trigger duplicate is deliberately not added: two lock implementations with independently-maintained status lists is precisely the drift D-ARCH-1 demonstrated.
**Closure evidence**: test proving an edit during `DRAFT`/`CALCULATING`/`LOCKED` (not just `PAID`) is rejected, on every write path (enumerated: the PATCH route; no other write path exists per the Stage 05 audit).

## 8. D-ARCH-1 dead branches / status drift (High)

Replace hardcoded status lists in the lock/guard helpers with derived subsets of the canonical `PayrollRunStatus` enum, declared once (e.g. `IN_PROGRESS_STATUSES: frozenset[PayrollRunStatus]`) and imported by every consumer.
**Closure evidence**: the closure plan's enum-iteration test — a test iterating the enum asserting every member is classified by the derived subsets (new statuses fail the test until classified, making silent divergence impossible).

## 9. Sequencing (consumed from the closure plan, restated for build order only)

C1 (auth + §2 routes + §4 retirement) → C2 facade/outbox (with §5 triggers in the same migration family) → §1 reconciliation schema fix → §3/§6–§8 in any order alongside. Nothing here re-prioritises the closure plan; §1.1's route guard is the only item pulled explicitly early (Stage 05: "the more urgent of the two fixes").
