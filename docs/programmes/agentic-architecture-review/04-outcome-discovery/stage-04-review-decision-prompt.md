# Stage 04 Review Decision — Outcome Discovery

Apply the human review decision for Stage 04 only.

## Decision: C7 anomaly-detection calibration approach

Approve a **layered combination**, introduced in stages:

1. **Launch baseline — absolute thresholds**
   - Use input-code-specific hard limits to catch extreme, unambiguous magnitude errors.
   - Thresholds must be configurable and explainable.
   - They must not be generated or adjusted by an LLM.

2. **Second layer — period-on-period variance**
   - Add employee-history comparison only where a minimum history window exists.
   - Use it as an additional flag, not as a replacement for hard limits.
   - The alert must show the current value, comparison baseline and variance.

3. **Peer-pattern comparison — defer**
   - Do not include peer-pattern comparison in the initial design.
   - Reconsider only where a workspace has sufficient comparable employee volume and reliable grade/role grouping.
   - It must never compare employees across tenants/workspaces.

4. **Exception workflow dependency**
   - C7 must not ship without the exception-resolution workflow needed to assign, review, confirm/dismiss and close alerts.

5. **Calibration governance**
   - Begin in shadow mode where practical.
   - Measure confirmed-error capture, confirmed-correct dismissal rate and later-discovered unflagged errors.
   - Threshold changes require versioning and auditability.
   - LLM use remains optional narration only and must not perform anomaly detection or threshold selection.

## Required updates

- Record this decision in `decisions.md` and `_core/HUMAN-DECISIONS.md` using the next available identifiers.
- Update `outputs/anomaly-detection-outcome-policy.md`, `outputs/outcome-prioritisation.md`, `outputs/measurement-framework.md` and relevant handoffs to reflect the approved layered approach.
- Preserve the final statistical formulas, numeric thresholds and minimum-history window for Stage 08 design and later product calibration; do not invent them in Stage 04.
- Update `findings.md` only where needed to reflect that the calibration approach is now decided.
- Mark Stage 04 `complete` in `review-state.md` and set the next stage to `05 — Platform Readiness`.
- Do not begin Stage 05.
- Do not modify production code or unrelated working-tree changes.

## Completion report

Return:

- Stage status
- Primary file
- Review-state path
- Commit SHA
- Decision recorded
- Remaining baseline gaps
- Forwarded Stage 08 specifications
- Next stage
