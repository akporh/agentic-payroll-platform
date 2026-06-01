/**
 * S11 — Run Detail (tabbed)
 *
 * Design decisions honoured:
 * DD-2  Four tabs: Results | Reconciliation | Timeline | Audit Log
 *        Run header (status, period, pay date) always visible above tabs
 * DD-3  Status-driven action panel — single primary action per status
 * DD-4  Mark as Paid opens ConfirmDialog with full consequences, red button
 * DD-7  Reconciliation tab: expected total hero card above the input form
 * DD-12 StatusBadge uses dot + text
 * DD-17 ExpandableRow uses grid-template-rows — no flicker (via DataTable renderExpanded)
 * DD-18 5s polling while run status is CALCULATING
 */

import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { payrollApi } from '../api/payroll';
import type {
  PayrollRun,
  PayrollResult,
  PayrollTotals,
  ExecutionTraceStep,
  AuditLogEntry,
  ReconciliationRecord,
} from '../types/payroll';
import {
  ContentHeader,
  Card,
  Btn,
  DownloadBtn,
  StatusBadge,
  SummaryCards,
  SummaryCard,
  TabBar,
  DataTable,
  ReconciliationCard,
  TimelineTable,
  AlertBanner,
  ConfirmDialog,
  Modal,
  EmptyState,
  NumberInput,
  Textarea,
  TextInput,
  useToast,
  formatNaira,
} from '../design-system';
import type { Tab, Column } from '../design-system';
import { PayrollTimeline } from '../components/payroll/PayrollTimeline';

// ── Tab keys ──────────────────────────────────────────────────────────────────

type TabKey = 'results' | 'reconciliation' | 'timeline' | 'audit';

const TABS: Tab[] = [
  { key: 'results',         label: 'Results' },
  { key: 'reconciliation',  label: 'Reconciliation' },
  { key: 'timeline',        label: 'Timeline' },
  { key: 'audit',           label: 'Audit Log' },
];

// ── Helper: format date range ─────────────────────────────────────────────────

function formatPeriod(start: string, end: string) {
  const opts: Intl.DateTimeFormatOptions = { day: 'numeric', month: 'short', year: 'numeric' };
  return `${new Date(start).toLocaleDateString('en-GB', opts)} – ${new Date(end).toLocaleDateString('en-GB', opts)}`;
}

// ── Status-driven Action Panel (DD-3) ─────────────────────────────────────────

interface ActionPanelProps {
  run: PayrollRun;
  onApprove: () => Promise<void>;
  onLock: () => Promise<void>;
  onPay: () => void;    // opens confirm dialog
  onRetry: () => Promise<void>;
  actionLoading: boolean;
}

