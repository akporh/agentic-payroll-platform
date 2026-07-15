# Stage 03: Agent Portfolio — Decisions

Stage-local log of human decisions made during this stage. Master log: `_core/HUMAN-DECISIONS.md`. Format matches `_core/HUMAN-DECISIONS.md`.

## Gate

- **Gate opened**: 2026-07-12, by human reviewer (Michael Emedo) — pointed to `stage-03-agent-portfolio-prompt.md` on GitHub as the instruction to begin Stage 03.
- **Gate closed**: 2026-07-12 — approved via `stage-03-review-decision-prompt.md` (D-03-01, `_core/HUMAN-DECISIONS.md` HD-6, HD-GATE-03). Stage 03 marked `complete`.

## D-03-01: Revised 15-capability portfolio approved as the reference portfolio
- **Date**: 2026-07-12
- **Decision**: The revised 15-capability portfolio (`outputs/agent-capability-matrix.md`) is approved as the reference portfolio for all downstream stages, replacing the source architecture document's original five-track/named-agent structure for the purposes of this review. The architecture document is preserved as a source input (per D-02-01, still "NEEDS REVISION"), but its original track/agent grouping is no longer the target portfolio.
- **Made by**: Michael Emedo, via `stage-03-review-decision-prompt.md`
- **Approved conditions** (all 14 preserved unchanged from this stage's findings — see the prompt's numbered list for full text): Stage 02 blockers/preconditions preserved (conditions 1–3); C5 null-trace refusal required (4); C3 current-state-only launch with explicit historical refusal (5); C6 stays deterministic (6); C7 deterministic detection + optional narration, threshold forwarded (7); C10 stays deterministic infrastructure, open questions forwarded to Stage 08 (8); C11 detect/compare/propose only (9); C12 separate deterministic capability (10); C13 cannot ship without C14 as hard gate, dry-run mechanism forwarded to Stage 08 (11); C1/C2 stay deterministic platform foundations (12); Trace Agent rejection stands (13); every tool requires independent workspace-ownership verification (14).
- **Affects**: all 16 confirmed findings and all 9 Stage 03 outputs; downstream Stages 04, 05, 06, 07, 08, 09, 11, 12 now consume the approved (not merely recommended) portfolio.

## Inherited binding decisions applied (not re-litigated)

## Inherited binding decisions applied (not re-litigated)

D-02-01 through D-02-04 (`_core/HUMAN-DECISIONS.md` HD-2–HD-5) were treated as gates throughout this stage, per the prompt's explicit instruction. See `agent-capability-matrix.md` C4, C8, C11, C12 and `blocked-and-deferred-register.md` for how each was applied.

## Human decisions required (raised by this stage)

Per the prompt's finding-discipline instruction ("do not create artificial human decisions where the evidence and inherited principles already resolve the issue"), this stage found **no new decisions requiring human adjudication at the Stage 03 gate itself** — every design-level ambiguity encountered either resolved directly from Stage 01/02 evidence, or was explicitly forwarded to a later stage as a specification/design task (not a decision needing this reviewer's judgment now):

- Anomaly-detection threshold/calibration policy (F-03-04) — forwarded to Stage 04 as a product/statistics calibration question, not a Stage 03 decision.
- Confirmation-protocol specification (expiry, conflicts, idempotency, state-transition invalidation) — forwarded to Stage 08 as design work, per the prompt's explicit instruction not to fully design this here.
- Dry-run mechanism definition — forwarded to Stage 08.

The one substantive judgment call this stage made on its own initiative — consolidating 24 fine-grained Stage 02 capability items into 15 portfolio-level capabilities, including merging 3 "agents" into one assistant (F-03-01) and rejecting Trace Agent as standalone (F-03-02) — is offered as a recommendation for the human reviewer to approve or challenge at this stage's gate, not a decision requiring a separate mid-stage question, since it followed directly from the overlap evidence gathered.

## Next action

**Stage 03 is complete. Await approval to begin Stage 04 — Outcome Discovery.**
