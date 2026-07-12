# Remediation Summary — 04-001 + 05-001

**Sprint:** Immediate remediation, per
`docs/audit-program/remediation-prompts/2026-07-12-04-001-05-001-immediate-remediation-sprint-prompt.md`
(commit `6e1d949`), executed under Stage 05's approved canonical contract
(`docs/audit-program/05-snapshot-integrity/findings.md` §9).

**Date:** 2026-07-12

---

## 04-001 — Snapshot-first statutory retry

### What changed

`backend/application/payroll_retry_service.py::_build_shared_context` no
longer queries live `statutory_rule`/`tax_band` tables. It now reads
exclusively from `payroll_run.rules_context_snapshot["statutory_rule"]`
(the exact content the original run froze), and hard-fails before any
calculation, deletion, or write if that content is not a complete v2
snapshot — never falls back to a live query.

- Removed: the `SELECT ... FROM statutory_rule ... ORDER BY effective_from
  DESC ...` and `SELECT ... FROM tax_band ...` queries, and the `workspace`
  JOIN that existed solely to supply `country_code` to the first of those
  (now unused — removed along with it).
- Added: a validation block checking `snapshot_version == 2` and that
  `statutory_rule.id`/`.version`/`.rules_jsonb`/`.tax_bands` are all
  non-null, raising `ValueError(f"Run {payroll_run_id} predates the v2
  statutory snapshot — open a correction run.")` on failure — same wording
  family as the existing `validate_snapshot_complete()` hard-fail.
- The existing `Decimal(str(...))` extraction/normalization logic
  (pension, rent relief, NHF, health insurance, development levy, life
  insurance) is unchanged — it now runs against the frozen `rules_jsonb`
  instead of a freshly-queried one, per Stage 05's §8 finding that the
  snapshot was already sufficient.

### A blocking gap found and fixed during implementation

While verifying the fix, `tests/test_payroll_retry.py`'s existing PENSION
rule (no `effective_from`) started failing retry with the new hard-fail —
tracing this back, `payroll.py`'s `rules_context_snapshot` construction
only emitted v2 format `if rule_set_id:`, and `rule_set_id` is only
non-null when the workspace has a **published rule_set**, which onboarding
only creates for payroll rules that carry an `effective_from` date. A query
against the local dev database confirmed **47 of 70 workspaces (67%) have
no `rule_set` at all** — meaning the 04-001 fix as originally scoped would
have made every retry-eligible run in those workspaces hard-fail, not just
genuinely legacy runs. This was not a hypothetical: it is the majority
case in the observed data.

Root cause: `build_rules_context_snapshot`'s v2/v1 branch was keyed on
`rule_set_id` presence, coupling two independent concerns — "does this
workspace have custom payroll rules" and "should the run's statutory
content be frozen." Fixed by decoupling: v2 format is now emitted whenever
statutory content OR `rule_set_id` is supplied (either signals a v2-format
request); a workspace with no published rule_set gets a v2 snapshot with
`"rule_set": None` rather than being silently downgraded to the v1,
statutory-content-free format.

Files touched by this correction: `backend/domain/rules/snapshot.py`
(condition + docstring), `backend/api/routes/payroll.py` (always calls the
v2-requesting branch; `rule_set_id`/`rule_set_effective_from`/
`rule_set_items_for_snapshot` are already `None`/`None`/`[]` when no rule
set exists, from existing code above this call site).

This was judged in-scope, not scope creep: without it, the approved
04-001 fix could not function correctly for the majority of observed
workspaces — implementing the letter of the specification while leaving it
non-functional in the common case would not have satisfied the sprint's
actual intent.

### Legacy/malformed snapshot handling

Per §6 of the Stage 05 contract, no tier falls back to a live query:

- **Pre-snapshot-engine runs** (no `employee_contract_snapshot`/
  `component_metadata_snapshot` rows): already hard-failed by the
  pre-existing `validate_snapshot_complete()` check, unchanged.
- **v1 ID-only snapshots** (`rules_context_snapshot` has `statutory_rule.id`/
  `.version` but no `.rules_jsonb`/`.tax_bands`) and any run whose
  `snapshot_version` is absent or not `2`: now hard-fail via the new
  validation block, with the correction-run error.
- **v2-complete snapshots**: proceed as before, reading frozen content.

---

## 05-001 — Fail-visible snapshot creation

### What changed

`backend/api/routes/payroll.py::_calculate_and_persist`'s snapshot-creation
`try/except` no longer swallows the exception and continues. On failure it
now:

