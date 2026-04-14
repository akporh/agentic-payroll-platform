export type PayrollRunStatus =
  | 'DRAFT'
  | 'CALCULATING'
  | 'CALCULATED'
  | 'PARTIAL'
  | 'APPROVED'
  | 'LOCKED'
  | 'PAID';

export interface PayrollRun {
  run_id: string;
  workspace_id: string;
  period_start: string;
  period_end: string;
  pay_date: string;
  status: PayrollRunStatus;
  created_at: string;
}

export interface ComponentTraceEntry {
  rule: string;
  method: string;
  status: string;
  amount: string;
  note: string;
  resolution_source: string;
  warning?: string | null;
}

export interface PayrollResult {
  employee_id: string;
  employee_name: string;
  employee_number: string;
  gross_pay: number;
  total_deductions: number;
  net_pay: number;
  status: string;
  component_trace?: ComponentTraceEntry[];
}

export interface PayrollTotals {
  gross: number;
  deductions: number;
  net: number;
  employee_count: number;
}

export interface Employee {
  employee_id: string;
  full_name: string;
  employee_number: string;
  status: string;
  designation?: string;
  grade?: string;
  contract_start?: string;
}

export interface ReconciliationRecord {
  run_id: string;
  expected_total: number;
  actual_payment: number | null;
  status: 'MATCHED' | 'MISMATCH' | 'PENDING' | 'RESOLVED';
  notes: string | null;
  resolved_by: string | null;
  resolved_at: string | null;
}

export interface PayrollInput {
  payroll_input_id: string;
  employee_id: string;
  employee_name: string;
  employee_number: string;
  input_code: string;
  input_category: 'EARNING' | 'DEDUCTION' | 'INFORMATION';
  quantity: number | null;
  rate: number | null;
  amount: number | null;
  source: string;
  created_at: string;
  reference_date: string | null;
}

export interface AuditLogEntry {
  entity_type: string;
  action: string;
  old_value: Record<string, unknown> | null;
  new_value: Record<string, unknown> | null;
  performed_by: string;
  performed_at: string;
}

export interface ExecutionTraceStep {
  step_name: string;
  status: 'success' | 'error' | 'warn';
  duration_ms: number | null;
  error_message: string | null;
  created_at: string;
}

export interface WorkspacePayrollConfig {
  config_id?: string;
  workspace_id?: string;
  effective_from?: string;
  ph_mode: 'AUTOMATIC' | 'FILE_BASED';
  ph_rate_code: string;
  saturday_ph_rule: 'PH_TAKES_PRECEDENCE' | 'DAY_OF_WEEK_TAKES_PRECEDENCE';
  sunday_ph_rule: 'PH_TAKES_PRECEDENCE' | 'DAY_OF_WEEK_TAKES_PRECEDENCE';
  d3_leave_overlap_rule: 'LEAVE_ABSORBS_PH' | 'PH_ADDITIVE';
  d4_absence_rule: 'ABSENT_IS_DEDUCTIBLE' | 'PH_EXCUSES_ABSENCE';
}

export interface RateCode {
  rate_code_id: string;
  workspace_id: string | null;
  code: string;
  multiplier: number;
  unit: 'hour' | 'day';
  base: 'basic_hourly' | 'basic_daily';
  description: string | null;
  is_active: boolean;
  is_platform: boolean;
}

export interface PublicHoliday {
  holiday_id: string | null;
  date: string;
  name: string;
  source: 'NATIONAL' | 'WORKSPACE';
}
