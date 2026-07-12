# Stage 04 — Findings

Status: **in-progress**. All entries below use the template in
[`../_core/finding-schema.md`](../_core/finding-schema.md). Status values are
restricted to this stage's five-value set: confirmed / plausible /
unconfirmed / rejected / human decision required.

---

## Headline result

Finding **04-001** (below) **reproduces** Stage 03's finding 03-002 by
controlled non-production execution: an original payroll run and a
subsequent per-employee retry of the same run can compute PAYE under two
different statutory-rule versions, silently, with no error or trace entry.
This is the primary Stage 04 result and is escalated to `_core/human-decisions.md`
as an S0 item per the severity model's escalation rule.

---

## 1. Original-run/retry execution comparison matrix

| Path | Entry point | Allowed run status | Component metadata source | Client override source | Payroll-rule source | Statutory rule/tax band source | Public holiday source | Executor |
|---|---|---|---|---|---|---|---|---|
| Original run | `POST /api/v1/payroll/run` (`payroll.py`) | `DRAFT` (created by the route itself) | Live `component_metadata` | Live `client_component_metadata` | Live `payroll_rule` (date-resolved) → frozen into `rule_set`/`rule_set_item` | Live `statutory_rule`/`tax_band`, date-resolved, then frozen into `rules_context_snapshot.statutory_rule` | Live `national_public_holiday` ∪ `workspace_public_holiday`, frozen into `public_holidays_snapshot` | Sequential (production path — `component_metadata` always supplied by the route) |
| Per-employee retry | `POST /payroll/run/{id}/retry` → `retry_failed_payroll_employees()` | `PARTIAL` only (`payroll_retry_service.py:561-565`) | `component_metadata_snapshot` (frozen) | `client_component_metadata_snapshot` (frozen) | `rule_set_item` by frozen `payroll_run.rule_set_id` (v2), or live date-resolution fallback for legacy pre-rule-set runs | **Live `statutory_rule`/`tax_band`, re-resolved from frozen `statutory_effective_date` — see 04-001** | `payroll_run.public_holidays_snapshot` (frozen) | Sequential (retry always supplies `component_metadata` from the snapshot tables — confirmed in Stage 01/03) |
| Full-run retry | `_retry_full_run()` stub | N/A | N/A | N/A | N/A | N/A | N/A | **Dead path** — the function's entire body is `raise ValueError("FULL_RUN retry is disabled...")` (`payroll_retry_service.py:494-499`), consistent with `CLAUDE.md`'s `retry_strategy` invariant. Not reachable via any API route. |
| Partial retry (as a distinct concept from per-employee) | — | — | — | — | — | — | — | **Not a distinct code path.** "Partial" describes the *run's status* (some employees failed), not a retry mode — the only retry mode is per-employee, which retries every `FAILED` row in a `PARTIAL` run. There is no separate "retry N of M failed employees" selector; `retry_failed_payroll_employees()` always retries all currently-`FAILED` rows for the run. |
| Legacy pre-snapshot run | Any run created before migration `b5c6d7e8f9a0` (Sprint 19) | Retry blocked | N/A | N/A | N/A | N/A | N/A | `validate_snapshot_complete()` raises `ValueError` ("predates snapshot engine — open a correction run") before any calculation is attempted — confirmed hard-fail, not silent skip (`snapshot_service.py:143-175`, cited in Stage 03) |
| Legacy pre-rule-set run | Run created before a `rule_set_id` existed for the workspace/date | Retryable | Snapshot tables (unaffected by rule-set presence) | Snapshot tables | Falls back to live `resolve_effective_rules()` date-resolution — same function the original run itself would have used | Live re-resolution (same as all retries — 04-001 applies equally) | Frozen snapshot | Sequential |
| Legacy executor fallback | Any caller passing no `component_metadata` | N/A (not a "run status", a per-employee code branch) | N/A — bypasses component_metadata entirely | N/A | N/A | Still resolved via whichever caller supplied it | N/A | Legacy (`executor.py`'s `else` branch) — confirmed in Stage 01/02 to be unreachable from the production route or retry service under normal operation (both always pass `component_metadata`); only reachable from a caller like the deprecated `scripts/run_first_payroll_emp001.py` (Stage 02, 02-005, confirmed broken/non-functional) |

**Rounding, handler order, totals construction:** identical between original run
and retry by construction — both call the exact same `run_sequential_payroll()`
function in `sequential_executor.py` (confirmed by direct code citation:
`executor.py:108-115`'s `_run_sequential()` is the sole entry point for both
`batch_processor.py` (original run) and `payroll_retry_service.py` (retry) —
there is no second implementation of the calculation loop). Any divergence
in a calculated *result* therefore traces back to a divergence in the
*inputs* fed to that shared function (statutory rule/tax bands — 04-001),
never to different rounding or ordering logic.

---

## 2. Context-construction comparison

Extends Stage 03's client_meta comparison (03-001, confirmed identical and
correctly reconciled) with the remaining context-builder surface:

