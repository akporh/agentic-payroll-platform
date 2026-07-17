# Stage 08 — Findings

Status: **complete**. All entries below use the template in
[`../_core/finding-schema.md`](../_core/finding-schema.md). Status values
restricted to this stage's five-value set.

---

## Headline results

1. **`04-004` is REJECTED**, with strong structural evidence: the state
   machine makes it **impossible** for a retry to ever occur on a run that
   already has a reconciliation record. Reconciliation requires `LOCKED`
   status; `LOCKED` is only reachable via `APPROVED` ← `CALCULATED`;
   `PARTIAL` (the only retry-eligible status) can *only* transition to
   `CALCULATED`, never directly to `APPROVED`. A run must fully resolve
   every `FAILED` employee (via retry) before it can reach `CALCULATED`,
   long before reconciliation becomes possible. There is no path back from
   `LOCKED`/`PAID` to `PARTIAL`. The specific concern Stage 04 raised
   ("does retry leave a stale reconciliation row, or allow approval
   against outdated totals") cannot occur by construction.
2. **New confirmed finding, 08-001:** `employee.employee_number` is
   **currently nullable** in the live schema, despite a migration
   explicitly named "employee_number NOT NULL" — because that migration's
   `ALTER COLUMN ... SET NOT NULL` is wrapped in a `DO $$ ... EXCEPTION
   WHEN others THEN NULL; END $$` block that silently swallows any failure.
   11 of 4,673 rows in the local dev database currently have a NULL
   `employee_number` (dev data, not cited as production evidence — cited
   only as proof the schema state permits it).
3. **`payroll_result` has excellent, confirmed immutability (positive
   control)**; `payroll_run`'s own total/period fields are protected only
   once `PAID`, one lifecycle stage later than `payroll_result`'s
   protection (`CALCULATED` onward) — see 08-002.

---

## 1. Data-integrity invariant catalogue (selective — highest-value domains)

| Domain | Business rule | DB constraint/trigger | Application guard | Integrity status |
|---|---|---|---|---|
| Employee uniqueness | One `employee_number` per workspace | `ux_employee_number` UNIQUE(workspace_id, employee_number) | Not verified this stage | Confirmed — DB-enforced when non-null |
| Employee number nullability | (implicitly expected NOT NULL per migration name) | **Not enforced** — migration's guard silently failed | Not verified this stage | Confirmed gap — 08-001 |
| Contract overlap | No two contracts for one employee may overlap in time | `excl_employee_contract_no_overlap` EXCLUDE USING gist | N/A — DB-enforced | Confirmed — strong positive control |
| Active contract uniqueness | At most one open-ended (`end_date IS NULL`) contract per employee | `uq_employee_active_contract` partial UNIQUE index | N/A — DB-enforced | Confirmed — strong positive control |
| Payroll result uniqueness | One result per `(payroll_run_id, employee_id)` | `uq_payroll_result_employee_run` UNIQUE | Retry's DELETE-before-INSERT pattern (Stage 02/04) | Confirmed — DB-enforced, consistent with application pattern |
| Payroll result immutability | Results immutable once calculation completes | `prevent_payroll_result_mutation()` — blocks UPDATE/DELETE when parent run status ∈ {CALCULATED, APPROVED, LOCKED, PAID}; explicitly excludes `PARTIAL` | Retry only operates on `PARTIAL` runs | Confirmed — strong positive control, correctly scoped to allow retry's own DELETE+INSERT |
| Payroll run immutability | Run-level totals/period immutable after finalization | `trg_prevent_paid_run_update`/`delete` — **only** fires when status = `PAID` | None found for `APPROVED`/`LOCKED` | Confirmed gap — 08-002 |
| Reconciliation MATCHED/MISMATCH consistency | `MATCHED` ⟺ `actual_total = expected_total`; `MISMATCH` ⟺ they differ | `chk_matched_totals_equal`, `chk_mismatch_totals_differ` CHECK constraints | N/A — DB-enforced | Confirmed — strong positive control, directly enforces `CLAUDE.md`'s invariant at the DB level |
| Reconciliation resolution completeness | `RESOLVED` requires `resolved_by`/`resolved_at` | `chk_resolved_audit_fields` CHECK | N/A — DB-enforced | Confirmed — positive control |
| Reconciliation/retry ordering | Retry must complete before reconciliation is possible | State machine (`PARTIAL→CALCULATED` only; reconciliation requires `LOCKED`) | `reconcile_payroll_run` explicit `LOCKED`-only guard | Confirmed — see headline result 1, `04-004` REJECTED |
| Payroll input validity | Quantity non-negative; unclaimed inputs unique per (workspace, employee, code, date, source) | `ck_payroll_input_quantity_non_negative`, `uq_payroll_input_unclaimed` | Not verified this stage beyond schema | Confirmed — DB-enforced |
| Statutory component enforcement (D-ARCH-2) | Statutory deductions should not be disableable | **Not enforced** — guard explicitly commented out (Stage 03, 03-004) | None | Confirmed gap, extended this stage — 08-003 |
| Snapshot table immutability | Frozen snapshots should not mutate after creation | Only 2 of ~8 mechanisms protected (Stage 05, 05-004) | None beyond convention | Deferred to Stage 13, per Stage 05's decision — not re-investigated here |

---

### 08-001 — `employee.employee_number` is nullable in the live schema despite a migration explicitly intended to enforce `NOT NULL`, because the migration silently swallows `ALTER` failures

- **stage:** 08-data-integrity
- **location:** `migrations/versions/c9d0e1f2a3b4_employee_number_not_null.py:19-22` (`DO $$ BEGIN ALTER TABLE employee ALTER COLUMN employee_number SET NOT NULL; EXCEPTION WHEN others THEN NULL; END $$;`)
- **current implementation:** The migration's own title and docstring ("MIG-18-A: employee_number NOT NULL + workspace-scoped unique index") state its intent clearly, but the `ALTER COLUMN` statement is wrapped in a `DO` block whose `EXCEPTION WHEN others THEN NULL` clause catches and discards *any* error the `ALTER` could raise (most plausibly a not-null-violation if any existing row already had a NULL value at migration time) and allows the migration to report success regardless. Confirmed empirically: the live schema (`\d employee`) shows `employee_number` with no `NOT NULL` marker, and a direct count shows 11 of 4,673 rows in the local dev database currently have `employee_number IS NULL`.
- **intended behaviour:** The migration's name and docstring state the intent unambiguously: `employee_number` should be `NOT NULL`.
- **suspected or confirmed defect:** Confirmed as a migration-safety anti-pattern with a demonstrated real effect (the constraint the migration exists to add is not present). This is distinct from `CLAUDE.md`'s documented ADD COLUMN guard convention (`EXCEPTION WHEN duplicate_column THEN NULL`) — that pattern is safe because it guards against a specific, expected, harmless condition (the column already existing). This migration's guard is a blanket `WHEN others`, which also silently absorbs the *unexpected and consequential* case of pre-existing NULL data, defeating the migration's own purpose without any error, warning, or log entry anywhere.
- **evidence:** `evidence/2026-07-13-employee-number-not-null-migration-silently-failed.txt`
- **status:** confirmed
- **severity:** S2 (a real, confirmed schema-integrity gap with a demonstrated live effect on the current dev database's data; not S1/S0 because a nullable `employee_number` does not itself corrupt payroll calculations — `employee_id`, not `employee_number`, is the actual join/foreign-key used throughout the calculation engine, per every prior stage's citations)
- **pattern scope check:** grepped all of `migrations/versions/` for the same `EXCEPTION WHEN others THEN NULL` pattern — one other occurrence found (`f9a0b1c2d3e4_add_component_override_columns.py`, inside a `downgrade()` dropping columns already guarded by `IF EXISTS`, a much lower-risk use of the same pattern since downgrades are rarely run against production and the outcome doesn't mask a missing constraint). Not treated as a second instance of this finding — recorded here only to confirm the pattern was checked for elsewhere and is not systemic.
- **related invariant:** none in `CLAUDE.md`'s table; this migration is itself the closest thing to a stated invariant, and it is not actually in effect

---

### 08-002 — `payroll_run`'s own total/period fields have no DB-level immutability protection until `PAID`; `payroll_result` rows are protected one lifecycle stage earlier, at `CALCULATED`

- **stage:** 08-data-integrity
- **location:** `payroll_run` triggers (`\d payroll_run`): `trg_prevent_paid_run_update`/`trg_prevent_paid_run_delete` both fire `WHEN (old.status = 'PAID')` only; contrast with `payroll_result`'s `prevent_payroll_result_mutation()` function, which blocks mutation whenever the parent run's status is `CALCULATED`, `APPROVED`, `LOCKED`, **or** `PAID`
- **current implementation:** A `payroll_run` row's own columns (`total_gross_pay`, `total_deduction`, `total_net_pay`, `total_tax`, `period_start`, `period_end`, etc.) can be updated via direct SQL with no trigger objection at any point before the run reaches `PAID` — including while `APPROVED` or `LOCKED`. `rules_context_snapshot` is separately protected by its own dedicated trigger (`trg_run_snapshot_immutable`, unconditional, Stage 05) regardless of status, but the run's financial totals and period fields are not.
- **intended behaviour:** `CLAUDE.md`'s Known Data Contract Rules table states `payroll_run.status = 'APPROVED' — immutable — no employee results can be modified`. Read literally, this invariant is about *employee results*, and `payroll_result`'s own trigger fully satisfies it (confirmed, positive control) — this finding does not claim that specific invariant is violated. It documents a narrower, adjacent gap: the *run's own* totals are not similarly protected until a stage later than its own results are.
- **suspected or confirmed defect:** Confirmed as a real gap by direct trigger-definition citation. Whether it is a *defect* depends on whether any code path could actually reach an UPDATE of these columns for an `APPROVED`/`LOCKED` run — this stage did not find one (every route that changes `payroll_run.status` uses the dedicated transition functions, none of which touch totals after initial calculation), so the gap is currently inert in practice, protected by the absence of a caller rather than by a structural guarantee. This is the same "no current mutation path, but no DB-level guarantee either" pattern Stage 05 already catalogued for `05-004`.
- **evidence:** `evidence/2026-07-13-payroll-run-vs-payroll-result-immutability-gap.txt`
- **status:** confirmed
- **severity:** S2 (defense-in-depth gap, consistent with Stage 05's `05-004` severity reasoning — no live exploitation path found, but no structural guarantee either)
- **related invariant:** `CLAUDE.md` — `payroll_run.status = 'APPROVED'` (adjacent to, not violating, since the invariant's literal text concerns employee results specifically)

---

### 08-003 — Disabled statutory components are silently filtered from the calculation engine's input with no compliance guard and no trace record that a mandatory deduction was omitted

- **stage:** 08-data-integrity
- **location:** `backend/api/routes/payroll.py:452-454`, `backend/application/payroll_retry_service.py:251-253` (both: `disabled_codes = {r[0] for r in override_rows if r[3] is False}; component_metadata = [m for m in component_metadata if m["component_code"] not in disabled_codes]`) — identical filtering logic in both call sites, applied uniformly regardless of `component_class`
- **current implementation:** Extends Stage 03's finding 03-004 (D-ARCH-2's protective guard is commented out, so any component — including `statutory_deduction`-class ones — can be disabled via `client_component_metadata.is_active = false`) with two new pieces of evidence this stage gathered: (1) the calculation engine's own filtering mechanism applies this exclusion identically regardless of whether the disabled component is a mandatory statutory deduction or an optional allowance — there is no class-aware guard anywhere in this filtering step; (2) `run_sequential_payroll()`'s trace mechanism (Stage 02, confirmed) only records components that *ran* — a disabled statutory component leaves no trace entry, no warning, and no persisted signal anywhere that it was omitted, distinct from components that ran but produced a zero result.
- **intended behaviour:** Not documented — same open question Stage 03 raised (03-004, still pending human decision).
- **suspected or confirmed defect:** Confirmed as a mechanism (the engine does correctly and mechanically skip disabled components — this is not a calculation-correctness defect, the engine behaves exactly as its inputs direct it), but confirmed as a compliance/observability gap: if a workspace ever did disable a mandatory statutory component, there would be no automated signal anywhere (trace, log, audit) that a payroll run proceeded without it. A read-only check of the local development database found **zero** workspaces currently in this state (evidence type 3, per `_core/evidence-standard.md`) — recorded per this stage's constraint not to treat development-data absence as production evidence, only as confirmation the schema-permitted state was checked for and not found in the one dataset available.
- **evidence:** `evidence/2026-07-13-statutory-component-disable-no-trace-signal.txt`
- **status:** confirmed
- **severity:** S2 (extends 03-004's severity reasoning — a real, confirmed mechanism gap, not yet observed to have fired against real data in the one dataset checked)
- **related invariant:** none directly in `CLAUDE.md`'s table; adjacent to the `component_class = 'non_taxable'`/`'paye_addition'` entries, which do carefully specify engine behaviour for other component-class edge cases

---

### 08-004 — `04-004` (reconciliation retry-parity) — REJECTED

- **stage:** 08-data-integrity
- **location:** `backend/domain/payroll/state_machine.py:15-24` (`ALLOWED_TRANSITIONS` — `PARTIAL: [CALCULATED]` only, no direct `PARTIAL→APPROVED`); `backend/application/payroll_approval_service.py:44-77` (`approve_payroll_run` calls `transition(current, APPROVED)`, which raises unless `current == CALCULATED`); `backend/application/reconciliation_service.py:62-65` (`reconcile_payroll_run` requires `status == 'LOCKED'`); `backend/infra/repositories/reconciliation_repo.py:60-76` (`insert_reconciliation` raises if a reconciliation row already exists for the run); `backend/application/payroll_retry_service.py:561-565` (retry requires `status == 'PARTIAL'`, rejecting `APPROVED`/`LOCKED` explicitly)
- **current implementation:** Confirmed by direct citation across the full chain: a run must be `CALCULATED` (i.e., zero `FAILED` employees remaining) before it can become `APPROVED`, then `LOCKED` — and only a `LOCKED` run can receive its first (and only, per the repository's own duplicate guard) reconciliation record. `PARTIAL` — the only status retry operates on — has no transition path to `APPROVED` that skips `CALCULATED`, and there is no transition path backward from `LOCKED`/`APPROVED`/`PAID` to `PARTIAL`. Retry and reconciliation are therefore temporally disjoint for any given run: retry can only ever happen *before* a reconciliation record could exist, never after.
- **intended behaviour:** Not separately documented as a design decision, but the state machine's structure makes the intended ordering self-evident and, per this stage's evidence, correctly enforced at both the Python state-machine layer and the service-layer guards (belt-and-suspenders, not a single point of failure).
- **suspected or confirmed defect:** Rejected. Stage 04's original concern (`04-004`, left `unconfirmed`) hypothesized that retry completion might leave a stale reconciliation row or allow approval against outdated totals. This stage's evidence demonstrates the hypothesized scenario cannot occur, by construction, independent of any single guard being correctly implemented — even if one guard were removed, at least one other (the state machine, the approval-transition check, or the reconciliation status check) would still prevent it.
- **evidence:** `evidence/2026-07-13-04-004-reconciliation-retry-structurally-impossible-overlap.txt`
- **status:** rejected
- **severity:** S3 (recorded as a positive-control finding — the "defect" being rejected was itself provisionally S1/S2 in Stage 04's framing, but this stage's evidence shows no risk exists)
- **related invariant:** `CLAUDE.md` — `payroll_reconciliation.status = 'MATCHED'`/`'RESOLVED'`

---

## 2. Referential and tenant consistency (spot checks)

Consistent with prior stages' findings (Stage 03's workspace-scoping
citations throughout `payroll.py`/`workspace.py`, Stage 06's confirmed
correct scoping on `GET .../results` after an initial single-line-grep
false positive), this stage's spot checks found no new schema-permitted
cross-workspace combination beyond what Stage 06 already flagged for
Stage 09 (the unscoped `/payroll/run/{run_id}/reconcile` route pair,
06-007). `employee_contract` does not carry its own `workspace_id` column
(confirmed, memory `feedback_employee_contract_workspace_scope` from prior
sessions) — it is scoped transitively through `employee.workspace_id`,
consistent with every query this and prior stages have inspected. A full
row-by-row foreign-key audit across all ~20 model tables was not performed
this stage; this is a targeted continuation of Stage 06's spot-check
approach, not an exhaustive schema audit (that remains Stage 09's remit
for the security-relevant subset).

## 3. Historical reproducibility

Not re-derived — **Stage 05 already produced the authoritative snapshot
inventory and lifecycle map** this question depends on
(`docs/audit-program/05-snapshot-integrity/findings.md` §1-§8). This
stage's contribution is confirming, from a data-integrity rather than a
snapshot-mechanism angle, that the answer is unchanged by anything found
in Stages 06-07: an auditor can reconstruct a past run's *statutory and
component-metadata basis* fully from `rules_context_snapshot`,
`component_metadata_snapshot`, `client_component_metadata_snapshot`,
`public_holidays_snapshot`, and `component_trace_jsonb` (all confirmed
sufficient/correct, Stage 05 §8, this stage's own 08-002 does not affect
their content, only their write-time mutation window). Two remaining
mutable-live-dependency gaps, both already catalogued: `employee_contract_
snapshot.components_jsonb` is captured but never read (Stage 05, 05-002 —
salary amounts are read from the *live* `salary_definition` table by
design, D1, mitigated by the D-ARCH-1 edit-lock), and `04-002`'s
still-open statutory-identity-per-result gap (no persisted field records
*which* frozen statutory content a specific retried employee's result
actually used, forcing forensic recomputation as Stage 04's own
controlled test had to do). Neither is new to this stage.

## 4. Duplicate source-of-truth and precedence register

Not re-derived — Stage 03's duplicate-representation register (§3 of that
stage's findings) and Stage 05's snapshot/live boundary map (§6) already
cover every item this stage's investigation list names:
`proration_strategy` (Stage 03, 03-001, confirmed correctly reconciled),
`is_active` (same), pay-cycle columns vs. `definition_json` (Stage 06,
06-002, confirmed write-once-then-unreachable — a UI/API gap, not a data-
correctness one, per that finding's own classification), salary-definition
live vs. snapshot content (Stage 05, 05-002/05-003), statutory identity in
run snapshot vs. missing per-result identity (`04-002`, Stage 05 §10's
recommendation, reused unchanged by Stage 07 §2). This stage adds one new
item: **run-level totals vs. sum of result rows** — `payroll_retry_service.py`'s
final status-recomputation step (Stage 04 citation, confirmed unchanged)
recomputes `payroll_run` totals from a live `SUM(...)` over `payroll_result`
rows after every retry, rather than incrementally adjusting a stored
total — confirmed as the correct pattern (source of truth is always the
result rows, the run-level total is a derived cache recomputed from them,
not a second independent source), no drift risk found.

## 5. Immutability after approval, lock, and payment (summary)

| Table | Protected from | Protected from what status | Gap |
|---|---|---|---|
| `payroll_result` | UPDATE, DELETE | `CALCULATED`, `APPROVED`, `LOCKED`, `PAID` (i.e., everything except the retry-eligible `PARTIAL`/`FAILED`-containing states) | None found — confirmed complete positive control |
| `payroll_run.rules_context_snapshot` | UPDATE (this column only) | Unconditional, any status | None — confirmed complete (Stage 05) |
| `payroll_run` (all other columns) | UPDATE, DELETE | `PAID` only | 08-002 — gap for `APPROVED`/`LOCKED` |
| Snapshot tables (`component_metadata_snapshot` etc.) | Nothing | N/A | Confirmed gap, already catalogued and deferred to Stage 13 (Stage 05, 05-004) — not re-investigated |
| `payroll_reconciliation` | Nothing found | N/A | Not deeply investigated this stage; mitigated by the single-writer-per-transition pattern (`insert_reconciliation` rejects duplicates, `update_reconciliation` only fires on an existing `MISMATCH`) but no DB trigger confirmed |

---

## Positive controls (confirmed correctly enforced, recorded so this stage isn't read as all-gaps)

- **Contract overlap and active-contract uniqueness**: both enforced at
  the DB level via a GIST exclusion constraint and a partial unique index
  respectively — genuinely strong, structural guarantees, not merely
  application-layer validation.
- **`payroll_result` immutability**: a single, well-designed trigger
  function correctly scopes protection to exactly the statuses where
  mutation should be blocked, while correctly permitting retry's own
  DELETE+INSERT pattern during `PARTIAL`.
- **Reconciliation MATCHED/MISMATCH invariant**: enforced by CHECK
  constraints directly at the database level — this is the strongest
  possible enforcement of a `CLAUDE.md`-documented invariant found
  anywhere in this audit so far, stronger than the application-level-only
  enforcement most other invariants rely on.
- **`04-004`**: the reconciliation/retry ordering question is not just
  "no bug found" but "structurally cannot happen," confirmed via multiple
  independent, redundant guards.
- **Payroll input validation**: non-negative quantity and unclaimed-input
  uniqueness both DB-enforced.

---

## Handoff notes for later stages

- **Stage 09 (security and tenant isolation):** the referential/tenant
  spot-checks (§2) found nothing new beyond what Stage 06 already handed
  off (06-007's unscoped reconciliation routes) — Stage 09 should treat
  that as still the primary open item from this angle, not expect new
  material from Stage 08.
- **Stage 10 (execution-trace remediation):** 08-003's finding that a
  disabled statutory component leaves no trace signal is a second,
  independent argument (alongside `04-002`) for why per-result statutory/
  component identity should be persisted — Stage 10's design should
  consider whether the same mechanism that closes `04-002` could also
  record which components were *excluded* by override, not just which ran.
- **Stage 11 (scenario testing):** 08-001 (nullable `employee_number`) and
  08-002 (payroll_run immutability gap) are both good candidates for
  regression tests once addressed — 08-001 in particular because the
  underlying migration bug (silently swallowed `ALTER` failure) is exactly
  the kind of defect a schema-assertion test would catch going forward.
- **Stage 12 (code simplification):** none new from this stage beyond
  what Stages 05/07 already flagged.
- **Stage 13 (consolidated backlog):** `04-004` should be closed out as
  `rejected` in the final backlog (no remediation needed). 08-001, 08-002,
  and 08-003 are all S2 — real, confirmed, but none rising to the
  `04-001`-class urgency. 08-001 is likely the cheapest to fix (a
  corrective migration for the 11 affected rows plus a properly-guarded
  `NOT NULL` re-application) and probably belongs earliest in the backlog
  among this stage's findings, given the underlying migration pattern
  (swallow-all `EXCEPTION WHEN others`) could be hiding similar issues
  elsewhere and is worth a broader grep across all migrations before
  Stage 13 finalizes scope.

## Human decisions required

None new from this stage. `03-004`'s pending human decision (should
statutory-deduction components be disableable) remains open and is now
additionally informed by 08-003's engine-behaviour evidence.

---

## Final review and closure summary (stage close, 2026-07-13)

**Review conclusion, accepted as recorded:** no new human decision was
required to close Stage 08.

- `04-004` is **rejected** — retry is only available for `PARTIAL` runs;
  reconciliation is only available for `LOCKED` runs reached through
  `CALCULATED → APPROVED → LOCKED`. The two operations cannot overlap for
  the same run, so retry cannot leave an existing reconciliation stale.
  Closed with no remediation required.
- `08-001` confirmed S2 — `employee.employee_number` remains nullable
  because migration `c9d0e1f2a3b4` swallows any `SET NOT NULL` failure
  with `EXCEPTION WHEN others THEN NULL`. The local development rows
  (11/4,673) demonstrate the schema-permitted state, not a production
  prevalence claim.
- `08-002` confirmed S2 — `payroll_run` totals/period fields lack
  DB-level immutability until `PAID`; no active application mutation path
  was found for `APPROVED` or `LOCKED`, so this is a defence-in-depth gap,
  not an active exploit.
- `08-003` confirmed S2 — disabled statutory components are removed
  before execution with no class-aware guard and no trace/audit signal
  that a mandatory component was omitted. Correct mechanical engine
  behaviour is distinguished from the missing compliance/observability
  guard — the engine does exactly what its configuration tells it to; the
  gap is the absence of a guard and a signal, not a calculation error.
  `03-004`'s underlying policy question (should statutory components be
  disableable at all) remains an **open human decision**, not resolved by
  Stage 08.
- No financial miscalculation, stale aggregate, reconciliation corruption,
  contract-overlap gap, or new historical-reproducibility defect was
  found. Positive controls remain on record: contract-overlap exclusion
  constraint, active-contract uniqueness, `payroll_result` uniqueness/
  three-layer immutability, reconciliation CHECK constraints, and
  payroll-input constraints.

**Review requirements verified before closing:**

1. `04-004`'s rejection cites the complete lifecycle chain (state machine,
   `approve_payroll_run`'s transition check, `reconcile_payroll_run`'s
   `LOCKED`-only guard, `insert_reconciliation`'s duplicate-row guard) —
   four independent, redundant confirmations, not a single point of
   failure.
2. `08-001` explicitly separates the confirmed schema defect (the
   migration's guard, and the empirical fact that the column is nullable
   today) from the local-development row count, which is cited only as
   proof the schema-permitted state exists, not as a production claim.
3. `08-002` makes no claim of an active exploit or application mutation
   path — the finding explicitly states none was found and frames the gap
   as defence-in-depth, consistent with `05-004`'s established severity
   reasoning.
4. `08-003` explicitly separates "the engine correctly and mechanically
   skips disabled components" (not a defect) from "no compliance guard or
   trace signal exists for that omission" (the confirmed gap).
5. All five positive controls remain recorded in the findings above,
   unchanged.
6. `03-004` remains open, carried forward for Stage 13's policy/backlog
   resolution — not resolved here.
7. `04-001` and `05-001` are not referenced by any Stage 08 finding's
   evidence or defect statement, and remain remediated.
8. All Stage 08 completion criteria (per `CONTEXT.md`) are satisfied; all
   4 findings use exactly one of the five valid statuses (3 `confirmed`,
   1 `rejected`).

**Handoff carry-forward (finalized):**

- `04-004` closed/rejected — no remediation required, no further carry-
  forward beyond this closure record.
- `08-001`, `08-002` → Stages 11 (regression test candidates) and 13
  (backlog).
- `08-003` → Stages 09, 10, 13 — and the open `03-004` policy decision is
  preserved unchanged, not resolved by this stage.
- `07-002` → Stage 13 as an audit-*consistency* issue specifically — not
  reinterpreted as reconciliation data corruption; the underlying
  reconciliation data itself is confirmed correct and complete in this
  stage's investigation.
- `04-002` and the resolved minimal-retry-trace design remain Stage 10's
  input, unchanged.
- `05-004` remains deferred to Stage 13, unchanged.
- Stages 01–07 and the `04-001`/`05-001` remediation record are preserved
  unchanged.
