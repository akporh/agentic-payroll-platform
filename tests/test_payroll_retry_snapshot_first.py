"""
Regression tests — 04-001 (snapshot-first statutory retry) and 05-001
(fail-visible snapshot creation) remediation.

Background
----------
Audit finding 04-001 (docs/audit-program/04-original-run-retry-parity/
findings.md): per-employee retry re-resolved statutory_rule/tax_band from
live tables keyed only by the run's frozen statutory_effective_date. A
statutory_rule row inserted after the original run, with an effective_from
between the original resolution and the run's statutory_effective_date,
would be silently picked up by a later retry — producing a different
calculation than the original run's own successful employees, within the
same payroll_run. Confirmed S0 by controlled reproduction in Stage 04;
fixed to read exclusively from the frozen rules_context_snapshot
["statutory_rule"] (Stage 05 findings.md §9's canonical contract).

Audit finding 05-001 (docs/audit-program/05-snapshot-integrity/
findings.md): component/client-override/employee-contract snapshot
creation ran in a background task with its exception silently logged and
swallowed, after which calculation and result persistence proceeded
anyway — a run whose snapshot failed to persist would still "succeed,"
only surfacing the problem later as a permanently retry-blocked run with
no operator-visible cause. Fixed to abort the run (status=FAILED,
error_message set, no calculation/persistence) when snapshot creation
fails.

Requirements
------------
- PostgreSQL running at DATABASE_URL env var, all migrations applied
  (including b8c9d0e1f2a3, which adds the FAILED status + error_message).

Run:
    pytest tests/test_payroll_retry_snapshot_first.py -v
"""

import uuid
from decimal import Decimal
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from psycopg2.extras import Json
from sqlalchemy import event, text

from backend.api.main import app
from backend.infra.db.models import Account, Workspace
from backend.infra.db.session import SessionLocal, engine
from backend.application.payroll_retry_service import retry_failed_payroll_employees
from tests.registry_state import pin_registry_state, restore_registry_state

client = TestClient(app)


# ---------------------------------------------------------------------------
# Shared fixture helper — builds one workspace with Employee A (valid) and
# Employee B (broken salary -> FAILED), runs payroll, asserts PARTIAL.
# Mirrors tests/test_payroll_retry.py's established pattern; kept local to
# this file rather than a shared conftest, matching this test suite's
# existing convention of fully self-contained test files.
# ---------------------------------------------------------------------------

