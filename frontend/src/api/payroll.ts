import { api } from './client';
import type { PayrollRun, PayrollResult, PayrollTotals, ReconciliationRecord, ExecutionTraceStep, AuditLogEntry, TimesheetEntry, AttendanceCodeConfig } from '../types/payroll';

export const payrollApi = {
  createRun: (
    workspaceId: string,
    payload: {
      period_start: string;
      period_end: string;
      pay_date: string;
      run_type?: string;
      period_type?: 'MONTHLY' | 'FORTNIGHTLY' | 'CUSTOM';
      working_days?: number;
      retry_strategy?: 'PER_EMPLOYEE' | 'FULL_RUN';
    }
  ) => api.post<{ run_id: string; status: string }>(`/${workspaceId}/payroll/run`, payload),

  getRuns: (workspaceId: string) =>
    api.get<PayrollRun[]>(`/${workspaceId}/payroll/runs`),

  getRun: (workspaceId: string, runId: string) =>
    api.get<PayrollRun>(`/${workspaceId}/payroll/runs/${runId}`),

  getResults: (workspaceId: string, runId: string) =>
    api.get<{ results: PayrollResult[]; totals: PayrollTotals }>(
      `/${workspaceId}/payroll/runs/${runId}/results`
    ),

  getReconciliation: (workspaceId: string, runId: string) =>
    api.get<ReconciliationRecord>(`/${workspaceId}/payroll/runs/${runId}/reconciliation`),

  submitReconciliation: (
    workspaceId: string,
    runId: string,
    payload: { actual_payment: number }
  ) =>
    api.post<ReconciliationRecord>(
      `/${workspaceId}/payroll/runs/${runId}/reconciliation`,
      payload
    ),

  resolveReconciliation: (
    workspaceId: string,
    runId: string,
    payload: { notes: string; resolved_by: string }
  ) =>
    api.patch<ReconciliationRecord>(
      `/${workspaceId}/payroll/runs/${runId}/reconciliation`,
      payload
    ),

  getTimeline: (workspaceId: string, runId: string) =>
    api.get<ExecutionTraceStep[]>(`/${workspaceId}/payroll/runs/${runId}/timeline`),

  approveRun: (runId: string) =>
    api.post<{ run_id: string; run_status: string }>(`/payroll/run/${runId}/approve`, {}),

  lockRun: (runId: string) =>
    api.post<{ run_id: string; run_status: string }>(`/payroll/run/${runId}/lock`, {}),

  payRun: (runId: string) =>
    api.post<{ run_id: string; run_status: string }>(`/payroll/run/${runId}/pay`, {}),

  retryRun: (runId: string) =>
    api.post<{ run_id: string; retried: number; success: number; still_failed: number }>(
      `/payroll/run/${runId}/retry`,
      {}
    ),

  getAuditLog: (workspaceId: string, runId: string) =>
    api.get<AuditLogEntry[]>(`/${workspaceId}/payroll/runs/${runId}/audit`),

  // ── Timesheet ──────────────────────────────────────────────────────────────

  uploadTimesheet: (workspaceId: string, periodStart: string, periodEnd: string, file: File) => {
    const fd = new FormData();
    fd.append('file', file);
    fd.append('period_start', periodStart);
    fd.append('period_end', periodEnd);
    return fetch(`/api/workspaces/${workspaceId}/timesheet/upload`, { method: 'POST', body: fd })
      .then(async (r) => {
        const json = await r.json();
        if (!r.ok) throw new Error(json.detail ?? r.statusText);
        return json;
      });
  },

  triggerDerivation: (workspaceId: string, periodStart: string, periodEnd: string) =>
    api.post<{ results: unknown[] }>(`/workspaces/${workspaceId}/timesheet/derive`, {
      period_start: periodStart,
      period_end: periodEnd,
    }),

  approveTimesheetPeriod: (workspaceId: string, periodStart: string, periodEnd: string) =>
    api.post<{ status: string }>(`/workspaces/${workspaceId}/timesheet/approve`, {
      period_start: periodStart,
      period_end: periodEnd,
    }),

  getTimesheetStatus: (workspaceId: string, periodStart: string) =>
    api.get<TimesheetEntry[]>(
      `/workspaces/${workspaceId}/timesheet/status?period_start=${periodStart}`
    ),

  // ── Attendance Config ───────────────────────────────────────────────────────

  getAttendanceCodes: (workspaceId: string) =>
    api.get<AttendanceCodeConfig[]>(`/workspaces/${workspaceId}/attendance-codes`),

  createAttendanceCode: (workspaceId: string, payload: Omit<AttendanceCodeConfig, 'attendance_code_config_id' | 'workspace_id' | 'has_policy'>) =>
    api.post<AttendanceCodeConfig>(`/workspaces/${workspaceId}/attendance-codes`, payload),

  patchAttendanceCode: (workspaceId: string, clientCode: string, payload: { description?: string; is_active?: boolean }) =>
    api.patch<AttendanceCodeConfig>(`/workspaces/${workspaceId}/attendance-codes/${clientCode}`, payload),

  patchAttendancePolicy: (
    workspaceId: string,
    clientCode: string,
    payload: Partial<Pick<AttendanceCodeConfig, 'counts_as_paid' | 'counts_towards_ot_threshold' | 'hours_equivalent' | 'unit_fraction' | 'eligible_for_shift_allowance' | 'eligible_for_ot'>>
  ) =>
    api.patch<AttendanceCodeConfig>(`/workspaces/${workspaceId}/attendance-policies/${clientCode}`, payload),

  /** Fetch a CSV export and trigger a browser download. */
  downloadExport: async (workspaceId: string, runId: string, exportType: 'bank-upload' | 'paye' | 'pension' | 'full-detail') => {
    const res = await fetch(`/api/${workspaceId}/payroll/runs/${runId}/exports/${exportType}`);
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`${res.status} ${res.statusText}: ${text}`);
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = res.headers.get('Content-Disposition')?.match(/filename="([^"]+)"/)?.[1]
      ?? `${exportType}_${runId.slice(0, 8)}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },
};
