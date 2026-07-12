# Stage 03 → Stage 05 Handoff (Platform Readiness)

## Named preconditions this stage confirmed block specific capabilities

1. **`payroll_reconciliation` repository-level workspace scoping (F-01-33)** — a named precondition for C8 (Reconciliation Investigation) and the `get_reconciliation` tool. Per D-02-02, this is mandatory; tool-layer verification is required *in addition*, not instead. See `outputs/blocked-and-deferred-register.md`.

2. **Historical reproducibility (F-01-27, F-01-29, F-01-38)** — a named launch precondition for C4 (Historical Payroll Explanation) and part of C8's blocker. Per D-02-03, this is not to be treated as an accepted residual risk. Please scope the closure of these three findings as an actual readiness item, not a background risk note.

3. **Statutory-rule change-management mechanism (C12, new capability, F-01-45/46)** — currently, the platform has no operator-facing path to apply a statutory-rule change at all (migration-only). This is a readiness gap independent of any AI capability — please assess what it takes to build C12 as a deterministic platform capability.

## Platform-trustworthiness areas from Stage 02 not yet fully assessed at readiness level

Carried forward from Stage 02's `stage-03-handoff.md` (now also relevant to Stage 05): parallel configuration entry points, silent employee exclusion (F-01-14/19/20), sequential/legacy executor divergence (F-01-24/28), snapshot completeness (F-01-26), retry behaviour (F-01-30-32), audit coverage (F-01-40), frontend/backend mismatches (F-01-31, F-01-43) — all previously confirmed Stage 01 findings, relevant to a full readiness review.

## New readiness dependency identified in this stage

- **Dry-run payroll mechanism (C14)** — undefined mechanically. Before C13/C14 can be considered launch-ready, Stage 05 (in coordination with Stage 08) should confirm what "dry-run" means: does it exercise the real sequential executor/snapshot machinery, or a separate simulation path? An unverified safety gate is not a safety gate (Stage 02 F-02-10).

## What Stage 05 should NOT re-derive

The specific capability-level blocking logic (which capability is blocked by which finding) — that's in `outputs/blocked-and-deferred-register.md`. Stage 05's job is to actually assess/close the underlying platform gaps, not re-decide whether they matter (already decided by D-02-02/03/04).
