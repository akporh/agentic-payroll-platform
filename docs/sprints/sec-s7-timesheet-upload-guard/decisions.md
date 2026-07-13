# Decisions — `sec-s7-timesheet-upload-guard`

Append-only HITL decision log, per `WORKFLOW.md`. One entry per human decision, in the order made. Every `decision_ref` cited in `state.md` must resolve to an `id` here.

```yaml
- id: DEC-sec-s7-timesheet-upload-guard-01
  date: 2026-07-13
  decision_owner: Michael Emedo
  stage: architecture
  decision_type: skip
  reason: >
    A minor cross-layer question exists: where should the 10 MB
    max-upload-size value live — a single shared constant between
    backend and frontend (no such shared-config mechanism exists yet
    between backend/ and frontend/), a duplicated literal in each layer,
    or a future workspace-configurable value. This is a genuine, if
    small, structural question — STAGE-REGISTRY.md's architecture entry
    condition ("sprint plan includes any structural or cross-layer
    design") legitimately holds, so this is skipped, not not-applicable.
    Resolution (D-VP-02, Validation-Pilot Scope Approval, 2026-07-13):
    the backend constant (MAX_TIMESHEET_UPLOAD_BYTES in
    backend/api/routes/payroll.py) is authoritative; a frontend copy of
    the same value may exist for early user feedback only, and must
    never weaken backend enforcement. Both locations cross-reference
    each other via inline comments. Compensating controls: the backend
    test suite proves the guard is independent of any frontend code
    path, and the security stage of this same sprint reviews the guard
    code directly. This decision is reversible — re-opens if a third
    consumer of the value appears, or if the limit needs to become
    workspace-configurable.
  reference: docs/diagnostics/2026-07-13-icm-follow-up-validation-pilot-scope.md
    §5; Validation-Pilot Scope Approval, this session, 2026-07-13
    (decision D-VP-02).

- id: DEC-sec-s7-timesheet-upload-guard-02
  date: 2026-07-13
  decision_owner: Michael Emedo
  stage: arch-council
  decision_type: not-applicable
  reason: >
    No status/state/enum field, DB constraint on a financially-critical
    table, meaning of an existing API response field, destructive
    migration step, cross-workspace endpoint, or shared type/interface/
    service contract is touched. This is an additive byte-size guard
    (HTTPException 413) and an advisory client-side check — neither is a
    data contract.
  reference: Sprint scoping, this session, 2026-07-13.

- id: DEC-sec-s7-timesheet-upload-guard-03
  date: 2026-07-13
  decision_owner: Michael Emedo
  stage: audit
  decision_type: not-applicable
  reason: >
    Neither sequential_executor.py, rule_evaluator.py, executor.py, nor a
    calculation-altering migration is touched — this sprint is upload
    validation (a byte-size guard), not a calculation path.
  reference: Sprint scoping, this session, 2026-07-13.
```
