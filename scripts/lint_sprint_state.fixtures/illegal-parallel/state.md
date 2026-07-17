# State — `illegal-parallel` (fixture)

```yaml
sprint: illegal-parallel
status: active

stages:
  roadmap:
    status: complete

  pm:
    status: complete

  implementation:
    status: active
    depends_on: [pm]
    may_run_with: [audit]

  verification:
    status: active
    depends_on: [implementation]

  security:
    status: active
    depends_on: [implementation]

  audit:
    status: active
    depends_on: [implementation]
    may_run_with: [implementation]

  test:
    status: not-started
    depends_on: [implementation, verification, security, audit]
```