def _setup_partial_run(rule_a_rate: Decimal, statutory_effective_from: str = "2026-05-20"):
    # 2026-05-20 must be LATER than any migration-seeded statutory_rule
    # effective_from (currently 2026-05-01) so this fixture wins the
    # effective_from DESC selection on a fresh migrated DB.
    account_id = uuid.uuid4()
    workspace_id = uuid.uuid4()
    statutory_rule_a_id = uuid.uuid4()
    broken_sal_def_id = uuid.uuid4()
    employee_b_id = uuid.uuid4()

    db = SessionLocal()
    # Expected amounts assume neither NHF nor rent relief applies — declare
    # that instead of assuming the registry happens to have them inactive.
    registry_prior = pin_registry_state(
        db, {"NHF_CONTRIBUTION": False, "RENT_RELIEF": False},
    )

    # Self-heal: this setup runs before the test's try/finally, so a crash
    # here strands rows that collide with uq_statutory_rule_country_effective
    # on every subsequent run. Clear any prior test artifact (version >= 9000)
    # at this date before inserting. Never touches migration-seeded rows.
    db.execute(text("""
        DELETE FROM tax_band WHERE statutory_rule_id IN (
            SELECT statutory_rule_id FROM statutory_rule
            WHERE country_code = 'NG' AND effective_from = :eff AND version >= 9000)
    """), {"eff": statutory_effective_from})
    db.execute(text("""
        DELETE FROM statutory_rule
        WHERE country_code = 'NG' AND effective_from = :eff AND version >= 9000
    """), {"eff": statutory_effective_from})
    db.commit()

    db.add(Account(account_id=account_id, name="SnapshotFirst Test Corp"))
    db.add(Workspace(
        workspace_id=workspace_id, account_id=account_id,
        name="SnapshotFirst Test WS", country_code="NG",
        base_currency="NGN", status="DRAFT",
    ))
    db.execute(text("""
        INSERT INTO statutory_rule
            (statutory_rule_id, state, version, rules_jsonb, country_code, effective_from)
        VALUES (:id, 'NATIONAL', 9700,
                '{"pension": {"employee_rate": 0.08, "employer_rate": 0.10}}',
                'NG', :eff)
    """), {"id": statutory_rule_a_id, "eff": statutory_effective_from})
    db.execute(text("""
        INSERT INTO tax_band (tax_band_id, statutory_rule_id, lower_limit, upper_limit, rate)
        VALUES (gen_random_uuid(), :sr_id, 0, NULL, :rate)
    """), {"sr_id": statutory_rule_a_id, "rate": rule_a_rate})
    db.commit()

    onboarding_payload = {
        "workspace_id": str(workspace_id),
        "salary_definitions": [{
            "name": "STANDARD",
            "components": {
                "BASIC": {"amount": 500_000},
                "HOUSING": {"amount": 200_000},
                "TRANSPORT": {"amount": 100_000},
            },
        }],
        "payroll_rules": [],
        "employees": [{
            "employee_number": "SF001",
            "full_name": "SnapshotFirst Employee A",
            "salary_definition_name": "STANDARD",
            "contract_start": "2025-01-01",
            "biodata": {
                "TIN": "1234567890", "BANK": "GTBank",
                "ACCOUNT_NUMBER": "0123456789", "RSA": "PEN100888888",
                "FULL_NAME": "SnapshotFirst Employee A",
            },
        }],
    }
    commit_resp = client.post("/api/v1/onboarding/commit", json=onboarding_payload)
    assert commit_resp.status_code == 200, commit_resp.text
    employee_a_id = db.execute(
        text("SELECT employee_id FROM employee WHERE workspace_id = :wid"),
        {"wid": workspace_id},
    ).fetchone()[0]

    db.execute(text("""
        INSERT INTO salary_definition (salary_definition_id, workspace_id, name, code, components_jsonb)
        VALUES (:id, :wid, 'BROKEN', 'BROKEN', :components)
    """), {"id": broken_sal_def_id, "wid": workspace_id, "components": Json({"BASIC": {"amount": "INVALID"}})})
    db.execute(text("""
        INSERT INTO employee (employee_id, workspace_id, employee_number, full_name, status)
        VALUES (:eid, :wid, 'SF002', 'SnapshotFirst Employee B (broken)', 'ACTIVE')
    """), {"eid": employee_b_id, "wid": workspace_id})
    db.execute(text("""
        INSERT INTO employee_contract (contract_id, employee_id, salary_definition_id, start_date)
        VALUES (gen_random_uuid(), :eid, :sdid, '2025-01-01')
    """), {"eid": employee_b_id, "sdid": broken_sal_def_id})
    db.commit()

    db.execute(text("UPDATE workspace SET status = 'LIVE' WHERE workspace_id = :wid"), {"wid": workspace_id})
    db.commit()

    run_resp = client.post("/api/v1/payroll/run", json={
        "workspace_id": str(workspace_id),
        "period_start": "2026-05-01",
        "period_end": "2026-05-31",
    })
    assert run_resp.status_code == 200, run_resp.text
    payroll_run_id = run_resp.json()["payroll_run_id"]

    run_status = db.execute(
        text("SELECT status FROM payroll_run WHERE payroll_run_id = :rid"),
        {"rid": payroll_run_id},
    ).scalar()
    assert run_status == "PARTIAL", f"expected PARTIAL, got {run_status}"

    return {
        "db": db,
        "account_id": account_id,
        "workspace_id": workspace_id,
        "statutory_rule_a_id": statutory_rule_a_id,
        "broken_sal_def_id": broken_sal_def_id,
        "employee_a_id": employee_a_id,
        "employee_b_id": employee_b_id,
        "payroll_run_id": payroll_run_id,
        "_registry_prior": registry_prior,
    }


