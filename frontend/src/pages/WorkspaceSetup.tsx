import { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { workspaceApi } from '../api/workspace';
import { api } from '../api/client';
import { onboardingApi } from '../api/onboarding';
import type { ValidateResponse, PreviewResponse, CommitResponse } from '../types/onboarding';
import type { Workspace } from '../types/workspace';
import type { WorkspacePayrollConfig, RateCode } from '../types/payroll';
import { ContentHeader, Card, Btn, AlertBanner, OnboardingStepper, Breadcrumb } from '../design-system';
import type { Step } from '../design-system';
import { EmployeeUpload } from '../components/employees/EmployeeUpload';
import type { MappedEmployee, SalaryDefinitionOption } from '../components/employees/EmployeeUpload';
import { WorkspaceExcelUpload } from '../components/onboarding/WorkspaceExcelUpload';
import type { WorkspaceConfig } from '../components/onboarding/WorkspaceExcelUpload';
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
  };
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

  // ── Existing config (non-DRAFT workspaces) ────────────────────────────────
  const [existingConfig, setExistingConfig] = useState<Record<string, unknown> | null>(null);
  const [configLoading, setConfigLoading] = useState(false);

  // ── Step ──────────────────────────────────────────────────────────────────
  const [step, setStep] = useState<OnboardingDraftStep>('client-config-json');

  // ── Step 2 ────────────────────────────────────────────────────────────────
  const [rawJson, setRawJson] = useState('');
  const [configParsed, setConfigParsed] = useState<Record<string, unknown> | null>(null);
  const [jsonParseError, setJsonParseError] = useState<string | null>(null);

  // ── Step 3 — Component Settings ─────────────────────────────────────────
  const [platformComponents, setPlatformComponents] = useState<{ component_code: string; label: string }[]>([]);
  const [_componentOverrides, setComponentOverrides] = useState<Record<string, boolean>>({});
  const [componentToggles, setComponentToggles] = useState<Record<string, boolean>>({});
  const [componentLoading, setComponentLoading] = useState(false);
  const [componentSaving, setComponentSaving] = useState(false);
  const [componentError, setComponentError] = useState<string | null>(null);

  // ── Commit ────────────────────────────────────────────────────────────────
  const [commitStage, setCommitStage] = useState<CommitStage>('idle');
  const [loading, setLoading] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [validateResult, setValidateResult] = useState<ValidateResponse | null>(null);
  const [previewResult, setPreviewResult] = useState<PreviewResponse | null>(null);
  const [commitResult, setCommitResult] = useState<CommitResponse | null>(null);

  // ── UI ────────────────────────────────────────────────────────────────────
  const [advancedJsonOpen, setAdvancedJsonOpen] = useState(false);

  // Debounce timer for rawJson draft saves
  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // ── Initialisation: fetch workspace + hydrate from draft ──────────────────

  useEffect(() => {
    if (!workspaceId) return;

    // Hydrate from localStorage immediately (before network) so the editor
    // is populated as fast as possible.
    const draft = loadDraft(workspaceId);
    if (draft) {
      // Guard: drafts saved with the old 'employee-upload' step fall back to component-settings
      const safeStep = (draft.activeStep as string) === 'employee-upload' ? 'component-settings' : draft.activeStep;
      setStep(safeStep);
      setRawJson(draft.rawJson);
      try { setConfigParsed(JSON.parse(draft.rawJson)); } catch { setConfigParsed(null); }
    }

    // Fetch workspace from DB
    workspaceApi.list().then((all) => {
      const found = all.find((w) => w.workspace_id === workspaceId) ?? null;
      if (!found) {
        setFetchError('Workspace not found. It may have been deleted.');
        return;
      }
      // Non-DRAFT workspace: show existing configuration instead of wizard
      if (found.status !== 'DRAFT') {
        clearDraft(workspaceId);
        setWorkspace(found);
        setConfigLoading(true);
        api.get<Record<string, unknown>>(`/${workspaceId}/configuration`)
          .then(setExistingConfig)
          .finally(() => setConfigLoading(false));
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
        });
      }
    }).catch((e: unknown) => {
      setFetchError(e instanceof Error ? e.message : 'Failed to load workspace.');
    });
  }, [workspaceId]); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Fetch platform components + overrides when entering Step 3 ─────────────

  useEffect(() => {
    if (step !== 'component-settings' || !workspaceId) return;
    setComponentLoading(true);
    setComponentError(null);

    Promise.all([
      api.get<{ component_code: string; label: string }[]>(`/${workspaceId}/platform-components`),
      api.get<{ component_code: string; overrides_json: { is_active?: boolean } }[]>(`/${workspaceId}/component-overrides`),
    ])
      .then(([components, overrides]) => {
        setPlatformComponents(components);
        const overrideMap: Record<string, boolean> = {};
        for (const o of overrides) {
          overrideMap[o.component_code] = o.overrides_json.is_active !== false;
        }
        setComponentOverrides(overrideMap);
        // Initialise toggles: use override if exists, otherwise default to true
        const toggles: Record<string, boolean> = {};
        for (const c of components) {
          toggles[c.component_code] = overrideMap[c.component_code] ?? true;
        }
        setComponentToggles(toggles);
      })
      .catch((e: unknown) => {
        setComponentError(e instanceof Error ? e.message : 'Failed to load components.');
      })
      .finally(() => setComponentLoading(false));
  }, [step, workspaceId]);

  // ── Derived ───────────────────────────────────────────────────────────────

  const configSalaryDefs = extractConfigSalaryDefs(configParsed);

  const structure = configParsed?.structure as Record<string, unknown> | undefined;
  const compensation = configParsed?.compensation as Record<string, unknown> | undefined;
  const rules = configParsed?.rules as Record<string, unknown> | undefined;

  const gradeCount = Array.isArray(structure?.grades) ? (structure.grades as unknown[]).length : 0;
  const designationCount = Array.isArray(structure?.designations) ? (structure.designations as unknown[]).length : 0;
  const salaryDefCount = Array.isArray(compensation?.salary_definitions) ? (compensation.salary_definitions as unknown[]).length : 0;
  const payrollRuleCount = Array.isArray(rules?.payroll_rules) ? (rules.payroll_rules as unknown[]).length : 0;
  const payCycleSet = structure?.pay_cycle != null && Object.keys(structure.pay_cycle as object).length > 0;
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
      employees: [],
      // Structural data — processed by the commit route to populate
      // pay_cycle, grade, designation tables and advance the state machine
      structure: configParsed.structure ?? {},
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

  function handleExcelConfigParsed(config: WorkspaceConfig) {
    const formatted = JSON.stringify(config, null, 2);
    setRawJson(formatted);
    setConfigParsed(config as unknown as Record<string, unknown>);
    setJsonParseError(null);
    if (workspaceId) saveDraft(workspaceId, { rawJson: formatted });
  }

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
    setStep('component-settings');
    if (workspaceId) saveDraft(workspaceId, { activeStep: 'component-settings' });
  }

  // ── Step 3 handlers — Component Settings ────────────────────────────────

  async function handleSaveComponents() {
    if (!workspaceId) return;
    setComponentSaving(true);
    setComponentError(null);
    try {
      for (const comp of platformComponents) {
        await api.post(`/${workspaceId}/component-metadata`, {
          component_code: comp.component_code,
          overrides_json: { is_active: componentToggles[comp.component_code] ?? true },
        });
      }
      setStep('activate');
      saveDraft(workspaceId, { activeStep: 'activate' });
    } catch (e: unknown) {
      setComponentError(e instanceof Error ? e.message : 'Failed to save component settings.');
    } finally {
      setComponentSaving(false);
    }
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
        <AlertBanner variant="error" description={fetchError} />
        <div className="mt-4">
          <Btn variant="secondary" onClick={() => navigate('/')}>← Back to Dashboard</Btn>
        </div>
      </div>
    );
  }

  // ── Existing config view (non-DRAFT workspaces) ──────────────────────────

  if (configLoading) {
    return <p className="text-sm text-slate-500 mt-6">Loading workspace configuration…</p>;
  }

  if (existingConfig) {
    return <ExistingConfigView workspace={workspace} config={existingConfig} />;
  }

  // ── Render (DRAFT wizard) ────────────────────────────────────────────────

  const WIZARD_STEPS: Step[] = [
    { label: 'Create Workspace' },
    { label: 'Configure Client' },
    { label: 'Component Settings' },
    { label: 'Activate' },
  ];
  const wizardCurrentStep =
    commitStage === 'committed' ? 4
    : step === 'activate' ? 3
    : step === 'component-settings' ? 2
    : 1;

  return (
    <div>
      <ContentHeader
        title="Client Setup"
        subtitle={workspace ? `${workspace.name} · Configure client · Activate` : 'Loading…'}
        back={
          <Breadcrumb items={[
            { label: 'Bureau Dashboard', to: '/' },
            { label: workspace?.name ?? '…', to: `/workspaces/${workspaceId}` },
            { label: 'Setup Wizard' },
          ]} />
        }
      />

      {/* ── Progress stepper ──────────────────────────────────────────────── */}
      <OnboardingStepper steps={WIZARD_STEPS} currentStep={wizardCurrentStep} className="mb-6" />

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
            {/* Excel upload */}
            {workspaceId && (
              <WorkspaceExcelUpload
                workspaceId={workspaceId}
                onConfigParsed={handleExcelConfigParsed}
              />
            )}

            {/* Advanced: JSON editor (collapsed by default) */}
            <div className="border border-slate-200 rounded-lg bg-white shadow-sm">
              <button
                className="w-full flex items-center justify-between px-5 py-3 text-left"
                onClick={() => setAdvancedJsonOpen((v) => !v)}
              >
                <span className="text-sm font-semibold text-slate-700">Advanced: Edit JSON directly</span>
                <span className="text-xs text-slate-400 ml-2">{advancedJsonOpen ? '▲ Hide' : '▼ Show'}</span>
              </button>
              {advancedJsonOpen && (
                <div className="px-5 pb-5 border-t border-slate-100">
                  <p className="text-xs text-slate-500 mt-3 mb-1">
                    Define pay cycle, grades, designations, salary definitions (with <code className="bg-slate-100 px-1 rounded">code</code>),
                    payroll rules and component metadata.
                  </p>
                  <p className="text-xs text-amber-600 mb-3">
                    Salary definition codes should match <strong>DESIGNATION_GRADE</strong> (e.g. <code className="bg-slate-100 px-1 rounded">ENGINEER_G5</code>).
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
                </div>
              )}
            </div>

            {/* Confirm button always visible */}
            <div className="flex gap-2">
              <Btn onClick={handleConfirmConfig} disabled={!configParsed}>
                Confirm Config → Component Settings
              </Btn>
            </div>
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
                </div>
              )}
            </Card>
          </div>
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════════════
          STEP 3 — Component Settings
      ══════════════════════════════════════════════════════════════════════ */}
      {step === 'component-settings' && workspace && (
        <div className="max-w-lg">
          <Card title="Component Settings">
            <p className="text-xs text-slate-500 mb-4">
              Toggle which payroll components are active for this workspace.
              Disabled components will be excluded from payroll calculations.
            </p>

            {componentLoading && (
              <p className="text-sm text-slate-400">Loading components...</p>
            )}

            {componentError && (
              <div className="mb-3">
                <AlertBanner variant="error" description={componentError} />
              </div>
            )}

            {!componentLoading && !componentError && platformComponents.length === 0 && (
              <p className="text-sm text-slate-400 mb-4">No platform components found.</p>
            )}

            {!componentLoading && platformComponents.length > 0 && (
              <div className="space-y-2 mb-4">
                {platformComponents.map((comp) => (
                  <label
                    key={comp.component_code}
                    className="flex items-center gap-3 px-3 py-2 rounded border border-slate-100 hover:bg-slate-50 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={componentToggles[comp.component_code] ?? true}
                      onChange={(e) =>
                        setComponentToggles((prev) => ({ ...prev, [comp.component_code]: e.target.checked }))
                      }
                      className="accent-slate-700 w-4 h-4"
                    />
                    <span className="text-sm text-slate-700 font-medium">{comp.label}</span>
                    <span className="text-xs font-mono text-slate-400 ml-auto">{comp.component_code}</span>
                  </label>
                ))}
              </div>
            )}

            <div className="flex gap-2">
              <Btn
                onClick={handleSaveComponents}
                loading={componentSaving}
                disabled={componentLoading || platformComponents.length === 0}
              >
                Save &amp; Continue
              </Btn>
              <button
                className="text-xs text-slate-400 underline px-2"
                onClick={() => { setStep('client-config-json'); if (workspaceId) saveDraft(workspaceId, { activeStep: 'client-config-json' }); }}
              >
                ← Back to client config
              </button>
            </div>
          </Card>
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════════════
          STEP 4 — Activate Workspace
      ══════════════════════════════════════════════════════════════════════ */}
      {step === 'activate' && workspace && (
        <div className="max-w-lg flex flex-col gap-4">
            <Card title="Activate Workspace">
              <p className="text-xs text-slate-500 mb-3">
                Validate the configuration and commit to activate this workspace.
                Employees can be added from the Employees page after activation.
              </p>

              {actionError && (
                <div className="mb-3">
                  <AlertBanner variant="error" description={actionError} />
                </div>
              )}

              <div className="flex gap-2 flex-wrap">
                <Btn
                  onClick={validate}
                  loading={loading && commitStage === 'idle'}
                  disabled={!configParsed}
                >
                  Validate
                </Btn>
                {commitStage === 'validated' && validateResult?.status === 'valid' && (
                  <Btn
                    onClick={commit}
                    loading={loading}
                    className="bg-green-700 hover:bg-green-600 text-white"
                  >
                    Activate Workspace
                  </Btn>
                )}
              </div>

              <button
                className="mt-3 text-xs text-slate-400 underline"
                onClick={() => { setStep('component-settings'); resetCommitState(); if (workspaceId) saveDraft(workspaceId, { activeStep: 'component-settings' }); }}
              >
                ← Back to component settings
              </button>
            </Card>

            {validateResult && (
              <Card title="Validation Result">
                {validateResult.status === 'valid' ? (
                  <AlertBanner variant="success" description="Payload is structurally valid." />
                ) : (
                  <AlertBanner
                    variant="error"
                    title="Validation Failed"
                    description={validateResult.errors.map((e) => `${e.field}: ${e.message}`).join(' · ')}
                  />
                )}
                {validateResult.warnings?.length > 0 && (
                  <div className="mt-2">
                    <AlertBanner
                      variant="warning"
                      title="Warnings (non-blocking)"
                      description={validateResult.warnings.map((w) =>
                        typeof w === 'object'
                          ? `${(w as { field: string }).field}: ${(w as { message: string }).message}`
                          : String(w)
                      ).join(' · ')}
                    />
                  </div>
                )}
              </Card>
            )}

            {previewResult && (
              <Card title="Hard Validation + AI Review">
                {aiWarnings.length > 0 && (
                  <AlertBanner variant="warning" title="AI Critic Warnings (non-blocking)" description={aiWarnings.join(' · ')} />
                )}
                {previewResult.status === 'invalid' && previewResult.errors && (
                  <div className="mt-2">
                    <AlertBanner
                      variant="error"
                      title="Hard Validation Failed"
                      description={previewResult.errors.map((e) => `${e.field}: ${e.message}`).join(' · ')}
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
                    <AlertBanner
                      variant="success"
                      description={commitResult.message ?? 'Onboarding committed successfully.'}
                    />
                    <div className="mt-3">
                      <Btn variant="secondary" onClick={() => navigate(`/workspaces/${workspace.workspace_id}`)}>
                        Open Workspace →
                      </Btn>
                    </div>
                  </>
                ) : (
                  <AlertBanner
                    variant="error"
                    title="Commit Failed"
                    description={
                      commitResult.errors
                        ? commitResult.errors.map((e) => `${e.field}: ${e.message}`).join(' · ')
                        : commitResult.message ?? 'Unknown error'
                    }
                  />
                )}
              </Card>
            )}
        </div>
      )}
    </div>
  );
}

