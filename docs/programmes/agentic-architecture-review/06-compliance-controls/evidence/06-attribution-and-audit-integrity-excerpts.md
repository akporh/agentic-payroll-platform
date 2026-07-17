# Evidence: Actor attribution and audit-record integrity (Stage 06)

Direct code reads, 2026-07-15, git commit `265db103cfb6a6b490c8655d5ceb4b776303e6fe` (branch `uat`). Saved per `_core/EVIDENCE-STANDARD.md` — several claims below are *absence* claims (grep sweeps), which are transient and therefore duplicated here rather than cited as path:line only.

## 1. `performed_by` is caller-supplied, unauthenticated, with self-asserted defaults

`backend/api/routes/payroll.py`:

```python
# line 1146
def retry_payroll_run(run_id: str, performed_by: str = Header(default="admin@internal", alias="X-Performed-By")):
# line 1173
def approve_run(run_id: str, performed_by: str = Header(default="admin@internal", alias="X-Performed-By")):
# line 1193
def lock_run(run_id: str, performed_by: str = Header(default="admin@internal", alias="X-Performed-By")):
```

`pay_run` (payroll.py:1211–1225) takes the actor from the request body:

```python
actor_id = payload.get("actor_id", "system@internal")
...
result = mark_payroll_run_paid(run_id, performed_by=actor_id)
```

`resolve_reconciliation_scoped` (payroll.py:1318–1331) takes `resolved_by` as free text from the request body:

```python
resolved_by = payload.get("resolved_by", "").strip()
...
record = resolve_reconciliation(run_id, notes=notes, resolved_by=resolved_by)
```

Service-layer defaults hardcode the same placeholder (`backend/application/payroll_approval_service.py:44,114,187`; `backend/application/payroll_retry_service.py:497,508,680` — `performed_by: str = "admin@internal"`). System-initiated transitions write `performed_by="system"` (payroll.py:958) and `performed_by="admin@internal"` (payroll.py:975).

## 2. Audit/event writes are post-commit, non-transactional, each in its own DB session

`backend/application/payroll_approval_service.py:88–102` (approve path; lock/paid paths follow the identical pattern at lines ~168 and ~243):

```python
        db.commit()

        # Write audit trail after successful commit (mirrors payroll_run_persister pattern)
        audit = build_transition_audit(...)
        save_audit_log(workspace_id, audit)
        save_event(build_transition_event(...))
```

`backend/infra/repositories/audit_log_repo.py:25–75` — `save_audit_log` opens its **own** `SessionLocal()`, INSERTs, commits, closes. `backend/infra/repositories/event_store_repo.py` — `save_event` does the same. Neither participates in the transaction that changed the state being audited. If the audit INSERT fails after `db.commit()` succeeded, the state change stands with no audit record; no retry/outbox exists (event-store consumer confirmed absent by Stage 05, F-05-02).

## 3. `audit_log` / `event_store` schemas (baseline migration)

`migrations/versions/5aa34350e00f_phase1_baseline_schema.py:104–126`:

```python
    op.create_table(
        "audit_log",
        sa.Column("audit_log_id", sa.UUID(), primary_key=True),
        sa.Column("workspace_id", sa.UUID(), sa.ForeignKey("workspace.workspace_id")),
        sa.Column("entity_type", sa.String(), nullable=False),
        sa.Column("entity_id", sa.UUID(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("old_value_jsonb", sa.JSON(), nullable=True),
        sa.Column("new_value_jsonb", sa.JSON(), nullable=True),
        sa.Column("performed_by", sa.String(), nullable=False),
        sa.Column("performed_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        "event_store",
        sa.Column("event_id", sa.UUID(), primary_key=True),
        sa.Column("aggregate_type", sa.String(), nullable=False),
        sa.Column("aggregate_id", sa.UUID(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("event_payload", sa.JSON(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(), server_default=sa.func.now()),
    )
```

`performed_by` is a plain `String` — no FK to any principal table (no such table exists, F-05-01).

## 4. No immutability protection on audit tables; no retention/purge mechanism anywhere

Grep sweep (2026-07-15, commit `265db10`):

- `grep -rn "CREATE TRIGGER" migrations/versions/*.py` → **10** trigger-bearing migrations, all protecting payroll/config tables: workspace-live enforcement (`0daab4ac893b`), payroll_result paid-lock (`3da637afb11b`, UPDATE+DELETE), payroll readiness (`4907cf6eb08f`), payroll_run state machine (`9901bc4ed0c5`), payroll_run snapshot lock (`a1b2c3d4e5f6`), payroll_run paid-lock (`d9828ee962a2`, `trg_prevent_paid_run_update`), payroll_result mutation guard (`e2f3a4b5c6d7`), payroll_run status transitions (`f1a2b3c4d5e6`), salary_definition paid-lock (`f45614d5aa92`), snapshot physical immutability (`fe0bad282b7d`). **None references `audit_log` or `event_store`** — each of the 10 files checked individually.
  *(Corrected 2026-07-17 per critic RC-1: the original sweep report named only 4 of the 10 files returned by the grep. The operative conclusion is unchanged; the full list strengthens the existing-immutability-precedent point in F-06-03's intended design — the platform protects payroll/config tables extensively while leaving the audit tables unprotected.)*
- `grep -rni "retention|purge|DELETE FROM audit_log|DELETE FROM event_store" backend/ migrations/versions/` (excluding tests) → zero matches. No retention policy, scheduled purge, or archival mechanism exists in the application or migrations.
- `migrations/versions/ea05e71efbd7_add_jsonb_integrity_constraints_for_.py:12` explicitly states: "We intentionally do NOT constrain event_store or audit_log payloads."

## 5. `statutory_rule` schema carries no provenance, timestamps, or approval fields

`backend/infra/db/models/statutory_rule.py:7–23` — full column list: `statutory_rule_id`, `state`, `version`, `rules_jsonb`, `tax_method`, `country_code`, `effective_from`. No `created_at`, no `updated_at`, no source-citation field, no approver/approval-record linkage. (`updated_at` was added to grade/designation/salary_definition/payroll_rule/pay_cycle by migration `a0b1c2d3e4f5` — `statutory_rule` was not included.)

## 6. Statutory-rate corrections are performed destructively in migrations, with provenance only in code comments

`migrations/versions/de1f2a3b4c5d_fix_ng_paye_bands_nta_2025.py` (2026-06-20): corrects the NG PAYE bands to the Nigeria Tax Act 2025 schedule by `DELETE FROM tax_band WHERE statutory_rule_id = ...` then re-INSERTing six new bands (`_replace_bands`, lines ~52–60). The Act citation and the description of the error being corrected exist **only in the migration docstring** — the database itself records no source citation, no approval, no timestamp of the change, and no trace that the old bands ever existed (they are recoverable only from the migration file's `_OLD_BANDS` constant and git history).

## 7. Architecture document's retention design (intended design, S-04)

`docs/architecture/agent-layer-architecture.html`:

- line 938 (story W5): "agent_session_log — workspace_id, operator_id, turn_sequence, tool_calls_jsonb, 7yr retention … Sprint A4 — ships after Track P (operator_id must be real)"
- line 1150–1151 (decision table): "Conversation history | Ephemeral session + agent_session_log | No full replay; audit trail only; 7-year retention for payroll dispute resolution"
- line 496 (blocking condition 5): "agent_session_log must wait for auth — Placeholder operator_id audit trail is worse than none."

The 7-year retention is proposed for `agent_session_log` (which itself embeds `tool_calls_jsonb`); no retention is proposed anywhere for the existing `audit_log`/`event_store` tables, and no legal basis for the 7-year figure is cited in the document.
