# Artefact 10 — Integration Touchpoints

> Source: CSV export routes, onboarding pipeline, external dependency analysis.
> "Integration" here means any point where the UI must interact with an external system,
> handle a file format from outside the platform, or produce output consumed outside the platform.

---

## INT-1 — Bank Upload CSV (Outbound)

**Trigger:** Finance Authoriser downloads from a LOCKED or PAID run.
**Format:** CSV with columns: employee_number, employee_name, bank_name, account_number, net_pay.
**Destination:** Nigerian commercial bank payment portal or bulk payment system (external — not specified in code).
**UI responsibility:**
- Provide download button (available only in LOCKED or PAID status).
- Filename: `bank_upload_{run_id[:8]}.csv`.
- No transformation in the UI — download is a direct file stream from the backend.

**Data quality risk:** If `BANK` or `ACCOUNT_NUMBER` is missing from `personal_details_encrypted`, the CSV row will have blank columns. The UI should warn if employee records have incomplete bank details before the run is locked.

---

## INT-2 — PAYE Remittance CSV (Outbound)

**Trigger:** Compliance Officer downloads from a LOCKED or PAID run.
**Format:** CSV with columns: employee_number, employee_name, tin, gross_pay, paye_withheld, period.
**Destination:** Federal Inland Revenue Service (FIRS) e-filing portal (external).
**UI responsibility:**
- Provide download button.
- Filename: `paye_remittance_{run_id[:8]}.csv`.
- Note to user: employees with FAILED results are excluded from this file.

**Data quality risk:** Blank TIN values will produce a non-compliant submission. The UI should surface a warning if any active employees have no TIN in their personal details.

---

## INT-3 — Pension Contribution CSV (Outbound)

**Trigger:** Compliance Officer downloads from a LOCKED or PAID run.
**Format:** CSV with columns: employee_number, employee_name, rsa_pin, basic_pay, pension_base, employee_contribution, employer_contribution, period.
**Destination:** Pension Fund Administrator (PFA) portal (external).
**UI responsibility:**
- Provide download button.
- Filename: `pension_contribution_{run_id[:8]}.csv`.
- Note to user: employees with FAILED results are excluded.

**Data quality risk:** Blank RSA pin values will produce a non-compliant submission.

---

## INT-4 — Excel Bulk Input Upload (Inbound)

**Trigger:** Payroll Operator uses the Bulk Upload screen.
**Format:** Expected columns: employee_number, input_code, quantity, reference_date.
**Source:** Client company HR team typically prepares this spreadsheet (external).
**UI responsibility:**
- File drop zone or file picker.
- Template download button (if the backend supports it — not confirmed in code; currently unknown).
- Display upload result: success count and per-row errors with reason.
- Validate file structure client-side before upload where possible.

---

## INT-5 — JSON Onboarding Upload (Inbound)

**Trigger:** Bureau Admin uses JsonOnboarding screen.
**Format:** Structured JSON payload containing employees, salary definitions, payroll rules, grades, designations.
**Source:** May be generated from an Excel-to-JSON conversion tool (external — not in this codebase).
**UI responsibility:**
- JSON editor or file upload.
- Preview validation (O2 endpoint) — show errors and warnings before commit.
- Commit action (O3 endpoint).

---

## INT-6 — National Public Holiday Calendar (Platform-Managed, Read-Only)

**Source:** `national_public_holiday` table — populated by platform administrators via migrations.
**UI responsibility:**
- Display national holidays as read-only in the public holiday calendar screen.
- No write path for national holidays from the workspace UI.
- The platform currently supports Nigeria (country_code = "NG"). Other countries would require separate statutory rule and PH configuration — no multi-country workspace UI is evident.

---

## INT-7 — Nigerian Statutory Rules (Platform Configuration, Not User-Editable)

**Source:** `statutory_rule` and `tax_band` tables — seeded by platform migrations.
**UI responsibility:**
- The workspace config screen can show which statutory rule is currently active (effective_from date, version).
- Users cannot edit statutory rules — this is platform-level configuration.
- If no statutory rule exists for the country, the run will fail. The UI must surface this as a clear configuration error with admin escalation path.

---

## INT-8 — Bank Reconciliation Confirmation (Inbound, Manual)

**Source:** The bank sends a confirmation of total disbursement (value only — no automated API connection in the current codebase).
**UI responsibility:**
- Finance Authoriser manually enters the confirmed amount in the Reconciliation screen.
- No automated bank API integration is present. The UI must make manual entry clear and prominent.

---

## INT-9 — Idempotency Key (Client-Controlled Header)

**Source:** API clients (including the frontend) may supply an `Idempotency-Key` header when submitting a run.
**UI responsibility:**
- The current frontend likely generates or omits this. If the UI implements a "re-submit" or "refresh" after a failed response, it should include the same idempotency key to avoid duplicate runs.
- If the server returns `"idempotent": true` in the response, the UI should recognise this and not treat it as an error.

---

## Summary: What the UI Must Produce or Consume

| # | Direction | Format | System | User action required |
|---|---|---|---|---|
| INT-1 | Outbound | CSV | Bank payment portal | Download button click |
| INT-2 | Outbound | CSV | FIRS e-filing portal | Download button click |
| INT-3 | Outbound | CSV | PFA pension portal | Download button click |
| INT-4 | Inbound | Excel/CSV | Client HR team | File upload |
| INT-5 | Inbound | JSON | Conversion tool / manual | File upload or paste |
| INT-6 | Read-only | DB table | Platform admin | None (display only) |
| INT-7 | Read-only | DB table | Platform admin | None (display only) |
| INT-8 | Inbound | Manual text entry | Bank confirmation | Manual number entry |
| INT-9 | Header | HTTP header | API client | Transparent (frontend logic) |
