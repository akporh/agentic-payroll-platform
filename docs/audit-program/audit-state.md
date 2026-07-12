---
name: Audit Programme State
description: Current stage and status tracker for docs/audit-program/
type: project
---

# Audit State

**Next action:** Stage 03 (configuration integrity) has produced its
configuration catalogue, precedence map, duplicate-representation and
dead-configuration registers, and `findings.md` (03-001–03-005) but is
**not yet marked complete** — awaiting explicit review/approval, same
pattern as Stage 02. Flagship finding: 03-002 (retry re-resolves the
statutory rule/tax bands live instead of reading the frozen snapshot —
plausible silent original-run/retry divergence risk). Seven human
decisions remain pending — see below.

## Stage status

| # | Stage | Status | Opened | Closed | Blocking issue |
|---|---|---|---|---|---|
| 01 | System inventory | complete | 2026-07-11 | 2026-07-11 | — |
| 02 | Execution trace & diagnostic-script baseline | complete | 2026-07-11 | 2026-07-12 | — |
| 03 | Configuration integrity | in-progress | 2026-07-12 | — | — |
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
