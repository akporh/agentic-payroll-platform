# Audit Programme — Sandy Payroll Platform

## What this is

An evidence-led, staged audit of the Phase 1 MVP payroll engine. Each stage
inspects one concern, logs findings against a fixed evidence bar, and feeds a
single consolidated backlog at the end. It is a documentation and evidence
workspace — it does not contain application code and does not, by itself,
change any.

## What this is not

- Not a new instruction file. `CLAUDE.md` (repo root) remains the sole
  governing instruction source for this project. Nothing in
  `docs/audit-program/` overrides it — this workspace produces evidence and
  findings *under* it.
- Not a rewrite or a refactor. Findings may recommend changes; this workspace
  does not make them.
- Not authoritative on payroll business rules. Rules live in
  `CLAUDE.md` and `docs/analysis/0.5-business-rules-catalogue.md` —
  audit files reference them, never restate or duplicate them.

## Read-only, end to end

Every stage in this programme, including the future execution-trace
remediation stage, is read-only against `backend/`, `frontend/`, and
`migrations/`. **No stage in this audit implements a code fix.** Stage 13
(consolidated backlog) is the last stage. Production-code remediation —
including for execution-trace gaps — only begins after Stage 13 produces an
approved backlog, and then proceeds as an ordinary sprint under this
project's normal `CLAUDE.md` sprint workflow (`/pm` → plan → `/arch-council`
→ implementation → `/security` / `/auditor` as applicable), outside this
audit workspace.

## Where to start

- [`WORKFLOW.md`](WORKFLOW.md) — how stages open, close, and escalate.
- [`audit-state.md`](audit-state.md) — current stage and status.
- [`_core/`](_core/) — the evidence standard, finding schema, severity
  model, and human-decisions log shared by every stage.

## Stage index

Only Stage 01 is scaffolded so far. Stages 02–13 are created just-in-time
when they open — this index lists the full planned sequence for orientation.

| # | Stage | Status |
|---|---|---|
| 01 | System inventory | scaffolded, not-started |
| 02 | Execution trace & diagnostic-script baseline | not created |
| 03 | Configuration integrity | not created |
| 04 | Original-run and retry parity | not created |
| 05 | Snapshot integrity | not created |
| 06 | UI/API/backend wiring | not created |
| 07 | Silent failures and observability | not created |
| 08 | Data integrity | not created |
| 09 | Security and tenant isolation | not created |
| 10 | Execution-trace remediation (read-only: findings + remediation *design* only) | not created |
| 11 | Scenario testing | not created |
| 12 | Code simplification | not created |
| 13 | Consolidated backlog | not created |

## Historical documents — reverify before trusting

`docs/analysis/`, `docs/audit/`, `docs/architecture/`, and especially
`docs/Buisness Specs & Designs (Drifted)/ARCHITECTURE_LOCK*.md` are reference
material only. They describe the system at a prior point in time and may be
stale relative to current code. Any claim sourced from them must be
reverified against current code, tests, or the database before being logged
as a confirmed finding — see [`_core/evidence-standard.md`](_core/evidence-standard.md).
