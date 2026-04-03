# ARCHITECTURE LOCK — PHASE 1 (Authoritative)

This document defines the enforced architecture for Phase 1.
All automated agents (Replit, AI tools) MUST follow this strictly.

This system is a MODULAR MONOLITH.
It is NOT a microservices architecture.
There is NO API Gateway.
There is NO CDC mechanism.
There is NO message queue.
There is NO distributed execution.

Future scalability considerations are OUT OF SCOPE.

------------------------------------------------------------
1. Runtime Architecture
------------------------------------------------------------

Frontend (Next.js)
        ↓
FastAPI (API Layer)
        ↓
Application Layer
        ↓
Domain Layer (Pure)
        ↓
Infrastructure Layer (Repositories)
        ↓
PostgreSQL

------------------------------------------------------------
2. Layer Responsibilities (STRICT)
------------------------------------------------------------

API Layer (backend/api/)
- Defines FastAPI routes only
- Performs request validation (Pydantic)
- Calls application layer functions
- MUST NOT:
    - Contain business logic
    - Call repositories directly
    - Execute SQL
    - Manage transactions
    - Perform state transitions

Application Layer (backend/application/)
- Orchestrates domain + repositories
- Manages transactions
- Coordinates persistence
- Converts domain output to persistence calls
- MUST NOT:
    - Contain business rule logic
    - Contain SQL
    - Import from API layer

Domain Layer (backend/domain/)
- Contains pure deterministic business logic
- No database access
- No FastAPI imports
- No SQL
- No session handling
- State machine logic lives here
- Payroll calculations live here
- Validator logic lives here

Infrastructure Layer (backend/infra/)
- Contains repositories only
- Handles SQLAlchemy sessions
- Performs SQL execution
- No business decisions
- No state transitions

------------------------------------------------------------
3. Data & Persistence Rules
------------------------------------------------------------

- All DB access must go through repositories.
- No raw SQL inside domain or API layer.
- Transactions are controlled by application layer.
- JSONB is used for flexible configuration storage.
- Audit and event entries are written explicitly by application layer.
- There is NO CDC mechanism in Phase 1.

------------------------------------------------------------
4. Payroll Execution Rules
------------------------------------------------------------

- Payroll execution is deterministic.
- State transitions must use the state machine.
- Execution modes:
    - atomic
    - isolated
- Partial execution is allowed in isolated mode.
- Domain layer must remain side-effect free.

------------------------------------------------------------
5. Onboarding Rules
------------------------------------------------------------

- Configuration must pass hard validation before load.
- Loader must run inside transaction.
- Duplicate workspace loads must be prevented.
- API layer must never insert configuration directly.

------------------------------------------------------------
6. What Is Explicitly Forbidden
------------------------------------------------------------

Do NOT:
- Introduce microservices
- Introduce API Gateway
- Introduce message queues
- Introduce CDC
- Add business logic to routes
- Add SQL outside repositories
- Add cross-layer imports
- Move state machine out of domain
- Move calculation logic into application layer

------------------------------------------------------------
7. Deferred Architecture (Future Phases)
------------------------------------------------------------

The following are explicitly deferred:

- CDC-based audit streaming
- Async job queues
- Distributed workers
- Event-driven external integrations
- Multi-tenant routing gateway
- Service separation into deployable units

These are roadmap items and must NOT be implemented in Phase 1.

------------------------------------------------------------
8. Guiding Principle
------------------------------------------------------------

This system prioritizes:

- Determinism
- Auditability
- Explicit state transitions
- Layer separation
- Simplicity over distribution

Stability over sophistication.
