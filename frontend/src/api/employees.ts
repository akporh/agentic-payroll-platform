import { api } from './client';

export interface ContractRecord {
  contract_id: string;
  salary_definition_id: string | null;
  salary_definition_code: string | null;
  grade_code: string | null;
  designation_code: string | null;
  start_date: string | null;
  end_date: string | null;
  change_reason: string | null;
}

export interface EmployeeDetail {
  employee_id: string;
  employee_number: string;
  full_name: string;
  status: string;
  created_at: string | null;
  contracts: ContractRecord[];
}

export const employeesApi = {
  getEmployee: (workspaceId: string, employeeId: string) =>
    api.get<EmployeeDetail>(`/${workspaceId}/employees/${employeeId}`),

  updateEmployee: (
    workspaceId: string,
    employeeId: string,
    payload: { full_name?: string; status?: string }
  ) => api.patch<{ status: string }>(`/${workspaceId}/employees/${employeeId}`, payload),

  patchContract: (
    workspaceId: string,
    contractId: string,
    payload: { end_date: string }
  ) => api.patch<{ status: string }>(
    `/${workspaceId}/employee-contracts/${contractId}`,
    payload
  ),

  addContract: (
    workspaceId: string,
    employeeId: string,
    payload: {
      salary_definition_id: string;
      start_date: string;
      grade_code?: string | null;
      designation_code?: string | null;
      shift_type?: string | null;
      change_reason?: string | null;
    }
  ) =>
    api.post<{ status: string; contract_id: string }>(
      `/${workspaceId}/employees/${employeeId}/contracts`,
      payload
    ),
};
