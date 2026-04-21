/**
 * S10 — New Payroll Run
 *
 * Design decisions honoured:
 * DD-3  Single primary action: "Run Payroll"
 * FRM-*  Form uses design system components throughout
 */

import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { payrollApi } from '../api/payroll';
import { workspaceApi } from '../api/workspace';
import {
  ContentHeader,
  Card,
  Btn,
  DateInput,
  SearchableSelect,
  RadioGroup,
  NumberInput,
  AlertBanner,
  useToast,
} from '../design-system';

// ── Helpers ───────────────────────────────────────────────────────────────────

function today() {
  return new Date().toISOString().slice(0, 10);
}

function firstOfMonth() {
  return today().slice(0, 7) + '-01';
}

// ── Component ─────────────────────────────────────────────────────────────────

export function RunPayroll() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const navigate = useNavigate();
  const toast = useToast();

  const [periodStart, setPeriodStart] = useState(firstOfMonth());
  const [periodEnd, setPeriodEnd] = useState(today());
  const [payDate, setPayDate] = useState(today());
  const [runType, setRunType] = useState<'REGULAR' | 'ADJUSTMENT'>('REGULAR');
  const [periodType, setPeriodType] = useState<'MONTHLY' | 'FORTNIGHTLY' | 'CUSTOM'>('MONTHLY');
  const [workingDays, setWorkingDays] = useState('');
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

    // Fix D: client-side date guard
    if (periodStart > periodEnd) {
      setError('Period start must be on or before period end.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const result = await payrollApi.createRun(workspaceId, {
        period_start: periodStart,
        period_end: periodEnd,
        pay_date: payDate,
        run_type: runType,
        period_type: periodType,
        ...(periodType === 'CUSTOM' && workingDays ? { working_days: Number(workingDays) } : {}),
        retry_strategy: retryStrategy,
      });
      toast.show('success', 'Payroll run started — calculating results…');
      navigate(`/workspaces/${workspaceId}/payroll/${result.run_id}/results`);
    } catch (e: unknown) {
      // Fix E: specific 409 message
      const status = (e as { response?: { status?: number } })?.response?.status;
      if (status === 409) {
        setError('A run for this period already exists — view it in the Runs list.');
      } else {
        setError(e instanceof Error ? e.message : 'Failed to create payroll run');
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-lg">
      <ContentHeader
        title="New Payroll Run"
        subtitle="Configure the period and submit to calculate results"
        back={
          <button
            onClick={() => navigate(`/workspaces/${workspaceId}/payroll`)}
            className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-brand transition-colors"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Runs
          </button>
        }
      />

      {!statusLoading && !isLive && (
        <AlertBanner
          variant="warning"
          title="Workspace not activated"
          description={`Payroll runs are only available when the workspace is LIVE. Current status: ${workspaceStatus ?? 'unknown'}.`}
          action={{
            label: 'Go to workspace settings →',
            onClick: () => navigate(`/workspaces/${workspaceId}`),
          }}
          className="mb-4"
        />
      )}

      <Card>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">

          {/* Period dates */}
          <div className="grid grid-cols-2 gap-4">
            <DateInput
              label="Period Start"
              value={periodStart}
              onChange={setPeriodStart}
              required
              disabled={!isLive}
            />
            <DateInput
              label="Period End"
              value={periodEnd}
              onChange={setPeriodEnd}
              required
              disabled={!isLive}
            />
          </div>

          <DateInput
            label="Pay Date"
            value={payDate}
            onChange={setPayDate}
            required
            disabled={!isLive}
          />

          {/* Run type */}
          <SearchableSelect
            label="Run Type"
            disabled={!isLive}
            value={runType}
            onChange={(v) => setRunType(v as 'REGULAR' | 'ADJUSTMENT')}
            options={[
              { value: 'REGULAR', label: 'Regular — standard monthly payroll' },
              { value: 'ADJUSTMENT', label: 'Adjustment — corrections or supplemental run' },
            ]}
          />

          {/* Period type */}
          <RadioGroup
            label="Period Type"
            name="period_type"
            value={periodType}
            onChange={(v) => { setPeriodType(v as 'MONTHLY' | 'FORTNIGHTLY' | 'CUSTOM'); setWorkingDays(''); }}
            options={[
              { value: 'MONTHLY',      label: 'Monthly',      description: 'Standard calendar month — working days calculated automatically' },
              { value: 'FORTNIGHTLY',  label: 'Fortnightly',  description: 'Two-week pay cycle' },
              { value: 'CUSTOM',       label: 'Custom',       description: 'Specify working days manually' },
            ]}
          />

          {periodType === 'CUSTOM' && (
            <NumberInput
              label="Working Days"
              value={workingDays}
              onChange={(e) => setWorkingDays(e.target.value)}
              min="1"
              max="31"
              required
              disabled={!isLive}
              hint="Number of working days in this pay period (e.g. 22)"
            />
          )}

          {/* Retry strategy */}
          <RadioGroup
            label="Retry Strategy"
            name="retry_strategy"
            value={retryStrategy}
            onChange={(v) => setRetryStrategy(v as 'PER_EMPLOYEE' | 'FULL_RUN')}
            options={[
              { value: 'PER_EMPLOYEE', label: 'Per Employee (recommended)', description: 'Failed employees are retried individually — successful employees are preserved' },
              { value: 'FULL_RUN',     label: 'Full Run',                   description: 'The entire run is retried from scratch on failure' },
            ]}
          />

          {error && (
            <AlertBanner variant="error" title="Failed to create run" description={error} />
          )}

          <div className="flex gap-3 pt-2">
            <Btn
              type="submit"
              variant="primary"
              size="md"
              loading={loading}
              disabled={statusLoading || !isLive}
            >
              Run Payroll
            </Btn>
            <Btn
              type="button"
              variant="secondary"
              size="md"
              onClick={() => navigate(`/workspaces/${workspaceId}/payroll`)}
            >
              Cancel
            </Btn>
          </div>
        </form>
      </Card>
    </div>
  );
}
