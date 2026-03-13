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
      rate?: number;
      amount?: number;
    }
  ) =>
    api.post<{ status: string; payroll_input_id: string }>(
      `/${workspaceId}/payroll/inputs`,
      payload
    ),

  delete: (workspaceId: string, inputId: string) =>
    api.delete<void>(`/${workspaceId}/payroll/inputs/${inputId}`),
};
