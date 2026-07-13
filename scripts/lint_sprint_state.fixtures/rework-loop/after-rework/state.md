# State — `rework-loop` (fixture, snapshot: after-rework)

```yaml
sprint: rework-loop
status: active

stages:
  roadmap:
    status: complete

  pm:
    status: complete

  implementation:
    status: needs-rework
    depends_on: [pm]
    evidence: evidence/implementation/attempt-1.md
    attempt: 1
    reason: >
      Audit found the attempt-1 evidence insufficient to prove the
      calculation was reproducible from the stored snapshot alone —
      fixture stand-in for a genuine correction, not a fabricated
      product defect.
    decision_owner: Michael Emedo
    decision_ref: DEC-rework-loop-03
    date: 2026-07-13

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
    status: blocked
    depends_on: [implementation]
    waiting_for:
      - implementation
    note: >
      Reverted from complete to blocked — mechanical consequence of
      implementation moving to needs-rework (WORKFLOW.md rework-loop
      rule), not a separate human decision.

  test:
    status: blocked
    depends_on: [implementation, audit]
    waiting_for:
      - implementation
      - audit
    note: >
      Reverted from eligible to blocked for the same reason as audit —
      it also directly lists implementation in depends_on.
```
