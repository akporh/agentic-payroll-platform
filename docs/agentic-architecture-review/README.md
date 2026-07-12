# Agentic Architecture Review

ICM-style (Issue/Confirm/Mitigate) structured review of the agentic payroll platform's current state, product thesis, and target direction.

## Purpose

This is a review workspace, not a delivery workspace. It exists to build an evidence-backed, stage-gated understanding of:

- What the current operating model and system actually do (not what we assume they do)
- Whether the product thesis holds
- What the agent portfolio actually covers vs. what it claims to cover
- Where platform, compliance, security, and human-experience gaps exist
- What target direction and roadmap should follow from confirmed findings — not from assumption

## Status

**Not started.** No stage has begun. See `review-state.md` for the authoritative status of every stage.

## How this workspace works

Read `WORKFLOW.md` before doing anything else — it defines the stage sequence, gating rules, and the finding lifecycle (draft → confirmed). Read the four `_core/` documents before starting any stage; they are binding for the whole review, not per-stage guidance.

## Hard rules

- This review does not modify production code. It is read-only with respect to `backend/`, `frontend/`, and `migrations/`.
- Stages run in numbered order. A stage does not start until the prior stage's gate is explicitly passed (see `WORKFLOW.md`).
- No finding is treated as fact until it meets the evidence standard in `_core/EVIDENCE-STANDARD.md` and is promoted from draft to confirmed per `_core/FINDING-SCHEMA.md`.
- Current implementation, intended design, and identified gap are always recorded as three separate things — never merged into one narrative. See `_core/REVIEW-PRINCIPLES.md`.

## Folder map

| Path | Purpose |
|---|---|
| `README.md` | This file |
| `WORKFLOW.md` | Stage sequence, gating rules, finding lifecycle |
| `review-state.md` | Live status of every stage — single source of truth for "where are we" |
| `_core/` | Binding standards: principles, evidence, finding schema, severity, human decision log |
| `_inputs/source-register.md` | Register of every source document/system consulted, with provenance |
| `01-current-operating-model` … `13-approved-roadmap` | Numbered stage folders, run in order |

## Next action

**Await approval to begin Stage 01.**
