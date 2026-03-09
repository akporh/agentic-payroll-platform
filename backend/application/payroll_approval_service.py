"""
Payroll Approval, Lock, and Pay Service.

Drives a payroll run through the final three lifecycle transitions:

    CALCULATED → APPROVED
    APPROVED   → LOCKED
    LOCKED     → PAID

All transitions are modelled in the Python state machine
(backend/domain/payroll/state_machine.py) and in the status enum
(backend/domain/payroll/status.py).

The DB trigger trg_payroll_run_state_machine (migration 9901bc4ed0c5)
only enforces DRAFT/PROCESSING/COMPLETED/PAID transitions.  CALCULATED,
APPROVED, and LOCKED are Python-layer statuses and fall through the
trigger's IF chain to RETURN NEW — so UPDATE is permitted by the DB.

DB-level immutability after PAID is enforced by trg_prevent_paid_run_update
(migration d9828ee962a2) — any UPDATE to a PAID run raises an exception.

Concurrency safety
------------------
All functions lock the payroll_run row with SELECT … FOR UPDATE before
reading status, preventing concurrent transitions from racing.

Idempotency
-----------
Calling any transition function on a run already in the target state
returns an error (not silently succeeds) because silent no-ops would mask
bugs in the caller.
"""

from sqlalchemy import text

from backend.domain.payroll.audit_events import build_transition_audit, build_transition_event
from backend.domain.payroll.state_machine import transition
from backend.domain.payroll.status import PayrollRunStatus
from backend.infra.db.session import SessionLocal
from backend.infra.repositories.audit_log_repo import save_audit_log
from backend.infra.repositories.event_store_repo import save_event


def approve_payroll_run(payroll_run_id: str) -> dict:
    """Transition a CALCULATED payroll run to APPROVED.

    Args:
        payroll_run_id: The run to approve.

    Returns:
        {"payroll_run_id": str, "status": "APPROVED"}

    Raises:
        ValueError: Run not found or not in CALCULATED state.
    """

    db = SessionLocal()

    try:
        run_row = db.execute(
            text("""
                SELECT workspace_id, status
                FROM   payroll_run
                WHERE  payroll_run_id = :run_id
                FOR UPDATE
            """),
            {"run_id": payroll_run_id},
        ).fetchone()

        if run_row is None:
            raise ValueError(f"Payroll run not found: {payroll_run_id}")

        workspace_id = str(run_row[0])
        current = PayrollRunStatus(run_row[1])

        # Validates via state machine — raises ValueError if transition illegal
        transition(current, PayrollRunStatus.APPROVED)

        db.execute(
            text("""
                UPDATE payroll_run
                SET    status = 'APPROVED'
                WHERE  payroll_run_id = :run_id
            """),
            {"run_id": payroll_run_id},
        )

        db.commit()

        # Write audit trail after successful commit (mirrors payroll_run_persister pattern)
        audit = build_transition_audit(
            payroll_run_id=payroll_run_id,
            old_status=current,
            new_status=PayrollRunStatus.APPROVED,
            performed_by="admin@internal",
        )
        save_audit_log(workspace_id, audit)
        save_event(build_transition_event(
            payroll_run_id=payroll_run_id,
            old_status=current,
            new_status=PayrollRunStatus.APPROVED,
        ))

        return {"payroll_run_id": payroll_run_id, "status": "APPROVED"}

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def lock_payroll_run(payroll_run_id: str) -> dict:
    """Transition an APPROVED payroll run to LOCKED.

    A LOCKED run is immutable.  No retry, recalculation, or result
    modification is permitted after this point.

    Args:
        payroll_run_id: The run to lock.

    Returns:
        {"payroll_run_id": str, "status": "LOCKED"}

    Raises:
        ValueError: Run not found or not in APPROVED state.
    """

    db = SessionLocal()

    try:
        run_row = db.execute(
            text("""
                SELECT workspace_id, status
                FROM   payroll_run
                WHERE  payroll_run_id = :run_id
                FOR UPDATE
            """),
            {"run_id": payroll_run_id},
        ).fetchone()

        if run_row is None:
            raise ValueError(f"Payroll run not found: {payroll_run_id}")

        workspace_id = str(run_row[0])
        current = PayrollRunStatus(run_row[1])

        # Validates via state machine — raises ValueError if transition illegal
        transition(current, PayrollRunStatus.LOCKED)

        db.execute(
            text("""
                UPDATE payroll_run
                SET    status = 'LOCKED'
                WHERE  payroll_run_id = :run_id
            """),
            {"run_id": payroll_run_id},
        )

        db.commit()

        # Write audit trail after successful commit (mirrors payroll_run_persister pattern)
        audit = build_transition_audit(
            payroll_run_id=payroll_run_id,
            old_status=current,
            new_status=PayrollRunStatus.LOCKED,
            performed_by="admin@internal",
        )
        save_audit_log(workspace_id, audit)
        save_event(build_transition_event(
            payroll_run_id=payroll_run_id,
            old_status=current,
            new_status=PayrollRunStatus.LOCKED,
        ))

        return {"payroll_run_id": payroll_run_id, "status": "LOCKED"}

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def mark_payroll_run_paid(payroll_run_id: str, actor_id: str) -> dict:
    """Transition a LOCKED payroll run to PAID.

    PAID is the terminal state.  Once a run is marked PAID the DB trigger
    trg_prevent_paid_run_update (migration d9828ee962a2) enforces full
    immutability — no column on the row can be changed.

    Args:
        payroll_run_id: The run to mark as paid.
        actor_id: Identity of the actor triggering the disbursement confirmation.

    Returns:
        {"payroll_run_id": str, "status": "PAID"}

    Raises:
        ValueError: Run not found or not in LOCKED state.
    """

    db = SessionLocal()

    try:
        run_row = db.execute(
            text("""
                SELECT workspace_id, status
                FROM   payroll_run
                WHERE  payroll_run_id = :run_id
                FOR UPDATE
            """),
            {"run_id": payroll_run_id},
        ).fetchone()

        if run_row is None:
            raise ValueError(f"Payroll run not found: {payroll_run_id}")

        workspace_id = str(run_row[0])
        current = PayrollRunStatus(run_row[1])

        # Validates via state machine — raises ValueError if transition illegal
        transition(current, PayrollRunStatus.PAID)

        db.execute(
            text("""
                UPDATE payroll_run
                SET    status = 'PAID'
                WHERE  payroll_run_id = :run_id
            """),
            {"run_id": payroll_run_id},
        )

        db.commit()

        # Write audit trail after successful commit
        audit = build_transition_audit(
            payroll_run_id=payroll_run_id,
            old_status=current,
            new_status=PayrollRunStatus.PAID,
            performed_by=actor_id,
        )
        save_audit_log(workspace_id, audit)
        save_event(build_transition_event(
            payroll_run_id=payroll_run_id,
            old_status=current,
            new_status=PayrollRunStatus.PAID,
        ))

        return {"payroll_run_id": payroll_run_id, "status": "PAID"}

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
