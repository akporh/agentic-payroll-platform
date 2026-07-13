---
name: Audit Programme State
description: Current stage and status tracker for docs/audit-program/
type: project
---

# Audit State

**Next action:** Stage 12 closed 2026-07-13. Open **Stage 13 —
Consolidated remediation backlog** (not started). Read-only
code-simplification design stage — no code/migration/test/script
modified throughout. Re-verified `01-002` (ORM repository layer):
genuinely distinct responsibility, recommend rename+document, not
consolidation. `01-004` (legacy executor fallback): confirmed reachable
from the **live production route**, not merely "old CLI callers" as the
code's own stale comment claims — **resolved at close as a phased
migrate-then-remove programme** (8 steps: telemetry → production
inventory → classify occurrences → migrate/repair configuration → prove
zero fallback usage over an observation window → hard-fail new runs →
remove default path), with 7 Stage 13 acceptance criteria, explicitly
not an immediate hard-fail and explicitly not backed by the dev-DB 9.3%
figure alone. Re-verified `05-002` (dead snapshot column, safe to remove)
and `05-005` (duplicated statutory-extraction logic — confirmed **still
fully live** even after the `04-001` remediation shipped, since that fix
changed *where* the data comes from but not the duplicated parsing
logic). **New finding:** `PayrollRunStatus` is defined twice in the
frontend, in two different modules, each wrong in a different way —
`types/payroll.ts` (used to type the real API field) is missing `FAILED`
entirely, while `design-system/components/Status.tsx` uses `'PENDING'`
instead of `'DRAFT'`. This sharpens `06-001`/`06-004`'s root cause with a
precise citation. `06-007`'s legacy reconciliation route identified as
the one genuine "just delete it" candidate in the whole unscoped-route
family (zero callers, fully-shipped replacement) — every other unscoped
lifecycle/admin route is load-bearing and blocked by Stage 09's security
architecture, not a simplification candidate. Migration hygiene:
swallow-all `EXCEPTION WHEN others` pattern confirmed bounded to exactly
the two already-known migrations, no others found. All findings carried
to Stage 13 exactly as classified — independently-safe,
bundle-with-remediation, blocked-by-architecture, retain-intentionally,
plus the resolved legacy-fallback programme.

## Stage 12 handoff summary (complete)

- **Repository-layer duplication (§2).** Retain both, rename/document —
  not consolidation; zero functional overlap confirmed.
- **Legacy executor fallback (§3) — resolved at close.** Phased
  migrate-then-remove programme (8 steps, 7 Stage 13 acceptance criteria);
  immediate hard-fail, permanent retain, and replay-only were each
  explicitly rejected with stated rationale; dev-DB 9.3% firing rate must
  not be cited as production evidence for the observation-window step.
- **Snapshot cleanup (§4).** `05-002` safe to remove; `05-003` retain
  intentionally (stated future audit purpose); `05-005` still fully live
  post-`04-001`, recommend extracting one shared pure-function helper.
- **Route removal matrix (§5).** Legacy reconciliation pair — independently
  safe cleanup (zero callers, shipped replacement); every other unscoped
  route (retry/approve/lock/pay/admin/legacy-stats) — blocked by security
  architecture, NOT a deletion candidate (still load-bearing).
- **Trace literal consolidation (§6).** Blocked by Stage 10's unimplemented
  migration; consolidation approach specified for when it lands.
- **Enum/contract duplication (§7).** `PayrollRunStatus` duplicated across
  two frontend modules, both incorrect relative to the 8-value backend
  enum, in different ways. Confirmed S2, bundled with `06-001`/`06-004`'s
  remediation.
- **Business-rule duplication (§8).** `05-005` (see §4); error-to-HTTP
  helper recommended alongside `07-001`'s fix; retry/original-run context
  construction correctly NOT consolidated (different lifecycle semantics).
- **Logging/diagnostics (§10).** `paye.py` print() removal; misleadingly-
  named `backend/scripts/test_*.py` files recommended for rename, not
  deletion (superseded by the 306-test suite but retain ad hoc value).
- **Migration hygiene (§11).** Swallow-all pattern confirmed bounded to
  exactly 2 files, no new instances found.
- **No human decision remains open** — the one raised during investigation
  was resolved at close.
- **Stage 12 is complete**, closed 2026-07-13.

## Stage 11 handoff summary (complete)

- **Automated baseline (§1).** 306 passed, 1 skipped, deterministic, no
  dedicated tenant/security test file exists anywhere in `tests/`.
- **`04-001`/`05-001` (§2, §3).** Re-executed directly, 6/6 passed, both
  remain remediated, no drift since Stage 05's close.
