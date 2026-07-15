# Stage 05 Output: Audit and Operational-History Coverage Assessment (F-01-40 re-check)

**Status: CONFIRMED, unchanged since Stage 01 — coverage has not widened despite one intervening remediation commit touching adjacent code.**

## Current state, exhaustively re-verified

- `audit_log`/`event_store` are written to exclusively for `payroll_run` status transitions. Current exact call sites (re-verified, not assumed from Stage 01):
  - `save_audit_log`: `payroll.py:954`, `payroll_approval_service.py:97,170,245`, `payroll_retry_service.py:797`, `payroll_run_persister.py:98`
  - `save_event`: `payroll.py:960`, `payroll_approval_service.py:98,171,246`, `payroll_retry_service.py:803`, `payroll_run_persister.py:104`
- Both builders (`build_transition_audit`, `build_transition_event`, `backend/domain/payroll/audit_events.py:16-67`) hardcode `entity_type`/`aggregate_type = "PAYROLL_RUN"`.
- `reconciliation_service.py`: zero calls to either function — confirmed again in this stage.
- Employee/salary-definition/pay-cycle PATCH routes in `workspace.py`/`employees.py`: zero calls to either function — confirmed again.
- The one intervening commit (`68e9307`) added a new terminal `FAILED` status that also writes via these same shared builders — this is more volume of the same `PAYROLL_RUN`-only pattern, not an extension to a new entity type.

## Required separation of audit concerns (per this stage's investigation)

| Audit concern | Current coverage |
|---|---|
| Payroll-run state-transition audit | Covered — the one thing this mechanism does |
| Domain-change audit (salary_definition, pay-cycle, contract edits) | **Not covered** — zero instrumentation |
| Agent/tool invocation audit | **Not applicable yet** — no agent/tool layer exists (per `event-notification-readiness.md`), but this is a forward-looking requirement once one does |
| Exception-resolution audit | **Not applicable yet** — no exception-resolution workflow exists (per Stage 04 F-04-01), but any future implementation must write here |

## Consequence for downstream operational-reporting outcomes

Stage 04 (F-04-06) identified "operational reporting and continuous improvement" as a lifecycle area with zero capability coverage, explicitly gated on this audit-coverage fix. This stage's re-verification confirms that gate is still fully closed — recurring-error reporting, control-completion evidence, and configuration-change history all require domain-change audit coverage that does not exist today for any table except `payroll_run`.

## Minimum audit expansion needed before downstream capabilities rely on historical operational reporting

1. Generalize `save_audit_log`/`save_event` (or introduce parallel functions) to accept an arbitrary `entity_type`, not hardcode `PAYROLL_RUN` — a signature change, not a new mechanism.
2. Add call sites at the salary-definition, pay-cycle, and contract-change PATCH routes, at minimum.
3. Add call sites to `reconciliation_service.py`'s `resolve_reconciliation` — this is the single highest-value addition, since it's the one write path in the entire reconciliation flow that currently leaves no attributable trail of who resolved a MISMATCH and when (only `resolved_by`/`resolved_at` columns on the reconciliation row itself, which capture the fact but not a durable, cross-entity-queryable event).

This is scoped as a technical readiness fact for Stage 06/08 to act on — this stage does not design the expanded audit schema itself, per its explicit constraint against final tool/mechanism design.
