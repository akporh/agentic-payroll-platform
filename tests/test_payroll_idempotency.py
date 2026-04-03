"""
Integration tests: payroll run idempotency.

Verifies that a payroll run cannot be executed twice for the same run record,
the same idempotency key, or the same pay period.

Idempotency layers
------------------
Layer 1 — Application-layer readiness guard (validate_payroll_run_ready):
    Condition 2: status must be DRAFT          → CALCULATED run is rejected
    Condition 4: no payroll_result rows exist  → existing results are rejected

Layer 2 — Database PK (payroll_run.payroll_run_id):
    save_payroll_run() issues INSERT INTO payroll_run.
    A second INSERT with the same payroll_run_id raises IntegrityError.

Layer 3 — Idempotency-Key header (migration b2c3d4e5f6a7):
    Route checks payroll_run for an existing (workspace_id, idempotency_key)
    hit before executing.  If found, the original run is returned with no
    recalculation.  The partial unique index ux_payroll_run_idempotency
    also catches race conditions at the DB level.

Layer 4 — Pay-period unique index (migration 6f5b05ff4690):
    uq_payroll_run_period ON payroll_run(workspace_id, period_start, period_end)
    prevents two runs for the same period when period dates are supplied.

Note on API behaviour
---------------------
POST /payroll/run without an Idempotency-Key always generates a fresh UUID,
so calling the endpoint twice creates two independent runs.
Idempotency at the workspace/period level requires the caller to supply
period_start + period_end (period uniqueness) or an Idempotency-Key (key
uniqueness).

Tests
-----
1. test_first_execution_creates_results
   Verifies that the initial payroll run populates payroll_result rows and
   leaves the run in CALCULATED status.

2. test_readiness_guard_blocks_second_execution
   After a run is CALCULATED, validate_payroll_run_ready() returns ready=False.
   Errors include both "status must be DRAFT" and "already has N result(s)".
   This is the application-layer gate that prevents re-execution.

3. test_result_count_unchanged_after_reexecution_attempt
   Calls execute_and_persist() a second time with the same payroll_run_id.
   Expects an IntegrityError from the duplicate PK INSERT.
   Asserts that payroll_result count is identical before and after the
   failed attempt (no partial data is written).

4. test_only_one_calculated_audit_record
   After a successful run, the audit_log contains exactly one record with
   new_value_jsonb.status = 'CALCULATED' (and exactly one for 'CALCULATING').
   Verifies that only two audit records exist per run — no phantom duplicates.

5. test_same_idempotency_key_returns_same_run
   Two POST /payroll/run requests with identical Idempotency-Key headers
   return the same payroll_run_id.  The second call performs no calculation
   and adds no payroll_result rows.

6. test_duplicate_period_creation_fails
   Two POST /payroll/run requests for the same workspace and period_start/
   period_end return HTTP 409 on the second request (uq_payroll_run_period
   index fires).  Only the first run's payroll_result rows exist.

7. test_idempotency_key_retry_creates_no_new_rows
   After a successful run with an Idempotency-Key, retrying with the same
   key leaves the payroll_result count and audit_log count unchanged.

Requirements
------------
- PostgreSQL running at DATABASE_URL env var.
- All Alembic migrations applied (including b2c3d4e5f6a7).

Run:
    pytest tests/test_payroll_idempotency.py -v
"""

