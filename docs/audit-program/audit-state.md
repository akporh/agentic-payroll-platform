---
name: Audit Programme State
description: Current stage and status tracker for docs/audit-program/
type: project
---

# Audit State

**Next action:** Stage 05 (snapshot integrity) has produced its full
inventory, immutability/timing analysis, and `findings.md` (05-001–05-005)
but is **not yet marked complete** — awaiting explicit review. Key result:
the v2 statutory snapshot is **already sufficient** — 04-001 was always a
retry-read-path gap, never a snapshot-completeness gap, which bounds the
remediation to a narrow read-path change (§9's canonical contract). Two new
findings: 05-001 (snapshot creation can fail silently, S2) and 05-004
(immutability enforcement inconsistent across snapshot tables, S2). **`04-001`
remains a confirmed S0 release blocker**, unchanged and not re-litigated.

## Stage 04 handoff summary

- **`04-001` (S0, confirmed, release blocker):** retry re-resolves the
  statutory rule/tax bands live instead of reading the frozen
  `rules_context_snapshot.statutory_rule`; reproduced with a controlled,
  self-cleaning non-production test (zero residue confirmed). Canonical fix
  direction already decided: retry must consume the frozen snapshot content;
  legacy runs lacking v2 statutory snapshot content must hard-fail, never
  silently fall back to a live re-query. Stage 05 validates and specifies
  this fix (read-only — no code changes in Stage 05); the actual remediation
  sprint follows immediately after, ahead of Stage 13, before any live
  payroll processing or production release.
- **`04-002` (S1, confirmed):** no persisted field records which
  statutory-rule version a `payroll_result` row was actually calculated
  under — compounds `04-001` by preventing retroactive detection. Passes to
  Stage 05 (should statutory identity be persisted per result?), Stage 07,
  and Stage 10.
- **`04-004` (unconfirmed):** reconciliation-refresh behaviour on retry
  completion was not investigated this stage — passes to Stage 08.
- The controlled reproduction script
  (`04-original-run-retry-parity/evidence/statutory_divergence_controlled_test.py`)
  passes to Stage 11 as the basis for a formal regression scenario once the
  fix lands.

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
| 04 | Original-run and retry parity | complete | 2026-07-12 | 2026-07-12 | — |
| 05 | Snapshot integrity | in-progress | 2026-07-12 | — | — |
| 06 | UI/API/backend wiring | not-created | — | — | — |
| 07 | Silent failures and observability | not-created | — | — | — |
| 08 | Data integrity | not-created | — | — | — |
| 09 | Security and tenant isolation | not-created | — | — | — |
| 10 | Execution-trace remediation (findings + design only — no code changes) | not-created | — | — | — |
| 11 | Scenario testing | not-created | — | — | — |
| 12 | Code simplification | not-created | — | — | — |
| 13 | Consolidated backlog | not-created | — | — | — |

## Open human decisions

Nine pending, one resolved this session — see [`_core/human-decisions.md`](_core/human-decisions.md):
- Empty `component_metadata` list silently triggering legacy executor fallback (finding 01-004)
- Second, ORM-based repository directory `backend/infra/db/repositories/` vs. documented single repository layer (finding 01-002)
- Authority/currency of `docs/wrapper-command/` agent-instruction set ("Casper") relative to `CLAUDE.md` (finding 01-013) — resolved (c) treat as non-authoritative
- Should per-employee retry produce the same `execution_trace` step-level footprint as an original run? (finding 02-002)
- Should `export_payroll_register_csv` and siblings be fixed or retired? (finding 02-009)
- Should retry read the frozen statutory-rule snapshot instead of re-resolving live? (finding 03-002) — superseded by 04-001's resolution below, effectively decided: yes
- Is `employee_contract_snapshot.components_jsonb` meant to ever be read? (finding 03-003)
- Should workspaces be able to disable statutory-deduction components (D-ARCH-2 currently unenforced)? (finding 03-004)
- Should 05-001 (silent snapshot-creation failure) and 05-004 (inconsistent immutability enforcement) be bundled into the 04-001 remediation sprint or deferred to Stage 13? (findings 05-001/05-004)
- ~~S0 — 04-001 urgency and fix direction~~ — **resolved 2026-07-12**: confirmed S0 release blocker; Stage 05 validates and specifies the fix; remediation follows immediately after, ahead of Stage 13, before any live payroll processing or production release. Full decision text in `_core/human-decisions.md`.

## Notes

- Updated at the end of each working session on this audit, never mid-stage.
- Production-code remediation for any finding does not begin until Stage 13
  produces an approved backlog (see `README.md`, `WORKFLOW.md`) — **except
  `04-001`**, which is an explicitly decided exception: it moves into an
  immediate remediation sprint as soon as Stage 05 produces a validated
  snapshot-first fix specification, ahead of Stage 13 and before any live
  payroll processing or production release. No other finding carries this
  exception.
