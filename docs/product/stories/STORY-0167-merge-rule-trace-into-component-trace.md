# `STORY-0167` — N1 / WI-08 — merge `_rule_trace` into `component_trace_jsonb`; add `rate_basis`

**Origin code(s):** `N1` · `WI-08`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-1` — Correctness, Audit & Snapshot
**Feature:** `FEAT-1` — Payroll calculation trace auditability
**Classification:** `technical enabler`
**Status:** `backlog`
**Confidence:** `requires human classification`

## Actor

auditor

## Problem addressed

`apply_payroll_rules()` builds a `_rule_trace` recording how each rule evaluated, and the executor discards it unconditionally. Rule evaluation outcomes are therefore unverifiable from the database — the trace shows the resulting component but not the reasoning that produced it.

## Delivered behaviour

**Not delivered.** Recorded here because the item was open in `docs/ROADMAP.md` and carried no `STORY-<nnnn>`.

## Acceptance criteria

**This item is not delivered.** It is recorded so that an allocated identifier exists and its absence from the delivered set is explicit rather than silent. If it is ever scheduled, criteria are written in the sprint that takes it.

## Source reference

`docs/ROADMAP.md` Track N, N1 — ⬜ open, marked **arch-council required**.

## Implementation evidence

None — not implemented.

## Test / review evidence

None — not implemented.

## Decision references

Allocated by the `roadmap-split` sprint under `STORY-0160` (`docs/sprints/roadmap-split/CONTEXT.md`), which closed the forward-coverage gap: `ID-ALLOCATION.md` claims that an item absent from it is an item no known evidence records, and that property held for delivered work but not for open work — only 6 of 20 open roadmap items carried an identifier. Classified `backlog` following the D-011 precedent.

## Dependencies

None blocking.

## Delivery sprint(s)

Not scheduled.

## Delivery history

- Track N — raised as WI-08. Still open.
- 2026-07-29 — allocated and recorded by the `roadmap-split` sprint (`STORY-0160`).

## Unresolved questions

**Arch-council required before any implementation** — the roadmap says so explicitly, and correctly: this extends the `component_trace_jsonb` schema contract, with the UI renderer and the retry snapshot reader as downstream consumers.
