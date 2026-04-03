# Temporal Data Contract — Payroll Inputs

## 1. Definitions

* period_start (ps): start of payroll period
* period_end   (pe): end of payroll period
* reference_date (rd): when the input occurred
* payroll_run_id: null if unprocessed

---

## 2. Classification

Every input MUST be classified as:

* CURRENT: rd BETWEEN ps AND pe
* LATE:    rd < ps
* FUTURE:  rd > pe
* UNSCOPED: rd IS NULL

---

## 3. Inclusion Rules

An input is eligible for processing if:

* payroll_run_id IS NULL
  AND
* classification IN (CURRENT, LATE)

---
## 4. Input Cardinality Rule
Multiple inputs with the same input_code MUST be preserved as distinct entries.

The system MUST NOT:
- collapse inputs by input_code
- overwrite inputs during transformation
- aggregate inputs prior to calculation

Aggregation is only allowed AFTER:
- rate resolution
- per-entry calculation

---

## 5. Non-Dependencies

Inclusion logic MUST NOT depend on:

* existence of prior payroll runs
* payroll_run table joins
* payroll_run status

---

## 6. Idempotency

* Inputs must be processed exactly once
* Once processed → payroll_run_id is set
* Processed inputs must never be reselected

---

## 7. Adjustments

* Corrections must be new inputs (not edits)
* Adjustment runs must not reprocess prior inputs

---

## 8. Observability

System must expose:

* total inputs retrieved
* count by classification
* count applied in calculation
