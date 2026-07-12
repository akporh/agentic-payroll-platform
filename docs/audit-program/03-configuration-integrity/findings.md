# Stage 03 — Findings

Status: **in-progress**. All entries below use the template in
[`../_core/finding-schema.md`](../_core/finding-schema.md).

---

## 1. Configuration catalogue

One row per configuration domain. "Original-run consumer" / "Retry consumer" columns
cite the actual reading code, not the schema — per this stage's constraint not to
infer consumption from existence of a field.

| Configuration | Business purpose | Entry point | Persistence | Duplicate representation? | Original-run consumer | Retry consumer | Snapshot behaviour | UI visibility |
|---|---|---|---|---|---|---|---|---|
| Component metadata (platform) | Defines every payroll component's class/calc method/execution order for a country | Platform-seeded via migrations, not editable via UI | `component_metadata` table | No | `payroll.py` route, live query | `component_metadata_snapshot`, frozen at run creation | Frozen at run time (`snapshot_service.py`) | Read-only list at `GET /{ws}/platform-components` |
| Client component overrides | Per-workspace override of platform component behaviour (disable, flat amount, proration) | `WorkspaceConfig.tsx` → `PATCH /{ws}/component-overrides/{code}` | `client_component_metadata` table; `overrides_json` (JSONB) + dedicated `proration_strategy`/`is_active` columns | **Yes — see 03-001** | `payroll.py` route, live query, reconciled into `client_meta` | `client_component_metadata_snapshot`, frozen at run creation | Frozen at run time | `GET /{ws}/component-overrides`, `GET /{ws}/configuration` |
| Payroll rules (legacy, pre-rule-set) | Workspace-specific calculation rules (OT, absences, allowances) | `WorkspaceConfig.tsx` → payroll-rule CRUD routes | `payroll_rule` table, `rule_definition_json` (JSONB), `is_active` + `effective_from` columns | No (single representation; `is_active`+`effective_from` is a resolution pair, not a duplicate — per `CLAUDE.md` invariant) | `resolve_effective_rules()` — date-driven | Same function, date-driven, or `rule_set_item` if `rule_set_id` present | Not directly snapshotted (superseded by rule sets where present) | `GET /{ws}/configuration` (all versions) |
| Rule sets / rule-set items | Immutable, point-in-time frozen snapshot of the payroll-rule set effective on a given date | Auto-published on payroll-rule create/version-save (`auto_publish()`); backfillable via `backend/scripts/backfill_rule_set_snapshots.py` | `rule_set`, `rule_set_item` tables | No (this *is* the snapshot mechanism for payroll rules) | `payroll.py` resolves `rule_set_id` for the period | Reads `rule_set_item` by the exact frozen `payroll_run.rule_set_id` | Immutable by construction once created (locked by first referencing run) | Not directly UI-editable; surfaced indirectly via `payroll_rule` UI |
| Statutory rule (PAYE bands, pension/NHF/health/levy/life-insurance rates) | Country-level statutory configuration | Platform-seeded via migrations | `statutory_rule` (`rules_jsonb`), `tax_band` tables; `(country_code, effective_from)` UNIQUE | **Yes — see 03-002** | `payroll.py`, live date-driven query; also written into `rules_context_snapshot.statutory_rule` (v2) | `payroll_retry_service.py::_build_shared_context`, **live date-driven re-query — snapshot's `statutory_rule` key is never read** | Frozen content exists in `rules_context_snapshot` but is unused for retry | Not directly UI-editable |
| Salary definitions | Per-grade/role component amounts (BASIC, HOUSING, TRANSPORT, etc.) | `WorkspaceConfig.tsx` → `PATCH /{ws}/salary-definition/{id}` | `salary_definition.components_jsonb` | **Yes — see 03-003** | `payroll.py`, live read via `employee_contract.salary_definition_id` | `payroll_retry_service.py`, live read via `employee_contract_snapshot.salary_definition_id` JOIN live `salary_definition` | `employee_contract_snapshot.components_jsonb` captured but never read back (03-003) | `GET /{ws}/configuration` |
| Pay cycle | Payroll frequency (MONTHLY/etc.), run/cutoff/payment days | `WorkspaceSetup.tsx` / `WorkspaceConfig.tsx` | `pay_cycle` table (`frequency`, `definition_json`), `is_active` — `CLAUDE.md` invariant: at most one active per workspace | No | `payroll.py`, live query, feeds `build_period_context()` as a default (explicit API field takes precedence) | Not re-queried — `period_ctx` rebuilt from `payroll_run.period_start/period_end` (frozen) plus `public_holidays_snapshot`; frequency itself is not re-resolved | Period dates frozen on `payroll_run`; `pay_cycle.frequency` itself not snapshotted (but not needed once dates are frozen) | `GET /{ws}/configuration` |
| Retry strategy | Which retry mode a run supports | Set at run creation, `POST /payroll/run` payload | `payroll_run.retry_strategy` column (moved off `workspace` — migration `f6a7b8c9d0e1`); `FULL_RUN` retired by CHECK constraint (migration `f7a1b2c3d4e5`) | No (single, per-run column — already corrected from an earlier per-workspace design) | N/A (set once at creation) | `payroll_retry_service.py:548` reads `payroll_run.retry_strategy` directly | Not applicable — it's the run's own column | Not surfaced as an editable UI control found in this stage |
| Attendance codes | Maps client-specific attendance codes to platform categories (absence, OT, etc.) | `AttendanceConfiguration.tsx` → `POST/PATCH /{ws}/attendance-codes` | `attendance_code_config` table | No | `timesheet_derivation_service.py` via `attendance_config_repo.get_attendance_policies_for_derivation()` — confirmed consumed | Same derivation service runs at timesheet-upload time, upstream of payroll run/retry — not a per-run config | Not snapshotted directly; its *output* (`payroll_input` rows) is claimed/frozen per run | `AttendanceConfiguration.tsx` |
| Public holidays | Dates excluded from working-day counts | `PublicHolidays.tsx` (workspace-specific); `national_public_holiday` platform-seeded | `national_public_holiday`, `workspace_public_holiday` tables | No (additive UNION, not competing precedence — see below) | `payroll.py:309-324`, live UNION query | Reads `ph_dates_used`/`ph_source` from `payroll_run.public_holidays_snapshot` (frozen) — does not re-query either table | Frozen (`ph_dates_used`, `ph_source`) — confirmed correct snapshot-first behaviour, contrast with statutory rule (03-002) | `PublicHolidays.tsx` |
| Employee/contract configuration | Contract dates, shift type, grade, salary_definition assignment | `Employees.tsx` (Upload/Enroll split, per `CLAUDE.md`) | `employee`, `employee_contract` tables | No (single representation; `employee_contract_snapshot` is the frozen copy, see 03-003) | Live `employee_contract` join | `employee_contract_snapshot` (structural fields only — `contract_start/end`, `shift_type`, `grade_id`, `grade_jsonb`; NOT `components_jsonb`, see 03-003) | Structural fields frozen; salary amounts intentionally live-joined (D1) | `Employees.tsx` |
| Reconciliation configuration | Configurable trigger/pre-payment-check rules | **Not implemented** — deferred per existing product backlog | N/A | N/A | N/A | N/A | N/A | `Reconciliation.tsx` shows results only, no configuration surface found |
| Onboarding configuration | Initial workspace/statutory/pay-cycle/component setup during first-time setup | `WorkspaceSetup.tsx` → `backend/api/routes/onboarding.py` | Writes into the same live tables listed above (`workspace`, `pay_cycle`, `component_metadata` selection, etc.) — no separate onboarding-only storage found | No (onboarding is a write path into the same tables, not a separate representation) | N/A — onboarding writes are read back through the same live-query paths as later edits | N/A | N/A | `WorkspaceSetup.tsx`, `onboarding_validation.py` |

