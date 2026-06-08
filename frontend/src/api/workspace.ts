import { api } from './client';
import type { Workspace, OnboardingStatus } from '../types/workspace';
import type { Employee, WorkspacePayrollConfig, RateCode, PublicHoliday } from '../types/payroll';

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
      code: string;
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

  publishRuleSet: (
    workspaceId: string,
    payload: {
      rules: Array<{
        rule_name: string;
        rule_definition_json: Record<string, unknown>;
        rule_type?: string;
        effective_from: string;  // ISO date "YYYY-MM-DD"
      }>;
      created_by?: string;  // UUID of publishing user
    }
  ) => api.post(`/${workspaceId}/rule-set`, payload),

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
    api.get<{
      workspace: { id: string; name: string; country_code: string; currency_code: string; status: string };
      pay_cycle: { frequency: string; run_day: number; cutoff_day: number; payment_day: number } | null;
      grades: { code: string; description: string | null }[];
      designations: { code: string; description: string | null }[];
      salary_definitions: {
        salary_definition_id: string; name: string; code: string;
        components: { component_name: string; amount: number }[];
      }[];
      payroll_rules: { rule_id: string; name: string; rule_type: string; method: string; is_active: boolean; rule_definition_json: Record<string, unknown> }[];
      component_overrides: { component_name: string; is_active: boolean; proration_strategy: string | null }[];
    }>(`/${workspaceId}/configuration`),

  updateEmployeeContract: (
    workspaceId: string,
    employeeId: string,
    payload: {
      grade_code?: string | null;
      designation_code?: string | null;
      contract_end?: string | null;
      set_contract_end?: boolean;
    }
  ) => api.patch(`/${workspaceId}/employees/${employeeId}/contract`, payload),

  createEmployee: (
    workspaceId: string,
    payload: {
      first_name: string;
      last_name: string;
      employee_number: string;
      salary_definition_code?: string | null;
      grade_code?: string | null;
      designation_code?: string | null;
      contract_start?: string | null;
      contract_end?: string | null;
      tin?: string | null;
      rsa?: string | null;
      bank?: string | null;
      account_number?: string | null;
    }
  ) => api.post<{ status: string; employee_id: string; full_name: string }>(
    `/${workspaceId}/employees`,
    payload
  ),

  enrollEmployee: (
    workspaceId: string,
    employeeId: string,
    payload: {
      salary_definition_code: string;
      grade_code?: string | null;
      designation_code?: string | null;
    }
  ) => api.post<{ status: string; employee_id: string }>(
    `/${workspaceId}/employees/${employeeId}/enroll`,
    payload
  ),

  bulkEnrollEmployees: (
    workspaceId: string,
    payload: {
      employee_ids: string[];
      salary_definition_code: string;
      grade_code?: string | null;
      designation_code?: string | null;
    }
  ) => api.post<{
    enrolled: number;
    skipped: number;
    failed: number;
    details: { employee_id: string; status: string; reason?: string }[];
  }>(`/${workspaceId}/employees/bulk-enroll`, payload),

  getInputCodes: (workspaceId: string) =>
    api.get<{
      input_codes: {
        code: string;
        category: string;
        rule_name: string;
        calculation_method: string;
      }[];
    }>(`/${workspaceId}/payroll/input-codes`),

  // PH-6 — Workspace Payroll Config
  getPayrollConfig: (workspaceId: string) =>
    api.get<WorkspacePayrollConfig>(`/workspaces/${workspaceId}/payroll-config`),

  upsertPayrollConfig: (workspaceId: string, payload: Partial<WorkspacePayrollConfig> & { effective_from: string }) =>
    api.put<WorkspacePayrollConfig>(`/workspaces/${workspaceId}/payroll-config`, payload),

  // PH-7 — Rate Code Registry
  getRateCodes: (workspaceId: string) =>
    api.get<RateCode[]>(`/workspaces/${workspaceId}/rate-codes`),

  addRateCode: (workspaceId: string, payload: { code: string; multiplier: number; unit: string; base: string; description?: string }) =>
    api.post<RateCode>(`/workspaces/${workspaceId}/rate-codes`, payload),

  deleteRateCode: (workspaceId: string, code: string) =>
    api.delete<{ status: string; code: string }>(`/workspaces/${workspaceId}/rate-codes/${code}`),

  // PH-1 — Public Holiday Calendar
  getPublicHolidays: (workspaceId: string, year?: number) =>
    api.get<PublicHoliday[]>(
      `/workspaces/${workspaceId}/public-holidays${year ? `?year=${year}` : ''}`
    ),

  addPublicHoliday: (workspaceId: string, payload: { date: string; name: string }) =>
    api.post<PublicHoliday>(`/workspaces/${workspaceId}/public-holidays`, payload),

  deletePublicHoliday: (workspaceId: string, holidayId: string) =>
    api.delete<{ status: string; holiday_id: string }>(`/workspaces/${workspaceId}/public-holidays/${holidayId}`),

  // Track J — Post-Onboarding Config Management PATCH endpoints
  updatePayCycle: (workspaceId: string, payload: {
    frequency?: string; run_day?: number; cutoff_day?: number; payment_day?: number;
  }) => api.patch<{ status: string }>(`/${workspaceId}/pay-cycle`, payload),

  updateGrade: (workspaceId: string, gradeCode: string, payload: { description?: string }) =>
    api.patch<{ status: string }>(`/${workspaceId}/grade/${encodeURIComponent(gradeCode)}`, payload),

  updateDesignation: (workspaceId: string, designationCode: string, payload: { description?: string }) =>
    api.patch<{ status: string }>(`/${workspaceId}/designation/${encodeURIComponent(designationCode)}`, payload),

  updateSalaryDefinition: (workspaceId: string, salaryDefinitionId: string, payload: {
    description?: string;
    components_jsonb: Array<{ component_name: string; amount: number }>;
  }) => api.patch<{ status: string }>(`/${workspaceId}/salary-definition/${salaryDefinitionId}`, payload),

  updatePayrollRule: (workspaceId: string, ruleId: string, payload: { is_active?: boolean; rule_name?: string; rule_definition_json?: Record<string, unknown> }) =>
    api.patch<{ status: string }>(`/${workspaceId}/payroll-rule/${ruleId}`, payload),

  deletePayrollRule: (workspaceId: string, ruleId: string) =>
    api.delete<{ status: string; rule_id: string }>(`/${workspaceId}/payroll-rule/${ruleId}`),

  updateComponentOverride: (workspaceId: string, componentCode: string, payload: {
    is_active?: boolean; proration_strategy?: string; overrides_json?: Record<string, unknown>;
  }) => api.patch<{ status: string }>(`/${workspaceId}/component-overrides/${encodeURIComponent(componentCode)}`, payload),

  getPlatformComponents: (workspaceId: string) =>
    api.get<Array<{ component_code: string; label: string; component_class: string }>>(
      `/${workspaceId}/platform-components`
    ),
};