- **`07-003` (§4).** No safe injection seam exists without editing
  production source; documented as a blocked-test specification for
  future implementation, not executed.
- **Retry behaviour matrix (§5).** All tested paths pass via the existing
  suite; `execution_trace` zero-rows-on-retry gap reaffirmed via live
  read-only query, consistent with Stages 02/07/10.
- **Security/tenant scenarios (§12) — six executed LIVE** against local
  `payroll_dev`: unauthenticated workspace enumeration (`09-001`),
  cross-workspace timeline access returning identical data (`09-005`),
  cross-workspace reconciliation access returning a real `MISMATCH`
  financial record identically regardless of workspace (`09-004`, the
  strongest evidence produced in this audit programme for that finding),
  legacy unscoped reconciliation route (`06-007`/`09-002`), global
  legacy-executor-stats leak (`09-006`), unauthenticated admin dashboards
  (`09-007`). All reaffirmed unchanged in status/severity, evidence class
  upgraded to live-executed.
- **`09-008` (§14) — executed and confirmed** via a synthetic, zero-residue
  in-memory CSV-injection proof: a leading `=` reaches the exported cell
  completely unescaped.
- **Stage 10 disposition matrix (§15).** 12 scenarios graded against
  *current shipped behaviour*, not the design's internal coherence — most
  are `blocked-by-unimplemented-design` or `blocked-by-missing-auth`, as
  expected for a design-only prior stage.
- **Coverage gap analysis (§16).** Zero automated tests exist for any
  Stage 09 security finding, `07-003`, `08-001`, `08-002`, `08-003`, or
  `07-001`. 8 permanent-test recommendations produced, each scoped to a
  specific finding's eventual remediation.
- **No new distinct finding.** Every scenario result links to an existing
  finding; none contradicted.
