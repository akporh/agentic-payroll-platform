# Test Harness — Progress Checklist

Workstream started 2026-07-11. Goal: turn the existing 287-test suite into a
real harness — green, gap-checked against known bugs, and running automatically.

## 1. Baseline ✅

- [x] Run full pytest suite (287 collected)
- [x] Record baseline report → `docs/test-reports/2026-07-11-test-harness-baseline.md`
- [x] Classify failures — all 4 are stale async-contract e2e tests (TF-7 class), zero calculation-path failures

## 2. Triage & fix failing tests ✅

- [x] Rewrite `test_full_payroll_pipeline_e2e` — assert async contract (DRAFT + run_id), verify counts/totals from persisted state
- [x] Rewrite `test_payroll_approval_and_lock_e2e` (same fix)
- [x] Rewrite `test_partial_payroll_run_e2e` (same fix)
- [x] Rewrite `test_payroll_retry_e2e` (same fix)
- [x] Full suite green — 286 passed, 0 failed, 1 documented Phase-2 skip

*Note: no polling needed — Starlette's TestClient runs BackgroundTasks to
completion before `client.post()` returns, so persisted state is final
immediately. Tests now assert the DB state (CALCULATED/PARTIAL + result rows),
matching how the passing e2e tests were already written.*

## 3. Regression coverage audit (known-bug memory) ✅

- [x] Proration: mid-period hires + `end_date` inclusive semantics — **COVERED** (`test_period_context.py`: mid-month hire, hire+termination same period, single-day hire, 28-day Feb, strategy comparison)
- [x] `overrides_json` destruction in `patch_component_override` — **GAP** (zero tests; memory flags this as CRITICAL — patch destroys NHF/Health/Levy rates if `overrides_json` absent from payload)
- [x] `payroll_rule.is_active` vs date-driven `effective_from` resolution — **PARTIAL** (display path covered by 3 tests in `test_payroll_input_codes_route.py` inc. the Sprint A historical-rate regression; calc-path "future-dated rate excluded from current period" — Sprint A fix 3 — has no dedicated test, named as deferred in the Sprint A report)
- [x] `non_taxable` / `paye_addition` component_class invariants — **COVERED** (18 tests in `test_sprint12_m1_m2.py`)
- [x] Reconciliation MATCHED vs RESOLVED invariants — **PARTIAL** (MATCHED/MISMATCH e2e covered; `RESOLVED` appears in zero tests — operator-resolution invariant "totals may differ only via RESOLVED" unprotected)
- [x] APPROVED run immutability — **COVERED** (7 files: state machine, illegal transitions, results-immutable, lock/approval e2e)
- [x] NHF / Health / Dev Levy statutory key names — **PARTIAL** (NHF `employee_rate` covered in `test_nhf.py` + executor test "NHF = BASIC × rate, not GROSS"; Health Insurance `employee_amount` and Dev Levy `amount` have ZERO tests despite live handlers at `sequential_executor.py:419,427` — this was the F1 ₦0 key-mismatch bug class)
- [x] Upload vs Enroll separation (`grade_code` null on bulk upload) — **GAP** (rule lives in frontend `handleImport`; there are no frontend tests at all — needs a decision: frontend test harness vs backend-side guard test)
- [x] Produce gap list: covered vs uncovered → section 4 below

## 4. Write missing regression tests ✅ (T4.5 parked by decision)

Money-correctness first:

