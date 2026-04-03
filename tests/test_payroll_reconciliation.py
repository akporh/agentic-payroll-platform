"""
Integration tests: payroll financial reconciliation (Phase 1).

Verifies that the two independently-computed net-pay totals agree after
every payroll run:

    SUM(payroll_result.net_pay)  — sum of every employee's stored net pay
    payroll_run.total_net_pay    — run-level summary written at persist time

Both figures must be equal.  A mismatch means the persistence layer wrote
inconsistent data: either the per-employee rows or the run header is wrong.

Phase 2 note
------------
Reconciliation against payroll_payment_instruction is a Phase 2 feature.
Money movement in Phase 1 is handled manually outside this system.
The relevant test is skipped with an explanatory message (see below).

Tests
-----
1. test_payroll_totals_reconcile
   Phase 1 check: SUM(payroll_result.net_pay) == payroll_run.total_net_pay.

2. test_payment_reconciliation_phase2_skipped
   Explicitly skipped — documents that payment-instruction reconciliation
   is deferred to Phase 2.

Requirements
------------
- PostgreSQL running at DATABASE_URL env var.
- Alembic migration c3d4e5f6a7b8 applied (total_tax column + NOT NULL
  constraints on total_gross_pay / total_net_pay).

Run:
    pytest tests/test_payroll_reconciliation.py -v
"""

import uuid
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from backend.api.main import app
from backend.infra.db.models import Account, Workspace
from backend.infra.db.session import SessionLocal

client = TestClient(app)

BASIC     = 400_000
HOUSING   = 120_000
TRANSPORT =  60_000


# ---------------------------------------------------------------------------
# Shared helpers (same pattern used across the payroll test suite)
# ---------------------------------------------------------------------------

