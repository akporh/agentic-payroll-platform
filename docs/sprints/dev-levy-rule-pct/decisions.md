# Decisions — `dev-levy-rule-pct`

Append-only log, per `docs/sprints/WORKFLOW.md`'s Recording HITL Decisions schema. One entry per human decision, in the order made.

```yaml
- id: DEC-dev-levy-rule-pct-01
  date: 2026-07-15
  decision_owner: Michael Emedo
  stage: pm
  decision_type: activate
  reason: >
    Levy cadence confirmed as annual — deducted in the January run, or in
    a hire's first paid month. (Superseded in wording, not substance, by
    DEC-04 below — the underlying trigger logic was always "OR," this
    entry's phrasing just used the imprecise "mid-year hire" framing.)
  reference: AskUserQuestion answer, this session, "Levy cadence" question.

- id: DEC-dev-levy-rule-pct-02
  date: 2026-07-15
  decision_owner: Michael Emedo
  stage: pm
  decision_type: activate
  reason: >
    Levy amount source confirmed as statutory default (₦100) + optional
    per-workspace override, matching the existing pension/NHF pattern.
  reference: AskUserQuestion answer, this session, "Levy source" question.

- id: DEC-dev-levy-rule-pct-03
  date: 2026-07-15
  decision_owner: Michael Emedo
  stage: pm
  decision_type: activate
  reason: >
    Percentage-of-basic rule scope confirmed as earnings-only (no
    deduction-type percentage rules this sprint).
  reference: AskUserQuestion answer, this session, "Percentage-of-basic scope" question.

- id: DEC-dev-levy-rule-pct-04
  date: 2026-07-16
  decision_owner: Michael Emedo
  stage: pm
  decision_type: activate
  reason: >
    Corrected the cadence model: the "first paid month" trigger is not
    scoped to "mid-year hires" — it applies to every hire's first paid
    month regardless of which calendar month that falls in, and it fires
    independently of the January trigger (OR, not exclusive). Confirmed
    explicitly: an employee whose first paid month is December is
    correctly charged in December AND again the following January — one
    charge per calendar year, not a double-charge defect. CONTEXT.md
    updated to remove the "mid-year hire" framing.
  reference: Direct chat correction, 2026-07-16 ("its not a mid-year hire...
    so someone starting in dec 2025 will be levied 100N in dec, and 100N
    in jan of 26").

- id: DEC-dev-levy-rule-pct-05
  date: 2026-07-15
  decision_owner: Arch Council (Senior Architect + Principal Engineer)
  stage: arch-council
  decision_type: block
  reason: >
    Interim verdict NEEDS REVISION (combined: architect NEEDS REVISION,
    principal CONCUR WITH ADDITIONS). Top blockers: (1) CRITICAL —
    overrides_json PATCH must merge, not full-replace, or it silently
    destroys other override keys (component_class, flat_amount) — a
    recurrence of a previously logged incident; (2) CRITICAL — deploy
    order: the cadence-gate code must ship before migrations A/B, or
    live runs overcharge 12x in the gap window; (3) cadence-absent
    default must be ANNUAL not MONTHLY; (4) the plan's own AC
    ("reconciliation diff -> 0 for all 184 employees") is unachievable
    as scoped because Jan 2026 is already closed — needs an explicit
    arrears-remediation decision. Full detail in architecture.md. Plan
    file (~/.claude/plans/steady-petting-orbit.md) not yet revised to
    incorporate these findings.
  reference: architecture.md (this folder) — reconstructed from working
    notes after the verbatim agent output was lost to a context
    compaction mid-session; noted as a reconstruction, not verbatim, in
    architecture.md itself.

- id: DEC-dev-levy-rule-pct-06
  date: 2026-07-16
  decision_owner: Michael Emedo
  stage: arch-council
  decision_type: activate
  reason: >
    2026 arrears (open question 1): accept the gap for the 184 already-
    reconciled January 2026 employees — no correction/backdated run. Fix
    forward only; the cadence gate governs all periods from its deploy
    date onward. Consequence for this sprint's AC: the plan's original
    "reconciliation diff -> 0 for all 184 employees" acceptance
    criterion must be dropped/rewritten in the plan revision — it is no
    longer a goal of this sprint, since the arrears are explicitly not
    being remediated.
  reference: Direct chat answer, 2026-07-16 ("1. accept gap, fix forward").

- id: DEC-dev-levy-rule-pct-07
  date: 2026-07-16
  decision_owner: Michael Emedo
  stage: arch-council
  decision_type: activate
  reason: >
    INACTIVE-in-January residual case (open question 2): accepted as a
    known edge case, no explicit handling built this sprint. An employee
    INACTIVE during their eligible trigger month (January, or their own
    first paid month) simply does not get charged that calendar year.
    Not tracked as a defect; may be revisited if it proves material in
    practice.
  reference: Direct chat answer, 2026-07-16 ("2. accept as edge case").

- id: DEC-dev-levy-rule-pct-08
  date: 2026-07-16
  decision_owner: Michael Emedo
  stage: arch-council
  decision_type: activate
  reason: >
    Rename timing (open question 3): rename now, in this sprint. The
    workspace-override key changes from `monthly_amount` to
    `annual_amount` for DEVELOPMENT_LEVY. This is the coordinated,
    multi-file change the Principal Engineer flagged (not a free
    rename) — plan revision must enumerate and update every read-site:
    `component_metadata.metadata_json.engine_behavior.workspace_override_key`
    seed value, the ~5 code read-sites the Principal Engineer identified
    (payroll.py override resolution, payroll_retry_service.py snapshot
    threading, WorkspaceConfig.tsx field key, and any others found during
    implementation), plus the SlideOver helper copy ("Leave blank to use
    the statutory default (N100/year)" already says "year," so no copy
    change needed there beyond the field key itself).
  reference: Direct chat answer, 2026-07-16 ("3. rename to s=annual_amount").

- id: DEC-dev-levy-rule-pct-09
  date: 2026-07-16
  decision_owner: Michael Emedo
  stage: arch-council
  decision_type: activate
  reason: >
    Explicit override = 0 semantics (open question 4): a workspace CAN
    zero out the Development Levy via an explicit `annual_amount: 0`
    override. This must remain distinct from "no override present"
    (which resolves to the statutory default, 100) — the PATCH/SlideOver
    logic must preserve the difference between "key absent" (-> default)
    and "key present with value 0" (-> genuinely zero), not collapse an
    empty/blank input into 0 or vice versa. D-ARCH-2's statutory
    hard-reject guard is already disabled (workspace.py:1316-1319, out
    of scope this sprint per CONTEXT.md) so no additional guard blocks
    this.
  reference: Direct chat answer, 2026-07-16 ("4. workspace can zero out").

- id: DEC-dev-levy-rule-pct-10
  date: 2026-07-16
  decision_owner: Michael Emedo
  stage: arch-council
  decision_type: activate
  reason: >
    Plan approved. The normal ExitPlanMode approval gate was unavailable
    (plan mode had already exited earlier in this session via a harness
    event, not an explicit ExitPlanMode call) -- approval obtained
    directly via AskUserQuestion instead. Plan copied verbatim into
    plan.md (this folder) per D5. implementation stage now eligible to
    start.
  reference: AskUserQuestion answer, 2026-07-16, "Plan approval" question
    -> "Approved".
```
