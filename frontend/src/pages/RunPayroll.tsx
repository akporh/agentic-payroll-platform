import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { payrollApi } from '../api/payroll';
import { workspaceApi } from '../api/workspace';
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
  const [runType, setRunType] = useState<'REGULAR' | 'ADJUSTMENT'>('REGULAR');
  const [periodType, setPeriodType] = useState<'MONTHLY' | 'FORTNIGHTLY' | 'CUSTOM'>('MONTHLY');
  const [workingDays, setWorkingDays] = useState<string>('');
  const [retryStrategy, setRetryStrategy] = useState<'PER_EMPLOYEE' | 'FULL_RUN'>('PER_EMPLOYEE');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [workspaceStatus, setWorkspaceStatus] = useState<string | null>(null);
  const [statusLoading, setStatusLoading] = useState(true);

  useEffect(() => {
    if (!workspaceId) return;
    workspaceApi
      .getOnboardingStatus(workspaceId)
      .then((s) => setWorkspaceStatus(s.status))
      .catch(() => setWorkspaceStatus(null))
      .finally(() => setStatusLoading(false));
  }, [workspaceId]);

  const isLive = workspaceStatus === 'LIVE';

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!workspaceId || !isLive) return;
    setLoading(true);
    setError(null);
    try {
      const result = await payrollApi.createRun(workspaceId, {
        period_start: periodStart,
        period_end:   periodEnd,
        pay_date:     payDate,
        run_type:     runType,
        period_type:  periodType,
        ...(periodType === 'CUSTOM' && workingDays ? { working_days: Number(workingDays) } : {}),
        retry_strategy: retryStrategy,
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
        {!statusLoading && !isLive && (
          <div className="mb-4 rounded border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            <p className="font-semibold mb-1">Workspace not activated</p>
            <p className="text-xs">
              Payroll runs are only available once the workspace is <strong>LIVE</strong>.
              Your workspace is currently <strong>{workspaceStatus ?? 'unknown'}</strong>.{' '}
              <Link
                to={`/workspaces/${workspaceId}`}
                className="underline font-medium"
              >
                Go to workspace settings to activate it.
              </Link>
            </p>
          </div>
        )}

        <Card title="New Payroll Run">
          <form onSubmit={handleSubmit} className="space-y-4">
            <Field label="Period Start">
              <input
                type="date"
                value={periodStart}
                onChange={(e) => setPeriodStart(e.target.value)}
                required
                disabled={!isLive}
                className={inputClass}
              />
            </Field>

            <Field label="Period End">
              <input
                type="date"
                value={periodEnd}
                onChange={(e) => setPeriodEnd(e.target.value)}
                required
                disabled={!isLive}
                className={inputClass}
              />
            </Field>

            <Field label="Pay Date">
              <input
                type="date"
                value={payDate}
                onChange={(e) => setPayDate(e.target.value)}
                required
                disabled={!isLive}
                className={inputClass}
              />
            </Field>

            <Field label="Run Type">
              <select
                value={runType}
                onChange={(e) => setRunType(e.target.value as 'REGULAR' | 'ADJUSTMENT')}
                disabled={!isLive}
                className={inputClass}
              >
                <option value="REGULAR">Regular</option>
                <option value="ADJUSTMENT">Adjustment</option>
              </select>
            </Field>

            <Field label="Period Type">
              <select
                value={periodType}
                onChange={(e) => {
                  setPeriodType(e.target.value as 'MONTHLY' | 'FORTNIGHTLY' | 'CUSTOM');
                  setWorkingDays('');
                }}
                disabled={!isLive}
                className={inputClass}
              >
                <option value="MONTHLY">Monthly</option>
                <option value="FORTNIGHTLY">Fortnightly</option>
                <option value="CUSTOM">Custom</option>
              </select>
            </Field>

            {periodType === 'CUSTOM' && (
              <Field label="Working Days">
                <input
                  type="number"
                  min="1"
                  value={workingDays}
                  onChange={(e) => setWorkingDays(e.target.value)}
                  required
                  disabled={!isLive}
                  placeholder="e.g. 22"
                  className={inputClass}
                />
              </Field>
            )}

            <Field label="Retry Strategy">
              <select
                value={retryStrategy}
                onChange={(e) => setRetryStrategy(e.target.value as 'PER_EMPLOYEE' | 'FULL_RUN')}
                disabled={!isLive}
                className={inputClass}
              >
                <option value="PER_EMPLOYEE">Per Employee (default)</option>
                <option value="FULL_RUN">Full Run</option>
              </select>
            </Field>

            {error && <AlertBox type="error" messages={[error]} />}

            <div className="flex gap-2 pt-2">
              <Btn
                type="submit"
                loading={loading}
                disabled={statusLoading || !isLive}
                title={!isLive ? 'Workspace must be LIVE to run payroll' : undefined}
              >
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
      </div>
    </div>
  );
}

const inputClass =
  'w-full border border-slate-200 rounded px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-slate-400 disabled:bg-slate-50 disabled:text-slate-400 disabled:cursor-not-allowed';

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-xs font-medium text-slate-600 mb-1">{label}</label>
      {children}
    </div>
  );
}
