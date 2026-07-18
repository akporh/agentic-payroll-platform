# Source Register

Register of every source document, system, or dataset consulted anywhere in this review. Every stage that reads a source must add an entry here (or confirm one already exists) before citing that source as evidence.

## Purpose

This gives the review a single place to check provenance — what was consulted, when, by whom, and how current it was at the time of consultation. It also lets a later stage or auditor spot-check whether a source has since changed.

## Register format

```markdown
### S-<n>: <source name>
- **Type**: code | data | documentation | memory-file | human-statement | external-system
- **Location**: <path, table name, URL, or description>
- **First consulted**: YYYY-MM-DD, Stage <#>
- **Snapshot basis**: <git commit SHA / DB state description / "live read" — what state this source was in when read>
- **Notes**: <anything relevant to reliability, e.g. "memory file — re-verified against current code on <date>">
```

## Sources

### S-01: Repository codebase (backend, migrations, frontend)
- **Type**: code
- **Location**: `backend/`, `migrations/versions/`, `frontend/src/` — full repository at `/Users/michaelemedo/Documents/2.OnAiR/Clients/Sandy/agentic-payroll-platform`
- **First consulted**: 2026-07-11, Stage 01
- **Snapshot basis**: git commit `9644d911fcf2fc601b85c88688abe7c872ed0e26`, branch `uat`
- **Notes**: Primary evidence source for all 46 confirmed findings in Stage 01. Read via 5 parallel Explore sub-investigations (workspace/onboarding/config; employee/contract/timesheet/input; run/execution/snapshot/trace; retry/reconciliation/approval/audit; UI/investigation/statutory) plus direct file reads for schema updates and evidence citation.

### S-02: Project CLAUDE.md files (documented intent, not implementation proof)
- **Type**: documentation
- **Location**: `/Users/michaelemedo/Documents/2.OnAiR/CLAUDE.md`, `Clients/Sandy/CLAUDE.md`, `Clients/Sandy/agentic-payroll-platform/CLAUDE.md`
- **First consulted**: prior sessions; re-consulted 2026-07-11, Stage 01
- **Snapshot basis**: live read, 2026-07-11
- **Notes**: Used only as a comparison point for "intended design" fields — never cited as evidence of current implementation on its own. Every finding citing a `CLAUDE.md` rule also cites an independent code/migration read confirming the rule's current accuracy, per `_core/EVIDENCE-STANDARD.md`.

### S-03: Prior-session memory files (re-verified, not cited standalone)
- **Type**: memory-file
- **Location**: `~/.claude/projects/-Users-michaelemedo-Documents-2-OnAiR-Clients-Sandy-agentic-payroll-platform/memory/*.md` — specifically `feedback_employee_contract_workspace_scope.md`, `feedback_salary_def_live_read.md`, `project_salary_def_code_format.md`, `feedback_retry_strategy_architecture.md`, `project_reconciliation_domain_rules.md`, `project_d_arch1_inner_join_gap.md`, `feedback_constraint_violations.md`
- **First consulted**: prior sessions; re-verification performed 2026-07-11, Stage 01
- **Snapshot basis**: memory files as of 2026-07-11
- **Notes**: Per `_core/EVIDENCE-STANDARD.md`'s re-verification rule, every claim drawn from these memory files was independently re-checked against current code/migrations before being recorded in `findings.md`. Findings F-01-08, F-01-15, F-01-27, F-01-30, F-01-33, F-01-36, F-01-38, F-01-17 each note where a memory claim was confirmed, clarified, or found to need updating against current evidence.

