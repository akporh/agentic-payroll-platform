---
name: Audit Programme Token-Savings Log
description: Estimated chat-output tokens saved by reporting each stage tersely (file + summary + SHA) instead of recapping full findings in chat, starting Stage 04
type: project
---

# Token-Savings Log

Tracks the estimated chat-output token cost of each stage's closing report,
comparing the **old style** (Stages 01–03: full findings recap pasted into
chat) against the **new style** (Stage 04 onward: file path + short summary
+ flags + commit SHA), per the reporting change adopted 2026-07-12 — see
memory `feedback_terse_audit_reporting`.

## Methodology (and its limits)

- No tool in this environment exposes exact per-message API token counts, so
  these are **estimates**, not billed figures.
- Estimate = character count of the assistant's closing report for that
  stage, divided by 4 (a standard rough chars-per-token heuristic for
  English prose/markdown). Character counts for Stages 02–03 were obtained
  by writing the actual historical message text to a scratch file and
  running `wc -c` against it (reproducible, not guessed).
- This log only covers the **closing stage-report message** — it does not
  cover the investigation/tool-call tokens (reading source files, grep
  output, writing `findings.md` itself), which cost the same either way and
  are not what this change targets. See the memory file for why.
- Stage 01 was not separately re-measured; it predates this tracking and
  used a similarly verbose style to Stages 02–03, so it is excluded from
  the running total rather than estimated after the fact.

## Log

| Report | Style | Report chars | Est. tokens (÷4) | Notes |
|---|---|---|---|---|
| Stage 02 close | old (full recap) | 3,870 | ~968 | Baseline — measured retroactively from the actual message text |
| Stage 03 in-progress report | old (full recap) | 5,382 | ~1,346 | Baseline — measured retroactively from the actual message text |
| Stage 03 close-out (Casper prompt execution) | new (terse) | 240 | ~60 | First report under the new format — status/file/commit/next-stage only, no findings recap |
| Stage 04 in-progress report (reproduced S0 finding 04-001) | new (terse) | 562 | ~141 | Includes two decision-required lines (S0 escalation) — longer than the Stage 03 close-out but still no findings/tables recap |
| Stage 04 close | new (terse) | 428 | ~107 | Decision line + next-stage only, no findings recap despite closing an S0 release-blocker stage |

**Old-style baseline (2 measured reports):** ~1,157 tokens per report.
**New-style (3 measured reports):** ~60, ~141, ~107 — avg ~103 tokens.
**Per-report saving so far:** ~1,054 tokens average (~91% reduction), n=3.

## Running totals

- Reports measured under old style: 2
- Total old-style tokens (measured): ~2,314
- Reports measured under new style: 2
- Total new-style tokens (measured): ~201
- Estimated cumulative savings so far: ~2,113 tokens (2 new-style reports
  vs. what 2 old-style equivalents would have cost: 2 × 1,157 = 2,314)
- Full-programme estimate: if every remaining stage (04–13, 10 stages ×
  2 reports each — in-progress + close, per the two formats in
  `feedback_terse_audit_reporting`) had instead used the old style, the
  programme would have spent roughly 10 × 2 × 1,157 ≈ 23,140 tokens on
  closing reports alone; at the new style's ~60–150 tokens per report
  (~100 avg estimate) that's ≈ 2,000 tokens — a projected saving on the
  order of 21,000 tokens by the end of the programme. This projection will
  be replaced with actual measured figures as each stage closes.

Update this table at the end of every stage: append a row with the new
report's character count and token estimate, then recompute the running
totals above.