---

## 2. Source-of-truth and precedence map

| Concept | Representations | Precedence | Evidence |
|---|---|---|---|
| Component proration strategy | (a) `client_component_metadata.proration_strategy` (dedicated column), (b) `overrides_json.calculations_behaviour.proration_strategy` (nested JSON) | **(a) wins** — both original run and retry explicitly reconcile column-over-JSON in identical code (03-001) | `evidence/2026-07-12-component-metadata-dual-storage-reconciled.txt` |
| Component is_active (workspace-level) | (a) `client_component_metadata.is_active` (dedicated column) | Single representation — `overrides_json` is never read for `is_active`; only the column. NULL → treat as active. | Same file |
| Statutory rule/tax bands for a run | (a) Live `statutory_rule`/`tax_band` tables, resolved by `effective_from <= statutory_effective_date`, (b) `rules_context_snapshot.statutory_rule` (frozen JSON, v2 runs only) | **Original run**: (a) is resolved and then written into (b). **Retry**: only (a) is read — (b) exists but is never consulted (03-002) | `evidence/2026-07-12-statutory-rule-retry-live-reresolve.txt` |
| Salary component amounts | (a) Live `salary_definition.components_jsonb`, (b) `employee_contract_snapshot.components_jsonb` (frozen at run creation) | **(a) always wins, by design (D1)** — (b) is written but never read (03-003) | `evidence/2026-07-12-employee-contract-snapshot-dead-column.txt` |
| Public holiday dates for a run | (a) Live `national_public_holiday` ∪ `workspace_public_holiday`, (b) `payroll_run.public_holidays_snapshot` (frozen) | **Original run**: (a), written into (b). **Retry**: (b) only — correct snapshot-first pattern | `evidence/2026-07-12-public-holidays-union-and-snapshot.txt` |
| Workspace payroll rules for a run | (a) Live `payroll_rule` (date-resolved), (b) `rule_set_item` (frozen, immutable once locked) | **Original run**: resolves (a) into a `rule_set`, i.e. (b) is created from (a). **Retry**: reads (b) directly by frozen `rule_set_id` if present, else falls back to re-resolving (a) for legacy pre-rule-set runs | `evidence/2026-07-12-rule-set-frozen-id-vs-statutory-date-only.txt` |
| Retry strategy | Single representation, `payroll_run.retry_strategy` | N/A — no duplication | grep, migration history |