def _teardown(ctx: dict, extra_statutory_rule_ids: list | None = None):
    db = ctx["db"]
    workspace_id = ctx["workspace_id"]
    db.rollback()
    if "_registry_prior" in ctx:
        restore_registry_state(db, ctx["_registry_prior"])
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

    all_sr_ids = [ctx["statutory_rule_a_id"]] + (extra_statutory_rule_ids or [])
    for sr_id in all_sr_ids:
        db.execute(text("DELETE FROM tax_band WHERE statutory_rule_id = :sr"), {"sr": sr_id})
        db.execute(text("DELETE FROM statutory_rule WHERE statutory_rule_id = :sr"), {"sr": sr_id})

    db.execute(text("DELETE FROM workspace WHERE workspace_id = :wid"), {"wid": workspace_id})
    db.execute(text("DELETE FROM account WHERE account_id = :aid"), {"aid": ctx["account_id"]})
    db.commit()
    db.close()


# ---------------------------------------------------------------------------
# 04-001 regression tests
# ---------------------------------------------------------------------------

def test_retry_uses_frozen_statutory_snapshot_not_intervening_live_rule():
    """Frozen statutory parity test (04-001, acceptance criterion 2).

    Rule A (10% flat PAYE) is in force when the original run executes.
    Rule B (25% flat PAYE) is inserted afterward with an intervening
    effective_from that the OLD (pre-fix) retry logic would have selected.
    Retry must use rule A — the frozen snapshot content — not rule B.
    """
    ctx = _setup_partial_run(rule_a_rate=Decimal("0.10"), statutory_effective_from="2026-05-18")
    statutory_rule_b_id = uuid.uuid4()
    try:
        db = ctx["db"]
        payroll_run_id = ctx["payroll_run_id"]

        snapshot = db.execute(
            text("SELECT rules_context_snapshot FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": payroll_run_id},
        ).scalar()
        assert snapshot["statutory_rule"]["id"] == str(ctx["statutory_rule_a_id"])

        # Intervening insert — the exact mechanism 04-001 exploited.
        db.execute(text("""
            INSERT INTO statutory_rule
                (statutory_rule_id, state, version, rules_jsonb, country_code, effective_from)
            VALUES (:id, 'NATIONAL', 9701,
                    '{"pension": {"employee_rate": 0.08, "employer_rate": 0.10}}',
                    'NG', '2026-05-25')
        """), {"id": statutory_rule_b_id})
        db.execute(text("""
            INSERT INTO tax_band (tax_band_id, statutory_rule_id, lower_limit, upper_limit, rate)
            VALUES (gen_random_uuid(), :sr_id, 0, NULL, 0.25)
        """), {"sr_id": statutory_rule_b_id})
        db.commit()

        db.execute(text("""
            UPDATE salary_definition SET components_jsonb = :components
            WHERE salary_definition_id = :id
        """), {
            "components": Json({"BASIC": {"amount": 300_000}, "HOUSING": {"amount": 100_000}}),
            "id": ctx["broken_sal_def_id"],
        })
        db.commit()

        result = retry_failed_payroll_employees(payroll_run_id, performed_by="test")
        assert result["success"] == 1, result

        row = db.execute(text("""
            SELECT status, deductions_jsonb->>'PAYE' AS paye
            FROM payroll_result WHERE payroll_run_id = :rid AND employee_id = :eid
        """), {"rid": payroll_run_id, "eid": ctx["employee_b_id"]}).fetchone()
        assert row[0] == "SUCCESS"

        gross_b = Decimal(400_000)
        pension_b = (gross_b * Decimal("0.08")).quantize(Decimal("0.01"))
        taxable_b = gross_b - pension_b
        expected_paye_rule_a = (taxable_b * Decimal("0.10")).quantize(Decimal("0.01"))
        expected_paye_rule_b = (taxable_b * Decimal("0.25")).quantize(Decimal("0.01"))

        actual_paye = Decimal(row[1])
        assert abs(actual_paye - expected_paye_rule_a) < Decimal("1.00"), (
            f"Retry used the wrong statutory content: PAYE {actual_paye} does not match "
            f"the frozen rule A ({expected_paye_rule_a}) — looks like rule B "
            f"({expected_paye_rule_b}) was used instead. 04-001 has regressed."
        )
        assert abs(actual_paye - expected_paye_rule_b) >= Decimal("1.00")
    finally:
        _teardown(ctx, extra_statutory_rule_ids=[statutory_rule_b_id])


