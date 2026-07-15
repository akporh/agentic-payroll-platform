# Stage 01: Current Operating Model — Findings

Schema: `_core/FINDING-SCHEMA.md`. All findings below are backed by direct code/migration reads (see `_inputs/source-register.md` for the consulted sources). No architecture documents, roadmap notes, or memory files were used as evidence — where a memory-file claim was in scope, it was independently re-verified against current code before being recorded here (per `_core/EVIDENCE-STANDARD.md`).

This stage is descriptive only. Severity is recorded per `_core/SEVERITY-MODEL.md` because the schema requires it on confirmed findings, but no recommendation, redesign, or fix is proposed here — that is out of scope for Stage 01.

---

## Draft Findings

(none — all observations below met the evidence bar directly from code/migration reads and were recorded as confirmed; nothing is carried forward as an unverified hypothesis)

---

## Confirmed Findings

### Area 1 — Workspace and tenant creation

#### F-01-01: Workspace creation route never sets `account_id`
- **Current implementation**: `Workspace` model (`backend/infra/db/models/workspace.py:7-16`) has a nullable `account_id` FK to `account`. `POST /workspace` (`backend/api/routes/workspace.py:45-95`) accepts `name`, `country_code`, `base_currency` only — `account_id` is never part of the request schema or the INSERT. Every workspace created through this route has `account_id = NULL`. Status is hardcoded to `'DRAFT'` on insert.
- **Intended design**: Undocumented — no spec or comment states whether multi-account/tenant grouping above workspace level is intended to be populated later or is dead schema.
- **Identified gap**: A modeled parent-tenant relationship (`account`) exists in the schema but is not wired to any creation path.
- **Evidence**: `backend/infra/db/models/workspace.py:7-16`; `backend/api/routes/workspace.py:45-95`; `backend/infra/db/models/account.py:7-11`
- **Severity**: Low — no observed dependency on `account_id` elsewhere; a nullable unused FK.
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster A

#### F-01-02: Workspace status is a DB enum with a payroll-creation guard trigger
- **Current implementation**: `workspace.status` is a Postgres ENUM (`DRAFT, STRUCTURE_DEFINED, COMPENSATION_DEFINED, RULES_DEFINED, READY, LIVE`) per `migrations/versions/b2e7a07972b7_add_workspace_status.py:20-53`. A `BEFORE INSERT ON payroll_run` trigger `enforce_workspace_live_before_payroll()` (`migrations/versions/0daab4ac893b_enforce_workspace_live_before_payroll.py:20-49`) rejects run creation unless `workspace.status = 'LIVE'`.
- **Intended design**: Matches — this is the documented onboarding gate; no separate spec contradicts it.
- **Identified gap**: None.
- **Evidence**: cited migrations above
- **Severity**: Informational
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster A

#### F-01-03: `workspace_id` scoping is present on nearly all domain tables, with two confirmed exceptions
- **Current implementation**: `workspace_id` is a column/FK on `client_component_metadata`, `grade`, `designation`, `pay_cycle`, `salary_definition`, `payroll_input`, `workspace_public_holiday`, `rate_code_registry`, `rule_set`, `payroll_rule`, `workspace_payroll_config`, `employee`, `payroll_run`, `audit_log`. Two confirmed tables have no `workspace_id` column at all: `employee_contract` (scoped only via join through `employee.workspace_id` — explicit comment at `backend/infra/repositories/employee_repo.py:415-418`) and `payroll_reconciliation` (no `workspace_id` column in its migration or ORM model; see F-01-15). The platform-level `component_metadata` table is intentionally workspace-agnostic, keyed by `country_code` instead.
- **Intended design**: Global project rule (`CLAUDE.md`): "Workspace scoping is mandatory on every DB query." `employee_contract`'s no-workspace-id design is a known, previously-documented tradeoff (memory: `feedback_employee_contract_workspace_scope.md`) — re-verified here directly against `employee_repo.py`.
- **Identified gap**: `employee_contract` scoping-through-join is consistently applied everywhere checked in this stage (`update_employee_contract`, `bulk_enroll_employee_contracts`). `payroll_reconciliation` has no equivalent join-based scoping — see F-01-15 for the specific gap.
- **Evidence**: `backend/infra/repositories/employee_repo.py:415-418`; `backend/infra/db/models/payroll_reconciliation.py:7-24`; grep of `backend/infra/db/models/*.py` for `workspace_id`
- **Severity**: Informational (for the general pattern); see F-01-15 for the reconciliation-specific gap severity
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster A / Cluster D

---

### Area 2 — Onboarding and structural configuration

#### F-01-04: Onboarding is a strict forward-only state machine gated by structural prerequisite checks
- **Current implementation**: `backend/domain/onboarding/workspace_state_machine.py:4-11` defines `DRAFT → STRUCTURE_DEFINED → COMPENSATION_DEFINED → RULES_DEFINED → READY → LIVE`, each with exactly one allowed next state (or none, for `LIVE`). `backend/domain/onboarding/hard_validator.py:147-196` requires: pay_cycle+grade+designation to exist before `STRUCTURE_DEFINED`; ≥1 salary_definition before `COMPENSATION_DEFINED`; ≥1 active payroll_rule before `RULES_DEFINED`; component_metadata present for the workspace's country before `READY`. No additional structural check gates `LIVE` itself (comment: "Execution guard handles payroll safety").
- **Intended design**: Matches the implementation — this is a single coherent state machine with no divergent spec found.
- **Identified gap**: None identified against a documented intent. Note (factual, not evaluative): `has_component_metadata` for the `READY` gate checks the **platform** `component_metadata` table filtered by country, not anything workspace-specific — so this specific gate can be satisfied even if the workspace itself has made no component choices.
- **Evidence**: `backend/domain/onboarding/workspace_state_machine.py:4-11`; `backend/domain/onboarding/hard_validator.py:147-196`; `backend/infra/db/repositories/workspace_repo.py:16-44`
- **Severity**: Informational
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster A

#### F-01-05: Structural configuration is created through two parallel paths — bulk onboarding commit and individual per-entity routes
- **Current implementation**: `POST /onboarding/commit` (`backend/api/routes/onboarding.py:146`) writes `salary_definition`, employee, and contract rows in one bulk flow after a separate `/onboarding/preview` validation-only step. Separately, individual creation routes exist per entity: `POST /{workspace_id}/pay-cycle`, `/grade`, `/designation`, `/salary-definition`, `/payroll-rule`, `/component-metadata` (`backend/api/routes/workspace.py:855-1045`), each calling `backend/application/onboarding_service.py` functions wrapped in `@auto_infer_workspace_state`, which recomputes/advances `workspace.status` after each write.
- **Intended design**: Undocumented as a single spec; both paths are live production code, not one legacy/one active.
- **Identified gap**: Two distinct entry points populate overlapping structural state (e.g. salary_definition can be created via bulk commit or the individual route). No evidence found of the two paths conflicting on constraints (both are subject to the same DB unique indexes), but this stage did not test concurrent use of both paths in the same session.
- **Evidence**: `backend/api/routes/onboarding.py:45,90,146,200-244`; `backend/api/routes/workspace.py:855-1045`; `backend/application/onboarding_service.py:17-162`; `backend/application/decorators.py:5`
- **Severity**: Informational
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster A

---

### Area 3 — Salary components and metadata

#### F-01-06: Two-tier component metadata (platform vs workspace override), with `is_pensionable` and taxability flags stored inside JSONB rather than as columns
- **Current implementation**: `ComponentMetadata` (platform, keyed by `component_code, country_code, version` — unique index `uq_component_metadata_code_country_version`) vs `ClientComponentMetadata` (per-workspace override, unique on `(workspace_id, component_code)`). `is_pensionable`/`is_taxable`/`is_proratable` live inside `metadata_json.legal_role` (e.g. `migrations/versions/8d2b70219b84_seed_ng_earning_component_metadata.py:90`), read at runtime by `sequential_executor.py:298-315`. A second `active` boolean column (distinct from `is_active`) was added later specifically to "control participation in the sequential execution pipeline" (`migrations/versions/b3363ecdb054_...py:22-26`) — i.e. two different boolean flags with different meanings coexist on `component_metadata`.
- **Intended design**: `component_class = 'non_taxable'` and related classes are documented project rules (`CLAUDE.md` Known Data Contract Rules) — re-verified directly in `sequential_executor.py` rather than taken from `CLAUDE.md` alone.
- **Identified gap**: The coexistence of `is_active` (older) and `active` (newer, execution-pipeline-specific) as two separately named boolean columns on the same table is a naming ambiguity confirmed in the migration itself, not inferred.
- **Evidence**: `backend/infra/db/models/component_metadata.py:7-30`; `migrations/versions/a1c2e3f4b5d6_add_component_code_seed_platform_components.py:657-756`; `migrations/versions/b3363ecdb054_component_metadata_active_and_taxable_income_priority.py:22-26`; `backend/domain/payroll/sequential_executor.py:298-315,535-539,667-678`
- **Severity**: Low — confirmed naming ambiguity between `is_active` and `active`, no observed miscalculation from it in this stage's scope (calculation correctness is Stage 10's remit).
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster A

