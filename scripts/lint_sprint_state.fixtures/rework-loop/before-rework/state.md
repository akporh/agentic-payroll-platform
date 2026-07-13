# State — `rework-loop` (fixture, snapshot: before-rework)

```yaml
sprint: rework-loop
status: active

stages:
  roadmap:
    status: complete

  pm:
    status: complete

  implementation:
    status: complete
    depends_on: [pm]
    evidence: evidence/implementation/attempt-1.md
    attempt: 1

  verification:
    status: not-applicable
    reason: Fixture stands in for a backend-only, migration-free change.
    decision_owner: Michael Emedo
    decision_ref: DEC-rework-loop-01
    date: 2026-07-13

  security:
    status: not-applicable
    reason: Fixture stands in for a change touching no API route.
    decision_owner: Michael Emedo
    decision_ref: DEC-rework-loop-02
    date: 2026-07-13

  audit:
    status: complete
    depends_on: [implementation]
    evidence: evidence/audit/review.md

  test:
    status: eligible
    depends_on: [implementation, audit]
```
