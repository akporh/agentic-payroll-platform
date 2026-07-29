# `STORY-0023` — NHF key fix — `employee_rate` (SR9)

**Origin code(s):** `PT-A4-10` · `SR9`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-19` — Statutory deduction correctness
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

employee

## Problem addressed

NHF was read under the wrong key, so the deduction silently resolved to ₦0 — a financial error invisible without comparing against an expected figure.

## Delivered behaviour

NHF reads `employee_rate`, the documented key for that component.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Phase 1 — Sprints 1–6, Execution (A4): “NHF key fix (employee_rate) ✅ (SR9)”.

## Implementation evidence

`backend/domain/payroll/` statutory handlers. The key is recorded in `CLAUDE.md`: “NHF (2.5% of basic, key: `employee_rate`)”.

## Test / review evidence

No dedicated report for Sprints 1–6.

## Decision references

None beyond routine execution.

## Dependencies

None.

## Delivery sprint(s)

Sprints 1–6 (Core MVP).

## Delivery history

- Sprints 1–6 — delivered as SR9.
- Sprint 7 — the same class of key-misalignment defect recurred for health and dev levy, fixed under `STORY-0034` FIX-2/FIX-3.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

This defect class — a statutory component silently resolving to ₦0 because of a key mismatch — recurred at least twice. Whether a structural guard exists against it is not established by this record.
