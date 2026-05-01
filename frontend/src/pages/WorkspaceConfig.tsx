import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { workspaceApi } from '../api/workspace';
import { WorkspaceExcelUpload, type WorkspaceConfig as WsConfig } from '../components/onboarding/WorkspaceExcelUpload';
import { api } from '../api/client';
import type { WorkspacePayrollConfig, RateCode } from '../types/payroll';
import {
  ContentHeader,
  Card,
  Btn,
  StatusBadge,
  AlertBanner,
  SlideOver,
  ExpandableRow,
  Breadcrumb,
  ConfirmDialog,
  TextInput,
  NumberInput,
  Toggle,
} from '../design-system';
import { useWorkspaceContext } from '../context/WorkspaceContext';

// ── Types ─────────────────────────────────────────────────────────────────────

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
  salary_definition_id: string;
  name: string;
  code: string;
  components: SalaryComponent[];
}

interface PayrollRule {
  rule_id: string;
  name: string;
  rule_type: string;
  method: string;
  is_active: boolean;
  rule_definition_json: Record<string, unknown>;
}

interface ComponentOverride {
  component_name: string;
  overrides_json: Record<string, unknown>;
  is_active: boolean;
  proration_strategy: string | null;
}

interface PlatformComponent {
  component_code: string;
  label: string;
  component_class: string | null;
}

interface WorkspaceConfiguration {
  workspace: {
    id: string;
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

// ── Icons ─────────────────────────────────────────────────────────────────────

function PencilIcon() {
  return (
    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M15.232 5.232l3.536 3.536M9 13l6.586-6.586a2 2 0 012.828 2.828L11.828 15.828a4 4 0 01-1.414.93l-3 1 1-3a4 4 0 01.93-1.414z" />
    </svg>
  );
}

function LockIcon() {
  return (
    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24" className="text-gray-400">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
    </svg>
  );
}

// ── Helper components ─────────────────────────────────────────────────────────

function Dt({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-gray-500 text-xs font-medium mb-1">{label}</dt>
      <dd className="text-gray-800 font-medium text-sm">{value}</dd>
    </div>
  );
}

function SectionHeader({
  label,
  count,
  children,
}: {
  label: string;
  count?: number;
  children?: React.ReactNode;
}) {
  return (
    <div className="flex justify-between items-center mb-3">
      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
        {label}
        {count !== undefined && count > 0 && (
          <span className="text-gray-400 font-normal normal-case ml-1">({count})</span>
        )}
      </p>
      {children && <div className="flex items-center gap-2">{children}</div>}
    </div>
  );
}

function ReadOnlyCode({ value }: { value: string }) {
  return (
    <div className="relative">
      <input
        value={value}
        disabled
        className="w-full bg-gray-100 text-gray-500 rounded px-3 py-2 pr-8 text-sm cursor-not-allowed border border-gray-200"
      />
      <span className="absolute right-2.5 top-2.5">
        <LockIcon />
      </span>
    </div>
  );
}

function SelectField({
  label,
  value,
  onChange,
  children,
  hint,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  children: React.ReactNode;
  hint?: string;
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-sm font-medium text-gray-700">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        style={{ borderRadius: 'var(--radius-input)', height: 'var(--height-md)' }}
        className="w-full border border-gray-300 hover:border-gray-400 rounded px-3 text-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent"
      >
        {children}
      </select>
      {hint && <p className="text-xs text-gray-500">{hint}</p>}
    </div>
  );
}

function RowEditBtn({ label, onClick }: { label: string; onClick: () => void }) {
  return (
    <button
      type="button"
      aria-label={`Edit ${label}`}
      onClick={onClick}
      className="p-1.5 rounded hover:bg-gray-100 text-gray-400 hover:text-gray-700 transition-colors"
    >
      <PencilIcon />
    </button>
  );
}

function TrashIcon() {
  return (
    <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
    </svg>
  );
}

function LockSmIcon() {
  return (
    <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24" className="inline-block text-gray-300 mr-1 flex-shrink-0">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
    </svg>
  );
}

function extractError(e: unknown): string {
  if (e instanceof Error) {
    try {
      const parsed = JSON.parse(e.message.replace(/^\d+ [^:]+: /, ''));
      if (parsed?.detail) return String(parsed.detail);
    } catch { /* fall through */ }
    return e.message;
  }
  return 'An unexpected error occurred.';
}

// ── Edit Pay Cycle SlideOver ──────────────────────────────────────────────────

function EditPayCycleSlideOver({
  open,
  workspaceId,
  current,
  onClose,
  onSaved,
}: {
  open: boolean;
  workspaceId: string;
  current: PayCycle | null;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [frequency, setFrequency] = useState('MONTHLY');
  const [runDay, setRunDay] = useState('1');
  const [cutoffDay, setCutoffDay] = useState('1');
  const [paymentDay, setPaymentDay] = useState('1');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open && current) {
      setFrequency(current.frequency);
      setRunDay(String(current.run_day));
      setCutoffDay(String(current.cutoff_day));
      setPaymentDay(String(current.payment_day));
      setError(null);
    }
  }, [open, current]);

  async function handleSave() {
    setSaving(true);
    setError(null);
    try {
      await workspaceApi.updatePayCycle(workspaceId, {
        frequency,
        run_day: parseInt(runDay, 10),
        cutoff_day: parseInt(cutoffDay, 10),
        payment_day: parseInt(paymentDay, 10),
      });
      onSaved();
      onClose();
    } catch (e) {
      setError(extractError(e));
    } finally {
      setSaving(false);
    }
  }

  return (
    <SlideOver
      open={open}
      onClose={onClose}
      title="Edit Pay Cycle"
      footer={
        <div className="flex justify-end gap-3 w-full">
          <Btn variant="secondary" size="md" onClick={onClose}>Cancel</Btn>
          <Btn variant="primary" size="md" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving…' : 'Save Changes →'}
          </Btn>
        </div>
      }
    >
      <div className="space-y-4">
        {error && <AlertBanner variant="error" description={error} />}
        <SelectField
          label="Frequency"
          value={frequency}
          onChange={setFrequency}
        >
          <option value="MONTHLY">Monthly</option>
          <option value="BIWEEKLY">Bi-weekly</option>
          <option value="WEEKLY">Weekly</option>
        </SelectField>
        <div className="grid grid-cols-3 gap-3">
          <NumberInput
            label="Run Day"
            min={1} max={31}
            value={runDay}
            onChange={(e) => setRunDay(e.target.value)}
          />
          <NumberInput
            label="Cutoff Day"
            min={1} max={31}
            value={cutoffDay}
            onChange={(e) => setCutoffDay(e.target.value)}
          />
          <NumberInput
            label="Payment Day"
            min={1} max={31}
            value={paymentDay}
            onChange={(e) => setPaymentDay(e.target.value)}
          />
        </div>
        <p className="text-xs text-gray-500">
          ⓘ Run day, cutoff day, and payment day are stored for reference only and are not currently
          used in payroll calculations.
        </p>
      </div>
    </SlideOver>
  );
}

// ── Add / Edit Grade SlideOvers ───────────────────────────────────────────────

function AddGradeSlideOver({
  open,
  workspaceId,
  onClose,
  onSaved,
}: {
  open: boolean;
  workspaceId: string;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [code, setCode] = useState('');
  const [description, setDescription] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) { setCode(''); setDescription(''); setError(null); }
  }, [open]);

  async function handleSave() {
    if (!code.trim()) { setError('Grade code is required.'); return; }
    setSaving(true);
    setError(null);
    try {
      await workspaceApi.createGrade(workspaceId, {
        grade_code: code.trim().toUpperCase(),
        description: description.trim() || undefined,
      });
      onSaved();
      onClose();
    } catch (e) {
      setError(extractError(e));
    } finally {
      setSaving(false);
    }
  }

  return (
    <SlideOver open={open} onClose={onClose} title="Add Grade"
      footer={
        <div className="flex justify-end gap-3 w-full">
          <Btn variant="secondary" size="md" onClick={onClose}>Cancel</Btn>
          <Btn variant="primary" size="md" onClick={handleSave} disabled={saving}>
            {saving ? 'Adding…' : 'Add Grade →'}
          </Btn>
        </div>
      }
    >
      <div className="space-y-4">
        {error && <AlertBanner variant="error" description={error} />}
        <TextInput
          label="Grade Code"
          required
          value={code}
          onChange={(e) => setCode(e.target.value.toUpperCase())}
          placeholder="e.g. SENIOR_ASSOCIATE"
          className="font-mono"
        />
        <TextInput
          label="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Optional"
        />
      </div>
    </SlideOver>
  );
}

function EditGradeSlideOver({
  open,
  workspaceId,
  grade,
  onClose,
  onSaved,
}: {
  open: boolean;
  workspaceId: string;
  grade: Grade | null;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [description, setDescription] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open && grade) { setDescription(grade.description ?? ''); setError(null); }
  }, [open, grade]);

  async function handleSave() {
    if (!grade) return;
    setSaving(true);
    setError(null);
    try {
      await workspaceApi.updateGrade(workspaceId, grade.code, { description: description.trim() || undefined });
      onSaved();
      onClose();
    } catch (e) {
      setError(extractError(e));
    } finally {
      setSaving(false);
    }
  }

  return (
    <SlideOver open={open} onClose={onClose} title="Edit Grade"
      footer={
        <div className="flex justify-end gap-3 w-full">
          <Btn variant="secondary" size="md" onClick={onClose}>Cancel</Btn>
          <Btn variant="primary" size="md" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving…' : 'Save Changes →'}
          </Btn>
        </div>
      }
    >
      <div className="space-y-4">
        {error && <AlertBanner variant="error" description={error} />}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Grade Code</label>
          <ReadOnlyCode value={grade?.code ?? ''} />
        </div>
        <TextInput
          label="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Optional"
        />
      </div>
    </SlideOver>
  );
}

// ── Add / Edit Designation SlideOvers ─────────────────────────────────────────

