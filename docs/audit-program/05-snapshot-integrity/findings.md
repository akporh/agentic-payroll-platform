# Stage 05 — Findings

Status: **in-progress**. All entries below use the template in
[`../_core/finding-schema.md`](../_core/finding-schema.md). Status values are
restricted to this stage's five-value set.

---

## 1. Snapshot inventory and lifecycle map

| # | Snapshot | Purpose | Writer | Creation point | Source | Consumer(s) |
|---|---|---|---|---|---|---|
| 1 | `payroll_run.rules_context_snapshot` | Freeze statutory rule, tax bands, and (v2) rule-set content resolved for a run | `payroll_run_repo.py::create_draft_payroll_run` | Synchronous, in the HTTP request, as part of the `DRAFT` INSERT | Live `statutory_rule`/`tax_band`/`rule_set`/`rule_set_item`, resolved in `payroll.py` | Original run (immediately, in-memory, not re-read from DB); retry (`_build_shared_context`) — **partially**, see §8 |
| 2 | `payroll_run.public_holidays_snapshot` | Freeze the resolved public-holiday date set | Same INSERT as #1 | Same as #1 | Live `national_public_holiday` ∪ `workspace_public_holiday` | Retry (`ph_dates_used`/`ph_source` read from here) — confirmed correct, Stage 03 |
| 3 | `component_metadata_snapshot` | Freeze platform component metadata | `snapshot_service.py::create_payroll_snapshot` | **Asynchronous** — inside the background task, after the DRAFT row exists and the HTTP response has returned | Live `component_metadata`, already loaded in-memory by the sync route | Retry only (original run uses its own in-memory copy, never re-reads this table) |
| 4 | `client_component_metadata_snapshot` | Freeze workspace component overrides | Same call as #3 | Same as #3 | Live `client_component_metadata` | Retry only |
| 5 | `employee_contract_snapshot` | Freeze structural contract fields + `salary_definition_id` per employee | Same call as #3 | Same as #3 | Live `employee_contract`, `salary_definition` (components_jsonb copied at that instant) | Retry only, and **only 6 of 7 columns** — see 03-003, revisited §7 |
| 6 | `payroll_result.calculations_snapshot_json` | Freeze gross/PAYE/net for one employee's result | `payroll_result_repo.py` (bulk on original run; per-row on retry) | At persistence time, per employee, after calculation | In-memory calculation output | UI/API result display; export functions (Stage 02, mostly unwired) |
| 7 | `payroll_result.salary_inputs_snapshot` | Audit trail — salary components actually used for this result (D4) | Same as #6 | Same as #6 | In-memory `components` list at calculation time | Not read by any calculation path — audit/display only (not investigated further this stage; no defect claimed) |
| 8 | `payroll_result.per_employee_context_json` | Freeze per-employee eligibility flags (e.g. `is_union_member`) for retry reuse | Same as #6 | Same as #6 | In-memory `employee_context` at calculation time | Retry (`get_employee_context_from_result`, confirmed reader — Stage 03/04 citations) |
| 9 | `payroll_result.component_trace_jsonb` | Per-component calculation trace | Same as #6 | Same as #6 | `run_sequential_payroll()`'s returned `trace` list | API trace endpoints (`payroll.py:1069,1376`); does NOT record statutory-rule identity (Stage 04, 04-002) |
| 10 | `rule_set` / `rule_set_item` | Immutable, point-in-time frozen payroll-rule set | `rule_set_service.py::auto_publish()` | On payroll-rule create/version-save, or via backfill script | Live `payroll_rule`, date-resolved | Retry, by frozen `payroll_run.rule_set_id` — confirmed correct, Stage 03 (03-005) |
| 11 | Claimed `payroll_input` rows | Freeze which input events belong to this run | `payroll_input_repo.py::link_inputs_to_run` | At original-run calculation time | Live `payroll_input` (unclaimed rows, `payroll_run_id IS NULL`) | Retry, via `load_inputs_for_run(payroll_run_id)` — confirmed correct, Stage 04 §3 |
| 12 | Frozen period fields (`payroll_run.period_start`/`period_end`) | Freeze the run's pay period | Same INSERT as #1 | Same as #1 | Live `pay_cycle`/explicit API params, resolved into a `PeriodContext` | Retry (`_build_shared_context:139-143`) — confirmed correct, Stage 04 §2 |

No dedicated "snapshot version" marker exists on any table except
`rules_context_snapshot`'s own internal `"snapshot_version"` key (1 or 2, see
§8) — none of #3, #4, #5, #6-9, #10, #11 carry an explicit schema-version
field. This is not currently a problem (their consumers do not need to
distinguish schema generations, since each table has had only one schema
since creation), but it means any future schema change to these tables has
no built-in migration-era compatibility marker to detect old rows by.

---

## 2. Snapshot writer/consumer matrix

