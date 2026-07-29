# Current Sprint(s)

Names the active sprint workspace(s) — nothing else. See `README.md` for what this folder is, `WORKFLOW.md` for transition rules, `STAGE-REGISTRY.md` for stage definitions.

```yaml
active_sprints: []
```

`active_sprints` is a list shape by design (D9, `docs/diagnostics/2026-07-12-nonlinear-icm-sprint-workflow-implementation-plan.md`), even though exactly one entry is supported and enforced for now — one active sprint at a time. This means multi-sprint support later is a validation-rule change, not a schema migration.

**No sprint currently active.** Four closed sprints are fully readable as worked examples of this structure:

- `roadmap-split` (opened and closed 2026-07-29) — retired `docs/ROADMAP.md`'s dual role: history frozen in place, `docs/PLAN.md` opened for forward planning, forward-coverage gap closed (157 → 176 stories). Notable as the first sprint where five stages were legitimately `not-applicable`, and as a worked example of the retro Close Gate catching defects in the sprint's own records — Part A/E034 (missing decision metadata), E064 (one bundled decision cannot cover five stages) and Part D (a docs sprint still owes a test report), all fixed before close.


- `dev-levy-rule-pct` (opened 2026-07-16, closed 2026-07-17) — Development Levy cadence gating + PERCENTAGE_OF_BASIC rule type (`b398c72`). Notable as the first sprint opened retroactively, mid-investigation, rather than starting from `/roadmap` — see `dev-levy-rule-pct/state.md` for the honest accounting of that, including the retro Sprint Workspace Close Gate catching two stale stage rows before close.

- `aud-q1-trace-source` (Changeset 2, approved 2026-07-12; closed Changeset 8, 2026-07-13) — the original ICM pilot. `component_source` in the `fixed_amount` trace entry (Track Q, Q1/AUD-1).
- `sec-s7-timesheet-upload-guard` (Candidate A, approved + closed 2026-07-13, per `docs/diagnostics/2026-07-13-icm-follow-up-validation-pilot-scope.md` and decisions D-VP-01 through D-VP-06) — the follow-up validation pilot. 10 MB server-side size cap on the timesheet upload endpoint (Track S, S7). Genuinely exercised a `skipped` `architecture` stage and `verification`+`security` running truly concurrently on real data — see `sec-s7-timesheet-upload-guard/retrospective.md` for the updated cumulative §9 scoreboard (5 of 6 scenarios now validated; rework loop remains fixture-only).
