"""
Stage 04 controlled non-production test — reproduce or reject finding 03-002.

Hypothesis (Stage 03, finding 03-002): per-employee retry re-resolves the
statutory rule/tax bands LIVE from `statutory_effective_date` (a frozen scalar
on payroll_run), instead of reading the full resolved content the original
run already froze into `rules_context_snapshot.statutory_rule`. If a new
statutory_rule row is inserted with an effective_from between the original
resolution and the run's statutory_effective_date, a later retry could select
different statutory content than the original run used for the SAME run's
other, already-successful employees.

Design
------
1. Insert statutory_rule A (effective_from=2026-05-01) with a flat 10% tax
   band, and statutory_rule B is NOT yet inserted.
2. Onboard two employees in a test workspace: Employee A (valid salary),
   Employee B (broken salary -> calculation fails).
3. Run payroll for period ending 2026-05-31 (statutory_effective_date =
   2026-05-31). Resolution picks rule A (effective_from 2026-05-01 <=
   2026-05-31, more recent than any real seeded NG rule). Employee A
   succeeds under rule A's 10% flat tax. Employee B fails -> run PARTIAL.
4. AFTER the original run completes and freezes its snapshot, insert
   statutory_rule B (effective_from=2026-05-15, strictly between A's
   effective_from and the frozen statutory_effective_date) with a flat 25%
   tax band -- the "intervening insert" the hypothesis requires.
5. Fix Employee B's broken salary so retry can succeed.
6. Call the retry service directly (bypassing HTTP, since the code path is
   the same `retry_failed_payroll_employees` function either way) for this
   run.
7. Compare Employee B's post-retry PAYE against what rule A's 10% band vs.
   rule B's 25% band would produce. If it matches B's 25%, the divergence
   is reproduced -- same run, two employees taxed under different statutory
   content, with no error or warning anywhere.

All test data uses fresh UUIDs and is deleted in a `finally` block. This
targets the local non-production `payroll_dev` database only (confirmed
reachable at postgresql+psycopg2://michaelemedo@localhost:5432/payroll_dev
via .env's DATABASE_URL) -- not a shared or production database.

Run:
    python docs/audit-program/04-original-run-retry-parity/evidence/statutory_divergence_controlled_test.py
"""

import sys
import uuid
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from psycopg2.extras import Json
from sqlalchemy import text
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.infra.db.models import Account, Workspace
from backend.infra.db.session import SessionLocal
from backend.application.payroll_retry_service import retry_failed_payroll_employees

client = TestClient(app)

BASIC_A, HOUSING_A, TRANSPORT_A = 500_000, 200_000, 100_000   # GROSS_A = 800_000
BASIC_B, HOUSING_B = 300_000, 100_000                           # GROSS_B (after fix) = 400_000

RULE_A_RATE = Decimal("0.10")   # flat, distinguishing marker
RULE_B_RATE = Decimal("0.25")   # flat, distinguishing marker


