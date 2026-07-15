# Stage 03 Review Decision — Agent Portfolio

Apply the human review decision for Stage 03 only.

## Decision

Approve the revised 15-capability portfolio as the reference portfolio for downstream stages.

The portfolio replaces the source architecture document's original five-track/named-agent structure for the purposes of this review. Preserve the architecture document as a source input, but do not treat its original grouping as the approved target portfolio.

## Approved conditions

1. Preserve all existing Stage 02 blockers and launch preconditions.
2. C4 Historical Payroll Explanation remains blocked until F-01-27, F-01-29 and F-01-38 are closed.
3. C8 Reconciliation Investigation and every tool touching `payroll_reconciliation` remain blocked until the repository-level workspace-scoping fix lands; tool-layer workspace verification is additionally required.
4. C5 Trace Explanation must explicitly refuse when `component_trace_jsonb` is null; it must never fabricate or silently degrade.
5. C3 Operator Assistant launches as current-state only and must explicitly refuse historical-outcome questions.
6. C6 Payroll Readiness remains a deterministic service, not an LLM-driven agent.
7. C7 anomaly detection uses deterministic/statistical detection; any LLM role is optional narration only. Threshold policy remains forwarded to Stage 04/08.
8. C10 confirmation/pending-action protocol remains deterministic infrastructure and its expiry, conflict, idempotency and run-state invalidation rules remain for Stage 08.
9. C11 Compliance Monitoring remains detect/compare/propose only.
10. C12 statutory-rule change management remains a separate deterministic platform/compliance capability.
11. C13 AI onboarding mapping may not ship without C14 deterministic validation/dry-run as its hard safety gate. The dry-run mechanism remains for Stage 08.
12. C1 and C2 remain classified as deterministic platform foundations, not agent capabilities.
13. The standalone Trace Agent name remains rejected; do not reintroduce it unless a later stage identifies a distinct, evidence-backed capability not covered by C5 or the existing UI.
14. Every tool must have independent workspace-ownership verification.

## Required updates

- Record the portfolio gate approval in `decisions.md` and `_core/HUMAN-DECISIONS.md` using the next available decision identifiers.
- Update `findings.md` and outputs only where necessary to reflect that the 15-capability portfolio is now approved rather than merely recommended.
- Update all downstream handoffs so Stages 04, 05, 06, 07, 08, 09, 11 and 12 consume the approved portfolio and retain the blockers/conditions above.
- Update `review-state.md` to mark Stage 03 `complete` and set the next stage to `04 — Outcome Discovery`.
- Do not begin Stage 04.
- Do not modify production code.

## Completion report

Return:

- Stage status
- Primary file
- Review-state path
- Commit SHA
- Approved portfolio count
- Blocked/deferred capabilities
- Forwarded decisions/specifications
- Next stage
