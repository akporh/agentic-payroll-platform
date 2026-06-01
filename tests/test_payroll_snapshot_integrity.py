"""
Integration tests: payroll result snapshot immutability.

Verifies that payroll_result rows are frozen after calculation, even if the
underlying salary definition changes or a re-execution is attempted.

Immutability layers
-------------------
Layer 1 — Payroll run PK (payroll_run.payroll_run_id):
    execute_and_persist() issues INSERT INTO payroll_run.
    A duplicate payroll_run_id raises IntegrityError before any result rows
    are touched, leaving the existing results unchanged.

Layer 2 — DB trigger trg_snapshot_immutable (migration fe0bad282b7d):
    Fires on BEFORE UPDATE OF payroll_result.calculations_snapshot_json.
    Raises EXCEPTION immediately, preventing any direct modification of the
    calculations snapshot.

Layer 3 — Salary definition isolation:
    salary_definition.components_jsonb stores the salary structure at
    onboarding time.  payroll_result.gross_components_jsonb captures the
    actual component amounts used in the calculation.  Updating the salary
    definition after a run does NOT retroactively change stored results.

Tests
-----
1. test_snapshot_frozen_after_salary_change
   Runs payroll, captures calculations_snapshot_json and net_pay, modifies
   the salary definition, attempts re-execution (rejected by PK), and
   verifies the stored snapshot values are unchanged.

2. test_calculations_snapshot_json_immutable_to_direct_update
   Attempts to directly UPDATE calculations_snapshot_json via raw SQL.
   Expects the trg_snapshot_immutable trigger to raise InternalError.

3. test_gross_components_frozen_after_salary_change
   Runs payroll, captures gross_components_jsonb, modifies salary definition,
   attempts re-execution (rejected by PK), and verifies gross_components_jsonb
   is unchanged.

4. test_no_new_calculated_audit_after_reexecution_attempt
   After a successful run and a failed re-execution attempt, the audit_log
   still contains exactly 2 records (CALCULATING + CALCULATED) — no phantom
   entries are written by the failed attempt.

Requirements
------------
- PostgreSQL running at DATABASE_URL env var.
- All Alembic migrations applied (including fe0bad282b7d).

Run:
    pytest tests/test_payroll_snapshot_integrity.py -v
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, InternalError

from backend.api.main import app
from backend.application.payroll_run_service import execute_and_persist
from backend.infra.db.models import Account, Workspace
from backend.infra.db.session import SessionLocal

client = TestClient(app)

BASIC     = 400_000
HOUSING   = 120_000
TRANSPORT =  60_000


# ---------------------------------------------------------------------------
# Shared helpers
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
    db.add(Account(account_id=account_id, name=f"Snapshot Test Corp {stat_version}"))
    db.add(Workspace(
        workspace_id=workspace_id,
        account_id=account_id,
        name=f"Snapshot Test Workspace {stat_version}",
        country_code="NG",
        base_currency="NGN",
        status="DRAFT",
    ))
    db.execute(
        text("""
            INSERT INTO statutory_rule
                (statutory_rule_id, state, version, rules_jsonb, country_code, effective_from)
            VALUES (:id, 'NATIONAL', :ver, '{"pension": {"employee_rate": 0.08, "employer_rate": 0.10}}', 'NG', '2026-04-15')
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
                "employee_number":        "EMP-SNAP-001",
                "full_name":              "Snapshot Test Employee",
                "salary_definition_name": "STANDARD",
                "contract_start":         "2025-01-01",
                "biodata": {
                    "TIN":            "9988776655",
                    "BANK":           "GTBank",
                    "ACCOUNT_NUMBER": "5555666677",
                    "RSA":            "PEN500000001",
                    "FULL_NAME":      "Snapshot Test Employee",
                },
            }
        ],
    }


def _run_payroll(workspace_id: uuid.UUID) -> str:
    """Onboard employee, activate workspace, execute payroll. Returns payroll_run_id."""
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


def _fetch_result_row(db, run_id: str) -> dict:
    """Fetch the first payroll_result row for a run as a dict."""
    row = db.execute(
        text("""
            SELECT gross_components_jsonb,
                   deductions_jsonb,
                   net_pay,
                   calculations_snapshot_json
            FROM   payroll_result
            WHERE  payroll_run_id = :rid
            LIMIT  1
        """),
        {"rid": run_id},
    ).fetchone()
    assert row is not None, f"No payroll_result found for run {run_id}"
    return {
        "gross_components_jsonb":     row[0],
        "deductions_jsonb":           row[1],
        "net_pay":                    row[2],
        "calculations_snapshot_json": row[3],
    }