function AddDesignationSlideOver({
  open,
  workspaceId,
  onClose,
  onSaved,
}: {
  open: boolean;
  workspaceId: string;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [code, setCode] = useState('');
  const [description, setDescription] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) { setCode(''); setDescription(''); setError(null); }
  }, [open]);

  async function handleSave() {
    if (!code.trim()) { setError('Designation code is required.'); return; }
    setSaving(true);
    setError(null);
    try {
      await workspaceApi.createDesignation(workspaceId, {
        designation_code: code.trim().toUpperCase(),
        description: description.trim() || undefined,
      });
      onSaved();
      onClose();
    } catch (e) {
      setError(extractError(e));
    } finally {
      setSaving(false);
    }
  }

  return (
    <SlideOver open={open} onClose={onClose} title="Add Designation"
      footer={
        <div className="flex justify-end gap-3 w-full">
          <Btn variant="secondary" size="md" onClick={onClose}>Cancel</Btn>
          <Btn variant="primary" size="md" onClick={handleSave} disabled={saving}>
            {saving ? 'Adding…' : 'Add Designation →'}
          </Btn>
        </div>
      }
    >
      <div className="space-y-4">
        {error && <AlertBanner variant="error" description={error} />}
        <TextInput
          label="Designation Code"
          required
          value={code}
          onChange={(e) => setCode(e.target.value.toUpperCase())}
          placeholder="e.g. SENIOR_MANAGER"
          className="font-mono"
        />
        <TextInput
          label="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Optional"
        />
      </div>
    </SlideOver>
  );
}

function EditDesignationSlideOver({
  open,
  workspaceId,
  designation,
  onClose,
  onSaved,
}: {
  open: boolean;
  workspaceId: string;
  designation: Designation | null;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [description, setDescription] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open && designation) { setDescription(designation.description ?? ''); setError(null); }
  }, [open, designation]);

  async function handleSave() {
    if (!designation) return;
    setSaving(true);
    setError(null);
    try {
      await workspaceApi.updateDesignation(workspaceId, designation.code, {
        description: description.trim() || undefined,
      });
      onSaved();
      onClose();
    } catch (e) {
      setError(extractError(e));
    } finally {
      setSaving(false);
    }
  }

  return (
    <SlideOver open={open} onClose={onClose} title="Edit Designation"
      footer={
        <div className="flex justify-end gap-3 w-full">
          <Btn variant="secondary" size="md" onClick={onClose}>Cancel</Btn>
          <Btn variant="primary" size="md" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving…' : 'Save Changes →'}
          </Btn>
        </div>
      }
    >
      <div className="space-y-4">
        {error && <AlertBanner variant="error" description={error} />}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Designation Code</label>
          <ReadOnlyCode value={designation?.code ?? ''} />
        </div>
        <TextInput
          label="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Optional"
        />
      </div>
    </SlideOver>
  );
}

// ── Edit Salary Definition SlideOver ──────────────────────────────────────────

const MANDATORY_COMPONENTS = new Set(['BASIC', 'HOUSING', 'TRANSPORT']);

