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

## Next action

**Complete Stage 01 current operating model review.**
