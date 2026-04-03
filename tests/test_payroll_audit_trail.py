"""
Integration tests: payroll audit trail.

Verifies that every critical state transition in a payroll run's lifecycle
produces a corresponding audit_log record.

Events tested
-------------
The five required audit events and their actual representation in the
audit_log table (action = "STATUS_TRANSITION" for all; the specific
event is identified by new_value_jsonb->>'status'):

  Event name (business)          new_value_jsonb.status
  ---------------------------    ----------------------
  payroll_run_created            CALCULATING   ← run initiates calculation
  payroll_calculation_completed  CALCULATED    ← calculation succeeds
  payroll_approved               APPROVED      ← CALCULATED → APPROVED
  payroll_locked                 LOCKED        ← APPROVED → LOCKED
  payroll_paid                   PAID          ← LOCKED → PAID

Lifecycle order (actual state machine)
---------------------------------------
  DRAFT → CALCULATING → CALCULATED → APPROVED → LOCKED → PAID

Actual audit_log schema
-----------------------
  audit_log_id    UUID (PK)
  workspace_id    UUID
  entity_type     VARCHAR  — "PAYROLL_RUN"
  entity_id       UUID     — payroll_run_id
  action          VARCHAR  — "STATUS_TRANSITION" for all payroll transitions
  old_value_jsonb JSONB    — {"status": "<from>"}
  new_value_jsonb JSONB    — {"status": "<to>"}   (task's "metadata_json")
  performed_by    VARCHAR  — actor identifier     (task's "actor_id")
  performed_at    DATETIME — write timestamp      (task's "created_at")

Test 1 — Full audit trail
  Runs the complete lifecycle end-to-end and asserts that each of the
  five transitions produces exactly one audit_log record with correct
  entity_type, entity_id, action, performed_at, and new_value_jsonb.

Test 2 — Chronological order
  Asserts that the five audit records appear in strict chronological
  order: CALCULATING → CALCULATED → APPROVED → LOCKED → PAID.

Test 3 — Rejected transition produces no audit record
  Attempts to mark a CALCULATED run PAID before it has been approved
  or locked (CALCULATED → PAID skips two required states).
  Asserts HTTP 400 is returned and no additional audit records are
  created for the failed attempt.

Requirements
------------
- PostgreSQL running at DATABASE_URL env var.
- All Alembic migrations applied.
- statutory_rule version=9079 so this test wins ORDER BY version DESC
  when the earlier tests (9080–9999) are absent.

Run:
    pytest tests/test_payroll_audit_trail.py -v
"""

import uuid

from fastapi.testclient import TestClient
from sqlalchemy import text

from backend.api.main import app
from backend.infra.db.models import Account, Workspace
from backend.infra.db.session import SessionLocal

client = TestClient(app)

