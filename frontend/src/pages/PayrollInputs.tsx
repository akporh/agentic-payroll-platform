/**
 * S7 — Payroll Inputs (Input Inbox)
 *
 * Design decisions honoured:
 * DD-8  Framed as an "Inbox" — title "Payroll Inputs", pending count in subtitle
 * DD-5  Empty state has a specific action CTA
 * DD-6  Input code dropdown groups by category (EARNING / DEDUCTION / INFORMATION)
 * DD-3  Single primary action: "Add Input" opens a SlideOver (not inline form)
 *
 * Adaeze's mental model: she is clearing a to-do list before month-end.
 * The inbox framing maps directly to that. Each pending input is something
 * she has committed to include. The pending count tells her how much is ready.
 */

import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { payrollInputApi } from '../api/payrollInput';
import { workspaceApi } from '../api/workspace';
import { payrollApi } from '../api/payroll';
import type { PayrollInput, Employee } from '../types/payroll';
import {
  ContentHeader,
  SlideOver,
  Card,
  Btn,
  IconBtn,
  SearchableSelect,
  NumberInput,
  DateInput,
  AlertBanner,
  EmptyState,
  useToast,
  Breadcrumb,
} from '../design-system';
import { useWorkspaceContext } from '../context/WorkspaceContext';

interface InputCodeDef {
  code: string;
  category: string;
  rule_name: string;
  calculation_method: string;
  rule_rate?: number | null;
  rule_amount?: number | null;
}

function showsQty(def: InputCodeDef | undefined) {
  return def?.calculation_method === 'unit_multiplier' || def?.calculation_method === 'daily_rate_deduction';
}
function showsRate(def: InputCodeDef | undefined) {
  return def?.calculation_method === 'unit_multiplier';
}
function showsAmt(def: InputCodeDef | undefined) {
  return def?.calculation_method === 'fixed_amount';
}

// ── Category badge (EARNING / DEDUCTION / INFORMATION) ───────────────────────

function CategoryBadge({ category }: { category: string }) {
  const cfg =
    category === 'EARNING'
      ? 'bg-green-100 text-green-800'
      : category === 'DEDUCTION'
      ? 'bg-red-100 text-red-800'
      : 'bg-gray-100 text-gray-600';
  return (
    <span
      style={{ borderRadius: 'var(--radius-badge)' }}
      className={`px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${cfg}`}
    >
      {category}
    </span>
  );
}

// ── Trash icon ────────────────────────────────────────────────────────────────

function TrashIcon() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75}
        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
    </svg>
  );
}

function PlusIcon() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
    </svg>
  );
}