#### F-01-07: `PH_OT` component was seeded without `is_pensionable` pending a handler fix, per the seeding migration's own comment
- **Current implementation**: `migrations/versions/b0c1d2e3f4a5_add_rate_code_registry.py:8-12,78-83` states in-migration that `is_pensionable` "does NOT live on this table — it lives on component_metadata" and that the flag was deliberately withheld for `PH_OT` pending a handler fix.
- **Intended design**: The migration's own comment states the intended eventual state (flag present once handler fix lands) but does not fix a date.
- **Identified gap**: `PH_OT`'s pensionable status is, per this migration comment, an intentionally incomplete/staged rollout as of the time that migration was written. This stage did not verify whether a later migration completed the fix — that would require checking migrations after `b0c1d2e3f4a5` for a corresponding update, which was outside this cluster's specific query. Recorded here as a fact about the seeding migration's stated intent, not a confirmed current-state gap.
- **Evidence**: `migrations/versions/b0c1d2e3f4a5_add_rate_code_registry.py:8-12,78-83`
- **Severity**: Not rated — staleness of this specific claim (whether since fixed) is unverified; flagged for Stage 08/10 to re-check against the current `PH_OT` component_metadata row.
- **Status**: confirmed (as a migration-text fact); the underlying current-state question is explicitly NOT confirmed either way
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster A

---

### Area 4 — Grades and designations

#### F-01-08: `salary_definition` does not store `grade_id`/`designation_id` — the actual link lives on `employee_contract`
- **Current implementation**: `salary_definition` has no `grade_id`/`designation_id` column (confirmed absent via grep across models/migrations). Its `code` column is documented by convention as `UPPER(designation)_UPPER(grade)` (`migrations/versions/c2d3e4f5a6b7_add_salary_definition_code.py:8-11`, which itself states "designation/grade are not stored on the salary_definition table itself"). The actual grade/designation assignment for a specific employee is on `employee_contract.grade_id`/`designation_id` (added by `7685c65f5d2_...py` and `695bcbcc42f3_...py` respectively).
- **Intended design**: This matches a previously-recorded project understanding (memory: `feedback_salary_def_live_read.md`, `project_salary_def_code_format.md`) — re-verified directly against the migrations here rather than cited from memory alone.
- **Identified gap**: `salary_definition.code` is a naming convention enforced nowhere in the schema (no CHECK constraint tying `code` format to an actual `grade`/`designation` pair) — it is purely a human-readable label; the authoritative grade/designation binding is the separate `employee_contract` row.
- **Evidence**: `backend/infra/db/models/salary_definition.py:7-16`; `migrations/versions/c2d3e4f5a6b7_add_salary_definition_code.py:8-11`; `migrations/versions/7685c65f5d2_add_grade_and_employee_contract_tables.py:37-46`; `migrations/versions/695bcbcc42f3_add_component_metadata_designation_.py:93-113`
- **Severity**: Informational
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster A

