---
name: Audit Programme State
description: Current stage and status tracker for docs/audit-program/
type: project
---

# Audit State

**Next action:** Stage 08 closed 2026-07-13. Open **Stage 09 — Security
and tenant isolation** (not started). Headline Stage 08 result: **`04-004`
rejected** — closed with no remediation required; retry and reconciliation
cannot overlap for the same run by lifecycle construction. Three confirmed
S2 findings carried forward: 08-001 (nullable `employee_number` despite a
migration named to enforce `NOT NULL` — its `ALTER` is guarded by a
swallow-all `EXCEPTION WHEN others`), 08-002 (`payroll_run` totals/period
fields DB-protected only at `PAID`, no active mutation path found),
08-003 (disabled statutory components filtered with no compliance guard
or trace signal — `03-004`'s policy question remains open, not resolved).
No financial miscalculation or data corruption found. `04-001`/`05-001`
remain remediated (not reopened); `05-004` deferred to Stage 13.

## Stage 08 handoff summary

- **`04-004` — closed, rejected, no remediation required.** Retry
  (`PARTIAL`-only) and reconciliation (`LOCKED`-only, reachable only via
  `CALCULATED→APPROVED→LOCKED`) cannot overlap for the same run — proven
  via four independent, redundant guards (state machine, approval
  transition check, reconciliation status guard, duplicate-reconciliation
  guard).
- **`08-001` (confirmed, S2) → Stages 11, 13.** `employee.employee_number`
  nullable despite migration `c9d0e1f2a3b4`'s stated intent — its `ALTER
  COLUMN ... SET NOT NULL` is wrapped in `EXCEPTION WHEN others THEN
  NULL`. Cheapest of this stage's findings to fix (corrective migration +
  properly-guarded re-application); the underlying swallow-all pattern is
  worth a broader migration grep before Stage 13 finalizes scope (one
  other, lower-risk occurrence already found and ruled out this stage).
- **`08-002` (confirmed, S2) → Stages 11, 13.** `payroll_run`'s own
  totals/period fields lack DB-level immutability until `PAID` (one stage
  later than `payroll_result`'s protection). No active application
  mutation path found — defence-in-depth gap, not an active exploit.
- **`08-003` (confirmed, S2) → Stages 09, 10, 13.** Disabled statutory
  components are filtered from engine input with no class-aware guard and
  no trace/audit signal of omission. Correct mechanical engine behaviour,
  distinguished from the missing guard/signal. `03-004`'s policy question
  (should statutory components be disableable at all) remains **open**,
  preserved unchanged for Stage 13.
- **`07-002` → Stage 13, as an audit-consistency issue specifically** —
  Stage 08 confirms the underlying reconciliation data itself is correct
  and complete; the gap is the absence of a unified `audit_log`/
  `event_store` entry, not data corruption.
- **Positive controls confirmed**, not carried forward as action items:
  contract-overlap GIST exclusion constraint, active-contract partial-
  unique index, `payroll_result`'s three-layer immutability trigger set,
  reconciliation's MATCHED/MISMATCH CHECK constraints (the strongest
  DB-level invariant enforcement found anywhere in this audit programme),
  and payroll-input validation constraints.

## Stage 07 handoff summary

- **`07-001` (confirmed, S1) → Stages 09, 13.** 21 sites returning raw
  exception text to API clients, violating `CLAUDE.md`'s standing
  prohibition for the third documented time. Stage 09 should determine
  which sites can leak genuinely sensitive detail versus which are safe
  today; Stage 13 should prioritize this near `04-001`'s historical S0.
- **`07-002` (confirmed, S2) → Stages 08, 13.** Reconciliation create/
  resolve actions write no `audit_log`/`event_store` entry — captured
  locally on `payroll_reconciliation` itself, but absent from the unified
  audit view every other transition uses.
- **`07-003` (confirmed, S2) → Stages 11, 13.** The background
  calculation task's outer exception handler remains log-only outside the
  `05-001`-remediated snapshot-creation step.
- **`07-004` (confirmed, S3) → Stage 12.** Stray `print()` at module scope
  in `backend/domain/rules/paye.py` — trivial removal.
- **`07-005` (resolved, confirmed) + `04-002` (unchanged recommendation)
  → Stage 10.** Retry's `execution_trace` should carry a defined minimal
  subset (invocation/preflight outcome, per-employee outcome, final
  transition) rather than full parity or zero rows; `04-002`'s
  recommendation (per-result `statutory_rule_id`/`statutory_version`
  columns) is unchanged from Stage 05 §10. Both are decisions/
  recommendations only — Stage 10 designs, does not implement in this
  audit workspace.
- **Positive controls confirmed**, not carried forward as action items:
  approval/lock/pay audit trail complete and consistent; per-employee
  original-run failures fully observable end to end; `04-001`'s
  legacy-snapshot retry rejection has a well-labeled frontend modal
  (`EMP-UX-3`) with good recovery guidance; `component_trace_jsonb`
  confirmed complete and accurate for both original runs and retries.

## Stage 06 handoff summary

- **`06-001`/`06-004` (confirmed) → Stage 13.** The `05-001` remediation's
  frontend consumption gap — `PayrollRunStatus` type missing `FAILED`,
  `StatusBadge` falls back to generic gray, `ActionPanel` returns `null`
  for `FAILED` runs. Both share one root cause (the frontend type) and are
  a natural single small follow-up sprint.
- **`06-002` (confirmed) → Stage 08, Stage 13.** `pay_cycle.definition_json`
  affects runtime (via `pay_cycle_definition` in the calculation context)
  but has been unreachable for view or edit since onboarding — no GET
  route returns it, the PATCH route doesn't accept it.
- **`06-003` (confirmed) → Stage 13.** `RunPayroll.tsx` offers `FULL_RUN`
  as a retry-strategy option; the backend allowlist is `{"PER_EMPLOYEE"}`
  only — always rejected on submission.
- **`06-006` (confirmed at close review) → Stage 13.** `GET .../timesheet/
  audit/{employee_id}` is a missing UI feature (bureau-operator workflow
  for explaining timesheet-to-payroll-input interpretation), not
  intentionally API-only. Backend route retained as the correct source.
- **`06-007` (confirmed) → Stage 09, Stage 12.** Unscoped
  `/payroll/run/{run_id}/reconcile` (GET/POST) is dead code, superseded by
  the workspace-scoped reconciliation routes — Stage 09 should verify its
  tenant-scoping before Stage 12 removes it (not verified in Stage 06).
- **`06-005` (confirmed, S3) — no further action required.** D-ARCH-1
  salary-definition edit lock is correctly enforced and its error
  correctly surfaced, just reactively rather than proactively — a UX
  polish opportunity, not a wiring gap.
- **Positive controls confirmed**, not carried forward as action items:
  retry mechanism correctly wired for `PARTIAL` runs including the
  legacy-hard-fail modal (`EMP-UX-3`); component-override
  `proration_strategy`/`is_active` dual-storage precedence (Stage 03's
  03-001) correctly reflected end-to-end in the UI; all 4 export types
  fully wired.

## Immediate remediation sprint — 04-001 + 05-001 — COMPLETE

- **Status:** complete, reviewed and approved 2026-07-12
- **Primary records:** `docs/audit-program/remediation/04-001-05-001/summary.md`,
  `docs/audit-program/remediation/04-001-05-001/verification.md`
- **04-001:** remediated — retry reads `rules_context_snapshot["statutory_rule"]`
  exclusively; live `statutory_rule`/`tax_band` queries removed from the
  retry path; legacy/incomplete snapshots hard-fail with no live fallback.
  The Stage 04 controlled reproduction script now returns `REJECTED`.
- **05-001:** remediated — snapshot-creation failure marks the run `FAILED`
  (new terminal status, migration `b8c9d0e1f2a3`) with an operator-visible
  `error_message`, and aborts before any calculation or persistence.
- **05-004:** correctly NOT touched, per the Stage 05 close decision —
  remains a Stage 13 backlog item.
- **04-002:** correctly NOT touched — remains a separate follow-up, open
  for Stages 07/10.
- **Tests:** 5 new regression tests
  (`tests/test_payroll_retry_snapshot_first.py`) plus 4 pre-existing tests
  updated for a shape change caused by the blocking-gap fix (not a
  behaviour change to what they verify) — see verification.md.
- **Schema impact:** one migration (`b8c9d0e1f2a3`) for 05-001's
  `error_message` column and `FAILED` status; none required for 04-001
  itself, confirming Stage 05 §8's sufficiency analysis. Reversibility
  confirmed by an actual `alembic downgrade -1` / `upgrade head` cycle
  during close review.
- **Acceptance criteria:** 9/9 met.

## Stage 05 handoff summary

- **`04-001` remediation specification approved as ready for
  implementation** — see Stage 05 `findings.md` §9 (canonical snapshot-first
  retry contract) and the "Immediate remediation handoff" section added at
  stage close.
- **`05-001` (S2, confirmed) bundled into the same sprint** — snapshot
  creation for component metadata, client overrides, and employee contracts
  runs in a background task with its exception silently logged and
  swallowed; the run proceeds to calculate/persist regardless, only
  surfacing later as a permanently retry-blocked run with no visible cause.
  The remediation must make this fail visibly.
- **`05-004` (S2, confirmed) deferred to Stage 13**, with Stage 12 input
  where relevant (Stage 12 candidate: harmonizing immutability triggers
  across `component_metadata_snapshot`, `client_component_metadata_snapshot`,
  `employee_contract_snapshot`, and uncovered `payroll_result` columns).
  **Standing constraint carried into the remediation sprint regardless:**
  any snapshot schema or write path the `04-001`/`05-001` work touches must
  preserve or strengthen existing DB-level immutability guarantees, never
  weaken them.
- **05-002/05-003/05-005** (dead column, unread audit column, duplicated
  extraction logic) pass to Stage 12 (simplification) as documented in
  Stage 05 `findings.md`'s handoff section — not part of the immediate
  sprint.
- **04-002** (no persisted statutory-identity field) — Stage 05 §10
  recommends per-result `statutory_rule_id`/`statutory_version` columns on
  `payroll_result`; recommended to bundle into the same remediation sprint
  (small additive migration touching the same insert call sites) but not
  mandated — passes to Stage 07/10 either way.

## Stage 04 handoff summary

- **`04-001` (S0, confirmed, release blocker):** retry re-resolves the
  statutory rule/tax bands live instead of reading the frozen
  `rules_context_snapshot.statutory_rule`; reproduced with a controlled,
  self-cleaning non-production test (zero residue confirmed). Canonical fix
  direction already decided: retry must consume the frozen snapshot content;
  legacy runs lacking v2 statutory snapshot content must hard-fail, never
  silently fall back to a live re-query. Stage 05 validates and specifies
  this fix (read-only — no code changes in Stage 05); the actual remediation
  sprint follows immediately after, ahead of Stage 13, before any live
  payroll processing or production release.
- **`04-002` (S1, confirmed):** no persisted field records which
  statutory-rule version a `payroll_result` row was actually calculated
  under — compounds `04-001` by preventing retroactive detection. Passes to
  Stage 05 (should statutory identity be persisted per result?), Stage 07,
  and Stage 10.
- **`04-004` (unconfirmed):** reconciliation-refresh behaviour on retry
  completion was not investigated this stage — passes to Stage 08.
  **Update (Stage 08, 2026-07-13): rejected** — retry and reconciliation
  cannot overlap for the same run by lifecycle construction; see Stage 08
  handoff summary above.
- The controlled reproduction script
  (`04-original-run-retry-parity/evidence/statutory_divergence_controlled_test.py`)
  passes to Stage 11 as the basis for a formal regression scenario once the
  fix lands.

## Stage 03 handoff summary

- **03-002** is the primary Stage 04 input — Stage 04 should reproduce the
  statutory-rule original-run/retry divergence using controlled
  non-production execution (insert a test `statutory_rule` row with an
  intervening `effective_from`, run, retry, compare). Status remains
  `plausible` until reproduced.
- **03-003** (dead `employee_contract_snapshot.components_jsonb` column)
  passes to Stage 05 (snapshot integrity — is the snapshot itself complete
  and correct independent of consumption?) and Stage 12 (simplification —
  removal candidate).
- **03-004** (statutory-deduction components can be disabled per workspace;
  D-ARCH-2 guard present but explicitly unenforced) passes to Stage 08
  (data integrity — any live workspace currently doing this?) and Stage 09
  (security/tenant isolation).
- UI coverage gaps, including `pay_cycle.definition_json` (not traced to a
  specific UI control in Stage 03), pass to Stage 06 (UI/API/backend
  wiring).

## Stage status

| # | Stage | Status | Opened | Closed | Blocking issue |
|---|---|---|---|---|---|
| 01 | System inventory | complete | 2026-07-11 | 2026-07-11 | — |
| 02 | Execution trace & diagnostic-script baseline | complete | 2026-07-11 | 2026-07-12 | — |
| 03 | Configuration integrity | complete | 2026-07-12 | 2026-07-12 | — |
| 04 | Original-run and retry parity | complete | 2026-07-12 | 2026-07-12 | — |
| 05 | Snapshot integrity | complete | 2026-07-12 | 2026-07-12 | — |
| 06 | UI/API/backend wiring | complete | 2026-07-12 | 2026-07-12 | — |
| 07 | Silent failures and observability | complete | 2026-07-12 | 2026-07-12 | — |
| 08 | Data integrity | complete | 2026-07-12 | 2026-07-13 | — |
| 09 | Security and tenant isolation | not-created | — | — | — |
| 10 | Execution-trace remediation (findings + design only — no code changes) | not-created | — | — | — |
| 11 | Scenario testing | not-created | — | — | — |
| 12 | Code simplification | not-created | — | — | — |
| 13 | Consolidated backlog | not-created | — | — | — |

## Open human decisions

Five genuinely open (no decision made yet); the rest below are resolved,
several this session — see [`_core/human-decisions.md`](_core/human-decisions.md) for full decision text:
- Empty `component_metadata` list silently triggering legacy executor fallback (finding 01-004)
- Second, ORM-based repository directory `backend/infra/db/repositories/` vs. documented single repository layer (finding 01-002)
- Authority/currency of `docs/wrapper-command/` agent-instruction set ("Casper") relative to `CLAUDE.md` (finding 01-013) — resolved (c) treat as non-authoritative
- ~~Should per-employee retry produce the same `execution_trace` step-level footprint as an original run?~~ — **resolved 2026-07-12 (as 07-005)**: a defined minimal subset (invocation/preflight, per-employee outcome, final transition), not full parity and not zero — see finding 07-005.
- Should `export_payroll_register_csv` and siblings be fixed or retired? (finding 02-009)
- Should retry read the frozen statutory-rule snapshot instead of re-resolving live? (finding 03-002) — resolved: yes, per 04-001's remediation specification
- Is `employee_contract_snapshot.components_jsonb` meant to ever be read? (finding 03-003) — effectively resolved via 05-002: no, confirmed safe to remove in Stage 12
- Should workspaces be able to disable statutory-deduction components (D-ARCH-2 currently unenforced)? (finding 03-004)
- ~~Is `timesheet/audit/{employee_id}` intentionally operator/API-only, or a missing UI feature?~~ — **resolved 2026-07-12**: missing UI feature, backend route retained, carried to Stage 13.
- Should the systemic `str(e)`-leak pattern (07-001) be a dedicated priority fix, flow through Stage 13 normally, or bundle with Stage 09's security review? (finding 07-001)
- ~~What is the intended `execution_trace` parity level for retry?~~ — **resolved 2026-07-12**: defined minimal subset — see finding 07-005.
- ~~S0 — 04-001 urgency and fix direction~~ — **resolved 2026-07-12**: confirmed S0 release blocker; remediation specification approved, ahead of Stage 13, before any live payroll processing or production release.
- ~~Should 05-001/05-004 be bundled with the 04-001 sprint?~~ — **resolved 2026-07-12**: 05-001 bundled in; 05-004 deferred to Stage 13 (immutability of the run must be preserved/strengthened, never weakened, by whatever the sprint touches).

## Notes

- Updated at the end of each working session on this audit, never mid-stage.
- Production-code remediation for any finding does not begin until Stage 13
  produces an approved backlog (see `README.md`, `WORKFLOW.md`) — `04-001`
  and `05-001` were the sole, explicitly decided exception (finalized at
  Stage 05 close), and that remediation is now **complete and closed**
  (2026-07-12) — see the section above. `05-004` was considered for the
  same exception and explicitly declined — it stays in the normal Stage 13
  backlog. No other finding carries this exception.
- The remediation sprint happened outside `docs/audit-program/`'s read-only
  remit, under `CLAUDE.md`'s normal sprint workflow, exactly as designed —
  this audit programme resumes its own read-only stages from Stage 06.
