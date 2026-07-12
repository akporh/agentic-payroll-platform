# Stage 02: Product Thesis — Decisions

Stage-local log of human decisions made during this stage. Master log: `_core/HUMAN-DECISIONS.md`. Format matches `_core/HUMAN-DECISIONS.md`.

## Gate

- **Gate opened**: 2026-07-12, by human reviewer (Michael Emedo) — pointed to `stage-02-product-thesis-prompt.md` on GitHub as the instruction to begin Stage 02.
- **Gate closed**: not yet — investigation complete; per the stage prompt, Stage 02 is marked `awaiting-review`, not `complete`, and Stage 03 has not begun.

## Human decisions required (raised by this stage, unresolved — for the human reviewer)

### HD-02-1: Is there a follow-up to the architecture document's "NEEDS REVISION" status?
- **Raised by**: F-02-02
- **Question**: The document (`docs/architecture/agent-layer-architecture.html`) is self-labelled "NEEDS REVISION" after a 2026-06-11 arch-council pass, with no note found on what specifically needs revision or whether a later round resolved it. Does such a record exist outside this document, and should it be pulled into this review?
- **Why this needs a human call**: Only the human reviewer (or whoever ran that arch-council session) knows whether "NEEDS REVISION" is stale labelling or an open, unresolved objection.
- **Affects**: How much weight Stage 12 (Target Direction) gives this document.

### HD-02-2: Precondition or compensating control for `get_reconciliation` workspace scoping?
- **Raised by**: F-02-06
- **Question**: Should closing the `payroll_reconciliation` workspace-scoping gap (F-01-33) be a hard precondition before Track V's tool layer ships, or is an independent compensating control at the tool-serialization layer (re-verifying workspace ownership in the new tool code, without touching the underlying repo functions) an acceptable alternative?
- **Why this needs a human call**: This is a sequencing/risk-acceptance tradeoff between fixing the platform gap directly vs. building a compensating control — a product/engineering priority call, not something derivable from evidence alone.
- **Affects**: Track V scoping (Stage 03), Stage 05 platform-readiness sequencing.

### HD-02-3: Precondition or accepted residual risk for historical reproducibility gaps?
- **Raised by**: F-02-09
- **Question**: Should Stage 01's F-01-27 (salary_definition editable pre-PAID) and F-01-38 (dead status branches in the D-ARCH-1 guard) be closed before Track W/X ship (since both implicitly depend on historical reproducibility), or is this an acceptable, disclosed residual risk for the first release of explanation/investigation agents?
- **Why this needs a human call**: A risk-acceptance decision balancing delivery speed against a low-but-nonzero chance of an agent generating a plausible-but-wrong explanation.
- **Affects**: Track W/X sequencing (Stage 03), Principle #7's practical rollout.

### HD-02-4: Should a statutory-rule change-management mechanism be scoped independently of Y1?
- **Raised by**: F-02-12
- **Question**: Y1 (Compliance Monitoring) cannot function as scoped because there is no product mechanism to apply a statutory-rule change other than a developer-authored migration. Should "operator-approved statutory-rule change workflow" be scoped as its own deterministic-software deliverable, independent of whether/when AI-based change *detection* (Y1) is built?
- **Why this needs a human call**: This is a roadmap-prioritization and build-vs-defer decision, and touches compliance risk appetite (Stage 06's remit to weigh in on too).
- **Affects**: Stage 06 (Compliance & Controls), Stage 11 (Commercial & Product Strategy), Track Y sequencing.

## Next action

**Human review of Stage 02 outputs; the four decisions above require your input. Gate approval required before Stage 03 begins.**