def test_retry_hard_fails_on_legacy_v1_statutory_snapshot():
    """Legacy hard-fail test (04-001, acceptance criterion 3).

    A run whose rules_context_snapshot is v1-shaped (id/version only, no
    rules_jsonb/tax_bands) must have its retry attempt hard-fail with the
    correction-run error — never fall back to a live query, never delete
    or replace the FAILED result, never write a new result.

    Built via direct INSERT (not the live route) since
    rules_context_snapshot is DB-level immutable
    (trg_run_snapshot_immutable) — a real legacy run predates that
    immutability trigger's data, but this test only needs the *shape*,
    not a literal pre-migration row.
    """
    account_id = uuid.uuid4()
    workspace_id = uuid.uuid4()
    payroll_run_id = uuid.uuid4()
    employee_id = uuid.uuid4()
    sal_def_id = uuid.uuid4()
    statutory_rule_id = uuid.uuid4()

    db = SessionLocal()
    try:
        db.add(Account(account_id=account_id, name="LegacySnap Test Corp"))
        db.add(Workspace(
            workspace_id=workspace_id, account_id=account_id,
            name="LegacySnap Test WS", country_code="NG",
            base_currency="NGN", status="LIVE",
        ))
        db.commit()
        db.execute(text("""
            INSERT INTO statutory_rule
                (statutory_rule_id, state, version, rules_jsonb, country_code, effective_from)
            VALUES (:id, 'NATIONAL', 9600,
                    '{"pension": {"employee_rate": 0.08, "employer_rate": 0.10}}',
                    'NG', '2025-01-01')
        """), {"id": statutory_rule_id})
        db.execute(text("""
            INSERT INTO salary_definition (salary_definition_id, workspace_id, name, code, components_jsonb)
            VALUES (:id, :wid, 'STANDARD', 'STANDARD', :components)
        """), {"id": sal_def_id, "wid": workspace_id, "components": Json({"BASIC": {"amount": 500_000}})})
        db.execute(text("""
            INSERT INTO employee (employee_id, workspace_id, employee_number, full_name, status)
            VALUES (:eid, :wid, 'LSNAP001', 'LegacySnap Employee', 'ACTIVE')
        """), {"eid": employee_id, "wid": workspace_id})
        db.execute(text("""
            INSERT INTO employee_contract (contract_id, employee_id, salary_definition_id, start_date)
            VALUES (gen_random_uuid(), :eid, :sdid, '2025-01-01')
        """), {"eid": employee_id, "sdid": sal_def_id})

        # v1-shaped snapshot, written once at INSERT (immutable thereafter) —
        # exactly what a genuine pre-RULE-VER-1 run's frozen content looks like.
        db.execute(text("""
            INSERT INTO payroll_run (
                payroll_run_id, workspace_id, status, rules_context_snapshot,
                period_start, period_end, statutory_effective_date,
                public_holidays_snapshot
            ) VALUES (
                :rid, :wid, 'DRAFT',
                jsonb_build_object(
                    'statutory_rule', jsonb_build_object('id', :sr_id, 'version', 9600),
                    'payroll_rules', '[]'::jsonb
                ),
                '2026-05-01', '2026-05-31', '2026-05-31',
                '[]'::jsonb
            )
        """), {"rid": payroll_run_id, "wid": workspace_id, "sr_id": str(statutory_rule_id)})

        # Snapshot-complete for the OTHER two required tables — this test targets
        # specifically the statutory-content gap, not the employee/component gap
        # validate_snapshot_complete() already covers (Stage 03/04).
        db.execute(text("""
            INSERT INTO employee_contract_snapshot
                (payroll_run_id, employee_id, salary_definition_id, components_jsonb,
                 contract_start, contract_end, shift_type)
            VALUES (:rid, :eid, :sdid, :components, '2025-01-01', NULL, NULL)
        """), {"rid": payroll_run_id, "eid": employee_id, "sdid": sal_def_id,
                "components": Json({"BASIC": {"amount": 500_000}})})
        db.execute(text("""
            INSERT INTO component_metadata_snapshot
                (payroll_run_id, component_code, component_class, calculation_method,
                 execution_priority, is_active, metadata_json)
            VALUES (:rid, 'BASIC', 'earning', 'salary_component', 10, true, '{}')
        """), {"rid": payroll_run_id})

        # DRAFT -> PARTIAL directly (rank 1 -> 3, forward per the transition
        # trigger) with one FAILED result — this test only needs a
        # retry-eligible run, not a faithful re-derivation of the original
        # calculation steps.
        db.execute(text("""
            UPDATE payroll_run SET status = 'PARTIAL' WHERE payroll_run_id = :rid
        """), {"rid": payroll_run_id})
        db.execute(text("""
            INSERT INTO payroll_result (
                payroll_result_id, payroll_run_id, employee_id,
                gross_components_jsonb, deductions_jsonb, net_pay,
                calculations_snapshot_json, status, error_message, salary_inputs_snapshot
            ) VALUES (
                gen_random_uuid(), :rid, :eid, '{}', '{}', 0, '{}', 'FAILED',
                'simulated pre-existing failure', '{}'
            )
        """), {"rid": payroll_run_id, "eid": employee_id})
        db.commit()

        pre_result = db.execute(text("""
            SELECT status, error_message FROM payroll_result
            WHERE payroll_run_id = :rid AND employee_id = :eid
        """), {"rid": payroll_run_id, "eid": employee_id}).fetchone()
        assert pre_result[0] == "FAILED"

        with pytest.raises(ValueError, match="v2 statutory snapshot"):
            retry_failed_payroll_employees(payroll_run_id, performed_by="test")

        db.rollback()

        post_result = db.execute(text("""
            SELECT status, error_message FROM payroll_result
            WHERE payroll_run_id = :rid AND employee_id = :eid
        """), {"rid": payroll_run_id, "eid": employee_id}).fetchone()
        assert post_result[0] == "FAILED", "the original FAILED row must not be deleted/replaced"
        assert post_result[1] == pre_result[1]

        run_status = db.execute(
            text("SELECT status FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": payroll_run_id},
        ).scalar()
        assert run_status == "PARTIAL", "run status must remain unchanged on a rejected retry"
    finally:
        db.rollback()
        db.execute(text("SET LOCAL session_replication_role = replica"))
        db.execute(text("DELETE FROM payroll_result WHERE payroll_run_id = :rid"), {"rid": payroll_run_id})
        db.execute(text("DELETE FROM employee_contract_snapshot WHERE payroll_run_id = :rid"), {"rid": payroll_run_id})
        db.execute(text("DELETE FROM component_metadata_snapshot WHERE payroll_run_id = :rid"), {"rid": payroll_run_id})
        db.execute(text("DELETE FROM payroll_run WHERE payroll_run_id = :rid"), {"rid": payroll_run_id})
        db.execute(text("DELETE FROM employee_contract WHERE employee_id = :eid"), {"eid": employee_id})
        db.execute(text("DELETE FROM employee WHERE employee_id = :eid"), {"eid": employee_id})
        db.execute(text("DELETE FROM salary_definition WHERE salary_definition_id = :sdid"), {"sdid": sal_def_id})
        db.execute(text("DELETE FROM statutory_rule WHERE statutory_rule_id = :sr"), {"sr": statutory_rule_id})
        db.execute(text("DELETE FROM workspace WHERE workspace_id = :wid"), {"wid": workspace_id})
        db.execute(text("DELETE FROM account WHERE account_id = :aid"), {"aid": account_id})
        db.commit()
        db.close()