function EditSalaryDefSlideOver({
  open,
  workspaceId,
  salaryDef,
  onClose,
  onSaved,
}: {
  open: boolean;
  workspaceId: string;
  salaryDef: SalaryDefinition | null;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [components, setComponents] = useState<SalaryComponent[]>([]);
  const [newCode, setNewCode] = useState('');
  const [newAmount, setNewAmount] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open && salaryDef) {
      setComponents(salaryDef.components.map((c) => ({ ...c })));
      setNewCode('');
      setNewAmount('');
      setError(null);
    }
  }, [open, salaryDef]);

  function updateAmount(index: number, value: string) {
    setComponents((prev) => prev.map((c, i) => i === index ? { ...c, amount: parseFloat(value) || 0 } : c));
  }

  function removeComponent(index: number) {
    setComponents((prev) => prev.filter((_, i) => i !== index));
  }

  function addComponent() {
    const code = newCode.trim().toUpperCase();
    if (!code || !newAmount) return;
    const amount = parseFloat(newAmount);
    if (isNaN(amount) || amount <= 0) return;
    if (components.some((c) => c.component_name === code)) return;
    setComponents((prev) => [...prev, { component_name: code, amount }]);
    setNewCode('');
    setNewAmount('');
  }

  async function handleSave() {
    if (!salaryDef) return;
    setSaving(true);
    setError(null);
    try {
      await workspaceApi.updateSalaryDefinition(workspaceId, salaryDef.salary_definition_id, {
        components_jsonb: components,
      });
      onSaved();
      onClose();
    } catch (e) {
      setError(extractError(e));
    } finally {
      setSaving(false);
    }
  }

  return (
    <SlideOver
      open={open}
      onClose={onClose}
      title={`Edit Salary Definition${salaryDef ? ` — ${salaryDef.name}` : ''}`}
      footer={
        <div className="flex justify-end gap-3 w-full">
          <Btn variant="secondary" size="md" onClick={onClose}>Cancel</Btn>
          <Btn variant="primary" size="md" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving…' : 'Save Changes →'}
          </Btn>
        </div>
      }
    >
      <div className="space-y-4">
        {error && <AlertBanner variant="error" description={error} />}
        <AlertBanner
          variant="info"
          description="Changes apply from the next payroll run only. They do not affect runs already in progress."
        />
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100">
              <th className="text-left text-[11px] font-semibold text-gray-500 uppercase tracking-wide pb-2">Component</th>
              <th className="text-right text-[11px] font-semibold text-gray-500 uppercase tracking-wide pb-2 pr-2">Amount (₦)</th>
              <th className="w-8" />
            </tr>
          </thead>
          <tbody>
            {components.map((c, i) => {
              const isMandatory = MANDATORY_COMPONENTS.has(c.component_name);
              return (
                <tr key={c.component_name} className="border-b border-gray-50">
                  <td className="py-2 text-gray-700 font-mono text-xs">{c.component_name}</td>
                  <td className="py-2 pr-2">
                    <div className="relative">
                      <span className="absolute inset-y-0 left-3 flex items-center text-sm text-gray-500 pointer-events-none select-none">₦</span>
                      <input
                        type="number"
                        min="0.01"
                        step="0.01"
                        value={c.amount}
                        onChange={(e) => updateAmount(i, e.target.value)}
                        aria-label={`Amount for ${c.component_name}`}
                        style={{ borderRadius: 'var(--radius-input)', height: 'var(--height-md)' }}
                        className="w-full border border-gray-300 hover:border-gray-400 text-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent pl-7 pr-3 text-right"
                      />
                    </div>
                  </td>
                  <td className="py-2 text-center">
                    {!isMandatory && (
                      <button
                        type="button"
                        onClick={() => removeComponent(i)}
                        className="text-gray-400 hover:text-red-500 transition-colors text-xs px-1"
                        aria-label={`Remove ${c.component_name}`}
                      >
                        ✕
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        <div className="pt-2 border-t border-gray-100">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Add Component</p>
          <div className="flex gap-2 items-end">
            <TextInput
              label="Code"
              value={newCode}
              onChange={(e) => setNewCode(e.target.value.toUpperCase())}
              placeholder="e.g. MEAL_ALLOWANCE"
              className="w-2/5 font-mono"
            />
            <NumberInput
              label="Amount"
              currency
              min={0.01}
              step={0.01}
              value={newAmount}
              onChange={(e) => setNewAmount(e.target.value)}
              placeholder="0.00"
              className="w-2/5"
            />
            <Btn variant="secondary" size="sm" onClick={addComponent}>Add</Btn>
          </div>
        </div>
      </div>
    </SlideOver>
  );
}

// ── Edit Component Override SlideOver ─────────────────────────────────────────

const PRORATION_OPTIONS = [
  { value: 'FULL_MONTH', label: 'Full Month' },
  { value: 'CALENDAR_DAYS', label: 'Calendar Days' },
  { value: 'WORKING_DAYS', label: 'Working Days' },
];

function EditComponentOverrideSlideOver({
  open,
  workspaceId,
  override: co,
  onClose,
  onSaved,
}: {
  open: boolean;
  workspaceId: string;
  override: ComponentOverride | null;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [isActive, setIsActive] = useState(true);
  const [prorationStrategy, setProrationStrategy] = useState('FULL_MONTH');
  const [rateValues, setRateValues] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open && co) {
      setIsActive(co.is_active);
      setProrationStrategy(co.proration_strategy ?? 'FULL_MONTH');
      setRateValues(
        Object.fromEntries(
          Object.entries(co.overrides_json ?? {}).map(([k, v]) => [k, String(v)])
        )
      );
      setError(null);
    }
  }, [open, co]);

  async function handleSave() {
    if (!co) return;
    setSaving(true);
    setError(null);
    const builtOverrides: Record<string, number> = {};
    for (const [k, v] of Object.entries(rateValues)) {
      const n = parseFloat(v);
      if (!isNaN(n)) builtOverrides[k] = n;
    }
    try {
      await workspaceApi.updateComponentOverride(workspaceId, co.component_name, {
        is_active: isActive,
        proration_strategy: prorationStrategy,
        overrides_json: builtOverrides,
      });
      onSaved();
      onClose();
    } catch (e) {
      setError(extractError(e));
    } finally {
      setSaving(false);
    }
  }

  const rateEntries = Object.entries(rateValues);

  return (
    <SlideOver
      open={open}
      onClose={onClose}
      title={`Edit Override — ${co?.component_name ?? ''}`}
      footer={
        <div className="flex justify-end gap-3 w-full">
          <Btn variant="secondary" size="md" onClick={onClose}>Cancel</Btn>
          <Btn variant="primary" size="md" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving…' : 'Save Changes →'}
          </Btn>
        </div>
      }
    >
      <div className="space-y-5">
        {error && <AlertBanner variant="error" description={error} />}

        <Toggle
          label="Component enabled"
          checked={isActive}
          onChange={setIsActive}
          inlineLabel
        />
        {!isActive && (
          <AlertBanner
            variant="warning"
            description="Disabling this component means it will not be calculated for any employee in the next payroll run."
          />
        )}

        <SelectField
          label="Proration Strategy"
          value={prorationStrategy}
          onChange={setProrationStrategy}
        >
          {PRORATION_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </SelectField>

        {rateEntries.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Rate Overrides</p>
            <div className="space-y-3">
              {rateEntries.map(([key, val]) => (
                <NumberInput
                  key={key}
                  label={key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                  value={val}
                  onChange={(e) => setRateValues((prev) => ({ ...prev, [key]: e.target.value }))}
                  hint={`Key: ${key}`}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </SlideOver>
  );
}

// ── Add Component Override SlideOver ──────────────────────────────────────────

function AddComponentOverrideSlideOver({
  open,
  workspaceId,
  onClose,
  onSaved,
}: {
  open: boolean;
  workspaceId: string;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [platformComponents, setPlatformComponents] = useState<PlatformComponent[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [componentCode, setComponentCode] = useState('');
  const [isActive, setIsActive] = useState(true);
  const [prorationStrategy, setProrationStrategy] = useState('FULL_MONTH');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      setError(null);
      setLoadError(null);
      setIsActive(true);
      setProrationStrategy('FULL_MONTH');
      workspaceApi.getPlatformComponents(workspaceId)
        .then((comps) => {
          setPlatformComponents(comps);
          if (comps.length > 0) setComponentCode(comps[0].component_code);
        })
        .catch(() => setLoadError('Could not load components. Close and try again.'));
    }
  }, [open, workspaceId]);

  async function handleSave() {
    if (!componentCode) { setError('Select a component.'); return; }
    setSaving(true);
    setError(null);
    try {
      await workspaceApi.updateComponentOverride(workspaceId, componentCode, {
        is_active: isActive,
        proration_strategy: prorationStrategy,
      });
      onSaved();
      onClose();
    } catch (e) {
      setError(extractError(e));
    } finally {
      setSaving(false);
    }
  }

  return (
    <SlideOver
      open={open}
      onClose={onClose}
      title="Add Component Override"
      footer={
        <div className="flex justify-end gap-3 w-full">
          <Btn variant="secondary" size="md" onClick={onClose}>Cancel</Btn>
          <Btn variant="primary" size="md" onClick={handleSave} disabled={saving || !!loadError}>
            {saving ? 'Adding…' : 'Add Override →'}
          </Btn>
        </div>
      }
    >
      <div className="space-y-4">
        {error && <AlertBanner variant="error" description={error} />}
        {loadError && <AlertBanner variant="error" description={loadError} />}
        <SelectField
          label="Component"
          value={componentCode}
          onChange={setComponentCode}
        >
          {platformComponents.map((c) => (
            <option key={c.component_code} value={c.component_code}>{c.label} ({c.component_code})</option>
          ))}
        </SelectField>
        <Toggle
          label="Component enabled"
          checked={isActive}
          onChange={setIsActive}
          inlineLabel
        />
        <SelectField
          label="Proration Strategy"
          value={prorationStrategy}
          onChange={setProrationStrategy}
        >
          {PRORATION_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </SelectField>
      </div>
    </SlideOver>
  );
}

// ── Add Earning Component SlideOver ───────────────────────────────────────────

function AddEarningComponentSlideOver({
  open,
  workspaceId,
  onClose,
  onSaved,
}: {
  open: boolean;
  workspaceId: string;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [name, setName] = useState('');
  const [amount, setAmount] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) { setName(''); setAmount(''); setError(null); }
  }, [open]);

  async function handleSave() {
    if (!name.trim()) { setError('Name is required.'); return; }
    const amt = parseFloat(amount);
    if (isNaN(amt) || amt <= 0) { setError('Enter a valid amount greater than zero.'); return; }
    setSaving(true);
    setError(null);
    try {
      await workspaceApi.createPayrollRule(workspaceId, {
        rule_name: name.trim(),
        rule_type: 'EARNING',
        rule_definition_json: { calculation_method: 'fixed_amount', amount: amt },
      });
      onSaved();
      onClose();
    } catch (e) {
      setError(extractError(e));
    } finally {
      setSaving(false);
    }
  }

  return (
    <SlideOver
      open={open}
      onClose={onClose}
      title="Add Earning Component"
      footer={
        <div className="flex justify-end gap-3 w-full">
          <Btn variant="secondary" size="md" onClick={onClose}>Cancel</Btn>
          <Btn variant="primary" size="md" onClick={handleSave} disabled={saving}>
            {saving ? 'Adding…' : 'Add Component →'}
          </Btn>
        </div>
      }
    >
      <div className="space-y-4">
        {error && <AlertBanner variant="error" description={error} />}
        <AlertBanner
          variant="info"
          description="This component will also appear in the Payroll Rules tab where you can manage its activation and re-publish rule sets."
        />
        <TextInput
          label="Component Name"
          required
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g. Meal Allowance"
          hint="Use a clear, descriptive name. It will appear on pay slips."
        />
        <NumberInput
          label="Monthly Amount (₦)"
          required
          currency
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          placeholder="0.00"
          hint="Fixed amount paid each payroll period."
        />
      </div>
    </SlideOver>
  );
}

// ── Add Payroll Rule SlideOver ─────────────────────────────────────────────────

const RULE_TYPE_OPTIONS = [
  { value: 'UNIT_RATE', label: 'Unit × Rate' },
  { value: 'OT_MULTIPLIER', label: 'OT Multiplier (Rate Code)' },
  { value: 'FIXED_AMOUNT', label: 'Fixed Amount' },
  { value: 'PERCENTAGE_OF_GROSS', label: 'Percentage of Gross' },
  { value: 'ALLOWANCE', label: 'Allowance' },
];

// calculation_method values recognised by the rule evaluator
const RULE_TYPE_METHOD: Record<string, string> = {
  UNIT_RATE: 'unit_multiplier',
  OT_MULTIPLIER: 'ot_multiplier',
  FIXED_AMOUNT: 'fixed_amount',
  PERCENTAGE_OF_GROSS: 'percentage_of_gross',
  ALLOWANCE: 'fixed_amount',
};

function RuleFields({
  ruleType,
  originalMethod,
  values,
  onChange,
  rateCodes,
}: {
  ruleType: string;
  originalMethod?: string;
  values: Record<string, string>;
  onChange: (key: string, val: string) => void;
  rateCodes: RateCode[];
}) {
  // OT Multiplier — uses a rate code reference from the registry
  if (ruleType === 'OT_MULTIPLIER' || originalMethod === 'ot_multiplier') {
    return (
      <>
        <SelectField
          label="Rate Code"
          value={values.rate_code ?? values.ot_code ?? ''}
          onChange={(v) => onChange('rate_code', v)}
          hint="OT rate code from the rate code registry."
        >
          <option value="">— select a rate code —</option>
          {rateCodes.map((rc) => (
            <option key={rc.code} value={rc.code}>
              {rc.code} — ×{rc.multiplier} {rc.unit}
            </option>
          ))}
        </SelectField>
        <TextInput
          label="Input Field"
          required
          value={values.input_field ?? ''}
          onChange={(e) => onChange('input_field', e.target.value)}
          placeholder="e.g. ot1_hours"
          hint="The employee input key that carries the OT quantity."
          className="font-mono"
        />
        <SelectField
          label="Unit"
          value={values.unit ?? 'hour'}
          onChange={(v) => onChange('unit', v)}
          hint="Unit of the input quantity."
        >
          <option value="hour">hour</option>
          <option value="day">day</option>
        </SelectField>
      </>
    );
  }
  if (originalMethod === 'daily_rate_deduction') {
    return (
      <>
        <TextInput
          label="Absent Days Input Code"
          required
          value={values.absent_days_input_code ?? ''}
          onChange={(e) => onChange('absent_days_input_code', e.target.value)}
          hint="The input key that carries the absent day count"
          className="font-mono"
        />
        <NumberInput
          label="Working Days in Month"
          required
          value={values.working_days_in_month ?? ''}
          onChange={(e) => onChange('working_days_in_month', e.target.value)}
          hint="Standard working days used as denominator"
        />
      </>
    );
  }
  if (ruleType === 'UNIT_RATE') {
    return (
      <>
        <TextInput
          label="Input Field"
          required
          value={values.input_field ?? ''}
          onChange={(e) => onChange('input_field', e.target.value)}
          placeholder="e.g. overtime_hours"
          hint="The employee input key that carries the quantity for this rule."
        />
        <NumberInput
          label="Rate (₦ per unit)"
          required
          value={values.rate ?? ''}
          onChange={(e) => onChange('rate', e.target.value)}
          placeholder="0.00"
          hint="Amount paid per unit of input."
        />
        <SelectField
          label="Unit"
          value={values.unit ?? 'hour'}
          onChange={(v) => onChange('unit', v)}
          hint="Unit of the input quantity."
        >
          <option value="hour">hour</option>
          <option value="day">day</option>
        </SelectField>
      </>
    );
  }
  if (ruleType === 'FIXED_AMOUNT' || ruleType === 'ALLOWANCE') {
    return (
      <NumberInput
        label="Amount (₦)"
        required
        currency
        value={values.amount ?? ''}
        onChange={(e) => onChange('amount', e.target.value)}
        placeholder="0.00"
      />
    );
  }
  if (ruleType === 'PERCENTAGE_OF_GROSS') {
    return (
      <NumberInput
        label="Percentage (%)"
        required
        value={values.percentage ?? ''}
        onChange={(e) => onChange('percentage', e.target.value)}
        placeholder="e.g. 5 for 5%"
        hint="Applied as a percentage of gross pay."
      />
    );
  }
  return null;
}

function AddPayrollRuleSlideOver({
  open,
  workspaceId,
  rateCodes,
  onClose,
  onSaved,
}: {
  open: boolean;
  workspaceId: string;
  rateCodes: RateCode[];
  onClose: () => void;
  onSaved: () => void;
}) {
  const [ruleName, setRuleName] = useState('');
  const [ruleType, setRuleType] = useState('UNIT_RATE');
  const [fieldValues, setFieldValues] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) { setRuleName(''); setRuleType('UNIT_RATE'); setFieldValues({}); setError(null); }
  }, [open]);

  function handleTypeChange(newType: string) {
    setRuleType(newType);
    setFieldValues({});
  }

  function setField(key: string, val: string) {
    setFieldValues((prev) => ({ ...prev, [key]: val }));
  }

  function buildDefinition(): Record<string, unknown> {
    const method = RULE_TYPE_METHOD[ruleType] ?? ruleType.toLowerCase();
    const def: Record<string, unknown> = { calculation_method: method };
    for (const [k, v] of Object.entries(fieldValues)) {
      const n = parseFloat(v);
      def[k] = isNaN(n) ? v : n;
    }
    return def;
  }

  async function handleSave() {
    if (!ruleName.trim()) { setError('Rule name is required.'); return; }
    setSaving(true);
    setError(null);
    try {
      await workspaceApi.createPayrollRule(workspaceId, {
        rule_name: ruleName.trim(),
        rule_type: ruleType,
        rule_definition_json: buildDefinition(),
      });
      onSaved();
      onClose();
    } catch (e) {
      setError(extractError(e));
    } finally {
      setSaving(false);
    }
  }

  return (
    <SlideOver
      open={open}
      onClose={onClose}
      title="Add Payroll Rule"
      footer={
        <div className="flex justify-end gap-3 w-full">
          <Btn variant="secondary" size="md" onClick={onClose}>Cancel</Btn>
          <Btn variant="primary" size="md" onClick={handleSave} disabled={saving}>
            {saving ? 'Adding…' : 'Add Rule →'}
          </Btn>
        </div>
      }
    >
      <div className="space-y-4">
        {error && <AlertBanner variant="error" description={error} />}
        <TextInput
          label="Rule Name"
          required
          value={ruleName}
          onChange={(e) => setRuleName(e.target.value)}
          placeholder="e.g. Overtime — Weekday"
        />
        <SelectField
          label="Rule Type"
          value={ruleType}
          onChange={handleTypeChange}
        >
          {RULE_TYPE_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </SelectField>
        <RuleFields ruleType={ruleType} values={fieldValues} onChange={setField} rateCodes={rateCodes} />
      </div>
    </SlideOver>
  );
}

// ── Edit Payroll Rule SlideOver ───────────────────────────────────────────────

const METHOD_TO_RULE_TYPE: Record<string, string> = {
  unit_multiplier: 'UNIT_RATE',
  fixed_amount: 'FIXED_AMOUNT',
  percentage_of_gross: 'PERCENTAGE_OF_GROSS',
  ot_multiplier: 'OT_MULTIPLIER',
  daily_rate_deduction: 'UNIT_RATE',
};

function EditPayrollRuleSlideOver({
  open,
  rule,
  workspaceId,
  rateCodes,
  onClose,
  onSaved,
}: {
  open: boolean;
  rule: PayrollRule | null;
  workspaceId: string;
  rateCodes: RateCode[];
  onClose: () => void;
  onSaved: () => void;
}) {
  const [ruleName, setRuleName] = useState('');
  const [ruleType, setRuleType] = useState('UNIT_RATE');
  // originalMethod is preserved verbatim — never re-derived — to prevent
  // calculation_method downgrade (e.g. ot_multiplier → unit_multiplier) on save.
  const [originalMethod, setOriginalMethod] = useState('');
  const [fieldValues, setFieldValues] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open && rule) {
      setRuleName(rule.name);
      const def = rule.rule_definition_json ?? {};
      const method = String(def.calculation_method ?? '');
      setOriginalMethod(method);
      setRuleType(METHOD_TO_RULE_TYPE[method] ?? 'UNIT_RATE');
      const initial: Record<string, string> = {};
      for (const [k, v] of Object.entries(def)) {
        if (k !== 'calculation_method') initial[k] = String(v ?? '');
      }
      setFieldValues(initial);
      setError(null);
    }
  }, [open, rule]);

  function setField(key: string, val: string) {
    setFieldValues((prev) => ({ ...prev, [key]: val }));
  }

  function buildDefinition(): Record<string, unknown> {
    const def: Record<string, unknown> = { calculation_method: originalMethod };
    for (const [k, v] of Object.entries(fieldValues)) {
      const n = parseFloat(v);
      def[k] = isNaN(n) ? v : n;
    }
    return def;
  }

  async function handleSave() {
    if (!rule) return;
    if (!ruleName.trim()) { setError('Rule name is required.'); return; }
    setSaving(true);
    setError(null);
    try {
      await workspaceApi.updatePayrollRule(workspaceId, rule.rule_id, {
        rule_name: ruleName.trim(),
        rule_definition_json: buildDefinition(),
      });
      onSaved();
      onClose();
    } catch (e) {
      setError(extractError(e));
    } finally {
      setSaving(false);
    }
  }

  const methodLabel = originalMethod.replace(/_/g, ' ');

  return (
    <SlideOver
      open={open}
      onClose={onClose}
      title={rule ? `Edit Rule — ${rule.name}` : 'Edit Rule'}
      footer={
        <div className="flex justify-end gap-3 w-full">
          <Btn variant="secondary" size="md" onClick={onClose}>Cancel</Btn>
          <Btn variant="primary" size="md" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving…' : 'Save Changes →'}
          </Btn>
        </div>
      }
    >
      <div className="space-y-4">
        {error && <AlertBanner variant="error" description={error} />}
        <TextInput
          label="Rule Name"
          required
          value={ruleName}
          onChange={(e) => setRuleName(e.target.value)}
          placeholder="e.g. Overtime — Weekday"
        />
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Calculation Method</p>
          <p className="text-sm text-gray-700 font-mono">{methodLabel || '—'}</p>
          <p className="text-xs text-gray-400 mt-0.5">Method cannot be changed. Delete and recreate the rule to change it.</p>
        </div>
        <RuleFields ruleType={ruleType} originalMethod={originalMethod} values={fieldValues} onChange={setField} rateCodes={rateCodes} />
      </div>
    </SlideOver>
  );
}

// ── Update Config SlideOver (existing Excel upload flow) ──────────────────────

function UpdateConfigSlideOver({
  open,
  workspaceId,
  onClose,
  onUpdated,
}: {
  open: boolean;
  workspaceId: string;
  onClose: () => void;
  onUpdated: () => void;
}) {
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  function handleClose() { setSuccessMsg(null); setErrorMsg(null); onClose(); }

  async function handleConfigParsed(parsedConfig: WsConfig) {
    setSaving(true);
    setSuccessMsg(null);
    setErrorMsg(null);
    try {
      const res = await api.post<{ status: string; message: string }>(
        '/onboarding/commit',
        { ...parsedConfig, workspace_id: workspaceId },
      );
      setSuccessMsg(res.message || 'Configuration updated successfully.');
      onUpdated();
    } catch (e: unknown) {
      setErrorMsg(e instanceof Error ? e.message : 'Failed to update configuration.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <SlideOver
      open={open}
      onClose={handleClose}
      title="Update Configuration"
      description="Upload a workspace config Excel to update salary definitions, grades, or component settings. Existing records are updated — nothing is deleted."
      footer={<Btn type="button" variant="secondary" size="md" onClick={handleClose}>Close</Btn>}
    >
      <div className="space-y-4">
        {saving && <p className="text-xs text-gray-500">Committing changes…</p>}
        {successMsg && <AlertBanner variant="success" description={successMsg} />}
        {errorMsg && <AlertBanner variant="error" description={errorMsg} />}
        <WorkspaceExcelUpload workspaceId={workspaceId} onConfigParsed={handleConfigParsed} />
      </div>
    </SlideOver>
  );
}

// ── Salary Def ExpandableRow ──────────────────────────────────────────────────

function SalaryDefRow({
  sd,
  onEdit,
}: {
  sd: SalaryDefinition;
  onEdit: (sd: SalaryDefinition) => void;
}) {
  const [open, setOpen] = useState(false);
  return (
    <div style={{ borderRadius: 'var(--radius-card)' }} className="border border-gray-200">
      <div className="flex items-center px-4 py-3 hover:bg-gray-50 transition-colors">
        <button
          onClick={() => setOpen((v) => !v)}
          className="flex-1 flex items-center gap-3 text-left"
        >
          <span className="text-sm font-semibold text-gray-800">{sd.name}</span>
          <span className="text-xs font-mono text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">{sd.code}</span>
          <span className="text-xs text-gray-400">{sd.components.length} component{sd.components.length !== 1 ? 's' : ''}</span>
          <svg
            className={`w-4 h-4 text-gray-400 shrink-0 transition-transform duration-200 ml-auto ${open ? 'rotate-180' : ''}`}
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        <RowEditBtn label={sd.name} onClick={() => onEdit(sd)} />
      </div>
      <ExpandableRow open={open}>
        <div className="px-4 pb-4">
          {sd.components.length > 0 ? (
            <table className="w-full text-sm mt-2">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="text-left text-[11px] font-semibold text-gray-500 uppercase tracking-wide pb-2 pr-4">Component</th>
                  <th className="text-right text-[11px] font-semibold text-gray-500 uppercase tracking-wide pb-2">Amount (₦)</th>
                </tr>
              </thead>
              <tbody>
                {sd.components.map((c) => (
                  <tr key={c.component_name} className="border-b border-gray-50">
                    <td className="py-1.5 pr-4 text-gray-700 font-mono text-xs">{c.component_name}</td>
                    <td className="py-1.5 text-gray-700 text-sm text-right">
                      {c.amount.toLocaleString('en-NG', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-xs text-gray-400">No components defined.</p>
          )}
        </div>
      </ExpandableRow>
    </div>
  );
}

// ── Add Salary Definition SlideOver ──────────────────────────────────────────

const MANDATORY_COMPONENTS_ADD = new Set(['BASIC', 'HOUSING', 'TRANSPORT']);

function AddSalaryDefSlideOver({
  open,
  workspaceId,
  onClose,
  onSaved,
}: {
  open: boolean;
  workspaceId: string;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [name, setName] = useState('');
  const [code, setCode] = useState('');
  const [components, setComponents] = useState([
    { component_name: 'BASIC', amount: '' },
    { component_name: 'HOUSING', amount: '' },
    { component_name: 'TRANSPORT', amount: '' },
  ]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      setName('');
      setCode('');
      setComponents([
        { component_name: 'BASIC', amount: '' },
        { component_name: 'HOUSING', amount: '' },
        { component_name: 'TRANSPORT', amount: '' },
      ]);
      setError(null);
    }
  }, [open]);

  function updateComponent(idx: number, field: 'component_name' | 'amount', val: string) {
    setComponents((prev) => prev.map((c, i) => i === idx ? { ...c, [field]: field === 'component_name' ? val.toUpperCase() : val } : c));
  }

  function addComponentRow() {
    setComponents((prev) => [...prev, { component_name: '', amount: '' }]);
  }

  function removeComponentRow(idx: number) {
    setComponents((prev) => prev.filter((_, i) => i !== idx));
  }

  async function handleSave() {
    const codes = components.map((c) => c.component_name);
    const duplicate = codes.find((c, i) => codes.indexOf(c) !== i);
    if (duplicate) {
      setError(`Component code ${duplicate} is already in this definition.`);
      return;
    }
    setSaving(true);
    setError(null);
    const components_jsonb: Record<string, { amount: number }> = {};
    for (const c of components) {
      components_jsonb[c.component_name] = { amount: parseFloat(c.amount) };
    }
    try {
      await workspaceApi.createSalaryDefinition(workspaceId, { name, components_jsonb });
      onSaved();
      onClose();
    } catch (e) {
      setError(extractError(e));
    } finally {
      setSaving(false);
    }
  }

  return (
    <SlideOver
      open={open}
      onClose={onClose}
      title="Add Salary Definition"
      footer={
        <div className="flex justify-end gap-3 w-full">
          <Btn variant="secondary" size="md" onClick={onClose}>Cancel</Btn>
          <Btn variant="primary" size="md" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving…' : 'Create →'}
          </Btn>
        </div>
      }
    >
      <div className="space-y-4">
        {error && <AlertBanner variant="error" description={error} />}
        <TextInput
          label="Name"
          required
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g. Senior Staff"
        />
        <TextInput
          label="Code"
          required
          value={code}
          onChange={(e) => setCode(e.target.value.toUpperCase())}
          placeholder="e.g. SENIOR"
          className="font-mono"
          hint="Unique identifier used in employee contracts."
        />
        <div>
          <p className="text-sm font-medium text-gray-700 mb-2">Components</p>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100">
                <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide pb-2 pr-2">Code</th>
                <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide pb-2">Amount (₦)</th>
                <th className="w-8" />
              </tr>
            </thead>
            <tbody>
              {components.map((c, idx) => {
                const isMandatory = MANDATORY_COMPONENTS_ADD.has(c.component_name);
                return (
                  <tr key={idx} className="border-b border-gray-50">
                    <td className="py-2 pr-2">
                      {isMandatory ? (
                        <span className="font-mono text-xs text-gray-700">{c.component_name}</span>
                      ) : (
                        <input
                          value={c.component_name}
                          onChange={(e) => updateComponent(idx, 'component_name', e.target.value)}
                          className="w-full border border-gray-300 rounded px-2 py-1 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-brand"
                          placeholder="CODE"
                          aria-label="Component code"
                        />
                      )}
                    </td>
                    <td className="py-2 pr-2">
                      <input
                        type="number"
                        min="0.01"
                        step="0.01"
                        value={c.amount}
                        onChange={(e) => updateComponent(idx, 'amount', e.target.value)}
                        className="w-full border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-brand"
                        placeholder="0.00"
                        aria-label={`Amount for ${c.component_name}`}
                      />
                    </td>
                    <td className="py-2 text-center">
                      {!isMandatory && (
                        <button
                          type="button"
                          onClick={() => removeComponentRow(idx)}
                          className="text-gray-400 hover:text-red-500 transition-colors"
                          aria-label="Remove component"
                        >
                          <TrashIcon />
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          <button
            type="button"
            onClick={addComponentRow}
            className="mt-2 text-xs text-brand hover:underline"
          >
            + Add component
          </button>
        </div>
      </div>
    </SlideOver>
  );
}

// ── Edit Payroll Config SlideOver ─────────────────────────────────────────────

function EditPayrollConfigSlideOver({
  open,
  workspaceId,
  current,
  rateCodes,
  onClose,
  onSaved,
}: {
  open: boolean;
  workspaceId: string;
  current: WorkspacePayrollConfig | null;
  rateCodes: RateCode[];
  onClose: () => void;
  onSaved: () => void;
}) {
  const [phMode, setPhMode] = useState('AUTOMATIC');
  const [phRateCode, setPhRateCode] = useState('OT001');
  const [satRule, setSatRule] = useState('PH_TAKES_PRECEDENCE');
  const [sunRule, setSunRule] = useState('PH_TAKES_PRECEDENCE');
  const [d3Rule, setD3Rule] = useState('LEAVE_ABSORBS_PH');
  const [d4Rule, setD4Rule] = useState('ABSENT_IS_DEDUCTIBLE');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open && current) {
      setPhMode(current.ph_mode);
      setPhRateCode(current.ph_rate_code ?? 'OT001');
      setSatRule(current.saturday_ph_rule);
      setSunRule(current.sunday_ph_rule);
      setD3Rule(current.d3_leave_overlap_rule ?? 'LEAVE_ABSORBS_PH');
      setD4Rule(current.d4_absence_rule ?? 'ABSENT_IS_DEDUCTIBLE');
      setError(null);
    }
  }, [open, current]);

  async function handleSave() {
    setSaving(true);
    setError(null);
    try {
      await workspaceApi.upsertPayrollConfig(workspaceId, {
        ph_mode: phMode as WorkspacePayrollConfig['ph_mode'],
        ph_rate_code: phRateCode,
        saturday_ph_rule: satRule as WorkspacePayrollConfig['saturday_ph_rule'],
        sunday_ph_rule: sunRule as WorkspacePayrollConfig['sunday_ph_rule'],
        d3_leave_overlap_rule: d3Rule as WorkspacePayrollConfig['d3_leave_overlap_rule'],
        d4_absence_rule: d4Rule as WorkspacePayrollConfig['d4_absence_rule'],
        effective_from: new Date().toISOString().slice(0, 10),
      });
      onSaved();
      onClose();
    } catch (e) {
      setError(extractError(e));
    } finally {
      setSaving(false);
    }
  }

  return (
    <SlideOver
      open={open}
      onClose={onClose}
      title="Edit OT & Holiday Behaviour"
      footer={
        <div className="flex justify-end gap-3 w-full">
          <Btn variant="secondary" size="md" onClick={onClose}>Cancel</Btn>
          <Btn variant="primary" size="md" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving…' : 'Save Changes →'}
          </Btn>
        </div>
      }
    >
      <div className="space-y-4">
        {error && <AlertBanner variant="error" description={error} />}
        <SelectField label="PH Mode" value={phMode} onChange={setPhMode}
          hint="Automatic mode calculates PH OT from the calendar. Manual requires hours as inputs.">
          <option value="AUTOMATIC">Automatic</option>
          <option value="FILE_BASED">Manual (file-based)</option>
        </SelectField>
        <SelectField
          label="PH Rate Code"
          value={phRateCode}
          onChange={setPhRateCode}
          hint="Rate code applied to public holiday overtime pay."
        >
          {rateCodes.map((rc) => (
            <option key={rc.code} value={rc.code}>
              {rc.code} — ×{rc.multiplier} {rc.unit}
            </option>
          ))}
        </SelectField>
        <SelectField label="Saturday PH Rule" value={satRule} onChange={setSatRule}>
          <option value="PH_TAKES_PRECEDENCE">PH takes precedence</option>
          <option value="DAY_OF_WEEK_TAKES_PRECEDENCE">Day of week takes precedence</option>
        </SelectField>
        <SelectField label="Sunday PH Rule" value={sunRule} onChange={setSunRule}>
          <option value="PH_TAKES_PRECEDENCE">PH takes precedence</option>
          <option value="DAY_OF_WEEK_TAKES_PRECEDENCE">Day of week takes precedence</option>
        </SelectField>
        <SelectField label="Leave Overlap Rule" value={d3Rule} onChange={setD3Rule}>
          <option value="LEAVE_ABSORBS_PH">Leave absorbs PH</option>
        </SelectField>
        <SelectField label="Absence Rule" value={d4Rule} onChange={setD4Rule}>
          <option value="ABSENT_IS_DEDUCTIBLE">Absent is deductible</option>
          <option value="PH_EXCUSES_ABSENCE">PH excuses absence</option>
        </SelectField>
      </div>
    </SlideOver>
  );
}

// ── Add Rate Code SlideOver ───────────────────────────────────────────────────

function AddRateCodeSlideOver({
  open,
  workspaceId,
  onClose,
  onSaved,
}: {
  open: boolean;
  workspaceId: string;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [code, setCode] = useState('');
  const [multiplier, setMultiplier] = useState('');
  const [unit, setUnit] = useState('hour');
  const [base, setBase] = useState('basic_hourly');
  const [description, setDescription] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      setCode(''); setMultiplier(''); setUnit('hours'); setBase('basic_hourly'); setDescription(''); setError(null);
    }
  }, [open]);

  async function handleSave() {
    setSaving(true);
    setError(null);
    try {
      await workspaceApi.addRateCode(workspaceId, {
        code,
        multiplier: parseFloat(multiplier),
        unit,
        base,
        description: description || undefined,
      });
      onSaved();
      onClose();
    } catch (e) {
      setError(extractError(e));
    } finally {
      setSaving(false);
    }
  }

  return (
    <SlideOver
      open={open}
      onClose={onClose}
      title="Add Rate Code"
      footer={
        <div className="flex justify-end gap-3 w-full">
          <Btn variant="secondary" size="md" onClick={onClose}>Cancel</Btn>
          <Btn variant="primary" size="md" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving…' : 'Add Rate Code →'}
          </Btn>
        </div>
      }
    >
      <div className="space-y-4">
        {error && <AlertBanner variant="error" description={error} />}
        <TextInput
          label="Code"
          required
          value={code}
          onChange={(e) => setCode(e.target.value.toUpperCase())}
          placeholder="e.g. SHIFT2"
          className="font-mono"
        />
        <NumberInput
          label="Multiplier"
          required
          value={multiplier}
          onChange={(e) => setMultiplier(e.target.value)}
          hint="e.g. 1.5 for time-and-a-half"
        />
        <SelectField label="Unit" value={unit} onChange={setUnit}>
          <option value="hour">Hour</option>
          <option value="day">Day</option>
        </SelectField>
        <SelectField label="Base" value={base} onChange={setBase}>
          <option value="basic_hourly">Basic hourly</option>
          <option value="basic_daily">Basic daily</option>
        </SelectField>
        <TextInput
          label="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Optional description"
        />
      </div>
    </SlideOver>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────

export function WorkspaceConfig() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const { workspace } = useWorkspaceContext();

  const [config, setConfig] = useState<WorkspaceConfiguration | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [platformComponents, setPlatformComponents] = useState<PlatformComponent[]>([]);
  const [activeTab, setActiveTab] = useState<'workforce' | 'earnings' | 'deductions' | 'rules' | 'ot-holidays'>('workforce');
  const [phConfig, setPhConfig] = useState<WorkspacePayrollConfig | null>(null);
  const [rateCodes, setRateCodes] = useState<RateCode[]>([]);

  // SlideOver / dialog state
  const [updateOpen, setUpdateOpen] = useState(false);
  const [editPayCycleOpen, setEditPayCycleOpen] = useState(false);
  const [addGradeOpen, setAddGradeOpen] = useState(false);
  const [editGrade, setEditGrade] = useState<Grade | null>(null);
  const [addDesignationOpen, setAddDesignationOpen] = useState(false);
  const [editDesignation, setEditDesignation] = useState<Designation | null>(null);
  const [editSalaryDef, setEditSalaryDef] = useState<SalaryDefinition | null>(null);
  const [addSalaryDefOpen, setAddSalaryDefOpen] = useState(false);
  const [editOverride, setEditOverride] = useState<ComponentOverride | null>(null);
  const [addOverrideOpen, setAddOverrideOpen] = useState(false);
  const [addRuleOpen, setAddRuleOpen] = useState(false);
  const [addEarningOpen, setAddEarningOpen] = useState(false);
  const [ruleToToggle, setRuleToToggle] = useState<PayrollRule | null>(null);
  const [ruleToggling, setRuleToggling] = useState(false);
  const [ruleToDelete, setRuleToDelete] = useState<PayrollRule | null>(null);
  const [ruleDeleting, setRuleDeleting] = useState(false);
  const [editRule, setEditRule] = useState<PayrollRule | null>(null);
  const [ruleChangeBanner, setRuleChangeBanner] = useState(false);
  const [ruleToggleError, setRuleToggleError] = useState<string | null>(null);
  const [editPhConfigOpen, setEditPhConfigOpen] = useState(false);
  const [addRateCodeOpen, setAddRateCodeOpen] = useState(false);

  function loadConfig() {
    if (!workspaceId) return;
    setLoading(true);
    setError(null);
    workspaceApi
      .getConfiguration(workspaceId)
      .then(setConfig)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : 'Failed to load'))
      .finally(() => setLoading(false));
  }

  function loadPhConfig() {
    if (!workspaceId) return;
    workspaceApi.getPayrollConfig(workspaceId).then(setPhConfig).catch(() => {});
  }

  function loadRateCodes() {
    if (!workspaceId) return;
    workspaceApi.getRateCodes(workspaceId).then(setRateCodes).catch(() => {});
  }

  useEffect(() => { loadConfig(); loadPhConfig(); loadRateCodes(); }, [workspaceId]);

  useEffect(() => {
    if (!workspaceId) return;
    workspaceApi.getPlatformComponents(workspaceId)
      .then(setPlatformComponents)
      .catch(() => { /* non-critical — labels fall back to component_code */ });
  }, [workspaceId]);

  const componentLabel = (code: string) =>
    platformComponents.find((c) => c.component_code === code)?.label ?? code;

  async function handleRuleToggleConfirm() {
    if (!workspaceId || !ruleToToggle) return;
    setRuleToggling(true);
    setRuleToggleError(null);
    const newActive = !ruleToToggle.is_active;
    // Optimistic update
    setConfig((prev) => prev ? {
      ...prev,
      payroll_rules: prev.payroll_rules.map((r) =>
        r.rule_id === ruleToToggle.rule_id ? { ...r, is_active: newActive } : r
      ),
    } : prev);
    const toggled = ruleToToggle;
    setRuleToToggle(null);
    try {
      await workspaceApi.updatePayrollRule(workspaceId, toggled.rule_id, { is_active: newActive });
      setRuleChangeBanner(true);
    } catch (e) {
      // Rollback
      setConfig((prev) => prev ? {
        ...prev,
        payroll_rules: prev.payroll_rules.map((r) =>
          r.rule_id === toggled.rule_id ? { ...r, is_active: !newActive } : r
        ),
      } : prev);
      setRuleToggleError(extractError(e));
    } finally {
      setRuleToggling(false);
    }
  }

  async function handleRuleDeleteConfirm() {
    if (!workspaceId || !ruleToDelete) return;
    setRuleDeleting(true);
    const deleted = ruleToDelete;
    setRuleToDelete(null);
    try {
      await workspaceApi.deletePayrollRule(workspaceId, deleted.rule_id);
      setConfig((prev) => prev ? {
        ...prev,
        payroll_rules: prev.payroll_rules.filter((r) => r.rule_id !== deleted.rule_id),
      } : prev);
    } catch (e) {
      setRuleToggleError(extractError(e));
    } finally {
      setRuleDeleting(false);
    }
  }

  if (!workspaceId) return null;

  return (
    <div className="max-w-4xl">
      <ContentHeader
        title="Configuration"
        subtitle={config ? config.workspace.name : 'Loading…'}
        back={
          <Breadcrumb items={[
            { label: 'Bureau Dashboard', to: '/' },
            { label: workspace?.name ?? '…', to: `/workspaces/${workspaceId}` },
            { label: 'Configuration' },
          ]} />
        }
        action={
          <Btn variant="secondary" size="md" onClick={() => setUpdateOpen(true)}>
            Re-upload Config
          </Btn>
        }
      />

      {error && <AlertBanner variant="error" description={error} className="mb-4" />}

      {loading ? (
        <div className="space-y-4 animate-pulse">
          {[1, 2, 3].map((i) => <div key={i} className="h-32 bg-gray-200 rounded-lg" />)}
        </div>
      ) : config && (
        <div className="space-y-5">

          {/* Workspace Info — always visible */}
          <Card>
            <SectionHeader label="Workspace" />
            <dl className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <Dt label="Name" value={config.workspace.name} />
              <Dt label="Country" value={config.workspace.country_code} />
              <Dt label="Currency" value={config.workspace.currency_code} />
              <div>
                <dt className="text-gray-500 text-xs font-medium mb-1">Status</dt>
                <dd><StatusBadge status={config.workspace.status} /></dd>
              </div>
            </dl>
          </Card>

          {/* Pay Cycle — always visible */}
          <Card>
            <SectionHeader label="Pay Cycle">
              <Btn variant="secondary" size="sm" onClick={() => setEditPayCycleOpen(true)}>Edit</Btn>
            </SectionHeader>
            {config.pay_cycle ? (
              <dl className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <Dt label="Frequency" value={config.pay_cycle.frequency} />
                <Dt label="Run Day" value={String(config.pay_cycle.run_day)} />
                <Dt label="Cutoff Day" value={String(config.pay_cycle.cutoff_day)} />
                <Dt label="Payment Day" value={String(config.pay_cycle.payment_day)} />
              </dl>
            ) : (
              <p className="text-sm text-gray-400">No pay cycle defined.</p>
            )}
          </Card>

          {/* Rule change banners — above tabs */}
          {ruleToggleError && (
            <AlertBanner variant="error" description={ruleToggleError} />
          )}
          {ruleChangeBanner && (
            <AlertBanner
              variant="info"
              description={
                <span>
                  Rule changes take effect only after the rule set is re-published.{' '}
                  <Link
                    to={`/workspaces/${workspaceId}/setup`}
                    className="font-medium underline hover:no-underline"
                  >
                    Go to Workspace Setup →
                  </Link>
                </span>
              }
              dismissible
              onDismiss={() => setRuleChangeBanner(false)}
            />
          )}

          {/* Tab bar */}
          <div className="border-b border-gray-200">
            <nav className="flex gap-0" aria-label="Configuration tabs">
              {([
                { key: 'workforce', label: 'Workforce' },
                { key: 'earnings', label: 'Earnings' },
                { key: 'deductions', label: 'Deductions' },
                { key: 'rules', label: 'Payroll Rules' },
                { key: 'ot-holidays', label: 'OT & Holidays' },
              ] as const).map((tab) => (
                <button
                  key={tab.key}
                  type="button"
                  onClick={() => setActiveTab(tab.key)}
                  className={[
                    'px-4 py-2.5 text-sm font-medium border-b-2 transition-colors whitespace-nowrap',
                    activeTab === tab.key
                      ? 'border-brand text-brand'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                  ].join(' ')}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Workforce tab */}
          {activeTab === 'workforce' && (
            <div className="space-y-5">
              {/* Grades */}
              <Card>
                <SectionHeader label="Grades" count={config.grades.length}>
                  <Btn variant="secondary" size="sm" onClick={() => setAddGradeOpen(true)}>Add Grade</Btn>
                </SectionHeader>
                {config.grades.length > 0 ? (
                  <table className="w-full text-sm mt-2">
                    <thead>
                      <tr className="border-b border-gray-100">
                        <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide pb-2 pr-4">Code</th>
                        <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide pb-2">Description</th>
                        <th className="w-12" />
                      </tr>
                    </thead>
                    <tbody>
                      {config.grades.map((g) => (
                        <tr key={g.code} className="border-b border-gray-50">
                          <td className="py-2 pr-4 text-xs font-mono text-gray-700">{g.code}</td>
                          <td className="py-2 text-gray-500 text-sm">{g.description ?? '—'}</td>
                          <td className="py-2 text-right">
                            <RowEditBtn label={g.code} onClick={() => setEditGrade(g)} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <p className="text-sm text-gray-400">No grades defined.</p>
                )}
              </Card>

              {/* Designations */}
              <Card>
                <SectionHeader label="Designations" count={config.designations.length}>
                  <Btn variant="secondary" size="sm" onClick={() => setAddDesignationOpen(true)}>Add Designation</Btn>
                </SectionHeader>
                {config.designations.length > 0 ? (
                  <table className="w-full text-sm mt-2">
                    <thead>
                      <tr className="border-b border-gray-100">
                        <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide pb-2 pr-4">Code</th>
                        <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide pb-2">Description</th>
                        <th className="w-12" />
                      </tr>
                    </thead>
                    <tbody>
                      {config.designations.map((d) => (
                        <tr key={d.code} className="border-b border-gray-50">
                          <td className="py-2 pr-4 text-xs font-mono text-gray-700">{d.code}</td>
                          <td className="py-2 text-gray-500 text-sm">{d.description ?? '—'}</td>
                          <td className="py-2 text-right">
                            <RowEditBtn label={d.code} onClick={() => setEditDesignation(d)} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <p className="text-sm text-gray-400">No designations defined.</p>
                )}
              </Card>

              {/* Salary Definitions */}
              <Card>
                <SectionHeader label="Salary Definitions" count={config.salary_definitions.length}>
                  <Btn variant="secondary" size="sm" onClick={() => setAddSalaryDefOpen(true)}>Add Salary Definition</Btn>
                </SectionHeader>
                {config.salary_definitions.length > 0 ? (
                  <div className="space-y-2">
                    {config.salary_definitions.map((sd) => (
                      <SalaryDefRow key={sd.salary_definition_id} sd={sd} onEdit={setEditSalaryDef} />
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-6">
                    <p className="text-sm text-gray-400 mb-3">No salary definitions. Upload a configuration file to get started.</p>
                    <Btn variant="secondary" size="sm" onClick={() => setUpdateOpen(true)}>Update Config</Btn>
                  </div>
                )}
              </Card>
            </div>
          )}

          {/* Earnings tab */}
          {activeTab === 'earnings' && (
            <div className="space-y-5">
              {/* Platform salary components */}
              <Card>
                <SectionHeader label="Salary Components">
                  <span className="text-xs text-gray-400 italic">Configured via salary definitions</span>
                </SectionHeader>
                {(() => {
                  const salaryComps = platformComponents.filter(
                    (pc) => pc.component_class === 'salary_component' || pc.component_class === 'earning',
                  );
                  if (salaryComps.length === 0) {
                    return <p className="text-sm text-gray-400">No salary components found.</p>;
                  }
                  return (
                    <div className="space-y-1">
                      {salaryComps.map((pc) => {
                        const override = config.component_overrides.find(
                          (co) => co.component_name === pc.component_code,
                        );
                        return (
                          <div
                            key={pc.component_code}
                            className="flex items-center justify-between py-2 px-3 rounded bg-gray-50 border border-gray-100"
                          >
                            <div>
                              <span className="text-sm text-gray-800 font-medium">{pc.label}</span>
                              <span className="text-xs text-gray-400 font-mono ml-2">{pc.component_code}</span>
                            </div>
                            <div className="flex items-center gap-3">
                              {override ? (
                                <>
                                  {override.proration_strategy && (
                                    <span className="text-xs text-gray-400">
                                      {override.proration_strategy.replace(/_/g, ' ')}
                                    </span>
                                  )}
                                  <StatusBadge status={override.is_active ? 'ACTIVE' : 'INACTIVE'} size="sm" />
                                  <RowEditBtn label={pc.component_code} onClick={() => setEditOverride(override)} />
                                </>
                              ) : (
                                <span className="text-xs text-gray-400 italic">Platform default</span>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  );
                })()}
              </Card>

              {/* Workspace custom earning components */}
              <Card>
                <SectionHeader
                  label="Custom Allowances"
                  count={config.payroll_rules.filter((r) => r.rule_type === 'EARNING').length}
                >
                  <Btn variant="secondary" size="sm" onClick={() => setAddEarningOpen(true)}>Add Component</Btn>
                </SectionHeader>
                {config.payroll_rules.filter((r) => r.rule_type === 'EARNING').length > 0 ? (
                  <div className="space-y-1">
                    {config.payroll_rules
                      .filter((r) => r.rule_type === 'EARNING')
                      .map((r) => {
                        const def = r.rule_definition_json ?? {};
                        const amount = def.amount != null ? `₦${Number(def.amount).toLocaleString()}` : null;
                        return (
                          <div
                            key={r.rule_id}
                            className="flex items-center justify-between py-2 px-3 rounded bg-gray-50 border border-gray-100"
                          >
                            <div>
                              <span className="text-sm text-gray-800 font-medium">{r.name}</span>
                              {amount && (
                                <span className="text-xs text-gray-500 ml-2">{amount}/month</span>
                              )}
                              <span
                                className="text-xs text-brand ml-2 italic"
                                title="This component is also listed under the Payroll Rules tab"
                              >
                                also in Payroll Rules
                              </span>
                            </div>
                            <div className="flex items-center gap-2">
                              <StatusBadge status={r.is_active ? 'ACTIVE' : 'INACTIVE'} size="sm" />
                              <RowEditBtn label={r.name} onClick={() => setEditRule(r)} />
                              <button
                                type="button"
                                onClick={() => setRuleToDelete(r)}
                                className="text-gray-400 hover:text-red-500 transition-colors"
                                aria-label={`Delete ${r.name}`}
                              >
                                <TrashIcon />
                              </button>
                            </div>
                          </div>
                        );
                      })}
                  </div>
                ) : (
                  <div className="text-center py-6">
                    <p className="text-sm text-gray-400 mb-3">
                      No custom allowances yet. Add components like Meal Allowance or Car Allowance.
                    </p>
                    <Btn variant="secondary" size="sm" onClick={() => setAddEarningOpen(true)}>Add Component</Btn>
                  </div>
                )}
              </Card>
            </div>
          )}

          {/* Payroll Rules tab */}
          {activeTab === 'rules' && (
            <div className="space-y-5">
              <Card>
                <SectionHeader label="Payroll Rules" count={config.payroll_rules.length}>
                  <Btn variant="secondary" size="sm" onClick={() => setAddRuleOpen(true)}>Add Rule</Btn>
                </SectionHeader>
                {config.payroll_rules.length > 0 ? (
                  <table className="w-full text-sm mt-2">
                    <thead>
                      <tr className="border-b border-gray-100">
                        <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide pb-2 pr-4">Name</th>
                        <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide pb-2 pr-4">Type</th>
                        <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide pb-2 pr-4 w-28">
                          Status
                          <span className="ml-1 text-gray-400 font-normal normal-case" title="Current activation state. Historical state per run is visible in the Run Trace.">ⓘ</span>
                        </th>
                        <th className="w-28" />
                      </tr>
                    </thead>
                    <tbody>
                      {config.payroll_rules.map((r) => (
                        <tr key={r.rule_id} className="border-b border-gray-50">
                          <td className="py-2 pr-4 text-gray-800 text-sm font-medium">{r.name}</td>
                          <td className="py-2 pr-4 text-gray-500 text-sm">{r.rule_type}</td>
                          <td className="py-2 pr-4 w-28">
                            <StatusBadge status={r.is_active ? 'ACTIVE' : 'INACTIVE'} size="sm" />
                          </td>
                          <td className="py-2 text-right">
                            <div className="flex items-center justify-end gap-2">
                              <RowEditBtn label={r.name} onClick={() => setEditRule(r)} />
                              <Btn
                                variant="secondary"
                                size="sm"
                                className="min-w-[90px]"
                                onClick={() => setRuleToToggle(r)}
                                disabled={ruleToggling}
                              >
                                {r.is_active ? 'Deactivate' : 'Activate'}
                              </Btn>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <div className="text-center py-6">
                    <p className="text-sm text-gray-400 mb-3">No payroll rules defined for this workspace.</p>
                    <div className="flex justify-center gap-2">
                      <Btn variant="primary" size="sm" onClick={() => setAddRuleOpen(true)}>Add Rule</Btn>
                      <Btn variant="secondary" size="sm" onClick={() => setUpdateOpen(true)}>Update Config</Btn>
                    </div>
                  </div>
                )}
              </Card>
            </div>
          )}

          {/* OT & Holidays tab */}
          {activeTab === 'ot-holidays' && (
            <div className="space-y-5">
              {/* OT & Holiday Behaviour */}
              <Card>
                <SectionHeader label="OT & Holiday Behaviour">
                  <Btn variant="secondary" size="sm" onClick={() => setEditPhConfigOpen(true)}>Edit</Btn>
                </SectionHeader>
                {phConfig ? (
                  <>
                    <dl className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                      <div>
                        <dt className="text-gray-500 text-xs font-medium mb-1">PH Mode</dt>
                        <dd><StatusBadge status={phConfig.ph_mode} size="sm" /></dd>
                      </div>
                      <Dt label="PH Rate Code" value={phConfig.ph_rate_code ?? '—'} />
                      <Dt label="Saturday PH" value={phConfig.saturday_ph_rule.replace(/_/g, ' ')} />
                    </dl>
                    <dl className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-gray-100">
                      <Dt label="Sunday PH" value={phConfig.sunday_ph_rule.replace(/_/g, ' ')} />
                      <Dt label="Leave Overlap" value={phConfig.d3_leave_overlap_rule?.replace(/_/g, ' ') ?? '—'} />
                      <Dt label="Absence Rule" value={phConfig.d4_absence_rule?.replace(/_/g, ' ') ?? '—'} />
                    </dl>
                  </>
                ) : (
                  <p className="text-sm text-gray-400">No payroll behaviour configured. Defaults apply.</p>
                )}
              </Card>

              {/* Rate Code Registry */}
              <Card>
                <SectionHeader label="Rate Code Registry" />
                {/* Platform codes */}
                <div className="mb-4">
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
                    Platform Codes ({rateCodes.filter((r) => r.is_platform).length})
                  </p>
                  {rateCodes.filter((r) => r.is_platform).length > 0 ? (
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-gray-100">
                          <th className="text-left text-xs font-semibold text-gray-400 uppercase tracking-wide pb-2 w-20">Code</th>
                          <th className="text-right text-xs font-semibold text-gray-400 uppercase tracking-wide pb-2 w-14">×</th>
                          <th className="text-left text-xs font-semibold text-gray-400 uppercase tracking-wide pb-2 w-16 pl-2">Unit</th>
                          <th className="text-left text-xs font-semibold text-gray-400 uppercase tracking-wide pb-2 w-28 pl-2">Base</th>
                          <th className="text-left text-xs font-semibold text-gray-400 uppercase tracking-wide pb-2 pl-2">Description</th>
                        </tr>
                      </thead>
                      <tbody>
                        {rateCodes.filter((r) => r.is_platform).map((rc) => (
                          <tr key={rc.code} className="border-b border-gray-50">
                            <td className="py-2 w-20">
                              <span className="flex items-center gap-1 font-mono text-xs text-gray-400">
                                <LockSmIcon />{rc.code}
                              </span>
                            </td>
                            <td className="py-2 w-14 text-right tabular-nums text-xs text-gray-400">{rc.multiplier}</td>
                            <td className="py-2 w-16 text-xs text-gray-400 pl-2">{rc.unit}</td>
                            <td className="py-2 w-28 font-mono text-xs text-gray-400 pl-2">{rc.base}</td>
                            <td className="py-2 text-xs text-gray-400 pl-2 truncate" title={rc.description ?? ''}>{rc.description ?? '—'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="text-xs text-gray-400">No platform codes.</p>
                  )}
                </div>

                {/* Workspace codes */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
                      Your Codes ({rateCodes.filter((r) => !r.is_platform).length})
                    </p>
                    <Btn variant="secondary" size="sm" onClick={() => setAddRateCodeOpen(true)}>Add Rate Code</Btn>
                  </div>
                  {rateCodes.filter((r) => !r.is_platform).length > 0 ? (
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-gray-100">
                          <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide pb-2 w-20">Code</th>
                          <th className="text-right text-xs font-semibold text-gray-500 uppercase tracking-wide pb-2 w-14">×</th>
                          <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide pb-2 w-16 pl-2">Unit</th>
                          <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide pb-2 w-28 pl-2">Base</th>
                          <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide pb-2 pl-2">Description</th>
                          <th className="w-8" />
                        </tr>
                      </thead>
                      <tbody>
                        {rateCodes.filter((r) => !r.is_platform).map((rc) => (
                          <tr key={rc.code} className="border-b border-gray-50">
                            <td className="py-2 w-20 font-mono text-xs text-gray-700">{rc.code}</td>
                            <td className="py-2 w-14 text-right tabular-nums text-sm text-gray-700">{rc.multiplier}</td>
                            <td className="py-2 w-16 text-xs text-gray-500 pl-2">{rc.unit}</td>
                            <td className="py-2 w-28 font-mono text-xs text-gray-500 pl-2">{rc.base}</td>
                            <td className="py-2 text-xs text-gray-500 pl-2 truncate" title={rc.description ?? ''}>{rc.description ?? '—'}</td>
                            <td className="py-2 text-center w-8">
                              <button
                                type="button"
                                onClick={async () => {
                                  if (!workspaceId) return;
                                  try {
                                    await workspaceApi.deleteRateCode(workspaceId, rc.code);
                                    loadRateCodes();
                                  } catch { /* non-critical */ }
                                }}
                                className="text-gray-400 hover:text-red-500 transition-colors"
                                aria-label={`Delete rate code ${rc.code}`}
                              >
                                <TrashIcon />
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <div className="text-center py-4">
                      <p className="text-sm text-gray-400 mb-2">No custom rate codes. Platform codes apply.</p>
                      <Btn variant="secondary" size="sm" onClick={() => setAddRateCodeOpen(true)}>Add Rate Code</Btn>
                    </div>
                  )}
                </div>
              </Card>
            </div>
          )}

          {/* Deductions tab */}
          {activeTab === 'deductions' && (
            <div className="space-y-5">
              <Card>
                {(() => {
                  const DEDUCTION_CLASSES = ['statutory_deduction', 'pension_rule'];
                  const CLASS_LABEL: Record<string, string> = {
                    statutory_deduction: 'Statutory Deductions',
                    pension_rule: 'Pension',
                  };
                  const deductionComps = platformComponents.filter(
                    (pc) => DEDUCTION_CLASSES.includes(pc.component_class ?? ''),
                  );
                  const groups: Record<string, typeof platformComponents> = {};
                  for (const pc of deductionComps) {
                    const cls = pc.component_class ?? 'other';
                    if (!groups[cls]) groups[cls] = [];
                    groups[cls].push(pc);
                  }
                  return (
                    <>
                      <SectionHeader label="Statutory Components" count={deductionComps.length}>
                        <Btn variant="secondary" size="sm" onClick={() => setAddOverrideOpen(true)}>Add Override</Btn>
                      </SectionHeader>
                      {deductionComps.length > 0 ? (
                        <div className="space-y-5">
                          {Object.entries(groups).map(([cls, components]) => (
                            <div key={cls}>
                              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                                {CLASS_LABEL[cls] ?? cls.replace(/_/g, ' ')}
                              </p>
                              <div className="space-y-1">
                                {components.map((pc) => {
                                  const override = config.component_overrides.find(
                                    (co) => co.component_name === pc.component_code,
                                  );
                                  return (
                                    <div
                                      key={pc.component_code}
                                      className="flex items-center justify-between py-2 px-3 rounded bg-gray-50 border border-gray-100"
                                    >
                                      <div>
                                        <span className="text-sm text-gray-800 font-medium">{pc.label}</span>
                                        <span className="text-xs text-gray-400 font-mono ml-2">{pc.component_code}</span>
                                      </div>
                                      <div className="flex items-center gap-3">
                                        {override ? (
                                          <>
                                            {override.proration_strategy && (
                                              <span className="text-xs text-gray-400">
                                                {override.proration_strategy.replace(/_/g, ' ')}
                                              </span>
                                            )}
                                            <StatusBadge status={override.is_active ? 'ACTIVE' : 'INACTIVE'} size="sm" />
                                            <RowEditBtn label={pc.component_code} onClick={() => setEditOverride(override)} />
                                          </>
                                        ) : (
                                          <span className="text-xs text-gray-400 italic">Platform default</span>
                                        )}
                                      </div>
                                    </div>
                                  );
                                })}
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-6">
                          <p className="text-sm text-gray-400">No statutory components found for this workspace.</p>
                        </div>
                      )}
                    </>
                  );
                })()}
              </Card>
            </div>
          )}
        </div>
      )}

      {/* SlideOvers */}
      <UpdateConfigSlideOver
        open={updateOpen}
        workspaceId={workspaceId}
        onClose={() => setUpdateOpen(false)}
        onUpdated={loadConfig}
      />
      <EditPayCycleSlideOver
        open={editPayCycleOpen}
        workspaceId={workspaceId}
        current={config?.pay_cycle ?? null}
        onClose={() => setEditPayCycleOpen(false)}
        onSaved={loadConfig}
      />
      <AddGradeSlideOver
        open={addGradeOpen}
        workspaceId={workspaceId}
        onClose={() => setAddGradeOpen(false)}
        onSaved={loadConfig}
      />
      <EditGradeSlideOver
        open={editGrade !== null}
        workspaceId={workspaceId}
        grade={editGrade}
        onClose={() => setEditGrade(null)}
        onSaved={loadConfig}
      />
      <AddDesignationSlideOver
        open={addDesignationOpen}
        workspaceId={workspaceId}
        onClose={() => setAddDesignationOpen(false)}
        onSaved={loadConfig}
      />
      <EditDesignationSlideOver
        open={editDesignation !== null}
        workspaceId={workspaceId}
        designation={editDesignation}
        onClose={() => setEditDesignation(null)}
        onSaved={loadConfig}
      />
      <EditSalaryDefSlideOver
        open={editSalaryDef !== null}
        workspaceId={workspaceId}
        salaryDef={editSalaryDef}
        onClose={() => setEditSalaryDef(null)}
        onSaved={loadConfig}
      />
      <AddSalaryDefSlideOver
        open={addSalaryDefOpen}
        workspaceId={workspaceId}
        onClose={() => setAddSalaryDefOpen(false)}
        onSaved={loadConfig}
      />
      <EditPayrollConfigSlideOver
        open={editPhConfigOpen}
        workspaceId={workspaceId}
        current={phConfig}
        rateCodes={rateCodes}
        onClose={() => setEditPhConfigOpen(false)}
        onSaved={loadPhConfig}
      />
      <AddRateCodeSlideOver
        open={addRateCodeOpen}
        workspaceId={workspaceId}
        onClose={() => setAddRateCodeOpen(false)}
        onSaved={loadRateCodes}
      />
      <EditComponentOverrideSlideOver
        open={editOverride !== null}
        workspaceId={workspaceId}
        override={editOverride}
        onClose={() => setEditOverride(null)}
        onSaved={loadConfig}
      />
      <AddComponentOverrideSlideOver
        open={addOverrideOpen}
        workspaceId={workspaceId}
        onClose={() => setAddOverrideOpen(false)}
        onSaved={loadConfig}
      />
      <AddEarningComponentSlideOver
        open={addEarningOpen}
        workspaceId={workspaceId}
        onClose={() => setAddEarningOpen(false)}
        onSaved={loadConfig}
      />
      <AddPayrollRuleSlideOver
        open={addRuleOpen}
        workspaceId={workspaceId}
        rateCodes={rateCodes}
        onClose={() => setAddRuleOpen(false)}
        onSaved={loadConfig}
      />
      <EditPayrollRuleSlideOver
        open={editRule !== null}
        rule={editRule}
        workspaceId={workspaceId}
        rateCodes={rateCodes}
        onClose={() => setEditRule(null)}
        onSaved={loadConfig}
      />

      {/* Payroll Rule Toggle Confirm Dialog */}
      <ConfirmDialog
        open={ruleToToggle !== null}
        onClose={() => setRuleToToggle(null)}
        onConfirm={handleRuleToggleConfirm}
        title={ruleToToggle ? `${ruleToToggle.is_active ? 'Deactivate' : 'Activate'} Rule` : ''}
        body={ruleToToggle ? (
          <p className="text-sm text-gray-600">
            {ruleToToggle.is_active
              ? `"${ruleToToggle.name}" will no longer be applied in future payroll runs.`
              : `"${ruleToToggle.name}" will be applied in future payroll runs.`}
            {' '}Re-publish the rule set for this change to take effect.
          </p>
        ) : ''}
        confirmLabel={ruleToToggle?.is_active ? 'Deactivate Rule' : 'Activate Rule'}
        loading={ruleToggling}
      />

      {/* Earning Component Delete Confirm Dialog */}
      <ConfirmDialog
        open={ruleToDelete !== null}
        onClose={() => setRuleToDelete(null)}
        onConfirm={handleRuleDeleteConfirm}
        title="Delete Earning Component"
        body={ruleToDelete ? (
          <p className="text-sm text-gray-600">
            <strong>"{ruleToDelete.name}"</strong> will be permanently removed. Historical payroll runs are not affected — rule snapshots are preserved separately. This cannot be undone.
          </p>
        ) : ''}
        confirmLabel="Delete Component"
        loading={ruleDeleting}
      />
    </div>
  );
}