function ActionPanel({ run, onApprove, onLock, onPay, onRetry, actionLoading }: ActionPanelProps) {
  if (run.status === 'CALCULATING') {
    return (
      <div className="mb-5 flex items-center gap-3 px-4 py-3 bg-blue-50 border border-blue-200 rounded-lg">
        <svg className="w-4 h-4 text-blue-500 animate-spin shrink-0" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
        </svg>
        <p className="text-sm text-blue-800 font-medium">Calculating payroll — refreshing automatically every 5 seconds…</p>
      </div>
    );
  }

  if (run.status === 'PARTIAL') {
    if (!run.statutory_effective_date) {
      return (
        <AlertBanner
          variant="warning"
          title="Some employees failed to calculate — retry not available"
          description="This run was created before the snapshot engine was enabled. Open a new payroll run to correct this period."
          className="mb-5"
        />
      );
    }
    return (
      <AlertBanner
        variant="warning"
        title="Some employees failed to calculate"
        description="Review the results table below. Retry to re-attempt failed employees — successful results are preserved."
        action={{ label: 'Retry Failed Employees', onClick: onRetry }}
        className="mb-5"
      />
    );
  }

  if (run.status === 'CALCULATED') {
    return (
      <div className="mb-5 flex items-center gap-3 px-4 py-3 bg-white border border-gray-200 rounded-lg" style={{ borderRadius: 'var(--radius-card)' }}>
        <div className="flex-1">
          <p className="text-sm font-semibold text-gray-800">Results calculated — ready for approval</p>
          <p className="text-xs text-gray-500 mt-0.5">Review the figures below, then approve to send for locking.</p>
        </div>
        <Btn variant="primary" size="md" loading={actionLoading} onClick={onApprove}>
          Approve Run
        </Btn>
      </div>
    );
  }

  if (run.status === 'APPROVED') {
    return (
      <div className="mb-5 flex items-center gap-3 px-4 py-3 bg-violet-50 border border-violet-200 rounded-lg" style={{ borderRadius: 'var(--radius-card)' }}>
        <div className="flex-1">
          <p className="text-sm font-semibold text-violet-800">Run approved. Lock it when ready for payment processing.</p>
          <p className="text-xs text-violet-600 mt-0.5">Locking prevents further changes and enables the Mark as Paid action.</p>
        </div>
        <Btn variant="primary" size="md" loading={actionLoading} onClick={onLock}>
          Lock Run
        </Btn>
      </div>
    );
  }

  if (run.status === 'LOCKED') {
    return (
      <div className="mb-5 flex items-center gap-3 px-4 py-3 bg-white border border-gray-200 rounded-lg" style={{ borderRadius: 'var(--radius-card)' }}>
        <div className="flex-1">
          <p className="text-sm font-semibold text-gray-800">Run is locked — ready to mark as paid</p>
          <p className="text-xs text-gray-500 mt-0.5">Once marked as PAID this cannot be undone.</p>
        </div>
        <Btn variant="destructive" size="md" onClick={onPay}>
          Mark as Paid
        </Btn>
      </div>
    );
  }

  if (run.status === 'PAID') {
    return (
      <div className="mb-5 px-4 py-3 bg-green-50 border border-green-200 rounded-lg" style={{ borderRadius: 'var(--radius-card)' }}>
        <p className="text-sm font-semibold text-green-800">Run is PAID — no further actions available.</p>
      </div>
    );
  }

  return null;
}

// ── Results Tab ───────────────────────────────────────────────────────────────

interface ResultsTabProps {
  run: PayrollRun;
  results: PayrollResult[];
  totals: PayrollTotals | null;
  timeline: ExecutionTraceStep[];
  canExport: boolean;
  canDownloadDetail: boolean;
  workspaceId: string;
  runId: string;
  onApprove: () => Promise<void>;
  onLock: () => Promise<void>;
  onPay: () => void;
  onRetry: () => Promise<void>;
  actionLoading: boolean;
  actionError: string | null;
}

