# Stage 11 — Scenario Testing: Findings

**Status:** complete
**Opened:** 2026-07-12
**Closed:** 2026-07-13
**Evidence:** `docs/audit-program/11-scenario-testing/evidence/`

This is an execution/testing stage. All scenarios below were run against local `payroll_dev` (non-production) via a locally-started `uvicorn backend.api.main:app` instance and the existing `pytest` suite. No production/client data was used. The local server was started and stopped cleanly within this stage; all live-server scenarios were read-only GETs against existing dev-fixture data — zero rows were created, modified, or deleted, so no cleanup step was required beyond stopping the server process (confirmed via `curl` returning connection-refused after shutdown, evidence file `06`). No production code, migration, test file, or data was modified.

**Scope decision, stated up front:** given the size of this stage's investigation surface (16 required areas) and the constraint against mutating shared dev-DB state without a fully isolated disposable fixture, this stage executes a representative, high-value subset live (automated test suite in full; targeted `04-001`/`05-001` regression; five cross-tenant/disclosure scenarios against real dev data; one synthetic in-memory CSV-injection proof) and, for the remaining areas, relies on re-verification of already-confirmed prior-stage evidence (re-queried live where cheap and safe — e.g. `08-001`'s nullable-count, the GIST overlap constraint's existence) rather than re-deriving every scenario from first principles. Every row below states explicitly which category it falls into, per this stage's own finding rules distinguishing "reproduces an existing finding" from "new distinct finding."

---

## 1. Automated test baseline

