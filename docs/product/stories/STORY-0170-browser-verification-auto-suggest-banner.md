# `STORY-0170` — EMP-VERIFY-1 — browser verification of the auto-suggest banner

**Origin code(s):** `EMP-VERIFY-1`
**Outcome:** `OUT-2` — Sustainable delivery process
**Capability:** `CAP-10` — Delivery Infrastructure
**Feature:** `FEAT-37` — Test harness & regression coverage
**Classification:** `technical enabler`
**Status:** `backlog`
**Confidence:** `requires human classification`

## Actor

engineer

## Problem addressed

Sprint 23's auto-suggest banner was accepted without live browser verification. Sprint 17's retro established that a PASS requires live execution, not code review — this item is the outstanding debt against that standard.

## Delivered behaviour

**Not delivered.** Recorded here because the item was open in `docs/ROADMAP.md` and carried no `STORY-<nnnn>`.

## Acceptance criteria

**This item is not delivered.** It is recorded so that an allocated identifier exists and its absence from the delivered set is explicit rather than silent. If it is ever scheduled, criteria are written in the sprint that takes it.

## Source reference

`docs/ROADMAP.md` Sprint 24 story index, EMP-VERIFY-1 — 🔜 open.

## Implementation evidence

None — not implemented.

## Test / review evidence

None — not implemented.

## Decision references

Allocated by the `roadmap-split` sprint under `STORY-0160` (`docs/sprints/roadmap-split/CONTEXT.md`), which closed the forward-coverage gap: `ID-ALLOCATION.md` claims that an item absent from it is an item no known evidence records, and that property held for delivered work but not for open work — only 6 of 20 open roadmap items carried an identifier. Classified `backlog` following the D-011 precedent.

## Dependencies

None.

## Delivery sprint(s)

Not scheduled.

## Delivery history

- Sprint 23 — banner shipped without live verification.
- Sprint 24 — the verification debt recorded as its own item. Still open.
- 2026-07-29 — allocated and recorded by the `roadmap-split` sprint (`STORY-0160`).

## Unresolved questions

Not delivered. Note the `dev-levy-rule-pct` precedent: a throwaway Playwright install in the scratchpad drove Chromium directly when no MCP browser tool was available, so lack of tooling is not a blocker here.
