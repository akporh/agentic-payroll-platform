# Human Decisions Log

Records decisions in this audit programme that require Michael's judgment
rather than more evidence — risk acceptance, scope calls, and approval to
proceed on anything outside a stage's default read-only, evidence-gathering
remit.

Logged here, not in a stage's `findings.md`, because these are decisions
*about* findings, not findings themselves.

## When an entry is required

- Any finding reaching **S0 — Critical** at `plausible` or `confirmed`
  status (per `severity-model.md` escalation rule).
- Any case where a stage is blocked because required evidence cannot be
  obtained without touching `backend/`, `frontend/`, or `migrations/`.
- Approval to open a stage before its declared dependency has reached
  `complete`.
- Approval of the Stage 13 backlog itself, and of the decision to begin
  production-code remediation afterward (which happens outside this
  workspace, as an ordinary sprint).
- Any decision to mark a stage `complete` with open, unresolved findings
  (i.e., accepting residual risk rather than blocking).

## Log

| Date | Decision needed | Context | Options | Decision | Decided by |
|---|---|---|---|---|---|
| 2026-07-11 | Is an empty `component_metadata` list meant to silently trigger the legacy executor fallback, same as an absent one? | Finding 01-004: `backend/api/routes/payroll.py:866` coerces `[]` to `None` before calling into `execute_single_employee_payroll`; `executor.py:108`'s `if component_metadata:` check treats `None` and `[]` identically. `CLAUDE.md`'s Executor Paths note only describes the `None` case and separately directs "migrate all callers" away from the legacy path. | (a) Intended — a workspace with no configured components should fall back silently; (b) Unintended — should instead surface as an onboarding-incomplete error; (c) Defer classification to Stage 02 (execution trace baseline), which will characterize how often this actually fires in practice | pending | — |
| 2026-07-11 | Is `backend/infra/db/repositories/workspace_repo.py` an intentional second repository layer, or migration debt? | Finding 01-002: this ORM-based file is imported only by three onboarding-domain modules, separate from the 14-file raw-SQL `backend/infra/repositories/` layer that `CLAUDE.md`'s architecture table describes as the sole repository location. | (a) Intentional isolation of onboarding-status checks; (b) Incomplete migration — should be consolidated into `backend/infra/repositories/`; (c) Leave open, revisit if a later stage (e.g. Stage 06 wiring) surfaces a concrete problem caused by the split | pending | — |

| 2026-07-11 | Is `docs/wrapper-command/` (an agent-instruction set addressed to "Casper," covering engineering-playbook rules, architecture-check prompts, and a payroll "SYSTEM GUARD") still authoritative, and how does it relate to `CLAUDE.md`? | Finding 01-013: this instruction set was not surfaced in the audit programme's original repository orientation and was found only during continued Stage 01 execution. Its currency, ownership, and relationship to `CLAUDE.md` (which this audit programme treats as the sole governing instruction source) is unknown. | (a) Superseded by `CLAUDE.md` — archive or mark deprecated; (b) Still in active use alongside `CLAUDE.md` for a distinct purpose ("Casper" tooling) — document the relationship; (c) Unknown — treat as non-authoritative for now, no further classification | **(c) Unknown — treat as non-authoritative for now.** "Casper" confirmed to be Michael's name for his coding agent (i.e. this agent), not a separate third-party tool — but no content-level comparison against `CLAUDE.md` was performed, and none is authorized at this time. `docs/wrapper-command/` must not be cited as an authoritative source in any later audit stage; `CLAUDE.md` remains the sole governing instruction source. | Michael |

**Resolved 2026-07-11.** The other two entries remain pending — they are recorded per the escalation rule so they are visible ahead of later stages rather than re-discovered.

| 2026-07-11 | Should per-employee retry produce the same `execution_trace` step-level audit footprint as an original run? | Finding 02-002 (Stage 02): `payroll_retry_service.py::retry_failed_payroll_employees` instantiates an `ExecutionTracer` but never calls `.step(...)`, so retries write zero rows to `execution_trace`, while original runs write ~7–9. `component_trace_jsonb` (per-employee, per-component) is unaffected — only the coarser run-level step trace is missing for retries. | (a) Acceptable as-is — `payroll_result.status`/`error_message` plus audit_log/event_store already capture retry outcomes at the row level; (b) Add `tracer.step(...)` wrapping to retry so it mirrors the original run's step trace; (c) Defer to Stage 04 (original-run and retry parity), which depends on this Stage 02 baseline and is the next stage scoped to compare original-vs-retry behaviour in depth | pending | — |
| 2026-07-11 | Should `export_payroll_register_csv` (and its siblings `export_net_pay_csv`, `export_paye_summary_csv`) be fixed and wired up, or retired? | Finding 02-009 (Stage 02): `export_payroll_register_csv` assumes `gross_components_jsonb` is a `list[dict]`; production (`executor.py:343-347`) writes it as `dict[str, dict]`. The function has zero production callers today, so this cannot currently corrupt a live export, but was already flagged as a backlog gap in prior analysis (`project_sprint6_backlog.md` memory: P0-3/P1-4/P1-5). Its own test script (`backend/scripts/test_export_register.py`) uses dummy data in the old list shape, masking the mismatch. | (a) Fix the shape mismatch and wire the export into an API route as part of closing the export gap; (b) Retire these three export functions if exports are being redesigned differently; (c) Leave open for Stage 13's consolidated backlog to prioritize alongside the other export gaps | pending | — |