| Snapshot | Writer(s) | Reader(s) — original run | Reader(s) — retry | Reader(s) — other |
|---|---|---|---|---|
| `rules_context_snapshot` | `payroll_run_repo.py` (1 writer) | None (uses in-memory values, never re-reads its own snapshot) | `payroll_retry_service.py` — **partially, see §8** | `payroll.py` GET routes return it verbatim for display |
| `public_holidays_snapshot` | `payroll_run_repo.py` | None | `payroll_retry_service.py:130-134` | none found |
| `component_metadata_snapshot` | `snapshot_service.py` (1 writer) | None | `payroll_retry_service.py:208-217` | `GET /ops/legacy-executor-stats`-adjacent inspection routes not found to read it |
| `client_component_metadata_snapshot` | `snapshot_service.py` | None | `payroll_retry_service.py:232-240` | none found |
| `employee_contract_snapshot` | `snapshot_service.py` | None | `payroll_retry_service.py:624-637` — 6 of 7 columns | none found |
| `calculations_snapshot_json` | `payroll_result_repo.py` (both paths) | N/A (write-only at creation) | N/A | API display routes |
| `salary_inputs_snapshot` | `payroll_result_repo.py`, `payroll_retry_service.py::_insert_result` | N/A | N/A | Not confirmed read anywhere — flagged §7 |
| `per_employee_context_json` | `payroll_result_repo.py`, `payroll_retry_service.py::_insert_result` | N/A | `payroll_retry_service.py::get_employee_context_from_result` | none found |
| `component_trace_jsonb` | `payroll_result_repo.py`, `payroll_retry_service.py::_insert_result` | N/A | N/A | API trace routes |
| `rule_set_item` | `rule_set_service.py::auto_publish()` | `payroll.py` (resolves into `payroll_rules_full`) | `payroll_retry_service.py:288-297` | none found |
| Claimed `payroll_input` | `payroll_input_repo.py::link_inputs_to_run` | Original run's own calculation | `payroll_retry_service.py:601` | none found |

Every writer is single-sourced (no snapshot table has more than one writer
function), which rules out a writer-side race between two different code
paths — the only race risk identified in this stage is the
resolve-then-freeze TOCTOU window described in §6, which is about live-table
reads preceding a snapshot write, not about two writers of the same
snapshot.

---

## 3. Snapshot schema/version register

| Snapshot | Version marker | Schema stability |
|---|---|---|
| `rules_context_snapshot` | Internal `"snapshot_version"` key: `1` (legacy, `{statutory_rule: {id, version}, payroll_rules: [...]}`) or `2` (full content, see §8) | Two live schema generations, distinguished by consumers via `.get("snapshot_version", 1)` |
| All other snapshot tables | None | Single schema since table creation (confirmed via migration history — no `ALTER TABLE ... ADD COLUMN` after initial creation for `component_metadata_snapshot`/`client_component_metadata_snapshot`; `employee_contract_snapshot` unchanged since `b5c6d7e8f9a0`) |

---

## 4. Immutability and validation matrix

