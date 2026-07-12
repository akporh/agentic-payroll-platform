# Decisions — `aud-q1-trace-source`

Append-only HITL decision log, per `WORKFLOW.md`. One entry per human decision, in the order made. Every `decision_ref` cited in `state.md` must resolve to an `id` here.

```yaml
- id: DEC-aud-q1-trace-source-01
  date: 2026-07-12
  decision_owner: Michael Emedo
  stage: architecture
  decision_type: not-applicable
  reason: >
    Single additive JSONB trace field within one existing rule branch
    (fixed_amount); no structural or cross-layer design component —
    STAGE-REGISTRY.md's `architecture` entry condition ("sprint plan
    includes any structural or cross-layer design") does not hold for
    this scope.
  reference: Pilot sprint scoping, this session, 2026-07-12 — CONTEXT.md
    "Why this item fits the pilot constraints" table.

- id: DEC-aud-q1-trace-source-02
  date: 2026-07-12
  decision_owner: Michael Emedo
  stage: arch-council
  decision_type: not-applicable
  reason: >
    No status/state/enum field, DB constraint on a financially-critical
    table, meaning of an existing API response field, destructive
    migration step, cross-workspace endpoint, or shared type/interface/
    service contract is touched. The trace field is an additive key
    inside an already-freeform JSONB blob (component_trace_jsonb) used
    only for audit trace, not a typed or enforced contract.
  reference: Pilot sprint scoping, this session, 2026-07-12.

- id: DEC-aud-q1-trace-source-03
  date: 2026-07-12
  decision_owner: Michael Emedo
  stage: security
  decision_type: not-applicable
  reason: >
    No file under backend/api/routes/ is added or modified — the change
    is confined to backend/domain/payroll/rule_evaluator.py.
  reference: Pilot sprint scoping, this session, 2026-07-12.

- id: DEC-aud-q1-trace-source-04
  date: 2026-07-12
  decision_owner: Michael Emedo
  stage: verification
  decision_type: not-applicable
  reason: >
    STAGE-REGISTRY.md's `verification` entry condition requires the
    sprint to touch both backend/api/routes/ AND a file under
    frontend/src/. This sprint touches neither.
  reference: Pilot sprint scoping, this session, 2026-07-12.
```
