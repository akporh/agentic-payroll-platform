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
| Stage 05 in-progress report (largest stage yet — 5 findings, full snapshot inventory) | new (terse) | 485 | ~121 | Still no findings/tables recap despite this being the deepest investigation so far |
| Stage 05 close (split remediation-scope decision: 05-001 bundled, 05-004 deferred) | new (terse) | 431 | ~108 | Decision + remediation status + next action, no findings recap |

**Old-style baseline (2 measured reports):** ~1,157 tokens per report.
**New-style (5 measured reports):** ~60, ~141, ~107, ~121, ~108 — avg ~107 tokens.
**Per-report saving so far:** ~1,050 tokens average (~91% reduction), n=5 —
the ratio is holding steady regardless of how large the underlying
investigation is, which is the core mechanism this change relies on (the
file content scales with the work; the chat report does not).

## Running totals

- Reports measured under old style: 2
- Total old-style tokens (measured): ~2,314
- Reports measured under new style: 5
- Total new-style tokens (measured): ~537
- Estimated cumulative savings so far: ~5,248 tokens (5 new-style reports
  vs. what 5 old-style equivalents would have cost: 5 × 1,157 = 5,785)
- Full-programme estimate: if every remaining stage (06–13, 8 stages ×
  2 reports each — in-progress + close, per the two formats in
  `feedback_terse_audit_reporting`) used the old style instead, that would
  cost roughly 8 × 2 × 1,157 ≈ 18,512 tokens; at the new style's measured
  ~107-token average that's ≈ 1,712 tokens — a projected additional saving
  of ~16,800 tokens over the remaining programme, on top of the ~5,248
  already measured across Stages 03–05. This projection will be replaced
  with actual measured figures as each remaining stage closes.

Update this table at the end of every stage: append a row with the new
report's character count and token estimate, then recompute the running
totals above.
