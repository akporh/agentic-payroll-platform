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

| Stage | Style | Report chars | Est. tokens (÷4) | Notes |
|---|---|---|---|---|
| 02 | old (full recap) | 3,870 | ~968 | Baseline — measured retroactively from the actual message text |
| 03 | old (full recap) | 5,382 | ~1,346 | Baseline — measured retroactively from the actual message text |
| 04 | — | — | — | First stage under the new terse format — to be filled in on close |

**Old-style baseline (Stages 02–03 average):** ~1,157 tokens per stage closing report.

## Running totals

- Stages measured under old style: 2 (Stages 02, 03)
- Total old-style tokens (measured): ~2,314
- Total new-style tokens (from Stage 04 on): _pending_
- Estimated cumulative savings: _pending — will be computed as
  `(old-style average × stages remaining) − (actual new-style total)`
  once Stage 04+ figures are in._

Update this table at the end of every stage: append a row with the new
report's character count and token estimate, then recompute the running
totals above.