- [x] **T4.1** `patch_component_override` preserves `overrides_json` when absent from payload — 3 tests in `tests/test_component_override_patch.py`
- [x] **T4.2** Health Insurance `employee_amount` / Dev Levy `amount` keys — 4 engine tests (`TestFlatAmountStatutoryDeductions` in `test_sequential_executor.py`) + full-path e2e (`tests/test_statutory_flat_amount_keys_e2e.py`)
- [x] **T4.3** Future-dated `effective_from` excluded from resolution — 2 tests in `tests/test_resolve_effective_rules.py` (pins the shared resolver used by run, retry, and legacy fallback)
- [x] **T4.4** Reconciliation RESOLVED invariant — `test_resolve_mismatch_sets_resolved_not_matched` in `test_payroll_reconciliation_e2e.py` (RESOLVED not MATCHED, totals preserved differing, re-resolve rejected)
- [ ] **T4.5** `grade_code` null on bulk upload — PARKED: frontend-only rule, no frontend harness exists; separate decision with Michael
- [x] Each test comments the invariant it protects
- [x] `/auditor` pass — arithmetic verified, check-7 key-consistency grep passed across all 3 callers; NHF pinned to 0 in e2e fixture per audit observation

Suite after section 4: **302 passed, 0 failed, 1 documented Phase-2 skip.**

*Audit flag for a future sprint: `reconciliation_repo.py` `update_reconciliation` docstring
says "Sets status to MATCHED" but the SQL correctly sets RESOLVED — stale pre-RC5 comment.*

## 4. Write missing regression tests

- [ ] Tests written for every gap from the audit (money-correctness rules first)
- [ ] Each test comments the invariant it protects
- [ ] `/auditor` pass on statutory-calculation tests

## 5. Automation ✅

- [x] Decision: both — pre-push hook (fast local gate) + GitHub Actions (safety net)
- [x] Suite made **environment-independent**: fresh-DB validation exposed 10 tests
      silently depending on drifted dev-DB state (registry activation flips, a
      missing `employee_number` NOT NULL, a missing seeded statutory rule).
      Fixed via `tests/registry_state.py` pin/restore helper + fixture date bumps
      past the 2026-05-01 migration seed + self-healing setup in snapshot-first tests.
      Suite green on BOTH: fresh migrated DB (306) and dev DB (306).
- [x] `.github/workflows/tests.yml` — on push/PR to uat/main: Postgres 16 service,
      `alembic upgrade head` on a fresh DB, full pytest; separate frontend
      typecheck job (`npm ci` + `tsc --noEmit`)
- [x] `.githooks/pre-push` — pytest + tsc before every push
      (`git config core.hooksPath .githooks`; bypass with `--no-verify`)
- [x] Verified live (2026-07-12): pre-push hook ran the full gate locally
      (306 passed + tsc) before the push; the push triggered GitHub Actions run
      #29204759931 — both jobs green (backend 39s, frontend 19s)

## 5a. Automation ✅ — summary

The harness is live: every push to uat/main now runs the full suite twice —
once locally before the push leaves the machine, once in CI against a fresh
migrated database. A regression cannot reach the remote silently.

### Follow-up (added by decision 2026-07-12)

- [ ] **Environment drift investigation**: compare Neon production
      `component_metadata` / `statutory_rule` / `employee` constraints against
      migration truth before the uat→main merge. Dev DB is confirmed drifted
      (NHF/Health/Levy/Rent-Relief manually deactivated at platform level, extra
      CRA + TOTAL_DEDUCTIONS rows, missing `employee_number` NOT NULL, missing
      2026-05-01 statutory seed row). Production state unknown — read-only check.

## 6. Documentation & workflow ✅

- [x] "Test Harness" section added to `agentic-payroll-platform/CLAUDE.md` (run command, gates, fixture rules for new e2e tests)
- [x] `/tester` skill checklist updated (user-home SKILL.md): full suite green required before sprint close, environment-independence rules for new fixtures, CI-red = sprint not closed
- [x] Rule adopted (in both CLAUDE.md and /tester): every bug fix ships with a regression test named for the invariant it protects
- [x] `docs/ROADMAP.md` Known Test Failures table updated: TF-3–TF-7 marked resolved (2026-07-12), suite-green banner added

---

**Workstream complete** except the two parked follow-ups: T4.5 (frontend `grade_code` rule — needs a frontend-harness decision) and the production drift investigation (compare Neon against migration truth before uat→main).