### S-04: Agent Layer Architecture document
- **Type**: documentation
- **Location**: `docs/architecture/agent-layer-architecture.html` (also mirrored at `frontend/public/architecture/agent-layer-architecture.html`)
- **First consulted**: 2026-07-12, Stage 02
- **Snapshot basis**: live read, 2026-07-12; document's own header states "Arch-council reviewed 2026-06-11", status pill "NEEDS REVISION"
- **Notes**: This is the current proposed Phase 2 product/technical thesis — treated as stated intent only, per `_core/EVIDENCE-STANDARD.md` and the Stage 02 prompt's explicit instruction not to treat architecture documents as proof of implementation. Nothing in Tracks P/V/W/X/Y is built; the document's own phase-timeline marks Track P as "current" and all others as not yet started. Its "As-Is Architecture" tab (self-assessed GAP-1 through GAP-6) was cross-checked against Stage 01's independently-derived findings rather than accepted at face value — see `findings.md` F-02-08.

### S-05: EP-004 Phase 2 product stub docs
- **Type**: documentation
- **Location**: `Clients/Sandy/_PRODUCT/EP-004_phase2-agentic/_epic.md`, `FEAT-020_ai-payroll-engine_FUTURE.md`, `FEAT-021_saas-multi-tenant_FUTURE.md`
- **First consulted**: 2026-07-12, Stage 02
- **Snapshot basis**: live read, 2026-07-12
- **Notes**: Confirmed these are stub/placeholder documents ("Acceptance criteria: TBD — to be scoped after Phase 1 closure", Status: FUTURE, "Sprint(s): Not yet started") — they add no design detail beyond what S-04 already states, and are not cited as evidence for any finding beyond confirming FEAT-020/021 are unscoped.

## Stage 03 note

