"""
Integration tests: payroll_run status transition enforcement.

Validates the two triggers added in migration f1a2b3c4d5e6:

  trg_validate_payroll_status_transition
      BEFORE UPDATE OF status ON payroll_run
      Enforces the lifecycle rank order:
        DRAFT(1) → VALIDATED/CALCULATING(2) → PARTIAL(3) →
        CALCULATED(4) → APPROVED(5) → LOCKED(6) → PAID(7)
      Any backward move (new_rank < old_rank) is rejected.

  trg_enforce_payroll_run_initial_status
      BEFORE INSERT ON payroll_run
      Requires that all new rows start with status = 'DRAFT'.

Tests
-----
1. test_valid_forward_transitions
   All canonical forward transitions succeed without exception:
   DRAFT → VALIDATED → CALCULATED → APPROVED → PAID.

2. test_illegal_payroll_status_transition
   A representative set of backward / illegal transitions each raise
   InternalError with a message containing "cannot move backwards".

3. test_paid_is_terminal
   Once a run reaches PAID, any further status change is rejected.
   (Enforced jointly by trg_validate_payroll_status_transition and the
   earlier trg_prevent_paid_run_update from migration d9828ee962a2.)

4. test_insert_requires_draft_status
   Inserting a payroll_run with any status other than DRAFT raises
   InternalError with "must be created with status DRAFT".

Requirements
------------
- PostgreSQL running at DATABASE_URL env var.
- Migration f1a2b3c4d5e6 (and all predecessors) applied.

Run:
    pytest tests/test_illegal_payroll_status_transition.py -v
"""

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import InternalError

from backend.infra.db.models import Account, Workspace
from backend.infra.db.session import SessionLocal


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_prerequisites(db):
    """Insert a minimal account + workspace and return their IDs."""
    account_id   = uuid.uuid4()
    workspace_id = uuid.uuid4()

    db.add(Account(account_id=account_id, name="Status Transition Test Corp"))
    db.add(Workspace(
        workspace_id=workspace_id,
        account_id=account_id,
        name="Status Transition Test Workspace",
        country_code="NG",
        base_currency="NGN",
        status="DRAFT",
    ))
    db.commit()
    return account_id, workspace_id


def _insert_draft_run(db, workspace_id):
    """Insert a payroll_run row with status='DRAFT'.

    Uses SET LOCAL session_replication_role = replica to bypass
    trg_enforce_payroll_readiness, which requires a fully configured LIVE
    workspace (statutory rules, tax bands, component metadata).  The replica
    setting is transaction-scoped and reverts automatically on COMMIT, so
    subsequent UPDATE statements run with full trigger enforcement.
    """
    run_id = uuid.uuid4()
    db.execute(text("SET LOCAL session_replication_role = replica"))
    db.execute(
        text("""
            INSERT INTO payroll_run (payroll_run_id, workspace_id, status)
            VALUES (:rid, :wid, 'DRAFT')
        """),
        {"rid": run_id, "wid": workspace_id},
    )
    db.commit()
    return run_id


def _set_status(db, run_id, new_status):
    """Direct SQL UPDATE; fires the state-machine trigger."""
    db.execute(
        text("UPDATE payroll_run SET status = :s WHERE payroll_run_id = :rid"),
        {"s": new_status, "rid": run_id},
    )
    db.commit()


def _current_status(db, run_id):
    return db.execute(
        text("SELECT status FROM payroll_run WHERE payroll_run_id = :rid"),
        {"rid": run_id},
    ).scalar()


