"""
Integration tests: payroll_input period-based claiming logic.

Validates that load_unclaimed_inputs_by_employee() classifies and includes/
excludes inputs correctly based solely on reference_date vs the pay period,
with NO dependency on prior payroll_run rows.

Classification rules
---------------------
  reference_date IS NULL      → period-agnostic   → always include
  reference_date <= period_end → CURRENT or LATE  → always include
  reference_date > period_end  → FUTURE           → always exclude

Idempotency
-----------
  payroll_run_id IS NOT NULL  → already claimed   → always exclude

Tests
-----
1. test_null_reference_date_always_included
2. test_current_period_input_included
3. test_late_input_included_without_prior_run
4. test_future_input_excluded
5. test_claimed_input_excluded

Requirements
------------
- PostgreSQL running at DATABASE_URL env var.
- Alembic migrations applied.

Run:
    pytest tests/test_payroll_input_claiming.py -v
"""

import uuid
from datetime import date, timedelta

import pytest
from sqlalchemy import text

from backend.infra.db.session import SessionLocal
from backend.infra.repositories.payroll_input_repo import load_unclaimed_inputs_by_employee


# ---------------------------------------------------------------------------
# Shared setup / teardown helpers
# ---------------------------------------------------------------------------

PERIOD_START = date(2026, 2, 19)
PERIOD_END   = date(2026, 3, 18)


def _insert_workspace_and_employee(db, workspace_id, employee_id):
    """Insert the minimum rows needed for a payroll_input FK chain."""
    account_id = uuid.uuid4()
    db.execute(
        text("INSERT INTO account (account_id, name) VALUES (:aid, :name)"),
        {"aid": account_id, "name": "Claiming Test Account"},
    )
    db.execute(
        text("""
            INSERT INTO workspace (workspace_id, account_id, name, country_code,
                                   base_currency, status)
            VALUES (:wid, :aid, 'Claiming Test WS', 'NG', 'NGN', 'LIVE')
        """),
        {"wid": workspace_id, "aid": account_id},
    )
    db.execute(
        text("""
            INSERT INTO employee (employee_id, workspace_id, employee_number,
                                  full_name, status)
            VALUES (:eid, :wid, 'CLM-001', 'Claiming Test Employee', 'ACTIVE')
        """),
        {"eid": employee_id, "wid": workspace_id},
    )
    db.commit()
    return account_id


def _insert_input(db, workspace_id, employee_id, *, reference_date, payroll_run_id=None):
    """Insert a payroll_input row and return its ID."""
    input_id = uuid.uuid4()
    db.execute(
        text("""
            INSERT INTO payroll_input (
                payroll_input_id, workspace_id, employee_id,
                input_code, input_category, quantity, source,
                reference_date, payroll_run_id
            ) VALUES (
                :iid, :wid, :eid,
                'regular_overtime_days', 'EARNING', 2, 'MANUAL',
                :ref_date, :run_id
            )
        """),
        {
            "iid":      input_id,
            "wid":      workspace_id,
            "eid":      employee_id,
            "ref_date": reference_date,
            "run_id":   payroll_run_id,
        },
    )
    db.commit()
    return input_id