function InboxIcon() {
  return (
    <svg className="w-full h-full" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
    </svg>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

export function PayrollInputs() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const navigate = useNavigate();
  const toast = useToast();
  const { workspace } = useWorkspaceContext();

  const [inputs, setInputs] = useState<PayrollInput[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [inputDefs, setInputDefs] = useState<InputCodeDef[]>([]);
  const [loading, setLoading] = useState(true);
  const [pageError, setPageError] = useState<string | null>(null);
  const [issues, setIssues] = useState<{ total: number; deactivated_with_inputs: number; unmatched_with_inputs: number; period_label: string } | null>(null);

  // slide-over state
  const [panelOpen, setPanelOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  // form fields
  const [employeeId, setEmployeeId] = useState('');
  const [inputCode, setInputCode] = useState('');
  const [quantity, setQuantity] = useState('');
  const [effectivePeriod, setEffectivePeriod] = useState('');

  useEffect(() => {
    if (!workspaceId) return;
    Promise.all([
      workspaceApi.getEmployees(workspaceId),
      payrollInputApi.list(workspaceId),
      workspaceApi.getInputCodes(workspaceId),
      payrollApi.getInputIssues(workspaceId).catch(() => null),
    ])
      .then(([emps, data, codesData, issuesData]) => {
        setEmployees(emps);
        setInputs(data.inputs);
        setInputDefs(codesData.input_codes);
        setIssues(issuesData);
      })
      .catch((e) => setPageError(e.message))
      .finally(() => setLoading(false));
  }, [workspaceId]);

  function resetForm() {
    setEmployeeId('');
    setInputCode('');
    setQuantity('');
    setEffectivePeriod('');
    setFormError(null);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!workspaceId || !employeeId || !inputCode) return;
    setSubmitting(true);
    setFormError(null);
    try {
      const payload: {
        employee_id: string;
        input_code: string;
        quantity?: number;
        reference_date?: string;
      } = { employee_id: employeeId, input_code: inputCode };
      if (quantity) payload.quantity = parseFloat(quantity);
      if (effectivePeriod) payload.reference_date = `${effectivePeriod}-01`;

      await payrollInputApi.create(workspaceId, payload);
      const data = await payrollInputApi.list(workspaceId);
      setInputs(data.inputs);
      resetForm();
      setPanelOpen(false);
      toast.show('success', 'Input added to payroll inbox');
    } catch (e: unknown) {
      setFormError(e instanceof Error ? e.message : 'Failed to add input');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(inputId: string) {
    if (!workspaceId) return;
    try {
      await payrollInputApi.delete(workspaceId, inputId);
      setInputs((prev) => prev.filter((i) => i.payroll_input_id !== inputId));
      toast.show('success', 'Input removed');
    } catch (e: unknown) {
      toast.show('error', e instanceof Error ? e.message : 'Failed to delete input');
    }
  }

  const selectedDef = inputDefs.find((d) => d.code === inputCode);

  // Group input codes by category for DD-6
  const employeeOptions = employees.map((e) => ({
    value: e.employee_id,
    label: `${e.full_name} (${e.employee_number})`,
  }));

  const inputCodeOptions = inputDefs.map((d) => ({
    value: d.code,
    label: `${d.rule_name}${d.code !== d.rule_name ? ` (${d.code})` : ''}`,
    group: d.category,
  }));

  const pendingCount = inputs.length;

  return (
    <div className="max-w-5xl">
      {/* DD-8: Inbox framing — title + pending count */}
      <ContentHeader
        title="Payroll Inputs"
        subtitle={
          loading
            ? 'Loading…'
            : pendingCount > 0
            ? `${pendingCount} pending — will be claimed on next payroll run`
            : 'No pending inputs for next run'
        }
        back={
          <Breadcrumb items={[
            { label: 'Bureau Dashboard', to: '/' },
            { label: workspace?.name ?? '…', to: `/workspaces/${workspaceId}` },
            { label: 'Period Inputs' },
          ]} />
        }
        action={
          <div className="flex items-center gap-2">
            <Link
              to={`/workspaces/${workspaceId}/payroll/inputs/bulk`}
              className="text-sm text-brand hover:underline"
            >
              Bulk upload
            </Link>
            <Btn
              variant="primary"
              size="md"
              icon={<PlusIcon />}
              iconPosition="left"
              onClick={() => { resetForm(); setPanelOpen(true); }}
            >
              Add Input
            </Btn>
          </div>
        }
      />

      {pageError && (
        <AlertBanner variant="error" title="Failed to load inputs" description={pageError} className="mb-4" />
      )}

      {issues && issues.total > 0 && (
        <AlertBanner
          variant="warning"
          title={`${issues.total} input${issues.total !== 1 ? 's' : ''} require attention before running payroll`}
          description={[
            issues.deactivated_with_inputs > 0 && `${issues.deactivated_with_inputs} deactivated employee${issues.deactivated_with_inputs !== 1 ? 's' : ''}`,
            issues.unmatched_with_inputs > 0 && `${issues.unmatched_with_inputs} employee${issues.unmatched_with_inputs !== 1 ? 's' : ''} missing grade or salary definition`,
          ].filter(Boolean).join(', ') + '.'}
          action={{ label: 'Review employees →', onClick: () => navigate(`/workspaces/${workspaceId}/employees`) }}
          className="mb-4"
        />
      )}

      {/* Inputs table */}
      <Card padding="sm">
        {loading ? (
          <table className="w-full">
            <tbody>
              {Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="animate-pulse border-b border-gray-100">
                  {[60, 80, 50, 40, 40, 40, 50, 30].map((w, j) => (
                    <td key={j} className="px-4 py-3">
                      <div className="h-4 bg-gray-200 rounded" style={{ width: `${w}%` }} />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        ) : inputs.length === 0 ? (
          <EmptyState
            icon={<InboxIcon />}
            headline="Inbox is clear"
            body="Add variable inputs — overtime, bonuses, deductions — to be included in the next payroll run."
            action={{ label: 'Add First Input', onClick: () => setPanelOpen(true) }}
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50 sticky top-0">
                  {['Employee', 'Code', 'Category', 'Qty', 'Rate', 'Amount', 'For Period', 'Source', ''].map((h, i) => (
                    <th
                      key={i}
                      className={`px-4 py-3 text-[11px] font-semibold uppercase tracking-wider text-gray-500 ${i >= 3 && i <= 6 ? 'text-right' : 'text-left'} ${i === 8 ? 'w-10' : ''}`}
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {inputs.map((inp) => {
                  const def = inputDefs.find((d) => d.code === inp.input_code);
                  const displayRate   = def?.rule_rate   != null ? `₦${Number(def.rule_rate).toLocaleString('en-NG', { minimumFractionDigits: 2 })}` : '—';
                  const displayAmount = def?.rule_amount != null ? `₦${Number(def.rule_amount).toLocaleString('en-NG', { minimumFractionDigits: 2 })}` : '—';
                  return (
                  <tr key={inp.payroll_input_id} className="border-b border-gray-100 hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3">
                      <p className="font-medium text-gray-800">{inp.employee_name}</p>
                      <p className="text-[11px] text-gray-400 mt-0.5 font-mono">{inp.employee_number}</p>
                    </td>
                    <td className="px-4 py-3 font-mono text-xs text-gray-600">{inp.input_code}</td>
                    <td className="px-4 py-3">
                      <CategoryBadge category={inp.input_category} />
                    </td>
                    <td className="px-4 py-3 text-right text-gray-600 tabular-nums">{inp.quantity ?? '—'}</td>
                    <td className="px-4 py-3 text-right text-gray-600 tabular-nums">{displayRate}</td>
                    <td className="px-4 py-3 text-right text-gray-600 tabular-nums">{displayAmount}</td>
                    <td className="px-4 py-3 text-right text-gray-500 text-xs">
                      {inp.reference_date ? inp.reference_date.slice(0, 7) : <span className="text-gray-400 italic">current</span>}
                    </td>
                    <td className="px-4 py-3 text-gray-400 text-xs">{inp.source}</td>
                    <td className="px-4 py-3">
                      <IconBtn
                        label={`Delete input for ${inp.employee_name}`}
                        size="sm"
                        className="text-gray-400 hover:text-red-600"
                        onClick={() => handleDelete(inp.payroll_input_id)}
                      >
                        <TrashIcon />
                      </IconBtn>
                    </td>
                  </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Add Input — SlideOver (DD-3: primary action opens panel, not inline form) */}
      <SlideOver
        open={panelOpen}
        onClose={() => setPanelOpen(false)}
        title="Add Payroll Input"
        description="Record a variable event for the next run"
        footer={
          <>
            <Btn variant="secondary" onClick={() => setPanelOpen(false)} disabled={submitting}>
              Cancel
            </Btn>
            <Btn
              variant="primary"
              loading={submitting}
              disabled={!employeeId || !inputCode}
              onClick={(e) => handleSubmit(e as unknown as React.FormEvent)}
            >
              Add Input
            </Btn>
          </>
        }
      >
        <form id="add-input-form" onSubmit={handleSubmit} className="flex flex-col gap-4">
          {formError && (
            <AlertBanner variant="error" title="Failed to add input" description={formError} />
          )}

          <SearchableSelect
            label="Employee"
            required
            options={employeeOptions}
            value={employeeId}
            onChange={setEmployeeId}
            placeholder="Select employee…"
          />

          {/* Input code — groups by category (DD-6) */}
          <SearchableSelect
            label="Input Code"
            required
            options={inputCodeOptions}
            value={inputCode}
            onChange={(v) => { setInputCode(v); setQuantity(''); }}
            placeholder="Select code…"
          />

          {/* Conditional fields based on calculation method */}
          {inputCode && showsQty(selectedDef) && (
            <NumberInput
              label="Quantity"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              step="0.01"
              min="0"
              hint={selectedDef?.calculation_method === 'daily_rate_deduction' ? 'Number of days' : 'Number of units'}
            />
          )}

          {inputCode && showsRate(selectedDef) && selectedDef?.rule_rate != null && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Rate per unit</label>
              <p className="text-sm text-gray-900 bg-gray-50 border border-gray-200 rounded px-3 py-2">
                ₦{Number(selectedDef.rule_rate).toLocaleString('en-NG', { minimumFractionDigits: 2 })}
                <span className="ml-2 text-xs text-gray-500">(from payroll rule — not editable)</span>
              </p>
            </div>
          )}

          {inputCode && showsAmt(selectedDef) && selectedDef?.rule_amount != null && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Amount</label>
              <p className="text-sm text-gray-900 bg-gray-50 border border-gray-200 rounded px-3 py-2">
                ₦{Number(selectedDef.rule_amount).toLocaleString('en-NG', { minimumFractionDigits: 2 })}
                <span className="ml-2 text-xs text-gray-500">(from payroll rule — not editable)</span>
              </p>
            </div>
          )}

          <DateInput
            label="For period"
            mode="month"
            value={effectivePeriod}
            onChange={setEffectivePeriod}
            hint="Leave blank for current run. Set only for late inputs from a prior month."
          />
        </form>
      </SlideOver>
    </div>
  );
}
