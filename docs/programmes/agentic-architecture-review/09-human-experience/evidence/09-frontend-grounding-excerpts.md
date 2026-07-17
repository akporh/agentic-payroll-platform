# Stage 09 Evidence: Frontend Grounding Excerpts

All excerpts read directly this session at git commit `7d36020` (branch `uat`, clean tree). These pin the existing-frontend facts the Stage 09 designs build on.

## 1. Two-tier navigation and the badge pattern

`frontend/src/design-system/components/Navigation.tsx`:

```
2  * Navigation — NAV-1 through NAV-5
4  * TopBar           NAV-1 — global top bar: logo | workspace picker | user menu
5  * WorkspaceSidebar NAV-2 — workspace nav: expanded 240px | collapsed 64px | mobile drawer
8  * OnboardingStepper NAV-5 — workspace setup stepper
11 * - DD-1: Two-tier navigation — top bar (bureau) + sidebar (workspace)
```

Sidebar items with numeric badges (lines 238, 244):

```
238  { label: 'Employees', to: `/workspaces/${w}/employees`, icon: 'employees', badge: (notEnrolledEmployeeCount + unmatchedEmployeeCount) || undefined },
244  { label: 'Inputs', to: `/workspaces/${w}/payroll/inputs`, icon: 'inputs',  end: true, badge: inputIssueCount || undefined },
```

Badge rendering caps at 99+ (line 311): `{item.badge > 99 ? '99+' : item.badge}`.

TopBar already renders a user menu (lines 158–167, `userName` prop with avatar initial) — currently fed by no authentication system.

## 2. Workspace switching is pure client navigation today

`frontend/src/components/layout/MainLayout.tsx:61`:

```
onWorkspaceSelect={(id) => navigate(`/workspaces/${id}`)}
```

Selecting a workspace in the TopBar picker performs a client-side route change only. No session, no token, no context invalidation — the workspace is navigation state.

## 3. Run detail: four tabs; Audit Log renders raw `performed_by` strings

`frontend/src/pages/PayrollResults.tsx`:

```
5   * DD-2  Four tabs: Results | Reconciliation | Timeline | Audit Log
63  type TabKey = 'results' | 'reconciliation' | 'timeline' | 'audit';
1171  const auditEntries = auditLog.map((e) => ({
1174    actor: e.performed_by,
```

The Audit Log tab maps `e.performed_by` directly to the `TimelineTable` actor column — today these are the self-asserted strings (`admin@internal`, `system`) that Stage 07/08's R1 rewiring replaces with operator UUIDs.

## 4. RunPayroll: FULL_RUN still offered; CORRECTION still absent

`frontend/src/pages/RunPayroll.tsx`:

```
45  const [runType, setRunType] = useState<'REGULAR' | 'ADJUSTMENT'>('REGULAR');
48  const [retryStrategy, setRetryStrategy] = useState<'PER_EMPLOYEE' | 'FULL_RUN'>('PER_EMPLOYEE');
```

Run Type select options (lines ~199–202): `REGULAR` and `ADJUSTMENT` only. Retry Strategy radio (lines ~235–240) still offers `FULL_RUN` ("The entire run is retried from scratch on failure") — the option the backend allowlist and DB CHECK constraint always reject (Stage 05 `frontend-backend-alignment.md` §1, re-verified unchanged at `7d36020`).

## 5. Upload flow components

`frontend/src/components/shared/NativeUploadFlow.tsx` and `frontend/src/components/shared/ColumnMappingPanel.tsx` exist and are consumed by `pages/Employees.tsx` and `pages/PayrollInputsBulkUpload.tsx` (grep this session) — the mapping panel C13 extends is a live, shared component, not a page-local widget.

## 6. Router structure

`frontend/src/router.tsx`: bureau dashboard at `/`; all workspace surfaces under `/workspaces/:workspaceId` (config, setup, public-holidays, rate-codes, attendance-configuration, timesheet, employees, payroll with runs/new/results/inputs/inputs-bulk). No platform-level admin area exists in the router today.
