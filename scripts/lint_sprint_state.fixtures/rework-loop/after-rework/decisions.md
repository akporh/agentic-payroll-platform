# Decisions — `rework-loop` (fixture, snapshot: after-rework)

```yaml
- id: DEC-rework-loop-01
  date: 2026-07-13
  decision_owner: Michael Emedo
  stage: verification
  decision_type: not-applicable
  reason: >
    Fixture stands in for a backend-only, migration-free change with no
    frontend file touched.
  reference: Fixture data, not a real decision.

- id: DEC-rework-loop-02
  date: 2026-07-13
  decision_owner: Michael Emedo
  stage: security
  decision_type: not-applicable
  reason: >
    Fixture stands in for a change touching no API route.
  reference: Fixture data, not a real decision.

- id: DEC-rework-loop-03
  date: 2026-07-13
  decision_owner: Michael Emedo
  stage: implementation
  decision_type: rework
  reason: >
    Audit (fixture stand-in, evidence/audit/review.md) found the
    attempt-1 evidence insufficient to prove the calculation was
    reproducible from the stored snapshot alone. Reopening
    implementation to needs-rework per WORKFLOW.md's rework-loop rule
    — this decision is what authorises the reopening; it does not
    happen silently.
  reference: Fixture data, not a real decision.
```
