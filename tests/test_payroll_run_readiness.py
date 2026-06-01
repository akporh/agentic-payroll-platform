"""
Integration tests: payroll run readiness validation.

Validates that validate_payroll_run_ready(run_id) correctly identifies
whether a payroll run can be safely executed before calculation starts.

Scenarios
---------
Test 1 — Valid run:           all prerequisites present    → ready=True
Test 2 — No employees:        all employees deactivated    → ready=False
Test 3 — Missing salary def:  employee contract expired    → ready=False
Test 4 — Wrong status:        run status is not DRAFT      → ready=False
Test 5 — Invalid component:   component missing 'amount'   → ready=False

Setup pattern
-------------
All tests start from a fully valid DRAFT run (which satisfies the
comprehensive DB-level validate_payroll_readiness() trigger that fires
on payroll_run INSERT).  Each failure test then degrades a specific
condition AFTER the DRAFT run is created.

This reflects real-world usage: conditions can change between when a
payroll run is initially created and when execution is about to start
(e.g., an employee is deactivated, a contract expires, a salary
definition is corrected but left in an invalid intermediate state).

DB triggers on payroll_run INSERT
-----------------------------------
- trg_enforce_workspace_live: workspace.status must be LIVE
- trg_enforce_payroll_readiness: calls validate_payroll_readiness() which
  checks salary definitions, payroll rules, employees, contracts, and
  ensures no duplicate run exists for the same workspace+period.

State machine (trg_payroll_run_state_machine, migration 9901bc4ed0c5)
----------------------------------------------------------------------
BEFORE UPDATE of status.  From DRAFT, only PROCESSING and CANCELLED are
allowed.  Test 4 uses DRAFT → CANCELLED to produce a non-DRAFT run.

Note on "missing pay component reference" (Test 5)
---------------------------------------------------
No pay_component lookup table exists in this schema; pay components are
stored as JSONB within salary_definition.components_jsonb.  "Missing pay
component reference" is adapted to mean a component entry that lacks the
required 'amount' field — the condition that would cause a runtime
calculation failure.

Run:
    pytest tests/test_payroll_run_readiness.py -v
"""

import uuid
from datetime import date

from fastapi.testclient import TestClient
from psycopg2.extras import Json as PgJson
from sqlalchemy import text

from backend.api.main import app
from backend.application.payroll_readiness_service import validate_payroll_run_ready
from backend.infra.db.models import Account, Workspace
from backend.infra.db.session import SessionLocal

client = TestClient(app)

# Pay period used across all tests.
PERIOD_START = date(2026, 3, 1)
PERIOD_END   = date(2026, 3, 31)

# Standard salary components for the onboarding payload.
BASIC     = 500_000
HOUSING   = 200_000
TRANSPORT = 100_000


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _create_base_prerequisites(
    db,
    *,
    account_id,
    workspace_id,
    statutory_rule_id,
    component_metadata_id,
    stat_version: int,
):
    """Insert account, LIVE workspace, statutory rule, tax bands, and
    component metadata.

    These are required by the DB triggers on payroll_run INSERT.
    The workspace is inserted as LIVE directly (valid since there is no
    workspace INSERT trigger requiring DRAFT as the initial state).
    """
    db.add(Account(account_id=account_id, name="Readiness Test Corp"))

    db.add(Workspace(
        workspace_id=workspace_id,
        account_id=account_id,
        name="Readiness Test Workspace",
        country_code="NG",
        base_currency="NGN",
        status="LIVE",
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


def _standard_onboarding_payload(workspace_id: uuid.UUID) -> dict:
    """Return the standard onboarding payload (one employee, one salary
    definition, one payroll rule)."""
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
                "employee_number":        "EMP001",
                "full_name":              "Jane Okeke",
                "salary_definition_name": "STANDARD",
                "contract_start":         "2025-01-01",
                "biodata": {
                    "TIN":            "1234567890",
                    "BANK":           "GTBank",
                    "ACCOUNT_NUMBER": "0123456789",
                    "RSA":            "PEN100123456",
                    "FULL_NAME":      "Jane Okeke",
                },
            }
        ],
    }


def _full_setup(
    db,
    *,
    account_id,
    workspace_id,
    statutory_rule_id,
    component_metadata_id,
    run_id,
    stat_version: int,
):
    """Create all prerequisites, onboard one employee, then insert a
    valid DRAFT payroll_run row.

    This satisfies all DB triggers that fire on payroll_run INSERT:
      - trg_enforce_workspace_live
      - trg_enforce_payroll_readiness (salary defs, payroll rules,
                                        active employees with contracts)
    """
    _create_base_prerequisites(
        db,
        account_id=account_id,
        workspace_id=workspace_id,
        statutory_rule_id=statutory_rule_id,
        component_metadata_id=component_metadata_id,
        stat_version=stat_version,
    )

    commit_resp = client.post(
        "/api/v1/onboarding/commit",
        json=_standard_onboarding_payload(workspace_id),
    )
    assert commit_resp.status_code == 200, (
        f"Onboarding commit failed: {commit_resp.text}"
    )

    db.execute(
        text("""
            INSERT INTO payroll_run
                (payroll_run_id, workspace_id, status, period_start, period_end)
            VALUES
                (:rid, :wid, 'DRAFT', :ps, :pe)
        """),
        {
            "rid": str(run_id),
            "wid": str(workspace_id),
            "ps":  PERIOD_START,
            "pe":  PERIOD_END,
        },
    )
    db.commit()


