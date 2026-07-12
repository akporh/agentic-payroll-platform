"""
Regression tests: resolve_effective_rules() date-driven rule resolution.

INVARIANT PROTECTED (T4.3 — Sprint A fix 3, money):
    `payroll_rule.is_active` means "not withdrawn", NEVER "currently in
    effect". Resolving "the rate for a given date" must always pair
    `is_active` with `effective_from <= as_of_date` ordered
    `effective_from DESC` — a future-dated row must never be selected for a
    current-period run, and multiple rows can legitimately be
    is_active = TRUE at once (a back-dated correction coexisting with a
    future-dated increase).

    This was the root cause of two separate Sprint A bugs (display path and
    calculation path). The display path got a regression test in Sprint A
    (test_payroll_input_codes_route.py); this file closes the deferred
    calculation-path gap by pinning the shared resolver used by the run,
    retry, and legacy-fallback call sites
    (backend/application/rule_set_service.py::resolve_effective_rules).
"""

import json
import uuid
from datetime import date

from sqlalchemy import text

from backend.application.rule_set_service import resolve_effective_rules
from backend.infra.db.models import Account, Workspace
from backend.infra.db.session import SessionLocal


def _insert_rule(db, workspace_id, rule_name, rate, effective_from, is_active=True):
    rule_id = uuid.uuid4()
    db.execute(
        text("""
            INSERT INTO payroll_rule
                (rule_id, workspace_id, rule_name, rule_definition_json,
                 rule_type, is_active, effective_from)
            VALUES
                (:rid, :wid, :name, CAST(:definition AS jsonb),
                 'DEDUCTION', :active, :eff)
        """),
        {
            "rid": rule_id,
            "wid": workspace_id,
            "name": rule_name,
            "definition": json.dumps({"method": "percentage", "rate": rate}),
            "active": is_active,
            "eff": effective_from,
        },
    )
    return str(rule_id)


def test_future_dated_rule_excluded_and_multiple_active_rows_resolved_by_date():
    account_id   = uuid.uuid4()
    workspace_id = uuid.uuid4()
    db = SessionLocal()
    try:
        db.add(Account(account_id=account_id, name="Resolve Rules Test Corp"))
        db.add(Workspace(
            workspace_id=workspace_id,
            account_id=account_id,
            name="Resolve Rules Test Workspace",
            country_code="NG",
            base_currency="NGN",
            status="DRAFT",
        ))
        db.flush()

        # Three is_active versions of the same rule — only the date decides:
        #   2026-01-01  rate 0.05   (in effect for July)
        #   2026-03-01  rate 0.06   (back-dated correction, latest <= as_of)
        #   2026-12-01  rate 0.07   (future-dated increase — must be EXCLUDED)
        _insert_rule(db, workspace_id, "UNION_DUES", 0.05, date(2026, 1, 1))
        expected_id = _insert_rule(db, workspace_id, "UNION_DUES", 0.06, date(2026, 3, 1))
        _insert_rule(db, workspace_id, "UNION_DUES", 0.07, date(2026, 12, 1))

        # A rule whose only version is future-dated — must not appear at all.
        _insert_rule(db, workspace_id, "NEW_YEAR_LEVY", 0.01, date(2027, 1, 1))
        db.commit()

        resolved = resolve_effective_rules(
            db, str(workspace_id), date(2026, 7, 31), active_only=True,
        )

        by_name = {r["rule_name"]: r for r in resolved}
        assert "UNION_DUES" in by_name
        assert by_name["UNION_DUES"]["rule_id"] == expected_id, (
            "Resolver must pick the latest effective_from <= as_of_date, "
            f"got {by_name['UNION_DUES']}"
        )
        assert float(by_name["UNION_DUES"]["rule_definition_json"]["rate"]) == 0.06

        assert "NEW_YEAR_LEVY" not in by_name, (
            "A future-dated rule leaked into current-period resolution — "
            "is_active alone is never sufficient (Sprint A bug class)"
        )
    finally:
        db.rollback()
        db.execute(text("DELETE FROM payroll_rule WHERE workspace_id = :wid"),
                   {"wid": workspace_id})
        db.execute(text("DELETE FROM workspace WHERE workspace_id = :wid"),
                   {"wid": workspace_id})
        db.execute(text("DELETE FROM account WHERE account_id = :aid"),
                   {"aid": account_id})
        db.commit()
        db.close()


def test_withdrawn_rule_excluded_when_active_only():
    """is_active=False (withdrawn) rows are excluded with active_only=True,
    and resolution falls back to the prior still-active version by date."""
    account_id   = uuid.uuid4()
    workspace_id = uuid.uuid4()
    db = SessionLocal()
    try:
        db.add(Account(account_id=account_id, name="Resolve Rules Test Corp 2"))
        db.add(Workspace(
            workspace_id=workspace_id,
            account_id=account_id,
            name="Resolve Rules Test Workspace 2",
            country_code="NG",
            base_currency="NGN",
            status="DRAFT",
        ))
        db.flush()

        older_id = _insert_rule(db, workspace_id, "CHECK_OFF", 0.02, date(2026, 1, 1))
        _insert_rule(db, workspace_id, "CHECK_OFF", 0.03, date(2026, 5, 1), is_active=False)
        db.commit()

        resolved = resolve_effective_rules(
            db, str(workspace_id), date(2026, 7, 31), active_only=True,
        )
        by_name = {r["rule_name"]: r for r in resolved}
        assert by_name["CHECK_OFF"]["rule_id"] == older_id, (
            "Withdrawn (is_active=False) version must be skipped; the prior "
            f"active version applies: {by_name['CHECK_OFF']}"
        )
    finally:
        db.rollback()
        db.execute(text("DELETE FROM payroll_rule WHERE workspace_id = :wid"),
                   {"wid": workspace_id})
        db.execute(text("DELETE FROM workspace WHERE workspace_id = :wid"),
                   {"wid": workspace_id})
        db.execute(text("DELETE FROM account WHERE account_id = :aid"),
                   {"aid": account_id})
        db.commit()
        db.close()
