# Stage 08 Output: Dry-Run Mechanism Design (C14)

Answers Stage 08 Q6, resolving DQ-003 and DQ-004 (and Stage 02's carried F-02-10), under SG-14's identity/scoping constraints. Consumes Stage 05's feasibility evidence (`onboarding-platform-readiness.md`): the engine's pure-compute entry points and the `simulate_payroll.py` precedent. Evidence pinned at `573be0d`.

## 1. F-02-10 resolved: real executor path, not a separate simulation

**The dry run exercises the real production calculation path** — `execute_single_employee_payroll` / `run_sequential_payroll` (`backend/domain/payroll/executor.py:1-11` documents "No database writes — pure computation only"; `sequential_executor.py:652` is the sequential entry) — with the same component-metadata, statutory-resolution, and proration machinery a real run uses. A separate simulation engine is rejected: it would immediately diverge from the engine it predicts (the platform already lived this lesson — `project_simulation_scripts_no_proration`), and the entire value of C14 as C13's safety gate is that dry-run results *are* what the real run would produce. The developer CLI `backend/scripts/simulate_payroll.py` already proves the reuse pattern ("Runs the real `run_sequential_payroll()` engine… Read-only: no database writes").

What the dry run reuses vs. bypasses:

| Real-run stage | Dry run |
|---|---|
| Input assembly (employees, components, statutory resolution, rule sets, period context) | **Reused** — same route-layer assembly logic, refactored into a shared `assemble_run_context(...)` function both paths call (today it lives inline in `_calculate_and_persist`, `payroll.py:939-1035`) |
| `link_inputs_to_run` claiming | **Bypassed** — dry runs never claim `payroll_input` rows (claiming mutates `payroll_run_id`; a dry run must not consume inputs another real run needs) |
| DRAFT `payroll_run` row creation | **Bypassed** (§2) |
| Pure execution (`execute_payroll_run_pure` → executors) | **Reused unchanged** |
| `persist_payroll_run_execution` (header/results/audit/events) | **Bypassed entirely** |

## 2. DQ-004 resolved: what "safely separated from production state" means operationally

**A dry run creates no `payroll_run` row** — nor any row in `payroll_result`, `payroll_input` (no claiming), `audit_log`'s run-transition domain, or `event_store`. Reasons: (a) every consumer of `payroll_run` (status pipeline, reconciliation, exports, retry, the D-ARCH-1 lock trigger, `is_first_paid_month` history queries — `payroll.py:245-260`) assumes rows are real runs; a `DRY_RUN` status value would ripple through every one of those consumers and violate the platform's own "new enum values are introduced, never overloaded" discipline at massive surface area; (b) the run tables are financially load-bearing evidence — polluting them with hypotheticals weakens the very properties Stages 06–07 hardened.

Instead, the dry run persists its own artifact:

### `dry_run_execution` (workspace-scoped, SG-14)

| Column | Notes |
|---|---|
| `dry_run_id` UUID PK | |
| `workspace_id` UUID NOT NULL | scoped like any workspace record |
| `requested_by` UUID FK NOT NULL | verified principal (SG-14: under the operator's identity — never a service placeholder) |
| `purpose` | `ONBOARDING_IMPORT` (C13 gate) / `AD_HOC` |
| `input_snapshot_jsonb` | the proposed employee/component rows as submitted (for `ONBOARDING_IMPORT`: the confirmed C13 mapping output), plus resolved context identifiers (statutory_rule_id/version, rule_set_id, period) — what was computed *from* |
| `input_hash` | SHA-256 over the canonicalised input snapshot — the commit-time linkage key (§3) |
| `results_jsonb` | per-employee results + totals, amounts as strings, including per-employee `component_trace` |
| `status` | `SUCCESS` / `FAILED` (with error detail) |
| `created_at` TIMESTAMPTZ DEFAULT now() | |

Append-only (it is evidence that the C13 gate was exercised — `event-audit-foundation-design.md` §5 trigger list); a `DRY_RUN` domain audit record is written through the facade on each execution (domain 1's config-adjacent action class).

## 3. Flow

1. `POST /{workspace_id}/dry-runs` (authenticated, workspace principal — R1/R2 via the shared dependency): body carries proposed rows (for onboarding: unmapped-to-committed employees — they need not exist in `employee` yet) + target period.
2. Validation: the existing deterministic hard-validator runs in propose-mode against the payload (Stage 05: "needs a 'propose, don't commit' mode, not new validation logic"). Validation failure → `FAILED` artifact with named errors (still a useful gate outcome).
3. Context assembly via the shared `assemble_run_context` — live salary definitions, date-driven statutory resolution (no shortcuts), workspace payroll config.
4. Pure execution; results written to `dry_run_execution` only.
5. `GET /{workspace_id}/dry-runs/{id}` returns results for the UI (Stage 09 surface).
6. **C13 commit linkage**: the onboarding commit endpoint (existing Upload/Enroll path) accepts an optional-in-v1, **mandatory-for-C13-flows** `dry_run_id`; commit verifies the artifact belongs to the workspace, is `SUCCESS`, and its `input_hash` matches the rows being committed — "commit preceded by a successful dry-run of exactly these rows" becomes checkable evidence, not workflow convention. Hash mismatch (rows edited after the dry run) → reject with "re-run the dry run".

## 4. Boundary notes

- Dry runs read live config (salary definitions, statutory rules) at execution time; the artifact records which versions were resolved, so a later commit after a config change is detectably stale via re-validation at commit (same principle as C12's re-validate-at-apply).
- No LLM anywhere (C14 is deterministic — the matrix); the C13 proposal that *feeds* the dry run is separately confirmed by the operator before this mechanism runs.
- Retention: dry-run artifacts are gate evidence for committed imports — they follow the 7-year-floor posture like other compliance evidence; no purge mechanism designed (DQ-008 posture).
- Rate/size bounds: request bounded to the bulk-upload row ceiling the platform already enforces on real imports.

## 5. Requirements satisfaction and verification

| Requirement | Satisfied by | Verification |
|---|---|---|
| SG-14 identity/scoping | §2 `requested_by` + workspace scoping; §3.1 shared dependency | Cross-workspace dry-run request → 404; artifact rows carry verified principal |
| Production-state separation (DQ-004) | §1 bypass table + §2 no-run-row | **Non-mutation test**: snapshot row counts of `payroll_run`/`payroll_result`/`payroll_input.payroll_run_id`/`event_store` before/after a dry run — identical (the load-bearing closure evidence) |
| Real-path fidelity (DQ-003) | §1 reuse of `execute_payroll_run_pure` | Equivalence test: same fixture through dry-run and real run produces identical per-employee results |
| C13 gate enforceability | §3.6 hash linkage | Commit with missing/mismatched/failed `dry_run_id` rejected (C13-flow fixtures) |
| Input non-consumption | §1 no claiming | Unclaimed `payroll_input` rows remain unclaimed after dry run |

DQ-003 and DQ-004 are resolved by this design (recorded in `decision-queue.md`).
