# Agentic Payroll Platform - Phase 1 MVP

## Overview

This project is now accessible and editable via Manus AI.
Bank-grade payroll processing system with metadata-driven rules engine. Phase 1 is a deterministic, audit-first Nigerian payroll engine.
Agentic workflows are **not implemented yet** — the system is designed to be agentic-ready

## 🎯 Phase 1 Goal

Build a payroll MVP that supports:

- Single payroll bureau client (one workspace)
- Monthly payroll for salaried employees only
- Deterministic statutory deductions (PAYE, pensions, etc.)
- Full audit + event traceability
- Manual compliance reporting outputs

## ✅ Phase 1 Scope (Non-Negotiable)

- No AI decision-making
- No autonomous agents
- No multi-tenant scaling yet
- No production deployment yet

Phase 1 is about **trust + correctness first**.

## 🔐 Source of Truth Documents
All contributors and agents must follow:

- docs/ARCHITECTURE_LOCK.md
- docs/INFRASTRUCTURE_DECISIONS.md
- docs/REPLIT_AGENT_GUARDRAILS.md
- Phase 1 Visual Architecture for Nigerian Payroll Platform MVP.md
- phase1_business_spec.md

No schema or logic may deviate from these.

## 📂 Repository Structure

backend/ # FastAPI + domain logic (Sprint 2+)
migrations/ # Alembic schema migrations
docs/ # Architecture lock + business specs
tests/ # Deterministic rule engine tests


## 🧱 Core Architecture

Phase 1 is built around:

- **PostgreSQL** as source of truth
- **Alembic migrations** for schema control
- **Rule config stored as JSONB**
- **Immutable audit/event history**
- tables specified in Phase 1 Visual Architecture for Nigerian Payroll Platform MVP.md


## Plan
- **Sprint 0**: Infrastructure & DevOps Foundation
- **Sprint 1**: Foundation & Data Integrity
- **Sprint 2**: Rules Engine & Deterministic Logic
- **Sprint 3**: Lifecycle, Immutability & Approval
- **Sprint 4**: Explainability & Compliance Output

## Branching Strategy
- main: stable baseline (protected)
- dev: active development branch
- All feature work is merged into dev first
- main only updates via PR when stable


## 🚧 Current Sprint Status
✅ Sprint 1 — Schema Foundation Complete
Core Phase 1 tables are migrated and ERD-aligned.

▶ Sprint 2 — Rule Engine (Next)
Next implementation:
Deterministic PAYE calculation using TAX_BAND
Payroll run execution pipeline

## Founder Note
This project is being built as a trust-first payroll platform.
Correctness and auditability matter more than speed.

Phase 1 proves deterministic payroll can outperform manual bureaus.
