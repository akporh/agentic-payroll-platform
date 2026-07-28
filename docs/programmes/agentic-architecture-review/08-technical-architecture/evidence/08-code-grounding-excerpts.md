# Stage 08 Evidence: Code-Grounding Excerpts

All excerpts read directly from the working tree at commit `573be0d80d2d4b0f4cbd40843ad6624d1fb12d1f` (clean tree, branch `uat`, 2026-07-17).

## §1 — Statutory resolution query with version tie-break (F-08-01)

`backend/api/routes/payroll.py:270-282`:

```python
    # ── A1-A2: Statutory rule — temporal selection using statutory_effective_date ─
    # SELECT the rule whose effective_from is <= statutory_effective_date,
    # breaking ties by most recently published (effective_from DESC, version DESC).
    stat_row = db.execute(text("""
        SELECT sr.statutory_rule_id, sr.version, sr.rules_jsonb, sr.effective_from
        FROM statutory_rule sr
        JOIN workspace w ON sr.country_code = w.country_code
        WHERE w.workspace_id = :workspace_id
          AND sr.effective_from <= :as_of_date
        ORDER BY sr.effective_from DESC, sr.version DESC
        LIMIT 1
    """), {"workspace_id": workspace_id, "as_of_date": statutory_effective_date}).fetchone()
```

`backend/infra/db/models/statutory_rule.py:9-11` (the constraint that makes the tie-break currently unreachable per country):

```python
    __table_args__ = (
        UniqueConstraint("country_code", "effective_from", name="uq_statutory_rule_country_effective"),
    )
```

## §2 — Per-repo independent transactions in the persister (F-08-02)

`backend/application/payroll_run_persister.py:70-110` (abridged — the four sequential persistence calls):

```python
    # 1️⃣ Finalise payroll_run (DRAFT row created before execution; write totals + status)
    ...
        finalise_payroll_run(...)
    # 2️⃣ Bulk insert all payroll_results — single connection, single transaction
    ...
        save_payroll_results_bulk(...)
    # 3️⃣ Insert audit logs
    ...
        for audit in audit_logs:
            save_audit_log(workspace_id, audit)
    # 4️⃣ Insert events
    ...
        for event in events:
            save_event(event)
```

Each callee opens and commits its own session — `audit_log_repo.py:35,74` (`db = SessionLocal()` … `db.commit()`), `event_store_repo.py:8,39` (same pattern), `payroll_run_repo.py` (`SessionLocal` at line 51 area per function). No shared session parameter exists in any signature.

## §3 — Citation-currency re-verification at `573be0d` (F-08-03)

Grep output (`grep -n "performed_by\|actor_id\|resolved_by" backend/api/routes/payroll.py`, abridged to the load-bearing sites):

```
992:                performed_by="system",
1009:            performed_by                = "admin@internal",
1180:def retry_payroll_run(run_id: str, performed_by: str = Header(default="admin@internal", alias="X-Performed-By")):
1207:def approve_run(run_id: str, performed_by: str = Header(default="admin@internal", alias="X-Performed-By")):
1227:def lock_run(run_id: str, performed_by: str = Header(default="admin@internal", alias="X-Performed-By")):
1257:    actor_id = payload.get("actor_id", "system@internal")
1359:    resolved_by = payload.get("resolved_by", "").strip()
1363:        raise HTTPException(status_code=400, detail="resolved_by is required")
```

Route positions at `573be0d`: reconciliation scoped trio `payroll.py:1327/1336/1352`, `get_run_timeline` `payroll.py:1371`, `legacy_executor_stats` `payroll.py:1378`. Hardcoded entity types: `audit_events.py:34` (`"entity_type": "PAYROLL_RUN"`), `audit_events.py:60` (`"aggregate_type": "PAYROLL_RUN"`). `payroll_reconciliation` model columns unchanged (`payroll_reconciliation.py:7-24`, no `workspace_id`). Trigger precedent `migrations/versions/3da637afb11b_lock_payroll_result_when_paid.py` unchanged (UPDATE+DELETE triggers via `prevent_result_modification_if_paid()`).

Executor purity (dry-run grounding): `backend/domain/payroll/executor.py:1-11` docstring — "No database writes — pure computation only."; `payroll_run_service.py`/`payroll_run_persister.py` show persistence layered on by the caller, not inside the engine.
