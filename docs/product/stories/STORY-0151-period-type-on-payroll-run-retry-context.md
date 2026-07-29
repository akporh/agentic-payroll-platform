# `STORY-0151` — `period_type` on `payroll_run`, passed to retry context (AUD-2 / Q2)

**Origin code(s):** `PT-Q-02` · `AUD-2` · `Q2`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-23` — Run retry & recovery
**Classification:** `operational story`
**Status:** `backlog`
**Confidence:** `requires human classification`

## Actor

auditor; payroll operator

## Problem addressed

`period_type` is a run parameter that affects calculation, but it is not persisted on `payroll_run` — so the retry context cannot reproduce it, and an auditor cannot see what the original run used.

## Delivered behaviour

**Not delivered.** Raised as a Track Q audit observation in Sprint 10 and still open.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track Q — Audit Observations register, Q2, marked 🔜 open.

## Implementation evidence

None — not implemented.

## Test / review evidence

None — not implemented.

## Decision references

D-011 classifies this as backlog: no evidence surfaced that it has been completed since ROADMAP was last updated.

## Dependencies

None.

## Delivery sprint(s)

Raised Sprint 10; not delivered.

## Delivery history

- Sprint 10 — raised as audit observation AUD-2/Q2. No delivery.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

Recorded here so the Execution Engine's picture is complete and this cannot be mistaken for delivered work by omission. It must not be cited as a capability. Retry determinism (`STORY-0135`) mitigates but does not resolve it.
