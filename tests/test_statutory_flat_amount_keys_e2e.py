"""
Regression test: statutory rules_jsonb key names for flat-amount deductions.

INVARIANT PROTECTED (T4.2 route layer — F1 bug class, money):
    The payroll run route extracts flat statutory amounts from
    statutory_rule.rules_jsonb using EXACTLY these keys:

        health_insurance.employee_amount  → Health Insurance deduction
        development_levy.amount           → Development Levy deduction

    (backend/api/routes/payroll.py — see the rules_jsonb extraction near the
    top of run_payroll.) A key mismatch anywhere in this chain does NOT error:
    it silently produces a ₦0 deduction and overpays every employee. This test
    seeds rules_jsonb through the real DB → API → engine → persistence path
    and asserts the amounts land, non-zero, in the results.

    The handler-side keys are pinned by
    tests/test_sequential_executor.py::TestFlatAmountStatutoryDeductions.

Fixture notes
-------------
- statutory_rule version=9993 (unique to this test; highest version wins
  only among rules present during the test run — 999x values are reserved
  for the e2e family).
- Same salary + tax bands as test_payroll_pipeline_e2e.py, so expected
  PAYE/pension are identical and only the two flat deductions differ:

      GROSS    = 800,000
      Pension  =  64,000 (8%)
      PAYE     = 145,226.67
      Health   =   5,000 (flat, from rules_jsonb)
      Dev Levy =   1,000 (flat, from rules_jsonb)
      NET      = 800,000 - 64,000 - 145,226.67 - 5,000 - 1,000 = 584,773.33
"""

import json
import uuid
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import text

from backend.api.main import app
from backend.infra.db.models import Account, Workspace
from backend.infra.db.session import SessionLocal
from tests.registry_state import pin_registry_state, restore_registry_state

client = TestClient(app)

BASIC     = 500_000
HOUSING   = 200_000
TRANSPORT = 100_000
GROSS     = BASIC + HOUSING + TRANSPORT   # 800_000

HEALTH_AMOUNT = 5_000
LEVY_AMOUNT   = 1_000

EXPECTED_NET = 584_773.33   # 800k - 64k - 145,226.67 - 5,000 - 1,000

RULES_JSONB = {
    "pension":          {"employee_rate": 0.08, "employer_rate": 0.10},
    # Pin NHF to 0 explicitly: the route defaults a missing nhf key to 0.025,
    # so if a registry change ever activates NHF_CONTRIBUTION this test's
    # expected NET stays valid instead of failing with a misleading message.
    "nhf":              {"employee_rate": 0},
    "health_insurance": {"employee_amount": HEALTH_AMOUNT},
    "development_levy": {"amount": LEVY_AMOUNT},
}


