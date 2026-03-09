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