---

### 03-001 — Component-level `proration_strategy` and `is_active` have dual storage locations, reconciled identically and correctly in both original run and retry

- **stage:** 03-configuration-integrity
- **location:** `backend/api/routes/workspace.py:1270-1340` (`patch_component_override` — writer); `backend/api/routes/payroll.py:432-493` (original-run reader/reconciler); `backend/application/payroll_retry_service.py:231-283` (retry reader/reconciler)
- **current implementation:** `client_component_metadata` stores `proration_strategy` and `is_active` as dedicated columns, while `overrides_json` (JSONB) can independently carry a nested `calculations_behaviour.proration_strategy` key inherited from the platform `component_metadata.metadata_json` base layer. Both the original-run route and the retry service build `client_meta` by (1) starting from platform `metadata_json`, (2) deep-merging `overrides_json` on top, then (3) explicitly overwriting `calculations_behaviour.proration_strategy` from the dedicated column if present — the column always wins. This three-step reconciliation is character-for-character identical between the two call sites.
- **intended behaviour:** Documented in-line at both sites ("If the column has a value it takes precedence over whatever is in overrides_json") — this is a deliberate, explained design, not an oversight.
- **suspected or confirmed defect:** None. Recorded as a confirmed duplicate representation with correct, synchronized precedence handling — a positive control example for what Stage 03 is checking for. Also confirms `is_active` has only one source (the column; `overrides_json` is never consulted for it) — no drift risk there.
- **evidence:** `evidence/2026-07-12-component-metadata-dual-storage-reconciled.txt`
- **status:** confirmed
- **severity:** S3 (documented, correctly reconciled, both call sites in sync)
- **related invariant:** none

---

### 03-002 — Retry re-resolves statutory rule/tax bands live from a frozen date, while the original run's frozen snapshot of the *actual resolved content* is never read

