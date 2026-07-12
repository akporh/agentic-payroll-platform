# Stage 03: Agent Portfolio — Decisions

Stage-local log of human decisions made during this stage. Master log: `_core/HUMAN-DECISIONS.md`. Format matches `_core/HUMAN-DECISIONS.md`.

## Gate

- **Gate opened**: 2026-07-12, by human reviewer (Michael Emedo) — pointed to `stage-03-agent-portfolio-prompt.md` on GitHub as the instruction to begin Stage 03.
- **Gate closed**: not yet — investigation complete; per the stage prompt, Stage 03 is marked `awaiting-review`, not `complete`.

## Inherited binding decisions applied (not re-litigated)

D-02-01 through D-02-04 (`_core/HUMAN-DECISIONS.md` HD-2–HD-5) were treated as gates throughout this stage, per the prompt's explicit instruction. See `agent-capability-matrix.md` C4, C8, C11, C12 and `blocked-and-deferred-register.md` for how each was applied.

## Human decisions required (raised by this stage)

Per the prompt's finding-discipline instruction ("do not create artificial human decisions where the evidence and inherited principles already resolve the issue"), this stage found **no new decisions requiring human adjudication at the Stage 03 gate itself** — every design-level ambiguity encountered either resolved directly from Stage 01/02 evidence, or was explicitly forwarded to a later stage as a specification/design task (not a decision needing this reviewer's judgment now):

- Anomaly-detection threshold/calibration policy (F-03-04) — forwarded to Stage 04 as a product/statistics calibration question, not a Stage 03 decision.
- Confirmation-protocol specification (expiry, conflicts, idempotency, state-transition invalidation) — forwarded to Stage 08 as design work, per the prompt's explicit instruction not to fully design this here.
- Dry-run mechanism definition — forwarded to Stage 08.

The one substantive judgment call this stage made on its own initiative — consolidating 24 fine-grained Stage 02 capability items into 15 portfolio-level capabilities, including merging 3 "agents" into one assistant (F-03-01) and rejecting Trace Agent as standalone (F-03-02) — is offered as a recommendation for the human reviewer to approve or challenge at this stage's gate, not a decision requiring a separate mid-stage question, since it followed directly from the overlap evidence gathered.

## Next action

**Human review of Stage 03 outputs (especially the recommended 15-capability portfolio and its dispositions); gate approval required before Stage 04.**
