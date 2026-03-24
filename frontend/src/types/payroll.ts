export type PayrollRunStatus =
  | 'PENDING'
  | 'RUNNING'
  | 'COMPLETED'
  | 'FAILED'
  | 'APPROVED'
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

export interface PayrollResult {
  employee_id: string;
  employee_name: string;
  employee_number: string;
  gross_pay: number;
  total_deductions: number;
  net_pay: number;
  status: string;
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
  status: 'MATCHED' | 'MISMATCH' | 'PENDING';
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

export interface ExecutionTraceStep {
  step_name: string;
  status: 'success' | 'error';
  duration_ms: number | null;
  error_message: string | null;
  created_at: string;
}