- **stage:** 03-configuration-integrity
- **location:** `backend/api/routes/payroll.py:605-635` (original run builds v2 snapshot with full `statutory_rule` content: `id`, `version`, `effective_from`, `rules_jsonb`, `tax_bands`); `backend/domain/rules/snapshot.py:96-111` (`build_rules_context_snapshot` v2 shape); `backend/application/payroll_retry_service.py:145-171` (`_build_shared_context` re-queries live `statutory_rule`/`tax_band` by `country_code` + `statutory_effective_date <= as_of_date ORDER BY effective_from DESC LIMIT 1`, never accesses `original_snapshot.get("statutory_rule")`)
- **current implementation:** The original run resolves the statutory rule live, then freezes the *result* (rule ID, version, full `rules_jsonb`, full tax band list) into `payroll_run.rules_context_snapshot["statutory_rule"]`. Retry has access to this exact frozen object (it already loads `original_snapshot = row[5]` at the top of `_build_shared_context`) but does not read the `"statutory_rule"` key from it — confirmed by grep, zero occurrences of `statutory_rule` as a snapshot-dict access anywhere in `payroll_retry_service.py`. Instead, retry re-runs the same date-driven resolution query the original run used, keyed only on the frozen `statutory_effective_date` scalar (a `payroll_run` column, not the snapshot JSON) against the **live** `statutory_rule`/`tax_band` tables. Contrast: `rule_set_item` (workspace payroll rules) *is* read by exact frozen ID on retry (03's precedence map, row 5) — the same "freeze an ID, join live-but-immutable-by-that-ID" pattern used there is not applied to `statutory_rule`, because `payroll_run` has no `statutory_rule_id` column at all (confirmed — no such column exists in any migration).
- **intended behaviour:** Not documented as intentional. The v2 snapshot's own purpose (per its docstring and the "F2 fix" comments elsewhere in the retry service, e.g. around `historical_rule_sets`: "Retry must never re-query live rule tables for historical rate resolution... is the authoritative source") states the general principle that retry should read frozen content, not re-query live tables — this principle is applied to `historical_rule_sets` and `rule_set_item` but not to `statutory_rule`/`tax_band`.
- **suspected or confirmed defect:** The mechanism is confirmed by direct code citation (retry re-queries live tables; the frozen alternative exists and is unused). Whether this can currently produce a divergent result between an original run and its retry is **plausible, not confirmed** — it requires a statutory_rule row to be inserted with an `effective_from` between the date originally resolved and the run's `statutory_effective_date` in the window between the original run and a subsequent retry. This is exactly the kind of change `CLAUDE.md`'s `statutory_rule (country_code, effective_from)` UNIQUE invariant anticipates (new dated versions are a normal, expected operation — e.g. mid-year statutory rate changes), so the precondition is realistic, not contrived. No DB evidence or controlled test was run in this stage to confirm an actual observed divergence (would require inserting a test statutory_rule row against a non-production DB, which is a controlled-execution step this stage did not perform).
- **evidence:** `evidence/2026-07-12-statutory-rule-retry-live-reresolve.txt`
- **status:** plausible
- **severity:** S1 (if the precondition fires, it is a silent original-run/retry divergence in PAYE/pension/NHF/health/levy calculation for exactly the employees being retried — the kind of issue `CLAUDE.md`'s severity framing for silent divergence targets; not S0 because it requires a specific, non-default admin action to trigger, not a routine code path)
- **related invariant:** `CLAUDE.md` — `statutory_rule (country_code, effective_from)` UNIQUE

---

### 03-003 — `employee_contract_snapshot.components_jsonb` is captured at run creation but has zero readers anywhere in the codebase

- **stage:** 03-configuration-integrity
- **location:** `backend/application/snapshot_service.py:108-135` (writer — `components_jsonb` populated from `emp.get("components_jsonb")`); `migrations/versions/b5c6d7e8f9a0_sprint19_snapshot_tables.py:29-50` (table creation, comment: "D1: salary_definition_id frozen; retry joins salary_definition live on it"); `backend/application/payroll_retry_service.py:619-658` (sole other reference to `employee_contract_snapshot` anywhere in `backend/`, and its `SELECT` list explicitly reads `sd.components_jsonb` from the **live** `salary_definition` join, not `ecs.components_jsonb`)
- **current implementation:** `employee_contract_snapshot.components_jsonb` is written on every run (part of the same `execute_values` batch as the structural fields that *are* later read: `contract_start`, `contract_end`, `shift_type`, `grade_id`, `grade_jsonb`). Confirmed by grep across all of `backend/` that no query, anywhere, ever selects `employee_contract_snapshot.components_jsonb` — the only SQL touching that table selects six other columns plus `sd.components_jsonb` from a joined live table under the same alias name, which could visually read as "the snapshot's own components" but is not.
- **intended behaviour:** The migration's own comment states the live-join is deliberate ("D1... retry joins salary_definition live on it") — this is an explicit architecture decision (salary corrections should apply retroactively even to a retry of an old run), not a bug in the read path. No document states whether the `components_jsonb` *column* on the snapshot table was intended to remain permanently unread, or was meant for a not-yet-built audit/diff feature (e.g. "show what changed between original run and now").
- **suspected or confirmed defect:** Confirmed as a dead-storage fact (write-only column, zero readers). Not a correctness defect: the D-ARCH-1 edit-lock (`backend/api/routes/workspace.py:1529-1550`) blocks `PATCH /salary-definition/{id}` whenever any employee on that definition has a run in `SUBMITTED, PROCESSING, CALCULATED, PARTIAL, APPROVED` — and `PARTIAL` (the only retry-eligible status) is in that blocking list — so the live-join cannot actually diverge from the original run's amounts during the window a retry is possible. The dead column is therefore inert, not risky, but it is unclear whether it was meant to ever be read (e.g. as a comparison baseline the edit-lock currently makes unreachable, or for a future audit view).
- **evidence:** `evidence/2026-07-12-employee-contract-snapshot-dead-column.txt`
- **status:** confirmed (dead-storage fact); the "is this consequence-free" claim is confirmed via the separately-verified D-ARCH-1 lock, not assumed
- **severity:** S3 (write-only column, no correctness impact given the lock; candidate for Stage 12 simplification review)
- **related invariant:** none directly; adjacent to `employee_contract.end_date` invariant in spirit (both concern which "version" of employee data a calculation should use)

---

### 03-004 — `patch_component_override`'s D-ARCH-2 statutory-protection guard is present in code but explicitly disabled by comment, not by removal

- **stage:** 03-configuration-integrity
- **location:** `backend/api/routes/workspace.py:1316-1320`
- **current implementation:** The route docstring lists "D-ARCH-2: Statutory deduction components cannot be disabled" as a guard, but the guard's implementation is a comment block reading "Guard is intentionally not enforced for now — operators may disable any component per workspace (e.g. NHF, NHIS, Check-Off Dues vary by employer). Re-enable this block to restore the restriction in future." No code currently prevents a workspace from disabling a `statutory_deduction`-class component via `client_component_metadata.is_active = false`.
- **intended behaviour:** The comment itself documents the current intended behaviour (permissive — any component may be disabled) and flags it as a deliberate, reversible relaxation of an earlier, stricter rule, not an accidental gap.
- **suspected or confirmed defect:** Not a defect against currently-stated intent — the docstring's own guard description ("D-ARCH-2: cannot be disabled") is now stale relative to the comment immediately below it, which is a documentation-drift issue inside a single file rather than a functional one. Flagged for Stage 03's completeness (this is exactly the kind of "documented guard vs. actual enforcement" gap this stage looks for) and because it means a workspace *can* disable NHF, pension, or PAYE-adjacent statutory components today if `client_component_metadata.is_active = false` is set for them — worth Stage 09 (security/tenant isolation) or Stage 13 confirming this permissiveness is still the desired product behaviour, since disabling a genuinely mandatory statutory deduction could create a compliance gap outside this audit's scope to judge.
- **evidence:** `evidence/2026-07-12-component-metadata-dual-storage-reconciled.txt`
- **status:** confirmed
- **severity:** S2 (compliance-adjacent — statutory deductions becoming disableable is a business-rules question this audit cannot resolve, but the code fact is confirmed and worth flagging up)
- **related invariant:** none listed in `CLAUDE.md`'s Known Data Contract Rules table; this may be a gap in that table worth a human decision

---

### 03-005 — Public holiday and rule-set resolution correctly follow the frozen-snapshot-on-retry pattern; recorded as a positive control, not a defect

- **stage:** 03-configuration-integrity
- **location:** `backend/api/routes/payroll.py:309-324` (original-run live UNION); `backend/application/payroll_retry_service.py:130-134` (`ph_snapshot` read from `payroll_run.public_holidays_snapshot`, converted to `public_holiday_dates`, never re-queries `national_public_holiday`/`workspace_public_holiday`); `backend/application/payroll_retry_service.py:284-311` (`rule_set_item` read by frozen `payroll_run.rule_set_id`)
- **current implementation:** Both of these configuration domains follow the pattern 03-002 shows is *missing* for statutory rules: the original run resolves the live configuration once, freezes the result, and retry reads only the frozen result — never re-querying the live source tables.
- **intended behaviour:** Consistent with the general snapshot-determinism principle stated elsewhere in the codebase (the "F2 fix" comment).
- **suspected or confirmed defect:** None. Recorded so Stage 04 (retry parity) has a confirmed-correct baseline alongside 03-002's confirmed-gap, rather than only seeing the negative findings.
- **evidence:** `evidence/2026-07-12-public-holidays-union-and-snapshot.txt`, `evidence/2026-07-12-rule-set-frozen-id-vs-statutory-date-only.txt`
- **status:** confirmed
- **severity:** S3 (positive finding)
- **related invariant:** none

---

## 3. Duplicate-representation register (summary)

| Duplicate | Writers | Readers | Precedence | Drift risk | Conflict handling |
|---|---|---|---|---|---|
| `proration_strategy` (column vs. JSON) | `patch_component_override` (column only) | Original run + retry, identically | Column wins, always | None — column is the only writer, JSON copy is inherited from platform defaults only | Explicit overwrite, not a rejection — no error path needed since one side never diverges independently |
| `is_active` for components (column vs. absence in JSON) | `patch_component_override` (column only) | Original run + retry | Column only; JSON never consulted | None | N/A |
| Statutory rule (live tables vs. `rules_context_snapshot.statutory_rule`) | Live tables: platform migrations. Snapshot: written once at original-run time | Original run reads live; retry reads live again (not the snapshot) | Live always wins for retry, snapshot content is inert | **Yes — see 03-002** | No conflict detection exists; a silent divergence would not raise an error, it would simply compute a different result |
| Salary components (live `salary_definition` vs. `employee_contract_snapshot.components_jsonb`) | Live: `patch_salary_definition`. Snapshot: written once at run creation | Both original run and retry read live only | Live always wins, snapshot inert | No — mitigated by D-ARCH-1 edit-lock during the only window retry is possible | N/A (dead column, no active conflict path) |
| Public holidays (live tables vs. `payroll_run.public_holidays_snapshot`) | Live: `PublicHolidays.tsx` CRUD. Snapshot: written once at run creation | Original run reads live; retry reads snapshot only | Correctly snapshot-first for retry | None — this is the correct pattern | N/A |
| Payroll rules (live `payroll_rule` vs. `rule_set_item`) | Live: rule CRUD, triggers `auto_publish()`. Rule set: auto-generated, immutable once locked | Original run resolves live into a rule set; retry reads rule set by frozen ID (or falls back to live resolution for legacy pre-rule-set runs) | Correctly snapshot-first for v2 runs | Low — only affects legacy runs without a `rule_set_id`, which fall back to the same date-driven live resolution both paths already agree on | N/A |

---

## 4. Dead or unused configuration register

| Configuration | Status | Evidence | Finding |
|---|---|---|---|
| `employee_contract_snapshot.components_jsonb` | Persisted, never read | `evidence/2026-07-12-employee-contract-snapshot-dead-column.txt` | 03-003 |
| `rules_context_snapshot.statutory_rule` (the full frozen object, not just its existence) | Persisted, never read by retry (read only implicitly via the route response to the original caller) | `evidence/2026-07-12-statutory-rule-retry-live-reresolve.txt` | 03-002 |
| Reconciliation configuration | Not yet built — no dead code, simply absent (deferred product feature, consistent with existing backlog memory) | grep — zero matches for `reconciliation_config`/`auto_reconcile` anywhere in `backend/` | N/A — not a defect, a scope note |

No instance was found in this stage of the inverse direction — UI displaying a control that silently fails to save, or backend-supported configuration entirely unavailable in the UI — within the domains investigated. This does not rule out such cases in domains outside this stage's catalogue depth (see Stage 06 handoff below).

---

## 5. Original-run / retry configuration-consumption comparison

| Configuration | Original run reads | Retry reads | Same? |
|---|---|---|---|
| Component metadata (platform) | Live `component_metadata` | `component_metadata_snapshot` (frozen) | Different tables, same effective content (frozen at run time from the same live read) — correct by design |
| Client component overrides | Live `client_component_metadata` | `client_component_metadata_snapshot` (frozen) | Same as above — correct |
| Statutory rule / tax bands | Live `statutory_rule`/`tax_band`, resolved once, then frozen into snapshot | Live `statutory_rule`/`tax_band`, **re-resolved independently** | **Different mechanism, same live tables — see 03-002** |
| Salary components | Live `salary_definition.components_jsonb` via `employee_contract` | Live `salary_definition.components_jsonb` via `employee_contract_snapshot.salary_definition_id` JOIN | Same live table, both by design (D1) — correct, mitigated by edit-lock |
| Payroll rules | Live `payroll_rule`, resolved into a `rule_set` | `rule_set_item` by frozen ID (v2) or live re-resolution (legacy) | Correct — matches by design |
| Public holidays | Live UNION of two tables | `payroll_run.public_holidays_snapshot` (frozen) | Correct — snapshot-first |
| `execution_trace` step-level footprint (from Stage 02) | ~7–9 rows | **Zero rows** (Stage 02 finding 02-002) | Different — carried forward from Stage 02, not re-derived here |

---

## 6. Snapshot/live configuration boundary map

```
                          ORIGINAL RUN                          RETRY (per-employee, only enabled strategy)
                          ─────────────                          ────────────────────────────────────────
component_metadata        live table  ──┐                        component_metadata_snapshot  (frozen) ✓
client_component_metadata live table  ──┼─→ snapshot_service.py   client_component_metadata_snapshot (frozen) ✓
employee_contract         live table  ──┘   freezes 3 tables      employee_contract_snapshot (frozen,
                                                                    but components_jsonb unused — 03-003)

statutory_rule / tax_band live tables ──→ rules_context_snapshot  LIVE TABLES AGAIN, re-resolved — 03-002 ✗
                                           .statutory_rule (frozen,
                                            but unused by retry)

payroll_rule               live table ──→ rule_set / rule_set_item  rule_set_item by frozen ID ✓
                                           (auto-published, immutable)

national/workspace_public_holiday
                            live tables ──→ payroll_run             payroll_run.public_holidays_snapshot ✓
                                            .public_holidays_snapshot
```

Legend: ✓ = retry correctly reads frozen content. ✗ = retry re-reads live source
despite a frozen alternative existing and being unused.

---

## 7. Silent-default and conflict-behaviour register

| Situation | Behaviour | Evidence |
|---|---|---|
| `client_component_metadata.is_active` is NULL | Treated as active (both original run and retry) | `evidence/2026-07-12-component-metadata-dual-storage-reconciled.txt` — comment: "NULL means no override → treat as active" |
| `client_component_metadata_snapshot` row predates the snapshot column migration | Treated as active | `evidence/2026-07-12-...` retry comment: "Rows predating the migration yield {} — eligibility gates suppressed" (this refers to `per_employee_context_json`, a related but distinct silent-default; noted for completeness) |
| Component has no `client_component_metadata` row at all | Falls through to platform `component_metadata.metadata_json` only, no error | `client_meta` construction — base layer always populated from platform metadata regardless of override presence |
| Workspace has zero `client_component_metadata` rows | `validate_snapshot_complete()` explicitly does NOT treat this as an error — "a workspace with zero component overrides is valid" | `backend/application/snapshot_service.py:150-152` |
| Statutory rule with an `effective_from` between the original resolution and a later retry | **Silently produces a different result** — no error, no divergence check, no warning (03-002) | `evidence/2026-07-12-statutory-rule-retry-live-reresolve.txt` |
| `payroll_run` predates the snapshot engine (no `statutory_effective_date`) | Hard-fails with `ValueError` ("open a correction run") — not silent | `backend/application/payroll_retry_service.py:161-164` |

---

## Human-decision candidates raised (logged separately)

See [`../_core/human-decisions.md`](../_core/human-decisions.md).

| Question | Finding(s) |
|---|---|
| Should retry read the frozen `rules_context_snapshot.statutory_rule` instead of re-resolving live, to close the original-run/retry divergence risk? | 03-002 |
| Is `employee_contract_snapshot.components_jsonb` meant to ever be read (e.g. an audit/diff feature), or is it dead weight to remove in a future simplification pass? | 03-003 |
| Is the current permissive behaviour of `patch_component_override` (any component, including statutory deductions, may be disabled per workspace) still the intended product behaviour, and should `CLAUDE.md`'s Known Data Contract Rules table document it explicitly? | 03-004 |

---

## Handoff notes for later stages

- **Stage 04 (original-run and retry parity):** 03-002 is the highest-priority
  input — it identifies a concrete, plausible mechanism for original-run/retry
  divergence in statutory calculation that Stage 04 should attempt to
  reproduce with a controlled test (insert a test `statutory_rule` row with an
  intervening `effective_from`, run, retry, compare). Section 5 and 6 above
  give Stage 04 the full consumption-comparison table so it does not need to
  re-derive which paths are snapshot-correct vs. live-re-resolved.
- **Stage 05 (snapshot integrity):** 03-003 (dead snapshot column) and 03-002
  (unused snapshot content) are both snapshot-completeness questions in
  Stage 05's specific remit — this stage found the *consumption* gap; Stage 05
  should assess whether the *snapshot content itself* is complete and correct
  independent of whether it's read.
- **Stage 06 (UI/API/backend wiring):** This stage's configuration catalogue
  (Section 1) covers the domains listed in the sprint prompt but was not
  exhaustive on every UI control's save-path fidelity — Stage 06 should treat
  Section 1's "UI visibility" column as a starting index, not a completed
  wiring audit. In particular, `pay_cycle.definition_json` (JSONB extension
  data referenced at `payroll.py:299`) was not traced to any specific UI
  control in this stage and is a candidate for Stage 06 to pick up.
- **Stage 07 (silent failures and observability):** Section 7 (silent-default
  register) is a direct input — none of the listed silent defaults raise or
  log, several are intentional/documented, but 03-002's divergence has no
  observability at all (no warning, no trace entry, nothing in
  `execution_trace` per Stage 02's findings) if it were to fire.
- **Stage 08 (data integrity):** 03-004 (statutory components can be disabled
  workspace-wide with no restriction) is a data-integrity-adjacent concern
  Stage 08 should assess for actual production impact (are any statutory
  components currently disabled in any live workspace?).
- **Stage 12 (simplification and duplicate removal):** 03-003's dead column
  and 03-001's (correctly-handled but still dual-storage) `proration_strategy`
  are both candidates for simplification — 03-001 should NOT be
  "simplified away" without preserving the documented column-wins precedence,
  since both call sites currently agree by careful duplication of the same
  reconciliation logic in two places (a DRY violation, but a synchronized one).