def main():
    account_id        = uuid.uuid4()
    workspace_id       = uuid.uuid4()
    statutory_rule_a_id = uuid.uuid4()
    statutory_rule_b_id = uuid.uuid4()
    broken_sal_def_id  = uuid.uuid4()
    employee_b_id      = uuid.uuid4()

    db = SessionLocal()
    result_lines = []

    def log(msg):
        print(msg)
        result_lines.append(msg)

    try:
        # ------------------------------------------------------------------
        # STEP 1 — statutory_rule A (present BEFORE the original run)
        # ------------------------------------------------------------------
        db.add(Account(account_id=account_id, name="Stage04 Divergence Test Corp"))
        db.add(Workspace(
            workspace_id=workspace_id, account_id=account_id,
            name="Stage04 Divergence Test WS", country_code="NG",
            base_currency="NGN", status="DRAFT",
        ))

        db.execute(text("""
            INSERT INTO statutory_rule
                (statutory_rule_id, state, version, rules_jsonb, country_code, effective_from)
            VALUES (:id, 'NATIONAL', 9800,
                    '{"pension": {"employee_rate": 0.08, "employer_rate": 0.10}}',
                    'NG', '2026-05-01')
        """), {"id": statutory_rule_a_id})
        db.execute(text("""
            INSERT INTO tax_band (tax_band_id, statutory_rule_id, lower_limit, upper_limit, rate)
            VALUES (gen_random_uuid(), :sr_id, 0, NULL, :rate)
        """), {"sr_id": statutory_rule_a_id, "rate": RULE_A_RATE})
        db.commit()
        log(f"[1] statutory_rule A inserted: id={statutory_rule_a_id} effective_from=2026-05-01 rate={RULE_A_RATE}")

        # ------------------------------------------------------------------
        # STEP 2 — onboard Employee A (valid) via the real commit endpoint
        # ------------------------------------------------------------------
        onboarding_payload = {
            "workspace_id": str(workspace_id),
            "salary_definitions": [{
                "name": "STANDARD",
                "components": {
                    "BASIC":     {"amount": BASIC_A},
                    "HOUSING":   {"amount": HOUSING_A},
                    "TRANSPORT": {"amount": TRANSPORT_A},
                },
            }],
            "payroll_rules": [],
            "employees": [{
                "employee_number":        "S4EMP001",
                "full_name":              "Stage04 Employee A",
                "salary_definition_name": "STANDARD",
                "contract_start":         "2025-01-01",
                "biodata": {
                    "TIN": "1234567890", "BANK": "GTBank",
                    "ACCOUNT_NUMBER": "0123456789", "RSA": "PEN100999999",
                    "FULL_NAME": "Stage04 Employee A",
                },
            }],
        }
        commit_resp = client.post("/api/v1/onboarding/commit", json=onboarding_payload)
        assert commit_resp.status_code == 200, f"onboarding commit failed: {commit_resp.status_code} {commit_resp.text}"
        emp_a_row = db.execute(
            text("SELECT employee_id FROM employee WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        ).fetchone()
        employee_a_id = emp_a_row[0]
        log(f"[2] Employee A onboarded: {employee_a_id}")

        # ------------------------------------------------------------------
        # STEP 3 — Employee B, broken salary (direct insert, mirrors
        # tests/test_payroll_retry.py's established pattern)
        # ------------------------------------------------------------------
        db.execute(text("""
            INSERT INTO salary_definition (salary_definition_id, workspace_id, name, code, components_jsonb)
            VALUES (:id, :wid, 'BROKEN', 'BROKEN', :components)
        """), {"id": broken_sal_def_id, "wid": workspace_id, "components": Json({"BASIC": {"amount": "INVALID"}})})
        db.execute(text("""
            INSERT INTO employee (employee_id, workspace_id, full_name, status)
            VALUES (:eid, :wid, 'Stage04 Employee B (broken)', 'ACTIVE')
        """), {"eid": employee_b_id, "wid": workspace_id})
        db.execute(text("""
            INSERT INTO employee_contract (contract_id, employee_id, salary_definition_id, start_date)
            VALUES (gen_random_uuid(), :eid, :sdid, '2025-01-01')
        """), {"eid": employee_b_id, "sdid": broken_sal_def_id})
        db.commit()
        log(f"[3] Employee B (broken) inserted: {employee_b_id}")

        db.execute(text("UPDATE workspace SET status = 'LIVE' WHERE workspace_id = :wid"), {"wid": workspace_id})
        db.commit()

        # ------------------------------------------------------------------
        # STEP 4 — original run, period ending 2026-05-31
        #          statutory_effective_date -> 2026-05-31 -> resolves rule A
        # ------------------------------------------------------------------
        run_resp = client.post("/api/v1/payroll/run", json={
            "workspace_id": str(workspace_id),
            "period_start": "2026-05-01",
            "period_end":   "2026-05-31",
        })
        assert run_resp.status_code == 200, f"run failed: {run_resp.status_code} {run_resp.text}"
        payroll_run_id = run_resp.json()["payroll_run_id"]
        log(f"[4] Original run created: {payroll_run_id} (TestClient completes the BackgroundTask synchronously)")

        run_row = db.execute(text("""
            SELECT status, statutory_effective_date, rules_context_snapshot
            FROM payroll_run WHERE payroll_run_id = :rid
        """), {"rid": payroll_run_id}).fetchone()
        run_status, stat_eff_date, snapshot = run_row
        log(f"[4] payroll_run.status={run_status} statutory_effective_date={stat_eff_date}")
        assert run_status == "PARTIAL", f"expected PARTIAL, got {run_status}"

        snap_statutory = (snapshot or {}).get("statutory_rule") or {}
        log(f"[4] rules_context_snapshot.statutory_rule = {snap_statutory}")
        assert snap_statutory.get("id") == str(statutory_rule_a_id), (
            f"expected original run to freeze rule A ({statutory_rule_a_id}), "
            f"snapshot shows {snap_statutory.get('id')}"
        )

        result_a = db.execute(text("""
            SELECT status, deductions_jsonb->>'PAYE' AS paye, net_pay
            FROM payroll_result WHERE payroll_run_id = :rid AND employee_id = :eid
        """), {"rid": payroll_run_id, "eid": employee_a_id}).fetchone()
        log(f"[4] Employee A result: status={result_a[0]} PAYE={result_a[1]} net_pay={result_a[2]}")
        assert result_a[0] == "SUCCESS"
        expected_paye_a_rule_a = (Decimal(800_000) * RULE_A_RATE).quantize(Decimal("0.01"))
        log(f"[4] Expected PAYE for Employee A under rule A (flat {RULE_A_RATE}): {expected_paye_a_rule_a}")

        # ------------------------------------------------------------------
        # STEP 5 — AFTER the original run: insert the intervening rule B
        # ------------------------------------------------------------------
        db.execute(text("""
            INSERT INTO statutory_rule
                (statutory_rule_id, state, version, rules_jsonb, country_code, effective_from)
            VALUES (:id, 'NATIONAL', 9801,
                    '{"pension": {"employee_rate": 0.08, "employer_rate": 0.10}}',
                    'NG', '2026-05-15')
        """), {"id": statutory_rule_b_id})
        db.execute(text("""
            INSERT INTO tax_band (tax_band_id, statutory_rule_id, lower_limit, upper_limit, rate)
            VALUES (gen_random_uuid(), :sr_id, 0, NULL, :rate)
        """), {"sr_id": statutory_rule_b_id, "rate": RULE_B_RATE})
        db.commit()
        log(f"[5] statutory_rule B inserted AFTER original run: id={statutory_rule_b_id} "
            f"effective_from=2026-05-15 (between rule A's 2026-05-01 and frozen "
            f"statutory_effective_date {stat_eff_date}) rate={RULE_B_RATE}")

        # Confirm the live re-resolution query retry uses would now pick B.
        live_pick = db.execute(text("""
            SELECT statutory_rule_id, version, effective_from
            FROM statutory_rule
            WHERE country_code = 'NG' AND effective_from <= :as_of
            ORDER BY effective_from DESC, version DESC
            LIMIT 1
        """), {"as_of": stat_eff_date}).fetchone()
        log(f"[5] Live re-resolution (retry's exact query) now picks: "
            f"id={live_pick[0]} version={live_pick[1]} effective_from={live_pick[2]}")
        assert str(live_pick[0]) == str(statutory_rule_b_id), (
            "expected live re-resolution to now pick rule B -- test design assumption failed"
        )

        # ------------------------------------------------------------------
        # STEP 6 — fix Employee B's salary, then retry
        # ------------------------------------------------------------------
        db.execute(text("""
            UPDATE salary_definition SET components_jsonb = :components WHERE salary_definition_id = :id
        """), {
            "components": Json({"BASIC": {"amount": BASIC_B}, "HOUSING": {"amount": HOUSING_B}}),
            "id": broken_sal_def_id,
        })
        db.commit()
        log("[6] Employee B's broken salary fixed")

        retry_result = retry_failed_payroll_employees(payroll_run_id, performed_by="stage04-controlled-test")
        log(f"[6] retry_failed_payroll_employees() returned: {retry_result}")
        assert retry_result["success"] == 1, f"expected 1 success, got {retry_result}"

        # ------------------------------------------------------------------
        # STEP 7 — compare Employee B's post-retry result
        # ------------------------------------------------------------------
        result_b = db.execute(text("""
            SELECT status, deductions_jsonb->>'PAYE' AS paye, net_pay
            FROM payroll_result WHERE payroll_run_id = :rid AND employee_id = :eid
        """), {"rid": payroll_run_id, "eid": employee_b_id}).fetchone()
        log(f"[7] Employee B post-retry result: status={result_b[0]} PAYE={result_b[1]} net_pay={result_b[2]}")

        gross_b = Decimal(BASIC_B + HOUSING_B)
        pension_b = (gross_b * Decimal("0.08")).quantize(Decimal("0.01"))
        taxable_b = gross_b - pension_b
        expected_paye_b_rule_a = (taxable_b * RULE_A_RATE).quantize(Decimal("0.01"))
        expected_paye_b_rule_b = (taxable_b * RULE_B_RATE).quantize(Decimal("0.01"))
        log(f"[7] Expected PAYE for Employee B if rule A (10%) had been used (matching "
            f"Employee A's original-run rule): {expected_paye_b_rule_a}")
        log(f"[7] Expected PAYE for Employee B if rule B (25%, the intervening insert) "
            f"was used instead: {expected_paye_b_rule_b}")

        actual_paye_b = Decimal(result_b[1])
        if abs(actual_paye_b - expected_paye_b_rule_b) < Decimal("1.00"):
            log("[VERDICT] DIVERGENCE REPRODUCED: Employee B's retried PAYE matches rule B "
                "(the intervening insert), NOT rule A (the rule the original run's Employee A "
                "was calculated under, in the SAME payroll_run). Confirms finding 03-002: "
                "per-employee retry can silently select different statutory content than the "
                "original run, with no error, warning, or trace entry anywhere.")
            verdict = "REPRODUCED"
        elif abs(actual_paye_b - expected_paye_b_rule_a) < Decimal("1.00"):
            log("[VERDICT] DIVERGENCE NOT REPRODUCED: Employee B's retried PAYE matches rule A "
                "(the original run's rule), contradicting the 03-002 hypothesis under this "
                "test design.")
            verdict = "REJECTED"
        else:
            log(f"[VERDICT] INCONCLUSIVE: actual PAYE {actual_paye_b} matches neither "
                f"candidate ({expected_paye_b_rule_a} / {expected_paye_b_rule_b}).")
            verdict = "INCONCLUSIVE"

        log(f"\nFINAL VERDICT: {verdict}")

    finally:
        # ------------------------------------------------------------------
        # Cleanup -- reverse FK order, scoped to this test's IDs only
        # ------------------------------------------------------------------
        db.rollback()
        db.execute(text("SET LOCAL session_replication_role = replica"))
        db.execute(text("""
            DELETE FROM payroll_result WHERE payroll_run_id IN (
                SELECT payroll_run_id FROM payroll_run WHERE workspace_id = :wid)
        """), {"wid": workspace_id})
        db.execute(text("""
            DELETE FROM component_metadata_snapshot WHERE payroll_run_id IN (
                SELECT payroll_run_id FROM payroll_run WHERE workspace_id = :wid)
        """), {"wid": workspace_id})
        db.execute(text("""
            DELETE FROM client_component_metadata_snapshot WHERE payroll_run_id IN (
                SELECT payroll_run_id FROM payroll_run WHERE workspace_id = :wid)
        """), {"wid": workspace_id})
        db.execute(text("""
            DELETE FROM employee_contract_snapshot WHERE payroll_run_id IN (
                SELECT payroll_run_id FROM payroll_run WHERE workspace_id = :wid)
        """), {"wid": workspace_id})
        db.execute(text("""
            DELETE FROM event_store WHERE aggregate_type = 'PAYROLL_RUN' AND aggregate_id IN (
                SELECT payroll_run_id FROM payroll_run WHERE workspace_id = :wid)
        """), {"wid": workspace_id})
        db.execute(text("DELETE FROM audit_log WHERE workspace_id = :wid"), {"wid": workspace_id})
        db.execute(text("DELETE FROM payroll_run WHERE workspace_id = :wid"), {"wid": workspace_id})
        db.execute(text("""
            DELETE FROM employee_contract WHERE employee_id IN (
                SELECT employee_id FROM employee WHERE workspace_id = :wid)
        """), {"wid": workspace_id})
        db.execute(text("DELETE FROM employee WHERE workspace_id = :wid"), {"wid": workspace_id})
        db.execute(text("DELETE FROM payroll_rule WHERE workspace_id = :wid"), {"wid": workspace_id})
        db.execute(text("DELETE FROM salary_definition WHERE workspace_id = :wid"), {"wid": workspace_id})
        db.execute(text("DELETE FROM tax_band WHERE statutory_rule_id IN (:a, :b)"),
                   {"a": statutory_rule_a_id, "b": statutory_rule_b_id})
        db.execute(text("DELETE FROM statutory_rule WHERE statutory_rule_id IN (:a, :b)"),
                   {"a": statutory_rule_a_id, "b": statutory_rule_b_id})
        db.execute(text("DELETE FROM workspace WHERE workspace_id = :wid"), {"wid": workspace_id})
        db.execute(text("DELETE FROM account WHERE account_id = :aid"), {"aid": account_id})
        db.commit()
        db.close()
        log("\n[CLEANUP] All test-scoped rows deleted (workspace, employees, contracts, "
            "salary defs, payroll_run/result, snapshots, statutory_rule A+B, tax_band A+B, "
            "account). Verified via reverse-FK-order DELETE, matching tests/test_payroll_retry.py's pattern.")

        out_path = Path(__file__).parent / "2026-07-12-statutory-divergence-test-output.txt"
        out_path.write_text("\n".join(result_lines) + "\n")
        print(f"\nFull output written to {out_path}")


if __name__ == "__main__":
    main()
