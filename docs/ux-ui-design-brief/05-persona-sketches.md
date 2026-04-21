# Artefact 5 — Persona Sketches

> Built on Actor List (Artefact 4). Where actor identity is inferred from domain knowledge,
> this is flagged explicitly.

---

## Persona 1 — Chidi, Bureau Administrator

**Who:** Chidi runs a mid-sized payroll bureau in Lagos that manages payroll for 15–25 client companies. He is technically competent — comfortable with spreadsheets, SQL-lite tools, and web apps — but he is not a developer. He oversees the bureau's operations and is the one who onboards new clients onto the platform.

**What he's trying to achieve:** Chidi wants a clear at-a-glance view of every client workspace: which ones are live, which have runs pending approval, and whether any reconciliations are outstanding. When a new client signs up, he wants to get their workspace created and populated quickly — ideally by uploading the client's existing Excel staff list rather than entering everything manually.

**How often:** Daily during payroll season (last week of month); lighter touch mid-month. Onboarding work is episodic — a few times per quarter when new clients join.

**What would frustrate him:**
- Having to click through multiple screens to see the state of all clients simultaneously.
- An onboarding process that fails silently or gives cryptic errors when an Excel upload has a bad row.
- No way to tell which workspaces are "stuck" (e.g. CALCULATING for too long, reconciliation MISMATCH unresolved).
- Having to re-enter data that was already in the uploaded file.

---

## Persona 2 — Adaeze, Payroll Operator

**Who:** Adaeze is a payroll officer at the bureau. She manages 3–5 client accounts and runs their payroll each month. She knows Nigerian payroll rules well (PAYE, pension, NHF) but doesn't think of herself as a finance person — she's focused on getting the numbers right and the run completed on time. She works from the office most days.

**What she's trying to achieve:** Each month, Adaeze needs to collect variable inputs from HR contacts at each client company (overtime, leave without pay, bonuses), enter them into the system, trigger the payroll run, check for failed employees, fix any issues, and hand off to the finance team for approval. She wants to trust the system's numbers but also be able to explain to a client why an employee's pay changed.

**How often:** Heavily at month-end — she may run 5–8 payrolls in a 3-day window. Inputs trickle in across the month.

**What would frustrate her:**
- The run failing with a cryptic error that doesn't tell her which employee or rule caused the problem.
- Having to switch between the system and a spreadsheet to track which inputs she has and hasn't entered.
- No way to see a component-level breakdown of an employee's pay to explain it to the client.
- Being unable to bulk-upload inputs — entering them one by one for 200 employees is not viable.
- Partial run failures (PARTIAL status) not clearly showing which employees failed and why.

---

## Persona 3 — Emeka, Finance Authoriser

**Who:** Emeka is the Finance Manager at the bureau. He is the final sign-off authority on every payroll before it goes to the bank. He is detail-oriented, risk-averse about money, and treats every payment as a liability until reconciled. He has moderate technical skill — comfortable with Excel and web portals but does not enjoy learning new UIs.

**What he's trying to achieve:** Emeka wants to review the payroll totals, confirm they match the expected figures from the client, lock the run, approve the bank transfer, and then reconcile the actual payment after the bank confirms. He needs a clear audit trail — who approved what, when, and for how much.

**How often:** Concentrated at month-end. He reviews and locks 10–20 runs in a 2–3 day window, then follows up on reconciliation over the next few days as bank confirmations come in.

**What would frustrate him:**
- Not being able to download the bank upload CSV until a run is in exactly the right status.
- Having to hunt for the reconciliation mismatch detail — he needs to see expected vs actual and the variance immediately.
- A MISMATCH record with no clear path to resolve it (no form, no guidance).
- Being asked to mark a run as PAID before the bank has actually confirmed — the UI should not rush this.
- No audit trail showing who approved what and when.

---

## Persona 4 — Ngozi, HR / Onboarding Administrator

**Who:** Ngozi is the HR lead at a client company (not at the bureau). She works closely with Adaeze to make sure employee records are up to date and contract changes are reflected in payroll on time. She is not a payroll expert — she knows HR and headcount but defers to Adaeze on calculations. She uses the system intermittently.

**What she's trying to achieve:** Ngozi needs to see the employee list, update grades and designations when promotions happen, and correct contract dates when people join or leave. She does not need to see pay figures — she wants to manage the structural data (who is employed, on what grade, from what date).

**How often:** A few times a month, usually when onboarding a new hire or processing a promotion.

**What would frustrate her:**
- Having to update employees one by one — bulk updates for a restructuring event need to be fast.
- The system not clearly telling her which employees have incomplete records that would block payroll.
- Mixing the employee management UI with payroll execution controls — these are different jobs.

---

## Persona 5 — Tunde, Compliance Officer (inferred)

**Who:** Tunde works in the tax and compliance function at the bureau. After payroll runs are locked, he downloads the PAYE remittance and pension contribution CSVs and files them with the relevant regulatory bodies (FIRS for PAYE, PFAs for pension). He cares about TINs and RSA pins being correct.

**How often:** Once per month per client, concentrated in the first 3–5 days after payroll is locked.

**What would frustrate him:**
- A downloaded CSV with blank TINs or RSA pins (data quality problem at the employee record level).
- Not being able to filter or search through runs to find the one he needs.
- Having to re-download a file he already downloaded because the format changed.
- No indication of which employees had FAILED results and were therefore excluded from the export.
