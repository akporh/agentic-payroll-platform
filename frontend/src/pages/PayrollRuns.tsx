/**
 * S9 — Payroll Runs List
 *
 * Design decisions honoured:
 * DD-5  Empty state: two variants (LIVE / not LIVE), both have a specific CTA
 * DD-18 5s polling when any run is CALCULATING; toast on status change
 * DD-12 StatusBadge uses dot + text (never colour alone)
 * DD-3  Single primary action per screen: "+ New Run"
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { payrollApi } from '../api/payroll';
import { workspaceApi } from '../api/workspace';
import type { PayrollRun } from '../types/payroll';
import {
  ContentHeader,
  Card,
  Btn,
  StatusBadge,
  EmptyState,
  AlertBanner,
  useToast,
  Breadcrumb,
} from '../design-system';
import { useWorkspaceContext } from '../context/WorkspaceContext';

// ── Icons ─────────────────────────────────────────────────────────────────────

function RunsIcon() {
  return (
    <svg className="w-full h-full" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}

function SetupIcon() {
  return (
    <svg className="w-full h-full" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
    </svg>
  );
}

function PlusIcon() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
    </svg>
  );
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function formatPeriod(start: string, end: string): string {
  const s = new Date(start).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
  const e = new Date(end).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
  return `${s} – ${e}`;
}

function formatDate(d: string | null | undefined) {
  if (!d) return '—';
  return new Date(d).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
}

// ── Component ─────────────────────────────────────────────────────────────────

export function PayrollRuns() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const navigate = useNavigate();
  const toast = useToast();
  const { workspace } = useWorkspaceContext();

  const [runs, setRuns] = useState<PayrollRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isLive, setIsLive] = useState(false);
  const pollFailCount = useRef(0);

  const fetchRuns = useCallback(async (silent = false) => {
    if (!workspaceId) return;
    if (!silent) setLoading(true);
    try {
      const newRuns = await payrollApi.getRuns(workspaceId);
      pollFailCount.current = 0;
      setRuns((prev) => {
        // DD-18: toast when a CALCULATING run transitions to a new status
        if (silent) {
          prev.forEach((old) => {
            const updated = newRuns.find((r) => r.run_id === old.run_id);
            if (old.status === 'CALCULATING' && updated && updated.status !== 'CALCULATING') {
              const label = updated.status === 'CALCULATED'
                ? 'Payroll run completed successfully'
                : updated.status === 'PARTIAL'
                ? 'Run completed with some failures — review results'
                : `Run status: ${updated.status}`;
              const variant = updated.status === 'CALCULATED' ? 'success' : 'warning';
              toast.show(variant, label);
            }
          });
        }
        return newRuns;
      });
    } catch (e: unknown) {
      if (!silent) {
        setError(e instanceof Error ? e.message : 'Failed to load runs');
      } else {
        pollFailCount.current += 1;
        if (pollFailCount.current >= 3) {
          setError('Auto-refresh paused — check your connection.');
        }
      }
    } finally {
      if (!silent) setLoading(false);
    }
  }, [workspaceId]);

  useEffect(() => {
    fetchRuns();
    if (!workspaceId) return;
    workspaceApi
      .getOnboardingStatus(workspaceId)
      .then((s) => setIsLive(s.status === 'LIVE'))
      .catch(() => setIsLive(false));
  }, [workspaceId]);

  // DD-18: 5s polling when any run is CALCULATING; stops after 3 consecutive failures
  const hasCalculating = runs.some((r) => r.status === 'CALCULATING');
  useEffect(() => {
    if (!hasCalculating || error) return;
    const id = setInterval(() => fetchRuns(true), 5000);
    return () => clearInterval(id);
  }, [hasCalculating, error, fetchRuns]);

  return (
    <div className="max-w-5xl">
      <ContentHeader
        title="Payroll Runs"
        subtitle={loading ? 'Loading…' : `${runs.length} run${runs.length !== 1 ? 's' : ''}`}
        back={
          <Breadcrumb items={[
            { label: 'Bureau Dashboard', to: '/' },
            { label: workspace?.name ?? '…', to: `/workspaces/${workspaceId}` },
            { label: 'Payroll Runs' },
          ]} />
        }
        action={
          <Btn
            variant="primary"
            size="md"
            icon={<PlusIcon />}
            iconPosition="left"
            disabled={!isLive}
            title={!isLive ? 'Workspace must be LIVE to run payroll' : undefined}
            onClick={() => navigate(`/workspaces/${workspaceId}/payroll/new`)}
          >
            New Run
          </Btn>
        }
      />

      {error && <AlertBanner variant="error" title="Failed to load runs" description={error} className="mb-4" />}

      {!isLive && !loading && (
        <AlertBanner
          variant="info"
          title="Workspace not activated"
          description="Payroll runs are only available once the workspace is LIVE. Complete the setup wizard to activate."
          action={{ label: 'Continue Setup →', onClick: () => navigate(`/workspaces/${workspaceId}/setup`) }}
          className="mb-4"
        />
      )}

      <Card padding="sm">
        {loading ? (
          /* Skeleton rows while fetching */
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                {['Period', 'Pay Date', 'Status', 'Run ID', ''].map((h, i) => (
                  <th key={i} className="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-gray-500">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="animate-pulse border-b border-gray-100">
                  {[70, 40, 30, 30, 20].map((w, j) => (
                    <td key={j} className="px-4 py-3">
                      <div className="h-4 bg-gray-200 rounded" style={{ width: `${w}%` }} />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        ) : runs.length === 0 ? (
          /* DD-5: empty state with specific CTA */
          isLive ? (
            <EmptyState
              icon={<RunsIcon />}
              headline="No payroll runs yet"
              body="Add variable inputs for the period, then create your first payroll run."
              action={{
                label: '+ New Run',
                onClick: () => navigate(`/workspaces/${workspaceId}/payroll/new`),
              }}
            />
          ) : (
            <EmptyState
              icon={<SetupIcon />}
              headline="Complete setup to unlock payroll runs"
              body="Payroll runs require the workspace to be LIVE. Finish the setup wizard to activate this workspace."
              action={{
                label: 'Continue Setup',
                onClick: () => navigate(`/workspaces/${workspaceId}/setup`),
              }}
            />
          )
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50 sticky top-0">
                  {['Period', 'Pay Date', 'Status', 'Run ID', ''].map((h, i) => (
                    <th key={i} className={`px-4 py-3 text-[11px] font-semibold uppercase tracking-wider text-gray-500 ${i === 2 ? 'text-center' : 'text-left'} ${i === 4 ? 'w-32' : ''}`}>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {runs.map((run) => (
                  <tr
                    key={run.run_id}
                    className="border-b border-gray-100 hover:bg-slate-50 transition-colors cursor-pointer"
                    onClick={() => navigate(`/workspaces/${workspaceId}/payroll/${run.run_id}/results`)}
                  >
                    <td className="px-4 py-3 text-gray-800 font-medium">
                      {formatPeriod(run.period_start, run.period_end)}
                    </td>
                    <td className="px-4 py-3 text-gray-600">{formatDate(run.pay_date)}</td>
                    <td className="px-4 py-3 text-center">
                      <StatusBadge status={run.status} />
                    </td>
                    <td className="px-4 py-3 font-mono text-xs text-gray-400">{run.run_id.slice(0, 8)}…</td>
                    <td className="px-4 py-3">
                      <Btn
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/workspaces/${workspaceId}/payroll/${run.run_id}/results`);
                        }}
                      >
                        View Results →
                      </Btn>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
