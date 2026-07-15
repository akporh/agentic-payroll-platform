# Stage 01: Current Operating Model — Context

## Status
Investigation complete 2026-07-11 — 46 confirmed findings recorded, 0 draft, 0 parked/rejected. Awaiting human gate approval before Stage 02 may begin (see `decisions.md`).

## Scope

Produce an evidence-backed description of how the payroll platform currently operates, from workspace/tenant creation through payroll completion and post-run investigation. Descriptive only — no recommendations, no agent design, no architecture assessment, no production code changes.

Areas inspected (per instruction from human reviewer):

1. Workspace and tenant creation
2. Onboarding and structural configuration
3. Salary components and metadata
4. Grades and designations
5. Pay-cycle and rule-set configuration
6. Employee registration
7. Employment or contract setup
8. Timesheet and payroll-input collection
9. Input validation and resolution
10. Payroll-run creation
11. Calculation execution
12. Snapshot creation and use
13. Execution tracing
14. Retry and partial-failure handling
15. Reconciliation
16. Approval, locking and payment-related states
17. Audit records
18. Existing operator-facing UI flows
19. Post-payroll investigation and correction
20. Statutory-rule maintenance

Evidence sources: `backend/api/routes/`, `backend/application/`, `backend/domain/payroll/`, `backend/infra/repositories/`, `backend/infra/db/models/`, `migrations/versions/`, `frontend/src/pages/`.

## Questions this stage answers

For each of the 20 areas above: what does the current implementation actually do (models, constraints, state transitions, routes, services), and — where intent is documented (CLAUDE.md, migrations, specs) — how does current implementation compare to intended design?

## Explicitly out of scope

- Whether the current design is good or should change (that's Stage 02/08/12)
- The proposed/target agent architecture (Stage 03, 12)
- Any recommendation
- Any code, migration, or data modification
- Treating architecture docs, roadmaps, or prior sprint notes as proof that something is implemented — only code/migrations/data reads count as implementation evidence

## Inputs consumed

None — this is the first stage, no prior confirmed findings exist. New sources recorded in `_inputs/source-register.md` as they are consulted.

## Next action

**Human review of `findings.md` and `outputs/current-operating-model-summary.md`, then explicit gate approval to close Stage 01 and permit Stage 02.**
