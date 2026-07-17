# Stage 09: Human Experience — Findings

Schema: `_core/FINDING-SCHEMA.md`. Draft and confirmed findings are kept in separate sections below — never merge them.

## Draft Findings

(hypotheses / observations not yet confirmed — MUST NOT be cited by other stages)

_None._

---

## Confirmed Findings

(meet the evidence standard in `_core/EVIDENCE-STANDARD.md` — safe to cite from later stages)

### F-09-01: Workspace switching is pure client navigation with no session semantics

- **Current implementation**: Selecting a workspace in the TopBar picker calls `navigate('/workspaces/${id}')` — a client-side route change only (`frontend/src/components/layout/MainLayout.tsx:61`). No session, token, or context-invalidation concept exists; the workspace is navigation state throughout the frontend.
- **Intended design**: Post-C1, workspace switch = revoke old session + issue new workspace-locked token, and the UI must present switching as a context change, not a filter (P6; `08-technical-architecture/outputs/auth-foundation-design.md` §2; Stage 08 → 09 handoff item 1).
- **Identified gap**: The entire switcher interaction model must change from instant navigation to a session-changing transition (`outputs/auth-and-audit-surfaces.md` §Q7.2). No current code anticipates this.
- **Evidence**: `frontend/src/components/layout/MainLayout.tsx:61`; `frontend/src/design-system/components/Navigation.tsx:111-120` (picker); excerpts in `evidence/09-frontend-grounding-excerpts.md` §2. Read at commit `7d36020`.
- **Severity**: Informational — intentional current design (pre-auth platform); recorded as the concrete UI delta C1 carries.
- **Status**: confirmed
- **Date**: 2026-07-17
- **Raised by**: Stage 09 (auth-surface grounding)

### F-09-02: Run Payroll page still offers FULL_RUN retry and still omits CORRECTION, unchanged at `7d36020`

- **Current implementation**: `frontend/src/pages/RunPayroll.tsx:48` types retry strategy as `'PER_EMPLOYEE' | 'FULL_RUN'` and the radio group (~lines 235–240) offers both; `RunPayroll.tsx:45` types run type as `'REGULAR' | 'ADJUSTMENT'` and the select (~lines 199–202) offers only those two, while the API allowlist accepts `CORRECTION`.
- **Intended design**: `payroll_retry_request.retry_strategy` allows `PER_EMPLOYEE` only (repo CLAUDE.md data-contract table; DB CHECK + API allowlist per F-01-30/31); `run_type` deliberately includes `CORRECTION` at the API (F-01-43).
- **Identified gap**: Both Stage 05 mismatches (`05-platform-readiness/outputs/frontend-backend-alignment.md` §§1–2) remain present ~4 days and multiple commits later: a selectable option the backend always rejects (FULL_RUN), and a supported backend capability unreachable from the UI (CORRECTION — the substance of DQ-005, disposed via `outputs/stage-11-handoff.md` §1).
- **Evidence**: `frontend/src/pages/RunPayroll.tsx:45,48,199-202,235-240`, re-read this session at `7d36020`; excerpts in `evidence/09-frontend-grounding-excerpts.md` §4.
- **Severity**: Medium — the FULL_RUN path fails loudly (rejected request) with no data harm and an obvious workaround; consistent with Stage 05's "launch-risk (non-data)" classification. Removal is a trivial fix (`stage-11-handoff.md` §2).
- **Status**: confirmed
- **Date**: 2026-07-17
- **Raised by**: Stage 09 (DQ-005 grounding re-verification)

### F-09-03: The run-detail Audit Log tab renders raw `performed_by` strings with no identity qualification

- **Current implementation**: The Audit Log tab maps audit entries with `actor: e.performed_by` (`frontend/src/pages/PayrollResults.tsx:1174`) into `TimelineTable` — today these are the self-asserted strings (`admin@internal`, `system`, free-text `resolved_by`) that F-06-01 confirmed, displayed verbatim as if they were actor identities.
- **Intended design**: Post-C1, audit records store operator UUIDs with display resolution via join, and every audit surface labels pre-epoch rows "identity unverified (pre-auth era)" mechanically from `platform_metadata.auth_cutover_epoch` (Stage 08 → 09 handoff item 2; threat-model §6).
- **Identified gap**: The highest-traffic audit surface has no actor-resolution or epoch-labelling concept; the `auditEntries` adapter is the single seam where the shared actor-display component lands (`outputs/auth-and-audit-surfaces.md` §Q8).
- **Evidence**: `frontend/src/pages/PayrollResults.tsx:1171-1174`; excerpts in `evidence/09-frontend-grounding-excerpts.md` §3. Read at `7d36020`.
- **Severity**: Informational — accurate rendering of the current (pre-auth) attribution model; recorded as the presentation-layer landing site for the epoch mechanism.
- **Status**: confirmed
- **Date**: 2026-07-17
- **Raised by**: Stage 09 (audit-surface grounding)

### F-09-04: The existing IA provides the patterns the new surfaces need — and contains no platform-level area

- **Current implementation**: Two-tier navigation (DD-1): TopBar (logo | workspace picker | user menu — including an unwired `userName` avatar) + workspace sidebar with numeric badge support on nav items, capped at 99+ (`frontend/src/design-system/components/Navigation.tsx:4-11,215,238,244,306-311`). The router (`frontend/src/router.tsx`) defines only the bureau dashboard (`/`) and `/workspaces/:workspaceId/*` — no platform-level admin routes exist. `NativeUploadFlow`/`ColumnMappingPanel` are shared components consumed by three pages (`Employees.tsx:1610`, `PayrollInputsBulkUpload.tsx:513`, `PayrollResults.tsx:443` — the reconciliation comparison upload; corrected per critic RC-1).
- **Intended design**: n/a — this is grounding, not a gap claim.
- **Identified gap**: None (informational). Consequences drawn in the outputs: the queue/pending-action badges and the notification bell reuse existing chrome patterns; C12 requires the platform's first platform-level area (one-off structural cost — `stage-11-handoff.md` §3); C13 extends live shared components rather than new surfaces.
- **Evidence**: `frontend/src/design-system/components/Navigation.tsx`, `frontend/src/router.tsx`, component grep — all read this session at `7d36020`; excerpts in `evidence/09-frontend-grounding-excerpts.md` §§1, 5, 6.
- **Severity**: Informational.
- **Status**: confirmed
- **Date**: 2026-07-17
- **Raised by**: Stage 09 (IA grounding)

---

## Parked / Rejected

_None._

## Next action

**None — stage closed 2026-07-17 on critic PASS (F-09-04 corrected per critic RC-1 pre-closure).**
