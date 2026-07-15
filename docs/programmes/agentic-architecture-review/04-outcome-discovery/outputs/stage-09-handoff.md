# Stage 04 → Stage 09 Handoff (Human Experience)

## Primary UX design task: the exception-resolution workflow

This stage identified exception resolution (`outputs/exception-resolution-outcome.md`) as the single highest-leverage missing outcome in the entire portfolio (F-04-01). It defines the *outcome* (8 stages: issue creation → prioritisation → ownership → evidence → recommended next action → resolution → verification → closure) but explicitly does not design the interface — that's this stage's work. Design considerations to carry in:

- The workflow must serve **three different exception sources** (C6 readiness gaps, C7 anomalies, and eventually C8 reconciliation mismatches) through one shared interface, not three separate ad hoc surfaces.
- Every exception needs a single accountable owner at any point in time — design for this explicitly, not as an afterthought.
- The interface must show evidence (the specific triggering data) alongside every exception, not just an assertion — matching Stage 02's Principle 4.
- Where a recommended next action is shown (a bounded, legitimate AI use per this stage's framing), it must be visually distinguishable from a verified fact, so an operator never confuses "the system suggests X" with "the system confirmed X."

## C3 (Operator Assistant) UX consideration

This stage's measurement framework (`measurement-framework.md`) explicitly warns against measuring chat usage volume as success — design the interface so it doesn't inadvertently *encourage* unnecessary chat interaction either (e.g. burying information behind chat that could be a one-glance UI element). Carried directly from `CONTEXT.md`'s own constraint.

## Onboarding mapping UX consideration (C13)

`outputs/onboarding-outcome-baseline.md` recommends C13 surface a confidence signal per mapped field, so operator attention concentrates on genuinely ambiguous mappings rather than reviewing every field with equal scrutiny. This is a UX design implication worth carrying into Stage 09's work on the onboarding flow.

## What Stage 09 should NOT re-derive

The underlying outcome definitions themselves (`product-opportunity-map.md`, `exception-resolution-outcome.md`) — Stage 09's job is interface design for outcomes already defined here, not re-deriving what the outcomes should be.