def _cleanup(db, *, workspace_id, statutory_rule_id, component_metadata_id, account_id):
    """Delete all test data in reverse FK dependency order.

    db.rollback() is called first so that any uncommitted error state is
    cleared before the DELETEs begin.
    """
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
    db.execute(
        text("DELETE FROM audit_log WHERE workspace_id = :wid"),
        {"wid": workspace_id},
    )
    db.execute(
        text("DELETE FROM payroll_run WHERE workspace_id = :wid"),
        {"wid": workspace_id},
    )
    db.execute(
        text("""
            DELETE FROM employee_contract
            WHERE employee_id IN (
                SELECT employee_id FROM employee WHERE workspace_id = :wid
            )
        """),
        {"wid": workspace_id},
    )
    db.execute(
        text("DELETE FROM employee WHERE workspace_id = :wid"),
        {"wid": workspace_id},
    )
    db.execute(
        text("DELETE FROM payroll_rule WHERE workspace_id = :wid"),
        {"wid": workspace_id},
    )
    db.execute(
        text("DELETE FROM salary_definition WHERE workspace_id = :wid"),
        {"wid": workspace_id},
    )
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
    db.execute(
        text("DELETE FROM workspace WHERE workspace_id = :wid"),
        {"wid": workspace_id},
    )
    db.execute(
        text("DELETE FROM account WHERE account_id = :aid"),
        {"aid": account_id},
    )
    db.commit()


# ---------------------------------------------------------------------------
# Test 1 — Valid run
# ---------------------------------------------------------------------------

def test_valid_run_is_ready():
    """All prerequisites present → ready=True, errors=[]."""

    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    statutory_rule_id     = uuid.uuid4()
    component_metadata_id = uuid.uuid4()
    run_id                = uuid.uuid4()

    db = SessionLocal()

    try:
        _full_setup(
            db,
            account_id=account_id,
            workspace_id=workspace_id,
            statutory_rule_id=statutory_rule_id,
            component_metadata_id=component_metadata_id,
            run_id=run_id,
            stat_version=9084,
        )

        result = validate_payroll_run_ready(str(run_id))

        assert result["ready"] is True, (
            f"Expected ready=True but got errors: {result['errors']}"
        )
        assert result["errors"] == []

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
# Test 2 — No active employees
# ---------------------------------------------------------------------------

def test_no_employees_not_ready():
    """All employees deactivated after DRAFT run creation → ready=False.

    Setup:
        1. Create a fully valid DRAFT run (satisfies all DB triggers).
        2. Set the employee's status to INACTIVE.
        3. Python validator finds no active employees.
    """

    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    statutory_rule_id     = uuid.uuid4()
    component_metadata_id = uuid.uuid4()
    run_id                = uuid.uuid4()

    db = SessionLocal()

    try:
        _full_setup(
            db,
            account_id=account_id,
            workspace_id=workspace_id,
            statutory_rule_id=statutory_rule_id,
            component_metadata_id=component_metadata_id,
            run_id=run_id,
            stat_version=9083,
        )

        # Degrade: deactivate all employees in the workspace.
        # Simulates employees being terminated after the run was scheduled.
        db.execute(
            text("""
                UPDATE employee
                SET    status = 'INACTIVE'
                WHERE  workspace_id = :wid
            """),
            {"wid": workspace_id},
        )
        db.commit()

        result = validate_payroll_run_ready(str(run_id))

        assert result["ready"] is False
        assert any(
            "No active employees" in e for e in result["errors"]
        ), f"Expected 'No active employees' in errors: {result['errors']}"

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
# Test 3 — Employee missing salary definition
# ---------------------------------------------------------------------------

