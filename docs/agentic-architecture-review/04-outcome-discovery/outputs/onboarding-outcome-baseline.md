# Stage 04 Output: Onboarding Outcome and Baseline (C13 → C14)

## Outcomes, defined

| Outcome | Current state | Desired state |
|---|---|---|
| Interpreting legacy payroll files | Manual column mapping via `NativeUploadFlow` (Stage 01 F-01-13) | AI-assisted interpretation of arbitrary, messy headers (C13), always as a proposal an operator confirms |
| Reducing manual mapping work | No time/error data currently recorded — see baseline gap below | Measurable reduction once C13 ships, against a real "before" number |
| Surfacing ambiguous mappings | Not distinguished from confident mappings today — `NativeUploadFlow` treats all mappings the same way | C13 should surface its own confidence per mapped field, so an operator's attention goes to the genuinely ambiguous ones, not every field equally |
| Validating proposed mappings deterministically | Existing onboarding hard-validator (Stage 01 F-01-04) validates committed data, not proposed-but-unconfirmed mappings | C14 validates a *proposed* import before commit — schema, tenant, and rule validation, reusing the existing hard-validator logic where possible rather than duplicating it |
| Running a trustworthy dry run | No dry-run mechanism exists at all today | A dry run that exercises real payroll logic (mechanism TBD — Stage 08) against the proposed import, before commit |
| Measuring parallel-run confidence | The existing "Reconcile with old system" tool (`ReconSlideOver`, Stage 01 F-01-41/44) is client-side-only and not persisted — it produces a one-time comparison view, not a tracked confidence metric | A persisted parallel-run agreement rate, trackable across the onboarding period, not a single ephemeral comparison |
| Reducing time to client go-live | No current measurement of onboarding duration | Track time-to-go-live per client once instrumented, to have a comparison basis for future improvement |

## Baseline-data gaps (explicit)

This repository and product currently have **no quantified baseline** for any of the following, which this stage cannot supply from code/migration evidence alone — each is a data-collection prerequisite before the corresponding outcome can be claimed as "improved":

1. **Manual column-mapping time per client onboarding** — not tracked anywhere in the current system. Recommend instrumenting this (even a simple timestamp-based measurement around the existing `NativeUploadFlow` step) *before* C13 ships, so there's a real "before" number.
2. **Mapping error rate** — how often a manually-mapped column turns out to be wrong, discovered later (e.g. at first payroll run or reconciliation). Not currently tracked; would require either a new data point at error-discovery time or a retrospective sampling exercise.
3. **Parallel-run agreement rate** — the existing `ReconSlideOver` tool (Stage 01 F-01-41) produces a MATCH/MISMATCH/NEW-ONLY/OLD-ONLY comparison but does not persist the result anywhere, so no historical agreement-rate trend exists. Recommend persisting this comparison's output (not just displaying it) as a first step, independent of whether C13/C14 are built yet.
4. **Time-to-go-live per client** — not currently instrumented. Would need a start/end marker in the onboarding workflow (workspace creation → LIVE transition, Stage 01 F-01-02, already has a `LIVE` status transition timestamp implicitly available via `workspace.status` history if such history were captured — currently it is not, since `workspace` has no status-change audit trail per Stage 01's audit-coverage finding, F-01-40).

## Recommendation

Before committing engineering time to C13, take the low-cost step of instrumenting baseline measurement for items 1, 2, and 4 above (item 3 already has a natural first step: persist `ReconSlideOver`'s output). This doesn't require building any AI capability — it's pure measurement instrumentation — but it's the only way "reduced onboarding friction" will ever be a demonstrable claim rather than an assumed one. This recommendation is offered to Stage 05/11 for prioritisation, not committed here.