#### F-01-09: `grade.total_monthly` percentage-split path coexists with the `salary_definition.components_jsonb` path for deriving BASIC/HOUSING/TRANSPORT/UTILITY
- **Current implementation**: When `grade.total_monthly` is set, a CHECK constraint (`chk_grade_pct_completeness`, `migrations/versions/a2b3c4d5e6f7_add_grade_percentage_structure.py:415-428`) requires all four percentage columns to be populated and sum to 1.0 (±0.0001), and the engine is documented (model comment, `grade.py:14-16`) to derive components from `total_monthly × pct` instead of `salary_definition.components_jsonb` in that case.
- **Intended design**: Undocumented outside this model comment and constraint — no spec found describing when an operator should use the grade-percentage path vs. the salary-definition-JSON path.
- **Identified gap**: Two independent mechanisms exist for deriving the same set of earning components (BASIC/HOUSING/TRANSPORT) for a given employee, selected implicitly by whether `grade.total_monthly` is NULL. This stage did not verify the selection logic in `sequential_executor.py` directly (that was Cluster A's grade/designation focus, not the executor cluster) — flagged for Stage 08 (Technical Architecture) to confirm the selection code path.
- **Evidence**: `backend/infra/db/models/grade.py:7-21`; `migrations/versions/a2b3c4d5e6f7_add_grade_percentage_structure.py:415-428`
- **Severity**: Not rated pending Stage 08 confirmation of the selection code path
- **Status**: confirmed (existence of both mechanisms); selection-logic detail marked for follow-up, not fabricated here
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster A

---

### Area 5 — Pay-cycle and rule-set configuration

#### F-01-10: `pay_cycle` single-active-row invariant is enforced at both application and DB level; `payroll_rule.is_active` requires date-driven resolution, never used alone
- **Current implementation**: Only one `is_active=TRUE` `pay_cycle` row per workspace is enforced by both `onboarding_service.create_pay_cycle` (application-level deactivation of prior rows) and a DB partial unique index `uq_pay_cycle_active` (`migrations/versions/e6f7a8b9c0d1_add_unique_active_pay_cycle.py:41-47`). For `payroll_rule`, `resolve_effective_rules` (`backend/application/rule_set_service.py:22-48`) always resolves via `SELECT DISTINCT ON (rule_name) ... WHERE effective_from <= :as_of_date ORDER BY rule_name, effective_from DESC` — `is_active` is applied only as an additional optional filter, never as the sole selector.
- **Intended design**: Matches the documented project rule (`CLAUDE.md`: "`is_active` means 'not withdrawn,' never 'currently in effect'... resolution must always be date-driven") — re-verified directly against `rule_set_service.py` rather than accepted from the `CLAUDE.md` rule alone.
- **Identified gap**: None — the current code matches the documented invariant everywhere checked in this stage.
- **Evidence**: `backend/application/onboarding_service.py:18-23`; `migrations/versions/e6f7a8b9c0d1_add_unique_active_pay_cycle.py:41-47`; `backend/application/rule_set_service.py:22-48`
- **Severity**: Informational
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster A

#### F-01-11: `rule_set`/`rule_set_item` are immutable-after-publish snapshots; `auto_publish` blocks re-publishing over a rule set already used by a run
- **Current implementation**: `rule_set` has a unique `(workspace_id, effective_from)` (enforced by two separate migrations, one an `IF NOT EXISTS`-guarded duplicate — `migrations/versions/a1b2c3d4e5f7_add_unique_rule_set_workspace_effective.py:20-30`). `auto_publish` (`backend/application/rule_set_service.py:51-144`) raises `RuleSetLockedError` (lines 97-102) if a `rule_set` for the target date is already referenced by a `payroll_run`, rather than mutating it.
- **Intended design**: Matches documented intent (`rule_set.py` docstring: "Rows are never updated after creation").
- **Identified gap**: None.
- **Evidence**: `backend/infra/db/models/rule_set.py:8-26`; `backend/infra/db/models/rule_set_item.py:6-17`; `backend/application/rule_set_service.py:51-144`
- **Severity**: Informational
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster A

#### F-01-12: `workspace_payroll_config` enum-like fields are validated by a Python allowlist duplicated from (not derived from) a DB CHECK constraint
- **Current implementation**: `backend/api/routes/onboarding.py:31-34` hardcodes Python frozensets (e.g. `_WPC_PH_MODE_VALUES = {"AUTOMATIC","FILE_BASED"}`) with an explicit comment "must match DB check constraints."
- **Intended design**: Undocumented whether single-sourcing was ever planned; the comment itself acknowledges the duplication.
- **Identified gap**: Two independent places (Python allowlist, DB CHECK) must be kept in sync manually for each of `ph_mode`, `saturday_ph_rule`, `sunday_ph_rule`, `d3_leave_overlap_rule`, `d4_absence_rule`. This stage did not verify whether the DB CHECK and Python set are currently in sync (that would require reading the specific migration for `workspace_payroll_config`'s CHECK constraints, which was not captured by Cluster A) — flagged as a fact about the pattern, not a confirmed divergence.
- **Evidence**: `backend/infra/db/models/workspace_payroll_config.py:7-21`; `backend/api/routes/onboarding.py:31-34`
- **Severity**: Not rated — divergence itself unverified; the dual-source-of-truth pattern is confirmed
- **Status**: confirmed (pattern); divergence unconfirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster A

---

### Area 6 — Employee registration

#### F-01-13: Upload (`createEmployee`) and Enroll (`enrollEmployee`/`bulkEnrollEmployees`) are two distinct, separately-gated operations by design
- **Current implementation**: `POST /{workspace_id}/employees` (`backend/api/routes/workspace.py:260-429`) accepts optional `salary_definition_code`/`grade_code`/`designation_code` — an employee can be created unenrolled (`salary_definition_id = NULL` on the paired `employee_contract` row). `POST /{workspace_id}/employees/{employee_id}/enroll` and `/bulk-enroll` (`workspace.py:438-578`) require `salary_definition_code` and reject employees who already have an active contract with `salary_definition_id IS NOT NULL`. `imported_grade_label`/`imported_designation_label` columns store raw Excel text from Upload for reference during Enroll, without auto-resolving them (`migrations/versions/ab1c2d3e4f50_...py:6-8`).
- **Intended design**: Matches documented project rule (`CLAUDE.md` "Upload / Enroll Separation, Sprint 22") and migration comments (`e7f8a9b0c1d2_...py:1-5`: "Employees can now be registered without a salary definition (not-enrolled state)") — re-verified directly against `workspace.py` and `employee_repo.py` rather than accepted from `CLAUDE.md` alone.
- **Identified gap**: None — implementation matches documented intent.
- **Evidence**: `backend/api/routes/workspace.py:260-578`; `backend/infra/repositories/employee_repo.py:261-378`; `migrations/versions/e7f8a9b0c1d2_allow_null_salary_definition_on_contract.py:1-5`; `migrations/versions/ab1c2d3e4f50_add_imported_labels_to_employee_contract.py:6-8`
- **Severity**: Informational
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster B

#### F-01-14: Employee eligibility for a payroll run is an inner-join filter with no explicit error for excluded employees; `employee.status` has no DB CHECK constraint
- **Current implementation**: `backend/api/routes/payroll.py:142-161` selects eligible employees via `INNER JOIN employee_contract` and `INNER JOIN salary_definition`, filtered on `e.status = 'ACTIVE'`. Employees that are `INACTIVE` or unenrolled (`salary_definition_id IS NULL`) are silently excluded from this query — no per-employee error surfaces at this point; only a workspace-wide `400 "No active employees found"` if the result set is empty. `_VALID_STATUSES = {"ACTIVE", "INACTIVE"}` (`backend/api/routes/employees.py:32`) is enforced only in the PATCH route's Python validation — there is no DB CHECK constraint on `employee.status` (confirmed absent from the column's migration, `6c2ecc683076_add_employee_number_and_status_fields.py:23-36`, which defines it as a plain `VARCHAR(20)`).
- **Intended design**: This matches documented project intent (`CLAUDE.md` Known Data Contract Rules: "`employee.status = 'INACTIVE'` + live contract... is intentional — payroll ineligibility is a consequence of INACTIVE status, not a data error... Do NOT add a hard PATCH guard") — re-verified against `payroll.py` and `employees.py` rather than accepted from `CLAUDE.md` alone.
- **Identified gap**: None against documented intent for the INACTIVE case. The absence of a DB CHECK constraint on `status` (enforcement is Python-only) is a factual gap between "the only two values ever written are ACTIVE/INACTIVE" and "the database itself permits any string."
- **Evidence**: `backend/api/routes/payroll.py:142-161,215-217`; `backend/api/routes/employees.py:32,131-156`; `migrations/versions/6c2ecc683076_add_employee_number_and_status_fields.py:23-36`
- **Severity**: Low — Python-only enum enforcement; no observed path in this stage that writes an invalid status value, but nothing at the DB layer prevents it.
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster B

---

### Area 7 — Employment / contract setup

#### F-01-15: `employee_contract` has no `workspace_id`; scoping is entirely join-through-`employee`; non-overlap is enforced by a GiST exclusion constraint
- **Current implementation**: Confirmed absent from every migration touching `employee_contract`. Workspace scoping in all write/read functions (`update_employee_contract`, `bulk_enroll_employee_contracts`, etc.) is via `JOIN employee e ON ... AND e.workspace_id = :wid`. A GiST exclusion constraint (`migrations/versions/d8e9f0a1b2c3_employee_contract_no_overlap.py:17-29`) prevents overlapping `[start_date, end_date)` ranges per employee; a partial unique index (`uq_employee_active_contract ... WHERE end_date IS NULL`) enforces at most one open contract per employee.
- **Intended design**: Matches prior documented understanding (memory: `feedback_employee_contract_workspace_scope.md`) — re-verified directly against `employee_repo.py` rather than accepted from memory alone, per the evidence standard's re-verification rule.
- **Identified gap**: None against documented intent — every function checked in this stage correctly joins through `employee.workspace_id`. This stage did not exhaustively check every call site across the codebase for this pattern; only the functions explicitly investigated are confirmed compliant.
- **Evidence**: `backend/infra/repositories/employee_repo.py:415-418,293-378`; `migrations/versions/d8e9f0a1b2c3_employee_contract_no_overlap.py:17-29`; `migrations/versions/6f5b05ff4690_add_final_phase1_integrity_constraints.py:62-66`
- **Severity**: Informational
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster B

#### F-01-16: `employee_contract.shift_type` is nullable at the DB layer but is handled with two different, contradictory defaults across two code paths
- **Current implementation**: DB CHECK constraint (`f1e2d3c4b5a6_add_employee_contract_shift_fields.py:46-53`) allows NULL. The direct payroll-run OT derivation path treats NULL as `'DAY'` by default (`backend/api/routes/payroll.py:202` inline comment: "NULL is treated as 'DAY' by the ot_multiplier handler gate"). The timesheet upload/derivation pipeline (`backend/application/timesheet_derivation_service.py:230-237,373-380`) instead hard-rejects rows/entries when `shift_type is None`, with an explicit error message instructing the operator to update the employee record.
- **Intended design**: Undocumented as a single unified rule — the payroll-run path's "NULL = DAY" comment and the timesheet path's "NULL is a hard failure" behavior are two different design choices for the same field, both present in current code.
- **Identified gap**: A NULL `shift_type` is silently defaulted to DAY in one execution path and explicitly rejected in another. This is recorded as a current-implementation fact; whether this divergence is intentional (e.g. timesheet-driven workspaces are expected to always set shift_type) is not established by this stage's evidence.
- **Evidence**: `migrations/versions/f1e2d3c4b5a6_add_employee_contract_shift_fields.py:20-53`; `backend/api/routes/payroll.py:202`; `backend/application/timesheet_derivation_service.py:230-237,373-380`
- **Severity**: Medium — a NULL value produces different calculation behavior depending on which entry path populated the input, which is a correctness-relevant divergence, though this stage did not test whether both paths can apply to the same employee/period in practice.
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster B

---

### Area 8 — Timesheet and payroll-input collection

#### F-01-17: `payroll_input` has DB-enforced category and non-negativity constraints; bulk upload treats duplicate/unique-violation rows as skipped rather than failing the batch
- **Current implementation**: `CHECK (input_category IN ('EARNING','DEDUCTION','STANDARD','PAYE_ONLY'))` (`ck_payroll_input_category`) and `CHECK (quantity >= 0)` (`ck_payroll_input_quantity_non_negative`), both with pre-migration data checks that would abort the migration if violated. `POST /{workspace_id}/payroll/inputs/bulk` (`backend/api/routes/payroll_input.py:247-390`) validates quantity/input_code/employee per row in Python (redundant with the DB CHECKs) and converts a `UniqueViolation` on the partial unique index `uq_payroll_input_unclaimed` into a `skipped_detail` entry rather than failing the whole request.
- **Intended design**: Matches documented project rule (`CLAUDE.md`: "Keep DB constraint hard failures; never silently dedup or mask input data errors" — memory: `feedback_constraint_violations.md`) for the negative-quantity/category cases (those remain hard DB failures). The skip-on-duplicate behavior specifically for the unclaimed-uniqueness constraint is a distinct, narrower behavior not covered by that rule (that rule is about masking *data errors*, not about the unclaimed-uniqueness partial index, which represents "this input already exists as an unclaimed row" rather than an error in the submitted data itself).
- **Identified gap**: None against the specific documented rule — negative quantities and bad categories still hard-fail; only the narrower "already-unclaimed" duplicate case is skip-not-fail, which is a different constraint serving a different purpose.
- **Evidence**: `migrations/versions/d6e7f8a9b0c1_add_input_category_constraint.py:20,40-49`; `migrations/versions/f8a9b0c1d2e3_add_payroll_input_non_negative_check.py:31-39`; `migrations/versions/ee5ff6aa7bb8_add_source_to_uq_payroll_input_unclaimed.py:20-24`; `backend/api/routes/payroll_input.py:247-390`
- **Severity**: Informational
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster B

#### F-01-18: Timesheet approval requires all entries `DERIVED` for the period; approval deletes and re-inserts prior unclaimed `TIMESHEET`-source inputs
- **Current implementation**: `approve_period()` (`backend/application/timesheet_derivation_service.py:481-546`) proceeds only if all entries for the period are `DERIVED` (lines 492-503), deletes prior unclaimed `TIMESHEET`-source rows for the employee/period (`delete_unclaimed_timesheet_inputs`), then inserts new ones only where `quantity > 0`, all inside one commit.
- **Intended design**: Undocumented outside the code itself; no contradicting spec found.
- **Identified gap**: None identified against a documented intent.
- **Evidence**: `backend/application/timesheet_derivation_service.py:481-546`; `backend/infra/repositories/payroll_input_repo.py:316-390`
- **Severity**: Informational
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster B

---

### Area 9 — Input validation and resolution

#### F-01-19: Salary-definition readiness is validated only in application code (Python), not by the DB-level readiness trigger, which produces an inconsistent enforcement boundary
- **Current implementation**: `validate_payroll_run_ready()` (`backend/application/payroll_readiness_service.py:34-215`) checks per-employee salary definition presence, component completeness, and (if `timesheet_enabled`) `derivation_status = APPROVED` for all employees. Separately, a DB trigger `enforce_payroll_readiness()` (`migrations/versions/4907cf6eb08f_enforce_payroll_readiness_db.py`, function body in `585ee430c647_upgrade_validate_payroll_readiness_.py:22-114`) fires `BEFORE INSERT ON payroll_run` and checks workspace `LIVE` status, ≥1 `statutory_rule`, ≥1 `tax_band`, active `component_metadata` for the country — but does **not** check per-employee `salary_definition` presence.
- **Intended design**: Undocumented whether the DB trigger was meant to be a full mirror of the Python check or intentionally a narrower workspace-level backstop.
- **Identified gap**: A `payroll_run` could theoretically be inserted directly (bypassing the Python `payroll_readiness_service` call) and pass the DB trigger despite employees lacking a salary definition — the DB layer is not a complete backstop for this specific check, unlike the workspace-LIVE/statutory-rule/tax-band checks which it does enforce.
- **Evidence**: `backend/application/payroll_readiness_service.py:34-215`; `migrations/versions/4907cf6eb08f_enforce_payroll_readiness_db.py:22-54`; `migrations/versions/585ee430c647_upgrade_validate_payroll_readiness_.py:22-114`
- **Severity**: Medium — a DB-level gap in an otherwise DB-enforced readiness gate, for a check whose Python-side violation (missing salary_definition) is elsewhere handled by silent INNER JOIN exclusion (F-01-14/F-01-20) rather than a hard error.
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster B

#### F-01-20: Execution-time query silently drops unenrolled employees; the pre-run readiness check raises an explicit error for the same condition — two different behaviors for the same input state
- **Current implementation**: `payroll_readiness_service.py:158-163` raises an explicit error ("Employee '...' is missing a salary definition") if invoked as a pre-check. But the actual run-execution employee-selection query (`backend/api/routes/payroll.py:142-161`) uses an inner `JOIN salary_definition`, which silently excludes unenrolled employees rather than erroring.
- **Intended design**: Undocumented whether the pre-check is mandatory-and-always-invoked before every run, in which case the execution-query behavior would never be reached for this condition, or whether runs can bypass the pre-check.
- **Identified gap**: If the readiness pre-check is skipped or bypassed for any run-creation path, an unenrolled employee would be silently excluded from the run with no error, rather than surfaced as in the pre-check. This stage did not trace every run-creation call site to confirm the pre-check is unconditionally invoked before every execution — flagged for Stage 08/10.
- **Evidence**: `backend/application/payroll_readiness_service.py:131-163`; `backend/api/routes/payroll.py:142-161`
- **Severity**: Medium — potential silent-exclusion path pending confirmation of whether the pre-check is unconditionally invoked.
- **Status**: confirmed (as a fact about two differing behaviors); the "is the pre-check always invoked" question is explicitly unresolved, not assumed either way
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster B

---

### Area 10 — Payroll-run creation

#### F-01-21: `run_type` has no DB CHECK constraint — it is enforced only by an API-layer allowlist
- **Current implementation**: `payroll_run.run_type` is `TEXT NOT NULL DEFAULT 'REGULAR'` (`migrations/versions/a8b9c0d1e2f3_add_rule_set_tables_temporal_rules.py:87-93`) with no CHECK constraint. `_VALID_RUN_TYPES = {"REGULAR", "ADJUSTMENT", "CORRECTION"}` (`backend/api/routes/payroll.py:65,72-77`) is the only enforcement, in the route handler.
- **Intended design**: Matches documented project rule (`CLAUDE.md`: "No DB CHECK constraint — API allowlist is the only enforcement. Do not add new values without a matching API allowlist update") — re-verified directly against the migration and route rather than accepted from `CLAUDE.md` alone.
- **Identified gap**: Any INSERT bypassing this specific route (a script, a future endpoint, direct SQL) is not constrained by the database to the three allowed values.
- **Evidence**: `migrations/versions/a8b9c0d1e2f3_add_rule_set_tables_temporal_rules.py:87-105`; `backend/api/routes/payroll.py:65,72-77`
- **Severity**: Low — matches a documented, accepted tradeoff; no observed second write path to `run_type` in this stage's evidence.
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster C

#### F-01-22: `payroll_run.status` transitions are enforced by a rank-based DB trigger; an earlier trigger generation referenced statuses the application never writes
- **Current implementation**: Current trigger `validate_payroll_status_transition()` (`migrations/versions/f1a2b3c4d5e6_enforce_payroll_run_status_transitions.py:92-159`) uses a rank table (`DRAFT=1 ... PAID=7`) to reject backward/unknown transitions; a companion `BEFORE INSERT` trigger forces new rows to `DRAFT`. This replaced an earlier trigger (`9901bc4ed0c5_enforce_payroll_run_state_machine.py`) that referenced now-nonexistent statuses (`PROCESSING/COMPLETED/FAILED/CANCELLED`), described in the replacing migration's own docstring as having become a "silent no-op."
- **Intended design**: The replacement migration itself documents the fix and its rationale — this is the current, intended enforcement mechanism.
- **Identified gap**: None against current intent — the replacement is complete and in place. Recorded because the surviving comment "silent no-op" is itself evidence that a DB-level guard existed for some period without actually enforcing anything, which is relevant history for Stage 06 (Compliance & Controls) to be aware of.
- **Evidence**: `migrations/versions/f1a2b3c4d5e6_enforce_payroll_run_status_transitions.py:92-213`; `migrations/versions/9901bc4ed0c5_enforce_payroll_run_state_machine.py` (docstring reference in replacing migration)
- **Severity**: Informational (current state); the historical no-op period is not re-assessed for severity here as it is superseded
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster C

#### F-01-23: Run creation is asynchronous — the HTTP response returns after DRAFT-row insert, before calculation begins
- **Current implementation**: `POST /payroll/run` inserts a `DRAFT` row (`create_draft_payroll_run`, hardcoded `status='DRAFT'`) then hands off to `background_tasks.add_task(_calculate_and_persist, ...)` (`backend/api/routes/payroll.py:852-877`) — the response is returned before calculation executes.
- **Intended design**: Undocumented as an explicit architectural decision in-repo; this stage did not find a spec describing the async/background-task choice.
- **Identified gap**: None identified against a stated intent (none was found to compare against); noted here as a structural fact relevant to Stage 09 (Human Experience — operator must poll for run completion, confirmed separately in `RunPayroll.tsx`'s polling loop) and Stage 08.
- **Evidence**: `backend/api/routes/payroll.py:826-877`; `backend/infra/repositories/payroll_run_repo.py:29-91`
- **Severity**: Informational
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster C / Cluster E

---

### Area 11 — Calculation execution

#### F-01-24: Sequential vs. legacy executor selection is a simple truthiness check on `component_metadata`; both call sites always supply it, but the legacy branch remains live code with a monitoring endpoint
- **Current implementation**: `execute_single_employee_payroll()` (`backend/domain/payroll/executor.py:108-132`) branches purely on `if component_metadata:` — no feature flag. Both production call sites (normal run route, retry path) always populate `component_metadata` (from the live table or from `component_metadata_snapshot` respectively). A dedicated monitoring endpoint `GET /{workspace_id}/payroll/ops/legacy-executor-stats` exists specifically to track how often the legacy path fires.
- **Intended design**: Matches documented project rule (`CLAUDE.md`: "Legacy executor ... used when `component_metadata` is None ... Logs a deprecation warning. Migrate all callers") — re-verified directly against `executor.py` rather than accepted from `CLAUDE.md` alone.
- **Identified gap**: The legacy branch is still reachable code (not removed), and a monitoring endpoint exists to track its usage — consistent with "migrate all callers" being an in-progress, not yet fully completed, intent.
- **Evidence**: `backend/domain/payroll/executor.py:108-132`; `backend/api/routes/payroll.py:411-429,1316-1331`; `backend/domain/payroll/batch_processor.py:15,124-140`
- **Severity**: Informational
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster C

#### F-01-25: Rule execution priority is DB-data-driven (a plain nullable Integer column), with a fixed synthetic priority for rule-injected components
- **Current implementation**: `component_metadata.execution_priority` sorts components ascending in `run_sequential_payroll()` (`sequential_executor.py:615-662`). Rule-injected components (from `apply_payroll_rules`) receive a fixed synthetic priority of 50 via the `RULE_COMPONENT_PRIORITY` constant, placing them before `sum_earnings` (priority 100). `PAYE_ONLY_ADDITIONS` (priority 95) and `CHECK_OFF_DUES` (priority 450) were each seeded by dedicated migrations with in-migration comments explaining their placement relative to neighboring priorities.
- **Intended design**: Matches documented project rule (`CLAUDE.md`: "Only reads by `_handle_taxable_income`... priority chain (CHECK_OFF_DUES=450)") — re-verified directly against `sequential_executor.py` and the two seeding migrations.
- **Identified gap**: None identified against documented intent.
- **Evidence**: `backend/domain/payroll/sequential_executor.py:10-27,177,223-256,615-662`; `migrations/versions/c5d6e7f8a9b0_add_non_taxable_component_class.py:68-100`; `migrations/versions/3c4d5e6f7a8b_seed_check_off_dues.py:7,38`; `migrations/versions/e1f2a3b4c5d6_sequential_component_execution_prep.py:27`
- **Severity**: Informational
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster C

---

### Area 12 — Snapshot creation and use

#### F-01-26: Three snapshot tables + a snapshot JSONB column capture run-start state; snapshot writes are one atomic commit with `ON CONFLICT DO NOTHING` idempotency
- **Current implementation**: `employee_contract_snapshot`, `component_metadata_snapshot`, `client_component_metadata_snapshot`, and `payroll_result.salary_inputs_snapshot` are all created together (`migrations/versions/b5c6d7e8f9a0_sprint19_snapshot_tables.py:33-103`). `create_payroll_snapshot()` (`backend/application/snapshot_service.py:35-140`) writes all three snapshot-table inserts under a single `raw_conn.commit()` — any failure propagates and leaves the DRAFT run with no snapshot rows, which then blocks any retry attempt via `validate_snapshot_complete()`.
- **Intended design**: Matches the in-code documented intent (module comments D1/D3 in `snapshot_service.py`).
- **Identified gap**: None against documented intent.
- **Evidence**: `migrations/versions/b5c6d7e8f9a0_sprint19_snapshot_tables.py:33-103`; `backend/application/snapshot_service.py:35-183`
- **Severity**: Informational
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster C

#### F-01-27: `salary_definition` edit-lock exists only for PAID runs — no lock exists for runs still in progress (DRAFT through LOCKED)
- **Current implementation**: `prevent_salary_definition_change_if_used()` trigger (`migrations/versions/f45614d5aa92_lock_salary_definition_when_paid.py:20-65`) blocks UPDATE/DELETE on `salary_definition` only when a `payroll_run` with `status = 'PAID'` references it through `employee_contract`/`payroll_result`. No trigger or constraint found (in the migrations directory searched) blocks editing `salary_definition` while a run referencing it is `DRAFT`/`CALCULATING`/`CALCULATED`/`APPROVED`/`LOCKED`. The only in-progress-relevant immutability found is on `payroll_run.rules_context_snapshot` itself (a different column, locked immediately after INSERT by `trg_run_snapshot_immutable`).
- **Intended design**: Prior documented understanding (memory: `feedback_salary_def_live_read.md`, `project_d_arch1_inner_join_gap.md`) describes "D-ARCH-1 edit-lock required before any PATCH" as a design requirement identified in a prior architecture review (Track J). This stage's direct code read confirms the *salary_definition* PAID-only lock exists, but found no equivalent lock for the in-progress window — meaning if D-ARCH-1's intent was a full in-progress edit-lock on `salary_definition`, that lock (as distinct from the `payroll_run` employee-based check found at `workspace.py:1529-1541`, which is a *different* table's edit-lock — see F-01-30) does not appear to extend to `salary_definition` itself for non-PAID in-progress runs.
- **Identified gap**: `salary_definition.components_jsonb` can, per this stage's evidence, be edited while a run that will read it live is DRAFT/CALCULATING/CALCULATED/APPROVED/LOCKED (not yet PAID) — the only DB-level lock fires at PAID. Whether the D-ARCH-1 lock found at `workspace.py:1529-1541` (which is on write access to `salary_definition` via `patch_salary_definition`, not a DB trigger) already closes this gap at the application layer is addressed in F-01-38 below.
- **Evidence**: `migrations/versions/f45614d5aa92_lock_salary_definition_when_paid.py:20-65`; `migrations/versions/a1b2c3d4e5f6_lock_payroll_run_snapshot.py:27-48`
- **Severity**: Not rated standalone — see F-01-38, which addresses whether the application-layer check closes this gap.
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster C

#### F-01-28: `component_trace_jsonb` is retained end-to-end in the production (sequential) path; the legacy path explicitly nulls it and does not evaluate workspace payroll rules at all
- **Current implementation**: In the sequential path, `_rule_trace` from `apply_payroll_rules` is merged into `full_context["_supplemental_traces"]` and flows into the persisted `component_trace_jsonb`. In the legacy path (`executor.py:116-132`), `build_payroll_result()` never calls `apply_payroll_rules` at all (only `calculate_gross()`/`calculate_net_pay()`), and the code explicitly sets `payroll_result["component_trace_jsonb"] = None`, accompanied by a warning log.
- **Intended design**: Matches documented project rule (`CLAUDE.md`: "Legacy executor ... Does NOT produce `component_trace_jsonb`") — re-verified directly, with the additional confirmed detail that the legacy path also skips rule evaluation entirely (workspace payroll rules — absences, overtime, check-off dues — are not applied), which is a stronger statement than "no trace" alone.
- **Identified gap**: None against documented intent for the trace-nulling behavior. The additional confirmed fact — that the legacy path silently skips all workspace payroll rule evaluation, not just trace capture — is recorded here because it was not explicit in the prior documented rule and was newly confirmed by direct code read in this stage.
- **Evidence**: `backend/domain/payroll/executor.py:108-132,150-370`; `backend/domain/payroll/result_builder.py:19-73`; `backend/domain/payroll/sequential_executor.py` (trace merge logic, cited via executor.py:227,253-254,369)
- **Severity**: High — if the legacy path is ever invoked in production (its live-callers currently always supply `component_metadata`, per F-01-24, so it is not observed to fire), it would silently omit all rule-based earnings/deductions (overtime, check-off dues, etc.), not merely omit the trace.
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster C

---

### Area 13 — Execution tracing

#### F-01-29: `component_trace_jsonb` persistence has two code paths (bulk and single-row) with different fallback precedence for the trace source
- **Current implementation**: Bulk path (`save_payroll_results_bulk`, `backend/infra/repositories/payroll_result_repo.py:37-115`) takes `component_trace_jsonb` directly from the result dict. Single-row path (`save_payroll_result`, same file, lines 118-211) prefers the trace from the `payroll_result` dict but falls back to a caller-supplied `component_trace` argument if the dict's value is absent (lines 152-154, "caller-supplied trace is a fallback").
- **Intended design**: Undocumented as an explicit single-source rule; both paths are live and used by different callers (bulk run execution vs. single-employee retry, per F-01 Area 14 evidence).
- **Identified gap**: Two different resolution-precedence rules for the same logical field, depending on which repo function a caller uses. This stage did not trace every caller of `save_payroll_result` to confirm whether the fallback branch is ever actually exercised in a live path (i.e., whether `payroll_result.get("component_trace_jsonb")` is ever actually absent when this function is called) — flagged for Stage 08.
- **Evidence**: `backend/infra/repositories/payroll_result_repo.py:37-211`
- **Severity**: Low — a latent inconsistency between two code paths; unconfirmed whether it is ever actually triggered.
- **Status**: confirmed (existence of the two differing code paths); the "is the fallback branch live" question is explicitly unresolved
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster C

---

### Area 14 — Retry and partial-failure handling

#### F-01-30: There is no `payroll_retry_request` table — retry is modeled as a column (`payroll_run.retry_strategy`) that has moved tables twice across migrations, and `FULL_RUN` is now DB-disabled
- **Current implementation**: No table of that name exists anywhere in the codebase (grep confirmed empty). `retry_strategy` originated on `workspace` (`423da33ffbd0_...py`), was moved to `payroll_run` (`f6a7b8c9d0e1_move_retry_strategy_to_payroll_run.py`), and was most recently restricted by `f7a1b2c3d4e5_retire_full_run_retry_strategy.py:17-28`, which drops and recreates the CHECK constraint as `CHECK (retry_strategy IN ('PER_EMPLOYEE'))` — i.e. `FULL_RUN` is no longer a legal value at the DB layer at all (not merely disabled in application code). This is mirrored by an application-layer allowlist (`_VALID_RETRY_STRATEGIES = {"PER_EMPLOYEE"}`, `backend/api/routes/payroll.py:79-84`) and a stub function that unconditionally raises for `FULL_RUN` (`payroll_retry_service.py:494-498`).
- **Intended design**: Matches documented project rule (`CLAUDE.md`: "Allowed values: PER_EMPLOYEE only. FULL_RUN is disabled by migration. API allowlist must match the migration-disabled set") — re-verified directly, with the corrected detail that the memory-recorded concept "`payroll_retry_request` table" does not exist as a table; retry state lives on `payroll_run` itself.
- **Identified gap**: A previously-recorded memory (`feedback_retry_strategy_architecture.md`) refers to `retry_strategy` as "per-run (payroll_run), never on Workspace" — this stage's evidence confirms that statement is accurate for the *current* schema, but the schema's own history shows it was in fact on `workspace` at an earlier point and was moved — recorded here as a clarification of prior memory against current+historical evidence, not a contradiction of the memory's current-state claim.
- **Evidence**: `migrations/versions/423da33ffbd0_retry_strategy_and_payroll_readines.py:26-40`; `migrations/versions/f6a7b8c9d0e1_move_retry_strategy_to_payroll_run.py:35-49,136-161`; `migrations/versions/f7a1b2c3d4e5_retire_full_run_retry_strategy.py:17-28`; `backend/api/routes/payroll.py:79-84`; `backend/application/payroll_retry_service.py:494-498`
- **Severity**: Informational
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster D

#### F-01-31: The frontend still presents `FULL_RUN` as a selectable retry-strategy option despite it being rejected by both the API and the DB
- **Current implementation**: `RunPayroll.tsx` (per Cluster E evidence) presents both `PER_EMPLOYEE` (labeled "recommended") and `FULL_RUN` as radio options. `_VALID_RETRY_STRATEGIES` on the backend rejects anything but `PER_EMPLOYEE` with a 422; the DB CHECK constraint also only permits `PER_EMPLOYEE`.
- **Intended design**: Undocumented whether the frontend option was meant to be removed at the same time as the backend restriction (`f7a1b2c3d4e5_retire_full_run_retry_strategy.py`).
- **Identified gap**: An operator selecting `FULL_RUN` in the UI would submit a request that the backend rejects — a UI/backend contract mismatch, confirmed by cross-referencing Cluster D's backend evidence against Cluster E's frontend evidence.
- **Evidence**: `backend/api/routes/payroll.py:79-84`; `migrations/versions/f7a1b2c3d4e5_retire_full_run_retry_strategy.py:17-28`; `frontend/src/pages/RunPayroll.tsx` (line 233-241 per Cluster E report)
- **Severity**: Medium — operator-facing dead-end that produces a rejected request rather than a data-integrity issue, but is a confirmed current-state UI/backend mismatch.
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster D / Cluster E (cross-referenced)

#### F-01-32: Retry uses delete-then-insert (never UPDATE) against `payroll_result`, driven by an immutability trigger on the snapshot column
- **Current implementation**: `retry_failed_payroll_employees()` (`backend/application/payroll_retry_service.py:505-819`) locks the run row `FOR UPDATE`, rejects retry for `PAID`/`APPROVED`/`LOCKED` runs, only re-processes `payroll_result` rows with `status='FAILED'`, and performs `DELETE ... WHERE status='FAILED'` followed by `INSERT` rather than `UPDATE`, because `trg_snapshot_immutable` blocks in-place update of `calculations_snapshot_json`.
- **Intended design**: Matches in-code documented rationale (comment in the same file explaining the trigger constraint).
- **Identified gap**: None against documented intent.
- **Evidence**: `backend/application/payroll_retry_service.py:396-487,505-819`
- **Severity**: Informational
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster D

---

### Area 15 — Reconciliation

#### F-01-33: `payroll_reconciliation` has no `workspace_id` column, and every repository function scopes solely by `payroll_run_id` — a confirmed workspace-scoping gap
- **Current implementation**: Confirmed absent from the table's creation migration (`migrations/versions/d1e2f3a4b5c6_add_payroll_reconciliation.py:50-76`) and the ORM model (`backend/infra/db/models/payroll_reconciliation.py:7-24`). `insert_reconciliation`, `update_reconciliation`, `get_reconciliation` (`backend/infra/repositories/reconciliation_repo.py:15-179`) filter only by `payroll_run_id`. Route handlers (`backend/api/routes/payroll.py:1207-1245`) take only `run_id` as a path parameter — no `workspace_id` check anywhere in this call chain.
- **Intended design**: Contradicts the global project rule (`CLAUDE.md`: "Workspace scoping enforced at the query level, not just the route") and a previously-recorded memory (`project_reconciliation_domain_rules.md`: "workspace scoping gap in repo") — this stage's direct read of `reconciliation_repo.py` and the table migration confirms the memory's claim rather than merely repeating it.
- **Identified gap**: Any caller with a valid `run_id` — regardless of which workspace it belongs to — can read or resolve that reconciliation record through these functions/routes, since nothing checks that the run belongs to the caller's workspace.
- **Evidence**: `migrations/versions/d1e2f3a4b5c6_add_payroll_reconciliation.py:50-76`; `backend/infra/db/models/payroll_reconciliation.py:7-24`; `backend/infra/repositories/reconciliation_repo.py:15-179`; `backend/api/routes/payroll.py:1207-1245`
- **Severity**: High — confirmed missing workspace-scoping on a financially-relevant record (reconciliation of actual vs. expected pay totals), directly contradicting a standing project rule.
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster D

#### F-01-34: `MATCHED`/`MISMATCH` totals-equality invariant is enforced by DB CHECK constraints; `RESOLVED` was introduced specifically to preserve that invariant rather than overload `MATCHED`
- **Current implementation**: `chk_matched_totals_equal` (`status <> 'MATCHED' OR actual_total = expected_total`) and `chk_mismatch_totals_differ` are both present from the original migration (`migrations/versions/d1e2f3a4b5c6_...py:50-76`) and retained unchanged after `RESOLVED` was added (`migrations/versions/f7a8b9c0d1e2_add_reconciliation_resolution_fields.py:22-44`), whose docstring explicitly states the reason: preserving "MATCHED → totals equal" by introducing a new status rather than reusing `MATCHED`.
- **Intended design**: Matches the documented project rule (`CLAUDE.md` Known Data Contract Rules, and the RC5 lesson referenced in the global `~/.claude/CLAUDE.md`) — re-verified directly against both migrations rather than accepted from `CLAUDE.md` alone.
- **Identified gap**: None — this is confirmed as correctly implemented, matching intent exactly.
- **Evidence**: `migrations/versions/d1e2f3a4b5c6_add_payroll_reconciliation.py:50-76`; `migrations/versions/f7a8b9c0d1e2_add_reconciliation_resolution_fields.py:7-9,22-44`
- **Severity**: Informational
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster D

#### F-01-35: `update_reconciliation`'s docstring says "Sets status to MATCHED" but the executed SQL sets `status = 'RESOLVED'`
- **Current implementation**: `backend/infra/repositories/reconciliation_repo.py:82-144` — docstring at lines 87-90 states the function "Sets status to MATCHED"; the actual SQL (lines 100-108) is `UPDATE payroll_reconciliation SET status='RESOLVED', ...`.
- **Intended design**: The docstring itself is the only stated intent, and it disagrees with the code it documents.
- **Identified gap**: Documentation/code mismatch within the same function — reported as a factual discrepancy in the source, not evaluated for impact (no caller was found in this stage's evidence that reads the docstring rather than the behavior, so no functional impact is claimed).
- **Evidence**: `backend/infra/repositories/reconciliation_repo.py:82-144`
- **Severity**: Low — documentation/code mismatch, no confirmed functional impact.
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster D

#### F-01-36: Reconciliation requires the run to be `LOCKED` — enforced in application code only, not by a DB constraint on `payroll_reconciliation`
- **Current implementation**: `reconcile_payroll_run()` (`backend/application/reconciliation_service.py:21-75`) reads `payroll_run.status` and raises `ValueError` if not `LOCKED` (lines 62-65). No DB-level constraint on `payroll_reconciliation` ties its existence/insertion to the parent run's status.
- **Intended design**: Matches documented project rule (`CLAUDE.md`: "LOCKED-only guard" — memory: `project_reconciliation_domain_rules.md`) — re-verified directly.
- **Identified gap**: The guard is application-layer only; a direct INSERT into `payroll_reconciliation` (bypassing the service function) would not be blocked by the database regardless of the parent run's status.
- **Evidence**: `backend/application/reconciliation_service.py:21-75,48-55`
- **Severity**: Low — consistent with the general pattern of DB CHECK constraints being reserved for column-value invariants rather than cross-table state guards in this codebase; no observed second write path bypassing the service.
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster D

---

### Area 16 — Approval, locking and payment-related states

#### F-01-37: `APPROVED` (not just `LOCKED`) already makes `payroll_result` immutable at the DB trigger level
- **Current implementation**: `prevent_payroll_result_mutation()` (`migrations/versions/e2f3a4b5c6d7_prevent_payroll_result_mutation.py:57-103`) blocks UPDATE/DELETE on `payroll_result` when the parent run's status is in `('CALCULATED', 'APPROVED', 'LOCKED', 'PAID')` — i.e., immutability begins at `CALCULATED`, one step before `APPROVED`, not only at `LOCKED` as the state name might suggest.
- **Intended design**: Matches documented project rule (`CLAUDE.md`: "`payroll_run.status = 'APPROVED'` | immutable — no employee results can be modified") — this stage's evidence confirms immutability actually begins even earlier, at `CALCULATED`, which is a stronger (not weaker) guarantee than the documented rule states, not a contradiction of it.
- **Identified gap**: None — the implementation is at least as strict as the documented rule.
- **Evidence**: `migrations/versions/e2f3a4b5c6d7_prevent_payroll_result_mutation.py:57-103`
- **Severity**: Informational
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster D

#### F-01-38: D-ARCH-1 salary_definition edit-lock check (application layer, `patch_salary_definition`) joins around `payroll_result` specifically to avoid a documented false-negative for SUBMITTED runs — but the status values it checks for include two that the application never writes
- **Current implementation**: `backend/api/routes/workspace.py:1529-1541` contains an explicit comment: joining `payroll_run → employee (workspace match) → employee_contract` specifically "to avoid joining through payroll_result, which has zero rows for SUBMITTED runs and bypasses the lock." The status list checked is `IN ('SUBMITTED','PROCESSING','CALCULATED','PARTIAL','APPROVED')`. Cross-referencing the actual `PayrollRunStatus` enum (`backend/domain/payroll/status.py:16-34`: `DRAFT, CALCULATING, CALCULATED, APPROVED, LOCKED, PARTIAL, PAID`) and the state machine (`backend/domain/payroll/state_machine.py:15-23`) confirms `'SUBMITTED'` and `'PROCESSING'` are never written by any Python transition code found in this stage.
- **Intended design**: The in-code comment states the intent clearly: avoid the payroll_result-join false negative for in-flight runs. This appears designed against an assumed status vocabulary that does not fully match the enum actually in use elsewhere in the same codebase.
- **Identified gap**: Two of the five statuses in this lock-check's allowlist (`SUBMITTED`, `PROCESSING`) do not correspond to any status the application-layer transition code currently writes to `payroll_run.status` — meaning those two branches of the guard are presently unreachable against current write paths, though this stage did not verify whether any other code path (e.g. a raw SQL script, a different service) ever writes those values. This is the same D-ARCH-1 mechanism referenced by prior memory (`project_d_arch1_inner_join_gap.md`), and this stage's direct read both confirms the fix (the payroll_result-avoidance join) is in place and surfaces this additional, previously-unrecorded status-vocabulary mismatch. This also resolves F-01-27's open question: this application-layer check does cover `CALCULATED`/`PARTIAL`/`APPROVED` in-progress states for `salary_definition` edits reached via `patch_salary_definition` specifically — but is scoped to that one route, not a DB-level guarantee, so any other write path to `salary_definition` (if one exists) would not be covered.
- **Evidence**: `backend/api/routes/workspace.py:1529-1541,1340-1350`; `backend/api/routes/employees.py:40-51,178-183`; `backend/domain/payroll/status.py:16-34`; `backend/domain/payroll/state_machine.py:15-23`
- **Severity**: Medium — dead/unreachable branches in a financially-relevant lock check are not themselves harmful, but indicate the guard's status vocabulary has drifted from the actual enum, raising the question (not resolved by this stage) of whether the guard still correctly covers every currently-reachable in-flight state it was meant to cover.
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster D

#### F-01-39: `LOCKED` is a distinct status between `APPROVED` and `PAID`, each transition individually guarded by row-level locking (`FOR UPDATE`) and the shared state machine
- **Current implementation**: `backend/domain/payroll/state_machine.py:15-23` — `APPROVED → [LOCKED]`, `LOCKED → [PAID]`. `payroll_approval_service.py`'s `approve_payroll_run`, `lock_payroll_run`, `mark_payroll_run_paid` each take a `SELECT ... FOR UPDATE` lock before checking/performing the transition.
- **Intended design**: Matches documented intent (docstring in `lock_payroll_run`: "A LOCKED run is immutable. No retry, recalculation, or result modification is permitted after this point.")
- **Identified gap**: None.
- **Evidence**: `backend/domain/payroll/state_machine.py:15-23`; `backend/application/payroll_approval_service.py:44-259`
- **Severity**: Informational
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster D

---

### Area 17 — Audit records

#### F-01-40: Audit trail (`audit_log`, `event_store`) captures only `payroll_run` status transitions — reconciliation and configuration edits are not written to either table
- **Current implementation**: `audit_log` and `event_store` were both created in the baseline migration (`5aa34350e00f_...py:106-126`). Confirmed call sites writing to them: run creation (`payroll_run_persister.py:98,104`), approve/lock/mark-paid transitions (`payroll_approval_service.py:91-102,164-175,239-250`), and the post-retry recompute (`payroll_retry_service.py:793-804`) — all hardcoded to `entity_type`/`aggregate_type = "PAYROLL_RUN"`. No `save_audit_log`/`save_event` calls were found in `reconciliation_service.py`, or in the employee/salary-definition/pay-cycle PATCH routes in `workspace.py`/`employees.py`.
- **Intended design**: Undocumented as an explicit scope decision — no spec found stating audit coverage was intended to be `payroll_run`-transitions-only versus broader.
- **Identified gap**: Reconciliation MATCHED/MISMATCH/RESOLVED transitions and configuration edits (salary definitions, pay cycle, contract changes) have no entry in `audit_log`/`event_store` — the only trail for those is each table's own `created_at`/`resolved_at` timestamp columns, which do not record *who* made the change or *what* the prior value was (`old_value_jsonb`/`new_value_jsonb` are `audit_log`-specific columns, not present on the other tables).
- **Evidence**: `migrations/versions/5aa34350e00f_phase1_baseline_schema.py:106-126`; `backend/infra/repositories/audit_log_repo.py:25-75`; `backend/domain/payroll/audit_events.py:16-67`; `backend/application/payroll_approval_service.py:91-102,164-175,239-250`; `backend/application/payroll_retry_service.py:793-804`; absence confirmed by grep of `reconciliation_service.py`, `workspace.py`, `employees.py` for `save_audit_log`/`save_event`
- **Severity**: Medium — a confirmed audit-coverage gap for reconciliation resolution and configuration edits, which are operator actions with financial/compliance relevance; Stage 06 (Compliance & Controls) should treat this as an input.
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster D

---

### Area 18 — Existing operator-facing UI flows

#### F-01-41: Operator-facing pages map to a coherent lifecycle (Bureau → Workspace setup → Employees → Run → Results), with several config pages (RateCodes, AttendanceConfiguration, PublicHolidays) as siblings rather than steps in that lifecycle
- **Current implementation**: `BureauDashboard.tsx` (workspace list + creation) → `WorkspaceDashboard.tsx` (state-flow CTA per onboarding status) → `WorkspaceSetup.tsx` (structural config, component toggles, validate/commit, and — for non-DRAFT workspaces — payroll-behaviour config and rate-code registry) → `Employees.tsx` (register/upload/enroll/edit/change-grade) → `RunPayroll.tsx`/`PayrollRuns.tsx` → `PayrollResults.tsx` (tabs: Results/Reconciliation/Timeline/Audit Log). `RateCodes.tsx`, `AttendanceConfiguration.tsx`, and `PublicHolidays.tsx` are separate top-level pages, not steps embedded in the onboarding wizard, despite `WorkspaceSetup.tsx`'s `ExistingConfigView` also surfacing rate-code management inline for post-onboarding workspaces.
- **Intended design**: Undocumented as a single formal IA spec; this stage reports what the routed pages let an operator do, per direct component reads (Cluster E).
- **Identified gap**: Rate-code management is reachable from two different places (the standalone `RateCodes.tsx` page and inline within `WorkspaceSetup.tsx`'s `ExistingConfigView`) — a confirmed duplication of entry point, not assessed further here (UI/IA assessment is Stage 09's remit).
- **Evidence**: `frontend/src/pages/BureauDashboard.tsx`, `WorkspaceDashboard.tsx`, `WorkspaceSetup.tsx`, `Employees.tsx`, `RunPayroll.tsx`, `PayrollRuns.tsx`, `PayrollResults.tsx`, `RateCodes.tsx`, `AttendanceConfiguration.tsx`, `PublicHolidays.tsx` (all per Cluster E citations)
- **Severity**: Not rated — IA/UX assessment is explicitly out of scope for Stage 01 (see `CONTEXT.md`); recorded as a factual observation for Stage 09 to pick up.
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster E

#### F-01-42: `Reconciliation.tsx` is a dead route — a pure redirect to a tab inside `PayrollResults.tsx`
- **Current implementation**: `frontend/src/pages/Reconciliation.tsx` (16 lines) is only a `<Navigate replace>` redirect, with an in-code comment stating it is "now a tab inside PayrollResults."
- **Intended design**: The comment itself documents the intended current state (reconciliation is meant to live inside `PayrollResults`, not as its own page) — this file is a compatibility redirect, not a live feature.
- **Identified gap**: None against stated intent — this is confirmed as intentional, already-migrated dead code left in place as a redirect shim.
- **Evidence**: `frontend/src/pages/Reconciliation.tsx` (per Cluster E citation)
- **Severity**: Informational
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster E

---

### Area 19 — Post-payroll investigation and correction

#### F-01-43: The designed correction mechanism for anything beyond per-employee retry is "open a new payroll run" (ADJUSTMENT/CORRECTION), not editing the existing run
- **Current implementation**: `PAID` runs are immutable by DB trigger. `APPROVED`/`LOCKED` runs reject retry (`payroll_retry_service.py:550-565`). The UI's own "Cannot retry this run" modal (`PayrollResults.tsx`, per Cluster E) states: "This run was created before the snapshot engine was enabled... To correct this period, open a new payroll run." `ADJUSTMENT` runs may supply an explicit `override_rule_set_id` to target a specific historical rule set.
- **Intended design**: This is stated directly in the product's own UI copy, which is being treated here as evidence of current operational design (not as a spec document) — it describes what the system currently tells the operator to do, which is itself a fact about current operation.
- **Identified gap**: `run_type = 'CORRECTION'` is accepted by the API but not exposed in the `RunPayroll.tsx` dropdown (which only offers `REGULAR`/`ADJUSTMENT`) — confirmed by cross-referencing Cluster C's backend allowlist evidence against Cluster E's frontend component read. An operator cannot currently select `CORRECTION` through the UI even though the backend supports it.
- **Evidence**: `backend/api/routes/payroll.py:65-76` (Cluster C); `frontend/src/pages/RunPayroll.tsx` lines 199-203 (Cluster E); `PayrollResults.tsx` line 1321-1325 (Cluster E)
- **Severity**: Medium — a supported backend capability (`CORRECTION` run type) has no UI path to invoke it, meaning operators can only reach it outside the normal UI (e.g., direct API call), which is a confirmed UI/backend capability gap.
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster C / Cluster E (cross-referenced)

#### F-01-44: The Results tab surfaces a specific "silent rate substitution" audit signal (`resolution_source === 'current_fallback'`) when historical rule-set resolution fails
- **Current implementation**: `PayrollResults.tsx`'s `renderTrace` shows an amber warning icon when a component's `resolution_source === 'current_fallback'`, per Cluster E's report — i.e., the engine fell back to the current rate rather than the historically-correct one, and this is visually flagged in the trace.
- **Intended design**: Matches an evident design intent to surface this specific failure mode to the operator, though the underlying condition that produces `current_fallback` was not traced back to its source code in this stage (that would require Stage 08 to confirm exactly which resolution path sets this value).
- **Identified gap**: None identified against the observed UI behavior; the underlying trigger condition for `current_fallback` is not yet traced to source — flagged for Stage 08.
- **Evidence**: `frontend/src/pages/PayrollResults.tsx` (`renderTrace`, per Cluster E citation, lines ~685-711)
- **Severity**: Not rated — this stage did not verify the producing code path; recorded as an operator-facing fact only.
- **Status**: confirmed (UI behavior only); underlying source mechanism unconfirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster E

---

### Area 20 — Statutory-rule maintenance

#### F-01-45: New statutory rates are added exclusively via Alembic migrations with raw SQL — no admin route or UI exists for creating/editing `statutory_rule`/`tax_band`
- **Current implementation**: Confirmed via grep across `backend/api/routes/` — only two read sites reference `statutory_rule`/`tax_band` (`payroll.py`, for run execution, and `workspace.py:57`, an onboarding existence check). `backend/api/routes/admin.py` serves only static Jinja2 dashboards with no statutory-rule endpoints. No frontend page references statutory rules or tax bands. Historical rate changes (e.g. NG PAYE bands corrected to NTA 2025, pension rate seeding) are each a dedicated migration performing raw `INSERT`/`UPDATE`/`DELETE` against `statutory_rule`/`tax_band`, guarded by the `(country_code, effective_from)` unique constraint (`ON CONFLICT DO NOTHING` idempotency in the seed migration).
- **Intended design**: Undocumented as an explicit "migration-only, forever" design decision — but consistently implemented this way across every statutory-rate-change migration found in this stage's evidence, with no counter-example.
- **Identified gap**: None against observed implementation; recorded as a factual operational constraint — any future statutory rate change requires a new migration and a deployment, not an operator-driven admin action.
- **Evidence**: `backend/infra/db/models/statutory_rule.py:7-23`; `migrations/versions/d4e5f6a7b8c9_add_unique_statutory_rule_country_effective.py`; `migrations/versions/e4f5a6b7c8d9_seed_ng_statutory_rule_paye_bands.py`; `migrations/versions/de1f2a3b4c5d_fix_ng_paye_bands_nta_2025.py`; `migrations/versions/c0d1e2f3a4b5_seed_pension_rates_in_statutory_rules.py`; `backend/api/routes/workspace.py:57`; `backend/api/routes/admin.py` (absence confirmed)
- **Severity**: Not rated — this stage does not assess whether migration-only maintenance is adequate (that judgment belongs to Stage 06/11); recorded as a confirmed operational fact.
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster E

#### F-01-46: PAYE tax bands live in a separate `tax_band` table, and a CHECK constraint explicitly forbids re-duplicating them inside `statutory_rule.rules_jsonb`; other statutory rates (pension/NHF/health/levy) remain unnormalized JSONB keys with silent Python-side defaults
- **Current implementation**: `tax_band` table FK's to `statutory_rule_id` (baseline migration). `chk_statutory_rule_no_tax_bands_in_jsonb` (`migrations/versions/2a3b4c5d6e7f_remove_tax_bands_from_statutory_rule_jsonb.py`) — `CHECK (NOT (rules_jsonb ? 'tax_bands'))`, with the migration's own docstring stating "The engine already reads from the tax_band table exclusively." Pension/NHF/health/development-levy/life-insurance/rent-relief rates remain inside `rules_jsonb` (not normalized into their own tables), read at runtime with Python-side fallback defaults, e.g. `Decimal(str(rules_jsonb.get("nhf", {}).get("employee_rate", "0.025")))` (`backend/api/routes/payroll.py:260-278`) — a silent default if the key is absent, not an error.
- **Intended design**: The migration itself documents the intended single-source-of-truth design for tax bands specifically; no equivalent stated intent was found for the other statutory rates remaining as JSONB keys with defaults.
- **Identified gap**: Tax bands are fully normalized and constrained against duplication. By contrast, no equivalent normalization or anti-duplication/anti-missing-key constraint was found for pension/NHF/health/development-levy rates.
- **Evidence**: `migrations/versions/2a3b4c5d6e7f_remove_tax_bands_from_statutory_rule_jsonb.py`; `backend/api/routes/payroll.py:260-278`
- **Severity**: Medium — a silent-default (rather than error) for missing statutory JSONB keys on financially-relevant rates (NHF, health insurance, development levy, life insurance) is a confirmed pattern; whether any workspace currently relies on the default rather than an explicit configured rate was not tested in this stage.
- **Status**: confirmed
- **Date**: 2026-07-11
- **Raised by**: Stage 01, Cluster E

---

## Parked / Rejected

_None — all leads investigated in this stage reached either a confirmed finding or an explicitly-marked open question within a confirmed finding (see F-01-07, F-01-09, F-01-12, F-01-20, F-01-29, F-01-44 for the specific unresolved sub-questions flagged for later stages)._

## Cross-references for later stages

- Stage 06 (Compliance & Controls) should treat F-01-33, F-01-40, F-01-46 as direct inputs.
- Stage 07 (Security & Identity) should treat F-01-33 (reconciliation workspace-scoping gap) as a direct input.
- Stage 08 (Technical Architecture) should resolve the open sub-questions in F-01-07, F-01-09, F-01-20, F-01-29, F-01-44.
- Stage 09 (Human Experience) should treat F-01-41 (duplicated rate-code entry point) and F-01-31 / F-01-43 (UI/backend capability mismatches) as direct inputs.
- Stage 10 (Evaluation & Assurance) should treat F-01-16 (shift_type default divergence) and F-01-38 (dead status branches in the D-ARCH-1 guard) as direct inputs.
