# Replit Agent Guardrails (Phase 1)

Purpose:
Replit is a junior engineer. It must execute tickets, not design systems.

All work must comply with:
- ARCHITECTURE_LOCK.md
- INFRASTRUCTURE_DECISIONS.md

No exceptions without founder approval.

---

## 1. Scope Rule (Hard)

You may implement ONLY the single assigned story.

Forbidden:
- Extra features
- “Nice improvements”
- Refactors outside ticket scope
- New tables or new services not requested

If uncertain: STOP.

---

## 2. Database Rules (Hard)

- PostgreSQL only
- Schema changes ONLY via Alembic migrations
- No direct SQL edits in production paths
- No invented columns or relationships

All tables must match ERD.json exactly.

---

## 3. No New Frameworks

Allowed:
- FastAPI
- SQLAlchemy
- Alembic
- Standard Python libs

Forbidden without approval:
- Django
- Prisma
- ORMs beyond SQLAlchemy
- Event bus frameworks
- Workflow engines

---

## 4. No Agentic Logic in Phase 1

Phase 1 is deterministic.

Forbidden:
- AI-driven decisions
- Autonomous rule inference
- “Smart” payroll corrections

Only explicit rules + calculations.

---

## 5. File Boundaries

Code must stay inside:

- backend/
- migrations/
- tests/
- docs/

Do not create new top-level directories.

---

## 6. Commit Discipline

All work must include:

- Small commits
- Clear messages
- No commits to main
- Work only on dev

Commit format:

feat: ...
fix: ...
chore: ...
docs: ...

---

## 7. Testing Requirement

Every calculation change must include:

- Unit test
- Deterministic expected output

No untested payroll logic.

---

## 8. Output Requirement

For every task, Replit must provide:

- Files changed
- Why it matches acceptance criteria
- What was NOT changed

---

## 9. Stop Conditions

Replit must STOP if:

- ERD conflict appears
- Story requires missing requirements
- Schema change is unclear
- Scope expands beyond ticket

Ask founder instead of guessing.

---

## Founder Authority

Founder approval is required for:

- Any new table
- Any new dependency
- Any architecture change
- Any cloud deployment step

