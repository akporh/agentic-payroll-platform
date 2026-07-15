# Stage 05 Output: Event, Notification, and Exception-Workflow Foundation Readiness (C2)

**Headline: every component this assessment checked is entirely greenfield.** Nothing has landed since Stage 01/02/03 proposed Track V (Agent Foundation). This is the single most consequential readiness gap in this stage's findings, since C2 is a named prerequisite for the highest-priority outcome Stage 04 identified (the exception-resolution workflow, F-04-01).

## Findings, re-verified against current committed code

| Component | Status | Evidence |
|---|---|---|
| Event-store consumer/dispatcher | **Does not exist** | `event_store` (`backend/infra/repositories/event_store_repo.py:16`) is write-only — grep for "outbox", "dispatcher", "EventConsumer" across all of `backend/` returns zero matches. Nothing reads from `event_store` after it's written. |
| `workspace_notification` table/model | **Does not exist** | Zero matches for "notification" across `backend/infra/db/models/` and `migrations/versions/`. |
| JWT/authentication mechanism | **Does not exist at all** | Zero matches for "jwt", "Authorization", "Bearer", "get_current_operator", "OAuth2", or any auth dependency across `backend/`. No `operator`-named file exists. Every route in `backend/api/main.py` is registered with zero `Depends(...)` auth check. `workspace_id` is a plain caller-supplied string today — not a security boundary at all. |
| Audit/event coverage (F-01-40 re-check) | **Confirmed, unchanged, coverage not widened** | Current call sites for `save_audit_log`: `payroll.py:954`, `payroll_approval_service.py:97,170,245`, `payroll_retry_service.py:797`, `payroll_run_persister.py:98`. Current call sites for `save_event`: `payroll.py:960`, `payroll_approval_service.py:98,171,246`, `payroll_retry_service.py:803`, `payroll_run_persister.py:104`. All still hardcoded to `entity_type`/`aggregate_type = "PAYROLL_RUN"` (`backend/domain/payroll/audit_events.py:34,60`). `reconciliation_service.py` and the employee/salary-definition/pay-cycle PATCH routes still have zero calls to either function. The `68e9307` remediation added one more instance of the same PAYROLL_RUN-only pattern (the new `FAILED` status also writes via the same shared builders) — it did not generalize the mechanism to any other entity type. |
| Exception/issue tracking, ownership, resolution workflow | **Does not exist** | Zero matches for an exception-queue/issue-tracking model or route anywhere in `backend/`. Incidental uses of the English words "exception"/"resolution" in docstrings/comments do not constitute a workflow. |

## Cross-reference: docs/audit-program independently confirms the auth gap

`docs/audit-program/09-security-tenant-isolation/findings.md:12-17` (finding 09-000) independently states: "No authentication mechanism exists anywhere in the application... `workspace_id` is a plain caller-supplied string, not a security boundary." This matches this stage's own direct re-verification exactly — two independent investigations, same conclusion, from different evidence-gathering passes.

## What this means for C1 (Identity & Auth Foundation)'s priority

Stage 03 already reclassified C1/C2 as deterministic platform engineering, sequenced first in Stage 04's prioritisation signal (C1 → C2 → ...). This stage's re-verification confirms that sequencing is not just theoretically correct but urgently so: **there is currently zero authentication anywhere in this application.** Every workspace-scoping gap this and prior stages have found (F-01-33 reconciliation, and the two new gaps in `outputs/tool-readiness-baseline.md`) exists in a system where `workspace_id` itself is an unauthenticated, caller-supplied value — meaning even a "correctly scoped" query today only enforces isolation against an honest caller, not a malicious one. This is a materially more severe framing than treating each scoping gap as an isolated bug: **the entire workspace-isolation model currently has no enforcement layer underneath it.**

## What this means for the exception-resolution workflow (F-04-01) and C2-dependent capabilities

C2, the notification/event foundation, is not partially built and needing extension — it is 100% unbuilt. Any estimate of "minimum viable platform closure" for the exception-resolution workflow must start from zero: a transactional outbox, new domain events for the specific triggers Stage 04 named (reconciliation MISMATCH, employee ENROLLED, employee STATUS CHANGED, payroll input SUBMITTED — per the source architecture document's own Track V design, still unbuilt), an event consumer worker, and a notification table are all greenfield work.

## Minimum viable platform closure (not final UI design, per this stage's scope)

1. **Auth (C1)** — an `operator` table, JWT issuance, and a `get_current_operator` dependency wired into every route. This is the hard prerequisite beneath everything else in this list.
2. **Event completeness + outbox** — the transactional outbox pattern plus the four named missing events, emitted in the same transaction as the state change they represent.
3. **Event consumer** — a polling worker (APScheduler, per the source document's own technology decision) that moves outbox entries into `event_store` and can dispatch to a notification writer.
4. **Notification table** — `workspace_notification` (workspace_id, operator_id, type, message, entity_ref, read_at, created_at), in-app only for the first version.
5. **Exception data model** — a new table (not yet named anywhere) recording issue creation, ownership, evidence links, resolution, and closure — the structural backbone `outputs/../04-outcome-discovery/outputs/exception-resolution-outcome.md`'s eight-stage outcome depends on.

None of items 1-5 exist today in any form. This is the platform-readiness reality Stage 06/08 must plan against.