def _fetch_audit_rows(db, *, workspace_id, run_id):
    return db.execute(
        text("""
            SELECT new_value_jsonb, performed_at
            FROM   audit_log
            WHERE  workspace_id = :wid
              AND  entity_type  = 'PAYROLL_RUN'
              AND  entity_id    = :run_id
              AND  action       = 'STATUS_TRANSITION'
            ORDER  BY performed_at ASC
        """),
        {"wid": workspace_id, "run_id": run_id},
    ).fetchall()


def _fetch_run_args(db, *, workspace_id, statutory_rule_id) -> dict:
    """Return kwargs for a direct execute_and_persist() call.

    Fetches current salary definition amounts (which may have been updated)
    to build the employees list.  Because execute_and_persist() fails on the
    payroll_run PK INSERT before writing any results, the salary amounts used
    here do not affect what is stored in payroll_result.
    """
    statutory_row = db.execute(
        text("""
            SELECT statutory_rule_id, version
            FROM   statutory_rule
            WHERE  statutory_rule_id = :sr_id
        """),
        {"sr_id": statutory_rule_id},
    ).fetchone()

    tax_band_rows = db.execute(
        text("""
            SELECT lower_limit, upper_limit, rate
            FROM   tax_band
            WHERE  statutory_rule_id = :sr_id
            ORDER  BY lower_limit
        """),
        {"sr_id": statutory_rule_id},
    ).fetchall()

    rule_rows = db.execute(
        text("SELECT rule_id FROM payroll_rule WHERE workspace_id = :wid"),
        {"wid": workspace_id},
    ).fetchall()

    employee_rows = db.execute(
        text("""
            SELECT e.employee_id, sd.components_jsonb
            FROM   employee e
            JOIN   employee_contract ec ON e.employee_id = ec.employee_id
            JOIN   salary_definition sd ON ec.salary_definition_id = sd.salary_definition_id
            WHERE  e.workspace_id = :wid AND e.status = 'ACTIVE'
        """),
        {"wid": workspace_id},
    ).fetchall()

    return {
        "statutory_rule_id": str(statutory_row[0]),
        "statutory_version": statutory_row[1],
        "tax_bands": [
            {"lower_limit": r[0], "upper_limit": r[1], "rate": r[2]}
            for r in tax_band_rows
        ],
        "payroll_rule_ids": [str(r[0]) for r in rule_rows],
        "employees": [
            {
                "employee_id": str(r[0]),
                "components": [
                    {"code": k, "amount": v["amount"]}
                    for k, v in r[1].items()
                ],
            }
            for r in employee_rows
        ],
    }


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
# Test 1 — Snapshot is frozen after salary definition change
# ---------------------------------------------------------------------------

