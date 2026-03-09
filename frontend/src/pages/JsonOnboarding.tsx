import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { workspaceApi } from '../api/workspace';
import { onboardingApi } from '../api/onboarding';
import type { ValidateResponse, PreviewResponse, CommitResponse } from '../types/onboarding';
import type { Workspace } from '../types/workspace';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Btn } from '../components/ui/Btn';
import { AlertBox } from '../components/ui/AlertBox';

type Step = 'create-workspace' | 'load-json';
type LoadStage = 'idle' | 'validated' | 'previewed' | 'committed';

const COUNTRIES = [
  { code: 'NG', label: 'Nigeria' },
  { code: 'GH', label: 'Ghana' },
  { code: 'KE', label: 'Kenya' },
  { code: 'ZA', label: 'South Africa' },
  { code: 'UG', label: 'Uganda' },
];

const CURRENCIES: Record<string, string> = {
  NG: 'NGN',
  GH: 'GHS',
  KE: 'KES',
  ZA: 'ZAR',
  UG: 'UGX',
};

export function JsonOnboarding() {
  const navigate = useNavigate();

  // ── Step tracking ────────────────────────────────────────────────────────
  const [step, setStep] = useState<Step>('create-workspace');

  // ── Step 1: workspace creation ───────────────────────────────────────────
  const [wsName, setWsName] = useState('');
  const [wsCountry, setWsCountry] = useState('NG');
  const [wsCreating, setWsCreating] = useState(false);
  const [wsError, setWsError] = useState<string | null>(null);
  const [workspace, setWorkspace] = useState<Workspace | null>(null);

  // ── Step 2: JSON load ────────────────────────────────────────────────────
  const [rawJson, setRawJson] = useState('');
  const [parsed, setParsed] = useState<Record<string, unknown> | null>(null);
  const [parseError, setParseError] = useState<string | null>(null);
  const [loadStage, setLoadStage] = useState<LoadStage>('idle');
  const [loading, setLoading] = useState(false);
  const [validateResult, setValidateResult] = useState<ValidateResponse | null>(null);
  const [previewResult, setPreviewResult] = useState<PreviewResponse | null>(null);
  const [commitResult, setCommitResult] = useState<CommitResponse | null>(null);

  // ── Workspace creation ───────────────────────────────────────────────────
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
      setWorkspace(created);
      // Inject workspace_id into a starter JSON template
      const template = {
        workspace_id: created.workspace_id,
        employees: [],
        salary_definitions: [],
        payroll_rules: [],
      };
      const formatted = JSON.stringify(template, null, 2);
      setRawJson(formatted);
      setParsed(template);
      setStep('load-json');
    } catch (e: unknown) {
      setWsError(e instanceof Error ? e.message : 'Failed to create workspace');
    } finally {
      setWsCreating(false);
    }
  }

  // ── JSON handling ────────────────────────────────────────────────────────
  function handleJsonChange(text: string) {
    setRawJson(text);
    setParseError(null);
    setValidateResult(null);
    setPreviewResult(null);
    setCommitResult(null);
    setLoadStage('idle');
    try {
      setParsed(JSON.parse(text));
    } catch {
      setParsed(null);
    }
  }

  function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      const text = ev.target?.result as string;
      // Inject workspace_id if workspace already created
      try {
        const obj = JSON.parse(text);
        if (workspace && !obj.workspace_id) {
          obj.workspace_id = workspace.workspace_id;
        }
        handleJsonChange(JSON.stringify(obj, null, 2));
      } catch {
        handleJsonChange(text);
      }
    };
    reader.readAsText(file);
  }

  async function validate() {
    if (!parsed) { setParseError('Fix JSON syntax before validating.'); return; }
    setLoading(true);
    try {
      const result = await onboardingApi.validate(parsed);
      setValidateResult(result);
      if (result.status === 'valid') setLoadStage('validated');
    } catch (e: unknown) {
      setParseError(e instanceof Error ? e.message : 'Request failed');
    } finally {
      setLoading(false);
    }
  }

  async function preview() {
    if (!parsed) return;
    setLoading(true);
    try {
      const result = await onboardingApi.preview(parsed);
      setPreviewResult(result);
      if (result.status === 'valid') setLoadStage('previewed');
    } catch (e: unknown) {
      setParseError(e instanceof Error ? e.message : 'Request failed');
    } finally {
      setLoading(false);
    }
  }

  async function commit() {
    if (!parsed) return;
    setLoading(true);
    try {
      const result = await onboardingApi.commit(parsed);
      setCommitResult(result);
      if (result.status === 'success') setLoadStage('committed');
    } catch (e: unknown) {
      setParseError(e instanceof Error ? e.message : 'Request failed');
    } finally {
      setLoading(false);
    }
  }

  const employees = parsed ? (parsed.employees as unknown[] ?? []) : [];
  const salaryDefs = parsed ? (parsed.salary_definitions as unknown[] ?? []) : [];
  const payrollRules = parsed ? (parsed.payroll_rules as unknown[] ?? []) : [];

  const aiWarnings: string[] = previewResult?.warnings
    ? previewResult.warnings.map((w) => (typeof w === 'string' ? w : String(w)))
    : [];

  // ── Step indicator ───────────────────────────────────────────────────────
  const steps = [
    { id: 'create-workspace', label: '1. Create Workspace' },
    { id: 'load-json', label: '2. Load Client Data' },
  ] as const;

  return (
    <div>
      <PageHeader
        title="New Client Onboarding"
        subtitle="Create a workspace, then load client configuration"
      />

      {/* Step indicator */}
      <div className="flex items-center gap-3 mb-6">
        {steps.map((s, i) => {
          const active = s.id === step;
          const done = step === 'load-json' && s.id === 'create-workspace';
          return (
            <div key={s.id} className="flex items-center gap-2">
              {i > 0 && <span className="text-slate-300 text-sm">→</span>}
              <span
                className={`px-3 py-1 rounded text-xs font-semibold ${
                  done
                    ? 'bg-green-100 text-green-700'
                    : active
                    ? 'bg-slate-800 text-white'
                    : 'bg-slate-100 text-slate-400'
                }`}
              >
                {done ? '✓ ' : ''}{s.label}
              </span>
            </div>
          );
        })}
      </div>

      {/* ── STEP 1: Create Workspace ─────────────────────────────────────── */}
      {step === 'create-workspace' && (
        <div className="max-w-md">
          <Card title="Create Workspace">
            <p className="text-sm text-slate-500 mb-4">
              A workspace must exist before any client data can be loaded. This
              creates an empty workspace in <strong>DRAFT</strong> status.
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
                    <option key={c.code} value={c.code}>
                      {c.label}
                    </option>
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
                <Btn
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate('/')}
                >
                  Cancel
                </Btn>
              </div>
            </form>
          </Card>
        </div>
      )}

      {/* ── STEP 2: Load JSON ────────────────────────────────────────────── */}
      {step === 'load-json' && workspace && (
        <>
          {/* Workspace badge */}
          <div className="mb-5 flex items-center gap-3 px-4 py-3 bg-green-50 border border-green-200 rounded-lg text-sm">
            <svg className="w-4 h-4 text-green-600 shrink-0" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <div>
              <span className="font-semibold text-green-800">{workspace.name}</span>
              <span className="text-green-600 ml-2">
                · {workspace.country_code} · {(workspace as unknown as Record<string, unknown>).base_currency as string}
              </span>
              <span className="ml-3 font-mono text-xs text-green-600 bg-green-100 px-2 py-0.5 rounded">
                {workspace.workspace_id}
              </span>
            </div>
            <button
              className="ml-auto text-xs text-green-600 underline"
              onClick={() => navigate(`/workspaces/${workspace.workspace_id}`)}
            >
              View workspace →
            </button>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
            {/* Left: JSON input */}
            <div className="flex flex-col gap-4">
              <Card title="Client JSON Payload">
                <p className="text-xs text-slate-500 mb-3">
                  The <code className="bg-slate-100 px-1 rounded">workspace_id</code> has been
                  pre-filled. Upload or paste the client's employee and payroll configuration.
                </p>
                <input
                  type="file"
                  accept=".json,application/json"
                  onChange={handleFileUpload}
                  className="block w-full text-sm text-slate-600 mb-3 file:mr-3 file:py-1 file:px-3 file:rounded file:border file:border-slate-300 file:text-xs file:bg-white file:text-slate-700 hover:file:bg-slate-50"
                />
                <textarea
                  className="w-full h-72 font-mono text-xs border border-slate-200 rounded p-3 resize-none focus:outline-none focus:ring-1 focus:ring-slate-400 bg-slate-50"
                  value={rawJson}
                  onChange={(e) => handleJsonChange(e.target.value)}
                />
                {parseError && (
                  <p className="text-red-600 text-xs mt-1">{parseError}</p>
                )}

                <div className="flex gap-2 mt-3 flex-wrap">
                  <Btn
                    onClick={validate}
                    loading={loading && loadStage === 'idle'}
                    disabled={!rawJson || !parsed}
                  >
                    Validate JSON
                  </Btn>
                  <Btn
                    variant="secondary"
                    onClick={preview}
                    loading={loading && loadStage === 'validated'}
                    disabled={loadStage === 'idle' || validateResult?.status !== 'valid'}
                  >
                    Preview Setup
                  </Btn>
                  {loadStage === 'previewed' && previewResult?.status === 'valid' && (
                    <Btn
                      onClick={commit}
                      loading={loading}
                      className="bg-green-700 hover:bg-green-600 text-white"
                    >
                      Commit Setup
                    </Btn>
                  )}
                </div>
              </Card>

              {validateResult && (
                <Card title="Validation Result">
                  {validateResult.status === 'valid' ? (
                    <AlertBox type="success" messages={['Payload is structurally valid.']} />
                  ) : (
                    <AlertBox
                      type="error"
                      title="Validation Failed"
                      messages={validateResult.errors.map((e) => `${e.field}: ${e.message}`)}
                    />
                  )}
                  {validateResult.warnings?.length > 0 && (
                    <div className="mt-2">
                      <AlertBox
                        type="warning"
                        title="Warnings (non-blocking)"
                        messages={validateResult.warnings.map((w) =>
                          typeof w === 'object'
                            ? `${(w as { field: string }).field}: ${(w as { message: string }).message}`
                            : String(w)
                        )}
                      />
                    </div>
                  )}
                </Card>
              )}

              {previewResult && (
                <Card title="Hard Validation + AI Review">
                  {aiWarnings.length > 0 && (
                    <AlertBox
                      type="warning"
                      title="AI Critic Warnings (non-blocking)"
                      messages={aiWarnings}
                    />
                  )}
                  {previewResult.status === 'invalid' && previewResult.errors && (
                    <div className="mt-2">
                      <AlertBox
                        type="error"
                        title="Hard Validation Failed"
                        messages={previewResult.errors.map((e) => `${e.field}: ${e.message}`)}
                      />
                    </div>
                  )}
                  {previewResult.status === 'valid' && (
                    <p className="text-sm text-green-700 font-medium mt-2">
                      Hard validation passed. Ready to commit.
                    </p>
                  )}
                </Card>
              )}

              {commitResult && (
                <Card title="Commit Result">
                  {commitResult.status === 'success' ? (
                    <>
                      <AlertBox
                        type="success"
                        messages={[commitResult.message ?? 'Onboarding committed successfully.']}
                      />
                      <div className="mt-3">
                        <Btn
                          variant="secondary"
                          onClick={() => navigate(`/workspaces/${workspace.workspace_id}`)}
                        >
                          Open Workspace →
                        </Btn>
                      </div>
                    </>
                  ) : (
                    <AlertBox
                      type="error"
                      title="Commit Failed"
                      messages={
                        commitResult.errors
                          ? commitResult.errors.map((e) => `${e.field}: ${e.message}`)
                          : [commitResult.message ?? 'Unknown error']
                      }
                    />
                  )}
                </Card>
              )}
            </div>

            {/* Right: payload summary */}
            <div className="flex flex-col gap-4">
              <Card title="Payload Summary">
                {!parsed ? (
                  <p className="text-sm text-slate-400">Paste or upload JSON to see a summary.</p>
                ) : (
                  <div className="space-y-3 text-sm">
                    <Row label="Workspace ID" value={workspace.workspace_id} />
                    <Row label="Employees" value={String(employees.length)} />
                    <Row label="Salary Definitions" value={String(salaryDefs.length)} />
                    <Row label="Payroll Rules" value={String(payrollRules.length)} />
                  </div>
                )}
              </Card>

              {parsed && employees.length > 0 && (
                <Card title={`Employees (${employees.length})`}>
                  <div className="overflow-auto max-h-52">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="border-b border-slate-100">
                          <Th>#</Th>
                          <Th>Number</Th>
                          <Th>Name</Th>
                          <Th>Salary Def</Th>
                        </tr>
                      </thead>
                      <tbody>
                        {(employees as Array<Record<string, unknown>>).map((emp, i) => {
                          const biodata = emp.biodata as Record<string, unknown> | undefined;
                          const name = emp.full_name ?? biodata?.FULL_NAME ?? emp.employee_number ?? '—';
                          return (
                            <tr key={i} className="border-b border-slate-50">
                              <Td>{i + 1}</Td>
                              <Td>{String(emp.employee_number ?? '—')}</Td>
                              <Td>{String(name)}</Td>
                              <Td>{String(emp.salary_definition_name ?? '—')}</Td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </Card>
              )}

              {parsed && salaryDefs.length > 0 && (
                <Card title={`Salary Definitions (${salaryDefs.length})`}>
                  <ul className="text-xs space-y-1">
                    {(salaryDefs as Array<Record<string, unknown>>).map((sd, i) => (
                      <li key={i} className="flex items-center gap-2 text-slate-600">
                        <span className="w-1.5 h-1.5 rounded-full bg-slate-400 shrink-0" />
                        {String(sd.name ?? '—')}
                      </li>
                    ))}
                  </ul>
                </Card>
              )}

              {parsed && payrollRules.length > 0 && (
                <Card title={`Payroll Rules (${payrollRules.length})`}>
                  <ul className="text-xs space-y-1">
                    {(payrollRules as Array<Record<string, unknown>>).map((rule, i) => (
                      <li key={i} className="flex items-center gap-2 text-slate-600">
                        <span className="w-1.5 h-1.5 rounded-full bg-slate-400 shrink-0" />
                        {String(rule.rule_code ?? rule.rule_name ?? '—')}
                      </li>
                    ))}
                  </ul>
                </Card>
              )}

              {previewResult?.preview && (
                <Card title="Generated SQL Preview">
                  <div className="space-y-3">
                    {previewResult.preview.employees_sql && (
                      <SqlBlock label="Employees" sql={previewResult.preview.employees_sql} />
                    )}
                    {previewResult.preview.salary_definitions_sql && (
                      <SqlBlock label="Salary Definitions" sql={previewResult.preview.salary_definitions_sql} />
                    )}
                    {previewResult.preview.payroll_rules_sql && (
                      <SqlBlock label="Payroll Rules" sql={previewResult.preview.payroll_rules_sql} />
                    )}
                  </div>
                </Card>
              )}
            </div>
          </div>
        </>
      )}
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

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between">
      <span className="text-slate-500">{label}</span>
      <span className="font-mono text-slate-700 text-xs truncate max-w-xs">{value}</span>
    </div>
  );
}

function SqlBlock({ label, sql }: { label: string; sql: string }) {
  return (
    <div>
      <p className="text-xs font-semibold text-slate-500 mb-1">{label}</p>
      <pre className="bg-slate-900 text-green-400 text-xs rounded p-3 overflow-auto max-h-32 whitespace-pre-wrap">
        {sql}
      </pre>
    </div>
  );
}

function Th({ children }: { children: React.ReactNode }) {
  return (
    <th className="text-left font-semibold text-slate-500 py-1.5 px-2 uppercase tracking-wide text-xs">
      {children}
    </th>
  );
}

function Td({ children }: { children: React.ReactNode }) {
  return <td className="py-1.5 px-2 text-slate-600">{children}</td>;
}
