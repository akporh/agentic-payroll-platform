import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { payrollApi } from '../api/payroll';
import type { PayrollResult, PayrollTotals } from '../types/payroll';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Btn } from '../components/ui/Btn';
import { AlertBox } from '../components/ui/AlertBox';

function fmt(n: number) {
  return n.toLocaleString('en-NG', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

export function PayrollResults() {
  const { workspaceId, runId } = useParams<{ workspaceId: string; runId: string }>();
  const navigate = useNavigate();

  const [results, setResults] = useState<PayrollResult[]>([]);
  const [totals, setTotals] = useState<PayrollTotals | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!workspaceId || !runId) return;
    payrollApi
      .getResults(workspaceId, runId)
      .then((data) => {
        setResults(data.results);
        setTotals(data.totals);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [workspaceId, runId]);

  return (
    <div>
      <PageHeader
        title="Payroll Results"
        subtitle={`Run ${runId?.slice(0, 8)}… · Workspace ${workspaceId}`}
        action={
          <Btn
            variant="secondary"
            size="sm"
            onClick={() =>
              navigate(`/workspaces/${workspaceId}/payroll/${runId}/reconciliation`)
            }
          >
            Reconcile →
          </Btn>
        }
      />

      {loading && <p className="text-sm text-slate-500">Loading results…</p>}
      {error && <AlertBox type="error" messages={[error]} />}

      {totals && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-5">
          <StatCard label="Employees" value={String(totals.employee_count)} />
          <StatCard label="Gross Pay" value={fmt(totals.gross)} />
          <StatCard label="Deductions" value={fmt(totals.deductions)} />
          <StatCard label="Net Pay" value={fmt(totals.net)} highlight />
        </div>
      )}

      {!loading && !error && (
        <Card>
          {results.length === 0 ? (
            <p className="text-sm text-slate-400 py-8 text-center">No results available.</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100">
                  <Th>Employee</Th>
                  <Th>Number</Th>
                  <Th align="right">Gross Pay</Th>
                  <Th align="right">Deductions</Th>
                  <Th align="right">Net Pay</Th>
                  <Th>Status</Th>
                </tr>
              </thead>
              <tbody>
                {results.map((r) => (
                  <tr key={r.employee_id} className="border-b border-slate-50 hover:bg-slate-50">
                    <Td className="font-medium text-slate-800">{r.employee_name}</Td>
                    <Td className="font-mono text-xs">{r.employee_number}</Td>
                    <Td align="right">{fmt(r.gross_pay)}</Td>
                    <Td align="right" className="text-red-600">
                      {fmt(r.total_deductions)}
                    </Td>
                    <Td align="right" className="font-semibold">
                      {fmt(r.net_pay)}
                    </Td>
                    <Td>
                      <span className="text-xs uppercase text-slate-500">{r.status}</span>
                    </Td>
                  </tr>
                ))}
              </tbody>
              {totals && (
                <tfoot>
                  <tr className="border-t-2 border-slate-200 bg-slate-50 font-semibold">
                    <Td className="text-slate-700" colSpan={2}>
                      Totals
                    </Td>
                    <Td align="right" className="text-slate-700">
                      {fmt(totals.gross)}
                    </Td>
                    <Td align="right" className="text-red-600">
                      {fmt(totals.deductions)}
                    </Td>
                    <Td align="right" className="text-slate-900">
                      {fmt(totals.net)}
                    </Td>
                    <Td />
                  </tr>
                </tfoot>
              )}
            </table>
          )}
        </Card>
      )}
    </div>
  );
}

function StatCard({
  label,
  value,
  highlight,
}: {
  label: string;
  value: string;
  highlight?: boolean;
}) {
  return (
    <div
      className={`rounded-lg border p-4 ${
        highlight ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'
      }`}
    >
      <p className={`text-xs font-medium mb-1 ${highlight ? 'text-slate-400' : 'text-slate-500'}`}>
        {label}
      </p>
      <p className={`text-lg font-bold ${highlight ? 'text-white' : 'text-slate-800'}`}>{value}</p>
    </div>
  );
}

function Th({
  children,
  align = 'left',
}: {
  children?: React.ReactNode;
  align?: 'left' | 'right';
}) {
  return (
    <th
      className={`text-xs font-semibold text-slate-500 uppercase tracking-wide py-2 px-3 ${
        align === 'right' ? 'text-right' : 'text-left'
      }`}
    >
      {children}
    </th>
  );
}

function Td({
  children,
  className = '',
  align = 'left',
  colSpan,
}: {
  children?: React.ReactNode;
  className?: string;
  align?: 'left' | 'right';
  colSpan?: number;
}) {
  return (
    <td
      colSpan={colSpan}
      className={`py-3 px-3 text-slate-600 ${align === 'right' ? 'text-right' : ''} ${className}`}
    >
      {children}
    </td>
  );
}
