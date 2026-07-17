# Decisions — `bad-decision-ref` (fixture)

```yaml
- id: DEC-bad-01
  date: 2026-07-13
  decision_owner: Michael Emedo
  stage: verification
  decision_type: not-applicable
  reason: >
    Fixture stands in for a sprint that touches no route or frontend file.
  reference: Fixture data, not a real decision.

- id: DEC-bad-01
  date: 2026-07-13
  decision_owner: Michael Emedo
  stage: does-not-exist
  decision_type: not-applicable
  reason: >
    Deliberately duplicates the DEC-bad-01 ID above and references a stage
    ID that is not registered in STAGE-REGISTRY.md, to exercise both the
    duplicate-decision-ID check and the unknown-stage-decision check in a
    single fixture.
  reference: Fixture data, not a real decision.
```
