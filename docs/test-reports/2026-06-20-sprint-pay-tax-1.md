# Sprint PAY-TAX-1 Test Report — 2026-06-20

## Summary
| Metric | Value |
|---|---|
| Sprint | PAY-TAX-1 — Fix NG PAYE Bands (Nigeria Tax Act 2025) |
| Date | 2026-06-20 |
| Test suite | 78 passed, 1 failed (pre-existing re-break, not caused by this sprint) |
| LIVE checks | 3 (migration apply, downgrade, re-upgrade) |
| STATIC checks | 4 (unit tests, DB state verification, data integrity) |
| BLOCKED checks | 0 |
| Overall verdict | **PASS** — sprint changes verified correct; 1 pre-existing failure documented |

---

## Environment
- Alembic head: `de1f2a3b4c5d` (new migration applied clean)
- DB: `payroll_dev` on localhost:5432
- Backend: not started (API-to-frontend boundary not touched — skip per CLAUDE.md)

---

## Sprint Items Verified

### PAY-TAX-1 — Migration: correct NG PAYE bands to NTA 2025 schedule

| Check | Type | Result |
|---|---|---|
| Migration applies clean to head | LIVE | PASS — `alembic upgrade head` ran without error |
| Downgrade restores old PITA bands (7/11/15/19/21/24%) | LIVE | PASS — 6 old bands verified in DB after `alembic downgrade -1` |
| Re-upgrade restores NTA 2025 bands (0/15/18/21/23/25%) | LIVE | PASS — 6 correct bands verified in DB after `alembic upgrade head` |
| DB has exactly 6 bands for NG / 2026-01-01 | LIVE | PASS |
| Band 1: ₦0–₦800k @ 0% | LIVE | PASS |
| Band 2: ₦800k–₦3M @ 15% | LIVE | PASS |
| Band 3: ₦3M–₦12M @ 18% | LIVE | PASS |
| Band 4: ₦12M–₦25M @ 21% | LIVE | PASS |
| Band 5: ₦25M–₦50M @ 23% | LIVE | PASS |
| Band 6: ₦50M+ @ 25% | LIVE | PASS |

### PAY-TAX-1 — Unit tests: NTA 2025 band boundary verification

| Check | Type | Result |
|---|---|---|
| `test_nta2025_within_free_band`: ₦500k → ₦0 | STATIC PASS | All assertions verified |
| `test_nta2025_at_800k_boundary`: ₦800k → ₦0 | STATIC PASS | ✓ |
| `test_nta2025_at_3m_boundary`: ₦3M → ₦330,000 | STATIC PASS | ✓ |
| `test_nta2025_at_12m_boundary`: ₦12M → ₦1,950,000 | STATIC PASS | ✓ |
| `test_nta2025_at_25m_boundary`: ₦25M → ₦4,680,000 | STATIC PASS | ✓ |
| `test_nta2025_at_50m_boundary`: ₦50M → ₦10,430,000 | STATIC PASS | ✓ |
| All 7 pre-existing algorithm tests still pass | STATIC PASS | ✓ |

---

## Data Integrity Spot-Check

| Check | Result |
|---|---|
| `payroll_result` rows with `net_pay IS NULL` | 0 ✓ |
| `payroll_result` rows with `component_trace_jsonb IS NULL AND status='SUCCESS'` | 20 — pre-existing (legacy executor path, not sequential executor) |
| Duplicate `statutory_rule (country_code, effective_from)` | 0 ✓ |
| Multiple active pay cycles per workspace | 0 ✓ |

---

## Regression Suite

```
78 passed, 1 failed in 3.07s
FAILED tests/test_payroll_lock_and_approval.py::test_payroll_approval_and_lock_e2e
```

**All 78 other tests pass.** The 1 failure is documented below.

---

## Known Pre-Existing Issues

### TF-7: `test_payroll_approval_and_lock_e2e`
- **Root cause:** `assert body["status"] == "success"` fails; API returns `"DRAFT"` (the run's status field, not a success envelope). This is NOT caused by the PAYE band change — the assertion is about API response shape, not PAYE values.
- **Pre-existing confirmation:** Failure reproduced on `git stash` (old code, same DB state). Not introduced by this sprint.
- **Likely cause:** Background-task / bulk-insert performance changes in Sprints 31–32 altered the response timing or shape.
- **Status:** Logged as TF-7 in ROADMAP.md Known Test Failures table.
- **Fix needed:** Separate story — update test assertion to match current API response schema.

### 20 NULL `component_trace_jsonb` on SUCCESS rows
- Pre-existing. These rows were produced by the legacy executor path (before sequential executor migration). Not a regression.

---

## Deferred

- **AC-1 (PAYE on live results page):** Verified at DB level only. Live end-to-end browser test deferred — backend API-to-frontend boundary not modified by this sprint. To confirm visually, run a payroll through the UI and compare PAYE column against the client Excel.
- **Retry determinism gap (Auditor Finding 1):** Retry service reads tax bands live from DB rather than from snapshot. This pre-existing design gap is now material post-band-change. Logged for a future story — retry PAYE will use new (correct) bands even for runs that were calculated under old bands. Intentional for this defect fix.

---

## Sign-off
Verified by: Claude Code (automated) — 2026-06-20
Sprint PAY-TAX-1 changes: **PASS**
