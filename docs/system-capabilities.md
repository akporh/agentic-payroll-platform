# System Capabilities Catalogue

A reference catalogue of non-negotiable system properties. Every entry is a contract the system must honour. Each feature's acceptance criteria must reference every SC code that applies to it.

**UI Status values** (for feature-level tracking):
- `not wired` — no UI entry point exists; operator cannot reach this without DB/API access
- `partial` — UI exists but does not cover all operator needs (discovery, configuration, or observability incomplete)
- `complete` — fully operator-accessible from the UI

---

## How to use this catalogue

- **Arch-council:** Any plan touching an `SC-GUA` or `SC-DAT` entry triggers a mandatory data contract review. Any plan touching `SC-ENG` triggers an executor path review.
- **Tester:** Verification for each sprint must confirm all referenced SC codes still pass.
- **Auditor:** `SC-AUD` entries form the minimum audit trail checklist before UAT sign-off.
- **Feature acceptance criteria:** Every story must list its applicable SC codes. If none apply, state "no SC constraints" explicitly (not silence).

---

## SC-GUA — Guarantees

What must always hold true regardless of code path, input, or operator action.

| Code | Name | Statement | Broken by | Verified by | AC tag |
|------|------|-----------|-----------|-------------|--------|
| SC-GUA-1 | Calculation snapshot immutability | `payroll_result.calculations_snapshot_json` can never be updated after INSERT | Any UPDATE path on `payroll_result` that touches this column; migration that drops the freeze trigger | Arch-council (data contract gate), DB trigger review, tester | Any feature that writes or reads `payroll_result` |
| SC-GUA-2 | Result immutability post-calculation | No `payroll_result` can be modified or deleted once parent `payroll_run` reaches CALCULATED, APPROVED, LOCKED, or PAID | Application-level UPDATE bypass; trigger removal; new status value inserted without immutability coverage | Arch-council, DB trigger review | Any feature that transitions run status or modifies results |
| SC-GUA-3 | Decimal precision on all monetary values | Every monetary amount uses `Decimal` with `ROUND_HALF_UP` to 2dp — never `float` | Introducing `float` arithmetic in any calculation path; JSON serialisation that casts Decimal to float | Code review, tester | Every feature that computes or stores a monetary value |
| SC-GUA-4 | MATCHED means totals are equal | `payroll_reconciliation.status = 'MATCHED'` if and only if `actual_total == expected_total` | Changing MATCHED logic to include operator-resolved mismatches; overloading the status value | Arch-council (data contract gate) | Any feature that writes or reads reconciliation status |
| SC-GUA-5 | APPROVED run is immutable | Once `payroll_run.status = 'APPROVED'`, no employee result can be modified | Any edit path on results that does not re-check run status; new bulk-edit feature without status guard | Arch-council, tester | Any feature that modifies payroll results or run state |
| SC-GUA-6 | Workspace scoping at query level | Every DB query is scoped to `workspace_id` at the repository layer, not only at the route layer | Querying without workspace filter; cross-workspace JOIN that leaks data; route-only scoping | Security review, arch-council | Every feature that reads or writes workspace-scoped data |

---

## SC-ENG — Engine

Core calculation logic and execution flow contracts.

| Code | Name | Statement | Broken by | Verified by | AC tag |
|------|------|-----------|-----------|-------------|--------|
| SC-ENG-1 | Canonical component execution order | Components execute in ascending `execution_priority` order — always | Changing sort order; adding a component without a defined priority; parallel execution without priority gate | Tester, code review | Any feature that adds a component type or modifies executor dispatch |
| SC-ENG-2 | Frozen period context | Working days, calendar days, and annualisation factor are computed once at run start and never mutated during execution | Mutable period context dataclass; recomputing working days mid-run | Code review, tester | Any feature that touches period date inputs or proration |
| SC-ENG-3 | PAYE on taxable income | PAYE is computed on taxable income after pension and configurable exclusions — never on gross | Adding an inclusion to PAYE base without updating `_handle_taxable_income`; changing priority chain so PAYE runs before deductions | Arch-council, tester | Any feature that modifies deduction handling or adds a new component class |
| SC-ENG-4 | Sequential executor is the production path | `sequential_executor.py` is the only executor that produces `component_trace_jsonb`; legacy executor path is deprecated | Routing new run types through legacy executor; calling executor without `component_metadata` | Code review, tester | Any feature that triggers a payroll run or adds a new run type |

