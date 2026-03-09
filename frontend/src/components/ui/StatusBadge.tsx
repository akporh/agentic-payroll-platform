import type { WorkspaceStatus } from '../../types/workspace';
import type { PayrollRunStatus } from '../../types/payroll';

const WORKSPACE_COLORS: Record<WorkspaceStatus, string> = {
  DRAFT: 'bg-slate-100 text-slate-600',
  STRUCTURE_DEFINED: 'bg-blue-100 text-blue-700',
  COMPENSATION_DEFINED: 'bg-indigo-100 text-indigo-700',
  RULES_DEFINED: 'bg-violet-100 text-violet-700',
  READY: 'bg-amber-100 text-amber-700',
  LIVE: 'bg-green-100 text-green-700',
};

const PAYROLL_COLORS: Record<PayrollRunStatus, string> = {
  PENDING: 'bg-slate-100 text-slate-600',
  RUNNING: 'bg-blue-100 text-blue-700',
  COMPLETED: 'bg-green-100 text-green-700',
  FAILED: 'bg-red-100 text-red-700',
  APPROVED: 'bg-amber-100 text-amber-700',
  PAID: 'bg-emerald-100 text-emerald-700',
};

interface Props {
  status: string;
  type?: 'workspace' | 'payroll';
}

export function StatusBadge({ status, type = 'workspace' }: Props) {
  const colors =
    type === 'payroll'
      ? PAYROLL_COLORS[status as PayrollRunStatus]
      : WORKSPACE_COLORS[status as WorkspaceStatus];

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold uppercase tracking-wide ${colors ?? 'bg-slate-100 text-slate-500'}`}
    >
      {status.replace(/_/g, ' ')}
    </span>
  );
}
