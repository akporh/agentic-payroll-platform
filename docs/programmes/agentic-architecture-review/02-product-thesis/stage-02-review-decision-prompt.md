# Stage 02 Review Decision Prompt

Apply the human review decisions below to Stage 02 only.

## Decisions

### D-02-01 — Architecture document status
The architecture document's `NEEDS REVISION` status remains open. Treat this review as the formal revision path. The document is not approved until Stage 12 synthesises the target direction and Stage 13 records approval.

### D-02-02 — Reconciliation workspace scoping
Correct repository-level reconciliation workspace scoping before `get_reconciliation` is exposed as an agent tool. Tool-layer workspace ownership validation is also mandatory as defence in depth.

Do not accept a tool-only workaround as the permanent resolution.

### D-02-03 — Historical reproducibility
Historical reproducibility is a launch precondition for capabilities that explain, trace or investigate historical payroll outcomes.

Track W may proceed selectively for current-state navigation and assistance where it does not depend on reconstructing historical truth. Historical explanation and Track X reconciliation/trace investigation must remain blocked until the relevant snapshot, mutation and reproducibility gaps are resolved.

Do not classify this as a general accepted residual risk disclosed to operators.

### D-02-04 — Statutory-rule change management
Scope statutory-rule change management as a separate deterministic platform and compliance capability, independent of Y1.

Y1 may later detect external changes, compare evidence and prepare proposals. It must not directly author, execute or deploy production Alembic migrations.

## Required updates

1. Record these decisions in:
   - `docs/programmes/agentic-architecture-review/02-product-thesis/decisions.md`
   - `docs/programmes/agentic-architecture-review/_core/HUMAN-DECISIONS.md`, if required by the workflow
2. Update affected Stage 02 findings and outputs so the decisions are reflected consistently.
3. Update the Stage 03, Stage 05, Stage 06, Stage 07, Stage 08, Stage 12 and Stage 13 handoffs where relevant.
4. Mark Stage 02 `complete` in `review-state.md` once the decision updates pass the Stage 02 completion criteria.
5. Set the next action to: `Await approval to begin Stage 03 — Agent Portfolio`.
6. Do not begin Stage 03.
7. Do not modify production code.

## Completion report

Return:

- files updated
- decisions recorded
- findings or outputs amended
- final Stage 02 status
- next action
- unresolved items, if any
- `git status --short`

Commit the documentation changes and report the commit SHA.