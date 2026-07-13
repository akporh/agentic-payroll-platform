# Stage 05 Output: Onboarding Instrumentation and Dry-Run Readiness (C13/C14)

## Persisting the parallel-run comparison (Stage 04 F-04-07's recommendation)

**Status: unchanged — still not persisted.** `ReconSlideOver` (`frontend/src/pages/PayrollResults.tsx:243-434`) does the entire legacy-system comparison client-side: `runComparison` diffs uploaded XLSX rows against `results` purely in JS state; `submitReconRows` only calls `setReconRows`/`setReconStep` (no network call); `downloadRecon` writes an XLSX via client-side `XLSX.writeFile`. Grep for `parallel_run`, `legacy_comparison`, `old_system` across `backend/` returns zero hits. No route or table persists this comparison.

**Important distinction confirmed in this stage**: this is a *different* feature from the already-built, already-tested scalar `payroll_reconciliation` mechanism (total `actual_total` vs. `expected_total`, MATCHED/MISMATCH). Do not conflate the two when scoping remediation — persisting `ReconSlideOver`'s row-level legacy-system diff is new work, not an extension of the existing reconciliation feature.

## Dry-run mechanism feasibility

**Status: entirely unbuilt as a product feature, but the underlying engine is already well-suited to it.** No `dry_run`/`simulate` concept exists anywhere in `backend/domain/payroll/` or `backend/application/`. However:

- `backend/domain/payroll/executor.py:1-9` explicitly documents its core functions as pure computation — "No database writes." `execute_single_employee_payroll` and `run_sequential_payroll` (`sequential_executor.py:615`) take dicts in, return a result dict out, with no `INSERT`/`commit()` inside them.
- `backend/scripts/simulate_payroll.py` already exists as a developer CLI proving this: its own docstring states it "Runs the real `run_sequential_payroll()` engine for a single employee... Read-only: no database writes," calling the exact production functions directly.
- The only production caller of `execute_single_employee_payroll` is the retry service (`payroll_retry_service.py:70,672`), which persists results itself after calling it — persistence is layered on by the caller, not baked into the engine.

**Conclusion**: a real dry-run endpoint is architecturally cheap relative to what might have been feared — it can wrap the same pure-compute entry point the developer script already uses, without touching the executor itself. This lowers the platform-readiness bar for C14 considerably compared to "we'd need to build a parallel calculation engine." The remaining work is product-level: an API endpoint, a UI to present dry-run results, and a decision on what "safely separated from production payroll-run state" means operationally (e.g. does a dry run create a `payroll_run` row at all, or bypass the table entirely?) — this exact question is forwarded to Stage 08, per this stage's scope.

## Instrumentation for the four baseline metrics (Stage 04 F-04-03)

None of the four metrics Stage 04 named (mapping time, mapping error rate, parallel-run agreement rate, time-to-go-live) are currently instrumented anywhere in the codebase. Confirmed by the absence of any timing/measurement code around `NativeUploadFlow`, the absence of persisted `ReconSlideOver` output (above), and the absence of any workspace-status-change history (`workspace.status` transitions are not audited — same underlying gap as `audit-coverage-assessment.md`). Time-to-go-live specifically cannot be measured without a workspace status-transition audit trail, which does not exist.

## C13/C14 readiness summary

| Prerequisite | Status |
|---|---|
| Persisted parallel-run comparison | Not built — greenfield, lower-cost first step available (persist what `ReconSlideOver` already computes) |
| Dry-run mechanism | Not built as a feature, but the engine's pure-compute path already exists and is proven reusable via `simulate_payroll.py` — moderate, not high, implementation cost |
| Deterministic import validation (existing hard-validator) | Already exists (Stage 01 F-01-04) — reusable for validating a *proposed* import, not just a committed one; needs a "propose, don't commit" mode, not new validation logic |
| Baseline instrumentation | Not built — requires workspace status-transition audit (shared dependency with `audit-coverage-assessment.md`) |

**C13 (Onboarding Mapping Assistant) remains correctly gated on C14 per the binding decision — this stage's evidence does not change that gate, but does clarify that C14's hardest sub-problem (a safe dry run) is more tractable than it might appear, given the engine's existing pure-compute design.**