# ---------------------------------------------------------------------------
# Salary constants (same as other E2E tests for consistency)
# ---------------------------------------------------------------------------
BASIC     = 500_000
HOUSING   = 200_000
TRANSPORT = 100_000
GROSS     = BASIC + HOUSING + TRANSPORT   # 800_000
EXPECTED_PAYE = 84_000
EXPECTED_NET  = GROSS - EXPECTED_PAYE     # 716_000


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
    """Insert account, workspace, statutory rule, tax bands, component metadata."""
    db.add(Account(account_id=account_id, name="Audit Trail Test Corp"))

    db.add(Workspace(
        workspace_id=workspace_id,
        account_id=account_id,
        name="Audit Trail Test Workspace",
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
                "employee_number":        "EMP001",
                "full_name":              "Jane Okeke",
                "salary_definition_name": "STANDARD",
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


def _fetch_audit_rows(db, *, workspace_id, run_id):
    """Return all audit_log rows for a payroll run ordered chronologically."""
    return db.execute(
        text("""
            SELECT
                entity_type,
                entity_id,
                action,
                old_value_jsonb,
                new_value_jsonb,
                performed_by,
                performed_at
            FROM audit_log
            WHERE workspace_id = :wid
              AND entity_type  = 'PAYROLL_RUN'
              AND entity_id    = :run_id
            ORDER BY performed_at ASC
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
    db.execute(text("DELETE FROM employee WHERE workspace_id = :wid"), {"wid": workspace_id})
    db.execute(text("DELETE FROM payroll_rule WHERE workspace_id = :wid"), {"wid": workspace_id})
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
    db.execute(text("DELETE FROM workspace WHERE workspace_id = :wid"), {"wid": workspace_id})
    db.execute(text("DELETE FROM account WHERE account_id = :aid"), {"aid": account_id})
    db.commit()


# ---------------------------------------------------------------------------
# Test 1 — Full audit trail across the complete payroll lifecycle
# ---------------------------------------------------------------------------

def test_full_audit_trail():
    """Every lifecycle transition produces a correct audit_log record.

    Pipeline
    --------
      POST /payroll/run              → DRAFT → CALCULATING → CALCULATED
                                       (2 audit records written)
      POST /payroll/run/{id}/approve → CALCULATED → APPROVED
                                       (1 audit record written)
      POST /payroll/run/{id}/lock    → APPROVED → LOCKED
                                       (1 audit record written)
      POST /payroll/run/{id}/pay     → LOCKED → PAID
                                       (1 audit record written)

    Assertions per audit record
    ---------------------------
      entity_type = "PAYROLL_RUN"
      entity_id   = payroll_run_id
      action      = "STATUS_TRANSITION"       (task: "action matches event name")
      performed_at IS NOT NULL                (task: "created_at not null")
      new_value_jsonb IS NOT NULL             (task: "metadata_json not null")
      new_value_jsonb["status"] identifies the specific transition

    The five business events and their system representation
    --------------------------------------------------------
      payroll_run_created           → new_value_jsonb.status = CALCULATING
      payroll_calculation_completed → new_value_jsonb.status = CALCULATED
      payroll_approved              → new_value_jsonb.status = APPROVED
      payroll_locked                → new_value_jsonb.status = LOCKED
      payroll_paid                  → new_value_jsonb.status = PAID
    """

    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    statutory_rule_id     = uuid.uuid4()
    component_metadata_id = uuid.uuid4()

    db = SessionLocal()

    try:
        # -------------------------------------------------------------------
        # STEP 1 — Prerequisites
        # -------------------------------------------------------------------
        _create_prerequisites(
            db,
            account_id=account_id,
            workspace_id=workspace_id,
            statutory_rule_id=statutory_rule_id,
            component_metadata_id=component_metadata_id,
            stat_version=9079,
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

        # -------------------------------------------------------------------
        # STEP 2 — Run payroll → CALCULATED
        # Expected audit records: DRAFT→CALCULATING, CALCULATING→CALCULATED
        # -------------------------------------------------------------------
        payroll_resp = client.post(
            "/api/v1/payroll/run",
            json={"workspace_id": str(workspace_id)},
        )
        assert payroll_resp.status_code == 200, payroll_resp.text
        run_id = payroll_resp.json()["payroll_run_id"]

        rows = _fetch_audit_rows(db, workspace_id=workspace_id, run_id=run_id)
        assert len(rows) == 2, (
            f"Expected 2 audit records after payroll run, found {len(rows)}"
        )

        # --- payroll_run_created (DRAFT → CALCULATING) ---
        r0 = rows[0]
        assert r0[0] == "PAYROLL_RUN",          "entity_type must be PAYROLL_RUN"
        assert str(r0[1]) == run_id,             "entity_id must equal payroll_run_id"
        assert r0[2] == "STATUS_TRANSITION",     "action must be STATUS_TRANSITION"
        assert r0[4] is not None,                "new_value_jsonb (metadata) must not be null"
        assert r0[6] is not None,                "performed_at (created_at) must not be null"
        assert r0[4]["status"] == "CALCULATING", (
            f"payroll_run_created: expected status=CALCULATING, got {r0[4]}"
        )

        # --- payroll_calculation_completed (CALCULATING → CALCULATED) ---
        r1 = rows[1]
        assert r1[0] == "PAYROLL_RUN"
        assert str(r1[1]) == run_id
        assert r1[2] == "STATUS_TRANSITION"
        assert r1[4] is not None
        assert r1[6] is not None
        assert r1[4]["status"] == "CALCULATED", (
            f"payroll_calculation_completed: expected status=CALCULATED, got {r1[4]}"
        )

        # -------------------------------------------------------------------
        # STEP 3 — Approve → APPROVED
        # Expected audit records: + CALCULATED→APPROVED
        # -------------------------------------------------------------------
        approve_resp = client.post(f"/api/v1/payroll/run/{run_id}/approve")
        assert approve_resp.status_code == 200, approve_resp.text

        rows = _fetch_audit_rows(db, workspace_id=workspace_id, run_id=run_id)
        assert len(rows) == 3, (
            f"Expected 3 audit records after approval, found {len(rows)}"
        )

        # --- payroll_approved (CALCULATED → APPROVED) ---
        r2 = rows[2]
        assert r2[0] == "PAYROLL_RUN"
        assert str(r2[1]) == run_id
        assert r2[2] == "STATUS_TRANSITION"
        assert r2[4] is not None
        assert r2[6] is not None
        assert r2[4]["status"] == "APPROVED", (
            f"payroll_approved: expected status=APPROVED, got {r2[4]}"
        )

        # -------------------------------------------------------------------
        # STEP 4 — Lock → LOCKED
        # Expected audit records: + APPROVED→LOCKED
        # -------------------------------------------------------------------
        lock_resp = client.post(f"/api/v1/payroll/run/{run_id}/lock")
        assert lock_resp.status_code == 200, lock_resp.text

        rows = _fetch_audit_rows(db, workspace_id=workspace_id, run_id=run_id)
        assert len(rows) == 4, (
            f"Expected 4 audit records after lock, found {len(rows)}"
        )

        # --- payroll_locked (APPROVED → LOCKED) ---
        r3 = rows[3]
        assert r3[0] == "PAYROLL_RUN"
        assert str(r3[1]) == run_id
        assert r3[2] == "STATUS_TRANSITION"
        assert r3[4] is not None
        assert r3[6] is not None
        assert r3[4]["status"] == "LOCKED", (
            f"payroll_locked: expected status=LOCKED, got {r3[4]}"
        )

        # -------------------------------------------------------------------
        # STEP 5 — Pay → PAID
        # Expected audit records: + LOCKED→PAID
        # -------------------------------------------------------------------
        pay_resp = client.post(
            f"/api/v1/payroll/run/{run_id}/pay",
            json={"actor_id": "finance@company.com"},
        )
        assert pay_resp.status_code == 200, pay_resp.text

        rows = _fetch_audit_rows(db, workspace_id=workspace_id, run_id=run_id)
        assert len(rows) == 5, (
            f"Expected 5 audit records after pay, found {len(rows)}"
        )

        # --- payroll_paid (LOCKED → PAID) ---
        r4 = rows[4]
        assert r4[0] == "PAYROLL_RUN"
        assert str(r4[1]) == run_id
        assert r4[2] == "STATUS_TRANSITION"
        assert r4[4] is not None,             "new_value_jsonb (metadata) must not be null"
        assert r4[6] is not None,             "performed_at (created_at) must not be null"
        assert r4[4]["status"] == "PAID", (
            f"payroll_paid: expected status=PAID, got {r4[4]}"
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
# Test 2 — Chronological order of audit records
# ---------------------------------------------------------------------------

def test_audit_trail_chronological_order():
    """Audit records appear in chronological order across the full lifecycle.

    Expected sequence of new_value_jsonb.status values ordered by
    performed_at ASC:

      1. CALCULATING   — payroll_run_created
      2. CALCULATED    — payroll_calculation_completed
      3. APPROVED      — payroll_approved
      4. LOCKED        — payroll_locked
      5. PAID          — payroll_paid
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
            stat_version=9078,
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

        # Run → Approve → Lock → Pay
        payroll_resp = client.post(
            "/api/v1/payroll/run",
            json={"workspace_id": str(workspace_id)},
        )
        assert payroll_resp.status_code == 200, payroll_resp.text
        run_id = payroll_resp.json()["payroll_run_id"]

        approve_resp = client.post(f"/api/v1/payroll/run/{run_id}/approve")
        assert approve_resp.status_code == 200, approve_resp.text

        lock_resp = client.post(f"/api/v1/payroll/run/{run_id}/lock")
        assert lock_resp.status_code == 200, lock_resp.text

        pay_resp = client.post(
            f"/api/v1/payroll/run/{run_id}/pay",
            json={"actor_id": "finance@company.com"},
        )
        assert pay_resp.status_code == 200, pay_resp.text

        # Fetch all 5 audit records ordered by performed_at
        rows = _fetch_audit_rows(db, workspace_id=workspace_id, run_id=run_id)
        assert len(rows) == 5, f"Expected 5 audit records, found {len(rows)}"

        # Extract the to-status from each row in chronological order
        statuses = [row[4]["status"] for row in rows]

        expected_sequence = ["CALCULATING", "CALCULATED", "APPROVED", "LOCKED", "PAID"]
        assert statuses == expected_sequence, (
            f"Audit records not in expected chronological order.\n"
            f"  Expected: {expected_sequence}\n"
            f"  Actual:   {statuses}"
        )

        # Also verify performed_at timestamps are non-null and non-decreasing
        timestamps = [row[6] for row in rows]
        assert all(t is not None for t in timestamps), (
            "All performed_at values must be non-null"
        )
        for i in range(len(timestamps) - 1):
            assert timestamps[i] <= timestamps[i + 1], (
                f"Timestamps not non-decreasing at position {i}: "
                f"{timestamps[i]} > {timestamps[i + 1]}"
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
# Test 3 — Rejected transition produces no audit record
# ---------------------------------------------------------------------------

def test_rejected_transition_produces_no_audit_record():
    """Marking a CALCULATED run PAID before locking is rejected with no audit record.

    The state machine requires CALCULATED → APPROVED → LOCKED → PAID.
    Attempting CALCULATED → PAID directly (skipping two required states)
    is rejected by the Python state machine.

    Expected behaviour:
      - POST /payroll/run/{id}/pay on a CALCULATED run → HTTP 400
      - audit_log record count for the run remains unchanged (still 2)
      - payroll_run.status remains CALCULATED
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
            stat_version=9077,
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

        payroll_resp = client.post(
            "/api/v1/payroll/run",
            json={"workspace_id": str(workspace_id)},
        )
        assert payroll_resp.status_code == 200, payroll_resp.text
        run_id = payroll_resp.json()["payroll_run_id"]

        # Confirm 2 audit records exist after the initial run
        rows_before = _fetch_audit_rows(db, workspace_id=workspace_id, run_id=run_id)
        assert len(rows_before) == 2, (
            f"Expected 2 audit records after payroll run, found {len(rows_before)}"
        )

        # Confirm run is in CALCULATED state
        status = db.execute(
            text("SELECT status FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": run_id},
        ).scalar()
        assert status == "CALCULATED", f"Expected CALCULATED, got {status}"

        # -------------------------------------------------------------------
        # Attempt to mark PAID without first approving and locking — must be rejected
        # (CALCULATED → PAID skips APPROVED and LOCKED; invalid per state machine)
        # -------------------------------------------------------------------
        premature_pay = client.post(
            f"/api/v1/payroll/run/{run_id}/pay",
            json={"actor_id": "finance@company.com"},
        )
        assert premature_pay.status_code == 400, (
            f"Expected HTTP 400 for pay on CALCULATED run, "
            f"got {premature_pay.status_code}: {premature_pay.text}"
        )

        # -------------------------------------------------------------------
        # Assert: no new audit record was created for the rejected operation
        # -------------------------------------------------------------------
        rows_after = _fetch_audit_rows(db, workspace_id=workspace_id, run_id=run_id)
        assert len(rows_after) == len(rows_before), (
            f"Audit record count must not change after rejected pay attempt.\n"
            f"  Before: {len(rows_before)} records\n"
            f"  After:  {len(rows_after)} records"
        )

        # -------------------------------------------------------------------
        # Assert: run status is still CALCULATED
        # -------------------------------------------------------------------
        status_after = db.execute(
            text("SELECT status FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": run_id},
        ).scalar()
        assert status_after == "CALCULATED", (
            f"Run status must remain CALCULATED after rejected pay attempt; got {status_after}"
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
