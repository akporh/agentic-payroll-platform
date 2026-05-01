# Sprint 9 — Full Payroll Detail Export

**Sprint goal:** Give operators a complete, downloadable breakdown of every employee's payroll calculation — available immediately after the run completes, before the approval/lock workflow.

**Arch-council:** Not required. No new migrations, status fields, enum changes, or data contract modifications. New read-only endpoint on existing `payroll_result` data.

---

## Story Index

| Story | Summary | Priority | Effort |
|-------|---------|----------|--------|
| S9-1 | Full Detail CSV export endpoint (H4) | P1 | M |
| S9-2 | Full Detail download button in PayrollResults UI | P2 | S |

---

## S9-1 — Full Detail CSV Export Endpoint

**As a** payroll operator,
**I want to** download a CSV showing every employee's full component breakdown immediately after a payroll run completes,
**So that** I can review, audit, or cross-post individual line items before committing to approval or lock.

**Acceptance Criteria:**

- **Happy path:** `GET /{workspace_id}/payroll/runs/{run_id}/exports/full-detail` on a CALCULATED, APPROVED, LOCKED, or PAID run returns a CSV with one row per employee result with `status = 'SUCCESS'`.
- **Column order:** `employee_number`, `employee_name`, `period`, then one column per component code (in execution trace order, union of all employees), then `gross_pay`, `total_deductions`, `net_pay`.
- **Dynamic columns:** Component codes are discovered from `component_trace_jsonb`. The `_period_context` sentinel entry is excluded from columns and data. Employees missing a component get an empty cell (not an error).
- **Monetary formatting:** All monetary values formatted to 2 decimal places (`f"{v:.2f}"`).
- **Filename:** `full_detail_{run_id[:8]}.csv`.
- **Guard (too early):** DRAFT or CALCULATING run → HTTP 409 with message `"Export available from CALCULATED status. Current status: {status}"`.
- **Guard (not found):** Unknown `run_id` or wrong `workspace_id` → HTTP 404.
- **Guard (no results):** Run with zero SUCCESS employee results → returns a header-only CSV (no error).
- **Legacy path:** Employees calculated via legacy executor (`component_trace_jsonb = NULL`) → dynamic component columns are empty; gross_pay, total_deductions, net_pay still populated from their JSON columns.

**Out of scope:**
- Excel/XLSX format.
- Filtering by employee or component.
- Exposing `_period_context` fields (annualisation factor, period fraction) as columns.

**Business risk:**
- **Cost of NOT building:** Operators have no complete audit view between calculation and lock. Any discrepancy can only be caught by clicking into individual employee records.
- **Cost of doing wrong:** Incorrect column alignment (mismatched employee ↔ component values) would corrupt audit records. The two-pass design (discover columns first, then write rows) prevents this.

**Priority:** P1 — directly unblocks operator review and reconciliation before approval.

---

## S9-2 — Full Detail Download Button in PayrollResults UI

**As a** payroll operator,
**I want to** see a "Full Detail" download button as soon as a payroll run reaches CALCULATED status,
**So that** I can immediately pull the full breakdown without waiting for the run to be locked.

**Acceptance Criteria:**

- **Visibility:** "Full Detail" button appears in the Downloads bar when run status is CALCULATED, APPROVED, LOCKED, or PAID.
- **Position:** "Full Detail" is the first button in the Downloads bar — before Bank Upload, PAYE Remittance, and Pension.
- **Remittance files still gated:** Bank Upload, PAYE Remittance, and Pension buttons only appear when status is LOCKED or PAID (unchanged from Sprint 8).
- **Loading state:** Button shows a spinner while the download is in flight; other buttons remain active.
- **Error handling:** On HTTP error, toast shows the error message.
- **TypeScript:** `npx tsc --noEmit` passes with no errors.

**Out of scope:**
- Showing individual component values inline in the UI table.
- A preview/modal before download.

**Business risk:**
- **Cost of NOT building:** Operator must call the API directly to get the full detail — no discoverability.

**Priority:** P2 — UI surface for the P1 backend capability.

---

## Open Items Carried From Sprint 8

These are not Sprint 9 stories but must be resolved before Sprint 9 is closed:

| Item | File | Fix |
|------|------|-----|
| ITEM 1 | `frontend/src/pages/WorkspaceConfig.tsx` L1657–1658 | Replace `?? ''` with `?? 'LEAVE_ABSORBS_PH'` and `?? 'ABSENT_IS_DEDUCTIBLE'` |
| ITEM 2 | `backend/domain/payroll/` | Verify `PH_ADDITIVE` has an engine handler; remove from dropdown if not |

Arch-council re-run also outstanding (hit rate limit end of Sprint 8 session).
