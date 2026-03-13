import { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { workspaceApi } from '../api/workspace';
import { onboardingApi } from '../api/onboarding';
import type { ValidateResponse, PreviewResponse, CommitResponse } from '../types/onboarding';
import type { Workspace } from '../types/workspace';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Btn } from '../components/ui/Btn';
import { AlertBox } from '../components/ui/AlertBox';
import { EmployeeUpload } from '../components/onboarding/EmployeeUpload';
import type { MappedEmployee, SalaryDefinitionOption } from '../components/onboarding/EmployeeUpload';
import { saveDraft, loadDraft, clearDraft } from '../utils/onboardingDraft';
import type { OnboardingDraftStep } from '../utils/onboardingDraft';

// ── Types ──────────────────────────────────────────────────────────────────────

type CommitStage = 'idle' | 'validated' | 'previewed' | 'committed';

// ── Helpers (shared logic, same as JsonOnboarding) ────────────────────────────

function buildConfigTemplate(workspaceId: string): Record<string, unknown> {
  return {
    workspace_id: workspaceId,
    structure: { pay_cycle: {}, grades: [], designations: [] },
    compensation: { salary_definitions: [] },
    rules: { payroll_rules: [] },
    components: { component_metadata: [] },
  };
}

function employeesToCommitShape(employees: MappedEmployee[]) {
  return employees.map((emp) => ({
    employee_number: emp.employee_id,
    employee_id: emp.employee_id,
    full_name: `${emp.first_name} ${emp.last_name}`.trim(),
    grade: emp.grade,
    designation: emp.designation,
    salary_definition_code: emp.salary_definition_code,
    biodata: {
      FULL_NAME: `${emp.first_name} ${emp.last_name}`.trim(),
      TIN: emp.tin,
      RSA: emp.rsa,
      BANK: emp.bank,
      ACCOUNT_NUMBER: emp.account_number,
    },
  }));
}

function extractConfigSalaryDefs(
  configParsed: Record<string, unknown> | null,
): SalaryDefinitionOption[] {
  const compensation = configParsed?.compensation as Record<string, unknown> | undefined;
  const defs = compensation?.salary_definitions;
  if (!Array.isArray(defs)) return [];
  return defs
    .filter((d): d is Record<string, unknown> => typeof d === 'object' && d !== null)
    .map((d, i) => ({
      salary_definition_id: String(i),
      code: String(d.code ?? (d.name as string ?? '').toUpperCase().replace(/ /g, '_')),
      name: String(d.name ?? ''),
    }));
}

// ── Component ──────────────────────────────────────────────────────────────────