def test_v2_retry_issues_no_live_statutory_rule_or_tax_band_query():
    """No-live-query test (04-001, acceptance criterion 1).

    Spies on every SQL statement executed during a valid v2 retry and
    asserts none of them target the live statutory_rule/tax_band tables.
    """
    ctx = _setup_partial_run(rule_a_rate=Decimal("0.10"), statutory_effective_from="2026-05-19")
    try:
        db = ctx["db"]
        payroll_run_id = ctx["payroll_run_id"]

        db.execute(text("""
            UPDATE salary_definition SET components_jsonb = :components
            WHERE salary_definition_id = :id
        """), {
            "components": Json({"BASIC": {"amount": 300_000}, "HOUSING": {"amount": 100_000}}),
            "id": ctx["broken_sal_def_id"],
        })
        db.commit()

        captured_sql: list[str] = []

        def _capture(conn, cursor, statement, parameters, context, executemany):
            captured_sql.append(statement)

        event.listen(engine, "before_cursor_execute", _capture)
        try:
            result = retry_failed_payroll_employees(payroll_run_id, performed_by="test")
        finally:
            event.remove(engine, "before_cursor_execute", _capture)

        assert result["success"] == 1, result

        offending = [
            s for s in captured_sql
            if ("FROM   statutory_rule" in s or "FROM statutory_rule" in s
                or "FROM   tax_band" in s or "FROM tax_band" in s)
        ]
        assert offending == [], (
            f"retry issued {len(offending)} live query(ies) against statutory_rule/"
            f"tax_band — 04-001 has regressed:\n" + "\n---\n".join(offending)
        )
    finally:
        _teardown(ctx)


