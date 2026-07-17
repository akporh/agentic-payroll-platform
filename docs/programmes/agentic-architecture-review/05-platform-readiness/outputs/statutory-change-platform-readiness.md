# Stage 05 Output: Statutory-Rule Change-Management Readiness (C12)

**Status: unchanged — no admin route, no tested change-management capability. Confirmed via direct code re-verification, cross-referenced against `docs/audit-program/03-configuration-integrity/findings.md`.**

## Current maintenance path, exhaustively re-verified

- `backend/api/routes/admin.py` contains exactly three routes, all `HTMLResponse` template renders (`/admin`, `/admin/onboarding`, `/admin/payroll`) — no POST/PUT/PATCH, no statutory_rule reference anywhere in this file.
- Every reference to `statutory_rule` across `backend/api/routes/` is a **read**: run-execution queries in `payroll.py` (lines 246-290, 624, 627, 863, 910, 972) and one existence check in `workspace.py:57`. No `INSERT INTO statutory_rule`/`tax_band` exists outside Alembic migrations.
- `docs/audit-program/03-configuration-integrity/findings.md:20` independently states statutory_rule is "Platform-seeded via migrations... Not directly UI-editable" — matches this stage's own re-verification exactly.

## Effective dating and duplicate-rule protection

- The `(country_code, effective_from)` UNIQUE constraint (Stage 01 F-01-45) remains the only protection against duplicate/conflicting rules, and it is DB-level, not validated pre-emptively by any application code (an attempted duplicate migration insert would fail at the DB layer, not be caught earlier with a helpful message).
- `tax_band` remains normalized with its own anti-duplication CHECK (Stage 01 F-01-46); pension/NHF/health/development-levy rates remain unstructured JSONB with silent Python-side defaults on missing keys — unchanged.

## Test coverage — re-verified

Over 20 test files insert `statutory_rule`/`tax_band` rows via raw SQL, but **every one is fixture setup for an unrelated payroll-run test**, not a test of statutory-rule administration itself (e.g. `test_payroll_pipeline_e2e.py`, `test_payroll_retry.py`, `test_payroll_reconciliation_e2e.py`, and 15+ others all `INSERT INTO statutory_rule` with a high `version` number "so this test wins ORDER BY version DESC," then tear down). The closest thing to an "effective-dating conflict" test is `test_payroll_retry_snapshot_first.py` (added by the 68e9307 remediation) — but it tests retry snapshot-vs-live divergence, not a UNIQUE-constraint violation, validation error, or preview/impact-analysis workflow.

**No test exercises**: (a) the UNIQUE constraint being violated and rejected gracefully, (b) `rules_jsonb` shape/required-key validation, (c) any preview-before-activate workflow — because none of these have corresponding application code to test.

## Deterministic platform capabilities that must exist before C11 proposals become actionable (C12's scope, per D-02-04)

1. **An application-level write path** for `statutory_rule`/`tax_band` — currently zero exists; every historical rate change has been a developer-authored migration.
2. **Pre-emptive duplicate/conflict validation** — surfacing a clear error before hitting the DB constraint, not after.
3. **A structured approval record** — who approved a given rate change, when, citing what source (this is also an audit-coverage item, see `audit-coverage-assessment.md`).
4. **Preview/impact analysis** — per the Stage 04 compliance-outcome-chain's step 4 (assess affected clients/runs), which this stage's investigation confirms has zero existing mechanism to build on — no code today computes "which workspaces/periods would this rate change affect" as a distinct capability.
5. **Test coverage for the above**, once built — currently absent because the capability is absent.

## Boundary note (per this stage's explicit scope)

Stage 06 owns the compliance-workflow design (approval process, who's authorized, evidence requirements). This stage's contribution is the technical-readiness fact: **none of the deterministic platform capability C12 requires exists today in any form** — this is a from-scratch build, not an extension of an existing admin surface. C11 (Compliance Monitoring) cannot be meaningfully sequenced ahead of this without producing proposals with nowhere to go, exactly as Stage 02/03 already identified (F-02-12).