export function WorkspaceSetup() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const navigate = useNavigate();

  // ── Workspace (fetched from DB) ───────────────────────────────────────────
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [fetchError, setFetchError] = useState<string | null>(null);

  // ── Step ──────────────────────────────────────────────────────────────────
  const [step, setStep] = useState<OnboardingDraftStep>('client-config-json');

  // ── Step 2 ────────────────────────────────────────────────────────────────
  const [rawJson, setRawJson] = useState('');
  const [configParsed, setConfigParsed] = useState<Record<string, unknown> | null>(null);
  const [jsonParseError, setJsonParseError] = useState<string | null>(null);

  // ── Step 3 ────────────────────────────────────────────────────────────────
  const [employees, setEmployees] = useState<MappedEmployee[]>([]);
  const [dbSalaryDefs, setDbSalaryDefs] = useState<SalaryDefinitionOption[]>([]);

  // ── Commit ────────────────────────────────────────────────────────────────
  const [commitStage, setCommitStage] = useState<CommitStage>('idle');
  const [loading, setLoading] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [validateResult, setValidateResult] = useState<ValidateResponse | null>(null);
  const [previewResult, setPreviewResult] = useState<PreviewResponse | null>(null);
  const [commitResult, setCommitResult] = useState<CommitResponse | null>(null);

  // ── UI ────────────────────────────────────────────────────────────────────
  const [sqlOpen, setSqlOpen] = useState(false);
  const [detailsOpen, setDetailsOpen] = useState(false);

  // Debounce timer for rawJson draft saves
  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // ── Initialisation: fetch workspace + hydrate from draft ──────────────────

  useEffect(() => {
    if (!workspaceId) return;

    // Hydrate from localStorage immediately (before network) so the editor
    // is populated as fast as possible.
    const draft = loadDraft(workspaceId);
    if (draft) {
      setStep(draft.activeStep);
      setRawJson(draft.rawJson);
      try { setConfigParsed(JSON.parse(draft.rawJson)); } catch { setConfigParsed(null); }
      setEmployees(draft.employees);
    }

    // Fetch workspace from DB
    workspaceApi.list().then((all) => {
      const found = all.find((w) => w.workspace_id === workspaceId) ?? null;
      if (!found) {
        setFetchError('Workspace not found. It may have been deleted.');
        return;
      }
      // If the workspace is no longer DRAFT (committed elsewhere), clear stale
      // draft and redirect to the workspace dashboard.
      if (found.status !== 'DRAFT') {
        clearDraft(workspaceId);
        navigate(`/workspaces/${workspaceId}`, { replace: true });
        return;
      }
      setWorkspace(found);
      // If no draft existed, seed the template so the editor isn't empty
      if (!draft) {
        const template = buildConfigTemplate(workspaceId);
        const formatted = JSON.stringify(template, null, 2);
        setRawJson(formatted);
        setConfigParsed(template);
        saveDraft(workspaceId, {
          version: 1,
          workspaceId,
          savedAt: new Date().toISOString(),
          activeStep: 'client-config-json',
          rawJson: formatted,
          employees: [],
        });
      }
    }).catch((e: unknown) => {
      setFetchError(e instanceof Error ? e.message : 'Failed to load workspace.');
    });
  }, [workspaceId]); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Fetch DB salary defs when entering Step 3 ─────────────────────────────

  useEffect(() => {
    if (step === 'employee-upload' && workspaceId) {
      workspaceApi
        .getSalaryDefinitions(workspaceId)
        .then(setDbSalaryDefs)
        .catch(() => { /* non-fatal — config JSON defs are the fallback */ });
    }
  }, [step, workspaceId]);

  // ── Derived ───────────────────────────────────────────────────────────────

  const configSalaryDefs = extractConfigSalaryDefs(configParsed);
  const allSalaryDefs: SalaryDefinitionOption[] = [
    ...dbSalaryDefs,
    ...configSalaryDefs.filter((c) => !dbSalaryDefs.some((d) => d.code === c.code)),
  ];

  const structure = configParsed?.structure as Record<string, unknown> | undefined;
  const compensation = configParsed?.compensation as Record<string, unknown> | undefined;
  const rules = configParsed?.rules as Record<string, unknown> | undefined;
  const components = configParsed?.components as Record<string, unknown> | undefined;

  const gradeCount = Array.isArray(structure?.grades) ? (structure.grades as unknown[]).length : 0;
  const designationCount = Array.isArray(structure?.designations) ? (structure.designations as unknown[]).length : 0;
  const salaryDefCount = Array.isArray(compensation?.salary_definitions) ? (compensation.salary_definitions as unknown[]).length : 0;
  const payrollRuleCount = Array.isArray(rules?.payroll_rules) ? (rules.payroll_rules as unknown[]).length : 0;
  const componentMetaCount = Array.isArray(components?.component_metadata) ? (components.component_metadata as unknown[]).length : 0;
  const payCycleSet = structure?.pay_cycle != null && Object.keys(structure.pay_cycle as object).length > 0;
  const unresolvedMappings = employees.filter((e) => e.mapping_unresolved).length;
  const aiWarnings: string[] = previewResult?.warnings
    ? previewResult.warnings.map((w) => (typeof w === 'string' ? w : String(w)))
    : [];

  // ── Helpers ───────────────────────────────────────────────────────────────

  function buildFinalPayload(): Record<string, unknown> | null {
    if (!configParsed || !workspace) return null;
    const comp = configParsed.compensation as Record<string, unknown> | undefined;
    const r = configParsed.rules as Record<string, unknown> | undefined;
    return {
      workspace_id: workspace.workspace_id,
      // Flat fields consumed by the existing validation + SQL pipeline
      salary_definitions: (comp?.salary_definitions as unknown[]) ?? [],
      payroll_rules: (r?.payroll_rules as unknown[]) ?? [],
      employees: employeesToCommitShape(employees),
      // Structural data — processed by the commit route to populate
      // pay_cycle, grade, designation tables and advance the state machine
      structure: configParsed.structure ?? {},
      components: configParsed.components ?? {},
    };
  }

  function resetCommitState() {
    setCommitStage('idle');
    setActionError(null);
    setValidateResult(null);
    setPreviewResult(null);
    setCommitResult(null);
  }

  // ── Step 2 handlers ───────────────────────────────────────────────────────

  function handleJsonChange(text: string) {
    setRawJson(text);
    setJsonParseError(null);
    try { setConfigParsed(JSON.parse(text)); } catch { setConfigParsed(null); }

    // Debounced draft save — avoids thrashing localStorage on every keystroke
    if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    saveTimerRef.current = setTimeout(() => {
      if (workspaceId) saveDraft(workspaceId, { rawJson: text });
    }, 500);
  }

  function handleJsonFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      const text = ev.target?.result as string;
      try {
        const obj = JSON.parse(text);
        if (workspace && !obj.workspace_id) obj.workspace_id = workspace.workspace_id;
        handleJsonChange(JSON.stringify(obj, null, 2));
      } catch {
        handleJsonChange(text);
      }
    };
    reader.readAsText(file);
    e.target.value = '';
  }

  function handleConfirmConfig() {
    if (!configParsed) { setJsonParseError('Fix JSON syntax errors before continuing.'); return; }
    setStep('employee-upload');
    if (workspaceId) saveDraft(workspaceId, { activeStep: 'employee-upload' });
  }

  // ── Step 3 handlers ───────────────────────────────────────────────────────

  function handleEmployeesLoaded(rows: MappedEmployee[]) {
    setEmployees(rows);
    resetCommitState();
    if (workspaceId) saveDraft(workspaceId, { employees: rows });
  }

  function handleMappingChange(updated: MappedEmployee[]) {
    setEmployees(updated);
    resetCommitState();
    if (workspaceId) saveDraft(workspaceId, { employees: updated });
  }

  // ── Commit handlers ───────────────────────────────────────────────────────

  async function validate() {
    const payload = buildFinalPayload();
    if (!payload) { setActionError('No configuration loaded.'); return; }
    setLoading(true);
    setActionError(null);
    try {
      const result = await onboardingApi.validate(payload);
      setValidateResult(result);
      if (result.status === 'valid') setCommitStage('validated');
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : 'Validation request failed');
    } finally { setLoading(false); }
  }

  async function preview() {
    const payload = buildFinalPayload();
    if (!payload) return;
    setLoading(true);
    setActionError(null);
    try {
      const result = await onboardingApi.preview(payload);
      setPreviewResult(result);
      if (result.status === 'valid') setCommitStage('previewed');
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : 'Preview request failed');
    } finally { setLoading(false); }
  }

  async function commit() {
    const payload = buildFinalPayload();
    if (!payload) return;
    setLoading(true);
    setActionError(null);
    try {
      const result = await onboardingApi.commit(payload);
      setCommitResult(result);
      if (result.status === 'success') {
        setCommitStage('committed');
        if (workspaceId) clearDraft(workspaceId);
      }
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : 'Commit request failed');
    } finally { setLoading(false); }
  }

  // ── Early render: loading / error states ──────────────────────────────────

  if (fetchError) {
    return (
      <div className="max-w-md mt-10">
        <AlertBox type="error" messages={[fetchError]} />
        <div className="mt-4">
          <Btn variant="secondary" onClick={() => navigate('/')}>← Back to Dashboard</Btn>
        </div>
      </div>
    );
  }

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div>
      <PageHeader
        title="Client Setup"
        subtitle={workspace ? `${workspace.name} · Configure client · Upload employees · Commit` : 'Loading…'}
      />

      {/* ── Progress bar ──────────────────────────────────────────────────── */}
      <div className="flex items-center gap-0 mb-6 flex-wrap">
        {/* Step 1 always done */}
        <span className="px-3 py-1 rounded text-xs font-semibold whitespace-nowrap bg-green-100 text-green-700">
          ✓ 1. Create Workspace
        </span>

        {(['client-config-json', 'employee-upload'] as OnboardingDraftStep[]).map((s, i) => {
          const label = s === 'client-config-json' ? 'Configure Client' : 'Upload Employees';
          const done = (i === 0 && step === 'employee-upload') || commitStage === 'committed';
          const active = s === step;
          return (
            <div key={s} className="flex items-center">
              <span className={`text-sm px-1 ${done ? 'text-green-400' : 'text-slate-300'}`}>→</span>
              <span className={`px-3 py-1 rounded text-xs font-semibold whitespace-nowrap ${
                done && !active ? 'bg-green-100 text-green-700'
                : active ? 'bg-slate-800 text-white'
                : 'bg-slate-100 text-slate-400'
              }`}>
                {done && !active ? '✓ ' : `${i + 2}. `}{label}
              </span>
            </div>
          );
        })}

        <div className="flex items-center">
          <span className={`text-sm px-1 ${commitStage === 'committed' ? 'text-green-400' : 'text-slate-300'}`}>→</span>
          <span className={`px-3 py-1 rounded text-xs font-semibold whitespace-nowrap ${
            commitStage === 'committed' ? 'bg-green-100 text-green-700'
            : step === 'employee-upload' ? 'bg-slate-100 text-slate-500'
            : 'bg-slate-100 text-slate-300'
          }`}>
            {commitStage === 'committed' ? '✓ ' : '4. '}Commit
          </span>
        </div>
      </div>

      {/* ── Workspace badge ───────────────────────────────────────────────── */}
      {workspace && (
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
      )}

      {/* ══════════════════════════════════════════════════════════════════════
          STEP 2 — Client Configuration JSON
      ══════════════════════════════════════════════════════════════════════ */}
      {step === 'client-config-json' && (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
          <div className="flex flex-col gap-4">
            <Card title="Client Setup JSON">
              <p className="text-xs text-slate-500 mb-1">
                Define pay cycle, grades, designations, salary definitions (with <code className="bg-slate-100 px-1 rounded">code</code>),
                payroll rules and component metadata.
              </p>
              <p className="text-xs text-amber-600 mb-3">
                Salary definition codes should match <strong>DESIGNATION_GRADE</strong> (e.g. <code className="bg-slate-100 px-1 rounded">ENGINEER_G5</code>).
                Employees are uploaded separately in the next step.
              </p>
              <input
                type="file"
                accept=".json,application/json"
                onChange={handleJsonFileUpload}
                className="block w-full text-sm text-slate-600 mb-3 file:mr-3 file:py-1 file:px-3 file:rounded file:border file:border-slate-300 file:text-xs file:bg-white file:text-slate-700 hover:file:bg-slate-50"
              />
              <textarea
                className="w-full h-96 font-mono text-xs border border-slate-200 rounded p-3 resize-none focus:outline-none focus:ring-1 focus:ring-slate-400 bg-slate-50"
                value={rawJson}
                onChange={(e) => handleJsonChange(e.target.value)}
                spellCheck={false}
              />
              {jsonParseError && <p className="text-red-600 text-xs mt-1">{jsonParseError}</p>}
              {!configParsed && rawJson && (
                <p className="text-amber-600 text-xs mt-1">Invalid JSON — fix syntax errors.</p>
              )}
              <div className="flex gap-2 mt-3">
                <Btn onClick={handleConfirmConfig} disabled={!configParsed}>
                  Confirm Config → Upload Employees
                </Btn>
              </div>
            </Card>
          </div>

          <div className="flex flex-col gap-4">
            <Card title="Configuration Summary">
              {!configParsed ? (
                <p className="text-sm text-slate-400">Paste or upload JSON to see a summary.</p>
              ) : (
                <div className="space-y-2 text-sm">
                  <Row label="Workspace ID" value={workspaceId ?? ''} />
                  <SectionHeader label="Structure" />
                  <Row label="Pay Cycle" value={payCycleSet ? 'Defined' : 'Empty'} />
                  <Row label="Grades" value={String(gradeCount)} />
                  <Row label="Designations" value={String(designationCount)} />
                  {configSalaryDefs.length > 0 && (
                    <div className="pl-2 space-y-0.5">
                      {configSalaryDefs.map((sd) => (
                        <p key={sd.code} className="font-mono text-xs text-slate-500">{sd.code}</p>
                      ))}
                    </div>
                  )}
                  <SectionHeader label="Compensation" />
                  <Row label="Salary Definitions" value={String(salaryDefCount)} />
                  <SectionHeader label="Rules" />
                  <Row label="Payroll Rules" value={String(payrollRuleCount)} />
                  <SectionHeader label="Components" />
                  <Row label="Component Metadata" value={String(componentMetaCount)} />
                  <SectionHeader label="Employees" />
                  <Row label="Employees" value="Upload in next step" />
                </div>
              )}
            </Card>
          </div>
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════════════
          STEP 3 — Employee Upload + Mapping + Commit
      ══════════════════════════════════════════════════════════════════════ */}
      {step === 'employee-upload' && workspace && (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
          {/* Left: upload + commit */}
          <div className="flex flex-col gap-4">
            <EmployeeUpload
              employees={employees}
              salaryDefinitions={allSalaryDefs}
              onEmployeesLoaded={handleEmployeesLoaded}
              onMappingChange={handleMappingChange}
            />

            <Card title="4. Commit Onboarding">
              <p className="text-xs text-slate-500 mb-3">
                Validate and preview before committing. The final payload merges
                the client config JSON with the uploaded employees.
              </p>

              {unresolvedMappings > 0 && (
                <div className="mb-3">
                  <AlertBox
                    type="warning"
                    messages={[`${unresolvedMappings} employee${unresolvedMappings !== 1 ? 's have' : ' has'} an unresolved salary mapping. Resolve above before committing.`]}
                  />
                </div>
              )}

              {actionError && (
                <div className="mb-3">
                  <AlertBox type="error" messages={[actionError]} />
                </div>
              )}

              <div className="flex gap-2 flex-wrap">
                <Btn
                  onClick={validate}
                  loading={loading && commitStage === 'idle'}
                  disabled={!configParsed || employees.length === 0 || unresolvedMappings > 0}
                >
                  Validate
                </Btn>
                <Btn
                  variant="secondary"
                  onClick={preview}
                  loading={loading && commitStage === 'validated'}
                  disabled={validateResult?.status !== 'valid'}
                >
                  Preview SQL
                </Btn>
                {commitStage === 'previewed' && previewResult?.status === 'valid' && (
                  <Btn
                    onClick={commit}
                    loading={loading}
                    className="bg-green-700 hover:bg-green-600 text-white"
                  >
                    Commit Setup
                  </Btn>
                )}
              </div>

              {employees.length === 0 && (
                <p className="text-xs text-amber-600 mt-2">Upload employees above before committing.</p>
              )}

              <button
                className="mt-3 text-xs text-slate-400 underline"
                onClick={() => { setStep('client-config-json'); resetCommitState(); if (workspaceId) saveDraft(workspaceId, { activeStep: 'client-config-json' }); }}
              >
                ← Back to client config
              </button>
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
                  <AlertBox type="warning" title="AI Critic Warnings (non-blocking)" messages={aiWarnings} />
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
                      <Btn variant="secondary" onClick={() => navigate(`/workspaces/${workspace.workspace_id}`)}>
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

          {/* Right: payload summary + SQL preview */}
          <div className="flex flex-col gap-4">
            <Card
              title="Payload Summary"
              action={
                <button
                  className="text-xs text-slate-500 hover:text-slate-800 underline"
                  onClick={() => setDetailsOpen(true)}
                >
                  View details
                </button>
              }
            >
              <div className="space-y-2 text-sm">
                <Row label="Workspace ID" value={workspace.workspace_id} />
                <SectionHeader label="Structure" />
                <Row label="Pay Cycle" value={payCycleSet ? 'Defined' : 'Empty'} />
                <Row label="Grades" value={String(gradeCount)} />
                <Row label="Designations" value={String(designationCount)} />
                <SectionHeader label="Compensation" />
                <Row label="Salary Definitions" value={String(salaryDefCount)} />
                <SectionHeader label="Rules" />
                <Row label="Payroll Rules" value={String(payrollRuleCount)} />
                <SectionHeader label="Components" />
                <Row label="Component Metadata" value={String(componentMetaCount)} />
                <SectionHeader label="Employees" />
                <Row label="Employees" value={employees.length > 0 ? String(employees.length) : 'None uploaded yet'} />
                {unresolvedMappings > 0 && (
                  <p className="text-xs text-amber-600 mt-1">
                    ⚠ {unresolvedMappings} unresolved salary mapping{unresolvedMappings !== 1 ? 's' : ''}
                  </p>
                )}
              </div>
            </Card>

            {previewResult?.preview && (
              <div className="bg-white rounded-lg border border-slate-200 shadow-sm">
                <button
                  className="w-full flex items-center justify-between px-5 py-3 border-b border-slate-100 text-left"
                  onClick={() => setSqlOpen((v) => !v)}
                >
                  <h2 className="text-sm font-semibold text-slate-700">Generated SQL Preview</h2>
                  <span className="text-xs text-slate-400 ml-2">{sqlOpen ? '▲ Hide' : '▼ Show'}</span>
                </button>
                {sqlOpen && (
                  <div className="p-5 space-y-3">
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
                )}
              </div>
            )}
          </div>

          {detailsOpen && (
            <DetailsModal
              workspace={workspace}
              configParsed={configParsed}
              employees={employees}
              onClose={() => setDetailsOpen(false)}
            />
          )}
        </div>
      )}
    </div>
  );
}