def _create_prerequisites(
    db,
    *,
    account_id,
    workspace_id,
    statutory_rule_id,
    component_metadata_id,
    stat_version: int,
):
    db.add(Account(account_id=account_id, name=f"Reconciliation Test Corp {stat_version}"))
    db.add(Workspace(
        workspace_id=workspace_id,
        account_id=account_id,
        name=f"Reconciliation Test Workspace {stat_version}",
        country_code="NG",
        base_currency="NGN",
        status="DRAFT",
    ))
    db.execute(
        text("""
            INSERT INTO statutory_rule (statutory_rule_id, state, version, rules_jsonb)
            VALUES (:id, 'NATIONAL', :ver, '{}')
        """),
        {"id": statutory_rule_id, "ver": stat_version},
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
            VALUES (:cm_id, 'TEST_SEED', 'NG', :ver, '{}', CURRENT_DATE, true)
        """),
        {"cm_id": component_metadata_id, "ver": stat_version},
    )
    db.commit()


def _onboarding_payload(workspace_id: uuid.UUID) -> dict:
    return {
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
                "employee_number":        "EMP-RECON-001",
                "full_name":              "Reconciliation Test Employee",
                "salary_definition_name": "STANDARD",
                "biodata": {
                    "TIN":            "1122334455",
                    "BANK":           "Access Bank",
                    "ACCOUNT_NUMBER": "3333444455",
                    "RSA":            "PEN600000001",
                    "FULL_NAME":      "Reconciliation Test Employee",
                },
            }
        ],
    }


def _run_payroll(workspace_id: uuid.UUID) -> str:
    """Onboard employees, activate workspace, execute payroll. Returns payroll_run_id."""
    commit_resp = client.post(
        "/api/v1/onboarding/commit",
        json=_onboarding_payload(workspace_id),
    )
    assert commit_resp.status_code == 200, commit_resp.text

    db = SessionLocal()
    db.execute(
        text("UPDATE workspace SET status = 'LIVE' WHERE workspace_id = :wid"),
        {"wid": workspace_id},
    )
    db.commit()
    db.close()

    run_resp = client.post(
        "/api/v1/payroll/run",
        json={"workspace_id": str(workspace_id)},
    )
    assert run_resp.status_code == 200, run_resp.text
    return run_resp.json()["payroll_run_id"]


def _cleanup(db, *, workspace_id, statutory_rule_id, component_metadata_id, account_id):
    db.rollback()
    # Bypass immutability triggers (trg_prevent_paid_result_delete,
    # trg_prevent_paid_run_delete) so teardown always succeeds regardless of
    # the lifecycle state the run was left in.
    db.execute(text("SET LOCAL session_replication_role = replica"))

    db.execute(
        text("""
            DELETE FROM payroll_result
            WHERE payroll_run_id IN (
                SELECT payroll_run_id FROM payroll_run WHERE workspace_id = :wid
            )
        """),
        {"wid": workspace_id},
    )
    db.execute(
        text("""
            DELETE FROM event_store
            WHERE aggregate_type = 'PAYROLL_RUN'
              AND aggregate_id IN (
                SELECT payroll_run_id FROM payroll_run WHERE workspace_id = :wid
              )
        """),
        {"wid": workspace_id},
    )
    db.execute(text("DELETE FROM audit_log WHERE workspace_id = :wid"), {"wid": workspace_id})
    db.execute(text("DELETE FROM payroll_run WHERE workspace_id = :wid"), {"wid": workspace_id})
    db.execute(
        text("""
            DELETE FROM employee_contract
            WHERE employee_id IN (
                SELECT employee_id FROM employee WHERE workspace_id = :wid
            )
        """),
        {"wid": workspace_id},
    )
    db.execute(text("DELETE FROM employee WHERE workspace_id = :wid"), {"wid": workspace_id})
    db.execute(text("DELETE FROM payroll_rule WHERE workspace_id = :wid"), {"wid": workspace_id})
    db.execute(text("DELETE FROM salary_definition WHERE workspace_id = :wid"), {"wid": workspace_id})
    db.execute(
        text("DELETE FROM tax_band WHERE statutory_rule_id = :sr_id"),
        {"sr_id": statutory_rule_id},
    )
    db.execute(
        text("DELETE FROM statutory_rule WHERE statutory_rule_id = :sr_id"),
        {"sr_id": statutory_rule_id},
    )
    db.execute(
        text("DELETE FROM component_metadata WHERE component_metadata_id = :cm_id"),
        {"cm_id": component_metadata_id},
    )
    db.execute(text("DELETE FROM workspace WHERE workspace_id = :wid"), {"wid": workspace_id})
    db.execute(text("DELETE FROM account WHERE account_id = :aid"), {"aid": account_id})
    db.commit()


# ---------------------------------------------------------------------------
# Test 1 — Phase 1 reconciliation: payroll_result totals == payroll_run totals
# ---------------------------------------------------------------------------

def test_payroll_totals_reconcile():
    """SUM(payroll_result.net_pay) must equal payroll_run.total_net_pay.

    After a successful run the persistence layer writes two independent
    representations of the same net-pay figure:

    employee_net_total:
        SUM of every payroll_result.net_pay row for the run.
        Computed row-by-row from the domain calculation.

    run_total:
        payroll_run.total_net_pay written by payroll_run_persister from
        batch_processor totals["total_net_pay"].

    Both figures originate from the same batch_processor output, so they
    must always agree.  A mismatch means one path wrote the wrong value.

    NULL handling
    -------------
    COALESCE(SUM(net_pay), 0) ensures that an empty payroll_result table
    (which would make SUM return NULL) is treated as 0 rather than None,
    avoiding silent Decimal comparison failures.

    Failure message
    ---------------
    "Payroll reconciliation failed:
     employee_total=<value>
     run_total=<value>"
    """
    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    statutory_rule_id     = uuid.uuid4()
    component_metadata_id = uuid.uuid4()

    db = SessionLocal()

    try:
        _create_prerequisites(
            db,
            account_id=account_id,
            workspace_id=workspace_id,
            statutory_rule_id=statutory_rule_id,
            component_metadata_id=component_metadata_id,
            stat_version=9061,
        )

        run_id = _run_payroll(workspace_id)

        # Step 2: employee totals — sum every payroll_result row
        employee_net_total = Decimal(
            db.execute(
                text("""
                    SELECT COALESCE(SUM(net_pay), 0)
                    FROM   payroll_result
                    WHERE  payroll_run_id = :rid
                """),
                {"rid": run_id},
            ).scalar()
        )

        assert employee_net_total > Decimal("0"), (
            f"employee_net_total must be positive after a successful run, "
            f"got {employee_net_total}"
        )

        # Step 5: run-level summary from payroll_run header
        run_total = Decimal(
            db.execute(
                text("""
                    SELECT COALESCE(total_net_pay, 0)
                    FROM   payroll_run
                    WHERE  payroll_run_id = :rid
                """),
                {"rid": run_id},
            ).scalar()
        )

        # Steps 4 + 6 + 7: assert reconciliation — fail with structured message
        assert employee_net_total == run_total, (
            f"Payroll reconciliation failed:\n"
            f" employee_total={employee_net_total}\n"
            f" run_total={run_total}"
        )

    finally:
        _cleanup(
            db,
            workspace_id=workspace_id,
            statutory_rule_id=statutory_rule_id,
            component_metadata_id=component_metadata_id,
            account_id=account_id,
        )
        db.close()


# ---------------------------------------------------------------------------
# Test 2 — Phase 2 payment reconciliation (skipped)
# ---------------------------------------------------------------------------

def test_payment_reconciliation_phase2_skipped():
    """Payment-instruction reconciliation is deferred to Phase 2.

    In Phase 1 money movement is handled manually outside this system.
    The payroll_payment_instruction table does not exist and no payment
    generation logic has been implemented.

    This test is intentionally skipped to document the Phase 2 requirement
    without causing a spurious failure in the Phase 1 test suite.
    """
    pytest.skip(
        "Payment reconciliation is a Phase 2 feature (automated payments). "
        "Implement payroll_payment_instruction table and payment generation "
        "before enabling this test."
    )
