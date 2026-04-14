import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { payrollApi } from '../api/payroll';
import type { PayrollRun, PayrollResult, PayrollTotals, ExecutionTraceStep, AuditLogEntry, ComponentTraceEntry } from '../types/payroll';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Btn } from '../components/ui/Btn';
import { AlertBox } from '../components/ui/AlertBox';
import { PayrollTimeline } from '../components/payroll/PayrollTimeline';

function fmt(n: number) {
  return n.toLocaleString('en-NG', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

export function PayrollResults() {
  const { workspaceId, runId } = useParams<{ workspaceId: string; runId: string }>();
  const navigate = useNavigate();

  const [run, setRun] = useState<PayrollRun | null>(null);
  const [results, setResults] = useState<PayrollResult[]>([]);
  const [totals, setTotals] = useState<PayrollTotals | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [timeline, setTimeline] = useState<ExecutionTraceStep[]>([]);
  const [auditLog, setAuditLog] = useState<AuditLogEntry[]>([]);
  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  const fetchRun = useCallback(() => {
    if (!workspaceId || !runId) return;
    payrollApi.getRun(workspaceId, runId).then(setRun).catch(() => null);
  }, [workspaceId, runId]);

  useEffect(() => {
    if (!workspaceId || !runId) return;
    Promise.all([
      payrollApi.getResults(workspaceId, runId),
      payrollApi.getTimeline(workspaceId, runId).catch(() => []),
      payrollApi.getRun(workspaceId, runId),
      payrollApi.getAuditLog(workspaceId, runId).catch(() => []),
    ])
      .then(([data, steps, runData, audit]) => {
        setResults(data.results);
        setTotals(data.totals);
        setTimeline(steps);
        setRun(runData);
        setAuditLog(audit);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [workspaceId, runId]);

  async function handleAction(action: () => Promise<unknown>) {
    setActionError(null);
    try {
      await action();
      fetchRun();
    } catch (e: unknown) {
      setActionError(e instanceof Error ? e.message : 'Action failed');
    }
  }

  const canReconcile = run?.status === 'LOCKED' || run?.status === 'PAID';
  const canExport = run?.status === 'LOCKED' || run?.status === 'PAID';

  const [exportError, setExportError] = useState<string | null>(null);
  const [exportBusy, setExportBusy] = useState<string | null>(null);

  async function handleExport(exportType: 'bank-upload' | 'paye' | 'pension') {
    if (!workspaceId || !runId) return;
    setExportError(null);
    setExportBusy(exportType);
    try {
      await payrollApi.downloadExport(workspaceId, runId, exportType);
    } catch (e: unknown) {
      setExportError(e instanceof Error ? e.message : 'Export failed');
    } finally {
      setExportBusy(null);
    }
  }

  return (
    <div>
      <PageHeader
        title="Payroll Results"
        subtitle={`Run ${runId?.slice(0, 8)}… · Workspace ${workspaceId}`}
        action={
          canReconcile ? (
            <Btn
              variant="secondary"
              size="sm"
              onClick={() =>
                navigate(`/workspaces/${workspaceId}/payroll/${runId}/reconciliation`)
              }
            >
              Reconcile →
            </Btn>
          ) : undefined
        }
      />

      {loading && <p className="text-sm text-slate-500">Loading results…</p>}
      {error && <AlertBox type="error" messages={[error]} />}
      {actionError && <AlertBox type="error" messages={[actionError]} />}

      {run && runId && (
        <RunActions
          run={run}
          onApprove={() => handleAction(() => payrollApi.approveRun(runId))}
          onLock={() => handleAction(() => payrollApi.lockRun(runId))}
          onPay={() => handleAction(() => payrollApi.payRun(runId))}
          onRetry={() => handleAction(() => payrollApi.retryRun(runId))}
        />
      )}

      {totals && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-5">
          <StatCard label="Employees" value={String(totals.employee_count)} />
          <StatCard label="Gross Pay" value={fmt(totals.gross)} />
          <StatCard label="Deductions" value={fmt(totals.deductions)} />
          <StatCard label="Net Pay" value={fmt(totals.net)} highlight />
        </div>
      )}

      {/* H1/H2/H3 — Export buttons */}
      {canExport && workspaceId && runId && (
        <div className="mb-4">
          <div className="flex gap-2 flex-wrap items-center">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide mr-1">
              Downloads:
            </span>
            {(
              [
                { type: 'bank-upload', label: 'Bank Upload' },
                { type: 'paye',        label: 'PAYE Remittance' },
                { type: 'pension',     label: 'Pension' },
              ] as const
            ).map(({ type, label }) => (
              <button
                key={type}
                onClick={() => handleExport(type)}
                disabled={exportBusy === type}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium border border-slate-200 rounded hover:bg-slate-50 disabled:opacity-50 disabled:cursor-wait"
              >
                <svg className="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                {exportBusy === type ? 'Downloading…' : label}
              </button>
            ))}
          </div>
          {exportError && <p className="text-xs text-red-500 mt-1.5">{exportError}</p>}
        </div>
      )}

      {/* PH warning banner (G6 — PH-10) */}
      {(() => {
        const phWarnings = timeline.filter((s) => s.status === 'warn');
        if (phWarnings.length === 0) return null;
        const shown = phWarnings.slice(0, 2);
        const rest = phWarnings.length - shown.length;
        return (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-4">
            <h3 className="font-medium text-amber-800 mb-2">⚠ Public Holiday Warnings</h3>
            <ul className="space-y-1">
              {shown.map((w, i) => (
                <li key={i} className="text-sm text-amber-700">
                  <span className="font-mono font-medium mr-2">{w.step_name}</span>
                  {w.error_message && <span className="text-amber-600">{w.error_message}</span>}
                </li>
              ))}
            </ul>
            {rest > 0 && (
              <p className="text-xs text-amber-500 mt-1">+{rest} more warning{rest !== 1 ? 's' : ''} — see Execution Timeline below.</p>
            )}
          </div>
        );
      })()}

      {!loading && !error && timeline.length > 0 && (
        <div className="mb-5">
          <PayrollTimeline steps={timeline} />
        </div>
      )}

      {auditLog.length > 0 && (
        <div className="mb-5">
          <h2 className="text-sm font-semibold text-slate-700 mb-2">Audit Trail</h2>
          <Card>
            <ul className="divide-y divide-slate-100">
              {auditLog.map((entry, i) => (
                <li key={i} className="py-2 px-3 text-xs text-slate-600 flex gap-3">
                  <span className="text-slate-400 whitespace-nowrap">
                    {new Date(entry.performed_at).toLocaleString()}
                  </span>
                  <span className="font-medium text-slate-700">{entry.performed_by}</span>
                  <span className="text-slate-500">{entry.action}</span>
                  {entry.old_value && entry.new_value && (
                    <span>
                      <span className="text-red-500">{JSON.stringify(entry.old_value)}</span>
                      {' → '}
                      <span className="text-green-600">{JSON.stringify(entry.new_value)}</span>
                    </span>
                  )}
                </li>
              ))}
            </ul>
          </Card>
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
                  <>
                    <tr
                      key={r.employee_id}
                      className="border-b border-slate-50 hover:bg-slate-50 cursor-pointer"
                      onClick={() => setExpandedRow(expandedRow === r.employee_id ? null : r.employee_id)}
                    >
                      <Td className="font-medium text-slate-800">
                        <span className="mr-1 text-slate-400">{expandedRow === r.employee_id ? '▼' : '▶'}</span>
                        {r.employee_name}
                      </Td>
                      <Td className="font-mono text-xs">{r.employee_number}</Td>
                      <Td align="right">{r.gross_pay != null ? fmt(r.gross_pay) : '—'}</Td>
                      <Td align="right" className="text-red-600">
                        {r.total_deductions != null ? fmt(r.total_deductions) : '—'}
                      </Td>
                      <Td align="right" className="font-semibold">
                        {r.net_pay != null ? fmt(r.net_pay) : '—'}
                      </Td>
                      <Td>
                        <span className="text-xs uppercase text-slate-500">{r.status}</span>
                      </Td>
                    </tr>
                    {expandedRow === r.employee_id && r.component_trace && r.component_trace.length > 0 && (
                      <tr key={`${r.employee_id}-trace`} className="bg-slate-50">
                        <td colSpan={6} className="px-3 py-2">
                          <ComponentTrace entries={r.component_trace} />
                        </td>
                      </tr>
                    )}
                  </>
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

function ComponentTrace({ entries }: { entries: ComponentTraceEntry[] }) {
  return (
    <table className="w-full text-xs border-collapse">
      <thead>
        <tr className="text-slate-400 uppercase tracking-wide">
          <th className="text-left py-1 px-2">Rule</th>
          <th className="text-left py-1 px-2">Method</th>
          <th className="text-left py-1 px-2">Status</th>
          <th className="text-right py-1 px-2">Amount</th>
          <th className="text-left py-1 px-2">Note</th>
          <th className="text-left py-1 px-2">Source</th>
        </tr>
      </thead>
      <tbody>
        {entries.map((e, i) => (
          <tr
            key={i}
            className={`border-t border-slate-200 ${e.warning ? 'bg-amber-50' : ''}`}
          >
            <td className="py-1 px-2 font-mono text-slate-700">{e.rule}</td>
            <td className="py-1 px-2 text-slate-500">{e.method}</td>
            <td className="py-1 px-2">
              <span className={e.status === 'applied' ? 'text-green-600' : 'text-slate-400'}>
                {e.status}
              </span>
            </td>
            <td className="py-1 px-2 text-right font-mono">{e.amount}</td>
            <td className="py-1 px-2 text-slate-500 max-w-xs truncate">{e.note}</td>
            <td className="py-1 px-2">
              {e.resolution_source === 'current_fallback' ? (
                <span className="text-amber-600 font-medium">⚠ fallback</span>
              ) : (
                <span className="text-slate-400">{e.resolution_source}</span>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function RunActions({
  run,
  onApprove,
  onLock,
  onPay,
  onRetry,
}: {
  run: PayrollRun;
  onApprove: () => void;
  onLock: () => void;
  onPay: () => void;
  onRetry: () => void;
}) {
  const [busy, setBusy] = useState<string | null>(null);

  async function wrap(label: string, fn: () => void) {
    setBusy(label);
    try { await fn(); } finally { setBusy(null); }
  }

  if (run.status === 'CALCULATED') {
    return (
      <div className="mb-4 flex gap-2">
        <Btn variant="primary" size="sm" loading={busy === 'approve'} onClick={() => wrap('approve', onApprove)}>
          Approve
        </Btn>
      </div>
    );
  }
  if (run.status === 'PARTIAL') {
    return (
      <div className="mb-4 flex gap-2">
        <Btn variant="secondary" size="sm" loading={busy === 'retry'} onClick={() => wrap('retry', onRetry)}>
          Retry Failed
        </Btn>
      </div>
    );
  }
  if (run.status === 'APPROVED') {
    return (
      <div className="mb-4 flex gap-2">
        <Btn variant="primary" size="sm" loading={busy === 'lock'} onClick={() => wrap('lock', onLock)}>
          Lock
        </Btn>
      </div>
    );
  }
  if (run.status === 'LOCKED') {
    return (
      <div className="mb-4 flex gap-2">
        <Btn variant="primary" size="sm" loading={busy === 'pay'} onClick={() => wrap('pay', onPay)}>
          Mark Paid
        </Btn>
      </div>
    );
  }
  return null;
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