def _cleanup(db, run_ids, workspace_id, account_id):
    """Remove all test data, bypassing immutability triggers."""
    db.rollback()
    db.execute(text("SET LOCAL session_replication_role = replica"))
    for rid in run_ids:
        db.execute(
            text("DELETE FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": rid},
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
    db.close()


# ---------------------------------------------------------------------------
# Test 1: All canonical forward transitions succeed
# ---------------------------------------------------------------------------

def test_valid_forward_transitions():
    """DRAFT → VALIDATED → CALCULATED → APPROVED → PAID must all succeed."""
    db = SessionLocal()
    account_id, workspace_id = _create_prerequisites(db)
    run_id = _insert_draft_run(db, workspace_id)

    try:
        _set_status(db, run_id, "VALIDATED")
        assert _current_status(db, run_id) == "VALIDATED"

        _set_status(db, run_id, "CALCULATED")
        assert _current_status(db, run_id) == "CALCULATED"

        _set_status(db, run_id, "APPROVED")
        assert _current_status(db, run_id) == "APPROVED"

        _set_status(db, run_id, "PAID")
        assert _current_status(db, run_id) == "PAID"

    finally:
        _cleanup(db, [run_id], workspace_id, account_id)


# ---------------------------------------------------------------------------
# Test 2: Backward and illegal transitions are rejected
# ---------------------------------------------------------------------------

def test_illegal_payroll_status_transition():
    """Backward or out-of-order status changes must raise InternalError.

    Cases verified:
      (a) CALCULATED → DRAFT        — large backward jump
      (b) APPROVED   → CALCULATED   — one step backward
      (c) APPROVED   → VALIDATED    — large backward jump
      (d) CALCULATED → CALCULATING  — same-rank backward into 'in-flight' state
    """
    db = SessionLocal()
    account_id, workspace_id = _create_prerequisites(db)

    # ── (a) CALCULATED → DRAFT ─────────────────────────────────────────────
    run_a = _insert_draft_run(db, workspace_id)
    _set_status(db, run_a, "CALCULATED")

    with pytest.raises(InternalError, match="cannot move backwards"):
        db.execute(
            text("UPDATE payroll_run SET status = 'DRAFT' WHERE payroll_run_id = :rid"),
            {"rid": run_a},
        )
        db.commit()

    db.rollback()
    assert _current_status(db, run_a) == "CALCULATED", "Status must be unchanged"

    # ── (b) APPROVED → CALCULATED ──────────────────────────────────────────
    run_b = _insert_draft_run(db, workspace_id)
    _set_status(db, run_b, "CALCULATED")
    _set_status(db, run_b, "APPROVED")

    with pytest.raises(InternalError, match="cannot move backwards"):
        db.execute(
            text("UPDATE payroll_run SET status = 'CALCULATED' WHERE payroll_run_id = :rid"),
            {"rid": run_b},
        )
        db.commit()

    db.rollback()
    assert _current_status(db, run_b) == "APPROVED", "Status must be unchanged"

    # ── (c) APPROVED → VALIDATED ───────────────────────────────────────────
    run_c = _insert_draft_run(db, workspace_id)
    _set_status(db, run_c, "VALIDATED")
    _set_status(db, run_c, "CALCULATED")
    _set_status(db, run_c, "APPROVED")

    with pytest.raises(InternalError, match="cannot move backwards"):
        db.execute(
            text("UPDATE payroll_run SET status = 'VALIDATED' WHERE payroll_run_id = :rid"),
            {"rid": run_c},
        )
        db.commit()

    db.rollback()
    assert _current_status(db, run_c) == "APPROVED", "Status must be unchanged"

    # ── (d) CALCULATED → CALCULATING ───────────────────────────────────────
    run_d = _insert_draft_run(db, workspace_id)
    _set_status(db, run_d, "CALCULATED")

    with pytest.raises(InternalError, match="cannot move backwards"):
        db.execute(
            text(
                "UPDATE payroll_run SET status = 'CALCULATING' "
                "WHERE payroll_run_id = :rid"
            ),
            {"rid": run_d},
        )
        db.commit()

    db.rollback()
    assert _current_status(db, run_d) == "CALCULATED", "Status must be unchanged"

    _cleanup(db, [run_a, run_b, run_c, run_d], workspace_id, account_id)


# ---------------------------------------------------------------------------
# Test 3: PAID is terminal
# ---------------------------------------------------------------------------

def test_paid_is_terminal():
    """No status change is permitted once a run reaches PAID."""
    db = SessionLocal()
    account_id, workspace_id = _create_prerequisites(db)
    run_id = _insert_draft_run(db, workspace_id)

    try:
        _set_status(db, run_id, "CALCULATED")
        _set_status(db, run_id, "APPROVED")
        _set_status(db, run_id, "PAID")
        assert _current_status(db, run_id) == "PAID"

        # Any attempt to change status FROM PAID must raise InternalError.
        # trg_prevent_paid_run_update (migration d9828ee962a2) fires first,
        # and trg_validate_payroll_status_transition also catches it since
        # PAID has the highest lifecycle rank.
        with pytest.raises(InternalError):
            db.execute(
                text(
                    "UPDATE payroll_run SET status = 'APPROVED' "
                    "WHERE payroll_run_id = :rid"
                ),
                {"rid": run_id},
            )
            db.commit()

        db.rollback()
        assert _current_status(db, run_id) == "PAID", "PAID status must be unchanged"

    finally:
        _cleanup(db, [run_id], workspace_id, account_id)


# ---------------------------------------------------------------------------
# Test 4: INSERT must use DRAFT status
# ---------------------------------------------------------------------------

def test_insert_requires_draft_status():
    """Inserting a payroll_run with a non-DRAFT status must raise InternalError.

    Trigger firing order on INSERT to payroll_run (alphabetical):
      1. trg_enforce_payroll_readiness   — requires salary defs, payroll rules,
                                           retry strategy, active employees +
                                           contracts (validate_payroll_readiness())
      2. trg_enforce_payroll_run_initial_status — requires status = 'DRAFT'
      3. trg_enforce_workspace_live      — requires workspace.status = 'LIVE'

    This test sets up the prerequisites that the current validate_payroll_readiness()
    function requires (workspace LIVE, statutory rule, tax bands, component metadata)
    so that trigger (1) passes.  trg_enforce_payroll_run_initial_status fires next
    and blocks every non-DRAFT INSERT with "must be created with status DRAFT".

    Prerequisites inserted directly (no need for onboarding endpoint):
      - workspace with status = 'LIVE'
      - statutory_rule + tax_bands  (NO_STATUTORY_RULE / NO_TAX_BANDS checks)
      - component_metadata for 'NG' (NO_ACTIVE_COMPONENT_METADATA check)
    """
    db = SessionLocal()
    account_id           = uuid.uuid4()
    workspace_id         = uuid.uuid4()
    statutory_rule_id    = uuid.uuid4()

    try:
        db.add(Account(account_id=account_id, name="Insert Guard Test Corp"))
        db.add(Workspace(
            workspace_id=workspace_id,
            account_id=account_id,
            name="Insert Guard Test Workspace",
            country_code="NG",
            base_currency="NGN",
            status="LIVE",
        ))

        db.execute(
            text("""
                INSERT INTO statutory_rule (statutory_rule_id, state, version, rules_jsonb)
                VALUES (:id, 'NATIONAL', 9994, '{}')
            """),
            {"id": statutory_rule_id},
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

        db.commit()

        # validate_payroll_readiness() now passes (LIVE workspace, statutory rule,
        # tax bands, component metadata).  trg_enforce_payroll_run_initial_status
        # fires and blocks every non-DRAFT INSERT.
        for invalid_status in ("CALCULATED", "APPROVED", "PAID", "VALIDATED"):
            with pytest.raises(InternalError, match="must be created with status DRAFT"):
                db.execute(
                    text("""
                        INSERT INTO payroll_run (payroll_run_id, workspace_id, status)
                        VALUES (:rid, :wid, :s)
                    """),
                    {"rid": uuid.uuid4(), "wid": workspace_id, "s": invalid_status},
                )
                db.commit()

            db.rollback()

    finally:
        db.rollback()
        db.execute(text("SET LOCAL session_replication_role = replica"))
        db.execute(
            text("DELETE FROM tax_band WHERE statutory_rule_id = :sr_id"),
            {"sr_id": statutory_rule_id},
        )
        db.execute(
            text("DELETE FROM statutory_rule WHERE statutory_rule_id = :sr_id"),
            {"sr_id": statutory_rule_id},
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
        db.close()
