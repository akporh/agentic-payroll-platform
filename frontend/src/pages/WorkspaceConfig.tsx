import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../api/client';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { AlertBox } from '../components/ui/AlertBox';
import { WorkspaceExcelUpload, type WorkspaceConfig as WsConfig } from '../components/onboarding/WorkspaceExcelUpload';

interface PayCycle {
  frequency: string;
  run_day: number;
  cutoff_day: number;
  payment_day: number;
}

interface Grade {
  code: string;
  description: string | null;
}

interface Designation {
  code: string;
  description: string | null;
}

interface SalaryComponent {
  component_name: string;
  amount: number;
}

interface SalaryDefinition {
  name: string;
  code: string;
  components: SalaryComponent[];
}

interface PayrollRule {
  name: string;
  rule_type: string;
  method: string;
}

interface ComponentOverride {
  component_name: string;
  is_active: boolean;
}

interface WorkspaceConfiguration {
  workspace: {
    name: string;
    country_code: string;
    currency_code: string;
    status: string;
  };
  pay_cycle: PayCycle | null;
  grades: Grade[];
  designations: Designation[];
  salary_definitions: SalaryDefinition[];
  payroll_rules: PayrollRule[];
  component_overrides: ComponentOverride[];
}

export function WorkspaceConfig() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const [config, setConfig] = useState<WorkspaceConfiguration | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reuploadMsg, setReuploadMsg] = useState<string | null>(null);
  const [reuploadError, setReuploadError] = useState<string | null>(null);
  const [reuploading, setReuploading] = useState(false);

  useEffect(() => {
    if (!workspaceId) return;
    setLoading(true);
    setError(null);
    api
      .get<WorkspaceConfiguration>(`/${workspaceId}/configuration`)
      .then(setConfig)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [workspaceId]);

  async function handleConfigParsed(parsedConfig: WsConfig) {
    if (!workspaceId) return;
    setReuploading(true);
    setReuploadMsg(null);
    setReuploadError(null);
    try {
      const res = await api.post<{ status: string; message: string }>(
        '/onboarding/commit',
        { ...parsedConfig, workspace_id: workspaceId },
      );
      setReuploadMsg(res.message || 'Configuration updated successfully.');
      // Reload current config
      const updated = await api.get<WorkspaceConfiguration>(`/${workspaceId}/configuration`);
      setConfig(updated);
    } catch (e: unknown) {
      setReuploadError(e instanceof Error ? e.message : 'Failed to update configuration.');
    } finally {
      setReuploading(false);
    }
  }

  return (
    <div>
      <PageHeader title="Configuration" subtitle={workspaceId} />

      {loading && <p className="text-sm text-slate-500">Loading configuration...</p>}
      {error && <AlertBox type="error" messages={[error]} />}

      {config && (
        <div className="space-y-5">
          {/* Workspace */}
          <Card title="Workspace">
            <dl className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
              <Dt label="Name" value={config.workspace.name} />
              <Dt label="Country" value={config.workspace.country_code} />
              <Dt label="Currency" value={config.workspace.currency_code} />
              <div>
                <dt className="text-slate-500 text-xs font-medium mb-1">Status</dt>
                <dd><StatusBadge status={config.workspace.status} /></dd>
              </div>
            </dl>
          </Card>

          {/* Pay Cycle */}
          <Card title="Pay Cycle">
            {config.pay_cycle ? (
              <dl className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                <Dt label="Frequency" value={config.pay_cycle.frequency} />
                <Dt label="Run Day" value={String(config.pay_cycle.run_day)} />
                <Dt label="Cutoff Day" value={String(config.pay_cycle.cutoff_day)} />
                <Dt label="Payment Day" value={String(config.pay_cycle.payment_day)} />
              </dl>
            ) : (
              <p className="text-sm text-slate-400">No pay cycle defined.</p>
            )}
          </Card>

          {/* Grades */}
          <Card title="Grades">
            {config.grades.length > 0 ? (
              <Table
                cols={['Code', 'Description']}
                rows={config.grades.map((g) => [g.code, g.description ?? '-'])}
              />
            ) : (
              <p className="text-sm text-slate-400">No grades defined.</p>
            )}
          </Card>

          {/* Designations */}
          <Card title="Designations">
            {config.designations.length > 0 ? (
              <Table
                cols={['Code', 'Description']}
                rows={config.designations.map((d) => [d.code, d.description ?? '-'])}
              />
            ) : (
              <p className="text-sm text-slate-400">No designations defined.</p>
            )}
          </Card>

          {/* Salary Definitions */}
          <Card title="Salary Definitions">
            {config.salary_definitions.length > 0 ? (
              <div className="space-y-3">
                {config.salary_definitions.map((sd) => (
                  <div key={sd.code} className="border border-slate-200 rounded p-3">
                    <p className="text-sm font-semibold text-slate-700">
                      {sd.name} <span className="text-slate-400 font-normal">({sd.code})</span>
                    </p>
                    {sd.components.length > 0 && (
                      <Table
                        cols={['Component', 'Amount']}
                        rows={sd.components.map((c) => [c.component_name, String(c.amount)])}
                      />
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-400">No salary definitions defined.</p>
            )}
          </Card>

          {/* Payroll Rules */}
          <Card title="Payroll Rules">
            {config.payroll_rules.length > 0 ? (
              <Table
                cols={['Name', 'Type', 'Method']}
                rows={config.payroll_rules.map((r) => [r.name, r.rule_type, r.method])}
              />
            ) : (
              <p className="text-sm text-slate-400">No payroll rules defined.</p>
            )}
          </Card>

          {/* Component Overrides */}
          <Card title="Component Overrides">
            {config.component_overrides.length > 0 ? (
              <div className="space-y-2">
                {config.component_overrides.map((co) => (
                  <div
                    key={co.component_name}
                    className="flex items-center justify-between py-1.5 px-2 rounded bg-slate-50 text-sm"
                  >
                    <span className="text-slate-700">{co.component_name}</span>
                    <span
                      className={`text-xs font-semibold px-2 py-0.5 rounded ${
                        co.is_active
                          ? 'bg-green-100 text-green-700'
                          : 'bg-slate-200 text-slate-500'
                      }`}
                    >
                      {co.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-400">No component overrides defined.</p>
            )}
          </Card>

          {/* Re-upload Configuration */}
          <div>
            <h2 className="text-sm font-semibold text-slate-600 mb-2 px-1">
              Update Configuration
            </h2>
            <p className="text-xs text-slate-400 mb-3 px-1">
              Re-upload a workspace config Excel to add salary definitions, update grades,
              or set component overrides. Existing records are updated; nothing is deleted.
            </p>
            {reuploadMsg && <AlertBox type="success" messages={[reuploadMsg]} />}
            {reuploadError && <AlertBox type="error" messages={[reuploadError]} />}
            {reuploading && <p className="text-xs text-slate-500 mb-2">Committing…</p>}
            {workspaceId && (
              <WorkspaceExcelUpload
                workspaceId={workspaceId}
                onConfigParsed={handleConfigParsed}
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function Dt({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-slate-500 text-xs font-medium mb-1">{label}</dt>
      <dd className="text-slate-800 font-medium">{value}</dd>
    </div>
  );
}

function Table({ cols, rows }: { cols: string[]; rows: string[][] }) {
  return (
    <table className="w-full text-sm mt-2">
      <thead>
        <tr>
          {cols.map((c) => (
            <th key={c} className="text-left text-xs text-slate-500 font-medium pb-2 pr-4">
              {c}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, i) => (
          <tr key={i} className="border-t border-slate-100">
            {row.map((cell, j) => (
              <td key={j} className="py-1.5 pr-4 text-slate-700">
                {cell}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