---

## SC-DAT — Data Model

Storage, schema, and relationship invariants.

| Code | Name | Statement | Broken by | Verified by | AC tag |
|------|------|-----------|-----------|-------------|--------|
| SC-DAT-1 | One active pay cycle per workspace | At most one `pay_cycle` row per workspace can have `is_active = true` | Removing the partial unique index; INSERT without checking active state | Migration review, arch-council | Any feature that creates or modifies pay cycles |
| SC-DAT-2 | Statutory rule uniqueness | `(country_code, effective_from)` is UNIQUE on `statutory_rule` — no duplicate effective dates | Dropping or softening the unique constraint; bulk-insert without duplicate check | Migration review, arch-council | Any feature that creates or imports statutory rules |
| SC-DAT-3 | Run starts in DRAFT | Every new `payroll_run` row must have `status = 'DRAFT'` on INSERT | Removing the enforce-initial-status DB trigger; creating a run via raw INSERT with a later status | DB trigger review, tester | Any feature that initiates a payroll run |
| SC-DAT-4 | Forward-only state transitions | `payroll_run.status` can only advance — CALCULATED → DRAFT is rejected | Removing the state machine validation; adding a new status without defining its rank | Arch-council (data contract gate), DB trigger review | Any feature that transitions run status or adds a new status value |
| SC-DAT-5 | One result per (run, employee) | `uq_payroll_result_employee_run` enforces no duplicate results within a run | Dropping the unique index; INSERT path that bypasses conflict handling | Migration review, tester | Any feature that writes payroll results |

---

## SC-TMP — Temporal / Versioning

Time-based behaviour and rule version resolution.

| Code | Name | Statement | Broken by | Verified by | AC tag |
|------|------|-----------|-----------|-------------|--------|
| SC-TMP-1 | Statutory rule resolved by period, not today | Statutory rule is selected where `effective_from ≤ period_end`, not `≤ today` | Substituting `date.today()` for `period_end` in the rule lookup query | Arch-council, tester | Any feature that reads or applies statutory rules |
| SC-TMP-2 | Historical inputs use incurred-period rate | An input with `reference_date` in a past month is evaluated using the rule set effective for that month | Removing historical rule set prefetch; falling back to current rate without logging the gap | Tester, arch-council | Any feature that processes cross-period inputs |
| SC-TMP-3 | Rule set selected by latest effective date ≤ period end | The workspace rule set whose `effective_from` is the latest value still ≤ `period_end` is used — not the most recently created | Ordering by `created_at` instead of `effective_from`; inserting a rule set without an `effective_from` | Arch-council, tester | Any feature that creates rule sets or triggers a payroll run |

---

## SC-RET — Execution & Retry

Failure handling and reprocessing contracts.

| Code | Name | Statement | Broken by | Verified by | AC tag |
|------|------|-----------|-----------|-------------|--------|
| SC-RET-1 | Retry uses original statutory rule | Re-executing failed employees uses the same statutory rule as the original run — not the current live rule | Reading statutory rule from DB rather than from `statutory_effective_date` on the run | Tester | Any feature that triggers a retry |
| SC-RET-2 | Retry never re-queries live rule tables | Historical rate resolution in retry reads from the frozen snapshot — not live `rule_set` / `rule_set_item` tables | Introducing a live DB query in the retry path for historical rates | Code review, tester | Any feature that modifies the retry service |
| SC-RET-3 | Retry preserves original period context | `period_start`, `period_end`, working days, and annualisation factor in retry match the original run | Recomputing period context from the current date during retry | Tester | Any feature that modifies retry execution |
| SC-RET-4 | Retry on a clean run is a no-op | Calling retry when no FAILED results exist returns immediately without modifying data | Removing the early-exit guard; adding a side effect before the guard check | Tester | Any feature that calls or extends the retry path |

---

## SC-AUD — Audit & Traceability

Explainability, logging, and evidence requirements.

