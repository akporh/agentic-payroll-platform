import { api } from './client';
import type { PayrollRun, PayrollResult, PayrollTotals, ReconciliationRecord, ExecutionTraceStep } from '../types/payroll';

export const payrollApi = {
  createRun: (
    workspaceId: string,
    payload: { period_start: string; period_end: string; pay_date: string }
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

  getTimeline: (workspaceId: string, runId: string) =>
    api.get<ExecutionTraceStep[]>(`/${workspaceId}/payroll/runs/${runId}/timeline`),
};
