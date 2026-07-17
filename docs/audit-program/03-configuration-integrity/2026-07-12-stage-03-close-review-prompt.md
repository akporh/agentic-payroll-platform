# Casper Prompt — Close Stage 03: Configuration Integrity

Use this prompt in Casper to perform the Stage 03 review and closure workflow.

---

Close Stage 03 — Configuration Integrity.

Before closing:

1. Read:
   - `docs/audit-program/03-configuration-integrity/CONTEXT.md`
   - `docs/audit-program/03-configuration-integrity/findings.md`
   - `docs/audit-program/_core/evidence-standard.md`
   - `docs/audit-program/_core/finding-schema.md`
   - `docs/audit-program/_core/human-decisions.md`

2. Correct finding `03-003` so its status field contains only:

   `confirmed`

   Preserve all nuance about the dead-storage fact, D1 design decision and lack of current correctness impact in the relevant narrative fields.

3. Verify every Stage 03 completion criterion against an explicit output:
   - all required configuration domains catalogued
   - duplicate representations include writers, readers, precedence and drift assessment
   - original-run/retry comparison completed for component metadata, payroll rules and at least one snapshot/live boundary
   - every finding has compliant evidence and a single valid status
   - handoffs exist for Stages 04, 05, 06, 07, 08 and 12

4. Keep these human decisions open:
   - whether retry should consume the frozen statutory-rule snapshot
   - whether `employee_contract_snapshot.components_jsonb` should remain
   - whether statutory components should remain disableable per workspace

5. Do not change finding `03-002` from `plausible`. Stage 04 must attempt controlled reproduction before it can become confirmed as an observed divergence.

Then update `docs/audit-program/audit-state.md`:

- mark Stage 03 as `complete`
- set its closed date to today
- set the next action to review and open Stage 04
- leave Stage 04 as not started

Add a final Stage 03 handoff summary stating:

- `03-002` is the primary Stage 04 input
- Stage 04 should reproduce the statutory-rule original-run/retry divergence using controlled non-production execution
- `03-003` passes to Stages 05 and 12
- `03-004` passes to Stages 08 and 09
- UI coverage gaps, including `pay_cycle.definition_json`, pass to Stage 06

Do not modify application code, tests, migrations, scripts or frontend files.

Report only:

- final finding count by status and severity
- completion-criteria verification
- open human decisions
- Stage 04 dependencies
- files changed
- `git diff --stat`
- `git status --short`
- primary file path
- resulting commit SHA after commit and push

Commit and push the audit-documentation changes to the current branch once the stage is internally consistent and evidence-complete.
