# Infrastructure Decisions (Phase 1 — Non-Negotiable)

Document Purpose:
This file defines the fixed infrastructure constraints for Phase 1.
All AI agents (Replit or otherwise) MUST follow these rules.
No architectural deviations are allowed without explicit founder approval.

---

## 1. Tech Stack (Locked)

Backend Language:
- Python 3.9+

Framework:
- FastAPI (Phase 1 API layer)

Database ORM:
- SQLAlchemy (minimal usage)

Migrations:
- Alembic ONLY

---

## 2. Database (Locked)

Database Engine:
- PostgreSQL 15

Environment:
- Local Postgres for Phase 1 development

Database Name:
- payroll_dev

Rule:
- No SQLite in production paths
- No schema changes outside Alembic migrations

---

## 3. Migration Policy (Strict)

All schema changes MUST be:
- One Alembic revision per change
- Reviewed before applying
- ERD-aligned (no invented tables/columns)

Forbidden:
- Auto-generating full ERD migrations without approval
- Direct DB edits

---

## 4. Branching + Source Control (Locked)

Branches:
- main = stable baseline (do not commit directly)
- dev = active development

Rule:
- Replit agents must work ONLY on `dev`
- All changes must be committed with clear messages

---

## 5. Environments (Phase 1)

Active:
- dev (local)

Deferred:
- staging (Phase 2)
- production (Phase 2)

No cloud deployment work is required in Phase 1.

---

## 6. Hosting Target (Phase 1)

Phase 1 Hosting:
- Local only

Phase 2 Target:
- DigitalOcean Droplet + Managed Postgres

Rule:
- No AWS-specific services in Phase 1

---

## 7. Secrets Management (Strict)

Allowed:
- Local `.env` (never committed)
- `.env.example` in repo

Forbidden:
- Hardcoded credentials
- Committing API keys or DB URLs

---

## 8. Logging + Audit (Phase 1 Requirement)

System must support:
- AUDIT_LOG table
- EVENT_STORE table

Logging Standard:
- Structured JSON logs (Python logging)

Forbidden:
- Silent failures
- Untracked state transitions

---

## 9. Phase 1 Scope Constraints

Phase 1 is deterministic only:
- No agentic execution
- No AI decision-making in payroll logic
- Manual compliance reporting only

System must remain:
- Explainable
- Auditable
- Reproducible

---

## 10. Replit Agent Rules (Non-Negotiable)

Replit must:
- Implement ONLY the assigned backlog story
- Never introduce new frameworks
- Never modify schema without migration
- Never change ERD structure

If unclear:
STOP and ask founder.





