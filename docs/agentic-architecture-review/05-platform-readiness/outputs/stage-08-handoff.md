# Stage 05 → Stage 08 Handoff (Technical Architecture)

## Mechanism-design tasks this stage's evidence directly informs

1. **Dry-run mechanism (C14)** — good news: the calculation engine already has a clean, side-effect-free entry point (`run_sequential_payroll`/`execute_single_employee_payroll`, `backend/domain/payroll/executor.py`), proven reusable by an existing developer script (`backend/scripts/simulate_payroll.py`). Design the dry-run endpoint as a thin wrapper around this existing pure-compute path, not a new engine. Open question forwarded: does a dry run create a `payroll_run` row at all, or bypass the table entirely? (`onboarding-platform-readiness.md`)

2. **`component_trace_jsonb` null handling** — the HTTP/UI layer is already fixed (`payroll.py:1129`, `PayrollResults.tsx:686-690`). Stage 08 needs to independently add the same protection at the data-access layer (`payroll_result_repo.py:63`, `payroll_retry_service.py:418`) for any future tool that reads `payroll_result` directly, bypassing the HTTP route. (`tool-readiness-baseline.md`)

3. **Reconciliation causal-diff mechanism (C8, once unblocked)** — unchanged from Stage 03's forward — still needs deterministic diff computation with LLM narration only, once both D-02-02 and D-02-03 preconditions close.

4. **Auth mechanism (C1)** — needs full design: `operator` table schema, JWT issuance/verification, `get_current_operator` dependency. This is now confirmed as the literal first build item — nothing else in the portfolio has a viable path forward without it.

5. **Event/notification foundation (C2)** — needs full design: transactional outbox, 4 named events, consumer worker, `workspace_notification` table. `outputs/event-notification-readiness.md` has the exact minimum-viable-closure list.

6. **Exception data model** — a new table/mechanism, not previously named in any prior stage's technical design — needs schema design for issue creation, ownership, evidence links, resolution, closure (per Stage 04's 8-stage outcome definition).

7. **Statutory-rule change-management mechanism (C12)** — application-level write path, duplicate validation, approval record, preview/impact analysis, all from scratch. (`statutory-change-platform-readiness.md`)

8. **`load_inputs_for_run` and `workspace_info()`** — need workspace-parameter additions/audits before either could safely be wrapped by a tool. (`tool-readiness-baseline.md`)

## Design constraints carried forward, unchanged

- Every tool requires independent workspace-ownership verification (Stage 02 Principle 11) — reaffirmed with concrete new evidence in this stage.
- C7's calibration approach is decided (D-04-01) — design within that approved shape, do not re-open it. C7 is now additionally gated on the exception-resolution workflow existing (item 6 above), per D-04-01's binding condition.
- Decimal values in any LLM-visible context serialize as strings, never floats — unchanged project rule.

## What Stage 08 should NOT re-derive

Whether these gaps matter or what their remediation priority is — that's `readiness-closure-plan.md`'s job, already done. Stage 08 designs the mechanisms; it does not re-litigate whether they're needed.