def test_employee_missing_salary_definition_not_ready():
    """Employee contract expires after DRAFT run creation → ready=False.

    Setup:
        1. Create a fully valid DRAFT run (satisfies all DB triggers).
        2. Expire the employee's contract by setting end_date to a past
           date (2020-01-01).
        3. The LEFT JOIN in the validator excludes expired contracts,
           returning NULL for salary_definition_id.
        4. Validator flags the employee as missing a salary definition.
    """

    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    statutory_rule_id     = uuid.uuid4()
    component_metadata_id = uuid.uuid4()
    run_id                = uuid.uuid4()

    db = SessionLocal()

    try:
        _full_setup(
            db,
            account_id=account_id,
            workspace_id=workspace_id,
            statutory_rule_id=statutory_rule_id,
            component_metadata_id=component_metadata_id,
            run_id=run_id,
            stat_version=9082,
        )

        # Degrade: expire all active contracts for this workspace.
        # Simulates contracts that were valid at run creation but have
        # since lapsed — a real scenario in multi-month payroll queues.
        db.execute(
            text("""
                UPDATE employee_contract
                SET    end_date = '2025-12-31'
                WHERE  employee_id IN (
                    SELECT employee_id FROM employee WHERE workspace_id = :wid
                )
                  AND  end_date IS NULL
            """),
            {"wid": workspace_id},
        )
        db.commit()

        result = validate_payroll_run_ready(str(run_id))

        assert result["ready"] is False
        assert any(
            "missing a salary definition" in e for e in result["errors"]
        ), f"Expected 'missing a salary definition' in errors: {result['errors']}"

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
# Test 4 — Invalid payroll run status
# ---------------------------------------------------------------------------

def test_non_draft_status_not_ready():
    """Payroll run advanced beyond DRAFT → ready=False.

    Setup:
        1. Create a fully valid DRAFT run.
        2. Advance to VALIDATED (DRAFT → VALIDATED is a forward transition
           permitted by trg_validate_payroll_status_transition, rank 1 → 2).
        3. Python validator rejects any status other than DRAFT.
    """

    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    statutory_rule_id     = uuid.uuid4()
    component_metadata_id = uuid.uuid4()
    run_id                = uuid.uuid4()

    db = SessionLocal()

    try:
        _full_setup(
            db,
            account_id=account_id,
            workspace_id=workspace_id,
            statutory_rule_id=statutory_rule_id,
            component_metadata_id=component_metadata_id,
            run_id=run_id,
            stat_version=9081,
        )

        # Degrade: advance the run status beyond DRAFT.
        # DRAFT → VALIDATED is a valid forward transition (rank 1 → 2)
        # permitted by trg_validate_payroll_status_transition.
        db.execute(
            text("""
                UPDATE payroll_run
                SET    status = 'VALIDATED'
                WHERE  payroll_run_id = :rid
            """),
            {"rid": str(run_id)},
        )
        db.commit()

        result = validate_payroll_run_ready(str(run_id))

        assert result["ready"] is False
        assert any(
            "DRAFT" in e for e in result["errors"]
        ), f"Expected status error mentioning DRAFT: {result['errors']}"

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
# Test 5 — Missing pay component reference
# ---------------------------------------------------------------------------

def test_invalid_pay_component_not_ready():
    """Salary definition component missing 'amount' field → ready=False.

    Adapts the "all pay components exist in pay_component table"
    requirement to this schema: since no pay_component lookup table
    exists, pay components are stored as JSONB within salary_definition.
    A component missing the required 'amount' key is treated as an
    unresolvable pay component reference.

    Setup:
        1. Create a fully valid DRAFT run (valid component structure
           satisfies all DB triggers).
        2. Corrupt the BASIC component: remove its 'amount' key.
        3. Python validator flags the component as structurally invalid.
    """

    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    statutory_rule_id     = uuid.uuid4()
    component_metadata_id = uuid.uuid4()
    run_id                = uuid.uuid4()

    db = SessionLocal()

    try:
        _full_setup(
            db,
            account_id=account_id,
            workspace_id=workspace_id,
            statutory_rule_id=statutory_rule_id,
            component_metadata_id=component_metadata_id,
            run_id=run_id,
            stat_version=9080,
        )

        # Degrade: remove the 'amount' key from the BASIC component.
        # salary_definition.components_jsonb has no DB-level structural
        # constraint, so this UPDATE is accepted by PostgreSQL.
        db.execute(
            text("""
                UPDATE salary_definition
                SET    components_jsonb = :comp
                WHERE  workspace_id    = :wid
            """),
            {
                "wid":  str(workspace_id),
                "comp": PgJson({
                    "BASIC":     {},                        # missing 'amount' key
                    "HOUSING":   {"amount": HOUSING},
                    "TRANSPORT": {"amount": TRANSPORT},
                }),
            },
        )
        db.commit()

        result = validate_payroll_run_ready(str(run_id))

        assert result["ready"] is False
        assert any(
            "amount" in e for e in result["errors"]
        ), f"Expected 'amount' field error in errors: {result['errors']}"

    finally:
        _cleanup(
            db,
            workspace_id=workspace_id,
            statutory_rule_id=statutory_rule_id,
            component_metadata_id=component_metadata_id,
            account_id=account_id,
        )
        db.close()
