import { api } from './client';
import type { PayrollInput } from '../types/payroll';

export const payrollInputApi = {
  list: (workspaceId: string) =>
    api.get<{ inputs: PayrollInput[]; count: number }>(
      `/${workspaceId}/payroll/inputs`
    ),

  create: (
    workspaceId: string,
    payload: {
      employee_id: string;
      input_code: string;
      quantity?: number;
      reference_date?: string;
    }
  ) =>
    api.post<{ status: string; payroll_input_id: string }>(
      `/${workspaceId}/payroll/inputs`,
      payload
    ),

  update: (
    workspaceId: string,
    inputId: string,
    payload: { quantity?: number; reference_date?: string }
  ) =>
    api.patch<{ status: string }>(`/${workspaceId}/payroll/inputs/${inputId}`, payload),

  delete: (workspaceId: string, inputId: string) =>
    api.delete<void>(`/${workspaceId}/payroll/inputs/${inputId}`),
};
