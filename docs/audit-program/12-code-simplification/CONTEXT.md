# Stage 12 — Code Simplification

**Status:** in-progress (see [`../audit-state.md`](../audit-state.md))

## Purpose

Identify code, schema, route, repository, migration, trace, and documentation structures that can be safely removed, consolidated, renamed, or made single-source without changing intended payroll behaviour.

This is a read-only audit/design stage. Do not perform cleanup.

## Confirmed handoff state

- Stages 01–11 are complete.
- `04-001` and `05-001` are remediated and regression-protected.
- Stage 11 baseline: 306 passed, 1 skipped.
- Stage 09 authentication, membership, RBAC, and ownership controls remain unimplemented S0 blockers.
- Stage 10 trace remediation design is approved but unimplemented.
- `06-007` / `09-002` legacy unscoped reconciliation routes are reachable, insecure, superseded, and have no callers found.
- `07-004` is the stray module-scope `print()` cleanup.
- Stage 05 simplification handoffs remain: `05-002`, `05-003`, `05-005`.
- `03-004` remains an open product-policy question.
- `05-004` remains a Stage 13 immutability remediation item, not simple cleanup.
- `CLAUDE.md` is authoritative.

## Required investigation

At minimum produce evidence-backed recommendations for:

1. Simplification candidate inventory.
2. Repository-layer duplication (`backend/infra/repositories/` vs `backend/infra/db/repositories/`).
3. Legacy executor fallback disposition.
4. Snapshot dead fields and duplicated extraction logic.
5. Legacy/superseded route removal.
6. Trace literal/event-code consolidation.
7. Backend/frontend enum and contract duplication.
8. Duplicate business-rule/helper logic.
9. Frontend dead code and contract drift.
10. Logging/debug/diagnostic cleanup.
11. Migration hygiene.
12. Documentation authority/staleness.
13. Dependency-aware cleanup sequencing.

## Finding rules

Use exactly one valid status:

- confirmed
- plausible
- unconfirmed
- rejected
- human decision required

Do not call code dead solely because the frontend has no caller. Verify routes, scripts, tests, compatibility, and historical replay needs.

Do not remove security-sensitive routes without a secure replacement or explicit retirement plan.

Do not merge code paths with materially different transaction, snapshot, or lifecycle semantics.

## Constraints

- Read-only audit/design stage.
- Do not modify backend/frontend code, migrations, tests, scripts, routes, tables, columns, docs, or evidence.
- Do not begin Stage 13.
- Do not reopen `04-001` or `05-001` without regression evidence.
- Do not resolve `03-004` without an explicit human decision.

---

## Close-review instruction

Use this section after the initial Stage 12 findings have been committed and presented for review.

### Human decision: legacy executor fallback

Resolve `01-004` and the Stage 12 legacy-executor decision as follows:

- Choose **migrate legacy configuration, then remove the fallback for new payroll runs**.
- This is a phased disposition, not an immediate hard-fail:
  1. retain the fallback temporarily;
  2. add explicit telemetry using the Stage 10 stable event-code design;
  3. inventory every environment/workspace that reaches the fallback;
  4. classify each occurrence as missing seed/configuration, deliberately disabled metadata, or legitimate historical dependency;
  5. migrate/repair configuration for every active workspace;
  6. prove new-run fallback usage is zero over an agreed observation window;
  7. change new payroll runs to hard-fail on empty active component metadata with an actionable configuration error;
  8. remove the default fallback path after verification.
- Historical replay support must not keep the fallback active for new runs. If a genuine historical-replay requirement is confirmed, isolate it behind an explicit replay-only path or compatibility mode with clear telemetry and no use by normal run creation.

Rationale:

- Immediate hard-fail is unsafe because actual production dependency is unknown.
- Permanent retain-and-telemetry leaves a silent-degradation path in place indefinitely and continues masking invalid configuration.
- Replay-only is not currently implementable because no replay/new-run distinction exists.
- Migration-then-removal provides the cleanest target state while allowing dependency discovery and controlled transition.

### Required legacy-fallback handoff for Stage 13

Record the following acceptance criteria:

1. The misleading `old CLI callers` comment is corrected immediately.
2. Fallback invocations use a stable event code and include workspace/run/country context.
3. A production-environment inventory is completed before behaviour changes.
4. Every active workspace has non-empty effective component metadata after migration.
5. Automated tests cover:
   - correctly configured workspace uses the sequential executor;
   - empty metadata produces an actionable hard failure for new runs after cutover;
   - historical replay compatibility, only if explicitly retained;
   - fallback telemetry during the transition period.
6. Removal/hard-fail cutover has a rollback plan.
7. No claim of removal is made from dev-database percentages alone.

### Review conclusions to preserve

Accept the Stage 12 findings as follows:

- Repository layers are intentionally distinct; rename/document the ORM onboarding-readiness layer rather than merge it.
- `employee_contract_snapshot.components_jsonb` is a safe dead-column removal candidate.
- `payroll_result.salary_inputs_snapshot` is retained intentionally.
- Statutory-rate extraction should become one shared pure helper.
- Remove the stray `paye.py` module-level `print()`.
- Rename/manual-label the six `backend/scripts/test_*.py` utilities rather than silently delete them.
- The legacy unscoped reconciliation GET/POST pair is a removal quick-win after a final undocumented-external-integration check.
- Unscoped retry/approve/lock/pay routes and admin/diagnostic surfaces require security redesign, not deletion.
- Frontend `PayrollRunStatus` duplication/drift is confirmed and should be fixed with `06-001`/`06-004`.
- Error-to-HTTP consolidation belongs with `07-001` remediation.
- Trace literal consolidation belongs with Stage 10 implementation.
- Migration comment/docstring cleanup belongs with `08-001` remediation.
- `03-004` remains open and unchanged.

### Close the stage

Update:

- `docs/audit-program/12-code-simplification/findings.md`
  - change status to `complete`;
  - replace the legacy-fallback `human decision required` status with the phased migrate-then-remove decision;
  - record the transition and acceptance criteria above;
  - add a final closure summary.
- `docs/audit-program/_core/human-decisions.md`
  - record the legacy executor fallback decision as resolved.
- `docs/audit-program/audit-state.md`
  - mark Stage 12 `complete`;
  - set the closed date to today;
  - set next action to open Stage 13 — Consolidated remediation backlog;
  - leave Stage 13 not started;
  - carry all independently safe cleanup items, bundled cleanup items, blocked items, retained items, and the phased legacy-fallback programme into Stage 13;
  - preserve all prior completed stages, decisions, findings, and remediation records.

### Constraints during close review

- Do not modify application code, migrations, tests, scripts, routes, schema, or data.
- Do not implement fallback telemetry or migration.
- Do not begin Stage 13.
- Do not create a separate close-review prompt file.

### Publish

Commit and push Stage 12 closure documentation to `uat`.

Return only:

```text
Stage: 12 — Code simplification
Status: complete
Primary file: docs/audit-program/12-code-simplification/findings.md
Audit state: docs/audit-program/audit-state.md
Commit: <SHA>

Decision:
- Legacy executor fallback: retain temporarily with telemetry, inventory and migrate active workspace configuration, then hard-fail/remove for new runs. Preserve replay-only compatibility only if a real historical-replay requirement is proven.

Next stage:
13 — Consolidated remediation backlog
```
