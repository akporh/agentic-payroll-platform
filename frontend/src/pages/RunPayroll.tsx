import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { payrollApi } from '../api/payroll';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Btn } from '../components/ui/Btn';
import { AlertBox } from '../components/ui/AlertBox';

export function RunPayroll() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const navigate = useNavigate();

  const today = new Date().toISOString().slice(0, 10);
  const [periodStart, setPeriodStart] = useState(today.slice(0, 7) + '-01');
  const [periodEnd, setPeriodEnd] = useState(today);
  const [payDate, setPayDate] = useState(today);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!workspaceId) return;
    setLoading(true);
    setError(null);
    try {
      const result = await payrollApi.createRun(workspaceId, {
        period_start: periodStart,
        period_end: periodEnd,
        pay_date: payDate,
      });
      navigate(`/workspaces/${workspaceId}/payroll/${result.run_id}/results`);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to create payroll run');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="Run Payroll"
        subtitle={`Workspace ${workspaceId}`}
      />

      <div className="max-w-md">
        <Card title="New Payroll Run">
          <form onSubmit={handleSubmit} className="space-y-4">
            <Field label="Period Start">
              <input
                type="date"
                value={periodStart}
                onChange={(e) => setPeriodStart(e.target.value)}
                required
                className={inputClass}
              />
            </Field>

            <Field label="Period End">
              <input
                type="date"
                value={periodEnd}
                onChange={(e) => setPeriodEnd(e.target.value)}
                required
                className={inputClass}
              />
            </Field>

            <Field label="Pay Date">
              <input
                type="date"
                value={payDate}
                onChange={(e) => setPayDate(e.target.value)}
                required
                className={inputClass}
              />
            </Field>

            {error && <AlertBox type="error" messages={[error]} />}

            <div className="flex gap-2 pt-2">
              <Btn type="submit" loading={loading}>
                Run Payroll
              </Btn>
              <Btn
                type="button"
                variant="secondary"
                onClick={() => navigate(`/workspaces/${workspaceId}/payroll`)}
              >
                Cancel
              </Btn>
            </div>
          </form>
        </Card>

        <div className="mt-4 rounded border border-amber-200 bg-amber-50 px-4 py-3 text-xs text-amber-800">
          <strong>Note:</strong> Payroll runs are only available when the workspace status is{' '}
          <strong>LIVE</strong>. The backend will reject the request if the workspace is not ready.
        </div>
      </div>
    </div>
  );
}

const inputClass =
  'w-full border border-slate-200 rounded px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-slate-400';

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-xs font-medium text-slate-600 mb-1">{label}</label>
      {children}
    </div>
  );
}
