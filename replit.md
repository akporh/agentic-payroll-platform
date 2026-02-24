# Agentic Payroll Platform — Phase 1 MVP

## Overview

This is a bank-grade Nigerian payroll processing platform, currently in Phase 1 (MVP). The goal is to build a deterministic, audit-first payroll engine for a single payroll bureau client. It handles monthly payroll for salaried employees with statutory deductions (PAYE, pensions) and full audit/event traceability.

**Phase 1 is explicitly NOT agentic.** There is no AI, no autonomous agents, no multi-tenant scaling. The focus is on trust and correctness — getting payroll calculations right with complete auditability. The architecture is designed to be agentic-ready for future phases.

Key payroll flow: employees are set up with salary definitions, statutory rules (Nigerian tax bands, pension) are configured, and payroll runs go through a strict state machine: `DRAFT → CALCULATING → CALCULATED → APPROVED → LOCKED`. No state may be skipped.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Tech Stack (Locked — No Deviations)
- **Backend:** Python 3.9+ with FastAPI
- **ORM:** SQLAlchemy (minimal usage)
- **Database:** PostgreSQL 15 (database name: `payroll_dev`)
- **Migrations:** Alembic only — all schema changes must go through Alembic revisions
- **Testing:** pytest with pytest-asyncio and httpx for API testing

### Source of Truth Documents
All code must comply with these documents (found in `docs/`). If there's ever a conflict between code and these docs, the docs win:
- `docs/ARCHITECTURE_LOCK.md` — the constitution; defines locked scope, tables, and state transitions
- `docs/INFRASTRUCTURE_DECISIONS.md` — fixed infrastructure constraints
- `docs/REPLIT_AGENT_GUARDRAILS.md` — rules for the coding agent (treat yourself as a junior engineer executing tickets)
- `docs/Phase 1 Visual Architecture for Nigerian Payroll Platform MVP.md` — ERD and architectural diagrams
- `docs/phase1_business_spec.md` — complete business rules and process specification

### Database Schema (Core Tables)
The schema is defined through Alembic migrations in `migrations/versions/`. The migration chain is:

1. `d6f59caea39f` — Core tables: `account`, `workspace`, `employee`
2. `dd26843b5e36` — `statutory_rule` (country-specific calculation rules like PAYE)
3. `a744f3e556a4` — `tax_band` (progressive tax brackets linked to statutory rules)
4. `76566966d3b3` — `audit_log` (immutable audit trail per workspace)
5. `4758b5bfe177` — `event_store` (event sourcing for aggregate changes)
6. `77b86ab4832a` — `payroll_run` (the actual payroll execution with status state machine)
7. `45ad7410d53e` — `payroll_result` (per-employee results within a payroll run)
8. `77c459d173ca` — Missing ERD columns: `rules_context_snapshot` on payroll_run, `version_number` on statutory_rule, effective dates on tax_band
9. `94a312394013` — `salary_definition` (employee salary components with effective dating)
10. `67a617d75a57` — `payroll_rule` (workspace-specific custom rules)

### Key Architectural Decisions

**Single-tenant for now, multi-tenant ready:** The `account → workspace` hierarchy exists from day one even though Phase 1 only has one workspace. All data is scoped to a workspace_id for future tenant isolation.

**JSONB for flexible rule storage:** Statutory rules, salary components, tax logic, and payroll rules all use JSONB columns. This allows the rules engine to be metadata-driven without schema changes for every new rule type.

**Event sourcing + audit logging:** Both `audit_log` and `event_store` tables exist to provide full traceability. Every change to payroll entities must be logged. This is a compliance requirement for payroll systems.

**Deterministic calculations only:** No AI, no probabilistic logic. Every payroll result must be reproducible given the same inputs. The `calculations_snapshot_json` on `payroll_result` and `rules_context_snapshot` on `payroll_run` capture the exact rules used at calculation time.

**Strict state machine:** Payroll runs follow `DRAFT → CALCULATING → CALCULATED → APPROVED → LOCKED`. This prevents accidental modifications to finalized payroll.

### Project Structure
```
backend/
  api/
    main.py              # FastAPI app entry point (uvicorn target)
    routes/
      health.py          # GET /api/v1/health
  application/           # Orchestration services (payroll run, persistence)
  domain/                # Pure domain logic (calculations, rules, state machine)
  infrastructure/        # Database repositories
migrations/              # Alembic migrations (schema is defined here)
  versions/              # Individual migration files
docs/                    # Architecture lock, business specs, planning docs
  planning/              # Roadmap, user story maps, backlog
tests/                   # Deterministic rule engine tests
```

### Hard Rules for the Agent
- Only implement what is explicitly assigned — no extra features or refactors
- All schema changes go through Alembic migrations, never direct SQL
- All tables must match the ERD exactly — no invented columns or relationships
- Only use FastAPI, SQLAlchemy, Alembic, and standard Python libs
- No SQLite in production code paths
- If uncertain about scope, stop and ask

## External Dependencies

### Database
- **PostgreSQL 15** — the single source of truth for all payroll data. Must be provisioned and available. Database name is `payroll_dev` for development.

### Python Packages (from requirements.txt)
| Package | Purpose |
|---------|---------|
| `fastapi` 0.109.0 | API framework |
| `uvicorn` 0.27.0 | ASGI server |
| `pydantic` 2.5.3 | Request/response validation |
| `sqlalchemy` 2.0.25 | ORM / database interaction |
| `alembic` 1.13.1 | Database migration management |
| `psycopg2-binary` 2.9.9 | PostgreSQL driver |
| `jsonschema` 4.21.0 | JSON schema validation (for JSONB rule validation) |
| `pytest` 7.4.4 | Testing framework |
| `pytest-asyncio` 0.23.3 | Async test support |
| `httpx` 0.26.0 | HTTP client for API testing |
| `python-dotenv` 1.0.0 | Environment variable management |

### External Services
- **None in Phase 1.** No external API integrations, no payment processors, no tax filing services. The system produces compliance data that humans file manually. External integrations are planned for future phases.