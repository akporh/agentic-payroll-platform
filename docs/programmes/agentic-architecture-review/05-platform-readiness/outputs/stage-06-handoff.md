# Stage 05 → Stage 06 Handoff (Compliance & Controls)

## Statutory-rule change management (C12) — confirmed entirely greenfield

`outputs/statutory-change-platform-readiness.md` confirms zero admin route, zero application-level write path, zero duplicate-validation, zero approval-record mechanism, and zero preview/impact-analysis capability exist today. This is Stage 06's primary design task — not an extension of an existing surface.

## Audit-trail gap directly affects compliance evidence

`outputs/audit-coverage-assessment.md` reconfirms F-01-40: `audit_log`/`event_store` cover only `payroll_run` transitions. Any compliance-approval record for a statutory-rule change (who approved, when, citing what source) needs this audit mechanism generalized beyond `PAYROLL_RUN` — currently it cannot record a statutory-rule-change approval at all.

## No authentication exists — compliance attribution has no foundation

`outputs/event-notification-readiness.md` confirms zero auth mechanism exists anywhere in the application. Any compliance workflow requiring "who approved this" is currently unbuildable in a trustworthy way — there is no verified identity to attribute an approval to.

## Reconciliation workspace scoping — a tenant-isolation compliance concern, not just a technical one

`outputs/reconciliation-scoping-assessment.md` confirms the gap is worse than previously known: routes that appear workspace-scoped to an API consumer actually aren't. This has compliance implications (data isolation between bureau clients) beyond the technical security framing — Stage 06 may want to treat this as a control-failure item, not purely Stage 07's remit.

## What Stage 06 should NOT re-derive

Whether C11 should be restricted to detect/compare/propose — already decided (D-02-04). Whether C12 is a separate capability from C11 — already decided. Stage 06's job is designing the compliance workflow within these already-fixed boundaries.