| Code | Name | Statement | Broken by | Verified by | AC tag |
|------|------|-----------|-----------|-------------|--------|
| SC-AUD-1 | Every run transition is audit logged | Every `payroll_run` status change produces an `audit_log` entry with actor, timestamp, old status, and new status | Removing the audit log INSERT from a transition path; adding a new transition without audit coverage | Auditor, tester | Any feature that transitions run status |
| SC-AUD-2 | Component trace populated for every sequential executor result | `payroll_result.component_trace_jsonb` is non-null for every result produced by the sequential executor | Introducing a code path in sequential executor that skips trace assembly; routing a run type to legacy executor | Tester, code review | Any feature that reads or displays payroll results |
| SC-AUD-3 | Full rule state frozen at run time | `payroll_run.rules_context_snapshot` (v2) captures statutory rule, tax bands, current rule set, and all historical rule sets used by that run | Removing fields from snapshot assembly; adding a new input type without including its rate source in the snapshot | Arch-council, tester | Any feature that modifies the snapshot builder or adds a new calculation input |

---

## SC-INT — Integration Boundaries

Service interaction and layering contracts.

| Code | Name | Statement | Broken by | Verified by | AC tag |
|------|------|-----------|-----------|-------------|--------|
| SC-INT-1 | Domain code never imports infrastructure | No file under `backend/domain/` imports from `backend/infra/` | Adding a repository call directly inside a domain function | Code review, arch-council | Any feature that adds domain logic |
| SC-INT-2 | Routes never contain business logic | No file under `backend/api/routes/` performs calculations or enforces business rules directly | Moving a calculation or state check from a service into a route handler | Code review, arch-council | Any feature that adds or modifies an API route |
| SC-INT-3 | Workspace scoping enforced at repository layer | Repository methods receive and apply `workspace_id` — routes must not be the only place it is applied | A repository method that accepts workspace_id as a parameter but does not include it in the WHERE clause | Security review, code review | Every feature that queries workspace-scoped data |

---

## SC-TST — Testing & Validation

How correctness is enforced and maintained.

| Code | Name | Statement | Broken by | Verified by | AC tag |
|------|------|-----------|-----------|-------------|--------|
| SC-TST-1 | Every migration has a working downgrade | Every `upgrade()` in `migrations/versions/` has a corresponding `downgrade()` that restores prior state | Writing a migration with a no-op or missing `downgrade()`; a downgrade that leaves orphaned columns or broken constraints | Migration review | Any feature that adds a migration |
| SC-TST-2 | Destructive migration steps have pre-checks | Any DROP, ALTER, or DELETE in a migration is preceded by a `DO $$ BEGIN ... END $$` existence or duplicate check | Removing the pre-check block; adding a destructive step without one | Migration review | Any feature that adds a migration with destructive steps |
| SC-TST-3 | Enum values are introduced, never overloaded | A new status or enum value is added for new meaning — existing values never have their semantics changed | Changing the meaning of `MATCHED`, `RESOLVED`, `SUCCESS`, or any existing status without a new value | Arch-council (data contract gate) | Any feature that adds or modifies a status or enum field |

---

## SC-FAIL — Failure Modes

How the system can break and what must not be silently swallowed.

| Code | Name | Statement | Broken by | Verified by | AC tag |
|------|------|-----------|-----------|-------------|--------|
| SC-FAIL-1 | DB constraint violations are hard failures | Constraint violations propagate as errors to the caller — never silently suppressed or deduped at the service layer | Try/except blocks that catch `IntegrityError` and return success; service-layer deduplication that masks a constraint violation | Code review, arch-council | Any feature that writes to a constrained table |
| SC-FAIL-2 | Duplicate reconciliation submission is rejected | A second `POST` to submit reconciliation for the same run returns an error — not a silent duplicate or 500 | Removing the duplicate check; changing INSERT to upsert without surfacing the conflict | Tester | Any feature that modifies the reconciliation submission path |
| SC-FAIL-3 | Missing salary definition is a hard reject | An employee without a resolvable salary definition causes the run to hard-fail for that employee — not a silent skip | Changing the missing-definition path to continue; swallowing the lookup exception | Tester | Any feature that modifies employee processing or onboarding |

---

*This catalogue is intentionally lean at initialisation. Entries are added as the UI audit and future sprints surface new contracts. Every new SC entry must be reviewed by arch-council before being referenced in acceptance criteria.*
