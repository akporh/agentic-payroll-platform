# State — `bad-decision-ref` (fixture)

```yaml
sprint: bad-decision-ref
status: active

stages:
  roadmap:
    status: complete

  pm:
    status: complete

  implementation:
    status: complete
    depends_on: [pm]

  verification:
    status: not-applicable
    depends_on: [implementation]
    reason: Sprint touches no route or frontend file.
    decision_owner: Michael Emedo
    decision_ref: DEC-bad-01
    date: 2026-07-13

  security:
    status: not-applicable
    depends_on: [implementation]
    reason: Sprint touches no API route.
    decision_owner: Michael Emedo
    decision_ref: DEC-bad-99
    date: 2026-07-13

  audit:
    status: not-applicable
    depends_on: [implementation]
    reason: No calculation or statutory-rule file touched.
    decision_owner: Michael Emedo
    decision_ref: DEC-bad-01
    date: 2026-07-13

  test:
    status: not-started
    depends_on: [implementation, verification, security, audit]
```
