/**
 * Workspace Dashboard — Gate 4 rewrite
 *
 * Design decisions:
 * - Title = workspace name (resolved from workspaceApi.list()), NOT the raw UUID
 * - Bespoke StateFlow re-skinned with design-system tokens
 * - Human-readable transition labels (TRANSITION_LABELS map)
 * - Primary CTA per status for non-LIVE workspaces
 */

import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { workspaceApi } from '../api/workspace';
import type { OnboardingStatus, WorkspaceStatus } from '../types/workspace';
import {
  ContentHeader,
  Card,
  Btn,
  StatusBadge,
  AlertBanner,
  ProgressBar,
  Breadcrumb,
} from '../design-system';

// ── Transition labels ─────────────────────────────────────────────────────────

const TRANSITION_LABELS: Record<string, string> = {
  STRUCTURE_DEFINED:    'Confirm structure is set up →',
  COMPENSATION_DEFINED: 'Confirm compensation is set up →',
  RULES_DEFINED:        'Confirm payroll rules are set up →',
  READY:                'Mark workspace as ready →',
  LIVE:                 'Activate workspace →',
};

// ── StateFlow ─────────────────────────────────────────────────────────────────

const STATE_SEQUENCE: WorkspaceStatus[] = [
  'DRAFT',
  'STRUCTURE_DEFINED',
  'COMPENSATION_DEFINED',
  'RULES_DEFINED',
  'READY',
  'LIVE',
];

const STATE_SHORT: Record<string, string> = {
  DRAFT:                'Draft',
  STRUCTURE_DEFINED:    'Structure',
  COMPENSATION_DEFINED: 'Compensation',
  RULES_DEFINED:        'Rules',
  READY:                'Ready',
  LIVE:                 'Live',
};

