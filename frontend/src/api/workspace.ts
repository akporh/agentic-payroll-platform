import { api } from './client';
import type { Workspace, OnboardingStatus } from '../types/workspace';
import type { Employee } from '../types/payroll';

export const workspaceApi = {
  list: () => api.get<Workspace[]>('/workspaces'),

  create: (payload: { name: string; country_code: string; base_currency?: string }) =>
    api.post<Workspace>('/workspace', payload),

  // Legacy single-workspace info endpoint
  getInfo: () => api.get<Workspace>('/workspace/info'),

  getOnboardingStatus: (workspaceId: string) =>
    api.get<OnboardingStatus>(`/${workspaceId}/onboarding-status`),

  transition: (workspaceId: string, targetState: string) =>
    api.post<{ workspace_id: string; from: string; to: string }>(
      `/${workspaceId}/transition?target_state=${targetState}`,
      {}
    ),

  createPayCycle: (
    workspaceId: string,
    payload: {
      frequency: string;
      run_day: number;
      cutoff_day: number;
      payment_day: number;
    }
  ) => api.post(`/${workspaceId}/pay-cycle`, payload),

  createGrade: (
    workspaceId: string,
    payload: { grade_code: string; description?: string }
  ) => api.post(`/${workspaceId}/grade`, payload),

  createDesignation: (
    workspaceId: string,
    payload: { designation_code: string; description?: string }
  ) => api.post(`/${workspaceId}/designation`, payload),

  createSalaryDefinition: (
    workspaceId: string,
    payload: {
      name: string;
      components_jsonb: Record<string, unknown>;
      effective_from?: string;
      effective_to?: string;
    }
  ) => api.post(`/${workspaceId}/salary-definition`, payload),

  createPayrollRule: (
    workspaceId: string,
    payload: {
      rule_name: string;
      rule_definition_json: Record<string, unknown>;
      rule_type: string;
    }
  ) => api.post(`/${workspaceId}/payroll-rule`, payload),

  createComponentMetadata: (
    workspaceId: string,
    payload: {
      version: number;
      rules_jsonb: Record<string, unknown>;
      effective_from: string;
    }
  ) => api.post(`/${workspaceId}/component-metadata`, payload),

  getEmployees: (workspaceId: string) =>
    api.get<Employee[]>(`/${workspaceId}/employees`),

  getSalaryDefinitions: (workspaceId: string) =>
    api.get<{ salary_definition_id: string; code: string; name: string }[]>(
      `/${workspaceId}/salary-definitions`
    ),

  getDesignations: (workspaceId: string) =>
    api.get<{ designation_id: string; code: string }[]>(
      `/${workspaceId}/designations`
    ),

  addSalaryDefinition: (workspaceId: string, code: string, name?: string) =>
    api.post<{ salary_definition_id: string; code: string; name: string }>(
      `/${workspaceId}/salary-definitions`,
      { code, name }
    ),

  getConfiguration: (workspaceId: string) =>
    api.get<{ grades: { code: string }[]; designations: { code: string }[] }>(
      `/${workspaceId}/configuration`
    ),

  updateEmployeeContract: (
    workspaceId: string,
    employeeId: string,
    payload: { grade_code?: string | null; designation_code?: string | null }
  ) => api.patch(`/${workspaceId}/employees/${employeeId}/contract`, payload),
};
