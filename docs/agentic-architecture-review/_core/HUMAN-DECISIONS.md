# Human Decisions

Log of every point in the review where a human judgment call, scope decision, severity call, gate approval, or contested-evidence adjudication was required. This is the master log; each stage's `decisions.md` holds the stage-local copy of decisions made during that stage, and should link back here.

Nothing in this file is inferred by the AI agent on the human reviewer's behalf — every entry corresponds to an actual statement or approval from the human reviewer (Michael Emedo, or a designated delegate).

## Log format

```markdown
### HD-<n>: <short title>
- **Date**: YYYY-MM-DD
- **Stage**: <stage number/name, or "cross-cutting">
- **Decision**: <what was decided>
- **Made by**: <who>
- **Context**: <why this required a human call rather than being derivable from evidence>
- **Affects**: <finding IDs, stage gates, or roadmap items this decision touches>
```

## Gate approvals

Stage gate approvals (permission to move a stage from `in-progress` to `gated-closed`, and to begin the next stage) are logged here as `HD-GATE-<stage#>` entries, in addition to being reflected in `review-state.md`.

## Decisions log

### HD-GATE-01: Stage 01 (Current Operating Model) gate approved
- **Date**: 2026-07-12
- **Stage**: 01 — Current Operating Model
- **Decision**: Approved closing Stage 01's gate. 46 confirmed findings (0 draft, 0 parked) are now citable by Stage 02 onward.
- **Made by**: Michael Emedo, via direct response to an explicit gate-approval question
- **Context**: `WORKFLOW.md` requires explicit human approval before a stage gate closes; this was obtained directly rather than inferred from the user directing work toward Stage 02.
- **Affects**: Stage 01 status (`review-state.md`), Stage 02 eligibility to begin

## Next action

**Stage 02 (Product Thesis) is open.**
