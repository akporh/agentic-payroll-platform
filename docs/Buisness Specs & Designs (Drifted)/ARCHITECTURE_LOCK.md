# ARCHITECTURE LOCK — Phase 1 Payroll MVP

This document is the constitution.
Agents must not deviate.

---

## Scope (Phase 1 Only)

- Single workspace/client
- Salaried employees only
- Deterministic calculations only
- Manual compliance reporting
- Agentic-ready, NOT agentic

---

## Phase 1 Source of Truth

Agents MUST follow:

1. Phase 1 Visual Architecture + ERD
   - Phase 1 Visual Architecture for Nigerian Payroll Platform MVP.md

2. Phase 1 Business Rules + Workflows
   - phase1_business_spec.md

3. Phase 1 Backlog
   - sprint_ready_backlog.md 	

No payroll logic may be implemented without matching these documents.

---

## Core Tables (Phase 1)

- account, workspace, employee
- statutory_rule, tax_band, payroll_rule
- salary_definition
- payroll_run, payroll_result
- audit_log, event_store

---

## State Transitions (Locked)

PAYROLL_RUN:
DRAFT → CALCULATING → CALCULATED → APPROVED → LOCKED

No skipping states.

---

## Audit Requirements

Must write:
- audit_log on every state change
- event_store on every immutable business event

---

## Non-Negotiables

- Postgres + Alembic only
- No schema edits outside migrations
- Work only on dev branch
- No AI inference in payroll logic

---