def test_snapshot_frozen_after_salary_change():
    """Stored calculations_snapshot_json and net_pay are unchanged after
    salary definition modification and a failed re-execution attempt.

    Steps
    -----
    1. Execute payroll run; record calculations_snapshot_json and net_pay.
    2. Increase salary_definition BASIC component by 50 000.
    3. Attempt to re-execute with the same payroll_run_id (PK violation).
    4. Re-fetch payroll_result; assert snapshot and net_pay are identical
       to the values recorded in step 1.

    The salary modification is not reflected in the stored result because:
    - The PK violation prevents any new payroll_run INSERT.
    - Since save_payroll_run() writes payroll_run BEFORE payroll_result,
      no result rows are touched by the failed attempt.
    - The original result row remains exactly as written at calculation time.
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
            stat_version=9065,
        )

        run_id = _run_payroll(workspace_id)

        # Step 1: capture the stored snapshot
        original = _fetch_result_row(db, run_id)
        assert original["calculations_snapshot_json"] is not None, (
            "calculations_snapshot_json must be populated after a successful run"
        )
        assert original["net_pay"] is not None, (
            "net_pay must be populated after a successful run"
        )

        # Step 2: increase BASIC salary component
        db.execute(
            text("""
                UPDATE salary_definition
                SET    components_jsonb = jsonb_set(
                           components_jsonb,
                           '{BASIC,amount}',
                           to_jsonb(
                               (components_jsonb->'BASIC'->>'amount')::numeric + 50000
                           )
                       )
                WHERE  workspace_id = :wid
            """),
            {"wid": workspace_id},
        )
        db.commit()

        # Step 3: attempt re-execution with the same run_id (PK violation expected)
        run_args = _fetch_run_args(
            db, workspace_id=workspace_id, statutory_rule_id=statutory_rule_id
        )

        with pytest.raises((IntegrityError, ValueError, Exception)):
            execute_and_persist(
                payroll_run_id=run_id,          # ← duplicate PK
                workspace_id=str(workspace_id),
                employees=run_args["employees"],
                tax_bands=run_args["tax_bands"],
                statutory_rule_id=run_args["statutory_rule_id"],
                statutory_version=run_args["statutory_version"],
                payroll_rule_ids=run_args["payroll_rule_ids"],
                performed_by="test@snapshot-integrity",
            )

        # Step 4: re-fetch and assert values unchanged
        after = _fetch_result_row(db, run_id)

        assert after["calculations_snapshot_json"] == original["calculations_snapshot_json"], (
            "calculations_snapshot_json must not change after salary modification.\n"
            f"  Original: {original['calculations_snapshot_json']}\n"
            f"  After:    {after['calculations_snapshot_json']}"
        )
        assert after["net_pay"] == original["net_pay"], (
            f"net_pay must not change after salary modification.\n"
            f"  Original: {original['net_pay']}\n"
            f"  After:    {after['net_pay']}"
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
# Test 2 — calculations_snapshot_json is immutable to direct SQL UPDATE
# ---------------------------------------------------------------------------

def test_calculations_snapshot_json_immutable_to_direct_update():
    """DB trigger trg_snapshot_immutable blocks any direct UPDATE of
    calculations_snapshot_json, raising InternalError immediately.

    The trigger (migration fe0bad282b7d) is defined as:
        BEFORE UPDATE OF calculations_snapshot_json ON payroll_result
        FOR EACH ROW EXECUTE FUNCTION fn_snapshot_immutable()

    fn_snapshot_immutable() calls:
        RAISE EXCEPTION 'calculations_snapshot_json is immutable ...'

    SQLAlchemy surfaces this as sqlalchemy.exc.InternalError.
    The stored value must be unchanged after the blocked attempt.
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
            stat_version=9064,
        )

        run_id = _run_payroll(workspace_id)

        # Confirm the result row exists before attempting the UPDATE
        original = _fetch_result_row(db, run_id)
        assert original["calculations_snapshot_json"] is not None, (
            "Precondition: calculations_snapshot_json must be set after a run"
        )

        # Attempt to directly overwrite calculations_snapshot_json — must fail
        with pytest.raises(InternalError):
            db.execute(
                text("""
                    UPDATE payroll_result
                    SET    calculations_snapshot_json =
                               '{"gross": 0, "paye": 0, "net": 0}'::jsonb
                    WHERE  payroll_run_id = :rid
                """),
                {"rid": run_id},
            )

        db.rollback()  # Required after an aborted transaction

        # Confirm the value is still the original (not zeroed out)
        after = _fetch_result_row(db, run_id)
        assert after["calculations_snapshot_json"] == original["calculations_snapshot_json"], (
            "calculations_snapshot_json must be unchanged after a blocked UPDATE attempt"
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
# Test 3 — gross_components_jsonb is frozen after salary definition change
# ---------------------------------------------------------------------------

def test_gross_components_frozen_after_salary_change():
    """gross_components_jsonb captured at calculation time is not retroactively
    updated when the salary definition changes.

    Steps
    -----
    1. Execute payroll run; capture gross_components_jsonb.
    2. Increase BASIC in salary_definition by 50 000.
    3. Attempt re-execution with the same run_id (PK violation).
    4. Re-fetch gross_components_jsonb; assert it matches the original.

    The stored gross_components_jsonb reflects the salary structure at
    calculation time.  Salary modifications do not propagate backwards
    into existing payroll_result rows.
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
            stat_version=9063,
        )

        run_id = _run_payroll(workspace_id)

        # Step 1: capture gross_components_jsonb
        original = _fetch_result_row(db, run_id)
        assert original["gross_components_jsonb"] is not None, (
            "gross_components_jsonb must be populated after a successful run"
        )
        original_basic = original["gross_components_jsonb"]["BASIC"]["amount"]
        # gross_components_jsonb stores Decimal amounts as strings; use float for comparison
        assert float(original_basic) == float(BASIC), (
            f"Expected BASIC={BASIC} in gross_components_jsonb, got {original_basic}"
        )

        # Step 2: increase BASIC in salary_definition
        db.execute(
            text("""
                UPDATE salary_definition
                SET    components_jsonb = jsonb_set(
                           components_jsonb,
                           '{BASIC,amount}',
                           to_jsonb(
                               (components_jsonb->'BASIC'->>'amount')::numeric + 50000
                           )
                       )
                WHERE  workspace_id = :wid
            """),
            {"wid": workspace_id},
        )
        db.commit()

        # Step 3: attempt re-execution with the same run_id
        run_args = _fetch_run_args(
            db, workspace_id=workspace_id, statutory_rule_id=statutory_rule_id
        )

        with pytest.raises((IntegrityError, ValueError, Exception)):
            execute_and_persist(
                payroll_run_id=run_id,          # ← duplicate PK
                workspace_id=str(workspace_id),
                employees=run_args["employees"],
                tax_bands=run_args["tax_bands"],
                statutory_rule_id=run_args["statutory_rule_id"],
                statutory_version=run_args["statutory_version"],
                payroll_rule_ids=run_args["payroll_rule_ids"],
                performed_by="test@snapshot-integrity",
            )

        # Step 4: re-fetch and compare
        after = _fetch_result_row(db, run_id)
        after_basic = after["gross_components_jsonb"]["BASIC"]["amount"]

        assert after["gross_components_jsonb"] == original["gross_components_jsonb"], (
            "gross_components_jsonb must not change after salary modification.\n"
            f"  Original BASIC: {original_basic}\n"
            f"  After BASIC:    {after_basic}"
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
# Test 4 — Audit log has no extra entries after a failed re-execution attempt
# ---------------------------------------------------------------------------

def test_no_new_calculated_audit_after_reexecution_attempt():
    """After a successful run and a failed re-execution attempt, the audit_log
    still contains exactly 2 records — no phantom entries are written.

    A failed execute_and_persist() call (duplicate PK) never reaches the
    audit-log write step because save_payroll_run() aborts the entire call
    before any audit or event records are touched.

    Assertions
    ----------
    - After first run: 2 audit records (CALCULATING + CALCULATED).
    - After failed re-execution: still exactly 2 audit records.
    - Exactly 1 CALCULATED record — no duplicates.
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
            stat_version=9062,
        )

        run_id = _run_payroll(workspace_id)

        # Baseline: 2 audit records after the initial run
        audit_before = _fetch_audit_rows(db, workspace_id=workspace_id, run_id=run_id)
        assert len(audit_before) == 2, (
            f"Expected 2 audit records after first run, got {len(audit_before)}"
        )

        statuses_before = [r[0]["status"] for r in audit_before]
        assert "CALCULATED" in statuses_before, (
            "CALCULATED audit record must exist after the initial run"
        )

        # Modify salary (ensures re-run would produce different output if it succeeded)
        db.execute(
            text("""
                UPDATE salary_definition
                SET    components_jsonb = jsonb_set(
                           components_jsonb,
                           '{BASIC,amount}',
                           to_jsonb(
                               (components_jsonb->'BASIC'->>'amount')::numeric + 50000
                           )
                       )
                WHERE  workspace_id = :wid
            """),
            {"wid": workspace_id},
        )
        db.commit()

        # Attempt re-execution with the same run_id (PK violation expected)
        run_args = _fetch_run_args(
            db, workspace_id=workspace_id, statutory_rule_id=statutory_rule_id
        )

        with pytest.raises((IntegrityError, ValueError, Exception)):
            execute_and_persist(
                payroll_run_id=run_id,          # ← duplicate PK
                workspace_id=str(workspace_id),
                employees=run_args["employees"],
                tax_bands=run_args["tax_bands"],
                statutory_rule_id=run_args["statutory_rule_id"],
                statutory_version=run_args["statutory_version"],
                payroll_rule_ids=run_args["payroll_rule_ids"],
                performed_by="test@snapshot-integrity",
            )

        # Audit count must be unchanged
        audit_after = _fetch_audit_rows(db, workspace_id=workspace_id, run_id=run_id)
        assert len(audit_after) == len(audit_before), (
            f"audit_log count must not change after failed re-execution.\n"
            f"  Before: {len(audit_before)}\n"
            f"  After:  {len(audit_after)}"
        )

        # No duplicate CALCULATED records
        calculated_count = sum(
            1 for r in audit_after if r[0].get("status") == "CALCULATED"
        )
        assert calculated_count == 1, (
            f"Expected exactly 1 CALCULATED audit record, found {calculated_count}"
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