| Context field | `payroll.py` (original) | `payroll_retry_service.py` (retry) | Parity |
|---|---|---|---|
| `client_meta` (proration/is_active reconciliation) | Lines 459-493 | Lines 257-282 | **Confirmed identical** — Stage 03 finding 03-001 |
| `period` (PeriodContext) | Built from live `pay_cycle.frequency` + explicit API params + live public holidays | Built from frozen `payroll_run.period_start/period_end` + frozen `public_holidays_snapshot` (`_build_shared_context:139-143`) | **Confirmed correct-by-design divergence** — retry must use the frozen period, not re-derive it; this is not a defect, it's the correct behaviour for a fixed run |
| `statutory_rule_id`/`tax_bands`/pension/NHF/health/levy/life-insurance rates | Resolved live, then frozen into snapshot | **Re-resolved live from `statutory_effective_date`, snapshot never read** | **Confirmed divergence mechanism — 04-001** |
| `payroll_rules` | Resolved live into a rule set | Read from `rule_set_item` by frozen ID, or live fallback for legacy runs | Confirmed correct — Stage 03 finding 03-005 |
| `rate_code_map` | `list_rate_codes(workspace_id)` — live | Same function, same live call (`_build_shared_context:343`) | **Confirmed identical mechanism.** Not snapshotted on either path — both re-read live rate codes. This is a duplicated-but-consistent live read, not a snapshot/live boundary gap, since both paths agree by construction (see 04-002 below for the drift risk this still carries). |
| `expected_hours`/`expected_days`/`ph_dates_used`/`ph_source` | Computed live | Read from `original_snapshot` (frozen) | Confirmed correct — snapshot-first |
| `rule_floor_dates` | Not applicable to original run (only used for historical-rate resolution during retry/cross-period input claiming) | Re-queried live (`_build_shared_context:349-358`) — **explicitly documented as safe to re-query**, per the in-code comment: "a floor date only ever moves earlier as more history is loaded, so re-querying cannot corrupt... determinism" | Confirmed intentional, reasoned divergence — not a defect |
| `salary_components` (per employee) | Live `employee_contract` → live `salary_definition` | Live `employee_contract_snapshot.salary_definition_id` → live `salary_definition` | Confirmed correct-by-design (D1) — Stage 03 finding 03-003, mitigated by the D-ARCH-1 edit-lock |

**Duplicated context-building logic:** `client_meta` construction (03-001) and
period/statutory-rate extraction are each implemented twice — once in
`payroll.py`, once in `payroll_retry_service.py` — rather than shared via a
common function. Where the two copies are semantically equivalent (client_meta,
public holidays, rule sets), this is a maintainability/DRY concern for Stage 12,
not a correctness defect, because both copies currently agree. Where they are
NOT equivalent (statutory rule resolution), the duplication is exactly how the
04-001 divergence became possible — a single shared "resolve and freeze, then
always read the freeze" helper would have structurally prevented it.

