import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { workspaceApi } from '../api/workspace';
import type { OnboardingStatus } from '../types/workspace';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { ProgressChecklist } from '../components/ui/ProgressChecklist';
import { Btn } from '../components/ui/Btn';
import { AlertBox } from '../components/ui/AlertBox';

export function WorkspaceDashboard() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const navigate = useNavigate();

  const [status, setStatus] = useState<OnboardingStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [transitioning, setTransitioning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [transitionError, setTransitionError] = useState<string | null>(null);
  const [transitionSuccess, setTransitionSuccess] = useState<string | null>(null);

  function load() {
    if (!workspaceId) return;
    setLoading(true);
    setError(null);
    workspaceApi
      .getOnboardingStatus(workspaceId)
      .then(setStatus)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    load();
  }, [workspaceId]);

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

  return (
    <div>
      <PageHeader
        title="Workspace Overview"
        subtitle={workspaceId}
        action={
          <div className="flex gap-2">
            <Btn variant="secondary" size="sm" onClick={() => navigate(`/workspaces/${workspaceId}/employees`)}>
              Employees
            </Btn>
            <Btn size="sm" onClick={() => navigate(`/workspaces/${workspaceId}/payroll`)}>
              Payroll Runs
            </Btn>
          </div>
        }
      />

      {loading && <p className="text-sm text-slate-500">Loading status…</p>}
      {error && <AlertBox type="error" messages={[error]} />}

      {status && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          {/* Status card */}
          <Card title="Current Status" className="lg:col-span-1">
            <div className="flex items-center gap-3 mb-4">
              <StatusBadge status={status.status} />
            </div>
            <ProgressChecklist
              missing={status.missing}
              progressPercent={status.progress_percent}
            />
          </Card>

          {/* State transition */}
          <Card title="State Lifecycle" className="lg:col-span-2">
            <StateFlow currentStatus={status.status} />

            {status.next_allowed_states.length > 0 ? (
              <div className="mt-5">
                <p className="text-xs text-slate-500 mb-2 font-medium">Advance to next state:</p>
                <div className="flex gap-2 flex-wrap">
                  {status.next_allowed_states.map((state) => (
                    <Btn
                      key={state}
                      variant="secondary"
                      size="sm"
                      loading={transitioning}
                      onClick={() => handleTransition(state)}
                    >
                      → {state.replace(/_/g, ' ')}
                    </Btn>
                  ))}
                </div>
              </div>
            ) : (
              <p className="mt-4 text-xs text-slate-400">
                {status.status === 'LIVE'
                  ? 'Workspace is LIVE. No further transitions available.'
                  : 'Complete all required setup steps before advancing.'}
              </p>
            )}

            {transitionError && (
              <div className="mt-3">
                <AlertBox type="error" messages={[transitionError]} />
              </div>
            )}
            {transitionSuccess && (
              <div className="mt-3">
                <AlertBox type="success" messages={[transitionSuccess]} />
              </div>
            )}
          </Card>

          {/* Quick actions */}
          <Card title="Quick Actions" className="lg:col-span-3">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
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

const STATE_SEQUENCE = [
  'DRAFT',
  'STRUCTURE_DEFINED',
  'COMPENSATION_DEFINED',
  'RULES_DEFINED',
  'READY',
  'LIVE',
];

function StateFlow({ currentStatus }: { currentStatus: string }) {
  const currentIdx = STATE_SEQUENCE.indexOf(currentStatus);
  return (
    <div className="flex items-center gap-0 flex-wrap">
      {STATE_SEQUENCE.map((state, i) => {
        const done = i < currentIdx;
        const active = i === currentIdx;
        return (
          <div key={state} className="flex items-center">
            <div
              className={`px-2.5 py-1 rounded text-xs font-semibold whitespace-nowrap ${
                active
                  ? 'bg-slate-800 text-white'
                  : done
                  ? 'bg-green-100 text-green-700'
                  : 'bg-slate-100 text-slate-400'
              }`}
            >
              {state.replace(/_/g, ' ')}
            </div>
            {i < STATE_SEQUENCE.length - 1 && (
              <span className={`text-sm px-1 ${done ? 'text-green-400' : 'text-slate-300'}`}>→</span>
            )}
          </div>
        );
      })}
    </div>
  );
}

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
      className="text-left p-3 rounded border border-slate-200 hover:bg-slate-50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
    >
      <p className="text-sm font-semibold text-slate-700">{label}</p>
      <p className="text-xs text-slate-400 mt-0.5">{desc}</p>
    </button>
  );
}
