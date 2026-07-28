# Stage 09 Output: Onboarding Flow Experience — C13/C14 (Q6)

Designs the mapping-review → dry-run → commit flow. **Mechanisms rendered**: C13 mapping proposal over `get_workspace_catalog` (`tool-contracts.md` §3.11), the C14 dry-run artifact and hash-gated commit (`08-technical-architecture/outputs/dry-run-mechanism-design.md` §§2–3). **Binding UX inputs**: per-field mapping confidence (Stage 04 handoff, `onboarding-outcome-baseline.md`); original header text alongside proposed mapping (Stage 08 handoff item 6); the standing **Upload/Enroll separation** (repo CLAUDE.md Sprint 22 — not conflated here).

## 1. Where the flow lives

C13/C14 extend the **existing** import surfaces — `NativeUploadFlow` + `ColumnMappingPanel` (`frontend/src/components/shared/`, consumed by three pages: Employees, PayrollInputsBulkUpload, and PayrollResults' reconciliation comparison upload — evidence file §5) — not a new parallel wizard. Because the shared components have three consuming surfaces, any C13 change to them regression-tests all three, not just the onboarding path (carried into `stage-11-handoff.md` §3 sizing). The portfolio decision (§7) already anchors C13 in "the existing upload UI"; this stage keeps that literally: the flow is a staged full-page sequence inside the workspace's existing import entry points. (Not a modal wizard: SlideOvers are single-step per ui-decisions, and the repo's wizard-modal pattern doesn't exist; full-page staged flow follows the existing WorkspaceSetup precedent.)

Stages, each a distinct page state with an explicit progress header (Upload → Review mapping → Dry run → Commit):

## 2. Stage A — Upload and mapping review (C13)

The operator drops the client file (existing flow). C13 returns mapping proposals; the existing `ColumnMappingPanel` gains proposal semantics:

- **Every row shows the original header text verbatim alongside the proposed target** (Stage 08 handoff item 6) — "Original column: `BASIC SAL (NGN)` → proposed: Basic Salary". The original text never disappears behind the proposal.
- **Per-field confidence** (Stage 04 binding): each proposed mapping carries a High / Medium / Low confidence chip (color + text, per ui-decisions badge rule). **Attention ordering**: low-confidence and unmapped rows sort first, under a summary line ("2 mappings need your attention; 14 look confident") — operator scrutiny concentrates where the model is unsure, instead of every row demanding equal review.
- **Everything is a proposal**: every row is operator-editable regardless of confidence; the confirmed mapping is the operator's, not C13's (the AI proposes, the operator disposes — D-03-01's C13 disposition). A "confirm all high-confidence" affordance is acceptable; auto-accepting anything without a confirming click is not.
- Suggested-vs-fact discipline: confidence chips and proposals use the same visually-distinct suggestion treatment as the exception queue's recommended actions — a proposal is never rendered as a settled fact.
- The existing `ColumnMappingPanel` behaviours (duplicate-target rules, auto-deduplication, Excluded section — ui-decisions) are unchanged; C13 fills the panel's initial state instead of leaving it blank.

**Upload/Enroll separation preserved (standing rule, restated as a design constraint)**: this flow imports **HR records** (Upload). The Excel grade column remains informational — shown in the mapping panel and used for salary-definition auto-match *display*, but `grade_code` is never forwarded to `createEmployee`. Enrollment (salary definition / grade / designation assignment) remains the separate Enroll flow. The staged flow may *link* to Enroll after commit ("12 employees imported — enroll them for payroll →"), it never merges the two operations into one submit.

## 3. Stage B — Dry run (C14)

Before commit, the flow requires a dry run of exactly the staged rows (mandatory for C13-originated flows — mechanism §3.6):

- **Run dry run** submits the staged rows + target period; results render from `dry_run_execution.results_jsonb` (per-employee results + traces, **amounts as strings** — mechanism §2).
- **Results view**: summary header (employees processed, gross/net totals, SUCCESS/FAILED status), then a per-employee table with expandable calculation trace per row — the same trace-presentation grammar as the run-detail Results tab, so operators read one trace idiom platform-wide.
- **UX-critical invariant — a dry run must be unmistakable for a real run**: persistent banner on the results view ("Dry run — no payroll was created, no inputs were consumed"), distinct page identity, and **no** appearance in the Runs list (no `payroll_run` row exists — DQ-004; the UI must not synthesise one). Validation failures render as named errors (`FAILED` artifact is still a useful gate outcome — mechanism §3.2).
- Dry-run artifacts are viewable history (append-only gate evidence): a "Dry runs" list within the import flow context, not in the Runs area.

## 4. Stage C — Commit, hash-gated

- Commit attaches the `dry_run_id`; the server verifies SUCCESS + `input_hash` match (mechanism §3.6). The UI enforces the same gate pre-emptively: **any edit to staged rows after the dry run disables Commit** and shows the mechanism's required state — **"Rows changed since the dry run — re-run required"** — with the re-run CTA. The client-side check is convenience; the server hash check is the guarantee (same two-layer pattern as C10 invalidation).
- Commit success lands on the existing post-import state (employee list + the enroll prompt), closing the loop into the standard lifecycle.

## 5. What this flow does not do

- No LLM output feeds the dry run or commit directly — the dry run computes from the operator-confirmed mapping (C14 is deterministic; C13's proposal is upstream and confirmed by a human first — mechanism §4).
- No parallel-run comparison UI here (ReconSlideOver / agreement-rate instrumentation is a separate baseline concern — EG-002; noted for Stage 11 sequencing, not designed into this flow).
- No baseline instrumentation UI in v1, but the flow's stage boundaries (upload started, mapping confirmed, dry run passed, committed) are the natural timestamps for EG-001/EG-003 measurement — Phase 3 should emit them as events from day one (zero-UI instrumentation; forwarded in `stage-11-handoff.md`).