| Snapshot | DB-level immutability | Application-level guard | Validated before retry use? |
|---|---|---|---|
| `rules_context_snapshot` | **Yes** — `trg_run_snapshot_immutable` (migration `a1b2c3d4e5f6`), `BEFORE UPDATE OF rules_context_snapshot`, raises on any change | Written once in the DRAFT INSERT by design (comment explicitly explains why) | No explicit validation of its *content* before retry reads it — only `validate_snapshot_complete()`'s check of *other* tables (§ below) gates retry at all |
| `public_holidays_snapshot` | **No trigger found** — not covered by `trg_run_snapshot_immutable` (that trigger is column-specific to `rules_context_snapshot` only) | None beyond "never updated by any code path" (confirmed by grep — no `UPDATE ... public_holidays_snapshot` anywhere) | Presence checked (`ph_snapshot is None` → hard-fail), content not further validated |
| `component_metadata_snapshot` | **No trigger found** | `ON CONFLICT (payroll_run_id, component_code) DO NOTHING` (idempotent re-insert, not immutability) | Presence checked via `validate_snapshot_complete()` (row-count only, not content) |
| `client_component_metadata_snapshot` | **No trigger found** | Same `ON CONFLICT DO NOTHING` pattern | **Not** checked by `validate_snapshot_complete()` — explicitly excluded by design ("a workspace with zero component overrides is valid") |
| `employee_contract_snapshot` | **No trigger found** | Same `ON CONFLICT DO NOTHING` pattern | Presence checked via `validate_snapshot_complete()` (row-count only) |
| `payroll_result.calculations_snapshot_json` | **Yes** — `trg_snapshot_immutable` (migration `fe0bad282b7d`) | Retry uses DELETE+INSERT specifically *because* this trigger blocks UPDATE (documented in `payroll_retry_service.py`'s module docstring) | N/A — write-once per row |
| `payroll_result.per_employee_context_json` | **Explicitly NOT covered** — migration `1a2b3c4d5e6f`'s own comment confirms the trigger is column-specific and this column is unaffected | None beyond "never updated by any code path" (DELETE+INSERT pattern used instead) | N/A in practice, since retry never issues an UPDATE to this table |
| `payroll_result.salary_inputs_snapshot`, `component_trace_jsonb` | **No trigger found** (same table, different columns from the protected one) | Same as above — inert in practice because of the DELETE+INSERT pattern, not because of a DB guarantee | N/A |
| `rule_set_item` | **No DB trigger found**, but effectively immutable by workflow: a `rule_set` becomes "locked" once referenced by a `payroll_run` (per `RuleSetLockedError`, cited in Stage 02's `backfill_rule_set_snapshots.py` evidence) — this is an **application-level lock**, not a schema-level guarantee | `RuleSetLockedError` raised by `rule_set_service.py` on attempted modification of a locked set | N/A |

**Finding preview:** three of the four "background-task" snapshot tables
(`component_metadata_snapshot`, `client_component_metadata_snapshot`,
`employee_contract_snapshot`) and three `payroll_result` columns
(`per_employee_context_json`, `salary_inputs_snapshot`, `component_trace_jsonb`)
have **no DB-level immutability enforcement** at all — they rely entirely on
the fact that no code path currently issues an `UPDATE` against them. This is
true today (confirmed by grep — zero `UPDATE` statements target any of these
columns anywhere in `backend/`), but it is an absence of misuse, not a
guarantee against it, unlike the two triggers that make misuse structurally
impossible. See finding 05-004.

---

## 5. Transaction/timing integrity assessment

| Snapshot | Same transaction as run creation? | Partial-failure behaviour | Run proceeds if incomplete? |
|---|---|---|---|
| `rules_context_snapshot`, `public_holidays_snapshot`, frozen period | **Yes** — written in the synchronous `create_draft_payroll_run()` INSERT, in the same request/transaction that creates the `DRAFT` row | If the INSERT fails, `create_draft_payroll_run` raises `ValueError` → route returns HTTP 409. **Not silent.** | No — the run is never created at all if this write fails |
| `component_metadata_snapshot`, `client_component_metadata_snapshot`, `employee_contract_snapshot` | **No** — written inside `_calculate_and_persist`, a `BackgroundTasks` job that runs *after* the DRAFT row is committed and the HTTP response has already returned | **Confirmed silently swallowed**: `create_payroll_snapshot(...)` is wrapped in `try/except Exception as exc: logger.error(...)` with no re-raise (`payroll.py:929-938`) — see finding 05-001 | **Yes** — execution falls through to `execute_and_persist(...)` regardless of whether the snapshot write succeeded |

**TOCTOU window (original run):** the live `statutory_rule`/`tax_band` query
(`payroll.py:241-296`) happens *before* `create_draft_payroll_run()`'s INSERT
(`payroll.py:827`) within the same synchronous request — a window of single-
digit milliseconds. A concurrent statutory-rule insert landing in that
narrow window could theoretically cause the *original* run itself to freeze
inconsistent data, but this is a categorically smaller risk surface than
04-001 (a single request's processing time vs. a `PARTIAL` run sitting
unretried for an arbitrary duration) and was not separately reproduced in
this stage — recorded as a plausible, much lower-priority observation, not
investigated further.

**Concurrent configuration edits between resolution and freeze:** for
`component_metadata`/`client_component_metadata`/`employee_contract`, the
live read happens in the synchronous route (before backgrounding) but the
*freeze* happens later, in the background task. A concurrent edit to, say,
`client_component_metadata` between those two points would mean the
in-memory values the *original run's own calculation* uses (loaded
synchronously, passed into the background task as parameters) could already
differ from what eventually gets frozen into the snapshot table — since the
snapshot writer re-receives the same in-memory `employees`/`component_metadata`
parameters passed into the background task, not a fresh live re-query, this
specific risk does not actually materialize (the frozen content matches what
was calculated, by construction — both come from the same in-memory
snapshot of data taken at the start of the request). Confirmed not a defect,
via direct parameter-flow tracing.

---

## 6. Legacy-run compatibility matrix

| Tier | Identifying characteristic | Statutory content available | Safe retry behaviour |
|---|---|---|---|
| **A — v2-complete** | `rules_context_snapshot.snapshot_version == 2` with `statutory_rule.rules_jsonb`/`tax_bands` populated | Full — id, version, effective_from, rules_jsonb, tax_bands | **Allow from snapshot** — this is the target state for the 04-001 fix |
| **B — v2-attempted, malformed** | Theoretically: a v2 snapshot missing a required sub-field | Not currently reproducible — `build_rules_context_snapshot`'s v2 branch raises `ValueError` synchronously if any required v2 param is `None` (`snapshot.py:78-94`), which fails the whole request (fail-closed) before any row is written. **No code path was found that could persist a partial v2 snapshot.** | **Reject and require correction run**, defensively, even though no live example is expected — a schema/constraint change elsewhere in the codebase could theoretically reintroduce this class in the future |
| **C — v1 ID-only** | `rules_context_snapshot.snapshot_version` absent (defaults to `1`); shape is `{"statutory_rule": {"id": ..., "version": ...}, "payroll_rules": [...]}` — no `rules_jsonb`, no `tax_bands` | **Partial** — identity only, not content | **Reject and require correction run.** A v1 snapshot cannot support a snapshot-first retry (the content isn't there), and re-deriving the missing `rules_jsonb`/`tax_bands` from the frozen `id` by querying the live `statutory_rule` table **is not safe** — the live row could have been edited or (per `CLAUDE.md`'s data model) a *new* row could exist that changes which one `ORDER BY effective_from DESC` would pick if re-resolved by date instead of by the frozen ID; querying live *by the frozen ID specifically* (not by date) would be safe **only if `statutory_rule` rows are provably never mutated in place** — this was not verified in this stage (no `UPDATE` was found against `statutory_rule`, but this was not exhaustively proven) and is flagged as an open question in the remediation spec, not assumed safe |
| **D — pre-snapshot-engine** | `employee_contract_snapshot`/`component_metadata_snapshot` empty for the run (predates migration `b5c6d7e8f9a0`) | None | **Already correctly rejected** — `validate_snapshot_complete()` hard-fails before any calculation, confirmed in Stage 03/04 |
| **E — frozen date, no frozen object** | `payroll_run.statutory_effective_date` present, but `rules_context_snapshot` is v1 (tier C) or absent entirely | Date only, no content | **Reject and require correction run** — same reasoning as tier C; a frozen date alone is exactly the mechanism 04-001 exploits (it re-resolves live *from* that date), so treating "we at least have a date" as sufficient would not fix anything |

No tier recommends falling back to a live re-query, per the stage's explicit
constraint. Tiers C and E are the ones a "backfill" temptation would most
naturally apply to (since a `statutory_rule_id` is known) — this is
explicitly the backfill anti-pattern the sprint prompt warns against ("Do not
recommend a backfill based only on re-running the current live resolution
query; that would recreate the same nondeterminism as 04-001"), and this
stage's specification (§9 below) does not recommend it.

---

## 7. Dead, unused, or ambiguous snapshot-field register

| Field | Status | Evidence |
|---|---|---|
| `employee_contract_snapshot.components_jsonb` | **Confirmed dead** (write-only, zero readers) — revisits Stage 03 finding 03-003 | See finding 05-002 below for this stage's classification |
| `payroll_result.salary_inputs_snapshot` | **Write-only, no confirmed reader found in this stage** — written by both `save_payroll_results_bulk`/`save_payroll_result` (original run) and `_insert_result` (retry), explicitly documented as a "D4 audit trail," but no query anywhere in `backend/` was found to `SELECT` this column | New finding this stage — 05-003 |
| `rules_context_snapshot.statutory_rule.effective_from` (v2) | **Present, used for audit/display, not required for recalculation** — distinct from `payroll_run.statutory_effective_date` (the "as of" date used for *resolution*); not redundant, but also not consumed by any calculation logic, only echoed back in GET responses | Not classified as a defect — informational |
| `client_component_metadata_snapshot` | **Correctly excluded from `validate_snapshot_complete()`'s check by design** (an empty table for a workspace with zero overrides is valid) — included here only to confirm this is a deliberate, not accidental, omission | Confirmed via direct citation, no defect |
| `payroll_run.public_holidays_snapshot` | Read (ph_dates_used/ph_source) — confirmed live, not dead | Cross-reference, no defect |

---

## 8. Field-by-field statutory snapshot sufficiency analysis

Comparing (a) what `payroll.py`'s live resolution extracts, (b) what the v2
`rules_context_snapshot["statutory_rule"]` freezes, and (c) what
`payroll_retry_service.py::_build_shared_context` currently re-derives live
(the mechanism 04-001 exploits) vs. what it *would* need if switched to
snapshot-first:

| Field | (a) Live resolution extracts | (b) Frozen in v2 snapshot | (c) Retry currently re-derives live | Classification |
|---|---|---|---|---|
| Statutory rule ID | `stat_row[0]` | `statutory_rule.id` | Re-derived (new ID possibly selected) | **Present and directly usable** — snapshot already has it |
| Version | `stat_row[1]` | `statutory_rule.version` | Re-derived | **Present and directly usable** |
| `effective_from` | `stat_row[3]` | `statutory_rule.effective_from` | Not used by retry today (retry uses `payroll_run.statutory_effective_date`, a different value) | **Present, redundant for the fix** (audit value, not a calculation input) |
| Full `rules_jsonb` (pension, reliefs, nhf, health_insurance, development_levy, life_insurance) | `stat_row[2]` | `statutory_rule.rules_jsonb` — **the full dict, not a subset** | Re-derived via a fresh `stat_row` fetch, then the *same* extraction logic (`pension_config = rules_jsonb.get("pension")`, etc.) applied a second time in `payroll_retry_service.py:172-185` | **Present and directly usable** — the snapshot already contains the exact same dict the original run extracted its rates from; retry's extraction logic is a second, currently-redundant copy of the same parsing code (see 05-005) |
| Tax bands (`lower_limit`/`upper_limit`/`rate`, ordered) | `tax_rows` → `tax_bands` list | `statutory_rule.tax_bands` — full list | Re-derived via a fresh `tax_rows` query | **Present and directly usable** — same shape, same values |
| Country code | Used only to `JOIN workspace w ON sr.country_code = w.country_code` during live resolution | **Not present** in the v2 snapshot | Not currently used by retry independent of the live query it's part of | **Missing, but not required** — once retry stops issuing the live query entirely, country_code has no remaining purpose in this flow; it is a resolution-time join key, not a calculation input |
| Derived/normalized fields (`Decimal(str(...))` conversions) | Computed at extraction time in `payroll.py` | Not pre-computed in the snapshot — raw JSON values (floats, per the Decimal-safe serializer) | Retry independently re-applies the same `Decimal(str(...))` conversions | **Present but requires deterministic normalization** — this is not a gap, it is the same normalization step the original run already performs; a snapshot-first retry must apply the identical `Decimal(str(...))` conversion logic to the frozen JSON values, which is a direct, mechanical port of existing code, not new logic |

**Conclusion: the v2 snapshot is already sufficient.** Every value retry
needs to compute PAYE, pension, NHF, health insurance, development levy, and
life insurance identically to the original run is already present in
`rules_context_snapshot["statutory_rule"]`. **04-001 was never a snapshot-
completeness gap — it is purely a retry-read-path gap.** This significantly
bounds the remediation: no snapshot schema change, no backfill, no new
migration is required to fix 04-001 itself (a migration may still be wanted
for 04-002's observability recommendation, see §11).

---

## Findings

### 05-001 — Snapshot creation for component metadata, client overrides, and employee contracts can fail silently, allowing an original run to complete and persist results with an incomplete or entirely absent snapshot

- **stage:** 05-snapshot-integrity
- **location:** `backend/api/routes/payroll.py:926-939` (`_calculate_and_persist`'s `try/except Exception as exc: logger.error(...)` around `create_payroll_snapshot(...)`, no re-raise)
- **current implementation:** If `create_payroll_snapshot()` raises for any reason (DB connectivity blip, constraint violation, etc.), the exception is logged and swallowed; execution proceeds directly to `execute_and_persist(...)`. Because `create_payroll_snapshot()`'s own three-table batch is internally atomic (a single `raw_conn.commit()` at the end, per its docstring), the failure mode is "all three snapshot tables end up with zero rows for this run" — not partial corruption across tables — but the original run's calculation and result persistence proceed regardless, using the in-memory data already loaded synchronously before backgrounding.
- **intended behaviour:** Not documented as intentional. The comment at `payroll.py:927-928` explains *why* the snapshot write was moved into the background task (HTTP response latency), but not why its failure is swallowed rather than surfaced or retried.
- **suspected or confirmed defect:** Confirmed as a silent-failure mechanism by direct code citation. The blast radius is bounded by `validate_snapshot_complete()`'s hard-fail at retry time (confirmed in Stage 03/04) — a run with a silently-failed snapshot will correctly block any future retry attempt with "predates snapshot engine — open a correction run," rather than proceeding with incomplete data. So the *original* run's own results are unaffected, and a *bad* retry cannot happen either — but a run that should have been retryable becomes permanently stuck requiring a manual correction run, with the actual cause (a swallowed background-task exception) visible only in server logs, not to any operator via the API or UI.
- **evidence:** `evidence/2026-07-12-snapshot-creation-swallowed-exception.txt`
- **status:** confirmed
- **severity:** S2 (a silent failure that degrades operator experience and requires a correction run, but does not cause incorrect calculation — distinct from and lower-severity than 04-001, which does)
- **related invariant:** none directly; relevant to Stage 07 (silent failures and observability)

---

### 05-002 — `employee_contract_snapshot.components_jsonb`: confirmed dead storage, and its dead status is evidence the snapshot boundary was not conceptually settled at design time

- **stage:** 05-snapshot-integrity
- **location:** Same citations as Stage 03 finding 03-003 (`snapshot_service.py:108-135`, `payroll_retry_service.py:619-658`, migration `b5c6d7e8f9a0`)
- **current implementation:** Unchanged from Stage 03 — written every run, read nowhere.
- **intended behaviour:** This stage's classification, per the sprint's five-option framework: **inconsistent with D1 live-salary-definition semantics.** The migration's own comment ("D1: salary_definition_id frozen; retry joins salary_definition live on it") describes freezing the *identifier*, not the *content*, as the deliberate design — meaning `components_jsonb` on the snapshot row was written despite the design already having decided the live join was the source of truth. This reads as a column added defensively (or copy-pasted from a similar pattern) without updating the write to match the already-decided read strategy, rather than a column awaiting a not-yet-built consumer.
- **suspected or confirmed defect:** Confirmed dead (unchanged from 03-003). This stage's addition: classified as evidence of a **momentary boundary inconsistency at the point the D1 decision was made**, not as a currently-live design ambiguity — the *rest* of the snapshot boundary (structural fields on the same table, `rule_set_item`, `public_holidays_snapshot`) is consistently "freeze what retry needs, nothing more," and this one column is the sole exception. Not required as an audit baseline (no consumer, confirmed), not intended for future diffing (no design document references one), safe to remove in a future Stage 12 pass.
- **evidence:** Stage 03's `evidence/2026-07-12-employee-contract-snapshot-dead-column.txt`, re-confirmed unchanged by this stage's inventory pass
- **status:** confirmed
- **severity:** S3 (unchanged from Stage 03 — write-only column, no correctness impact, D-ARCH-1 edit-lock still confirmed as the mitigating control)
- **related invariant:** none

---

### 05-003 — `payroll_result.salary_inputs_snapshot` has no confirmed reader anywhere in the codebase

- **stage:** 05-snapshot-integrity
- **location:** `backend/infra/repositories/payroll_result_repo.py` (writer, both `save_payroll_results_bulk` and `save_payroll_result`), `backend/application/payroll_retry_service.py::_insert_result` (writer, retry path); migration `b5c6d7e8f9a0` ("Column added: `payroll_result.salary_inputs_snapshot` JSONB NOT NULL")
- **current implementation:** This column is written on every `payroll_result` row insert (both original run and retry), documented in its introducing migration as part of "full audit traceability," but no `SELECT` targeting this column was found anywhere in `backend/` (confirmed by grep across the full backend tree).
- **intended behaviour:** The migration's docstring frames it as an audit-trail column ("ensures... full audit traceability") — presumably intended to be surfaced via a future audit UI/API, not necessarily consumed by calculation logic. Unlike 05-002 (`employee_contract_snapshot.components_jsonb`), there is no D1-style comment suggesting this was superseded by a different design — it reads as a genuinely not-yet-built consumer, not an inconsistency.
- **suspected or confirmed defect:** Confirmed as currently unread (write-only), by direct grep evidence. Not classified as a defect — this stage's five-option framework classifies it as **"intended for future diffing/audit," not required as a live audit baseline today** — distinct from 05-002's classification. Flagged, not recommended for removal, since removing it would foreclose the audit-surface use case its own migration comment describes, whereas 05-002's dead column is inconsistent with an already-decided design and has no such stated future purpose.
- **evidence:** New this stage — grep confirms zero `SELECT ... salary_inputs_snapshot` matches in `backend/`
- **status:** confirmed
- **severity:** S3
- **related invariant:** none

---

### 05-004 — Immutability enforcement is inconsistent across snapshot tables: two tables have DB-level triggers, the rest rely entirely on the absence of any `UPDATE` code path

- **stage:** 05-snapshot-integrity
- **location:** See §4 immutability matrix above; migrations `a1b2c3d4e5f6`, `fe0bad282b7d`, `1a2b3c4d5e6f`
- **current implementation:** `payroll_run.rules_context_snapshot` and `payroll_result.calculations_snapshot_json` are physically immutable at the database level — any `UPDATE` attempt raises a Postgres exception, regardless of which application code issues it. Every other snapshot mechanism (`component_metadata_snapshot`, `client_component_metadata_snapshot`, `employee_contract_snapshot`, and the `payroll_result` columns `per_employee_context_json`/`salary_inputs_snapshot`/`component_trace_jsonb`) has no equivalent trigger — their immutability today is entirely a property of "no code path currently issues an UPDATE against them," confirmed by grep, not a schema-enforced guarantee.
- **intended behaviour:** Not documented as a deliberate two-tier design. The two tables that *do* have triggers were each given one for a specific, cited reason (retry's DELETE+INSERT dance around `calculations_snapshot_json`; general snapshot-integrity concern for `rules_context_snapshot`) — there's no evidence the remaining tables were deliberately left unprotected, more likely they were added later and the immutability pattern wasn't systematically re-applied.
- **suspected or confirmed defect:** Confirmed as an inconsistency by direct citation. Not a currently-exploitable defect (no code path attempts these updates today), but it means a future code change — e.g. a well-intentioned "fix" that updates `employee_contract_snapshot` in place instead of following the existing delete/reinsert convention — would not be caught by the database, only by code review, unlike the two already-protected tables where such a mistake would fail loudly at the DB layer immediately.
- **evidence:** `evidence/2026-07-12-immutability-trigger-inventory.txt`
- **status:** confirmed
- **severity:** S2 (defense-in-depth gap, not a live defect — elevated above S3 because snapshot immutability is exactly the property this whole stage, and 04-001's fix, depends on)
- **related invariant:** none directly; structurally related to every invariant that depends on snapshot immutability (e.g. `payroll_run.status = 'APPROVED'` — immutable, no employee results can be modified)

---

### 05-005 — Retry's statutory-rate extraction logic (`rules_jsonb.get("pension")`, etc.) is duplicated verbatim from the original route rather than shared, which is how 04-001 became structurally possible

- **stage:** 05-snapshot-integrity
- **location:** `backend/api/routes/payroll.py:260-278` vs. `backend/application/payroll_retry_service.py:172-185` — near-identical extraction logic, applied to two different `rules_jsonb` sources (original: freshly-resolved live row; retry: a second, independently re-resolved live row)
- **current implementation:** Confirmed — both call sites parse the identical set of keys (`pension.employee_rate`/`employer_rate`, `reliefs.rent_relief`, `nhf.employee_rate`, `health_insurance.employee_amount`, `development_levy.amount`, `life_insurance.employer_rate`) out of a `rules_jsonb` dict, with the same defaults and the same `Decimal(str(...))` conversions. The two copies are semantically equivalent today.
- **intended behaviour:** Not documented as a deliberate duplication.
- **suspected or confirmed defect:** Not itself a defect (the two copies currently agree), but directly explanatory of §8's conclusion: had this extraction logic been implemented once, taking a `rules_jsonb` dict as a parameter regardless of whether it came from a live query or a frozen snapshot, retry's fix would have been a one-line source change (pass the snapshot's `rules_jsonb` instead of a freshly-queried one) rather than requiring this stage's full sufficiency analysis to confirm safety. Recorded as a Stage 12 simplification candidate that would also reduce future-defect risk of this same class.
- **evidence:** §8 above (line citations)
- **status:** confirmed
- **severity:** S3 (structural/maintainability observation, not a live defect)
- **related invariant:** none

---

## 9. Canonical snapshot-first retry contract for 04-001

**Exact snapshot key and schema retry must read:**
`payroll_run.rules_context_snapshot["statutory_rule"]`, requiring
`snapshot_version == 2` and the four sub-fields `id`, `version`, `rules_jsonb`,
`tax_bands` all present and non-null (per §8's sufficiency analysis —
`effective_from` may be read for audit/logging but must not gate validity).

**Exact live queries that must no longer occur for v2 runs:**
`payroll_retry_service.py:150-164`'s `SELECT sr.statutory_rule_id, sr.version, sr.rules_jsonb FROM statutory_rule sr WHERE sr.country_code = :cc AND sr.effective_from <= :as_of_date ORDER BY ... LIMIT 1`, and the subsequent `tax_band` query at lines 188-196, must both be removed from the retry-eligible code path for any run classified as tier A (§6). The `Decimal(str(...))` normalization logic immediately following (lines 172-185) is retained unchanged, applied to the snapshot's `rules_jsonb` instead of a freshly-queried one.

**Validation rules before retry begins:** extend `validate_snapshot_complete()`
(or an adjacent, equally-named check called at the same point in
`_build_shared_context`) to also verify `rules_context_snapshot.get("snapshot_version") == 2` and that `rules_context_snapshot["statutory_rule"]` contains all four required sub-fields. This should run alongside the existing `employee_contract_snapshot`/`component_metadata_snapshot` row-count check, not as a separate, later check — a single hard-fail point is easier to reason about than several scattered ones.

**Hard-fail behaviour and error wording:** for any run failing the above
validation (tiers B, C, E per §6), raise the same class of error
`validate_snapshot_complete()` already raises, with wording consistent with
the existing pattern: *"Run {payroll_run_id} predates the v2 statutory
snapshot — open a correction run."* This mirrors the exact existing wording
style ("predates snapshot engine — open a correction run") so operators see
one consistent error family, not a new one.

**Legacy-run policy:** tiers B, C, D, E are all rejected (§6) — no tier
falls back to a live query. Tier D is already correctly rejected by the
existing `validate_snapshot_complete()` check; the new check adds coverage
for tiers B, C, E, which currently pass that check (since it doesn't inspect
`rules_context_snapshot` at all) and fall through into 04-001's live
re-resolution today.

**Migration/backfill safety:** **no backfill is recommended.** Per §6 tier
C/E reasoning, reconstructing `rules_jsonb`/`tax_bands` for old v1 runs by
querying `statutory_rule` — even by the frozen ID rather than by date — was
not proven safe in this stage (mutation-in-place of `statutory_rule` rows
was not exhaustively ruled out) and is exactly the category of "recreate the
live-query nondeterminism" the sprint prompt warns against. Old runs simply
become permanently retry-ineligible via correction run, which is already the
existing, accepted pattern for tier D.

**Required audit/event/trace data:** none beyond what already exists is
strictly required to fix 04-001 itself — the fix is a read-path change, not
a write-path change. (04-002's separate observability recommendation, §11,
is additive and independent.)

**Required regression tests:** a fixed-behaviour variant of this stage's
controlled reproduction script
(`docs/audit-program/04-original-run-retry-parity/evidence/statutory_divergence_controlled_test.py`)
— after the fix, the same test setup (rule A resolved originally, rule B
inserted afterward with an intervening `effective_from`) must show the
retried employee's PAYE matching rule A (the frozen snapshot), not rule B.
A second test should cover the legacy hard-fail: a run manufactured with a
v1-shaped `rules_context_snapshot` must have its retry attempt raise the new
validation error, not silently succeed or crash differently.

**Acceptance criteria proving original-run/retry statutory parity:**
1. For any `PARTIAL` v2 run, retrying any `FAILED` employee produces a
   result whose PAYE/pension/NHF/health/levy exactly match what that
   employee would have received under the *original* run's resolved
   statutory rule, regardless of any `statutory_rule` rows inserted after
   the original run.
2. For any run lacking a v2 statutory snapshot, a retry attempt fails with
   the new, clearly-worded hard-fail error, and creates no `payroll_result`
   row for the affected employee (no partial/incorrect write).
3. The now-unused live `statutory_rule`/`tax_band` queries are removed from
   `_build_shared_context`'s retry-eligible path (not merely bypassed by a
   conditional) — confirmed by code review, not just behavioural testing.

---

## 10. Statutory identity observability recommendation (04-002)

Per the sprint's explicit instruction, kept separate from the 04-001 fix
itself. Options assessed:

| Option | Assessment |
|---|---|
| Per-run immutable statutory rule ID/version | **Already exists** (`rules_context_snapshot.statutory_rule.id`/`.version`) — insufficient alone for 04-002, since it only proves what the *original* run used, not what a *specific retried employee's result* was calculated under |
| **Per-result statutory rule ID/version (recommended)** | Add `statutory_rule_id` and `statutory_version` columns (or a nested object) to `payroll_result`, populated at insert time from whichever source (snapshot, post-fix) actually produced that row's calculation. Minimal, directly queryable, requires one migration + one write-path change at the exact point `_insert_result`/`save_payroll_results_bulk` already run |
| Inclusion in `calculations_snapshot_json` | Would work but conflates a financial-summary field with an audit-identity field — not recommended as the primary mechanism, though harmless as a secondary echo |
| Inclusion in `component_trace_jsonb` | Already has a natural home (the `_period_context` header entry, per Stage 02's citation) — a `statutory_rule_id`/`version` key could be added there cheaply, but `component_trace_jsonb` is `None` on the legacy executor path (Stage 01/02) and is a JSONB blob, not a queryable column — useful as a *secondary* confirmation, not the primary mechanism |
| Inclusion in `execution_trace` | Not recommended as primary — Stage 02 already established retry writes zero `execution_trace` rows (02-002), so this would require fixing that gap first, and `execution_trace` is a step-level table, not naturally scoped to a specific employee's result |

**Minimum reliable design:** add `payroll_result.statutory_rule_id` (UUID,
nullable — legacy rows predating the migration have no value, which is
itself informative) and `payroll_result.statutory_version` (integer,
nullable), populated at every insert (both original run and retry) from the
same value used for that calculation. This directly closes 04-002: any
`payroll_result` row becomes independently auditable without forensic
recomputation, and — as a secondary benefit — provides a natural place to
add a future consistency check ("does this employee's `statutory_rule_id`
match the run's `rules_context_snapshot.statutory_rule.id`?") that could
catch a *future* regression of 04-001's class automatically.

---

## Handoff notes for later stages

- **Stage 07 (silent failures and observability):** 05-001 (swallowed
  snapshot-creation exception) is a direct, newly-confirmed input — a
  concrete example of a background-task failure with zero operator-visible
  signal.
- **Stage 08 (data integrity):** carries forward Stage 04's 04-004
  (reconciliation-refresh parity, still unverified) — this stage did not
  add new evidence on that question.
- **Stage 10 (execution-trace remediation):** §11's recommended design
  (per-result `statutory_rule_id`/`statutory_version` columns) is a direct
  input for closing 04-002 — note it is a `payroll_result` schema addition,
  not an `execution_trace`/`component_trace_jsonb` change, so it sits
  alongside whatever Stage 10 designs for the broader trace-remediation
  question rather than being folded into it.
- **Stage 11 (scenario testing):** the two regression tests specified in §9
  ("Required regression tests") are ready to be formalized once the fix
  lands; this stage's evidence folder does not include a working
  post-fix test (the fix is not implemented), only the specification.
- **Stage 12 (code simplification):** 05-002 (dead
  `employee_contract_snapshot.components_jsonb` column, confirmed safe to
  remove), and 05-005 (duplicated statutory-extraction logic between
  `payroll.py` and `payroll_retry_service.py`, a natural target for
  extraction into one shared function as part of implementing the 04-001
  fix itself, not a separate later cleanup).
- **The immediate post-Stage-05 remediation sprint** (per Stage 04's
  decided timing — before Stage 13, before any live payroll processing or
  production release): §9's canonical contract is the bounded specification
  to implement. Scope is deliberately narrow — a read-path change in
  `payroll_retry_service.py::_build_shared_context` plus one new validation
  check — no snapshot schema change is required for 04-001 itself (§8's
  sufficiency conclusion). §10's per-result identity columns for 04-002 can
  be implemented in the same sprint (small, additive migration) or deferred
  to a follow-up — this stage recommends bundling them, since the same
  sprint will already be touching the exact insert call sites.
