import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { workspaceApi } from '../api/workspace';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Btn } from '../components/ui/Btn';
import { AlertBox } from '../components/ui/AlertBox';
import { saveDraft } from '../utils/onboardingDraft';

const COUNTRIES = [
  { code: 'NG', label: 'Nigeria' },
  { code: 'GH', label: 'Ghana' },
  { code: 'KE', label: 'Kenya' },
  { code: 'ZA', label: 'South Africa' },
  { code: 'UG', label: 'Uganda' },
];

const CURRENCIES: Record<string, string> = {
  NG: 'NGN', GH: 'GHS', KE: 'KES', ZA: 'ZAR', UG: 'UGX',
};

function buildConfigTemplate(workspaceId: string): Record<string, unknown> {
  return {
    workspace_id: workspaceId,
    structure: { pay_cycle: {}, grades: [], designations: [] },
    compensation: { salary_definitions: [] },
    rules: { payroll_rules: [] },
    components: { component_metadata: [] },
  };
}

export function JsonOnboarding() {
  const navigate = useNavigate();

  const [wsName, setWsName] = useState('');
  const [wsCountry, setWsCountry] = useState('NG');
  const [wsCreating, setWsCreating] = useState(false);
  const [wsError, setWsError] = useState<string | null>(null);

  async function handleCreateWorkspace(e: React.FormEvent) {
    e.preventDefault();
    setWsCreating(true);
    setWsError(null);
    try {
      const created = await workspaceApi.create({
        name: wsName,
        country_code: wsCountry,
        base_currency: CURRENCIES[wsCountry] ?? 'NGN',
      });
      // Seed localStorage draft so WorkspaceSetup hydrates immediately on arrival
      const template = buildConfigTemplate(created.workspace_id);
      saveDraft(created.workspace_id, {
        version: 1,
        workspaceId: created.workspace_id,
        savedAt: new Date().toISOString(),
        activeStep: 'client-config-json',
        rawJson: JSON.stringify(template, null, 2),
        employees: [],
      });
      navigate(`/workspaces/${created.workspace_id}/setup`);
    } catch (err: unknown) {
      setWsError(err instanceof Error ? err.message : 'Failed to create workspace');
    } finally {
      setWsCreating(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="New Client Onboarding"
        subtitle="Create a workspace to begin client setup"
      />

      {/* Step indicator */}
      <div className="flex items-center gap-0 mb-6">
        <span className="px-3 py-1 rounded text-xs font-semibold bg-slate-800 text-white">
          1. Create Workspace
        </span>
        <span className="text-sm px-1 text-slate-300">→</span>
        <span className="px-3 py-1 rounded text-xs font-semibold bg-slate-100 text-slate-400">
          2. Configure Client
        </span>
        <span className="text-sm px-1 text-slate-300">→</span>
        <span className="px-3 py-1 rounded text-xs font-semibold bg-slate-100 text-slate-400">
          3. Upload Employees
        </span>
        <span className="text-sm px-1 text-slate-300">→</span>
        <span className="px-3 py-1 rounded text-xs font-semibold bg-slate-100 text-slate-300">
          4. Commit
        </span>
      </div>

      <div className="max-w-md">
        <Card title="Create Workspace">
          <p className="text-sm text-slate-500 mb-4">
            A workspace must exist before any client data can be loaded.
            This creates an empty workspace in <strong>DRAFT</strong> status.
          </p>
          <form onSubmit={handleCreateWorkspace} className="space-y-4">
            <Field label="Client / Company Name">
              <input
                type="text"
                required
                placeholder="e.g. Acme Corporation"
                value={wsName}
                onChange={(e) => setWsName(e.target.value)}
                className={inputClass}
              />
            </Field>
            <Field label="Country">
              <select
                value={wsCountry}
                onChange={(e) => setWsCountry(e.target.value)}
                className={inputClass}
              >
                {COUNTRIES.map((c) => (
                  <option key={c.code} value={c.code}>{c.label}</option>
                ))}
              </select>
            </Field>
            <Field label="Base Currency">
              <input
                type="text"
                readOnly
                value={CURRENCIES[wsCountry] ?? 'NGN'}
                className={`${inputClass} bg-slate-50 text-slate-500`}
              />
            </Field>
            {wsError && <AlertBox type="error" messages={[wsError]} />}
            <div className="flex gap-2 pt-1">
              <Btn type="submit" loading={wsCreating} disabled={!wsName.trim()}>
                Create Workspace
              </Btn>
              <Btn type="button" variant="ghost" size="sm" onClick={() => navigate('/')}>
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
  'w-full border border-slate-200 rounded px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-slate-400 bg-white';

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-xs font-medium text-slate-600 mb-1">{label}</label>
      {children}
    </div>
  );
}