// ── Shared micro-components ───────────────────────────────────────────────────

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between">
      <span className="text-slate-500">{label}</span>
      <span className="font-mono text-slate-700 text-xs truncate max-w-[200px]">{value}</span>
    </div>
  );
}

function SectionHeader({ label }: { label: string }) {
  return (
    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide pt-1 border-t border-slate-100 mt-1">
      {label}
    </p>
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
    <th className="text-left font-semibold text-slate-500 py-1.5 px-2 uppercase tracking-wide text-xs whitespace-nowrap">
      {children}
    </th>
  );
}

function Td({ children }: { children: React.ReactNode }) {
  return <td className="py-1.5 px-2 text-slate-600 whitespace-nowrap">{children}</td>;
}

// ── Details Modal ─────────────────────────────────────────────────────────────

function DetailsModal({
  workspace,
  configParsed,
  employees,
  onClose,
}: {
  workspace: Workspace;
  configParsed: Record<string, unknown> | null;
  employees: MappedEmployee[];
  onClose: () => void;
}) {
  const overlayRef = useRef<HTMLDivElement>(null);

  function handleOverlayClick(e: React.MouseEvent) {
    if (e.target === overlayRef.current) onClose();
  }

  const structure = configParsed?.structure as Record<string, unknown> | undefined;
  const compensation = configParsed?.compensation as Record<string, unknown> | undefined;
  const rules = configParsed?.rules as Record<string, unknown> | undefined;

  const grades = (structure?.grades as Record<string, unknown>[]) ?? [];
  const designations = (structure?.designations as Record<string, unknown>[]) ?? [];
  const payCycle = structure?.pay_cycle as Record<string, unknown> | undefined;
  const salaryDefs = (compensation?.salary_definitions as Record<string, unknown>[]) ?? [];
  const payrollRules = (rules?.payroll_rules as Record<string, unknown>[]) ?? [];

  return (
    <div
      ref={overlayRef}
      className="fixed inset-0 z-50 bg-black/40 flex items-start justify-center overflow-y-auto py-10 px-4"
      onClick={handleOverlayClick}
    >
      <div className="bg-white rounded-xl shadow-xl w-full max-w-4xl">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <div>
            <h2 className="text-base font-semibold text-slate-800">Onboarding Details</h2>
            <p className="text-xs text-slate-400 mt-0.5">{workspace.name} · {workspace.workspace_id}</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700 text-lg leading-none px-2">✕</button>
        </div>

        <div className="p-6 space-y-6 text-sm">
          <section>
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Pay Cycle</h3>
            {payCycle && Object.keys(payCycle).length > 0 ? (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {Object.entries(payCycle).map(([k, v]) => (
                  <div key={k} className="bg-slate-50 rounded px-3 py-2">
                    <p className="text-xs text-slate-400 capitalize">{k.replace(/_/g, ' ')}</p>
                    <p className="font-medium text-slate-700 mt-0.5">{String(v)}</p>
                  </div>
                ))}
              </div>
            ) : <p className="text-slate-400 text-xs">Not configured</p>}
          </section>

          <section className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Grades ({grades.length})</h3>
              {grades.length > 0 ? (
                <ul className="space-y-1">
                  {grades.map((g, i) => (
                    <li key={i} className="flex items-center gap-2 bg-slate-50 rounded px-3 py-1.5">
                      <span className="font-mono text-xs font-semibold text-slate-700">
                        {String(g.grade_code ?? g.code ?? g.name ?? `Grade ${i + 1}`)}
                      </span>
                      {g.description && <span className="text-xs text-slate-400">{String(g.description)}</span>}
                    </li>
                  ))}
                </ul>
              ) : <p className="text-slate-400 text-xs">None defined</p>}
            </div>
            <div>
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Designations ({designations.length})</h3>
              {designations.length > 0 ? (
                <ul className="space-y-1">
                  {designations.map((d, i) => (
                    <li key={i} className="flex items-center gap-2 bg-slate-50 rounded px-3 py-1.5">
                      <span className="font-mono text-xs font-semibold text-slate-700">
                        {String(d.designation_code ?? d.code ?? d.name ?? `Designation ${i + 1}`)}
                      </span>
                      {d.description && <span className="text-xs text-slate-400">{String(d.description)}</span>}
                    </li>
                  ))}
                </ul>
              ) : <p className="text-slate-400 text-xs">None defined</p>}
            </div>
          </section>

          <section>
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Salary Definitions ({salaryDefs.length})</h3>
            {salaryDefs.length > 0 ? (
              <div className="space-y-2">
                {salaryDefs.map((sd, i) => {
                  const comps = sd.components as Record<string, unknown> | undefined;
                  return (
                    <div key={i} className="border border-slate-100 rounded-lg px-4 py-3">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="font-mono text-xs font-semibold text-slate-700 bg-slate-100 px-2 py-0.5 rounded">{String(sd.code ?? '')}</span>
                        <span className="text-slate-600">{String(sd.name ?? '')}</span>
                      </div>
                      {comps && (
                        <div className="grid grid-cols-3 sm:grid-cols-5 gap-2">
                          {Object.entries(comps).map(([comp, val]) => {
                            const amount = typeof val === 'object' && val !== null ? (val as Record<string, unknown>).amount : val;
                            return (
                              <div key={comp} className="bg-slate-50 rounded px-2 py-1.5 text-center">
                                <p className="text-xs text-slate-400">{comp}</p>
                                <p className="text-xs font-semibold text-slate-700 mt-0.5">
                                  {typeof amount === 'number' ? amount.toLocaleString() : String(amount ?? '—')}
                                </p>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : <p className="text-slate-400 text-xs">None defined</p>}
          </section>

          <section>
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Payroll Rules ({payrollRules.length})</h3>
            {payrollRules.length > 0 ? (
              <div className="overflow-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-slate-100">
                      <Th>Code</Th><Th>Name</Th><Th>Method</Th><Th>Details</Th>
                    </tr>
                  </thead>
                  <tbody>
                    {payrollRules.map((rule, i) => {
                      const def = rule.definition as Record<string, unknown> | undefined;
                      const method = String(def?.method ?? '—');
                      const details = def
                        ? Object.entries(def).filter(([k]) => k !== 'method').map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`).join(' · ')
                        : '—';
                      return (
                        <tr key={i} className="border-b border-slate-50">
                          <Td><span className="font-mono">{String(rule.rule_code ?? rule.code ?? '—')}</span></Td>
                          <Td>{String(rule.rule_name ?? rule.name ?? '—')}</Td>
                          <Td><span className="bg-slate-100 px-1.5 py-0.5 rounded text-slate-600">{method}</span></Td>
                          <Td><span className="text-slate-400">{details}</span></Td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : <p className="text-slate-400 text-xs">None defined</p>}
          </section>

          <section>
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Employees ({employees.length})</h3>
            {employees.length > 0 ? (
              <div className="overflow-auto max-h-72">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-slate-100">
                      <Th>#</Th><Th>ID</Th><Th>Name</Th><Th>Grade</Th><Th>Designation</Th><Th>Salary Structure</Th><Th>Bank</Th><Th>Account</Th>
                    </tr>
                  </thead>
                  <tbody>
                    {employees.map((emp, i) => (
                      <tr key={emp.employee_id} className={`border-b border-slate-50 ${emp.mapping_unresolved ? 'bg-amber-50' : ''}`}>
                        <Td>{i + 1}</Td>
                        <Td><span className="font-mono">{emp.employee_id}</span></Td>
                        <Td>{emp.first_name} {emp.last_name}</Td>
                        <Td>{emp.grade}</Td>
                        <Td>{emp.designation}</Td>
                        <Td><span className={`font-mono ${emp.mapping_unresolved ? 'text-amber-600' : 'text-green-700'}`}>{emp.salary_definition_code}</span></Td>
                        <Td>{emp.bank}</Td>
                        <Td>{emp.account_number}</Td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : <p className="text-slate-400 text-xs">No employees uploaded yet</p>}
          </section>
        </div>

        <div className="px-6 py-4 border-t border-slate-100 flex justify-end">
          <Btn variant="secondary" onClick={onClose}>Close</Btn>
        </div>
      </div>
    </div>
  );
}
