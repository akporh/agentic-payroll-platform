import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { payrollApi } from '../api/payroll';
import type { ReconciliationRecord } from '../types/payroll';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Btn } from '../components/ui/Btn';
import { AlertBox } from '../components/ui/AlertBox';

function fmt(n: number | null | undefined) {
  if (n == null) return '—';
  return n.toLocaleString('en-NG', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

export function Reconciliation() {
  const { workspaceId, runId } = useParams<{ workspaceId: string; runId: string }>();

  const [record, setRecord] = useState<ReconciliationRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [actualPayment, setActualPayment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  function load() {
    if (!workspaceId || !runId) return;
    setLoading(true);
    payrollApi
      .getReconciliation(workspaceId, runId)
      .then(setRecord)
      .catch((e: any) => {
        if (e?.response?.status !== 404) {
          setError(e.message);
        }
      })
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    load();
  }, [workspaceId, runId]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!workspaceId || !runId) return;
    const amount = parseFloat(actualPayment);
    if (isNaN(amount)) {
      setSubmitError('Enter a valid number');
      return;
    }
    setSubmitting(true);
    setSubmitError(null);
    try {
      const updated = await payrollApi.submitReconciliation(workspaceId, runId, {
        actual_payment: amount,
      });
      setRecord(updated);
    } catch (e: unknown) {
      setSubmitError(e instanceof Error ? e.message : 'Submit failed');
    } finally {
      setSubmitting(false);
    }
  }

  const statusColor =
    record?.status === 'MATCHED'
      ? 'bg-green-100 text-green-700 border-green-200'
      : record?.status === 'MISMATCH'
      ? 'bg-red-100 text-red-700 border-red-200'
      : 'bg-slate-100 text-slate-600 border-slate-200';

  return (
    <div>
      <PageHeader
        title="Payroll Reconciliation"
        subtitle={`Run ${runId?.slice(0, 8)}… · Workspace ${workspaceId}`}
      />

      {loading && <p className="text-sm text-slate-500">Loading reconciliation…</p>}
      {error && <AlertBox type="error" messages={[error]} />}

      {!loading && !error && (
        <div className="max-w-lg space-y-4">
          {record && (
            <Card title="Reconciliation Status">
              <div className="space-y-4">
                <Row label="Expected Total (Net Pay)" value={fmt(record.expected_total)} />
                <Row label="Actual Payment" value={fmt(record.actual_payment)} />

                {record.status && (
                  <div
                    className={`inline-flex px-4 py-2 rounded border text-sm font-bold uppercase tracking-wide ${statusColor}`}
                  >
                    {record.status}
                  </div>
                )}

                {record.status === 'MISMATCH' && record.actual_payment != null && (
                  <div className="text-sm text-red-600">
                    Variance:{' '}
                    <strong>{fmt(Math.abs(record.expected_total - record.actual_payment))}</strong>
                  </div>
                )}
              </div>
            </Card>
          )}

          {(!record || record.status === 'PENDING' || record.status === 'MISMATCH') && (
            <Card title="Submit Actual Payment">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">
                    Actual Payment Amount
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    placeholder="0.00"
                    value={actualPayment}
                    onChange={(e) => setActualPayment(e.target.value)}
                    required
                    className="w-full border border-slate-200 rounded px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-slate-400"
                  />
                </div>

                {submitError && <AlertBox type="error" messages={[submitError]} />}

                <Btn type="submit" loading={submitting}>
                  Submit Reconciliation
                </Btn>
              </form>
            </Card>
          )}

          {record?.status === 'MATCHED' && (
            <AlertBox type="success" messages={['Reconciliation complete. Payment matches expected net pay.']} />
          )}
        </div>
      )}
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-slate-50 last:border-0">
      <span className="text-sm text-slate-500">{label}</span>
      <span className="text-sm font-semibold text-slate-800 font-mono">{value}</span>
    </div>
  );
}