---

## 3. Snapshot-source comparison

Carries forward Stage 03's snapshot/live boundary map (Section 6 of
`03-configuration-integrity/findings.md`) without re-deriving it. Per the
sprint's four-way classification (frozen content / frozen ID joined to
immutable content / frozen date re-querying mutable content / no snapshot
boundary):

| Domain | Classification | Evidence |
|---|---|---|
| Component metadata | Frozen content (`component_metadata_snapshot`) | Stage 03 §1, §6 |
| Client component overrides | Frozen content (`client_component_metadata_snapshot`) | Stage 03 §1, §6 |
| Employee contract (structural fields) | Frozen content (`employee_contract_snapshot`, minus `components_jsonb`) | Stage 03 finding 03-003 |
| Salary definition/components | Frozen `salary_definition_id` joined to **live, mutable** `salary_definition.components_jsonb` | Stage 03 finding 03-003 — deliberate (D1), mitigated by edit-lock |
| Payroll rules/rule sets | Frozen ID (`rule_set_id`) joined to immutable `rule_set_item` (v2); live date-resolution fallback for legacy runs | Stage 03 finding 03-005 |
| **Statutory rules/tax bands** | **Frozen date (`statutory_effective_date`) re-querying mutable live content** — the one domain in this classification's riskiest category | **04-001** |
| Public holidays | Frozen content (`public_holidays_snapshot`) | Stage 03 finding 03-005 |
| Payroll inputs | Claimed and frozen via `link_inputs_to_run` at original-run time (per `CLAUDE.md`'s `payroll_input.input_category` invariant); retry reads the same claimed rows via `load_inputs_for_run(payroll_run_id)` (`payroll_retry_service.py:601`) — **frozen content**, confirmed by direct citation, not previously covered by Stage 03 | New this stage |
| Period context | Frozen (`payroll_run.period_start/period_end`) | This stage, §2 above |

**Statutory rules/tax bands is the only domain in the entire configuration
surface classified in the riskiest category** ("frozen date re-querying
mutable content") rather than "frozen content" or "frozen ID → immutable
content." Every other domain either freezes its actual content or freezes an
identifier that points at content which cannot change without a separate,
independently-guarded mechanism (the rule-set lock, the salary-definition
edit-lock). Statutory rules have neither protection.

---

## 4. Rule-resolution comparison

No new divergence found beyond what Stage 03 already established (03-005,
confirmed correct). `resolve_effective_rules()` — the single function used by
both the original route (for legacy pre-rule-set workspaces) and by
`_build_shared_context`'s fallback branch — implements the `is_active` +
`effective_from DESC` date-driven resolution `CLAUDE.md`'s invariant table
requires. Both call sites use the identical function, so no drift is
possible between them by construction.

---

## 5. Calculation and rounding comparison

Both paths call `run_sequential_payroll()` in `sequential_executor.py` —
confirmed the sole implementation of component eligibility, ordering,
proration, taxable/non-taxable classification, gross pay, deductions, PAYE,
NHF/pension/health/levy/life-insurance, and rounding (`Decimal` +
`ROUND_HALF_UP` throughout, per `CLAUDE.md`'s monetary-value rule). No
separate retry-specific calculation logic exists anywhere in
`payroll_retry_service.py` — it assembles inputs and hands off to the same
`execute_single_employee_payroll()` → `_run_sequential()` → `run_sequential_payroll()`
chain the original run uses via `batch_processor.py`. Confirmed by the fact
that this stage's controlled test's Employee A (original run) and Employee B
(retry) results both matched their respective expected-PAYE formulas exactly
(§ controlled test below) — the arithmetic itself is provably identical; only
the statutory-rate *input* diverged.

**Existing test reliability check** (per the sprint's instruction to verify
tests exercise current production paths): `tests/test_payroll_retry.py` was
inspected (not modified, not executed as part of this stage — Stage 04's
controlled test is a separate script per the "do not rely on existing
scripts/tests without independent validation" constraint) and confirmed to
call the real `/api/v1/payroll/run` and `/api/v1/payroll/run/{id}/retry`
routes, i.e. the current production paths, not a mock or superseded
endpoint. Its assertions on `payroll_run.total_tax`/`total_deduction`/`total_net_pay`
(lines 419-467) independently confirm persistence-layer totals-aggregation
parity between original and retried results, consistent with what this
stage found in §6 below.

---

## 6. Persistence and state-transition comparison

| Aspect | Original run | Retry | Parity |
|---|---|---|---|
| Result columns written | `payroll_result_repo.py::save_payroll_results_bulk` — 12 columns (`payroll_result_id`, `payroll_run_id`, `employee_id`, `gross_components_jsonb`, `deductions_jsonb`, `net_pay`, `calculations_snapshot_json`, `component_trace_jsonb`, `status`, `error_message`, `per_employee_context_json`, `salary_inputs_snapshot`) | `payroll_retry_service.py::_insert_result` — same 12 columns | **Confirmed identical column set** |
| Insert mechanism | Single multi-row `execute_values` INSERT (bulk, first write for the run) | `DELETE ... WHERE status='FAILED'` then single-row `INSERT` per employee, per the module's documented rationale (the `trg_snapshot_immutable` trigger blocks UPDATE once `calculations_snapshot_json` is non-empty, and `uq_payroll_result_employee_run` requires the old row gone before the new one lands) | Confirmed correct, documented design — not a parity gap, a necessary mechanical difference given the same underlying constraints both paths respect |
| Run status transitions | `DRAFT → CALCULATING → CALCULATED\|PARTIAL` (`run_executor.py`) | `PARTIAL → CALCULATED\|PARTIAL`, recomputed from a live `COUNT(*) FILTER (WHERE status='FAILED')` over `payroll_result`, not from local counters (`payroll_retry_service.py:733-743`) | Confirmed correct — retry's recomputation-from-DB approach is more robust than trusting in-memory counts, consistent with the module's own stated design rationale |
| Failure/rollback behaviour | `execution_mode="isolated"` (route default) — one employee's failure does not abort the batch; `execution_mode="atomic"` would re-raise (not used by the production route) | Per-employee `try/except` around `execute_single_employee_payroll`; a calculation exception is caught and written as a `FAILED` result, not re-raised — confirmed equivalent isolation semantics to the original run's `isolated` mode | Confirmed equivalent |
| Reconciliation refresh | Out of this stage's direct evidence — `reconciliation_service.py` was not traced in this stage; flagged for Stage 08 (data integrity) since Stage 03 confirmed reconciliation *configuration* doesn't exist yet, but reconciliation *execution* on retry completion was not verified here | — | **Unverifiable in this stage — insufficient evidence gathered; not claimed either way** |
| Audit log / event store | Original: `save_audit_log`/`save_event` per transition, called from `run_executor.py`'s audit/event payload builders | Retry: same `save_audit_log`/`save_event` functions, called directly from `payroll_retry_service.py:794-804` for the `PARTIAL → CALCULATED` (or `→ PARTIAL`) transition | Confirmed identical mechanism, same repository functions |

---

## 7. Trace-footprint comparison

Carries forward Stage 02 finding 02-002 without re-deriving it: original run
produces ~7-9 `execution_trace` step rows; per-employee retry produces
**zero**, because `retry_failed_payroll_employees()` instantiates an
`ExecutionTracer` but never calls `.step(...)` anywhere in its body (Stage 02
evidence, re-confirmed still accurate by this stage's controlled test — the
retry's console output in the test run above genuinely does show far less
structured step output than the original run's, visually consistent with the
Stage 02 finding).

**Does this prevent parity verification?** For the specific 04-001 divergence:
**no** — `component_trace_jsonb` on the retried `payroll_result` row does NOT
record which `statutory_rule_id`/version was used (confirmed by inspecting the
`trace` structure built in `run_sequential_payroll()`, Stage 02 evidence
`2026-07-11-component-trace-jsonb-mechanism.txt` — the trace records
component/method/result per line item, not the statutory-rule identity that
produced the PAYE band applied). The *only* way this stage was able to detect
and confirm the divergence was by comparing the actual numeric PAYE result
against hand-computed expectations under each candidate rule — there is no
persisted field anywhere (`execution_trace`, `component_trace_jsonb`, or any
other column) that would let an operator retroactively determine, from the
database alone, which statutory-rule version a given `payroll_result` row was
actually calculated under. This is a distinct, compounding observability gap
on top of 04-001 itself — see finding 04-002.

---

## 8. Legacy-run compatibility assessment

- **Pre-snapshot-engine runs** (created before migration `b5c6d7e8f9a0`):
  retry hard-fails via `validate_snapshot_complete()` before any calculation
  is attempted. Confirmed safe — no silent wrong-data risk, per Stage 03.
- **Pre-rule-set runs** (snapshot engine present, but no `rule_set_id`
  resolved at original-run time): retry falls back to live
  `resolve_effective_rules()` — the exact same function and date-driven
  logic the original route itself would have used. Confirmed low-risk: this
  fallback can only diverge from the original run if the workspace's
  `payroll_rule` table changed between the original run and the retry, which
  is a general risk shared with the *original run's own* rule resolution (not
  a retry-specific gap), and is a much narrower surface than 04-001 since
  `payroll_rule` changes are workspace-initiated CRUD (visible, deliberate),
  not a platform-level statutory update.
- **Legacy executor fallback**: confirmed unreachable from either the
  production route or the retry service under normal operation (Stage 01/02)
  — not a live compatibility concern for this stage's parity question.

---

## Findings

### 04-001 — Reproduced: retry can silently calculate PAYE under different statutory content than the original run, within the same payroll_run

- **stage:** 04-original-run-retry-parity
- **location:** `backend/application/payroll_retry_service.py:145-171` (live re-resolution query, unchanged since Stage 03's citation); controlled reproduction: `evidence/statutory_divergence_controlled_test.py`, output at `evidence/2026-07-12-statutory-divergence-test-output.txt`
- **current implementation:** Confirmed by direct, reproduced observation against the local non-production `payroll_dev` database (not a shared or production database — connection confirmed local-only, all test rows deleted afterward, verified via a post-cleanup `SELECT COUNT(*)` query showing zero residue). Test design: Employee A calculated successfully under statutory_rule A (10% flat PAYE marker) in an original run; a new statutory_rule B (25% flat PAYE marker, `effective_from` between A's and the run's frozen `statutory_effective_date`) was inserted after the original run completed; Employee B (initially failed, then fixed and retried) was calculated under statutory_rule **B**, not A — confirmed by exact numeric match (retried PAYE ₦92,000.00 against a ₦92,000.00 prediction under rule B, vs. a ₦36,800.00 prediction under rule A — a 2.5x difference, unambiguous). Both employees belong to the same `payroll_run`.
- **intended behaviour:** Not documented as intentional anywhere. `CLAUDE.md`'s `payroll_run.status = 'APPROVED'` invariant establishes that once a run is finalized its results must not change — the spirit of that invariant (a payroll run's calculation basis should be stable and internally consistent) is violated at the `PARTIAL` stage by this mechanism, even though `PARTIAL` is not itself covered by the `APPROVED` immutability rule.
- **suspected or confirmed defect:** **Confirmed** — reproduced with compliant controlled-execution evidence per `_core/evidence-standard.md` type 4. Upgraded from Stage 03's `plausible` per this stage's explicit instruction: "upgrade to confirmed only if an actual original-run/retry divergence is reproduced with compliant evidence."
- **evidence:** `evidence/statutory_divergence_controlled_test.py`, `evidence/2026-07-12-statutory-divergence-test-output.txt`
- **status:** confirmed
- **severity:** S0 — statutory/financial miscalculation, per `_core/severity-model.md`'s definition verbatim ("Statutory/financial miscalculation... or violation of a `CLAUDE.md` data-contract invariant"). Escalated to `_core/human-decisions.md` immediately per the severity model's escalation rule.
- **related invariant:** `CLAUDE.md` — `statutory_rule (country_code, effective_from)` UNIQUE (the mechanism this finding depends on); adjacent in spirit to the `payroll_run.status = 'APPROVED'` immutability invariant

---

### 04-002 — No persisted field records which statutory-rule version a payroll_result row was actually calculated under

- **stage:** 04-original-run-retry-parity
- **location:** `backend/domain/payroll/sequential_executor.py:696-786` (trace structure — confirmed to record component/method/result, not statutory-rule identity); `payroll_result` table schema (no `statutory_rule_id` column, confirmed via Stage 03's migration search finding no such column exists anywhere)
- **current implementation:** Neither `execution_trace`, `component_trace_jsonb`, nor any dedicated `payroll_result` column records which `statutory_rule_id`/version was resolved for a given employee's calculation. The only way this stage could confirm 04-001's divergence was to independently recompute expected PAYE under each candidate rule and compare against the persisted numeric result — a forensic reconstruction, not a direct read.
- **intended behaviour:** Not documented. `rules_context_snapshot.statutory_rule` on the `payroll_run` row records what the *original* run resolved, but nothing records what a *retry* actually used per employee, which is precisely the gap 04-001 exploits and this finding shows has no independent audit trail either.
- **suspected or confirmed defect:** Confirmed as an observability gap by direct citation (absence of the field, confirmed by schema inspection). This compounds 04-001's severity: even after this audit, an operator with a suspicious `payroll_result` row would have no persisted way to confirm or rule out this divergence for a specific historical run without a forensic recomputation like the one this stage performed.
- **evidence:** Same as 04-001, plus Stage 02's `2026-07-11-component-trace-jsonb-mechanism.txt`
- **status:** confirmed
- **severity:** S1 (observability gap compounding a confirmed S0 — not itself a miscalculation, but it means 04-001 cannot be detected retroactively in production without this kind of audit)
- **related invariant:** none directly; relevant to Stage 10 (execution-trace remediation)

---

### 04-003 — Persistence, state-transition, and calculation-arithmetic parity confirmed across all other compared dimensions

- **stage:** 04-original-run-retry-parity
- **location:** see §5 and §6 tables above
- **current implementation:** Both paths share the identical calculation function chain (`run_sequential_payroll()`), the identical `payroll_result` column set and semantics, equivalent failure-isolation behaviour, and DB-authoritative (not counter-based) status recomputation.
- **intended behaviour:** Consistent with a single shared calculation engine design.
- **suspected or confirmed defect:** None — recorded as a positive control so Stage 04's overall parity picture is not read as "everything is broken." The confirmed gap is narrow and specific to statutory-rule sourcing (04-001), not systemic.
- **evidence:** §5, §6 above; Stage 03 §1-§6
- **status:** confirmed
- **severity:** S3 (positive finding)
- **related invariant:** none

---

### 04-004 — Reconciliation-refresh behaviour on retry completion is unverified in this stage

- **stage:** 04-original-run-retry-parity
- **location:** `backend/application/reconciliation_service.py` (not traced in this stage)
- **current implementation:** Not determined — this stage did not trace whether a `PARTIAL → CALCULATED` transition triggered by retry causes any reconciliation-related side effect, and whether that would differ from the original run's `CALCULATING → CALCULATED` transition.
- **intended behaviour:** Not determined in this stage.
- **suspected or confirmed defect:** Unconfirmed — genuinely not investigated, not a claim of correctness or defect either way.
- **evidence:** none gathered
- **status:** unconfirmed
- **severity:** S3 (unclassified pending investigation, not assumed low-risk)
- **related invariant:** `CLAUDE.md` — `payroll_reconciliation.status = 'MATCHED'`/`'RESOLVED'` invariants (potentially relevant, not confirmed)

---

## Confirmed parity register

| Dimension | Status |
|---|---|
| Component metadata resolution (snapshot vs. live) | Confirmed parity — correct by design |
| Client component overrides (`proration_strategy`/`is_active` dual storage) | Confirmed parity — Stage 03 03-001 |
| Payroll rule resolution (date-driven, `rule_set_item` frozen ID) | Confirmed parity — Stage 03 03-005 |
| Public holiday sourcing | Confirmed parity — Stage 03 03-005 |
| Payroll input claiming | Confirmed parity — new this stage |
| Calculation arithmetic, rounding, handler order | Confirmed parity — identical shared function |
| Persistence column set and semantics | Confirmed parity — 04-003 |
| Run-status transition logic | Confirmed parity — DB-authoritative on both paths |
| Audit log / event store writes | Confirmed parity |
| Failure isolation semantics | Confirmed parity |
| Legacy pre-snapshot-engine compatibility | Confirmed safe (hard-fail, not silent) |
| Legacy pre-rule-set compatibility | Confirmed low-risk (shared resolution function) |

## Divergence register

| Dimension | Classification | Finding |
|---|---|---|
| Statutory rule/tax band sourcing | **Reproduced defect** | 04-001 (S0) |
| Statutory-rule-used observability | Confirmed defect (observability gap) | 04-002 (S1) |
| Period context (frozen vs. live) | Intentional divergence — correct by design | §2 |
| Salary component sourcing (live join, D1) | Intentional divergence — correct by design, mitigated | Stage 03 03-003 |
| `rule_floor_dates` (live re-query) | Intentional divergence — explicitly reasoned safe in-code | §2 |
| `execution_trace` step-level footprint | Confirmed defect (carried from Stage 02) | 02-002 |
| Reconciliation-refresh parity | Unverifiable in this stage | 04-004 |

---

## Handoff notes for later stages

- **Stage 05 (snapshot integrity):** 04-001 and 04-002 are direct inputs —
  Stage 05 should assess whether `rules_context_snapshot.statutory_rule`
  should be the canonical read path for retry (closing 04-001) and whether
  snapshot completeness should be extended to record which statutory content
  was *actually used* per employee (closing 04-002), not just what the
  original run resolved.
- **Stage 07 (silent failures and observability):** 04-001 is a silent
  divergence with zero observability signal by construction (no exception,
  no log line beyond ordinary calculation success, no trace entry) — the
  clearest possible example of what Stage 07 is scoped to catalogue.
- **Stage 08 (data integrity):** 04-004 (reconciliation-refresh parity,
  unverified) should be picked up directly. 04-001's real-world likelihood
  (how often are new `statutory_rule` versions actually inserted while a run
  sits `PARTIAL` in production) is a data-integrity question Stage 08 is
  better positioned to answer than this stage was (this stage used
  synthetic, deliberately-triggered data, not a frequency analysis of real
  workspace history).
- **Stage 10 (execution-trace remediation):** 04-002 is a direct input — any
  remediation design for `execution_trace`/`component_trace_jsonb` should
  consider recording the resolved `statutory_rule_id` per calculation,
  closing this stage's forensic-reconstruction gap.
- **Stage 11 (scenario testing):** This stage's controlled test script
  (`evidence/statutory_divergence_controlled_test.py`) is a working,
  self-cleaning reproduction of a real S0 defect — Stage 11 should consider
  formalizing it (or a fixed-behaviour variant, post-remediation) as a
  regression scenario, since nothing in the current test suite
  (`tests/test_payroll_retry.py` or elsewhere) currently covers this case.
- **Stage 13 (consolidated backlog):** 04-001 (S0, confirmed) is the
  highest-severity finding in the programme so far and should be the top
  entry once the backlog is assembled, per the severity model's
  status-then-severity prioritization rule.