# ---------------------------------------------------------------------------
# 05-001 regression tests
# ---------------------------------------------------------------------------

def test_snapshot_creation_failure_aborts_calculation_and_marks_run_failed():
    """Snapshot-creation-failure test (05-001, acceptance criteria 4 and 5).

    Forces create_payroll_snapshot() to raise inside the background
    calculation task. Asserts: no payroll_result rows are written, the run
    is left in FAILED status with a non-null error_message (queryable via
    the API, not just server logs), and calculation never ran.
    """
    from backend.api.routes import payroll as payroll_route

    account_id = uuid.uuid4()
    workspace_id = uuid.uuid4()
    db = SessionLocal()

    db.add(Account(account_id=account_id, name="SnapshotFail Test Corp"))
    db.add(Workspace(
        workspace_id=workspace_id, account_id=account_id,
        name="SnapshotFail Test WS", country_code="NG",
        base_currency="NGN", status="DRAFT",
    ))
    db.commit()

    onboarding_payload = {
        "workspace_id": str(workspace_id),
        "salary_definitions": [{
            "name": "STANDARD",
            "components": {
                "BASIC": {"amount": 500_000},
                "HOUSING": {"amount": 200_000},
                "TRANSPORT": {"amount": 100_000},
            },
        }],
        "payroll_rules": [],
        "employees": [{
            "employee_number": "SF002",
            "full_name": "SnapshotFail Employee",
            "salary_definition_name": "STANDARD",
            "contract_start": "2025-01-01",
            "biodata": {
                "TIN": "1234567890", "BANK": "GTBank",
                "ACCOUNT_NUMBER": "0123456789", "RSA": "PEN100777777",
                "FULL_NAME": "SnapshotFail Employee",
            },
        }],
    }
    try:
        commit_resp = client.post("/api/v1/onboarding/commit", json=onboarding_payload)
        assert commit_resp.status_code == 200, commit_resp.text

        db.execute(text("UPDATE workspace SET status = 'LIVE' WHERE workspace_id = :wid"), {"wid": workspace_id})
        db.commit()

        with patch.object(
            payroll_route, "create_payroll_snapshot",
            side_effect=RuntimeError("simulated snapshot write failure"),
        ), patch.object(payroll_route, "execute_and_persist") as mock_execute:
            run_resp = client.post("/api/v1/payroll/run", json={
                "workspace_id": str(workspace_id),
                "period_start": "2026-05-01",
                "period_end": "2026-05-31",
            })
            assert run_resp.status_code == 200, run_resp.text
            payroll_run_id = run_resp.json()["payroll_run_id"]

            mock_execute.assert_not_called()

        run_row = db.execute(text("""
            SELECT status, error_message FROM payroll_run WHERE payroll_run_id = :rid
        """), {"rid": payroll_run_id}).fetchone()
        assert run_row[0] == "FAILED", f"expected FAILED, got {run_row[0]}"
        assert run_row[1], "error_message must be populated, not silent"

        result_count = db.execute(text("""
            SELECT COUNT(*) FROM payroll_result WHERE payroll_run_id = :rid
        """), {"rid": payroll_run_id}).scalar()
        assert result_count == 0, "no payroll_result rows may be written when snapshot creation fails"

        api_resp = client.get(f"/api/v1/{workspace_id}/payroll/runs/{payroll_run_id}")
        assert api_resp.status_code == 200
        assert api_resp.json()["status"] == "FAILED"
        assert api_resp.json()["error_message"], "failure must be visible via the API, not just server logs"

    finally:
        db.rollback()
        db.execute(text("SET LOCAL session_replication_role = replica"))
        db.execute(text("""
            DELETE FROM payroll_result WHERE payroll_run_id IN (
                SELECT payroll_run_id FROM payroll_run WHERE workspace_id = :wid)
        """), {"wid": workspace_id})
        db.execute(text("DELETE FROM payroll_run WHERE workspace_id = :wid"), {"wid": workspace_id})
        db.execute(text("""
            DELETE FROM employee_contract WHERE employee_id IN (
                SELECT employee_id FROM employee WHERE workspace_id = :wid)
        """), {"wid": workspace_id})
        db.execute(text("DELETE FROM employee WHERE workspace_id = :wid"), {"wid": workspace_id})
        db.execute(text("DELETE FROM salary_definition WHERE workspace_id = :wid"), {"wid": workspace_id})
        db.execute(text("DELETE FROM workspace WHERE workspace_id = :wid"), {"wid": workspace_id})
        db.execute(text("DELETE FROM account WHERE account_id = :aid"), {"aid": account_id})
        db.commit()
        db.close()


