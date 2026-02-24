ARCHITECTURE LOCK — Phase 1 Payroll MVP (v1.1 Reality-Aligned)

This document supersedes ARCHITECTURE_LOCK.md (v1.0).

This is the binding constitution for the current implementation.

1. Phase 1 Scope (Locked)

Single workspace (operationally)

Salaried employees only

Deterministic calculations only

Manual compliance reporting

Local environment only

No AI inference

No external integrations

2. Implemented Tables (Current Reality)

Core:

account

workspace

employee

employee_contract

salary_definition

statutory_rule

tax_band

payroll_rule

payroll_run

payroll_result

audit_log

event_store

No new tables allowed without founder approval.

3. Payroll Execution Architecture (Current Implementation)

Layering:

FastAPI (Presentation Layer)  ← To Be Implemented
Application Layer
    - payroll_run_service
    - payroll_run_persister
Domain Layer
    - run_executor
    - batch_processor
    - executor (single employee)
    - state_machine
Infrastructure Layer
    - repositories
    - session


Rules:

Domain layer must remain pure (no DB calls)

Application layer coordinates + persists

Infrastructure layer performs DB writes only

No business logic inside repositories

4. PAYROLL_RUN State Machine (Updated)

Valid transitions:

DRAFT → CALCULATING
CALCULATING → PARTIAL
CALCULATING → CALCULATED
PARTIAL → CALCULATED
CALCULATED → APPROVED
APPROVED → LOCKED

No skipping states.

No deletion of payroll runs.

5. Execution Modes

Allowed:

atomic

isolated

atomic:

Entire batch fails if one employee fails

isolated:

Per-employee failure allowed

Run may move to PARTIAL

No other modes allowed.

6. Audit + Event Requirements (Simplified Phase 1)

Phase 1 does NOT implement CDC.

Instead:

audit_log written at application level

event_store written explicitly at state transitions

payroll_result immutable after insert

Append-only:

event_store

audit_log

payroll_result

7. Determinism Rule

Forbidden:

AI-driven rule selection

Smart retry inference

Auto salary correction

Any dynamic rule discovery

All calculations must be reproducible from:

salary_definition

statutory_rule

tax_band

payroll_rule

employee_contract

8. JSON Handling Rules

All JSON written to DB must:

Convert Decimal → float

Be serialization-safe

Be deterministic

9. API Layer (Required Next)

Phase 1 requires:

FastAPI application

Onboarding route

Payroll trigger route

No UI in backend

No API Gateway abstraction required in Phase 1.

FastAPI itself acts as entry boundary.

10. What Is Explicitly Deferred

CDC

Event replay

Multi-workspace management

External bank integrations

Compliance auto-submission

AI validation

