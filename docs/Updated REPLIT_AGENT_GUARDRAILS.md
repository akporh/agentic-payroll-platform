🔥 Updated REPLIT_AGENT_GUARDRAILS.md

Replace its content with:

Replit Guardrails (Phase 1 — v1.1)

Replit is a junior engineer. It executes stories only.

All work must comply with:

ARCHITECTURE_LOCK_V1_1.md

INFRASTRUCTURE_DECISIONS.md

phase1_business_spec.md

If conflict exists:

ARCHITECTURE_LOCK_V1_1.md wins.

1. Scope Rule

Implement ONLY the assigned story.

Forbidden:

New tables

New frameworks

State machine changes

Architecture refactors

Silent improvements

If unsure: STOP.

2. Database Rules

PostgreSQL only

Alembic for all schema changes

No invented columns

No raw schema edits

Must match ERD + current migrations

3. Layer Discipline

Domain:

Pure functions only

No DB access

Application:

Orchestrates

Calls persister

Infrastructure:

Repositories only

No business logic

4. State Machine Discipline

Must follow:

DRAFT → CALCULATING → PARTIAL → CALCULATED → APPROVED → LOCKED

No deviations.

5. Execution Modes

Allowed only:

atomic

isolated

No new modes.

6. Deterministic Rule

No AI logic.
No auto corrections.
No inference.

7. Required Output After Every Task

Replit must provide:

Files changed

Why change matches story

What was NOT modified

8. Stop Conditions

Replit must STOP if:

State machine conflict

Schema conflict

Story requires architecture change

ERD mismatch

Ask founder instead.