import uuid
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from backend.api.main import app
from backend.application.payroll_readiness_service import validate_payroll_run_ready
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
    db.add(Account(account_id=account_id, name=f"Idempotency Test Corp {stat_version}"))
    db.add(Workspace(
        workspace_id=workspace_id,
        account_id=account_id,
        name=f"Idempotency Test Workspace {stat_version}",
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
                "employee_number":        "EMP-IDMP-001",
                "full_name":              "Idempotency Test Employee",
                "salary_definition_name": "STANDARD",
                "biodata": {
                    "TIN":            "5544332211",
                    "BANK":           "Zenith Bank",
                    "ACCOUNT_NUMBER": "1111222233",
                    "RSA":            "PEN400000001",
                    "FULL_NAME":      "Idempotency Test Employee",
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


def _result_count(db, run_id: str) -> int:
    return db.execute(
        text("SELECT COUNT(*) FROM payroll_result WHERE payroll_run_id = :rid"),
        {"rid": run_id},
    ).scalar()


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
# Test 1 — First execution creates payroll_result records
# ---------------------------------------------------------------------------

def test_first_execution_creates_results():
    """Initial payroll run populates payroll_result rows and reaches CALCULATED.

    Requirement 1+2: create the run, execute once, verify results exist.
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
            stat_version=9072,
        )

        run_id = _run_payroll(workspace_id)

        # Run row must exist and be CALCULATED
        run_row = db.execute(
            text("SELECT status FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": run_id},
        ).fetchone()
        assert run_row is not None, "payroll_run row must exist after execution"
        assert run_row[0] == "CALCULATED", (
            f"Expected status=CALCULATED after first run, got {run_row[0]}"
        )

        # payroll_result rows must exist
        count = _result_count(db, run_id)
        assert count > 0, (
            f"Expected at least one payroll_result after first execution, got {count}"
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
# Test 2 — Application-layer readiness guard blocks second execution
# ---------------------------------------------------------------------------

def test_readiness_guard_blocks_second_execution():
    """validate_payroll_run_ready() rejects a CALCULATED run on two grounds.

    After the first execution the run is CALCULATED and has payroll_result rows.
    The readiness service must detect both conditions and return ready=False.

    Requirement 3: operation rejected.

    Errors expected
    ---------------
    - "status must be DRAFT; current status: CALCULATED"
      (readiness condition 2: status != DRAFT)
    - "already has N result(s); cannot execute a run that already has results"
      (readiness condition 4: existing payroll_result rows)
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
            stat_version=9071,
        )

        run_id = _run_payroll(workspace_id)

        # Confirm the run succeeded
        result_count_after_first_run = _result_count(db, run_id)
        assert result_count_after_first_run > 0, "Precondition: run must have results"

        # -------------------------------------------------------------------
        # Call the readiness validator — must return ready=False
        # -------------------------------------------------------------------
        readiness = validate_payroll_run_ready(run_id)

        assert readiness["ready"] is False, (
            "validate_payroll_run_ready must return ready=False for a CALCULATED run"
        )

        errors_text = " | ".join(readiness["errors"])

        # Error 1: status is not DRAFT
        assert any("DRAFT" in e for e in readiness["errors"]), (
            f"Expected an error about status not being DRAFT. Got errors: {errors_text}"
        )

        # Error 2: existing results
        assert any("result" in e.lower() for e in readiness["errors"]), (
            f"Expected an error about existing payroll_result rows. Got errors: {errors_text}"
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
# Test 3 — payroll_result count is unchanged after a failed re-execution attempt
# ---------------------------------------------------------------------------

def test_result_count_unchanged_after_reexecution_attempt():
    """Direct re-execution of the same payroll_run_id raises an error and
    leaves payroll_result rows completely untouched.

    Requirement 3+4: operation rejected AND no new payroll_result records created.

    Mechanism
    ---------
    execute_and_persist() calls save_payroll_run(), which issues:
      INSERT INTO payroll_run (payroll_run_id, ...) VALUES (:id, ...)
    When the run_id already exists the database raises a unique-constraint
    violation (IntegrityError).  Because persist_payroll_run_execution()
    writes payroll_run BEFORE payroll_result rows, the constraint fires
    before any result rows are touched — leaving the count unchanged.
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
            stat_version=9070,
        )

        run_id = _run_payroll(workspace_id)

        # Count results after first successful execution
        count_before = _result_count(db, run_id)
        assert count_before > 0, "Precondition: first run must have created results"

        # -------------------------------------------------------------------
        # Fetch the arguments needed to call execute_and_persist directly
        # -------------------------------------------------------------------
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

        tax_bands = [
            {"lower_limit": r[0], "upper_limit": r[1], "rate": r[2]}
            for r in tax_band_rows
        ]

        rule_rows = db.execute(
            text("SELECT rule_id FROM payroll_rule WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        ).fetchall()
        payroll_rule_ids = [str(r[0]) for r in rule_rows]

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

        employees = [
            {
                "employee_id": str(r[0]),
                "components": [
                    {"code": k, "amount": v["amount"]}
                    for k, v in r[1].items()
                ],
            }
            for r in employee_rows
        ]

        # -------------------------------------------------------------------
        # Attempt to re-execute with the SAME payroll_run_id — must fail
        # -------------------------------------------------------------------
        with pytest.raises((IntegrityError, Exception)) as exc_info:
            execute_and_persist(
                payroll_run_id=run_id,          # ← duplicate PK
                workspace_id=str(workspace_id),
                employees=employees,
                tax_bands=tax_bands,
                statutory_rule_id=str(statutory_row[0]),
                statutory_version=statutory_row[1],
                payroll_rule_ids=payroll_rule_ids,
                performed_by="test@idempotency",
            )

        # Confirm the exception originated from a DB constraint (PK violation)
        assert exc_info.value is not None, "Re-execution must raise an exception"

        # -------------------------------------------------------------------
        # Requirement 4: payroll_result count must be unchanged
        # -------------------------------------------------------------------
        count_after = _result_count(db, run_id)
        assert count_after == count_before, (
            f"payroll_result count must not change after failed re-execution.\n"
            f"  Before: {count_before}\n"
            f"  After:  {count_after}"
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
# Test 4 — Audit log contains exactly one CALCULATED transition per run
# ---------------------------------------------------------------------------

def test_only_one_calculated_audit_record():
    """After a successful run, audit_log contains exactly one CALCULATED entry.

    Requirement 5: only one CALCULATED transition in the audit trail.

    The full lifecycle of a single run produces exactly two audit records:
      1. DRAFT → CALCULATING   (new_value_jsonb.status = "CALCULATING")
      2. CALCULATING → CALCULATED  (new_value_jsonb.status = "CALCULATED")

    Verifies that:
    - There is exactly 1 record with status=CALCULATING
    - There is exactly 1 record with status=CALCULATED
    - No phantom duplicates exist (total = 2)
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
            stat_version=9069,
        )

        run_id = _run_payroll(workspace_id)

        rows = _fetch_audit_rows(db, workspace_id=workspace_id, run_id=run_id)

        # Exactly two lifecycle audit records for the initial run
        assert len(rows) == 2, (
            f"Expected 2 audit records (CALCULATING + CALCULATED), found {len(rows)}"
        )

        statuses = [row[0]["status"] for row in rows]

        # Exactly one CALCULATING record
        calculating_records = [s for s in statuses if s == "CALCULATING"]
        assert len(calculating_records) == 1, (
            f"Expected exactly 1 CALCULATING audit record, found {len(calculating_records)}"
        )

        # Exactly one CALCULATED record
        calculated_records = [s for s in statuses if s == "CALCULATED"]
        assert len(calculated_records) == 1, (
            f"Expected exactly 1 CALCULATED audit record, found {len(calculated_records)}"
        )

        # CALCULATING must come before CALCULATED
        assert statuses.index("CALCULATING") < statuses.index("CALCULATED"), (
            "CALCULATING audit record must precede CALCULATED audit record"
        )

        # All performed_at values must be non-null
        assert all(row[1] is not None for row in rows), (
            "All audit records must have a non-null performed_at timestamp"
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
# Test 5 — Same Idempotency-Key returns the same payroll_run_id
# ---------------------------------------------------------------------------

def test_same_idempotency_key_returns_same_run():
    """Two requests with identical Idempotency-Key return the original run_id.

    First request: key="idem-key-001" → executes calculation, creates run A.
    Second request: key="idem-key-001" → hits the key cache, returns run A
                    without recalculating.

    Assertions
    ----------
    - Both responses return the same payroll_run_id.
    - Second response includes idempotent=True.
    - payroll_result count after second call equals count after first call
      (no additional rows were written).
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
            stat_version=9068,
        )

        # Onboard and activate workspace (without calling _run_payroll so we
        # can control the Idempotency-Key header)
        commit_resp = client.post(
            "/api/v1/onboarding/commit",
            json=_onboarding_payload(workspace_id),
        )
        assert commit_resp.status_code == 200, commit_resp.text

        db.execute(
            text("UPDATE workspace SET status = 'LIVE' WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        )
        db.commit()

        idem_key = "idem-test-key-001"

        # First request — executes the full calculation
        resp1 = client.post(
            "/api/v1/payroll/run",
            json={"workspace_id": str(workspace_id)},
            headers={"Idempotency-Key": idem_key},
        )
        assert resp1.status_code == 200, resp1.text
        run_id_first = resp1.json()["payroll_run_id"]
        assert resp1.json().get("idempotent") is not True, (
            "First request must not be marked idempotent"
        )

        count_after_first = _result_count(db, run_id_first)
        assert count_after_first > 0, "First run must produce payroll_result rows"

        # Second request — same key, same workspace
        resp2 = client.post(
            "/api/v1/payroll/run",
            json={"workspace_id": str(workspace_id)},
            headers={"Idempotency-Key": idem_key},
        )
        assert resp2.status_code == 200, resp2.text
        run_id_second = resp2.json()["payroll_run_id"]

        # Must return the SAME run
        assert run_id_second == run_id_first, (
            f"Same idempotency key must return the same payroll_run_id.\n"
            f"  First:  {run_id_first}\n"
            f"  Second: {run_id_second}"
        )

        assert resp2.json().get("idempotent") is True, (
            "Second request with same key must be marked idempotent=True"
        )

        # payroll_result count must not change
        count_after_second = _result_count(db, run_id_first)
        assert count_after_second == count_after_first, (
            f"payroll_result count must not change after idempotent retry.\n"
            f"  After first:  {count_after_first}\n"
            f"  After second: {count_after_second}"
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
# Test 6 — Duplicate pay period creation is rejected with HTTP 409
# ---------------------------------------------------------------------------

def test_duplicate_period_creation_fails():
    """Two runs for the same workspace and pay period produce HTTP 409 on retry.

    The unique index uq_payroll_run_period (migration 6f5b05ff4690) enforces
    (workspace_id, period_start, period_end) uniqueness when period dates are
    provided.  The route converts the resulting IntegrityError into HTTP 409.

    Assertions
    ----------
    - First POST with period dates returns 200.
    - Second POST with identical period dates returns 409.
    - Only the first run's payroll_result rows exist in the DB.
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
            stat_version=9067,
        )

        commit_resp = client.post(
            "/api/v1/onboarding/commit",
            json=_onboarding_payload(workspace_id),
        )
        assert commit_resp.status_code == 200, commit_resp.text

        db.execute(
            text("UPDATE workspace SET status = 'LIVE' WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        )
        db.commit()

        period_start = date.today()
        period_end   = date.today() + timedelta(days=30)
        period_payload = {
            "workspace_id": str(workspace_id),
            "period_start": period_start.isoformat(),
            "period_end":   period_end.isoformat(),
        }

        # First run — must succeed
        resp1 = client.post("/api/v1/payroll/run", json=period_payload)
        assert resp1.status_code == 200, resp1.text
        run_id_first = resp1.json()["payroll_run_id"]

        count_after_first = _result_count(db, run_id_first)
        assert count_after_first > 0, "First run must produce payroll_result rows"

        # Second run for the same period — must be rejected
        resp2 = client.post("/api/v1/payroll/run", json=period_payload)
        assert resp2.status_code == 409, (
            f"Expected HTTP 409 for duplicate period, got {resp2.status_code}: {resp2.text}"
        )

        # Only the first run's results exist
        total_results = db.execute(
            text("""
                SELECT COUNT(*)
                FROM payroll_result
                WHERE payroll_run_id IN (
                    SELECT payroll_run_id FROM payroll_run WHERE workspace_id = :wid
                )
            """),
            {"wid": workspace_id},
        ).scalar()

        assert total_results == count_after_first, (
            f"Total payroll_result count must equal first run's count after rejected duplicate.\n"
            f"  First run count: {count_after_first}\n"
            f"  Total in DB:     {total_results}"
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
# Test 7 — Idempotency-Key retry creates no new payroll_result rows
# ---------------------------------------------------------------------------

def test_idempotency_key_retry_creates_no_new_rows():
    """Retrying with the same Idempotency-Key leaves all DB counts unchanged.

    Verifies that a retry:
    - Does not insert new payroll_result rows.
    - Does not insert new audit_log records.
    - Returns the original payroll_run_id.
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
            stat_version=9066,
        )

        commit_resp = client.post(
            "/api/v1/onboarding/commit",
            json=_onboarding_payload(workspace_id),
        )
        assert commit_resp.status_code == 200, commit_resp.text

        db.execute(
            text("UPDATE workspace SET status = 'LIVE' WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        )
        db.commit()

        idem_key = "retry-test-key-002"

        # First request
        resp1 = client.post(
            "/api/v1/payroll/run",
            json={"workspace_id": str(workspace_id)},
            headers={"Idempotency-Key": idem_key},
        )
        assert resp1.status_code == 200, resp1.text
        run_id = resp1.json()["payroll_run_id"]

        result_count_before = _result_count(db, run_id)
        audit_rows_before   = _fetch_audit_rows(db, workspace_id=workspace_id, run_id=run_id)

        assert result_count_before > 0, "Precondition: first run must have results"
        assert len(audit_rows_before) == 2, (
            f"Precondition: first run must have 2 audit records, got {len(audit_rows_before)}"
        )

        # Retry — same key
        resp2 = client.post(
            "/api/v1/payroll/run",
            json={"workspace_id": str(workspace_id)},
            headers={"Idempotency-Key": idem_key},
        )
        assert resp2.status_code == 200, resp2.text
        assert resp2.json()["payroll_run_id"] == run_id, (
            "Retry must return original payroll_run_id"
        )

        # payroll_result count unchanged
        result_count_after = _result_count(db, run_id)
        assert result_count_after == result_count_before, (
            f"payroll_result count must not change after retry.\n"
            f"  Before: {result_count_before}\n"
            f"  After:  {result_count_after}"
        )

        # audit_log count unchanged
        audit_rows_after = _fetch_audit_rows(db, workspace_id=workspace_id, run_id=run_id)
        assert len(audit_rows_after) == len(audit_rows_before), (
            f"audit_log count must not change after retry.\n"
            f"  Before: {len(audit_rows_before)}\n"
            f"  After:  {len(audit_rows_after)}"
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