function StateFlow({ currentStatus }: { currentStatus: string }) {
  const currentIdx = STATE_SEQUENCE.indexOf(currentStatus as WorkspaceStatus);
  return (
    <div className="flex items-center gap-0 flex-wrap gap-y-2">
      {STATE_SEQUENCE.map((state, i) => {
        const done   = i < currentIdx;
        const active = i === currentIdx;
        return (
          <div key={state} className="flex items-center">
            <div
              style={{ borderRadius: 'var(--radius-badge)' }}
              className={`px-2.5 py-1 text-xs font-semibold whitespace-nowrap transition-colors ${
                active
                  ? 'bg-brand text-white'
                  : done
                  ? 'bg-green-100 text-green-700'
                  : 'bg-gray-100 text-gray-400'
              }`}
            >
              {STATE_SHORT[state] ?? state}
            </div>
            {i < STATE_SEQUENCE.length - 1 && (
              <span className={`text-sm px-1 ${done ? 'text-green-400' : 'text-gray-300'}`}>→</span>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ── Quick action tile ─────────────────────────────────────────────────────────

function ActionTile({
  label,
  desc,
  onClick,
  disabled,
}: {
  label: string;
  desc: string;
  onClick: () => void;
  disabled?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{ borderRadius: 'var(--radius-card)' }}
      className="text-left p-3 border border-gray-200 hover:bg-slate-50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
    >
      <p className="text-sm font-semibold text-gray-700">{label}</p>
      <p className="text-xs text-gray-400 mt-0.5">{desc}</p>
    </button>
  );
}

// ── Missing checklist ─────────────────────────────────────────────────────────

function MissingChecklist({ missing }: { missing: string[] }) {
  if (missing.length === 0) {
    return <p className="text-xs text-green-700 font-medium">All setup steps complete.</p>;
  }
  return (
    <ul className="space-y-1 mt-2">
      {missing.map((item) => (
        <li key={item} className="flex items-center gap-2 text-xs text-gray-600">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400 shrink-0" />
          {item}
        </li>
      ))}
    </ul>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────

export function WorkspaceDashboard() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const navigate = useNavigate();

  const [workspaceName, setWorkspaceName] = useState<string | null>(null);
  const [status, setStatus] = useState<OnboardingStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [transitioning, setTransitioning] = useState(false);
  const [transitionError, setTransitionError] = useState<string | null>(null);
  const [transitionSuccess, setTransitionSuccess] = useState<string | null>(null);

  const load = useCallback(() => {
    if (!workspaceId) return;
    setLoading(true);
    setError(null);
    Promise.all([
      workspaceApi.getOnboardingStatus(workspaceId),
      workspaceApi.list().catch(() => []),
    ])
      .then(([onboarding, allWorkspaces]) => {
        setStatus(onboarding);
        const ws = allWorkspaces.find((w) => w.workspace_id === workspaceId);
        if (ws) setWorkspaceName(ws.name);
      })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : 'Failed to load'))
      .finally(() => setLoading(false));
  }, [workspaceId]);

  useEffect(() => { load(); }, [load]);

  async function handleTransition(targetState: string) {
    if (!workspaceId) return;
    setTransitioning(true);
    setTransitionError(null);
    setTransitionSuccess(null);
    try {
      const result = await workspaceApi.transition(workspaceId, targetState);
      setTransitionSuccess(`Workspace advanced to ${result.to}`);
      load();
    } catch (e: unknown) {
      setTransitionError(e instanceof Error ? e.message : 'Transition failed');
    } finally {
      setTransitioning(false);
    }
  }

  if (loading) {
    return (
      <div className="max-w-5xl animate-pulse space-y-4">
        <div className="h-8 bg-gray-200 rounded w-56" />
        <div className="h-4 bg-gray-200 rounded w-32" />
        <div className="grid grid-cols-3 gap-5 mt-6">
          {[1, 2, 3].map((i) => <div key={i} className="h-40 bg-gray-200 rounded-lg" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl">
      <ContentHeader
        title={workspaceName ?? 'Workspace Overview'}
        subtitle={status ? `Status: ${status.status}` : ''}
        back={
          <Breadcrumb items={[
            { label: 'Bureau Dashboard', to: '/' },
            { label: workspaceName ?? '…' },
          ]} />
        }
        action={
          status && (
            <div className="flex items-center gap-2">
              <StatusBadge status={status.status} />
            </div>
          )
        }
      />

      {error && <AlertBanner variant="error" title="Failed to load workspace" description={error} className="mb-4" />}

      {status && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">

          {/* Status + progress */}
          <Card className="lg:col-span-1">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Setup Progress</p>
            <ProgressBar percent={status.progress_percent} />
            <p className="text-xs text-gray-500 mt-1">{status.progress_percent}% complete</p>
            <div className="mt-4">
              <MissingChecklist missing={status.missing} />
            </div>
          </Card>

          {/* State lifecycle + transition */}
          <Card className="lg:col-span-2">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">State Lifecycle</p>
            <StateFlow currentStatus={status.status} />

            {status.next_allowed_states.length > 0 ? (
              <div className="mt-5 space-y-2">
                {status.next_allowed_states.map((state) => (
                  <Btn
                    key={state}
                    variant="primary"
                    size="md"
                    loading={transitioning}
                    onClick={() => handleTransition(state)}
                  >
                    {TRANSITION_LABELS[state] ?? `→ ${state.replace(/_/g, ' ')}`}
                  </Btn>
                ))}
              </div>
            ) : (
              <p className="mt-4 text-xs text-gray-400">
                {status.status === 'LIVE'
                  ? 'Workspace is LIVE — all payroll features are available.'
                  : 'Complete all required setup steps before advancing.'}
              </p>
            )}

            {transitionError && (
              <div className="mt-3">
                <AlertBanner variant="error" title="Transition failed" description={transitionError} />
              </div>
            )}
            {transitionSuccess && (
              <div className="mt-3">
                <AlertBanner variant="success" title="Status updated" description={transitionSuccess} />
              </div>
            )}
          </Card>

          {/* Quick actions */}
          <Card className="lg:col-span-3">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Quick Actions</p>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
              <ActionTile
                label="Client Setup"
                desc="Re-run workspace setup wizard"
                onClick={() => navigate(`/workspaces/${workspaceId}/setup`)}
              />
              <ActionTile
                label="Configuration"
                desc="View workspace settings"
                onClick={() => navigate(`/workspaces/${workspaceId}/config`)}
              />
              <ActionTile
                label="Employees"
                desc="View active headcount"
                onClick={() => navigate(`/workspaces/${workspaceId}/employees`)}
              />
              <ActionTile
                label="Run Payroll"
                desc="Create a new payroll run"
                onClick={() => navigate(`/workspaces/${workspaceId}/payroll/new`)}
                disabled={status.status !== 'LIVE'}
              />
              <ActionTile
                label="Payroll Runs"
                desc="History and results"
                onClick={() => navigate(`/workspaces/${workspaceId}/payroll`)}
              />
            </div>
          </Card>

        </div>
      )}
    </div>
  );
}
