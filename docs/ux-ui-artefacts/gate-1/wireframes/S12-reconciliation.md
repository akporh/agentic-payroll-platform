# S12 — Reconciliation

**Actor:** Finance Authoriser (Emeka)
**Emotional state:** Detail-oriented, risk-averse. Any mismatch is a problem. Clear numbers and audit trail matter more than anything.

---

## Layout — No Reconciliation Yet (run is LOCKED)

```
┌────────────────────────────────────────────────────────────────────────────┐
│  March 2026 Payroll    [LOCKED] 🔒            [Results] [Reconciliation●] │
│                                              [Timeline]  [Audit Log]       │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Payment Reconciliation                                                    │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │  Expected payment                                                    │ │
│  │  ₦ 18,432,000.00                                                    │ │
│  │  (Total net pay from payroll engine)                                 │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│  ─────────────────────────────────────────────────────────────────────    │
│                                                                            │
│  Enter actual amount received from bank                                    │
│                                                                            │
│  ┌───────────────────────────────────────────┐                            │
│  │ ₦  [ 18,432,000.00                    ]   │                            │
│  └───────────────────────────────────────────┘                            │
│                                                                            │
│  ℹ Enter the total amount your bank confirms was disbursed.               │
│    This will be compared against the expected total above.                 │
│                                                                            │
│                              [Submit Reconciliation →]                     │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## State — MATCHED

```
│  Payment Reconciliation                                                    │
│                                                                            │
│  ┌─ ✓ MATCHED ─────────────────────────────────────────────────────────┐ │
│  │                                                                     │ │
│  │  Expected    ₦ 18,432,000.00                                        │ │
│  │  Actual      ₦ 18,432,000.00                                        │ │
│  │  Variance    ₦ 0.00                                                 │ │
│  │                                                                     │ │
│  │  Reconciled on 15 Apr 2026 at 09:47                                 │ │
│  │                                                                     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│  ✓ No further action required.                                            │
│    You may now mark this run as paid.                                      │
│                                    [→ Back to Results / Mark as Paid]     │
```

---

## State — MISMATCH

```
│  Payment Reconciliation                                                    │
│                                                                            │
│  ┌─ ⚠ MISMATCH ────────────────────────────────────────────────────────┐ │
│  │                                                                     │ │
│  │  Expected    ₦ 18,432,000.00                                        │ │
│  │  Actual      ₦ 18,390,000.00                                        │ │
│  │  Variance    – ₦ 42,000.00                                          │ │
│  │  (Actual is less than expected)                                     │ │
│  │                                                                     │ │
│  │  Submitted on 15 Apr 2026 at 09:47                                  │ │
│  │                                                                     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│  Resolve this mismatch                                                     │
│                                                                            │
│  This run cannot be marked as paid until the mismatch is resolved.        │
│                                                                            │
│  Explanation *                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ e.g. "Two employees' salaries were adjusted post-disbursement."     │ │
│  │                                                                     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│  Resolved by *                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ Your name or identifier                                             │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│                                  [Mark as Resolved →]                     │
│                                                                            │
```

---

## State — RESOLVED

```
│  ┌─ ✓ RESOLVED ────────────────────────────────────────────────────────┐ │
│  │                                                                     │ │
│  │  Expected    ₦ 18,432,000.00                                        │ │
│  │  Actual      ₦ 18,390,000.00                                        │ │
│  │  Variance    – ₦ 42,000.00                                          │ │
│  │                                                                     │ │
│  │  Resolved by  Emeka Obi                                             │ │
│  │  Resolved on  15 Apr 2026 at 11:23                                  │ │
│  │  Notes        Two employees' salaries were adjusted post-           │ │
│  │               disbursement per client instruction.                  │ │
│  │                                                                     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│  Mismatch resolved. You may now mark this run as paid.                    │
│                                    [→ Back to Results / Mark as Paid]     │
```

---

## State — Run Not LOCKED

```
│  ┌─ ○ Not yet available ────────────────────────────────────────────────┐ │
│  │                                                                     │ │
│  │  Reconciliation becomes available once this run is locked.          │ │
│  │  Current status: APPROVED                                           │ │
│  │                                                                     │ │
│  │  To reconcile: Lock the run first, then return here.               │ │
│  │                                    [→ Back to Results]              │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
```

---

## Key UX Decisions

**Expected total is the anchor:** Emeka's job is to confirm the bank disbursed the right amount. Show the expected total prominently and first — it's his reference point.

**Variance displayed prominently in MISMATCH:** Don't make Emeka calculate the difference himself. Show it immediately, with a sign (+ or –) and plain English ("Actual is less than expected").

**Resolution form is inline, not a separate page:** Emeka shouldn't need to navigate away to resolve a mismatch. The form appears in place below the mismatch summary.

**Both resolution fields are marked required:** The API returns 400 if either is missing. Pre-validate client-side to avoid a round trip.

**MATCHED = nothing more to do:** Show a clear completion state. Don't leave Emeka wondering if he needs to do something else.

**No re-submission form after first submission:** Once reconciliation exists (any status), the submit form is gone. Show the reconciliation result instead. Only the resolution form appears when status is MISMATCH.
