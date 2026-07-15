# Stage 05 → Stage 07 Handoff (Security & Identity)

## Headline: zero authentication exists anywhere in the application

`outputs/event-notification-readiness.md` confirms — independently corroborated by `docs/audit-program/09-security-tenant-isolation/findings.md` (09-000) — that no JWT/auth dependency exists on any route. `workspace_id` is a plain, caller-supplied, unauthenticated value throughout the application today. This is the single most important fact for Stage 07 to carry forward: every workspace-scoping assessment in this stage (and Stage 01) implicitly assumes an honest caller, because there is currently no mechanism to enforce otherwise.

## Reconciliation workspace scoping — worse than previously documented

`outputs/reconciliation-scoping-assessment.md`: the "workspace-scoped" reconciliation routes (`backend/api/routes/payroll.py:1293-1334`) accept a `workspace_id` path parameter and **never use it** — a false impression of isolation for any API consumer or frontend developer who assumes the route enforces what its URL structure implies. This is a distinct, arguably more severe finding than the underlying data-layer gap alone, since it could mislead a security review that only checks "does this route accept a workspace_id parameter" without checking whether it's enforced.

## Two newly-identified tool-wrapping risks

`outputs/tool-readiness-baseline.md` identifies two functions not previously flagged in Stage 01: `load_inputs_for_run(payroll_run_id)` (no workspace_id parameter at all — safe today only because of upstream caller discipline) and `workspace_info()` (picks an arbitrary workspace with `LIMIT 1`, no scoping whatsoever). Both should be in scope for Stage 07's review, independent of whether any tool ever wraps them — `workspace_info()` in particular may already be producing wrong results for existing non-tool callers in a multi-workspace deployment; worth Stage 07 checking its current callers directly.

## Defence-in-depth requirement, reaffirmed

Per D-02-02/Principle 11 (Stage 02/03): every future tool must independently verify workspace ownership, never trusting the underlying function. This stage's evidence (the reconciliation gap, plus the two newly-identified functions) demonstrates concretely why that principle exists — in all three cases, "the function already works for its current caller" was true and irrelevant to whether it's safe to wrap directly.

## What Stage 07 should NOT re-derive

The general principle that tools need independent scoping checks — already established. Stage 07's job is the security-specific review of the auth build (once it exists) and verification that the closure evidence in `readiness-closure-plan.md` actually meets a security bar, not re-deriving the principle itself.
