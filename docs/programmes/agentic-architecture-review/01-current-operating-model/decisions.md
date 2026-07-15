# Stage 01: Current Operating Model — Decisions

Stage-local log of human decisions made during this stage. Master log: `_core/HUMAN-DECISIONS.md`. Format matches `_core/HUMAN-DECISIONS.md`.

## Gate

- **Gate opened**: 2026-07-11, by human reviewer (Michael Emedo) — instruction to "Perform Stage 01" using CONTEXT.md
- **Gate closed**: 2026-07-12, by human reviewer (Michael Emedo), via explicit approval ("Approve — close Stage 01, begin Stage 02") in response to a direct gate-approval question. Stage 01's 46 confirmed findings are now citable by later stages.

## Decisions log

### HD-01-1: Scope confirmed as descriptive-only, 20 named areas
- **Date**: 2026-07-11
- **Decision**: Stage 01 covers exactly the 20 areas listed in the human reviewer's instruction (workspace/tenant creation through statutory-rule maintenance). Explicitly excludes agent recommendations, architecture assessment, workflow redesign, and treating architecture docs as proof of implementation.
- **Made by**: Michael Emedo (via task instruction)
- **Context**: Sets the evidence bar — code/migrations/data only, not roadmap or design docs — per `_core/EVIDENCE-STANDARD.md`.
- **Affects**: All findings in this stage's `findings.md`

### HD-01-2: Two findings recorded without a severity rating pending later-stage confirmation
- **Date**: 2026-07-11
- **Decision**: F-01-07 (PH_OT pensionable flag), F-01-09 (grade-percentage vs salary-definition-JSON selection), F-01-12 (workspace_payroll_config allowlist/CHECK sync), F-01-20 (readiness pre-check invocation guarantee), F-01-29 (trace fallback branch liveness), and F-01-44 (current_fallback producing code path) were recorded as confirmed facts about what exists, but explicitly left their underlying open question unresolved rather than guessing, since resolving them required evidence outside this stage's cluster assignments.
- **Made by**: Claude (agent), consistent with `_core/REVIEW-PRINCIPLES.md` §3 (evidence over inference)
- **Context**: The alternative was either fabricating a resolution without evidence or discarding the observation entirely — both worse than recording the fact plus an explicit unresolved marker for the stage best positioned to resolve it (usually Stage 08).
- **Affects**: F-01-07, F-01-09, F-01-12, F-01-20, F-01-29, F-01-44; forwarded to Stage 08 per `findings.md` cross-references section

## Next action

**Stage 01 gate closed. Stage 02 (Product Thesis) is open.**
