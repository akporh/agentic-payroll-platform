# `STORY-0103` — `Employees.tsx` split-action rework — browser UAT BLOCKED

**Origin code(s):** `PT-A1-23` · `EMP-B3`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-4` — Employee Lifecycle Management
**Feature:** `FEAT-11` — Employee page UX
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `tentative`

## Actor

payroll operator

## Problem addressed

A single Edit action mixed HR corrections with payroll-structure changes, so an operator fixing a misspelt name was presented with grade and salary fields whose change has a financial effect.

## Delivered behaviour

The employee row's actions are split into distinct Edit, Change Grade and View Contracts paths, each with its own field set.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-17-employee-crud.md`, item B3.

## Implementation evidence

`frontend/src/pages/Employees.tsx` row actions and their slide-overs.

## Test / review evidence

`docs/test-reports/2026-05-27-sprint-17-full.md` — **B3 browser UAT is recorded as BLOCKED.**

## Decision references

The plan-quality rule this item produced is recorded in `~/.claude/CLAUDE.md`: when a sprint plan adds multiple slide-overs to one page, the plan must enumerate the exact fields in each, because scope drift is otherwise only caught mid-implementation.

## Dependencies

`STORY-0101` — the employee CRUD API these actions call; `STORY-0106` — the UX-track record of the same split.

## Delivery sprint(s)

Sprint 17.

## Delivery history

- Sprint 17 — implemented; browser UAT blocked, so live behaviour was never observed end-to-end.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

**Confidence is `tentative` because verification is incomplete, not because the work is unclear.** The Sprint 17 test report marks B3's browser UAT as BLOCKED. Code-level review passed; live behaviour was not observed. Do not cite this item as evidence of verified UI behaviour.
