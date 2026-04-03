import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { payrollApi } from '../api/payroll';
import { workspaceApi } from '../api/workspace';
import type { PayrollRun } from '../types/payroll';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Btn } from '../components/ui/Btn';
import { AlertBox } from '../components/ui/AlertBox';

export function PayrollRuns() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const navigate = useNavigate();
  const [runs, setRuns] = useState<PayrollRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isLive, setIsLive] = useState(false);

  useEffect(() => {
    if (!workspaceId) return;
    payrollApi
      .getRuns(workspaceId)
      .then(setRuns)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
    workspaceApi
      .getOnboardingStatus(workspaceId)
      .then((s) => setIsLive(s.status === 'LIVE'))
      .catch(() => setIsLive(false));
  }, [workspaceId]);

  return (
    <div>
      <PageHeader
        title="Payroll Runs"
        subtitle={`Workspace ${workspaceId}`}
        action={
          <Btn
            onClick={() => navigate(`/workspaces/${workspaceId}/payroll/new`)}
            disabled={!isLive}
            title={!isLive ? 'Workspace must be LIVE to run payroll' : undefined}
          >
            + New Run
          </Btn>
        }
      />

      {loading && <p className="text-sm text-slate-500">Loading runs…</p>}
      {error && <AlertBox type="error" messages={[error]} />}

      {!loading && !error && (
        <Card>
          {runs.length === 0 ? (
            <p className="text-sm text-slate-400 py-8 text-center">
              No payroll runs yet.{' '}
              {isLive ? (
                <button
                  className="underline text-slate-600"
                  onClick={() => navigate(`/workspaces/${workspaceId}/payroll/new`)}
                >
                  Create the first run.
                </button>
              ) : (
                <span className="text-amber-700">Activate the workspace to run payroll.</span>
              )}
            </p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100">
                  <Th>Run ID</Th>
                  <Th>Period Start</Th>
                  <Th>Period End</Th>
                  <Th>Pay Date</Th>
                  <Th>Status</Th>
                  <Th></Th>
                </tr>
              </thead>
              <tbody>
                {runs.map((run) => (
                  <tr key={run.run_id} className="border-b border-slate-50 hover:bg-slate-50">
                    <Td className="font-mono text-xs">{run.run_id.slice(0, 8)}…</Td>
                    <Td>{run.period_start}</Td>
                    <Td>{run.period_end}</Td>
                    <Td>{run.pay_date}</Td>
                    <Td>
                      <StatusBadge status={run.status} type="payroll" />
                    </Td>
                    <Td>
                      <div className="flex gap-1">
                        <Btn
                          variant="ghost"
                          size="sm"
                          onClick={() =>
                            navigate(`/workspaces/${workspaceId}/payroll/${run.run_id}/results`)
                          }
                        >
                          Results
                        </Btn>
                        <Btn
                          variant="ghost"
                          size="sm"
                          onClick={() =>
                            navigate(
                              `/workspaces/${workspaceId}/payroll/${run.run_id}/reconciliation`
                            )
                          }
                        >
                          Reconcile
                        </Btn>
                      </div>
                    </Td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Card>
      )}
    </div>
  );
}

function Th({ children }: { children?: React.ReactNode }) {
  return (
    <th className="text-left text-xs font-semibold text-slate-500 uppercase tracking-wide py-2 px-3">
      {children}
    </th>
  );
}

function Td({ children, className = '' }: { children?: React.ReactNode; className?: string }) {
  return <td className={`py-3 px-3 text-slate-600 ${className}`}>{children}</td>;
}