1. Marks the run `FAILED` with an operator-visible `error_message`
   (`backend/infra/repositories/payroll_run_repo.py::mark_payroll_run_failed`,
   new function).
2. Writes the same `audit_log`/`event_store` entries the normal
   DRAFT→CALCULATING transition would have written, reusing the existing
   `build_transition_audit`/`build_transition_event` builders — no new
   audit mechanism invented.
3. Returns immediately — `execute_and_persist(...)` and
   `link_inputs_to_run(...)` are never called, so no `payroll_result` row
   is written and no employee input is claimed for a run whose snapshot
   never persisted.

### Lifecycle design chosen

A new terminal `FAILED` status was added to `PayrollRunStatus`
(`backend/domain/payroll/status.py`), reachable only from `DRAFT`
(`backend/domain/payroll/state_machine.py`). This is a **new** status
value, not an overload of an existing one, per `CLAUDE.md`'s "New
status/enum values are introduced, never overloaded with new meaning"
rule — existing states were judged insufficient because:

- Leaving the run at `DRAFT` would be indistinguishable from a normal
  run that simply hasn't been picked up by the background task yet — an
  operator has no way to tell "stuck" from "about to run."
- No `payroll_run.error_message`-equivalent column existed to attach a
  reason to any existing status.

Migration `b8c9d0e1f2a3` (revision chain: `ef2a3b4c5d6e` → `b8c9d0e1f2a3`):

- Adds nullable `payroll_run.error_message TEXT`, guarded per `CLAUDE.md`'s
  ADD COLUMN convention (`DO $$ ... EXCEPTION WHEN duplicate_column THEN
  NULL; END $$`).
- Extends `validate_payroll_status_transition()` (the DB-level trigger) to
  recognize `FAILED` at the same lifecycle rank as `DRAFT` (rank 1) — it is
  reachable only from `DRAFT` and the trigger's forward-only rule requires
  rank to never decrease.
- Full, symmetric `downgrade()` restoring the pre-migration trigger body
  and dropping the column.

`GET /{workspace_id}/payroll/runs/{run_id}` now returns `error_message` in
its response, so the failure is visible via the API — not only in server
logs.

### Explicitly out of scope (per the sprint prompt)

- **05-004** (broad immutability-trigger harmonisation across
  `component_metadata_snapshot`, `client_component_metadata_snapshot`,
  `employee_contract_snapshot`, and uncovered `payroll_result` columns) —
  deferred to Stage 13, per the Stage 05 close decision. Not touched.
- **04-002** (per-result `statutory_rule_id`/`statutory_version` columns)
  — not implemented; not technically required by either approved fix.
  Remains a separate follow-up.

### Immutability preserved

`create_payroll_snapshot()`'s own atomic three-table commit is unchanged.
The pre-existing `trg_run_snapshot_immutable` trigger on
`rules_context_snapshot` was not touched by either fix. No new
update-in-place behaviour was introduced for any snapshot content — the
new `FAILED` transition only updates `status` and `error_message`, neither
of which is snapshot content.

---

## Files changed

| File | Change |
|---|---|
| `backend/application/payroll_retry_service.py` | 04-001: snapshot-first statutory read, removed live queries, removed now-unused `country_code`/workspace JOIN, updated docstring |
| `backend/api/routes/payroll.py` | 04-001: always request v2 snapshot format; 05-001: fail-visible snapshot-creation handling; `error_message` added to `GET .../runs/{run_id}` |
| `backend/domain/rules/snapshot.py` | 04-001 blocking-gap fix: decoupled v2 emission from `rule_set_id` presence |
| `backend/domain/payroll/status.py` | 05-001: added `FAILED` status |
| `backend/domain/payroll/state_machine.py` | 05-001: added `DRAFT → FAILED` transition |
| `backend/infra/repositories/payroll_run_repo.py` | 05-001: added `mark_payroll_run_failed()` |
| `migrations/versions/b8c9d0e1f2a3_add_failed_payroll_run_status.py` | 05-001: `error_message` column + DB trigger update for `FAILED` |
| `tests/test_payroll_retry_snapshot_first.py` | New — 5 regression tests (3 for 04-001, 2 for 05-001) |
| `tests/test_payroll_retry.py` | Fixed pre-existing test gap: PENSION rule lacked `effective_from`, so it exercised the legacy pre-rule-set path rather than current production behaviour |
| `tests/test_payroll_pipeline_e2e.py` | Updated snapshot-shape assertion for the now-always-v2 format |
| `tests/test_payroll_run_snapshot_immutable.py` | Same update as above |
| `tests/test_status.py` | Updated expected enum set to include `FAILED` |

See `verification.md` for test commands and results.
