---
name: Audit Programme State
description: Current stage and status tracker for docs/audit-program/
type: project
---

# Audit State

**Next action:** Stage 03 (configuration integrity) closed 2026-07-12.
Review and open Stage 04 (original-run and retry parity). Stage 04 has
not been started — its primary input is finding 03-002 (retry re-resolves
the statutory rule/tax bands live instead of reading the frozen snapshot),
which Stage 04 must attempt to reproduce with a controlled non-production
test before it can move past `plausible`.

## Stage 03 handoff summary

- **03-002** is the primary Stage 04 input — Stage 04 should reproduce the
  statutory-rule original-run/retry divergence using controlled
  non-production execution (insert a test `statutory_rule` row with an
  intervening `effective_from`, run, retry, compare). Status remains
  `plausible` until reproduced.
- **03-003** (dead `employee_contract_snapshot.components_jsonb` column)
  passes to Stage 05 (snapshot integrity — is the snapshot itself complete
  and correct independent of consumption?) and Stage 12 (simplification —
  removal candidate).
- **03-004** (statutory-deduction components can be disabled per workspace;
  D-ARCH-2 guard present but explicitly unenforced) passes to Stage 08
  (data integrity — any live workspace currently doing this?) and Stage 09
  (security/tenant isolation).
- UI coverage gaps, including `pay_cycle.definition_json` (not traced to a
  specific UI control in Stage 03), pass to Stage 06 (UI/API/backend
  wiring).

## Stage status

| # | Stage | Status | Opened | Closed | Blocking issue |
|---|---|---|---|---|---|
| 01 | System inventory | complete | 2026-07-11 | 2026-07-11 | — |
| 02 | Execution trace & diagnostic-script baseline | complete | 2026-07-11 | 2026-07-12 | — |
| 03 | Configuration integrity | complete | 2026-07-12 | 2026-07-12 | — |
| 04 | Original-run and retry parity | not-created | — | — | — |
| 05 | Snapshot integrity | not-created | — | — | — |
| 06 | UI/API/backend wiring | not-created | — | — | — |
| 07 | Silent failures and observability | not-created | — | — | — |
| 08 | Data integrity | not-created | — | — | — |
| 09 | Security and tenant isolation | not-created | — | — | — |
| 10 | Execution-trace remediation (findings + design only — no code changes) | not-created | — | — | — |
| 11 | Scenario testing | not-created | — | — | — |
| 12 | Code simplification | not-created | — | — | — |
| 13 | Consolidated backlog | not-created | — | — | — |

## Open human decisions

Seven pending — see [`_core/human-decisions.md`](_core/human-decisions.md):
- Empty `component_metadata` list silently triggering legacy executor fallback (finding 01-004)
- Second, ORM-based repository directory `backend/infra/db/repositories/` vs. documented single repository layer (finding 01-002)
- Authority/currency of `docs/wrapper-command/` agent-instruction set ("Casper") relative to `CLAUDE.md` (finding 01-013) — resolved (c) treat as non-authoritative
- Should per-employee retry produce the same `execution_trace` step-level footprint as an original run? (finding 02-002)
- Should `export_payroll_register_csv` and siblings be fixed or retired? (finding 02-009)
- Should retry read the frozen statutory-rule snapshot instead of re-resolving live? (finding 03-002)
- Is `employee_contract_snapshot.components_jsonb` meant to ever be read? (finding 03-003)
- Should workspaces be able to disable statutory-deduction components (D-ARCH-2 currently unenforced)? (finding 03-004)

## Notes

- Updated at the end of each working session on this audit, never mid-stage.
- Production-code remediation for any finding does not begin until Stage 13
  produces an approved backlog (see `README.md`, `WORKFLOW.md`).