// ── Existing Config View (non-DRAFT workspaces) ───────────────────────────────

function ExistingConfigView({
  workspace,
  config,
}: {
  workspace: Workspace | null;
  config: Record<string, unknown>;
}) {
  const ws = config.workspace as Record<string, unknown> | undefined;
  const payCycle = config.pay_cycle as Record<string, unknown> | null;
  const grades = (config.grades as { code: string; description: string | null }[]) ?? [];
  const designations = (config.designations as { code: string; description: string | null }[]) ?? [];
  const salaryDefs = (config.salary_definitions as {
    name: string; code: string;
    components: { component_name: string; amount: number }[];
  }[]) ?? [];
  const payrollRules = (config.payroll_rules as { name: string; rule_type: string; method: string }[]) ?? [];
  const overrides = (config.component_overrides as { component_name: string; is_active: boolean }[]) ?? [];

  const workspaceId = workspace?.workspace_id;

  // ── Employee re-upload state ──────────────────────────────────────────────
  const [uploadEmployees, setUploadEmployees] = useState<MappedEmployee[]>([]);
  const [salaryDefOptions, setSalaryDefOptions] = useState<SalaryDefinitionOption[]>([]);
  const [designationOptions, setDesignationOptions] = useState<string[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<{ updated: number; not_found: string[] } | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // G3 — Payroll Behaviour
  const [payrollConfig, setPayrollConfig] = useState<WorkspacePayrollConfig | null>(null);
  const [configFetchError, setConfigFetchError] = useState<string | null>(null);
  const [phBehaviourOpen, setPhBehaviourOpen] = useState(true);
  const [editingBehaviour, setEditingBehaviour] = useState(false);
  const [behaviourForm, setBehaviourForm] = useState({
    effective_from: '',
    ph_mode: 'AUTOMATIC' as 'AUTOMATIC' | 'FILE_BASED',
    ph_rate_code: 'PH_OT',
    saturday_ph_rule: 'PH_TAKES_PRECEDENCE' as 'PH_TAKES_PRECEDENCE' | 'DAY_OF_WEEK_TAKES_PRECEDENCE',
    sunday_ph_rule: 'PH_TAKES_PRECEDENCE' as 'PH_TAKES_PRECEDENCE' | 'DAY_OF_WEEK_TAKES_PRECEDENCE',
    d3_leave_overlap_rule: 'LEAVE_ABSORBS_PH' as 'LEAVE_ABSORBS_PH',
    d4_absence_rule: 'ABSENT_IS_DEDUCTIBLE' as 'ABSENT_IS_DEDUCTIBLE' | 'PH_EXCUSES_ABSENCE',
  });
  const [behaviourSaving, setBehaviourSaving] = useState(false);
  const [behaviourError, setBehaviourError] = useState<string | null>(null);
  const [behaviourSaved, setBehaviourSaved] = useState(false);

  // G4 — Rate Code Registry
  const [rateCodes, setRateCodes] = useState<RateCode[]>([]);
  const [rateCodeFetchError, setRateCodeFetchError] = useState<string | null>(null);
  const [rateCodeOpen, setRateCodeOpen] = useState(false);
  const [rcForm, setRcForm] = useState({ code: '', multiplier: 1.0, unit: 'day', base: 'basic_daily', description: '' });
  const [rcAdding, setRcAdding] = useState(false);
  const [rcAddError, setRcAddError] = useState<string | null>(null);
  const [rcDeleteCode, setRcDeleteCode] = useState<string | null>(null);

  useEffect(() => {
    if (!workspaceId) return;
    workspaceApi.getSalaryDefinitions(workspaceId).then(setSalaryDefOptions).catch(() => {});
    workspaceApi.getDesignations(workspaceId)
      .then((rows) => setDesignationOptions(rows.map((r) => r.code)))
      .catch(() => {});
  }, [workspaceId]);

  useEffect(() => {
    if (!workspaceId) return;
    workspaceApi.getPayrollConfig(workspaceId)
      .then(setPayrollConfig)
      .catch(() => {
        setConfigFetchError('Could not load saved config — showing platform defaults.');
        setPayrollConfig({
          ph_mode: 'FILE_BASED',
          ph_rate_code: 'OT005',
          saturday_ph_rule: 'PH_TAKES_PRECEDENCE',
          sunday_ph_rule: 'PH_TAKES_PRECEDENCE',
          d3_leave_overlap_rule: 'LEAVE_ABSORBS_PH',
          d4_absence_rule: 'ABSENT_IS_DEDUCTIBLE',
        });
      });
  }, [workspaceId]);

  useEffect(() => {
    if (!workspaceId) return;
    workspaceApi.getRateCodes(workspaceId)
      .then(setRateCodes)
      .catch(() => setRateCodeFetchError('Failed to load rate codes.'));
  }, [workspaceId]);

  async function handleEmployeeUploadSubmit() {
    if (!workspaceId || uploadEmployees.length === 0) return;
    setUploading(true);
    setUploadError(null);
    setUploadResult(null);
    try {
      const body = uploadEmployees.map((emp) => ({
        employee_number: emp.employee_id,
        contract_start:  emp.contract_start || undefined,
        contract_end:    emp.contract_end   || undefined,
      }));
      const result = await api.patch<{ updated: number; not_found: string[] }>(
        `/${workspaceId}/employees/contracts`,
        body,
      );
      setUploadResult(result);
      setUploadEmployees([]);
    } catch (e: unknown) {
      setUploadError(e instanceof Error ? e.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  }

  return (
    <div>
      <ContentHeader
        title="Client Setup"
        subtitle={workspace ? `${workspace.name} · ${ws?.country_code ?? ''} · ${ws?.currency_code ?? ''}` : 'Loading…'}
      />

      <div className="mb-4 px-4 py-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-700">
        This workspace is <strong>{String(ws?.status ?? '')}</strong>. Configuration is read-only.
        Use the section below to correct employee contract dates.
      </div>

      <div className="space-y-5">
        {/* Pay Cycle */}
        <Card title="Pay Cycle">
          {payCycle ? (
            <dl className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
              {Object.entries(payCycle).map(([k, v]) => (
                <div key={k}>
                  <dt className="text-slate-500 text-xs font-medium mb-1 capitalize">{k.replace(/_/g, ' ')}</dt>
                  <dd className="text-slate-800 font-medium">{String(v)}</dd>
                </div>
              ))}
            </dl>
          ) : <p className="text-sm text-slate-400">No pay cycle defined.</p>}
        </Card>

        {/* Grades & Designations */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <Card title={`Grades (${grades.length})`}>
            {grades.length > 0 ? (
              <ul className="space-y-1">
                {grades.map((g) => (
                  <li key={g.code} className="flex items-center gap-2 bg-slate-50 rounded px-3 py-1.5 text-sm">
                    <span className="font-mono font-semibold text-slate-700">{g.code}</span>
                    {g.description && <span className="text-slate-400 text-xs">{g.description}</span>}
                  </li>
                ))}
              </ul>
            ) : <p className="text-sm text-slate-400">No grades defined.</p>}
          </Card>

          <Card title={`Designations (${designations.length})`}>
            {designations.length > 0 ? (
              <ul className="space-y-1">
                {designations.map((d) => (
                  <li key={d.code} className="flex items-center gap-2 bg-slate-50 rounded px-3 py-1.5 text-sm">
                    <span className="font-mono font-semibold text-slate-700">{d.code}</span>
                    {d.description && <span className="text-slate-400 text-xs">{d.description}</span>}
                  </li>
                ))}
              </ul>
            ) : <p className="text-sm text-slate-400">No designations defined.</p>}
          </Card>
        </div>

        {/* Salary Definitions */}
        <Card title={`Salary Definitions (${salaryDefs.length})`}>
          {salaryDefs.length > 0 ? (
            <div className="space-y-3">
              {salaryDefs.map((sd) => (
                <div key={sd.code} className="border border-slate-200 rounded p-3">
                  <p className="text-sm font-semibold text-slate-700 mb-2">
                    {sd.name} <span className="font-mono font-normal text-slate-400 text-xs">({sd.code})</span>
                  </p>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                    {sd.components.map((c) => (
                      <div key={c.component_name} className="bg-slate-50 rounded px-2 py-1.5 text-center">
                        <p className="text-xs text-slate-400">{c.component_name}</p>
                        <p className="text-xs font-semibold text-slate-700 mt-0.5">
                          {c.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : <p className="text-sm text-slate-400">No salary definitions defined.</p>}
        </Card>

        {/* Payroll Rules */}
        <Card title={`Payroll Rules (${payrollRules.length})`}>
          {payrollRules.length > 0 ? (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100">
                  <th className="text-left text-xs text-slate-500 font-medium pb-2 pr-4">Name</th>
                  <th className="text-left text-xs text-slate-500 font-medium pb-2 pr-4">Type</th>
                  <th className="text-left text-xs text-slate-500 font-medium pb-2">Method</th>
                </tr>
              </thead>
              <tbody>
                {payrollRules.map((r, i) => (
                  <tr key={i} className="border-t border-slate-100">
                    <td className="py-1.5 pr-4 text-slate-700">{r.name}</td>
                    <td className="py-1.5 pr-4 text-slate-500 text-xs">{r.rule_type}</td>
                    <td className="py-1.5 text-slate-500 text-xs font-mono">{r.method}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : <p className="text-sm text-slate-400">No payroll rules defined.</p>}
        </Card>

        {/* Component Overrides */}
        {overrides.length > 0 && (
          <Card title="Component Settings">
            <div className="space-y-2">
              {overrides.map((co) => (
                <div key={co.component_name} className="flex items-center justify-between py-1.5 px-2 rounded bg-slate-50 text-sm">
                  <span className="text-slate-700 font-mono text-xs">{co.component_name}</span>
                  <span className={`text-xs font-semibold px-2 py-0.5 rounded ${co.is_active ? 'bg-green-100 text-green-700' : 'bg-slate-200 text-slate-500'}`}>
                    {co.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* ── Employee re-upload ─────────────────────────────────────────── */}
        <div>
          <h2 className="text-sm font-semibold text-slate-700 mb-3 mt-2">
            Update Employee Contracts
          </h2>
          <p className="text-xs text-slate-500 mb-4">
            Upload your employee file to correct contract start/end dates.
            Existing employees are matched by <strong>employee_id</strong> column.
            New employees in the file will be ignored — only existing employees are updated.
          </p>

          <EmployeeUpload
            employees={uploadEmployees}
            salaryDefinitions={salaryDefOptions}
            designationOptions={designationOptions}
            onEmployeesLoaded={setUploadEmployees}
            onMappingChange={setUploadEmployees}
          />

          {uploadEmployees.length > 0 && (
            <div className="mt-4 flex items-center gap-3">
              <Btn
                onClick={handleEmployeeUploadSubmit}
                loading={uploading}
              >
                Update {uploadEmployees.length} Employee Contract{uploadEmployees.length !== 1 ? 's' : ''}
              </Btn>
              <span className="text-xs text-slate-400">
                Only contract_start and contract_end will be changed.
              </span>
            </div>
          )}

          {uploadResult && (
            <div className="mt-3">
              <AlertBanner
                variant="success"
                description={[
                  `${uploadResult.updated} contract${uploadResult.updated !== 1 ? 's' : ''} updated.`,
                  ...(uploadResult.not_found.length > 0
                    ? [`Not found (${uploadResult.not_found.length}): ${uploadResult.not_found.slice(0, 5).join(', ')}${uploadResult.not_found.length > 5 ? '…' : ''}`]
                    : []),
                ].join(' ')}
              />
            </div>
          )}

          {uploadError && (
            <div className="mt-3">
              <AlertBanner variant="error" description={uploadError} />
            </div>
          )}
        </div>

        {/* ── G3: Payroll Behaviour ──────────────────────────────────────── */}
        <div className="border border-slate-200 rounded-lg bg-white shadow-sm">
          <button
            className="w-full flex items-center justify-between px-5 py-3 text-left hover:bg-slate-50 transition-colors rounded-lg"
            onClick={() => setPhBehaviourOpen((v) => !v)}
          >
            <span className="text-sm font-semibold text-slate-700">Payroll Behaviour</span>
            <svg className={`w-4 h-4 text-slate-400 transition-transform ${phBehaviourOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" /></svg>
          </button>
          {phBehaviourOpen && (
            <div className="px-5 pb-5 border-t border-slate-100">
              {configFetchError && (
                <div className="mt-3 mb-2">
                  <AlertBanner variant="warning" description={configFetchError} />
                </div>
              )}

              {payrollConfig && (
                <div className="mt-3 mb-4 grid grid-cols-2 sm:grid-cols-3 gap-3 text-sm">
                  <div>
                    <p className="text-xs text-slate-400 mb-0.5">Public Holiday Mode</p>
                    <p className="font-medium text-slate-700">
                      {payrollConfig.ph_mode === 'AUTOMATIC' ? 'Automatic (from calendar)' : 'File-based (per run)'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400 mb-0.5">Public Holiday Rate Code</p>
                    <p className="font-mono text-slate-700">{payrollConfig.ph_rate_code}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400 mb-0.5">Effective From</p>
                    <p className="font-medium text-slate-700">
                      {payrollConfig.effective_from
                        ? new Date(payrollConfig.effective_from).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
                        : '—'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400 mb-0.5">Saturday Public Holiday Rule</p>
                    <p className="text-xs text-slate-600">
                      {payrollConfig.saturday_ph_rule === 'PH_TAKES_PRECEDENCE' ? 'Public holiday takes precedence' : 'Day-of-week rate applies'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400 mb-0.5">Sunday Public Holiday Rule</p>
                    <p className="text-xs text-slate-600">
                      {payrollConfig.sunday_ph_rule === 'PH_TAKES_PRECEDENCE' ? 'Public holiday takes precedence' : 'Day-of-week rate applies'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400 mb-0.5">Leave + Public Holiday Overlap</p>
                    <p className="text-xs text-slate-600">
                      {payrollConfig.d3_leave_overlap_rule === 'LEAVE_ABSORBS_PH' ? 'Leave absorbs public holiday (no additive pay)' : 'Public holiday is additive (pay both)'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400 mb-0.5">Absence on a Public Holiday</p>
                    <p className="text-xs text-slate-600">
                      {payrollConfig.d4_absence_rule === 'ABSENT_IS_DEDUCTIBLE' ? 'Absence is deductible' : 'Public holiday excuses absence'}
                    </p>
                  </div>
                </div>
              )}

              {!editingBehaviour ? (
                <button
                  className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-600 border border-slate-200 rounded px-3 py-1.5 hover:bg-slate-50 transition-colors"
                  onClick={() => {
                    setBehaviourForm({
                      effective_from: new Date().toISOString().slice(0, 10),
                      ph_mode: payrollConfig?.ph_mode ?? 'AUTOMATIC',
                      ph_rate_code: payrollConfig?.ph_rate_code ?? 'PH_OT',
                      saturday_ph_rule: payrollConfig?.saturday_ph_rule ?? 'PH_TAKES_PRECEDENCE',
                      sunday_ph_rule: payrollConfig?.sunday_ph_rule ?? 'PH_TAKES_PRECEDENCE',
                      d3_leave_overlap_rule: payrollConfig?.d3_leave_overlap_rule ?? 'LEAVE_ABSORBS_PH',
                      d4_absence_rule: payrollConfig?.d4_absence_rule ?? 'ABSENT_IS_DEDUCTIBLE',
                    });
                    setEditingBehaviour(true);
                    setBehaviourError(null);
                    setBehaviourSaved(false);
                  }}
                >
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>
                  {payrollConfig?.effective_from ? 'Update settings' : 'Configure settings'}
                </button>
              ) : (
                <div className="mt-3 space-y-5">
                  <p className="text-xs text-slate-400">
                    Changes take effect on the date below. Running payrolls are not affected.
                  </p>

                  {/* ── Row 1: When + PH Rate Code ── */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1.5">Effective From *</label>
                      <input
                        type="date"
                        value={behaviourForm.effective_from}
                        onChange={(e) => setBehaviourForm((f) => ({ ...f, effective_from: e.target.value }))}
                        className="border border-slate-200 rounded px-3 py-2 text-sm w-full focus:outline-none focus:ring-1 focus:ring-slate-400"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1.5">Public Holiday Rate Code</label>
                      <select
                        value={behaviourForm.ph_rate_code}
                        onChange={(e) => {
                          if (e.target.value === '__new__') {
                            setRateCodeOpen(true);
                            setEditingBehaviour(false);
                          } else {
                            setBehaviourForm((f) => ({ ...f, ph_rate_code: e.target.value }));
                          }
                        }}
                        className="border border-slate-200 rounded px-3 py-2 text-sm w-full focus:outline-none focus:ring-1 focus:ring-slate-400"
                      >
                        {rateCodes.length === 0 && (
                          <option value={behaviourForm.ph_rate_code}>{behaviourForm.ph_rate_code}</option>
                        )}
                        {rateCodes.map((rc) => (
                          <option key={rc.code} value={rc.code}>
                            {rc.code} — {rc.multiplier}× {rc.unit === 'hour' ? 'hourly' : 'daily'}
                          </option>
                        ))}
                        <option disabled>──────────────</option>
                        <option value="__new__">+ Add new rate code…</option>
                      </select>
                    </div>
                  </div>

                  {/* ── PH Mode ── */}
                  <div>
                    <p className="text-xs font-semibold text-slate-600 mb-2">Public Holiday Mode</p>
                    <div className="flex gap-3">
                      {([
                        { v: 'AUTOMATIC', label: 'Automatic', sub: 'Uses the system calendar' },
                        { v: 'FILE_BASED', label: 'File-based', sub: 'Supplied per payroll run' },
                      ] as const).map(({ v, label, sub }) => (
                        <label
                          key={v}
                          className={`flex-1 flex items-start gap-2.5 border rounded-lg px-3 py-2.5 cursor-pointer transition-colors ${behaviourForm.ph_mode === v ? 'border-slate-700 bg-slate-50' : 'border-slate-200 hover:border-slate-300'}`}
                        >
                          <input
                            type="radio"
                            name="ph_mode"
                            value={v}
                            checked={behaviourForm.ph_mode === v}
                            onChange={() => setBehaviourForm((f) => ({ ...f, ph_mode: v }))}
                            className="mt-0.5 accent-slate-700 shrink-0"
                          />
                          <div>
                            <p className="text-sm font-medium text-slate-700">{label}</p>
                            <p className="text-xs text-slate-400 mt-0.5">{sub}</p>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* ── Weekend Rules ── */}
                  <div>
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Weekend Rules</p>
                    <div className="border border-slate-100 rounded-lg divide-y divide-slate-100">
                      {([
                        { day: 'Saturday', field: 'saturday_ph_rule' as const },
                        { day: 'Sunday',   field: 'sunday_ph_rule'   as const },
                      ]).map(({ day, field }) => (
                        <div key={day} className="flex items-center justify-between px-4 py-3">
                          <span className="text-sm text-slate-600 w-20">{day}</span>
                          <div className="flex gap-2">
                            {([
                              { v: 'PH_TAKES_PRECEDENCE',       label: 'Public holiday rate' },
                              { v: 'DAY_OF_WEEK_TAKES_PRECEDENCE', label: 'Weekend rate' },
                            ] as const).map(({ v, label }) => (
                              <button
                                key={v}
                                type="button"
                                onClick={() => setBehaviourForm((f) => ({ ...f, [field]: v }))}
                                className={`text-xs px-3 py-1.5 rounded-md border transition-colors ${behaviourForm[field] === v ? 'bg-slate-700 text-white border-slate-700' : 'bg-white text-slate-500 border-slate-200 hover:border-slate-400'}`}
                              >
                                {label}
                              </button>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* ── Pay Calculation Rules ── */}
                  <div>
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Pay Calculation Rules</p>
                    <div className="border border-slate-100 rounded-lg divide-y divide-slate-100">
                      <div className="flex items-center justify-between px-4 py-3">
                        <div className="mr-4">
                          <p className="text-sm text-slate-600">Leave overlaps a public holiday</p>
                          <p className="text-xs text-slate-400 mt-0.5">What happens when leave and a PH fall on the same day?</p>
                        </div>
                        <select
                          value={behaviourForm.d3_leave_overlap_rule}
                          onChange={(e) => setBehaviourForm((f) => ({ ...f, d3_leave_overlap_rule: e.target.value as typeof f.d3_leave_overlap_rule }))}
                          className="border border-slate-200 rounded px-2.5 py-1.5 text-xs text-slate-700 focus:outline-none focus:ring-1 focus:ring-slate-400 shrink-0"
                        >
                          <option value="LEAVE_ABSORBS_PH">Leave absorbs — no additive pay</option>
                        </select>
                      </div>
                      <div className="flex items-center justify-between px-4 py-3">
                        <div className="mr-4">
                          <p className="text-sm text-slate-600">Employee is absent on a public holiday</p>
                          <p className="text-xs text-slate-400 mt-0.5">Is the absence deductible when the day is a PH?</p>
                        </div>
                        <select
                          value={behaviourForm.d4_absence_rule}
                          onChange={(e) => setBehaviourForm((f) => ({ ...f, d4_absence_rule: e.target.value as typeof f.d4_absence_rule }))}
                          className="border border-slate-200 rounded px-2.5 py-1.5 text-xs text-slate-700 focus:outline-none focus:ring-1 focus:ring-slate-400 shrink-0"
                        >
                          <option value="ABSENT_IS_DEDUCTIBLE">Deductible — absence still counts</option>
                          <option value="PH_EXCUSES_ABSENCE">Excused — PH covers the absence</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {behaviourError && (
                    <AlertBanner variant="error" description={behaviourError} />
                  )}
                  {behaviourSaved && (
                    <AlertBanner variant="success" description="Payroll behaviour config saved." />
                  )}

                  <div className="flex gap-2 pt-1">
                    <Btn
                      onClick={async () => {
                        if (!workspaceId || !behaviourForm.effective_from) return;
                        setBehaviourSaving(true);
                        setBehaviourError(null);
                        try {
                          const saved = await workspaceApi.upsertPayrollConfig(workspaceId, behaviourForm);
                          setPayrollConfig(saved);
                          setBehaviourSaved(true);
                          setEditingBehaviour(false);
                        } catch (e: unknown) {
                          setBehaviourError(e instanceof Error ? e.message : 'Failed to save config');
                        } finally {
                          setBehaviourSaving(false);
                        }
                      }}
                      loading={behaviourSaving}
                      disabled={!behaviourForm.effective_from}
                    >
                      Save settings
                    </Btn>
                    <button
                      className="text-xs text-slate-400 hover:text-slate-600 px-3 py-1.5 transition-colors"
                      onClick={() => { setEditingBehaviour(false); setBehaviourError(null); setBehaviourSaved(false); }}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* ── G4: Rate Code Registry ─────────────────────────────────────── */}
        <div className="border border-slate-200 rounded-lg bg-white shadow-sm">
          <button
            className="w-full flex items-center justify-between px-5 py-3 text-left hover:bg-slate-50 transition-colors rounded-lg"
            onClick={() => setRateCodeOpen((v) => !v)}
          >
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-slate-700">Rate Code Registry</span>
              <span className="text-xs text-slate-400">
                {rateCodes.length} code{rateCodes.length !== 1 ? 's' : ''}
              </span>
            </div>
            <svg className={`w-4 h-4 text-slate-400 transition-transform ${rateCodeOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" /></svg>
          </button>
          {rateCodeOpen && (
            <div className="px-5 pb-5 border-t border-slate-100">
              {rateCodeFetchError && (
                <div className="mt-3 mb-2">
                  <AlertBanner variant="error" description={rateCodeFetchError} />
                </div>
              )}

              <table className="w-full text-sm mt-3">
                <thead>
                  <tr className="border-b border-slate-100">
                    <th className="text-left text-xs text-slate-400 font-semibold uppercase tracking-wide pb-2 pr-3">Code</th>
                    <th className="text-left text-xs text-slate-400 font-semibold uppercase tracking-wide pb-2 pr-3">Multiplier</th>
                    <th className="text-left text-xs text-slate-400 font-semibold uppercase tracking-wide pb-2 pr-3">Unit</th>
                    <th className="text-left text-xs text-slate-400 font-semibold uppercase tracking-wide pb-2 pr-3">Base</th>
                    <th className="text-left text-xs text-slate-400 font-semibold uppercase tracking-wide pb-2">Source</th>
                    <th className="pb-2" />
                  </tr>
                </thead>
                <tbody>
                  {rateCodes.map((rc) => (
                    <tr key={rc.code} className={`border-b border-slate-50 ${rc.is_platform ? 'opacity-60' : ''}`}>
                      <td className="py-2 pr-3 font-mono text-xs text-slate-700">{rc.code}</td>
                      <td className="py-2 pr-3 text-slate-600">{rc.multiplier}×</td>
                      <td className="py-2 pr-3 text-slate-500 text-xs capitalize">{rc.unit}</td>
                      <td className="py-2 pr-3 text-slate-500 text-xs">
                        {rc.base === 'basic_daily' ? 'Basic daily' : rc.base === 'basic_hourly' ? 'Basic hourly' : rc.base}
                      </td>
                      <td className="py-2 pr-3">
                        {rc.is_platform ? (
                          <span className="text-xs text-slate-400 italic">platform</span>
                        ) : (
                          <span className="text-xs text-blue-600">workspace</span>
                        )}
                      </td>
                      <td className="py-2">
                        {!rc.is_platform && (
                          rcDeleteCode === rc.code ? (
                            <span className="flex items-center gap-2">
                              <button
                                onClick={async () => {
                                  if (!workspaceId) return;
                                  try {
                                    await workspaceApi.deleteRateCode(workspaceId, rc.code);
                                    setRateCodes((prev) => prev.filter((r) => r.code !== rc.code));
                                    setRcDeleteCode(null);
                                  } catch (e: unknown) {
                                    setRcAddError(e instanceof Error ? e.message : 'Delete failed');
                                    setRcDeleteCode(null);
                                  }
                                }}
                                className="text-xs text-red-600 hover:text-red-800"
                              >
                                Confirm
                              </button>
                              <button
                                onClick={() => setRcDeleteCode(null)}
                                className="text-xs text-slate-400 hover:text-slate-600"
                              >
                                Cancel
                              </button>
                            </span>
                          ) : (
                            <button
                              onClick={() => setRcDeleteCode(rc.code)}
                              className="text-xs text-red-400 hover:text-red-600"
                            >
                              Delete
                            </button>
                          )
                        )}
                      </td>
                    </tr>
                  ))}
                  {rateCodes.length === 0 && (
                    <tr>
                      <td colSpan={6} className="py-4 text-sm text-slate-400 text-center">
                        No rate codes found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>

              <div className="mt-4 border-t border-slate-100 pt-4">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">
                  Add Workspace Rate Code
                </p>
                <div className="flex gap-3 flex-wrap items-end">
                  <div>
                    <label className="block text-xs font-medium text-slate-600 mb-1">Code *</label>
                    <input
                      type="text"
                      value={rcForm.code}
                      onChange={(e) => setRcForm((f) => ({ ...f, code: e.target.value.toUpperCase() }))}
                      placeholder="e.g. SHIFT2"
                      className="border border-slate-200 rounded px-3 py-1.5 text-sm font-mono w-28 focus:outline-none focus:ring-1 focus:ring-slate-400"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-600 mb-1">Multiplier</label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      value={rcForm.multiplier}
                      onChange={(e) => setRcForm((f) => ({ ...f, multiplier: parseFloat(e.target.value) || 1 }))}
                      className="border border-slate-200 rounded px-3 py-1.5 text-sm w-20 focus:outline-none focus:ring-1 focus:ring-slate-400"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-600 mb-1">Unit</label>
                    <select
                      value={rcForm.unit}
                      onChange={(e) => setRcForm((f) => ({ ...f, unit: e.target.value }))}
                      className="border border-slate-200 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-slate-400"
                    >
                      <option value="day">Day</option>
                      <option value="hour">Hour</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-600 mb-1">Base</label>
                    <select
                      value={rcForm.base}
                      onChange={(e) => setRcForm((f) => ({ ...f, base: e.target.value }))}
                      className="border border-slate-200 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-slate-400"
                    >
                      <option value="basic_daily">Basic Daily</option>
                      <option value="basic_hourly">Basic Hourly</option>
                    </select>
                  </div>
                  <div className="flex-1 min-w-32">
                    <label className="block text-xs font-medium text-slate-600 mb-1">Description</label>
                    <input
                      type="text"
                      value={rcForm.description}
                      onChange={(e) => setRcForm((f) => ({ ...f, description: e.target.value }))}
                      placeholder="Optional"
                      className="border border-slate-200 rounded px-3 py-1.5 text-sm w-full focus:outline-none focus:ring-1 focus:ring-slate-400"
                    />
                  </div>
                  <Btn
                    onClick={async () => {
                      if (!workspaceId || !rcForm.code.trim()) return;
                      setRcAdding(true);
                      setRcAddError(null);
                      try {
                        const created = await workspaceApi.addRateCode(workspaceId, {
                          code: rcForm.code.trim(),
                          multiplier: rcForm.multiplier,
                          unit: rcForm.unit as 'day' | 'hour',
                          base: rcForm.base as 'basic_daily' | 'basic_hourly',
                          description: rcForm.description || undefined,
                        });
                        setRateCodes((prev) => [...prev, created]);
                        setRcForm({ code: '', multiplier: 1.0, unit: 'day', base: 'basic_daily', description: '' });
                      } catch (e: unknown) {
                        const msg = e instanceof Error ? e.message : 'Failed to add rate code';
                        setRcAddError(
                          msg.includes('409') || msg.toLowerCase().includes('duplicate')
                            ? `Code "${rcForm.code}" already exists.`
                            : msg
                        );
                      } finally {
                        setRcAdding(false);
                      }
                    }}
                    loading={rcAdding}
                    disabled={!rcForm.code.trim()}
                  >
                    Add
                  </Btn>
                </div>
                {rcAddError && <p className="text-xs text-red-500 mt-2">{rcAddError}</p>}
              </div>
            </div>
          )}
        </div>

      </div>
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
                {Object.entries(payCycle)
                  .filter(([, v]) => v !== null && typeof v !== 'object')
                  .map(([k, v]) => (
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
                      {Boolean(g.description) && <span className="text-xs text-slate-400">{String(g.description)}</span>}
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
                      {Boolean(d.description) && <span className="text-xs text-slate-400">{String(d.description)}</span>}
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
