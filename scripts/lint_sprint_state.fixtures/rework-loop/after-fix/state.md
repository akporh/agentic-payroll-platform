# State — `rework-loop` (fixture, snapshot: after-fix)

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
    evidence: evidence/implementation/attempt-2.md
    attempt: 2
    note: >
      Corrective second attempt — attempt-1's evidence
      (evidence/implementation/attempt-1.md) is preserved, not deleted,
      per WORKFLOW.md's rework-loop rule ("prior evidence is never
      deleted"). This attempt's evidence is what now governs the
      complete status.

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
    status: eligible
    depends_on: [implementation]
    note: implementation reached complete again — dependency now terminal.

  test:
    status: blocked
    depends_on: [implementation, audit]
    waiting_for:
      - audit
    note: >
      implementation is terminal again, but audit is only eligible, not
      yet complete — test correctly remains blocked on the one
      dependency still non-terminal. This fixture deliberately stops
      here: audit becoming eligible again (mirrored from
      after-rework's blocked) is the mechanic this snapshot exists to
      prove; a full second pass of audit-to-complete is not needed to
      demonstrate it and would just repeat before-rework's shape.
```
