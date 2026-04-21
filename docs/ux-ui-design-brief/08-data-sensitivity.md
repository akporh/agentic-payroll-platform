# Artefact 8 — Data Sensitivity Register

> Source: `backend/infra/db/models/` (field definitions), route SQL queries, export CSV column definitions.
> Sensitivity types: PII (personally identifiable), Financial (monetary amounts), Statutory (regulatory reference numbers).

---

## High Sensitivity — PII

These fields identify a specific individual. Exposure could enable identity theft, fraud, or breach of Nigerian data protection law (NDPR).

| Entity | Field | Sensitivity | Notes |
|---|---|---|---|
| employee | full_name | PII | Human name — must not appear in URL parameters or logs |
| employee | employee_number | PII | Internal identifier, but still maps to a specific person |
| employee.personal_details_encrypted | TIN | PII + Statutory | Tax Identification Number — required for PAYE filing; FIRS regulatory reference |
| employee.personal_details_encrypted | RSA | PII + Statutory | RSA Pin (Retirement Savings Account) — PFA regulatory reference |
| employee.personal_details_encrypted | BANK | PII + Financial | Bank name — links person to a financial institution |
| employee.personal_details_encrypted | ACCOUNT_NUMBER | PII + Financial | Bank account number — direct payment routing; highest sensitivity |
| payroll_reconciliation | resolved_by | PII | Name or identity of the operator who resolved the mismatch |
| audit_log | performed_by | PII | Identity of anyone who took an action — treat as PII |

**Notes on personal_details_encrypted:**
- The field name says "encrypted" but the codebase reads values directly as plaintext JSONB in CSV export routes (`biodata.get("BANK", "")`, etc.).
- **Either encryption is not implemented, or it is handled transparently at a DB layer not visible in the application code.** This is a critical ambiguity (see Drift Log).

---

## High Sensitivity — Financial

These fields represent actual monetary values. Unauthorised access could expose payroll liability, salary benchmarks, or enable fraud.

| Entity | Field | Sensitivity | Notes |
|---|---|---|---|
| payroll_run | total_gross_pay | Financial | Total employer payroll cost |
| payroll_run | total_deduction | Financial | Total statutory deductions |
| payroll_run | total_net_pay | Financial | Total disbursement amount |
| payroll_result | net_pay | Financial | Individual employee take-home pay |
| payroll_result | gross_components_jsonb | Financial | Per-component earning amounts for each employee |
| payroll_result | deductions_jsonb | Financial | Per-deduction amounts (PAYE, pension, NHF, etc.) |
| payroll_reconciliation | expected_total | Financial | Expected payment total |
| payroll_reconciliation | actual_total | Financial | Actual payment confirmed by bank |
| salary_definition | components_jsonb | Financial | Component amounts that define each salary grade — salary benchmarking data |
| statutory_rule | rules_jsonb | Financial | Tax bands, contribution rates — regulatory configuration |

---

## Medium Sensitivity — Statutory / Regulatory References

These are not individually sensitive but are required for regulatory filing and must be accurate.

| Entity | Field | Sensitivity | Notes |
|---|---|---|---|
| employee.personal_details_encrypted | TIN | Statutory | FIRS Tax Identification Number |
| employee.personal_details_encrypted | RSA | Statutory | PFA Retirement Savings Account pin |
| payroll_result | component_trace_jsonb | Statutory | Audit trail of calculation — required for dispute resolution and tax audit |
| statutory_rule | effective_from | Statutory | Date from which tax rules apply — temporal accuracy is legally significant |
| tax_band | rate | Statutory | Tax rates — must match FIRS published rates |
| payroll_run | period_start / period_end | Statutory | Defines the tax period — used in PAYE and pension filings |

---

## Sensitivity in Exports (CSV Files)

These CSVs contain a concentration of sensitive fields and must be treated accordingly.

| Export | Sensitive Columns |
|---|---|
| Bank Upload CSV | employee_number, employee_name, bank_name, account_number, net_pay |
| PAYE Remittance CSV | employee_number, employee_name, TIN, gross_pay, paye_withheld |
| Pension Contribution CSV | employee_number, employee_name, RSA pin, basic_pay, employee_contribution, employer_contribution |

**Recommendation for UI:** These downloads should require explicit confirmation action. Consider adding download logging (who downloaded, when) to the audit trail.

---

## Sensitivity in Transit

| Category | Note |
|---|---|
| All API responses | All routes are HTTP — if the platform is not behind HTTPS termination, all data is exposed in transit. Not determinable from code. |
| personal_details_encrypted | Ambiguity noted above — treatment in UI should assume field contains plaintext PII until confirmed otherwise. |

---

## Fields That Must Not Appear in URLs or Logs

| Field | Reason |
|---|---|
| employee_number | Maps to an individual |
| TIN | Regulatory identifier |
| RSA | Regulatory identifier |
| ACCOUNT_NUMBER | Bank account — financial fraud risk |
| payroll_run_id | In URLs (acceptable as UUID, low risk), but must not appear in public-facing URLs |
