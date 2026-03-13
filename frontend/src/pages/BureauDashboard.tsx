import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { workspaceApi } from '../api/workspace';
import type { Workspace } from '../types/workspace';
import { PageHeader } from '../components/ui/PageHeader';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Btn } from '../components/ui/Btn';
import { Card } from '../components/ui/Card';

export function BureauDashboard() {
  const navigate = useNavigate();
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    workspaceApi
      .list()
      .then(setWorkspaces)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <PageHeader
        title="Bureau Dashboard"
        subtitle="All workspaces managed by this bureau"
        action={
          <Btn onClick={() => navigate('/onboarding')}>
            + New Client
          </Btn>
        }
      />

      {loading && <p className="text-sm text-slate-500">Loading workspaces…</p>}
      {error && (
        <div className="rounded border border-red-200 bg-red-50 text-red-700 px-4 py-3 text-sm mb-4">
          {error}
        </div>
      )}

      {!loading && (
        <Card>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100">
                <Th>Workspace Name</Th>
                <Th>Country</Th>
                <Th>Currency</Th>
                <Th>Status</Th>
                <Th>Employees</Th>
                <Th></Th>
              </tr>
            </thead>
            <tbody>
              {workspaces.length === 0 && !error ? (
                <tr>
                  <td colSpan={6} className="py-10 text-center text-slate-400 text-sm">
                    No workspaces yet.{' '}
                    <button
                      className="underline text-slate-600"
                      onClick={() => navigate('/onboarding')}
                    >
                      Create the first one.
                    </button>
                  </td>
                </tr>
              ) : (
                workspaces.map((ws) => (
                  <tr key={ws.workspace_id} className="border-b border-slate-50 hover:bg-slate-50">
                    <Td className="font-medium text-slate-800">{ws.name}</Td>
                    <Td>{ws.country_code ?? '—'}</Td>
                    <Td>{(ws as unknown as Record<string, unknown>).base_currency as string ?? '—'}</Td>
                    <Td>
                      <StatusBadge status={ws.status ?? 'DRAFT'} />
                    </Td>
                    <Td>{ws.active_employee_count ?? 0}</Td>
                    <Td>
                      {ws.status === 'DRAFT' ? (
                        <Btn
                          variant="secondary"
                          size="sm"
                          onClick={() => navigate(`/workspaces/${ws.workspace_id}/setup`)}
                        >
                          Continue Setup
                        </Btn>
                      ) : (
                        <Btn
                          variant="secondary"
                          size="sm"
                          onClick={() => navigate(`/workspaces/${ws.workspace_id}`)}
                        >
                          Open
                        </Btn>
                      )}
                    </Td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
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
