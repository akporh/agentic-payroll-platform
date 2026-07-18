# Stage 11 Evidence: Business-Context Document Excerpts

Transient live-read excerpts duplicated per `_core/EVIDENCE-STANDARD.md` (these files sit outside the git repository, so path:line citation alone is insufficient — the excerpt is the durable record). All reads 2026-07-18. Repository state for repo-internal citations: commit `4abafdc`, branch `uat`, clean tree.

## 1. `Clients/Sandy/_PRODUCT/EP-004_phase2-agentic/FEAT-021_saas-multi-tenant_FUTURE.md` (live read 2026-07-18, full file)

```markdown
# FEAT-021 — Agentic SaaS Multi-Tenant Platform

## What this delivers
A commercially available SaaS product that allows multiple payroll bureaus to run the platform independently, each with their own isolated workspace and data.

## Acceptance criteria
- TBD — to be scoped after Phase 1 closure

## Status
FUTURE

## Sprint(s)
Not yet started

## Notes
Current architecture has multi-tenant workspace scoping in place. The SaaS layer (billing, onboarding, tenant management) is the Phase 2 work.
```

Unchanged in substance from Stage 02's S-05 read (2026-07-12): still a stub, still unscoped, still `FUTURE`.

## 2. `Clients/Sandy/_PRODUCT/EP-004_phase2-agentic/FEAT-020_ai-payroll-engine_FUTURE.md` (live read 2026-07-18, header)

```markdown
# FEAT-020 — AI-Powered Payroll Engine

## What this delivers
An agentic layer on top of the deterministic engine that detects anomalies, flags edge cases, and suggests corrections — reducing manual review time for payroll bureau operators.

## Acceptance criteria
- TBD — to be scoped after Phase 1 closure

## Status
FUTURE
```

## 3. `Clients/Sandy/CLAUDE.md` (documented business intent, live read 2026-07-18)

> **Phase 1 (MVP — current):** Deterministic rule-based payroll engine. No AI. Processes payroll according to fixed rules. Needs to be completed and closed off.
>
> **Phase 2 (future):** Agentic SaaS payroll platform. AI-powered. Broader market. Does not start until Phase 1 MVP is delivered and closed.

> **Client:** Sandy — family payroll bureau (HR outsourcing firm). First completed client for onAiR.

Treated as documented intent (evidence type 4), not as demand evidence: it records what the business *plans*, not what any client has asked for or would pay for.

## 4. Absence check: registered commercial-demand evidence

Sweep performed 2026-07-18 across the programme's registered sources (`_inputs/source-register.md` S-01–S-09) and all stage `decisions.md` files: **no evidence-type-5 human statement and no registered external source records client demand, willingness to pay, competitive pricing, or a client request for any of the 15 capabilities.** The only commercial-intent records are the type-4 documents excerpted above. This absence grounds F-11-02 and evidence gaps EG-004/EG-005.
