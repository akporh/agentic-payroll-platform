# Agentic Architecture Review

ICM-style (Issue/Confirm/Mitigate) structured review of the agentic payroll platform's current state, product thesis, and target direction.

> **Programme registration (2026-07-15):** this review is Phase 1 of the `agentic-architecture-review` programme and was moved here from `docs/agentic-architecture-review/` (`git mv`, history preserved — see `decisions.md` D-001/D-002). Programme control files (`PROGRAMME.md`, `POLICY.md`, `PHASES.md`, `state.md`, `decisions.md`, `exceptions.md`) sit alongside this README; they govern phase-level scope only. Nothing about stage sequencing, gating, or the finding lifecycle changed — `WORKFLOW.md` and `review-state.md` remain authoritative for the review itself. Historical records elsewhere in `docs/` deliberately still cite the old path.

## Purpose

This is a review workspace, not a delivery workspace. It exists to build an evidence-backed, stage-gated understanding of:

- What the current operating model and system actually do (not what we assume they do)
- Whether the product thesis holds
- What the agent portfolio actually covers vs. what it claims to cover
- Where platform, compliance, security, and human-experience gaps exist
- What target direction and roadmap should follow from confirmed findings — not from assumption

## Status

See `review-state.md` — the single source of truth for every stage's status and the next action. (This section previously duplicated stage status and went stale; it now only points.)

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
| `PROGRAMME.md`, `POLICY.md`, `PHASES.md`, `state.md`, `decisions.md`, `exceptions.md` | Programme-level control files (phase scope and gates — added at programme registration, 2026-07-15) |

## Next action

See `review-state.md` (stage-level) and `state.md` (phase-level). This section previously hard-coded a next action and went stale; it now only points.