function ResultsTab({ run, results, totals, timeline, canExport, canDownloadDetail, workspaceId, runId, onApprove, onLock, onPay, onRetry, actionLoading, actionError }: ResultsTabProps) {
  const toast = useToast();
  const [exportBusy, setExportBusy] = useState<string | null>(null);

  async function handleExport(exportType: 'bank-upload' | 'paye' | 'pension' | 'full-detail') {
    setExportBusy(exportType);
    try {
      await payrollApi.downloadExport(workspaceId, runId, exportType);
    } catch (e: unknown) {
      toast.show('error', e instanceof Error ? e.message : 'Export failed');
    } finally {
      setExportBusy(null);
    }
  }

  // PH warnings from timeline
  const phWarnings = timeline.filter((s) => s.status === 'warn');

  // Column widths — mirrored in TRACE_GRID below so expanded rows align exactly
  // chevron: w-10 (2.5rem) | employee: auto | gross: w-36 (9rem) | deductions: w-36 | net: w-36 | status: w-28 (7rem)
  const TRACE_GRID = '2.5rem 1fr 9rem 9rem 9rem 7rem';

  const EARNING_METHODS  = new Set(['salary_component', 'sum_earnings']);
  const DEDUCT_METHODS   = new Set(['pension_rule', 'paye_rule', 'life_insurance_rule']);
  const INFO_METHODS     = new Set(['pension_employer', 'taxable_income']);

  const columns: Column<PayrollResult>[] = [
    {
      key: 'employee',
      header: 'Employee',
      render: (r) => (
        <div>
          <p className="font-medium text-gray-800">{r.employee_name}</p>
          <p className="text-[11px] text-gray-400 mt-0.5 font-mono">{r.employee_number}</p>
        </div>
      ),
    },
    {
      key: 'gross',
      header: 'Gross Pay',
      align: 'right',
      width: 'w-36',
      render: (r) => (
        <span className="tabular-nums text-gray-700">
          {r.gross_pay != null ? formatNaira(r.gross_pay) : '—'}
        </span>
      ),
    },
    {
      key: 'deductions',
      header: 'Deductions',
      align: 'right',
      width: 'w-36',
      render: (r) => (
        <span className="tabular-nums text-red-600">
          {r.total_deductions != null ? formatNaira(r.total_deductions) : '—'}
        </span>
      ),
    },
    {
      key: 'net',
      header: 'Net Pay',
      align: 'right',
      width: 'w-36',
      render: (r) => (
        <span className="tabular-nums font-semibold text-gray-900">
          {r.net_pay != null ? formatNaira(r.net_pay) : '—'}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      align: 'center',
      width: 'w-28',
      render: (r) => <StatusBadge status={r.status} size="sm" />,
    },
  ];

  function renderTrace(r: PayrollResult) {
    if (!r.component_trace || r.component_trace.length === 0) {
      return (
        <p className="py-2 px-4 text-xs text-gray-400 italic">
          No component trace — legacy executor run.
        </p>
      );
    }

    const entries = r.component_trace.filter((e) => e.component !== '_period_context');
    const primary = entries.filter((e) => !INFO_METHODS.has(e.method));
    const info    = entries.filter((e) =>  INFO_METHODS.has(e.method));

    const CheckIcon = () => (
      <svg className="inline w-3.5 h-3.5 text-green-500" fill="none" stroke="currentColor" strokeWidth={2.5} viewBox="0 0 24 24" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
      </svg>
    );

    return (
      <div className="bg-slate-50 border-t border-gray-200">
        {/* Mini column headers — labelled to match parent columns */}
        <div style={{ display: 'grid', gridTemplateColumns: TRACE_GRID }} className="border-b border-gray-200">
          <div />
          <div className="px-4 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-gray-400">Component</div>
          <div className="px-4 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-gray-400 text-right">Gross Pay</div>
          <div className="px-4 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-gray-400 text-right">Deductions</div>
          <div className="px-4 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-gray-400 text-right">Net Pay</div>
          <div className="px-4 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-gray-400 text-center">Applied</div>
        </div>

        {primary.map((e, i) => {
          const hasResult  = e.result != null && e.result !== 'None';
          const amount     = hasResult ? parseFloat(e.result!) : null;
          const isEarning  = EARNING_METHODS.has(e.method);
          const isDeduct   = DEDUCT_METHODS.has(e.method);
          const isNet      = e.method === 'net_formula';
          const isSummary  = e.method === 'sum_earnings' || e.method === 'net_formula';

          return (
            <div
              key={i}
              style={{ display: 'grid', gridTemplateColumns: TRACE_GRID }}
              className={`text-xs border-t ${isSummary ? 'border-gray-200 bg-white font-semibold' : 'border-gray-100'}`}
            >
              <div className="flex items-center justify-center">
                <div className="w-px self-stretch bg-gray-200" />
              </div>
              <div className="px-4 py-1.5 min-w-0">
                <span className="font-mono font-medium text-gray-700 whitespace-nowrap">{e.component}</span>
                {!isSummary && (
                  <span className="ml-2 text-[10px] text-gray-400">{e.method}</span>
                )}
              </div>
              <div className="px-4 py-1.5 text-right tabular-nums text-gray-700">
                {isEarning && amount != null ? formatNaira(amount) : ''}
              </div>
              <div className="px-4 py-1.5 text-right tabular-nums text-red-600">
                {isDeduct && amount != null ? formatNaira(amount) : ''}
              </div>
              <div className="px-4 py-1.5 text-right tabular-nums text-gray-900">
                {isNet && amount != null ? formatNaira(amount) : ''}
              </div>
              <div className="px-4 py-1.5 flex items-center justify-center">
                {hasResult ? <CheckIcon /> : <span className="text-gray-300">—</span>}
              </div>
            </div>
          );
        })}

        {/* Intermediates (taxable_income, pension_employer) — contextual, not column-aligned */}
        {info.length > 0 && (
          <div className="border-t border-dashed border-gray-200 px-4 py-2 flex flex-wrap gap-x-6 gap-y-0.5">
            {info.map((e, i) => {
              const hasResult = e.result != null && e.result !== 'None';
              const amount    = hasResult ? parseFloat(e.result!) : null;
              return (
                <span key={i} className="text-[11px] text-gray-400">
                  <span className="font-mono font-medium text-gray-500">{e.component}</span>
                  <span className="mx-1 text-gray-300">·</span>
                  <span>{e.method}</span>
                  <span className="mx-1 text-gray-300">·</span>
                  <span className="tabular-nums">{amount != null ? formatNaira(amount) : '—'}</span>
                </span>
              );
            })}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {/* DD-3: status-driven action panel */}
      {actionError && (
        <AlertBanner variant="error" title="Action failed" description={actionError} className="mb-0" />
      )}
      <ActionPanel
        run={run}
        onApprove={onApprove}
        onLock={onLock}
        onPay={onPay}
        onRetry={onRetry}
        actionLoading={actionLoading}
      />

      {/* KPI summary cards — DAT-1 */}
      {totals && (
        <SummaryCards
          cols={4}
          cards={[
            { label: 'Employees',   value: String(totals.employee_count) },
            { label: 'Gross Pay',   value: `₦${totals.gross.toLocaleString('en-NG', { minimumFractionDigits: 2 })}` },
            { label: 'Deductions',  value: `₦${totals.deductions.toLocaleString('en-NG', { minimumFractionDigits: 2 })}` },
            { label: 'Net Pay',     value: `₦${totals.net.toLocaleString('en-NG', { minimumFractionDigits: 2 })}`, sublabel: 'Total disbursement' },
          ]}
        />
      )}

      {/* Downloads — Full Detail from CALCULATED onwards; remittance files from LOCKED/PAID only */}
      {canDownloadDetail && (
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Downloads:</span>
          <DownloadBtn label="Full Detail"      loading={exportBusy === 'full-detail'} onClick={() => handleExport('full-detail')} />
          {canExport && (
            <>
              <DownloadBtn label="Bank Upload"      loading={exportBusy === 'bank-upload'} onClick={() => handleExport('bank-upload')} />
              <DownloadBtn label="PAYE Remittance"  loading={exportBusy === 'paye'}        onClick={() => handleExport('paye')} />
              <DownloadBtn label="Pension"          loading={exportBusy === 'pension'}     onClick={() => handleExport('pension')} />
            </>
          )}
        </div>
      )}

      {/* PH warnings */}
      {phWarnings.length > 0 && (
        <AlertBanner
          variant="warning"
          title={`${phWarnings.length} public holiday warning${phWarnings.length !== 1 ? 's' : ''}`}
          description={phWarnings.slice(0, 2).map((w) => w.step_name + (w.error_message ? ': ' + w.error_message : '')).join(' · ') + (phWarnings.length > 2 ? ` +${phWarnings.length - 2} more — see Timeline tab` : '')}
        />
      )}

      {/* Employee results table — column-aligned expandable trace + tfoot totals */}
      <DataTable
        columns={columns}
        rows={results}
        getKey={(r) => r.employee_id}
        tableLayout="fixed"
        empty={
          <EmptyState
            headline="No results available"
            body="Results will appear here once the run has completed calculating."
          />
        }
        renderExpanded={renderTrace}
        footer={totals && results.length > 0 ? (
          <tr>
            <td />
            <td className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Totals</td>
            <td className="px-4 py-3 text-right text-sm font-semibold tabular-nums text-gray-700">{formatNaira(totals.gross)}</td>
            <td className="px-4 py-3 text-right text-sm font-semibold tabular-nums text-red-600">{formatNaira(totals.deductions)}</td>
            <td className="px-4 py-3 text-right text-sm font-bold tabular-nums text-gray-900">{formatNaira(totals.net)}</td>
            <td />
          </tr>
        ) : undefined}
      />
    </div>
  );
}

// ── Reconciliation Tab (DD-7: expected total hero) ────────────────────────────

interface RecTabProps {
  workspaceId: string;
  runId: string;
  totals: PayrollTotals | null;
}

function ReconciliationTab({ workspaceId, runId, totals }: RecTabProps) {
  const toast = useToast();
  const [record, setRecord] = useState<ReconciliationRecord | null>(null);
  const [recLoading, setRecLoading] = useState(true);
  const [recError, setRecError] = useState<string | null>(null);

  // Form: submit actual payment
  const [actualPayment, setActualPayment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Form: resolve mismatch
  const [resolveNotes, setResolveNotes] = useState('');
  const [resolveBy, setResolveBy] = useState('');
  const [resolving, setResolving] = useState(false);
  const [resolveError, setResolveError] = useState<string | null>(null);

  const load = useCallback(() => {
    setRecLoading(true);
    payrollApi
      .getReconciliation(workspaceId, runId)
      .then(setRecord)
      .catch((e: { response?: { status?: number }; message?: string }) => {
        if (e?.response?.status !== 404) setRecError(e.message ?? 'Failed to load');
      })
      .finally(() => setRecLoading(false));
  }, [workspaceId, runId]);

  useEffect(() => { load(); }, [load]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const amount = parseFloat(actualPayment);
    if (isNaN(amount)) { setSubmitError('Enter a valid amount'); return; }
    setSubmitting(true);
    setSubmitError(null);
    try {
      const updated = await payrollApi.submitReconciliation(workspaceId, runId, { actual_payment: amount });
      setRecord(updated);
      toast.show(updated.status === 'MATCHED' ? 'success' : 'warning',
        updated.status === 'MATCHED' ? 'Reconciliation matched — payment confirmed' : 'Mismatch detected — review and resolve'
      );
    } catch (e: unknown) {
      setSubmitError(e instanceof Error ? e.message : 'Submit failed');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleResolve(e: React.FormEvent) {
    e.preventDefault();
    setResolving(true);
    setResolveError(null);
    try {
      const updated = await payrollApi.resolveReconciliation(workspaceId, runId, { notes: resolveNotes, resolved_by: resolveBy });
      setRecord(updated);
      toast.show('success', 'Mismatch resolved');
    } catch (e: unknown) {
      setResolveError(e instanceof Error ? e.message : 'Resolve failed');
    } finally {
      setResolving(false);
    }
  }

  if (recLoading) {
    return <p className="text-sm text-gray-500 py-8 text-center">Loading reconciliation…</p>;
  }

  if (recError) {
    return <AlertBanner variant="error" title="Failed to load reconciliation" description={recError} />;
  }

  const expectedTotal = record?.expected_total ?? totals?.net ?? 0;
  const actualTotal = record?.actual_payment;
  const variance = record?.status === 'MISMATCH' && actualTotal != null
    ? actualTotal - expectedTotal
    : null;

  return (
    <div className="max-w-lg space-y-5">
      {/* DD-7: Expected total is the hero */}
      <SummaryCard
        label="Expected Net Pay (engine)"
        value={formatNaira(expectedTotal)}
        large
        sublabel="This is what the payroll engine calculated as the total disbursement"
      />

      {/* Reconciliation status card */}
      {record && (
        <ReconciliationCard
          status={
            record.status === 'PENDING' ? 'AWAITING'
            : record.status === 'MATCHED' ? 'MATCHED'
            : record.status === 'MISMATCH' ? 'MISMATCH'
            : 'RESOLVED'
          }
          expectedTotal={expectedTotal}
          actualTotal={actualTotal}
          variance={variance}
          resolvedBy={record.resolved_by ?? undefined}
          resolvedAt={record.resolved_at ? new Date(record.resolved_at).toLocaleString() : undefined}
          resolutionNote={record.notes ?? undefined}
        />
      )}

      {/* Submit actual payment form */}
      {(!record || record.status === 'PENDING' || record.status === 'MISMATCH') && (
        <Card>
          <p className="text-sm font-semibold text-gray-800 mb-4">Submit actual bank payment</p>
          <form onSubmit={handleSubmit} className="space-y-4">
            <NumberInput
              label="Actual Payment Amount"
              currency
              value={actualPayment}
              onChange={(e) => setActualPayment(e.target.value)}
              step="0.01"
              placeholder="0.00"
              required
              hint="Enter the exact amount disbursed by the bank"
            />
            {submitError && <AlertBanner variant="error" title="Submission failed" description={submitError} />}
            <Btn type="submit" variant="primary" loading={submitting}>
              Submit Reconciliation
            </Btn>
          </form>
        </Card>
      )}

      {/* Resolve mismatch form */}
      {record?.status === 'MISMATCH' && (
        <Card>
          <p className="text-sm font-semibold text-gray-800 mb-1">Mark mismatch as resolved</p>
          <p className="text-xs text-gray-500 mb-4">Use this only if the discrepancy has been investigated and is acceptable.</p>
          <form onSubmit={handleResolve} className="space-y-4">
            <Textarea
              label="Resolution Notes"
              value={resolveNotes}
              onChange={(e) => setResolveNotes(e.target.value)}
              placeholder="Explain why this discrepancy is considered resolved…"
              required
            />
            <TextInput
              label="Resolved By"
              value={resolveBy}
              onChange={(e) => setResolveBy(e.target.value)}
              placeholder="Your name or email"
              required
            />
            {resolveError && <AlertBanner variant="error" title="Resolve failed" description={resolveError} />}
            <Btn type="submit" variant="secondary" loading={resolving}>
              Mark as Resolved
            </Btn>
          </form>
        </Card>
      )}

      {record?.status === 'MATCHED' && (
        <AlertBanner variant="success" title="Reconciliation complete" description="Payment matches expected net pay." />
      )}
      {record?.status === 'RESOLVED' && (
        <AlertBanner variant="info" title="Mismatch resolved" description="This mismatch was closed by an operator. See resolution details above." />
      )}
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────

export function PayrollResults() {
  const { workspaceId, runId } = useParams<{ workspaceId: string; runId: string }>();
  const navigate = useNavigate();
  const toast = useToast();

  const [run, setRun] = useState<PayrollRun | null>(null);
  const [results, setResults] = useState<PayrollResult[]>([]);
  const [totals, setTotals] = useState<PayrollTotals | null>(null);
  const [timeline, setTimeline] = useState<ExecutionTraceStep[]>([]);
  const [auditLog, setAuditLog] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabKey>('results');
  const [showPayConfirm, setShowPayConfirm] = useState(false);
  const [payConfirmLoading, setPayConfirmLoading] = useState(false);
  const [showRetryBlockedModal, setShowRetryBlockedModal] = useState(false);

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

  // DD-18: poll every 5s while CALCULATING
  useEffect(() => {
    if (!run || run.status !== 'CALCULATING') return;
    const id = setInterval(fetchRun, 5000);
    return () => clearInterval(id);
  }, [run?.status, fetchRun]);

  // When run transitions out of CALCULATING, reload results
  const prevStatus = run?.status;
  useEffect(() => {
    if (prevStatus && prevStatus !== 'CALCULATING' && run?.status !== 'CALCULATING') return;
    if (run && run.status !== 'CALCULATING') {
      if (!workspaceId || !runId) return;
      payrollApi.getResults(workspaceId, runId)
        .then((data) => { setResults(data.results); setTotals(data.totals); })
        .catch(() => null);
    }
  }, [run?.status]);

  async function handleAction(label: string, fn: () => Promise<unknown>) {
    setActionLoading(true);
    setActionError(null);
    try {
      await fn();
      fetchRun();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : `${label} failed`;
      if (label === 'Retry' && msg.includes('predates snapshot engine')) {
        setShowRetryBlockedModal(true);
      } else {
        setActionError(msg);
      }
    } finally {
      setActionLoading(false);
    }
  }

  async function handlePay() {
    if (!runId) return;
    setPayConfirmLoading(true);
    try {
      await payrollApi.payRun(runId);
      fetchRun();
      setShowPayConfirm(false);
      toast.show('success', 'Run marked as PAID');
    } catch (e: unknown) {
      setActionError(e instanceof Error ? e.message : 'Mark as paid failed');
      setShowPayConfirm(false);
    } finally {
      setPayConfirmLoading(false);
    }
  }

  const canDownloadDetail = ['CALCULATED', 'APPROVED', 'LOCKED', 'PAID'].includes(run?.status ?? '');
  const canExport = run?.status === 'LOCKED' || run?.status === 'PAID';

  // Audit log adapted for TimelineTable
  const auditEntries = auditLog.map((e) => ({
    timestamp: new Date(e.performed_at).toLocaleString(),
    action: e.action,
    actor: e.performed_by,
    details: e.old_value && e.new_value
      ? `${JSON.stringify(e.old_value)} → ${JSON.stringify(e.new_value)}`
      : undefined,
  }));

  if (loading) {
    return (
      <div className="max-w-5xl">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-64" />
          <div className="h-4 bg-gray-200 rounded w-48" />
          <div className="grid grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => <div key={i} className="h-24 bg-gray-200 rounded-lg" />)}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-5xl">
        <AlertBanner variant="error" title="Failed to load run" description={error} />
      </div>
    );
  }

  return (
    <div className="max-w-5xl">
      {/* Back link */}
      <ContentHeader
        title={run ? `Run ${run.run_id.slice(0, 8)}…` : 'Run Detail'}
        subtitle={run ? formatPeriod(run.period_start, run.period_end) + (run.pay_date ? ' · Pay date: ' + new Date(run.pay_date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : '') : ''}
        back={
          <button
            onClick={() => navigate(`/workspaces/${workspaceId}/payroll`)}
            className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-brand transition-colors"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            All Runs
          </button>
        }
        action={run && <StatusBadge status={run.status} />}
      />

      {/* DD-2: Tab bar — always visible, run header above it */}
      <TabBar
        tabs={TABS}
        activeKey={activeTab}
        onChange={(k) => setActiveTab(k as TabKey)}
        className="mb-6"
      />

      {/* Tab content */}
      {activeTab === 'results' && run && workspaceId && runId && (
        <ResultsTab
          run={run}
          results={results}
          totals={totals}
          timeline={timeline}
          canExport={canExport}
          canDownloadDetail={canDownloadDetail}
          workspaceId={workspaceId}
          runId={runId}
          onApprove={() => handleAction('Approve', () => payrollApi.approveRun(runId))}
          onLock={() => handleAction('Lock', () => payrollApi.lockRun(runId))}
          onPay={() => setShowPayConfirm(true)}
          onRetry={() => handleAction('Retry', () => payrollApi.retryRun(runId))}
          actionLoading={actionLoading}
          actionError={actionError}
        />
      )}

      {activeTab === 'reconciliation' && workspaceId && runId && (
        <ReconciliationTab workspaceId={workspaceId} runId={runId} totals={totals} />
      )}

      {activeTab === 'timeline' && (
        timeline.length > 0
          ? <PayrollTimeline steps={timeline} />
          : <EmptyState headline="No timeline data" body="Execution timeline is only available for runs processed by the sequential executor." />
      )}

      {activeTab === 'audit' && (
        auditEntries.length > 0
          ? <Card padding="sm"><TimelineTable entries={auditEntries} /></Card>
          : <EmptyState headline="No audit events" body="Audit events are recorded when the run status changes or actions are taken." />
      )}

      {/* DD-4: Mark as Paid — intentionally friction-heavy ConfirmDialog */}
      <ConfirmDialog
        open={showPayConfirm}
        onClose={() => setShowPayConfirm(false)}
        onConfirm={handlePay}
        title="Mark run as PAID"
        body={
          <div className="space-y-2 text-sm text-gray-600">
            {run && (
              <p>
                <strong>Period:</strong>{' '}
                {formatPeriod(run.period_start, run.period_end)}
              </p>
            )}
            {totals && (
              <p>
                <strong>Net Pay:</strong>{' '}
                <span className="font-mono">{formatNaira(totals.net)}</span>
              </p>
            )}
            <p className="mt-3 font-semibold text-gray-800">
              This action is irreversible. Once marked as PAID, this run cannot be modified and no further changes can be made to employee results.
            </p>
          </div>
        }
        confirmLabel="Mark as Paid"
        cancelLabel="Go back"
        destructive
        loading={payConfirmLoading}
      />

      {/* EMP-UX-3: Retry blocked — run predates snapshot engine */}
      <Modal
        open={showRetryBlockedModal}
        onClose={() => setShowRetryBlockedModal(false)}
        title="Cannot retry this run"
        size="form"
        footer={
          <>
            <Btn variant="secondary" onClick={() => setShowRetryBlockedModal(false)}>Close</Btn>
            <Btn variant="primary" onClick={() => navigate(`/workspaces/${workspaceId}/payroll/new`)}>
              New Run →
            </Btn>
          </>
        }
      >
        <p className="text-sm text-gray-600">
          This run was created before the snapshot engine was enabled. Retrying would read live
          data and may produce different results to the original. To correct this period, open a
          new payroll run.
        </p>
      </Modal>
    </div>
  );
}
