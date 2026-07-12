"""
Shared helper: pin NG platform-registry activation state for e2e tests.

Why this exists
---------------
The payroll run route loads `component_metadata WHERE is_active = TRUE`, so a
test's expected PAYE/NET depends on which statutory components are active in
the registry at run time. Migration truth ships NHF_CONTRIBUTION and
RENT_RELIEF active; several long-standing e2e worked examples were written
assuming neither deducts ("No NHF workspace rule configured..."). Any test
whose expected values depend on registry state must DECLARE that state with
`pin_registry_state()` and restore it in its `finally:` — never assume the
database it happens to run against.

Usage
-----
    prior = pin_registry_state(db, {"NHF_CONTRIBUTION": False, "RENT_RELIEF": False})
    try:
        ...
    finally:
        restore_registry_state(db, prior)

Both functions commit; the suite runs serially so a pinned window never
overlaps another test.
"""

from sqlalchemy import text


def pin_registry_state(db, desired: dict[str, bool]) -> dict[str, bool]:
    """Set is_active per component_code (NG) and return the prior state map."""
    codes = list(desired)
    prior = dict(db.execute(
        text("""
            SELECT component_code, is_active FROM component_metadata
            WHERE country_code = 'NG' AND component_code = ANY(:codes)
        """),
        {"codes": codes},
    ).fetchall())
    for code, active in desired.items():
        db.execute(
            text("""
                UPDATE component_metadata SET is_active = :active
                WHERE country_code = 'NG' AND component_code = :code
            """),
            {"active": active, "code": code},
        )
    db.commit()
    return prior


def restore_registry_state(db, prior: dict[str, bool]) -> None:
    """Restore is_active values captured by pin_registry_state()."""
    for code, active in prior.items():
        db.execute(
            text("""
                UPDATE component_metadata SET is_active = :active
                WHERE country_code = 'NG' AND component_code = :code
            """),
            {"active": active, "code": code},
        )
    db.commit()