- **No human decision required.**
- **Stage 11 is complete**, closed 2026-07-13. No new human decision was
  raised or required. Carried to Stage 13: `07-003`, `08-001`, `08-002`,
  `08-003`, `09-008`, the Stage 09 security package, the Stage 10 trace
  package (all with this stage's live-test evidence attached), and the
  eight permanent-test recommendations as remediation acceptance criteria.
  `04-004` carries forward rejected, no action required.

## Stage 10 handoff summary (complete)

- **Retry event model (§2).** 4 invocation/preflight events + 1 terminal
  event per retried employee + 3 final-outcome events, all sharing one
  `invocation_id` per retry API call. Matches the binding `07-005` decision
  (minimal subset, not full parity, not zero).
- **`execution_trace` migration (§3, §14).** Additive columns:
  `workspace_id` (NOT NULL, backfilled from `payroll_run.workspace_id`),
  `event_code`, `operation_type` (`ORIGINAL_RUN`/`RETRY`), `invocation_id`,
  `employee_id`, `actor_id`, `metadata_jsonb`, `error_class`. Guarded per
  `CLAUDE.md`'s ADD COLUMN convention, matching downgrade, no destructive
  step.
- **`04-002` per-result statutory identity (§7).** `payroll_result` gains
  nullable `statutory_rule_id`/`statutory_version`, populated going forward
  from the run's own frozen `rules_context_snapshot`; legacy rows stay NULL
  — no backfill from mutable live tables, per the CONTEXT.md constraint.
- **`08-003` excluded-component visibility (§8).** `component_trace_jsonb`
  gains an `outcome` discriminator
  (`executed`/`skipped_eligibility`/`excluded_by_configuration`); one
  run-level `COMPONENT_EXCLUDED_BY_CONFIGURATION` trace row per distinct
  excluded component per run. Policy-neutral — works whether Stage 13
  re-enables `D-ARCH-2` or formalizes controlled disablement.
- **`09-005` secure timeline design (§10).** Target query scopes by both
  `run_id` and the new `execution_trace.workspace_id` column directly (not
  via join-through-`payroll_run` alone). `404`-for-both resource-concealment
  policy chosen over `403`. **Explicitly not implementable until Stage 09's
  authentication/membership/RBAC work exists** — stated as a hard
  dependency, not assumed away.
- **Migration/rollout sequence (§14), 12 acceptance criteria (§15), 12
  Stage 11 regression scenarios (§16), and rejected alternatives (§17)**
  all specified in full — see findings.md.
- **No human decision required** to close Stage 10 as currently specified;
  every design choice resolves against a prior binding decision or this
  stage's own finding rules.
- **Approved at close, unchanged from the initial design.** All 17 design
  sections held at review; the approved trace package carries to Stage 13
  for sequencing/implementation, and the 12 regression scenarios carry to
  Stage 11.
- **Stage 10 is complete**, closed 2026-07-12.

## Stage 09 handoff summary (complete)

- **`09-000` (confirmed, S0).** No authentication mechanism anywhere in
  `backend/` or `frontend/`: no token/session, no `current_user`, no auth
  dependency on any router. CORS defaults `allow_origins=["*"]`. Root cause
  underlying nearly every other finding this stage.
- **`09-001` (confirmed, S0).** `GET /workspaces` returns every workspace
  (id, name, country, currency, status, headcount) to any unauthenticated
  caller — the practical enabler of the IDOR findings below.
- **`09-002` (confirmed, S0) — extends and finalizes `06-007`.**
  Retry/approve/lock/pay and the legacy `/payroll/run/{run_id}/reconcile`
  pair take only `run_id`, no `workspace_id`; the application-service layer
  derives `workspace_id` from the run row itself purely for its own joins,
  never to verify caller entitlement. `06-007` final classification:
  **insecure/tenant-bypass risk**.
- **`09-004`/`09-005` (confirmed, S1).** The nominally workspace-scoped
  reconciliation routes (`GET/POST/PATCH .../reconciliation`) and the
  timeline route (`GET .../timeline`) accept `workspace_id` in the path but
  never pass it to the underlying service call — verified against all five
  function signatures involved, none of which accept a `workspace_id` arg.
- **`09-006` (confirmed, S1).** `GET .../ops/legacy-executor-stats` ignores
  its `workspace_id` path param entirely and returns global stats,
  including per-run breakdowns, across every workspace.
- **`09-007` (confirmed, S1).** `/admin`, `/admin/onboarding`,
  `/admin/payroll` are unauthenticated operator dashboards at predictable
  paths; public reachability is an infrastructure question outside this
  repository's visibility, not resolved here.
- **`09-008` (confirmed, S2).** Payroll CSV exports write employee-controlled
  free-text fields (e.g. `employee_name`) without formula-injection
  sanitization.
- **`07-001` (unchanged S1, classified this stage).** 21 sites: 10 broad
  `except Exception` sites structurally capable of leaking raw DB/schema
  detail (Group A); 11 sites (`ValueError`/custom exceptions) currently
  safe because this codebase's service layer only raises them with
  developer-controlled messages.
- **`03-004`/`08-003`.** Access-control fact confirmed: no role/auth
  distinction exists for statutory-component disablement — same (absent)
  model as every other route. The underlying product-policy question
  remains open under `03-004`, not resolved by this stage.
- **§14 cross-workspace relational consistency — rejected.** No new
  schema/FK-level cross-workspace defect found; the operative risk this
  stage is uniformly at the route/service layer, not the data model.
- **Human decisions — resolved at close.** (1) `09-000` is an unrecognized
  S0 production blocker; app-level authentication and server-side
  authorization are mandatory before any live/production-data use; network
  controls remain defence-in-depth only. (2) Intended model: one bureau
  account manages multiple client workspaces via explicit membership;
  minimum roles are platform administrator, bureau administrator, payroll
  operator, payroll approver, and read-only auditor/viewer; direct
  client-workspace users are deferred but the model must remain extensible
  to them.
- **Stage 09 is complete**, closed 2026-07-12.

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
| 09 | Security and tenant isolation | complete | 2026-07-12 | 2026-07-12 | — |
| 10 | Execution-trace remediation (findings + design only — no code changes) | complete | 2026-07-12 | 2026-07-12 | — |
| 11 | Scenario testing | complete | 2026-07-12 | 2026-07-13 | — |
| 12 | Code simplification | complete | 2026-07-13 | 2026-07-13 | — |
| 13 | Consolidated backlog | not-created | — | — | — |

## Open human decisions

Five genuinely open (no decision made yet); the rest below are resolved,
several this session — see [`_core/human-decisions.md`](_core/human-decisions.md) for full decision text:
- ~~Should the legacy executor fallback be retained with telemetry, hard-failed, migrated-then-removed, or restricted to historical replay only?~~ — **resolved 2026-07-13 at Stage 12 close**: migrate-then-remove, phased 8-step programme (see finding 01-004 / Stage 12 §3).
- ~~Is application-level authentication out of scope by design, or an unrecognized gap?~~ — **resolved 2026-07-12 (as 09-000)**: unrecognized S0 production blocker; app-level auth/authorization mandatory before any live/production-data use.
- ~~What is the intended role model?~~ — **resolved 2026-07-12**: one bureau account manages multiple client workspaces via explicit membership; five minimum roles (platform admin, bureau admin, payroll operator, payroll approver, read-only auditor/viewer); direct client users deferred but the model must remain extensible.
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