def _cleanup(db, workspace_id, account_id):
    db.execute(
        text("DELETE FROM payroll_input WHERE workspace_id = :wid"),
        {"wid": workspace_id},
    )
    db.execute(
        text("DELETE FROM employee WHERE workspace_id = :wid"),
        {"wid": workspace_id},
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
# Test 1 — NULL reference_date is always included
# ---------------------------------------------------------------------------

def test_null_reference_date_always_included():
    """Period-agnostic input (reference_date IS NULL) must always be returned."""
    ws_id  = uuid.uuid4()
    emp_id = uuid.uuid4()
    db = SessionLocal()
    account_id = _insert_workspace_and_employee(db, ws_id, emp_id)
    try:
        _insert_input(db, ws_id, emp_id, reference_date=None)
        result = load_unclaimed_inputs_by_employee(
            str(ws_id), period_start=PERIOD_START, period_end=PERIOD_END
        )
        assert str(emp_id) in result, "Employee with NULL reference_date must be included"
        assert "regular_overtime_days" in result[str(emp_id)]
        assert isinstance(result[str(emp_id)]["regular_overtime_days"], list)
    finally:
        _cleanup(db, ws_id, account_id)
        db.close()


# ---------------------------------------------------------------------------
# Test 2 — Current-period input (reference_date within period) is included
# ---------------------------------------------------------------------------

def test_current_period_input_included():
    """Input with reference_date inside the period window must be included."""
    ws_id  = uuid.uuid4()
    emp_id = uuid.uuid4()
    db = SessionLocal()
    account_id = _insert_workspace_and_employee(db, ws_id, emp_id)
    try:
        _insert_input(db, ws_id, emp_id, reference_date=PERIOD_START + timedelta(days=1))
        result = load_unclaimed_inputs_by_employee(
            str(ws_id), period_start=PERIOD_START, period_end=PERIOD_END
        )
        assert str(emp_id) in result, "Current-period input must be included"
        assert isinstance(result[str(emp_id)]["regular_overtime_days"], list)
    finally:
        _cleanup(db, ws_id, account_id)
        db.close()


# ---------------------------------------------------------------------------
# Test 3 — Late input (reference_date < period_start) is ALWAYS included
#           — no prior payroll_run row required
# ---------------------------------------------------------------------------

def test_late_input_included_without_prior_run():
    """LATE input (reference_date before period_start) must be included with no prior run.

    This test specifically verifies that inclusion does NOT depend on the
    existence of a prior payroll_run row with a closed status.  No payroll_run
    rows are created in this test.
    """
    ws_id  = uuid.uuid4()
    emp_id = uuid.uuid4()
    db = SessionLocal()
    account_id = _insert_workspace_and_employee(db, ws_id, emp_id)
    try:
        # reference_date is 30 days before period_start — clearly LATE
        late_ref = PERIOD_START - timedelta(days=30)
        _insert_input(db, ws_id, emp_id, reference_date=late_ref)

        result = load_unclaimed_inputs_by_employee(
            str(ws_id), period_start=PERIOD_START, period_end=PERIOD_END
        )
        assert str(emp_id) in result, (
            f"LATE input (ref={late_ref}) must be included even with no prior payroll_run"
        )
        assert "regular_overtime_days" in result[str(emp_id)]
        assert isinstance(result[str(emp_id)]["regular_overtime_days"], list)
    finally:
        _cleanup(db, ws_id, account_id)
        db.close()


# ---------------------------------------------------------------------------
# Test 4 — Future input (reference_date > period_end) is excluded
# ---------------------------------------------------------------------------

def test_future_input_excluded():
    """FUTURE input (reference_date after period_end) must never be included."""
    ws_id  = uuid.uuid4()
    emp_id = uuid.uuid4()
    db = SessionLocal()
    account_id = _insert_workspace_and_employee(db, ws_id, emp_id)
    try:
        future_ref = PERIOD_END + timedelta(days=1)
        _insert_input(db, ws_id, emp_id, reference_date=future_ref)

        result = load_unclaimed_inputs_by_employee(
            str(ws_id), period_start=PERIOD_START, period_end=PERIOD_END
        )
        assert str(emp_id) not in result, (
            f"FUTURE input (ref={future_ref}) must be excluded"
        )
    finally:
        _cleanup(db, ws_id, account_id)
        db.close()


# ---------------------------------------------------------------------------
# Test 5 — Already-claimed input (payroll_run_id IS NOT NULL) is excluded
# ---------------------------------------------------------------------------

def test_claimed_input_excluded():
    """Input with payroll_run_id set must never be returned (idempotency)."""
    ws_id   = uuid.uuid4()
    emp_id  = uuid.uuid4()
    fake_run_id = uuid.uuid4()
    db = SessionLocal()
    account_id = _insert_workspace_and_employee(db, ws_id, emp_id)

    # We need a payroll_run row to satisfy the FK on payroll_input.payroll_run_id.
    # DB trigger requires initial status=DRAFT; bypass it with session_replication_role.
    db.execute(text("SET LOCAL session_replication_role = replica"))
    db.execute(
        text("""
            INSERT INTO payroll_run (
                payroll_run_id, workspace_id, status
            ) VALUES (:rid, :wid, 'CALCULATED')
        """),
        {"rid": fake_run_id, "wid": ws_id},
    )
    db.commit()

    try:
        _insert_input(
            db, ws_id, emp_id,
            reference_date=PERIOD_START,
            payroll_run_id=str(fake_run_id),
        )
        result = load_unclaimed_inputs_by_employee(
            str(ws_id), period_start=PERIOD_START, period_end=PERIOD_END
        )
        assert str(emp_id) not in result, (
            "Already-claimed input (payroll_run_id IS NOT NULL) must be excluded"
        )
    finally:
        db.execute(
            text("DELETE FROM payroll_input WHERE workspace_id = :wid"),
            {"wid": ws_id},
        )
        db.execute(
            text("DELETE FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": fake_run_id},
        )
        db.commit()
        _cleanup(db, ws_id, account_id)
        db.close()