Stage 03 (Agent Portfolio) introduced no new sources — its evidence base is entirely S-01 (codebase, re-cited via Stage 01's confirmed findings), S-02/S-03 (already-reconciled memory/CLAUDE.md context), and S-04 (the architecture document, already registered). No new code exploration was performed; Stage 03 is a design/synthesis stage building on already-gathered evidence.

## Stage 04 note

Stage 04 (Outcome Discovery) introduced no new sources — its evidence base is S-01 (codebase, re-cited via Stage 01's confirmed findings), S-04 (the architecture document), and Stage 02/03's own confirmed findings and outputs. No new code exploration was performed; Stage 04 is an outcome-framing/prioritisation stage building on already-gathered evidence, per its own explicit "current code only where needed to verify that an outcome has a real current-state basis" instruction — no such verification was needed beyond what Stage 01 already established.

### S-06: Repository codebase, re-verified at a later commit (Stage 05)
- **Type**: code
- **Location**: `backend/`, `frontend/src/`, `migrations/versions/`, `tests/` — same repository, later snapshot
- **First consulted**: 2026-07-11 (Stage 01, commit `9644d91`); re-verified 2026-07-13, Stage 05
- **Snapshot basis**: git commit `65e87aa3fd1df1ec90c7ea7e47a0c0af54805132`, branch `uat` — approximately 2 days and several commits after Stage 01's snapshot, including genuine remediation work (commit `68e9307`, "Remediate 04-001 (S0) + 05-001")
- **Notes**: Stage 05's defining discipline is that it does NOT assume Stage 01's findings are still accurate — every cited Stage 01 finding relevant to this stage's scope (F-01-27, F-01-29, F-01-33, F-01-38, F-01-40) was independently re-read against this later commit via 5 parallel Explore sub-investigations, with explicit git-log checks for each relevant file to catch any intervening changes. Two findings were confirmed materially changed since Stage 01 (F-01-29 downgraded — confirmed unreachable in production; snapshot/retry integrity genuinely improved by commit `68e9307`); the rest were confirmed unchanged. Two new findings (F-05-11's tool-wrapping risks) were surfaced by this stage's different investigative lens, not present in Stage 01's original sweep.

### S-07: docs/audit-program/ findings (cross-reference only, independently re-verified)
- **Type**: documentation (a parallel, independent investigation workstream in the same repository)
- **Location**: `docs/audit-program/03-configuration-integrity/findings.md`, `06-ui-api-backend-wiring/findings.md`, `07-silent-failures-observability/findings.md`, `09-security-tenant-isolation/findings.md`
- **First consulted**: 2026-07-13, Stage 05
- **Snapshot basis**: live read, 2026-07-13
- **Notes**: This is a separate, independently-run audit workstream investigating much of the same codebase. Per `_core/EVIDENCE-STANDARD.md`, its findings were never cited as standalone evidence — every reference to it in this stage's outputs (findings 03-002, 06-003, 06-007, 07-002, 09-000, 09-002, 09-004) is used only as corroboration alongside this stage's own independent direct code re-read, never as a substitute for it. Where the two investigations' independently-derived conclusions matched exactly (e.g. the reconciliation workspace-scoping gap, the FULL_RUN UI mismatch, the absence of authentication), this is noted as cross-validation, not as this review outsourcing its evidence-gathering.

### S-08: Repository codebase, re-verified at a later commit (Stage 06)
- **Type**: code
- **Location**: `backend/api/routes/payroll.py`, `backend/application/{payroll_approval_service,payroll_retry_service,reconciliation_service}.py`, `backend/infra/repositories/{audit_log_repo,event_store_repo}.py`, `backend/infra/db/models/statutory_rule.py`, `backend/domain/payroll/audit_events.py`, `migrations/versions/` (baseline `5aa34350e00f`, statutory seeds `e4f5a6b7c8d9`/`de1f2a3b4c5d`, trigger migrations, `ea05e71efbd7`)
- **First consulted**: 2026-07-11 (Stage 01); re-read 2026-07-15, Stage 06
- **Snapshot basis**: git commit `265db103cfb6a6b490c8655d5ceb4b776303e6fe`, branch `uat`
- **Notes**: Stage 06 consumed Stage 05's confirmed platform facts without re-verification (per its `CONTEXT.md`), and performed fresh direct reads only for its own new control claims: actor-attribution sources (F-06-01), audit-write transactionality (F-06-02), audit-table immutability/retention absence (F-06-03), and statutory_rule provenance schema (F-06-04). Absence claims (no triggers on audit tables, no retention mechanism) are grep sweeps duplicated into `06-compliance-controls/evidence/06-attribution-and-audit-integrity-excerpts.md` per the evidence standard.

### S-04 note (Stage 06)
Stage 06 re-read `docs/architecture/agent-layer-architecture.html` (S-04, live read 2026-07-15) only for the `agent_session_log`/retention design (lines 496, 938, 1150–1151) — excerpts saved in the Stage 06 evidence file §7. Treated as stated intent only, unchanged status ("NEEDS REVISION", D-02-01).

### Codebase re-read notes (Stages 07–09)

- **Stage 07 (2026-07-17)**: fresh direct reads of the route surface, CORS configuration, and `workspace_info()` callers at commit `ea1590a`; excerpts in `07-security-identity/evidence/`.
- **Stage 08 (2026-07-17)**: fresh direct reads at commit `573be0d` (clean tree) for mechanism grounding — statutory resolution query, persister transaction boundaries, actor-input sites, reconciliation/decorative routes, executor purity, `simulate_payroll.py` precedent; excerpts in `08-technical-architecture/evidence/08-code-grounding-excerpts.md`. Stage 08 also re-read S-04 (`agent-layer-architecture.html`, live read 2026-07-17) for the Track P/V/X/Y mechanism proposals — design under review, not authority, unchanged status.
- **Stage 09 (2026-07-17)**: fresh direct reads of the frontend surface at commit `7d36020` (clean tree) for IA/surface grounding — `router.tsx`, `MainLayout.tsx`, design-system `Navigation.tsx`/`Layout.tsx`, `PayrollResults.tsx` (tabs + audit adapter), `RunPayroll.tsx` (run-type/retry options), shared upload components, `docs/design/ui-decisions.md` (standing UI decisions log, binding input); excerpts in `09-human-experience/evidence/09-frontend-grounding-excerpts.md`. Stage 05's frontend claims (F-05 §§1–2) were re-verified against this later commit rather than carried over. No new external sources.

### S-09: Repository test/CI infrastructure (Stage 10)
- **Type**: code
- **Location**: `.github/workflows/tests.yml`, `frontend/package.json`, `tests/` (tree listing + collect run), `docs/test-reports/test-harness/test-harness-checklist.md`, `CLAUDE.md` (Test Harness section)
- **First consulted**: 2026-07-17, Stage 10
- **Snapshot basis**: git commit `e4ad484`, branch `uat`, clean tree; transient command outputs (pytest collect count 328, full run 327 passed / 1 skipped, find/grep counts) duplicated into `10-evaluation-assurance/evidence/10-ci-and-harness-excerpts.md` per the evidence standard
- **Notes**: Grounds F-10-01 (no frontend test harness), F-10-02 (no CI schedule seam), F-10-03 (documented suite size stale). The test-harness checklist and `CLAUDE.md` were used as documented intent and cross-checked against the workflow file / package.json / test tree directly — the T4.5 park corroborates F-10-01 but the finding rests on the direct reads.

### Stage 10 note

Beyond S-09, Stage 10 consumed only prior confirmed findings, gate registers, Stage 07–09 handoffs/designs, and the Stage 04 measurement framework — all programme-internal, already registered via their producing stages' evidence. No new external sources.

### S-10: Sandy business-context documents (Stage 11 re-read)
- **Type**: documentation
- **Location**: `Clients/Sandy/CLAUDE.md` (business phases/intent); `Clients/Sandy/_PRODUCT/EP-004_phase2-agentic/FEAT-020_ai-payroll-engine_FUTURE.md`, `FEAT-021_saas-multi-tenant_FUTURE.md` (Phase 2 product stubs — same files as S-05, re-verified)
- **First consulted**: 2026-07-12 (Stage 02, as S-02/S-05); re-read 2026-07-18, Stage 11
- **Snapshot basis**: live read 2026-07-18; excerpts duplicated into `11-commercial-product-strategy/evidence/11-business-context-excerpts.md` (files sit outside the git repository, so excerpt duplication is the durable record per the evidence standard)
- **Notes**: Treated strictly as documented *intent* (evidence type 4) — never as demand evidence. Grounds F-11-01 (FEAT-021 still an unscoped stub) and, via the §4 absence sweep, F-11-02 (no registered type-5 commercial-demand evidence anywhere in the programme). Repo-internal citations in Stage 11 are pinned at commit `4abafdc`, branch `uat`, clean tree.

### Stage 11 note

Beyond S-10, Stage 11 consumed only programme-internal inputs (Stage 02/04/05/09/10 confirmed findings, outputs and handoffs; the gate/evidence/residual-risk registers; `decision-queue.md`) — all already registered via their producing stages. No new external sources; no business fact was taken from an unregistered source (gaps recorded as EG-004/EG-005 instead).

### Stage 12 note

Stage 12 (Target Direction, executor pass 2026-07-18) introduced no new sources — it is a pure synthesis stage consuming programme-internal inputs only (Stage 02/03/04/05/09/10/11 confirmed findings, outputs and handoffs; the gate/evidence/residual-risk registers; `decision-queue.md`), all already registered via their producing stages. One re-read: **S-04** (`docs/architecture/agent-layer-architecture.html`, live read 2026-07-18) solely to state the revision's disposition (`12-target-direction/outputs/source-document-disposition.md`) — unchanged status ("Arch-council reviewed 2026-06-11", pill "NEEDS REVISION"), treated as stated intent only per D-02-01. No new code exploration; no repo-code citations beyond prior stages' confirmed findings. Repository HEAD at the time of the pass: `33a4651`, branch `uat`, clean tree.

## Next action

**Register current through Stage 12 executor pass. Next entries due from Stage 13's consulted sources (if any).**