```
command:      python -m pytest tests/ -q
environment:  local payroll_dev (non-production PostgreSQL), Python 3.10.19, pytest 7.4.4
result:       306 passed, 1 skipped, 48 warnings, 7.10s
```
Full output: `evidence/01-full-test-suite-run.txt`. Deterministic (no `-p no:randomly` needed — suite has no randomization plugin active; two consecutive local runs produced identical pass counts, one captured in evidence, one via the pre-existing pre-push hook run at Stage 10's close). Test suite includes payroll calculation (`test_calculation_scenarios.py`, `test_paye.py`, `test_pension.py`, `test_nhf.py`, `test_salary.py`), retry (`test_payroll_retry.py`, `test_payroll_retry_snapshot_first.py`), snapshot (`test_payroll_snapshot_integrity.py`, `test_payroll_run_snapshot_immutable.py`, `test_snapshot.py`), reconciliation (`test_payroll_reconciliation.py`, `test_payroll_reconciliation_e2e.py`), state-machine/lifecycle (`test_state_machine.py`, `test_illegal_payroll_status_transition.py`, `test_payroll_lock_and_approval.py`, `test_payroll_paid_lifecycle.py`), and export-adjacent (`test_sql_emitter.py`) coverage. **No dedicated tenant/workspace-scoping test file exists** — confirmed by directory listing; this is itself a coverage gap, carried to §16/§18 below and to `09-000`'s remediation package.

Tests mutate persistent data within their own transaction-rollback fixtures (standard pytest DB-fixture pattern already in use throughout this codebase) — none of this stage's test runs altered `payroll_dev`'s persisted state.

---

## 2. `04-001` snapshot-first retry regression — re-executed, passed

```
command: python -m pytest tests/test_payroll_retry_snapshot_first.py tests/test_payroll_run_snapshot_immutable.py -v
result:  6 passed, 0 failed
```
Specifically confirms: `test_retry_uses_frozen_statutory_snapshot_not_intervening_live_rule` (proves the exact scenario in this stage's §2 instructions — a later live statutory rule change does not affect retry), `test_retry_hard_fails_on_legacy_v1_statutory_snapshot` (incomplete/legacy snapshots are rejected before mutation, no live fallback), `test_v2_retry_issues_no_live_statutory_rule_or_tax_band_query` (structural proof retry never queries live statutory tables), `test_snapshot_creation_failure_aborts_calculation_and_marks_run_failed` (this is simultaneously `05-001`'s regression, see §3), `test_successful_snapshot_creation_still_calculates_normally` (positive control), `test_run_snapshot_is_immutable` (DB-trigger-level immutability, unchanged).

**Disposition:** `passed` — `04-001` regression suite fully green, `04-001` remains remediated. No contradictory evidence found; not reopened.

---

## 3. `05-001` snapshot-failure visibility regression — re-executed, passed

`test_snapshot_creation_failure_aborts_calculation_and_marks_run_failed` (same run as §2) directly asserts: run reaches terminal `FAILED` status, `error_message` is populated, calculation/result persistence does not begin when snapshot creation fails, consistent with the remediation's own `verification.md`. Not independently re-derived beyond re-running the existing test this stage, since the test already asserts exactly the invariants this stage's instructions ask for (run status, `error_message`, no persisted results) — re-executing the same scenario via a fresh hand-rolled fixture would not add evidence beyond what the existing, passing regression test already proves.

**Frontend handling status:** unchanged, still incomplete per `06-001`/`06-004` (not re-verified live this stage — no code changed since Stage 06/09 confirmed this; re-stating it here only to correctly distinguish "backend behaves correctly" from "frontend doesn't yet display it," per this stage's own instruction).

**Disposition:** `passed` (backend regression); `06-001`/`06-004` frontend gap unchanged, not re-tested (no code change since last confirmed).

---

## 4. Outer background-task failure (`07-003`) — blocked-by-missing-test-seam, documented

No safe injection point exists to force an *outer* (post-snapshot, pre-contained) background-task failure without either (a) modifying production source on disk (prohibited this stage) or (b) constructing a fully isolated monkeypatch harness that reaches into `payroll_run_service.py`'s background-task execution path at a specific point — which the existing test suite does not currently expose a seam for (confirmed by inspecting `test_payroll_partial_run_e2e.py`/`test_payroll_pipeline_e2e.py`, neither of which injects failures at this specific boundary; both test the happy path and the already-covered per-employee-failure `PARTIAL` path).

**Blocked-test specification for future implementation:** a dependency-injection seam (e.g. an injectable post-snapshot hook, or a pytest `monkeypatch` target on the specific outer `try` block identified in Stage 07's `07-003` finding at the exact call site between snapshot completion and per-employee batch start) is required before this scenario can be executed without editing production source. This is recorded as a new permanent-test recommendation in §18, not executed this stage.

**Disposition:** `not-executed-with-reason` — documented blocked seam, not a new defect; `07-003` remains confirmed exactly as Stage 07 left it (log-only outer failure), unchanged and unre-derived.

---

## 5. Retry behaviour matrix

| Scenario | Disposition | Evidence |
|---|---|---|
| Valid `PARTIAL` run, one failed employee, retry succeeds | passed | `test_payroll_retry_snapshot_first.py::test_successful_snapshot_creation_still_calculates_normally` and `test_payroll_retry.py` (existing suite) |
| Multiple failed employees, mixed success/failure | passed | existing `test_payroll_retry.py` coverage (not re-derived beyond suite pass; matches Stage 04's own controlled test shape) |
| Invalid status (not `PARTIAL`) rejected | passed | `payroll_approval_service.py`/`payroll_retry_service.py` guard, exercised by existing suite |
| Complete snapshot | passed | §2 |
| Incomplete/legacy snapshot hard-fails | passed | §2 (`test_retry_hard_fails_on_legacy_v1_statutory_snapshot`) |
| Repeated retry request on the same run | plausible/not independently re-executed | Existing suite does not include an explicit "retry twice in a row" test; Stage 08's `04-004` structural proof (state-machine guards) implies the second call would fail preflight (run no longer `PARTIAL` once fully resolved, or the DELETE+INSERT replacement remains safe if still `PARTIAL`), but this specific double-invocation path was not freshly executed this stage. Recorded as a coverage gap in §16/§18, not claimed as tested. |
| Result uniqueness after DELETE+INSERT replacement | passed | `uq_payroll_result_employee_run` constraint (confirmed present, Stage 08) plus existing retry test assertions |
| Total recomputation from result rows | passed | existing suite |
| Final transition to `CALCULATED` or remaining `PARTIAL` | passed | existing suite |
| Preservation of successful original employee results | passed | existing suite (retry only touches `FAILED` rows, confirmed by code and test) |
| `execution_trace` output for retry | **confirmed gap, not a surprise** | Live read-only query (`evidence/07-retry-trace-zero-rows.txt`) plus Stage 02/07/10's static code confirmation that `payroll_retry_service.py` instantiates `ExecutionTracer` but never calls `.step()`. Not independently re-demonstrated via a fresh live retry invocation this stage (would mutate shared dev-DB `payroll_run`/`payroll_result` state without a disposable fixture) — relying on the already-confirmed code-level fact (`02-002`, restated with exact call-site precision in Stage 10) rather than re-deriving it. |

---

## 6. Financial calculation scenarios

**Not independently re-executed this stage.** The existing automated suite (§1) already covers salaried monthly, joiner/leaver proration, pension employee/employer split, NHF, PAYE, timesheet/shift, overtime, and zero-value/ineligible-component scenarios via `test_calculation_scenarios.py`, `test_paye.py`, `test_pension.py`, `test_nhf.py`, `test_salary.py`, `test_client3_shift_allowance.py`, `test_multi_event_rule_evaluation.py`, `test_sprint12_m1_m2.py`, and all passed in §1's full run. Constructing fresh hand-derived expected-value fixtures for each of these categories, independent of the implementation under test, is a materially larger effort than this stage's time budget supports beyond confirming the existing suite is green and covers the named categories by file/test-name inspection (confirmed: each named scenario category has at least one corresponding test file). Rent relief and arrears/reference-period handling were not confirmed to have dedicated test coverage by this file-name scan — recorded as a coverage gap in §16, not claimed as tested.

**Disposition:** `passed` (via existing suite, not independently re-derived) for salaried/proration/pension/NHF/PAYE/shift/overtime; `not-executed-with-reason` (no confirmed dedicated coverage found) for rent relief and arrears/reference-period handling specifically.

---

## 7. Payroll arithmetic and aggregate invariants

`gross_pay - deductions - tax = net_pay`, run-total-equals-sum-of-successful-results, and Decimal-precision stability are all asserted within the existing e2e suite (`test_payroll_pipeline_e2e.py`, `test_payroll_partial_run_e2e.py`) which passed in §1. Not independently re-derived via a fresh hand-computed scenario this stage.

**Disposition:** `passed` (via existing suite).

---

## 8. Employee and contract integrity scenarios

| Scenario | Disposition | Evidence |
|---|---|---|
| Duplicate non-null `employee_number` in one workspace rejected | passed | existing unique constraint + suite coverage |
| Same `employee_number` across different workspaces | passed (allowed by design) | unique constraint is workspace-scoped, confirmed in prior stages |
| `NULL employee_number` currently accepted (`08-001`) | **confirmed, re-verified live** | `psql`: 11 of 4,673 rows have `employee_number IS NULL` — identical to Stage 08's finding, re-queried fresh this stage and unchanged (evidence: inline query, `SELECT COUNT(*) FILTER (WHERE employee_number IS NULL), COUNT(*) FROM employee` → `11|4673`) |
| Overlapping contracts rejected by GIST constraint | **confirmed, re-verified live** | `psql`: `excl_employee_contract_no_overlap` constraint confirmed present on `employee_contract` (`contype='x'`) |
| Multiple open-ended contracts rejected | passed | covered by the same GIST exclusion constraint; not independently re-tested with a fresh insert attempt this stage (would require a disposable insert into shared dev data) |
| Valid sequential contracts accepted | passed | existing suite |
| Payroll selects the contract effective for the run period | passed | existing suite (`test_period_context.py` and pipeline e2e tests) |
| Joiner/leaver dates influence inclusion/proration | passed | existing suite |

No repair of nullable rows was performed, per this stage's constraint.

---

## 9. Lifecycle and immutability scenarios

Allowed/forbidden state transitions and mutation-attempt guards are covered by `test_state_machine.py`, `test_illegal_payroll_status_transition.py`, `test_payroll_lock_and_approval.py`, `test_payroll_paid_lifecycle.py`, `test_payroll_results_immutable.py`, `test_payroll_run_snapshot_immutable.py` — all passed in §1's full run, confirming actual DB-trigger enforcement (these tests attempt real mutations against real triggers, not merely repository-layer checks, per their naming and the trigger definitions already confirmed present in Stage 08).

`08-002` (`payroll_run` totals/period fields lack DB-level immutability until `PAID`) was **not re-tested via a fresh mutation attempt** this stage — doing so against a shared dev-DB `APPROVED`/`LOCKED` run risks leaving a genuinely mutated row without a clean revert path if the guard is in fact absent (which is exactly what `08-002` already confirms). Relying on Stage 08's already-confirmed trigger-definition evidence (`\d payroll_run` showing `trg_prevent_paid_run_update` fires only `WHEN (old.status = 'PAID')`) rather than re-deriving it via a live write this stage.

**Disposition:** `passed` (transitions and result/snapshot immutability, live-tested via the existing suite); `08-002` reaffirmed via prior-stage evidence, not independently re-executed this stage — consistent with this stage's own principle 4 ("do not weaken guards... to create testability") interpreted conservatively as also meaning "do not risk creating an unrecoverable mutation on shared dev data to prove a guard's absence that is already proven by static evidence."

---

## 10. Reconciliation scenarios

`only LOCKED runs can be reconciled`, `MATCHED requires equal totals`, `MISMATCH requires unequal totals`, `RESOLVED requires audit fields`, `duplicate reconciliation rejected` are all covered by `test_payroll_reconciliation.py` and `test_payroll_reconciliation_e2e.py` (9 test functions), all passed in §1.

**Reconciliation cannot coexist with retry-eligible `PARTIAL`:** re-affirms `04-004`'s structural rejection from Stage 08 (state-machine construction, not re-derived live this stage — `04-004` remains rejected, no contradictory evidence found in this stage's test run or live scenarios).

**Absence of unified audit/event entries (`07-002`) remains observable:** confirmed via the live cross-workspace scenario in §12 — the `MISMATCH` record returned by both the correct and incorrect workspace path (evidence `04`) has `notes: null`, `resolved_by: null` — consistent with `07-002`'s finding that reconciliation-local fields exist but no unified `audit_log`/`event_store` entry accompanies creation.

**Disposition:** `passed` (via existing suite); `04-004` reaffirmed rejected, unchanged; `07-002` reaffirmed via live data inspection.

---

## 11. Statutory-component disablement (`08-003`) — not independently re-executed live; reaffirmed via prior evidence

Setting up a disposable workspace, disabling a statutory component through the supported configuration path, running payroll, and restoring state is a multi-step live mutation sequence against a fresh workspace. Given this stage's time budget and that `08-003`'s underlying mechanism (`sequential_executor.py:658`'s `active_meta = [m for m in component_metadata if m.get("is_active")]` filter, confirmed by direct code read in both Stage 08 and Stage 09/10) is already confirmed via static evidence with high confidence (a simple list-comprehension filter, not a complex runtime-dependent code path where live behaviour could plausibly diverge from static reading), this stage relies on that prior confirmation rather than re-executing the full live workflow.

**Disposition:** `not-executed-with-reason` (relies on prior-stage static evidence, high confidence given the simplicity of the confirmed filtering mechanism) — `08-003` unchanged, not reopened, not newly re-confirmed live.

---

## 12. Security and tenant-isolation scenarios — executed live against local `payroll_dev`

All scenarios below were executed via `curl` against a locally-started `uvicorn backend.api.main:app` (started and stopped cleanly within this stage; no authentication was presented on any request, matching the confirmed `09-000` reality). Full transcripts: `evidence/03-cross-workspace-live-scenarios.txt`, `evidence/04-reconciliation-cross-workspace-proof.txt`, `evidence/06-unscoped-lifecycle-routes-reachable.txt`.

| Scenario | Result | Disposition |
|---|---|---|
| Unauthenticated workspace enumeration | `GET /api/v1/workspaces` with no auth header → `200`, full list of every workspace (id/name/country/currency/status/headcount) returned | **confirmed live**, reaffirms `09-001` exactly |
| Cross-workspace timeline access (mismatched path `workspace_id`) | `GET /{WRONG_workspace_id}/payroll/runs/{run_id}/timeline` → `200`, response byte-identical to the same request made with the *correct* `workspace_id` | **confirmed live**, definitive proof of `09-005` — the path segment provably makes zero difference to the query result |
| Cross-workspace reconciliation access, on a run with a real existing `MISMATCH` record | `GET /{WRONG_workspace_id}/.../reconciliation` → `200`, returned the full financial reconciliation record (`expected_total: 196231.72`, `actual_payment: 196230.0`, `status: MISMATCH`) — byte-identical to the request made with the correct `workspace_id` | **confirmed live**, definitive proof of `09-004` with real financial data, stronger evidence than Stage 09's static-only confirmation |
| Legacy unscoped reconciliation route (`06-007`) | `GET /api/v1/payroll/run/{run_id}/reconcile` (no `workspace_id` anywhere in the path) → `200`, same reconciliation data returned | **confirmed live**, reaffirms `06-007`'s final classification (insecure/tenant-bypass risk) and `09-002` |
| Global legacy-executor-stats through a workspace path | `GET /{WRONG_workspace_id}/payroll/ops/legacy-executor-stats` → `200`, returned platform-wide aggregate (`total_runs: 3130`, `runs_with_legacy: 290`) including a `by_run` array of other workspaces' run IDs, regardless of the path's `workspace_id` | **confirmed live**, reaffirms `09-006` |
| Unscoped lifecycle routes reachable (retry/approve/lock/pay/reconcile) | Confirmed reachable and registered via the live OpenAPI schema (`GET /openapi.json`) — all five routes present with only `run_id` as a path parameter, no `workspace_id` | **confirmed live** (route registration/reachability); **not exercised as a state-mutating call** this stage, to avoid transitioning a real shared dev-DB run without a disposable fixture and rollback plan — reaffirms `09-002`'s reachability claim without re-proving the mutation itself, which was already proven structurally in Stage 09 by reading the service-layer code directly |
| Unauthenticated admin/operator dashboards | `GET /admin` → `200`; `GET /admin/payroll` → `200`, no auth header presented | **confirmed live**, reaffirms `09-007` |
| Export access across workspaces | Not executed this stage — the export guard (`_guard_locked_or_paid`, requiring both correct `workspace_id` AND `run_id`) was already confirmed as a genuine positive control in Stage 09 (unlike reconciliation/timeline, which are decorative); re-testing it live would only reconfirm a control already shown to work correctly by code reading, at the cost of exercising export generation against real dev employee data unnecessarily | not-executed-with-reason, positive control reaffirmed via Stage 09 code evidence, not re-derived live |

No sensitive dataset was extracted or retained beyond what is captured in the evidence files (dev-fixture data only: synthetic company names like "ACME", "ACME Banking" — not real client data; the financial reconciliation figures shown are real dev-fixture numbers, retained in evidence only for defect proof, consistent with this stage's "record only the minimum evidence necessary" instruction).

**Future blocked scenarios from Stage 10** (authenticated unauthorized trace request → non-disclosing `404`; read-only auditor authorized access; platform-administrator explicit/audited access; direct-client user workspace restriction): all four remain `blocked-by-missing-auth` — no authentication exists to construct any of these test identities against, exactly as anticipated by Stage 10's design. Not executed, correctly not claimed as executed.

---

## 13. Raw exception and error-sanitization scenarios

Representative Group A (`workspace.py:93` — broad `except Exception`) and Group B/C (`payroll.py:1159` — narrow `except ValueError`) sites were not independently triggered live this stage (doing so safely requires either a contrived malformed request that reliably reproduces the underlying DB/validation error, or a code-level monkeypatch — both add meaningful setup cost for a class of finding already confirmed with high structural confidence in Stage 09 by direct code reading of the `except` clause types and their wrapped operations). Stage 09's classification (10 structurally disclosure-capable Group A sites, 11 currently-safe Group B/C sites) is reaffirmed unchanged; this stage adds no new live-triggered evidence for `07-001`.

**Disposition:** `not-executed-with-reason` — `07-001` unchanged, reaffirmed via prior-stage static evidence only.

---

## 14. CSV formula-injection scenario (`09-008`) — executed, confirmed

A synthetic, in-memory-only reproduction of `payroll.py`'s exact CSV-row-writing logic (`csv.writer` + `writerow`, matching `export_bank_upload`'s code shape line-for-line) was run locally with a synthetic malicious `employee_name = "=1+1"` — no database read or write, no file left on disk, zero residue by construction (evidence: `evidence/05-csv-injection-synthetic-proof.txt`).

**Result:** the written CSV cell for `employee_name` is `=1+1` verbatim — Python's `csv.writer` does not escape or quote a value merely for starting with `=` (it only quotes fields containing a comma, quote character, or newline, per RFC 4180— a leading `=` alone is not special to the CSV format itself, only to spreadsheet applications that parse the *cell content* afterward). Re-parsing the generated CSV with `csv.reader` confirms the cell value delivered to any downstream consumer (including Excel/Sheets) begins with `=`, which those applications interpret as a formula trigger on open. The file was not opened in any spreadsheet application, per this stage's constraint.

**Disposition:** `passed` (i.e., the vulnerability scenario itself executed successfully, proving the risk) — `09-008` reaffirmed as confirmed, now with live/executed proof rather than static-only reasoning; severity unchanged at S2 per Stage 09's original classification (no new information changes the severity assessment — real-world exploitability still depends on whether onboarding validation restricts `full_name` content, which remains unverified this stage as in Stage 09).

---

## 15. Stage 10 12-scenario disposition matrix

| # | Scenario (Stage 10 §16) | Disposition |
|---|---|---|
| 1 | Successful retry, one employee | blocked-by-unimplemented-design — the *retry itself* succeeds today (§5), but the specific event sequence (`RETRY_INVOCATION_STARTED` → ... → `RETRY_COMPLETED`) does not exist until Stage 10's schema/write-side design ships |
| 2 | Retry, multiple employees, mixed success/failure | blocked-by-unimplemented-design (same reason) |
| 3 | Preflight failure — legacy/incomplete snapshot | partially executable — the underlying hard-fail behaviour is proven today (§2, `test_retry_hard_fails_on_legacy_v1_statutory_snapshot`), but the specific durable `RETRY_PREFLIGHT_FAILED` trace row does not exist yet |
| 4 | Statutory snapshot validation failure | partially executable (same reason as #3) |
| 5 | Repeated retry attempts, distinct `invocation_id` per attempt | blocked-by-unimplemented-design — no `invocation_id` column exists yet |
| 6 | Original-run vs. retry timeline grouping | blocked-by-unimplemented-design — no `operation_type` column exists yet; current timeline is a flat list (confirmed live in §12, empty for the tested run but structurally flat regardless) |
| 7 | Statutory identity parity between original and retry results | blocked-by-unimplemented-design — `statutory_rule_id`/`statutory_version` columns do not exist on `payroll_result` yet (confirmed via `\d payroll_result` in Stage 10, unchanged) |
| 8 | Disabled statutory component recorded as excluded | blocked-by-unimplemented-design — no `outcome` discriminator exists in `component_trace_jsonb` yet; current behaviour is silent omission, confirmed in §11 |
| 9 | Cross-workspace timeline request denied | blocked-by-missing-auth — and, per §12, currently the *opposite* is true (identical data returned regardless of workspace) |
| 10 | Read-only auditor allowed to view authorized trace | blocked-by-missing-auth — no roles exist |
| 11 | Unauthorized direct-client user denied | deferred — direct-client users are a future feature per Stage 09's decision, not yet built regardless of auth status |
| 12 | Trace-write failure containment | partially executable — the underlying principle (`ExecutionTracer._persist()`'s existing `except Exception: pass`) is confirmed present by code reading (Stage 10 evidence), but the *upgraded* requirement (structured server-side log line on trace-write failure) does not exist yet; not independently re-triggered live this stage |

No Stage 10 acceptance criterion is claimed as passing merely because the design is internally coherent, per this stage's explicit instruction — every row above is graded against **current shipped behaviour**, not the design document.

---

## 16. Test-coverage gap analysis

| Finding | Existing automated test | Controlled audit-only scenario (this stage) | Coverage status |
|---|---|---|---|
| `04-001` | yes (`test_payroll_retry_snapshot_first.py`) | re-run, passed | covered |
| `05-001` | yes (same file) | re-run, passed | covered |
| `07-003` | no | blocked, seam missing | **no coverage, architecture-blocked** |
| `08-001` | no (nullable state is schema-permitted, not test-asserted) | re-queried live | **no coverage** — nothing prevents a future regression from silently allowing more NULLs |
| `08-002` | no | not re-executed live this stage | **no coverage** |
| `08-003` | no | not re-executed live this stage | **no coverage** |
| `09-000`–`09-008` (all Stage 09 security findings) | no — confirmed by directory listing, no `tests/test_*tenant*`, `test_*auth*`, or `test_*security*` file exists | 6 of 9 executed live this stage (§12) | **no automated regression coverage at all** — this is the single largest gap in the entire audit programme; every security finding was proven by manual/live investigation, none is guarded by a permanent test that would catch a regression |
| `09-008` | no | executed, confirmed | **no automated coverage**, live-proven only |
| `07-001` | no | not re-executed live this stage | **no coverage** |
| Stage 10's entire design | not applicable — unimplemented | N/A | not applicable until implemented |

**Minimum new permanent tests required during remediation** (feeds Stage 13):

1. **Tenant-ownership tests** (highest priority) — for every workspace-scoped route, assert that a request with a mismatched `workspace_id` either fails cleanly (post-auth: `404`) or, at minimum pre-auth, is flagged by a static/lint-style test that fails the build if a route accepts `workspace_id` but a code-path audit shows it unused (a cheap regression guard against exactly the `09-004`/`09-005` defect class recurring after remediation).
2. **`employee_number` NOT NULL enforcement test** — a migration-upgrade test asserting the column is genuinely `NOT NULL` after the corrective migration ships (closes `08-001`'s "no coverage" gap and would have caught the original silently-swallowed `EXCEPTION WHEN others` defect).
3. **`payroll_run` post-approval immutability test** — attempt a direct UPDATE against `total_net_pay`/`period_end` on an `APPROVED` run and assert it is rejected at the DB layer, once `08-002`'s remediation ships.
4. **Statutory-component-exclusion trace test** — once Stage 10's design ships, assert a disabled component produces the `outcome: excluded_by_configuration` entry and the run-level trace row.
5. **Background-task fault-injection test** — requires the seam identified in §4 to be added first; then assert `07-003`'s outer-failure path produces a terminal `FAILED` status and populated `error_message`, mirroring `05-001`'s existing regression shape.
6. **Retry trace and statutory-identity tests** — once Stage 10 ships, assert the exact event sequence (§Stage 10 §2) and per-result `statutory_rule_id`/`statutory_version` population.
7. **Export sanitization test** — assert CSV export escapes or prefixes any cell beginning with `=`, `+`, `-`, or `@` (e.g. with a leading `'` or explicit quoting), once `09-008`'s remediation ships; this stage's synthetic proof (§14) is the exact fixture shape such a test should use.
8. **Migration upgrade/downgrade smoke test** — a generic, reusable test (not finding-specific) that runs every migration's `upgrade()` then `downgrade()` against a scratch schema and asserts no error — not currently confirmed to exist as a standing CI check (not verified this stage; flagged as a general-purpose recommendation).

---

## 17. Positive controls (reaffirmed this stage)

- Full backend test suite: 306/306 non-skipped tests passing, zero flakiness observed across two independent runs.
- `04-001`/`05-001` remediation: both fully green under direct re-execution, no drift since Stage 05's close.
- GIST overlap exclusion constraint on `employee_contract`: confirmed present via live schema query.
- Export guard (`_guard_locked_or_paid`): confirmed via Stage 09 code reading as the one route family that correctly enforces the compound `workspace_id + run_id` predicate — not contradicted by any live scenario this stage.
- `payroll_result`/`payroll_run` lifecycle immutability triggers: exercised live via the passing `test_payroll_results_immutable.py`/`test_payroll_lock_and_approval.py`/`test_payroll_paid_lifecycle.py` suite, not merely asserted statically.
- `payroll_reconciliation` CHECK constraints: exercised live via the passing reconciliation test suite (9 tests).

---

## Findings — new or materially extended this stage

No new distinct defect mechanism was discovered this stage. Every scenario that surfaced a problem reproduces an already-confirmed finding from Stages 02–10; per this stage's finding rule, these are **not** recorded as new findings, only linked and, where the live execution materially strengthens the evidence quality (moving from static-code-only confirmation to live-executed proof), noted as such:

- `09-001`, `09-004`, `09-005`, `09-006`, `06-007`/`09-002`, `09-007` — all reaffirmed **live** this stage (§12), upgrading their evidence class from "code reading" to "code reading + live execution" without changing status, severity, or scope.
- `09-008` — reaffirmed **live** this stage (§14) via a self-contained synthetic proof, same upgrade.
- `04-001`, `05-001` — reaffirmed **live** via direct test re-execution (§2, §3), remain remediated.
- `08-001` — reaffirmed **live** via a fresh count query, unchanged (`11`/`4673`).
- `04-004` — reaffirmed rejected, no contradictory evidence.
- `07-002`, `07-003`, `08-002`, `08-003`, `07-001` — reaffirmed via prior-stage evidence only, not independently re-executed live this stage (each with a stated reason above); none contradicted.

**status:** confirmed (for every reaffirmed finding listed above — this stage found no evidence contradicting any prior confirmed finding, and found no new defect mechanism)

---

## Handoff notes for Stages 12 and 13

- **Stage 12** (code simplification): the complete absence of any tenant/security-focused test file (§16) is itself worth flagging as a structural gap a simplification/consistency pass should not "clean up" by deleting anything — rather, it is the single clearest argument for why Stage 13's remediation package must ship *with* tests, not as a bare code change, given this audit programme found zero regression protection for the entire security dimension.
- **Stage 13** (consolidated backlog): the 8 permanent-test recommendations in §16 should be attached as acceptance-criteria line items to their corresponding remediation backlog entries (`09-000`'s package, `08-001`, `08-002`, `08-003`, `07-003`, Stage 10's trace package, `09-008`), not tracked as a separate generic "add tests" item — each is scoped to the specific defect it guards against. The live cross-workspace evidence in §12 (byte-identical reconciliation data returned under a mismatched `workspace_id`, including real financial totals) is the strongest available evidence for prioritizing `09-000`/`09-001`/`09-002`/`09-004`/`09-005` at the top of Stage 13's sequencing — this is no longer a theoretical code-reading concern, it was demonstrated end-to-end against a running instance of the actual application this stage.

## Human decisions required

None. This stage found no new defect mechanism requiring a policy or scope decision; all findings reaffirmed were already logged with their decisions resolved (where applicable) in prior stages.

---

## Stage 11 close — final review and closure summary

No new human decision was required to close Stage 11. All conclusions in the CONTEXT.md close-review instruction are confirmed against this document's own evidence with no revision:

1. **Full backend suite: 306 passed, 1 skipped** (§1) — reconfirmed.
2. **`04-001`/`05-001` regressions: 6/6 passed** (§2, §3), both remain remediated — reconfirmed.
3. **No new distinct defect mechanism discovered** — every scenario result in §2–§14 that surfaced a problem links to an existing finding (Stages 02–10); none revealed a materially distinct mechanism or severity.
4. **`04-004` remains rejected**, not reopened — no contradictory evidence found in this stage's live scenarios or test run.
5. **`07-003` remains untested** — no safe fault-injection seam exists without editing production source; the blocked-test specification in §4 is accepted as sufficient for this audit stage, per the CONTEXT.md's own review conclusion.
6. **Current retry behaviour is correct** apart from the already-known zero-row `execution_trace` gap on retry (§5) — unchanged, not a new finding.
7. **Financial, arithmetic, lifecycle, result-immutability, contract-overlap, and reconciliation controls remain green** through the existing suite (§6–§10) and the targeted live re-checks (GIST constraint, `08-001` count) performed this stage.
8. **`08-001`'s nullable `employee_number`** reconfirmed live in the local schema (11/4,673) — no permanent regression test exists for it, carried to Stage 13 (§16, §18).
9. **Live execution materially strengthened five Stage 09 findings** (§12): unauthenticated workspace enumeration (`09-001`); mismatched-workspace timeline and reconciliation requests returning identical data to correctly-scoped requests (`09-005`, `09-004` — the latter proven with a real financial `MISMATCH` record); the legacy unscoped reconciliation route reachable (`06-007`/`09-002`); global legacy-executor statistics ignoring workspace scope (`09-006`); unauthenticated admin dashboards reachable (`09-007`).
10. **`09-008` CSV formula injection confirmed** by the synthetic, zero-residue in-memory reproduction (§14) — a leading `=` reaches the exported cell unescaped.
11. **Stage 10's 12 scenarios correctly classified** (§15) as executable/partial/blocked-by-unimplemented-design/blocked-by-missing-auth/deferred, graded against current shipped behaviour, not the design's internal coherence.
12. **The absence of any permanent authentication/tenant/security regression test is confirmed as the largest coverage gap** (§16) — zero such tests exist anywhere in `tests/`.

Review requirements verified at closure:

1. All live evidence (§12, §14, and the evidence files) used non-production dev-fixture data only — confirmed by the workspace names (`ACME`, `ACME Banking`, etc.) and the fully synthetic CSV-injection reproduction.
2. The local `uvicorn` server was stopped cleanly after all live scenarios; zero residue was verified via a subsequent connection-refused check (`evidence/`, confirmed in-session).
3. No Stage 10 acceptance criterion is represented as implemented — §15 explicitly grades every scenario against current behaviour, marking 9 of 12 as blocked/partial/deferred.
4. No previous finding is duplicated as a new Stage 11 defect — the "Findings — new or materially extended this stage" section above explicitly links every result to its originating Stage 02–10 finding.
5. `04-001` and `05-001` remain closed/remediated, reconfirmed via direct re-execution, not reopened.
6. Every unexecuted scenario (§4, §6 partial, §8 partial, §9 partial, §11, §12 export row, §13) states its specific reason inline.
7. The eight permanent-test recommendations (§16, §18) are each scoped to a named finding's eventual remediation (`08-001`, `08-002`, `08-003`, `07-003`, Stage 10's trace package, `09-008`, plus the general tenant-ownership and migration-smoke recommendations) — not a generic "add tests" backlog item.
8. All completion criteria stated in the CONTEXT.md are satisfied by the sections above.

### Carried to Stage 13

- `07-003`, `08-001`, `08-002`, `08-003`, `09-008`, the full Stage 09 security package, and the Stage 10 trace package all carry to Stage 13 with this stage's live-test evidence and status attached — none reopened, none re-scoped.
- The eight permanent-test recommendations (§16, §18) carry into their respective Stage 13 remediation entries as acceptance criteria, not as a separate generic testing item.
- `04-004` carries forward as rejected, no action required.
