# State — `clean` (fixture)

```yaml
sprint: clean
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
    status: active
    depends_on: [implementation]
    may_run_with: [security]

  security:
    status: active
    depends_on: [implementation]
    may_run_with: [verification]

  audit:
    status: not-applicable
    depends_on: [implementation]
    reason: No calculation or statutory-rule file touched in this fixture.
    decision_owner: Michael Emedo
    decision_ref: DEC-clean-01
    date: 2026-07-13

  test:
    status: blocked
    depends_on: [implementation, verification, security, audit]
    waiting_for:
      - verification
      - security
```