def test_flat_amount_keys_flow_from_rules_jsonb_to_result():
    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    statutory_rule_id     = uuid.uuid4()
    component_metadata_id = uuid.uuid4()

    db = SessionLocal()
    # The run route only loads registry components WHERE is_active = TRUE, so
    # declare the exact registry state this test's expected NET assumes:
    # both flat components active, rent relief inactive (it would lower PAYE).
    # NHF is handled via the explicit rate-0 pin in RULES_JSONB above.
    registry_prior = pin_registry_state(db, {
        "HEALTH_INSURANCE_EMPLOYEE": True,
        "DEVELOPMENT_LEVY":          True,
        "RENT_RELIEF":               False,
    })
    try:
        # --- prerequisites -------------------------------------------------
        db.add(Account(account_id=account_id, name="Flat Keys Test Corp"))
        db.add(Workspace(
            workspace_id=workspace_id,
            account_id=account_id,
            name="Flat Keys Test Workspace",
            country_code="NG",
            base_currency="NGN",
            status="DRAFT",
        ))
        db.execute(
            text("""
                INSERT INTO statutory_rule
                    (statutory_rule_id, state, version, rules_jsonb, country_code, effective_from)
                VALUES (:id, 'NATIONAL', 9993, CAST(:rules AS jsonb), 'NG', '2026-05-17')
            """),
            {"id": statutory_rule_id, "rules": json.dumps(RULES_JSONB)},
        )
        for lower, upper, rate in [
            (0,         300_000,   0.07),
            (300_000,   600_000,   0.11),
            (600_000,   1_100_000, 0.15),
            (1_100_000, 1_600_000, 0.19),
            (1_600_000, None,      0.21),
        ]:
            db.execute(
                text("""
                    INSERT INTO tax_band
                        (tax_band_id, statutory_rule_id, lower_limit, upper_limit, rate)
                    VALUES (gen_random_uuid(), :sr_id, :lower, :upper, :rate)
                """),
                {"sr_id": statutory_rule_id, "lower": lower, "upper": upper, "rate": rate},
            )
        db.execute(
            text("""
                INSERT INTO component_metadata
                    (component_metadata_id, component_code, country_code, version,
                     metadata_json, effective_from, is_active)
                VALUES (:cm_id, 'TEST_SEED', 'NG', 9993, '{}', CURRENT_DATE, true)
            """),
            {"cm_id": component_metadata_id},
        )
        db.commit()

        # --- onboard one employee ------------------------------------------
        payload = {
            "workspace_id": str(workspace_id),
            "salary_definitions": [
                {
                    "name": "STANDARD",
                    "components": {
                        "BASIC":     {"amount": BASIC},
                        "HOUSING":   {"amount": HOUSING},
                        "TRANSPORT": {"amount": TRANSPORT},
                    },
                }
            ],
            "payroll_rules": [
                {
                    "rule_code": "PENSION",
                    "rule_name": "Employee Pension",
                    "definition": {
                        "method":          "percentage",
                        "rate":            0.08,
                        "base_components": ["BASIC", "HOUSING", "TRANSPORT"],
                    },
                }
            ],
            "employees": [
                {
                    "employee_number":        "EMP-FLAT-1",
                    "full_name":              "Flat Keys Employee",
                    "salary_definition_name": "STANDARD",
                    "contract_start":         "2025-01-01",
                    "biodata": {
                        "TIN":            "1234567890",
                        "BANK":           "GTBank",
                        "ACCOUNT_NUMBER": "0123456789",
                        "RSA":            "PEN100999888",
                        "FULL_NAME":      "Flat Keys Employee",
                    },
                }
            ],
        }
        commit_resp = client.post("/api/v1/onboarding/commit", json=payload)
        assert commit_resp.status_code == 200, commit_resp.text
        assert commit_resp.json()["status"] == "success"

        db.execute(
            text("UPDATE workspace SET status = 'LIVE' WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        )
        db.commit()

        # --- run payroll (async contract: DRAFT + run_id) -------------------
        # Pinned to an explicit January period (dev-levy-rule-pct housekeeping):
        # once the levy's cadence gate ships, a wall-clock-default period would
        # make this test month-sensitive/flaky (₦0 levy outside January /
        # first-paid-month). RULES_JSONB carries no "cadence" key, so it
        # resolves to the ANNUAL default — January is one of its two triggers.
        # January 2027 (not 2026) deliberately: this test's statutory_rule row
        # is seeded with effective_from='2026-05-17' — the temporal resolution
        # query (payroll.py) picks the highest effective_from <= period_end, so
        # the period must land after that date or this fixture's rules_jsonb
        # would be silently skipped in favour of an earlier statutory row.
        run_resp = client.post(
            "/api/v1/payroll/run",
            json={
                "workspace_id": str(workspace_id),
                "period_start": "2027-01-01",
                "period_end":   "2027-01-31",
            },
        )
        assert run_resp.status_code == 200, run_resp.text
        run_body = run_resp.json()
        assert run_body["status"] == "DRAFT", run_body
        run_id = run_body["payroll_run_id"]

        # --- assert both flat amounts landed, non-zero ----------------------
        result_row = db.execute(
            text("""
                SELECT net_pay, component_trace_jsonb
                FROM payroll_result
                WHERE payroll_run_id = :rid
            """),
            {"rid": run_id},
        ).fetchone()
        assert result_row is not None, "payroll_result row not found"

        net_pay, trace = result_row
        assert float(net_pay) == EXPECTED_NET, (
            f"NET_PAY {net_pay} != {EXPECTED_NET} — a flat statutory amount "
            "was dropped (₦0 key-mismatch bug class)"
        )

        assert trace is not None, "component_trace_jsonb missing (production path)"
        by_component = {t["component"]: t for t in trace if "component" in t}
        assert Decimal(by_component["HEALTH_INSURANCE_EMPLOYEE"]["result"]) == Decimal(HEALTH_AMOUNT), (
            f"Health Insurance did not receive rules_jsonb "
            f"health_insurance.employee_amount: {by_component.get('HEALTH_INSURANCE_EMPLOYEE')}"
        )
        assert Decimal(by_component["DEVELOPMENT_LEVY"]["result"]) == Decimal(LEVY_AMOUNT), (
            f"Development Levy did not receive rules_jsonb "
            f"development_levy.amount: {by_component.get('DEVELOPMENT_LEVY')}"
        )

    finally:
        db.rollback()
        restore_registry_state(db, registry_prior)
        db.execute(text("SET LOCAL session_replication_role = replica"))
        for stmt, params in [
            ("DELETE FROM payroll_result WHERE payroll_run_id IN (SELECT payroll_run_id FROM payroll_run WHERE workspace_id = :wid)", {"wid": workspace_id}),
            ("DELETE FROM event_store WHERE aggregate_type = 'PAYROLL_RUN' AND aggregate_id IN (SELECT payroll_run_id FROM payroll_run WHERE workspace_id = :wid)", {"wid": workspace_id}),
            ("DELETE FROM audit_log WHERE workspace_id = :wid", {"wid": workspace_id}),
            ("DELETE FROM payroll_run WHERE workspace_id = :wid", {"wid": workspace_id}),
            ("DELETE FROM employee_contract WHERE employee_id IN (SELECT employee_id FROM employee WHERE workspace_id = :wid)", {"wid": workspace_id}),
            ("DELETE FROM employee WHERE workspace_id = :wid", {"wid": workspace_id}),
            ("DELETE FROM rule_set_item WHERE rule_set_id IN (SELECT rule_set_id FROM rule_set WHERE workspace_id = :wid)", {"wid": workspace_id}),
            ("DELETE FROM rule_set WHERE workspace_id = :wid", {"wid": workspace_id}),
            ("DELETE FROM payroll_rule WHERE workspace_id = :wid", {"wid": workspace_id}),
            ("DELETE FROM salary_definition WHERE workspace_id = :wid", {"wid": workspace_id}),
            ("DELETE FROM tax_band WHERE statutory_rule_id = :sr_id", {"sr_id": statutory_rule_id}),
            ("DELETE FROM statutory_rule WHERE statutory_rule_id = :sr_id", {"sr_id": statutory_rule_id}),
            ("DELETE FROM component_metadata WHERE component_metadata_id = :cm_id", {"cm_id": component_metadata_id}),
            ("DELETE FROM workspace WHERE workspace_id = :wid", {"wid": workspace_id}),
            ("DELETE FROM account WHERE account_id = :aid", {"aid": account_id}),
        ]:
            db.execute(text(stmt), params)
        db.commit()
        db.close()
