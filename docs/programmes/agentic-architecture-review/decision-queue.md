# Decision Queue — Agentic Architecture Review Programme

This file tracks unresolved questions without turning every question into a human stop.

## Blocking human decisions

_None currently recorded._

## Non-blocking forwarded decisions

| ID | Question | Source stage | Target stage | Status |
|---|---|---|---|---|
| DQ-001 | Concrete C7 statistical formulas, numeric thresholds and minimum history window | 04 | 08 | forwarded |
| DQ-002 | Confirmation-protocol expiry, conflict, idempotency and run-state invalidation rules | 03 | 08 | forwarded |
| DQ-003 | Deterministic onboarding dry-run mechanism | 03/04 | 08 | forwarded |

## Evidence gaps

| ID | Gap | Owner stage | Blocking? |
|---|---|---|---|
| EG-001 | Onboarding mapping time and error-rate baseline | 04/05 | no — instrument before C13/C14 launch |
| EG-002 | Parallel-run agreement-rate baseline | 04/05 | no — instrument before C13/C14 launch |
| EG-003 | Time-to-go-live baseline | 04/05 | no — instrument before C13/C14 launch |

## Rules

- Add an item when it is discovered; do not stop unless it is classified `blocking-human-decision`.
- Remove nothing silently. Mark resolved items with the decision/evidence reference.
- Later-stage implementation specifications are not human decisions unless they require a product, risk or compliance choice.
- The controller checks this file before advancing and before presenting a decision pack to the human reviewer.
