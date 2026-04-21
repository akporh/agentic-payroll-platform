# S8 — Bulk Input Upload

**Actor:** Payroll Operator (Adaeze)
**Emotional state:** Efficient, wants to process a large list quickly

---

## Layout — Idle

```
┌────────────────────────────────────────────────────────────────────────────┐
│  ← Back to Inputs     Bulk Upload Payroll Inputs                          │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Upload a CSV or Excel file with variable payroll events.                  │
│                                                                            │
│  ┌─ Required columns ──────────────────────────────────────────────────┐  │
│  │  employee_number  ·  input_code  ·  quantity  ·  reference_date     │  │
│  │                                      [↓ Download template]          │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌─ Drop zone ─────────────────────────────────────────────────────────┐  │
│  │                                                                     │  │
│  │                                                                     │  │
│  │              [Icon: file/upload]                                    │  │
│  │                                                                     │  │
│  │         Drop your file here, or                                     │  │
│  │                  [Browse files]                                     │  │
│  │                                                                     │  │
│  │         Accepts .csv and .xlsx · Max 5MB                           │  │
│  │                                                                     │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  Valid input codes for this workspace:                                     │
│  OVERTIME, LEAVE_NOPAY, BONUS, TRANSPORT_CLAIM, SHIFT_ALLOWANCE           │
│  [View all codes →]                                                        │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Layout — Processing

```
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  ⟳  Processing overtime_march_2026.xlsx...                         │  │
│  │     Validating 234 rows                                             │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
```

---

## Layout — Result (All Success)

```
│  ┌─ ✓ Upload complete ─────────────────────────────────────────────────┐  │
│  │  234 inputs created successfully                                    │  │
│  │  0 errors                                                           │  │
│  │                                        [← Back to Input Inbox]     │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
```

---

## Layout — Result (Partial Errors)

```
│  ┌─ ⚠ Upload partially successful ────────────────────────────────────┐  │
│  │  218 inputs created successfully                                   │  │
│  │  16 rows had errors and were skipped                               │  │
│  │                                                                    │  │
│  │  [↓ Download error report]                                         │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  Errors                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ Row  Employee #    Input Code    Reason                             │  │
│  ├─────────────────────────────────────────────────────────────────────┤  │
│  │  3   EMP-045       OVERTIIME     Invalid input code "OVERTIIME"     │  │
│  │  7   EMP-099       OVERTIME      Employee number not found          │  │
│  │ 14   EMP-012       LEAVE_NOPAY   Quantity -3 is invalid (must be ≥0)│  │
│  │ 22   —             BONUS         Missing employee_number            │  │
│  │ ...  (12 more)                                                      │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  Fix the errors and re-upload, or continue with the inputs created.       │
│                                                                            │
│  [Upload Another File]            [← Back to Input Inbox]                 │
│                                                                            │
```

---

## Key UX Decisions

**Template download is prominent:** Adaeze shouldn't have to guess the column names. The template ensures the format is always correct.

**Valid codes shown on the upload screen:** Adaeze gets the file from her client's HR team. If the client used a wrong code, she needs to know what the correct ones are before uploading.

**Error table is scannable:** Row number, employee number, code, and plain-English reason. Not JSON. Not stack traces.

**Download error report:** For 16+ errors, scrolling a table is tedious. A downloadable CSV lets Adaeze fix errors in bulk and send the corrections back to the client.

**Partial success is not an error:** 218/234 inputs created is a success. Don't show a red error state for the whole upload — separate the success count from the error count clearly.