def test_successful_snapshot_creation_still_calculates_normally():
    """Successful-path test (05-001, "normal path unchanged" requirement).

    A run whose snapshot creation succeeds must calculate and persist
    results exactly as before — the 05-001 fix only changes the failure
    path.
    """
    ctx = _setup_partial_run(rule_a_rate=Decimal("0.10"), statutory_effective_from="2026-05-21")
    try:
        db = ctx["db"]
        payroll_run_id = ctx["payroll_run_id"]

        comp_count = db.execute(text("""
            SELECT COUNT(*) FROM component_metadata_snapshot WHERE payroll_run_id = :rid
        """), {"rid": payroll_run_id}).scalar()
        assert comp_count > 0, "snapshot creation must have succeeded and persisted rows"

        run_row = db.execute(text("""
            SELECT status, error_message FROM payroll_run WHERE payroll_run_id = :rid
        """), {"rid": payroll_run_id}).fetchone()
        assert run_row[0] == "PARTIAL"
        assert run_row[1] is None, "no error_message on a run whose snapshot succeeded"

        result_a = db.execute(text("""
            SELECT status FROM payroll_result WHERE payroll_run_id = :rid AND employee_id = :eid
        """), {"rid": payroll_run_id, "eid": ctx["employee_a_id"]}).fetchone()
        assert result_a[0] == "SUCCESS"
    finally:
        _teardown(ctx)
