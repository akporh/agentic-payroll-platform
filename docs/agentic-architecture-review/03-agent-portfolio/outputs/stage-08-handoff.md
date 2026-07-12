# Stage 03 → Stage 08 Handoff (Technical Architecture)

**The 15-capability portfolio is approved (D-03-01, 2026-07-12) — the specification questions below are confirmed open work items within an approved portfolio, not pending a portfolio-level decision.**

## Specification questions this stage explicitly did not resolve (by design, per the prompt's constraints)

1. **Structured confirmation / pending-action protocol (C10)** — full detail needed on:
   - Expiry: what happens if an operator never confirms a pending action?
   - Conflicts: how are two proactive agents proposing conflicting pending actions on the same entity reconciled?
   - Idempotency: what happens if a confirmation is submitted twice?
   - State-transition invalidation: what happens to a pending action if the target `payroll_run` transitions to `APPROVED`/`LOCKED`/`PAID` before the operator confirms? (Carried unchanged from Stage 02 F-02-13.)

2. **Dry-run payroll mechanism (C14)** — does "dry-run" mean exercising the real sequential executor/snapshot machinery against a proposed import, or a separate simulation path? This must be answered before C13 (Onboarding Mapping Assistant) can rely on C14 as its safety gate. (Carried unchanged from Stage 02 F-02-10.)

3. **`explain_component_trace` null-trace behavior (C5)** — needs an explicit specification: refuse cleanly, or degrade to a generic explanation referencing the legacy-executor gap? Currently unspecified in the source document. (F-03-15)

4. **`get_enrollment_status` tool contract (C3's underlying tool)** — should return individual facts (status, enrollment state, contract window, salary-definition presence), not a pre-packaged "why" conclusion. Needs a concrete field-level contract definition. (F-03-08)

5. **Input anomaly detection mechanism (C7)** — needs a concrete statistical method (threshold vs. z-score vs. something else) once Stage 04 supplies the calibration policy.

6. **Reconciliation causal-diff computation (C8, once unblocked)** — needs a concrete deterministic algorithm design for identifying which employee/component/amount caused a MISMATCH, reading `component_trace_jsonb`/`payroll_reconciliation`. Do not design this until D-02-02/D-02-03 preconditions clear, but the algorithm itself should be specified in advance so it's ready to build once unblocked.

7. **Independent workspace-ownership verification pattern (all tools)** — needs one consistent implementation pattern (e.g. a shared decorator/middleware) applied to every tool in `outputs/tool-portfolio-matrix.md`, rather than ad hoc per-tool checks that could drift out of sync. (F-03-07)

8. **New workspace catalog tool (C13)** — a grade/designation/salary-definition catalog reader, not in the source document's original 10-tool list, needed for the Onboarding Mapping Assistant. Needs a full contract definition (same rigor as the other 10 tools in `outputs/tool-portfolio-matrix.md`).

## Design constraints already decided (apply, do not re-litigate)

- Reconciliation causal diff must be deterministic; LLM narrates only (F-03-05, matches the existing `explain_component_trace` slot-filling pattern).
- Every tool requires independent workspace-ownership verification (F-03-07, Stage 02 Principle 11).
- Decimal values in any LLM-visible context must serialize as strings, not floats (source document's own stated rule, reconfirmed applicable to every tool in `outputs/tool-portfolio-matrix.md`).

## What Stage 08 should NOT re-derive

The capability portfolio and tool list themselves (`outputs/agent-capability-matrix.md`, `outputs/tool-portfolio-matrix.md`) — Stage 08's job is mechanism design for the specification gaps above, not re-deciding which capabilities exist.
