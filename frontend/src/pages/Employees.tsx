import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { workspaceApi } from '../api/workspace';
import type { Employee } from '../types/payroll';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { AlertBox } from '../components/ui/AlertBox';

export function Employees() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!workspaceId) return;
    workspaceApi
      .getEmployees(workspaceId)
      .then(setEmployees)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [workspaceId]);

  return (
    <div>
      <PageHeader
        title="Employees"
        subtitle={`Workspace ${workspaceId}`}
      />

      {loading && <p className="text-sm text-slate-500">Loading employees…</p>}
      {error && <AlertBox type="error" messages={[error]} />}

      {!loading && !error && (
        <Card>
          {employees.length === 0 ? (
            <p className="text-sm text-slate-400 py-8 text-center">
              No employees found for this workspace.
            </p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100">
                  <Th>Name</Th>
                  <Th>Employee #</Th>
                  <Th>Designation</Th>
                  <Th>Grade</Th>
                  <Th>Contract Start</Th>
                  <Th>Status</Th>
                </tr>
              </thead>
              <tbody>
                {employees.map((emp) => (
                  <tr key={emp.employee_id} className="border-b border-slate-50 hover:bg-slate-50">
                    <Td className="font-medium text-slate-800">{emp.full_name}</Td>
                    <Td className="font-mono">{emp.employee_number}</Td>
                    <Td>{emp.designation ?? '—'}</Td>
                    <Td>{emp.grade ?? '—'}</Td>
                    <Td>{emp.contract_start ?? '—'}</Td>
                    <Td>
                      <span
                        className={`inline-flex px-2 py-0.5 rounded text-xs font-semibold uppercase ${
                          emp.status === 'ACTIVE'
                            ? 'bg-green-100 text-green-700'
                            : 'bg-slate-100 text-slate-500'
                        }`}
                      >
                        {emp.status}
                      </span>
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

function Th({ children }: { children: React.ReactNode }) {
  return (
    <th className="text-left text-xs font-semibold text-slate-500 uppercase tracking-wide py-2 px-3">
      {children}
    </th>
  );
}

function Td({ children, className = '' }: { children?: React.ReactNode; className?: string }) {
  return <td className={`py-3 px-3 text-slate-600 ${className}`}>{children}</td>;
}
