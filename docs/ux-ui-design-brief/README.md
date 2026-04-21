# UX Design Brief — Agentic Payroll Platform

**Prepared by:** Technical analyst pass over live codebase  
**Date:** 2026-04-14  
**Authoritative source:** All artefacts are derived from the actual code. Where code and documentation conflict, the code wins. All conflicts are recorded in the Drift Log.

---

## What This Folder Is

This folder contains the structured technical artefacts a UI/UX designer needs to design the frontend for a Nigerian payroll bureau platform. It covers every data model, API endpoint, business rule, actor, user journey, screen, sensitive field, status lifecycle, and external integration that is actually implemented in the codebase as of Sprint 7.

---

## Read Order for a UI/UX Agent

Start here, then read artefacts in order:

| File | What it tells you |
|---|---|
| `01-entity-map.md` | Every data model, its fields, and how models relate to each other |
| `02-api-surface.md` | Every endpoint — what it does, what it needs, what it returns |
| `03-business-rules.md` | Payroll calculations and constraints the UI must respect or surface |
| `04-actors.md` | Who uses this system and their scope |
| `05-persona-sketches.md` | Who each actor is, what they need, what would frustrate them |
| `06-user-journey-maps.md` | End-to-end task sequences per actor |
| `07-screen-inventory.md` | Every screen the UI needs — purpose, data, actions, and states |
| `08-data-sensitivity.md` | Every sensitive field — PII, financial, statutory |
| `09-state-flows.md` | Lifecycle diagrams for Payroll Run, Result, Reconciliation, Workspace, Employee |
| `10-integration-touchpoints.md` | External systems, file imports, file exports |
| `11-drift-log.md` | Every conflict between documentation and code, and every ambiguity |

---

## Platform Summary (for orientation)

- **What it does:** Manages payroll for Nigerian companies through a payroll bureau model. Multiple client companies ("workspaces") are managed by one bureau.
- **Domain:** Nigerian payroll — PAYE (cumulative annual method), Pension (8% employee / 10% employer), NHF (2.5% basic), Health Insurance (flat monthly), Development Levy (flat annual).
- **Currency:** NGN (Nigerian Naira). All monetary values use Decimal precision.
- **Data model:** Multi-tenant via `workspace_id`. Every table is scoped to a workspace.
- **Payroll engine:** Deterministic, component-based. Each component has a defined execution priority and calculation method. Full audit trail via component_trace_jsonb.
- **Key workflow:** Collect inputs → Run payroll → Review → Approve → Lock → Reconcile → Mark Paid.
- **Auth:** No RBAC in the current backend. Visual role separation in UI only. See DRIFT-2 in the Drift Log.

---

## Critical Design Constraints

1. **PAID is irreversible.** The UI must require explicit confirmation before the Mark as Paid action. Once PAID, nothing can change.
2. **Exports are gated on LOCKED or PAID.** Do not show export buttons in any other status.
3. **Reconciliation requires LOCKED status.** Disable the reconciliation form if the run is not LOCKED.
4. **New Run requires workspace status LIVE.** Gate this action clearly with an explanation and a path to complete setup.
5. **FAILED employees are excluded from all CSV exports.** The UI must surface this to the user.
6. **No RBAC in backend.** UI role separation is visual only. Flag this to the security team before production deployment.
7. **personal_details_encrypted may not actually be encrypted.** Treat all biodata as plaintext PII in your designs. See DRIFT-1.
