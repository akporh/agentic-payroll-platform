# Workflow

## Stage sequence

Stages run in strict numbered order. A stage is a unit of investigation, not a unit of delivery.

| # | Stage | Folder |
|---|---|---|
| 01 | Current Operating Model | `01-current-operating-model` |
| 02 | Product Thesis | `02-product-thesis` |
| 03 | Agent Portfolio | `03-agent-portfolio` |
| 04 | Outcome Discovery | `04-outcome-discovery` |
| 05 | Platform Readiness | `05-platform-readiness` |
| 06 | Compliance & Controls | `06-compliance-controls` |
| 07 | Security & Identity | `07-security-identity` |
| 08 | Technical Architecture | `08-technical-architecture` |
| 09 | Human Experience | `09-human-experience` |
| 10 | Evaluation & Assurance | `10-evaluation-assurance` |
| 11 | Commercial & Product Strategy | `11-commercial-product-strategy` |
| 12 | Target Direction | `12-target-direction` |
| 13 | Approved Roadmap | `13-approved-roadmap` |

Stages 01–11 are diagnostic: they establish what is true now. Stage 12 synthesizes confirmed findings into a target direction. Stage 13 is the only stage that produces a roadmap, and it may only draw on confirmed findings and human decisions from prior stages — never on draft findings or assumptions carried in from outside the review.

## Per-stage contents

Every stage folder contains:

- `CONTEXT.md` — scope of the stage, questions it is answering, what is explicitly out of scope
- `findings.md` — findings log for the stage, using the schema in `_core/FINDING-SCHEMA.md`. Draft and confirmed findings are visually and structurally separated in this file — never merged into one list.
- `decisions.md` — human decisions made during the stage, logged per `_core/HUMAN-DECISIONS.md`
- `evidence/` — raw evidence artifacts (query outputs, file excerpts, screenshots, logs) that back confirmed findings. Every confirmed finding must cite a file in this folder.
- `outputs/` — synthesized stage deliverables (e.g. a written assessment, a diagram) produced once the stage is gated closed

## Gating rules

A stage may not begin until:

1. The prior stage's gate has been explicitly passed by the human reviewer (see `_core/HUMAN-DECISIONS.md` for how approval is recorded).
2. `review-state.md` has been updated to reflect the prior stage's closure.

A stage may not be marked closed until:

1. Every finding in `findings.md` intended to inform later stages is either confirmed (with evidence) or explicitly marked as parked/rejected — no findings are left ambiguously "maybe."
2. `review-state.md` is updated with the stage's final status.

## Finding lifecycle

1. **Draft** — an observation or hypothesis, recorded as soon as it is noticed. Not to be cited by any other stage.
2. **Confirmed** — meets the bar in `_core/EVIDENCE-STANDARD.md`, has a cited evidence artifact, and has been reviewed. Only confirmed findings may be cited by Stage 12 or Stage 13, or by any later stage's `CONTEXT.md`.
3. **Parked / Rejected** — explicitly closed out without promotion, with a one-line reason. This prevents a draft from silently rotting into an assumed fact by omission.

## Current operating model / intended design / gap separation

Every stage that touches a system behavior must record three things separately, never as one merged statement:

- **Current implementation** — what the code/config/data actually does today, cited to evidence
- **Intended design** — what the design intent was (from specs, tickets, `CLAUDE.md`, or stated by the human reviewer)
- **Identified gap** — the delta between the two, if any

This separation is structural in `_core/FINDING-SCHEMA.md` and must not be collapsed in prose.

## Production code

This review does not modify production code, configuration, or data. All stage work is read/analysis only. Any output that recommends a code change is a roadmap recommendation for future delivery work, not an edit made during the review.

## Next action

**Await approval to begin Stage 01.**
