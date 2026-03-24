import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { payrollInputApi } from '../api/payrollInput';
import { workspaceApi } from '../api/workspace';
import type { PayrollInput, Employee } from '../types/payroll';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Btn } from '../components/ui/Btn';
import { AlertBox } from '../components/ui/AlertBox';

const INPUT_CODES = [
  'SPECIAL_OVERTIME',
  'REGULAR_OVERTIME',
  'WEEKEND_ALLOWANCE',
  'ABSENCE',
  'SUSPENSION',
  'ACCIDENT_FREE_BONUS',
  'BONUS',
  'ADJUSTMENT',
] as const;

const CODE_CATEGORY: Record<string, string> = {
  SPECIAL_OVERTIME:    'EARNING',
  REGULAR_OVERTIME:    'EARNING',
  WEEKEND_ALLOWANCE:   'EARNING',
  ABSENCE:             'DEDUCTION',
  SUSPENSION:          'DEDUCTION',
  ACCIDENT_FREE_BONUS: 'EARNING',
  BONUS:               'EARNING',
  ADJUSTMENT:          'EARNING',
};

const QTY_RATE_CODES = new Set(['SPECIAL_OVERTIME', 'REGULAR_OVERTIME', 'ABSENCE', 'SUSPENSION']);
const QTY_ONLY_CODES = new Set(['ABSENCE', 'SUSPENSION']);
const AMOUNT_CODES   = new Set(['WEEKEND_ALLOWANCE', 'ACCIDENT_FREE_BONUS', 'BONUS', 'ADJUSTMENT']);

function showsQty(code: string)  { return QTY_RATE_CODES.has(code); }
function showsRate(code: string) { return QTY_RATE_CODES.has(code) && !QTY_ONLY_CODES.has(code); }
function showsAmt(code: string)  { return AMOUNT_CODES.has(code); }

export function PayrollInputs() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const [inputs,     setInputs]     = useState<PayrollInput[]>([]);
  const [employees,  setEmployees]  = useState<Employee[]>([]);
  const [loading,    setLoading]    = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error,      setError]      = useState<string | null>(null);

  // form state
  const [employeeId,      setEmployeeId]      = useState('');
  const [inputCode,       setInputCode]       = useState('');
  const [quantity,        setQuantity]        = useState('');
  const [rate,            setRate]            = useState('');
  const [amount,          setAmount]          = useState('');
  const [effectivePeriod, setEffectivePeriod] = useState('');

  useEffect(() => {
    if (!workspaceId) return;
    Promise.all([
      workspaceApi.getEmployees(workspaceId),
      payrollInputApi.list(workspaceId),
    ])
      .then(([emps, data]) => {
        setEmployees(emps);
        setInputs(data.inputs);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [workspaceId]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!workspaceId || !employeeId || !inputCode) return;
    setSubmitting(true);
    setError(null);
    try {
      const payload: {
        employee_id: string;
        input_code: string;
        quantity?: number;
        rate?: number;
        amount?: number;
        reference_date?: string;
      } = { employee_id: employeeId, input_code: inputCode };
      if (quantity)        payload.quantity       = parseFloat(quantity);
      if (rate)            payload.rate           = parseFloat(rate);
      if (amount)          payload.amount         = parseFloat(amount);
      if (effectivePeriod) payload.reference_date = `${effectivePeriod}-01`;

      await payrollInputApi.create(workspaceId, payload);
      // Re-fetch list to get full row with employee name
      const data = await payrollInputApi.list(workspaceId);
      setInputs(data.inputs);
      // Reset form
      setEmployeeId('');
      setInputCode('');
      setQuantity('');
      setRate('');
      setAmount('');
      setEffectivePeriod('');
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to add input');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(inputId: string) {
    if (!workspaceId) return;
    try {
      await payrollInputApi.delete(workspaceId, inputId);
      setInputs((prev) => prev.filter((i) => i.payroll_input_id !== inputId));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to delete input');
    }
  }

  const category = CODE_CATEGORY[inputCode] ?? '';

  return (
    <div>
      <PageHeader
        title="Period Inputs"
        subtitle="Variable events pending for next payroll run"
      />

      {error && <AlertBox type="error" messages={[error]} />}

      {!loading && (
        <div className="mb-4 px-1">
          <span className="text-sm text-slate-500">
            {inputs.length} input(s) pending — will be claimed on next payroll run
          </span>
        </div>
      )}

      {/* Add Input Form */}
      <Card>
        <h2 className="text-sm font-semibold text-slate-700 mb-4">Add Input</h2>
        <form onSubmit={handleSubmit} className="flex flex-wrap gap-3 items-end">
          {/* Employee */}
          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-500">Employee</label>
            <select
              className="border border-slate-200 rounded px-2 py-1.5 text-sm text-slate-700 min-w-[180px]"
              value={employeeId}
              onChange={(e) => setEmployeeId(e.target.value)}
              required
            >
              <option value="">Select employee…</option>
              {employees.map((emp) => (
                <option key={emp.employee_id} value={emp.employee_id}>
                  {emp.full_name} ({emp.employee_number})
                </option>
              ))}
            </select>
          </div>

          {/* Input Code */}
          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-500">Input Code</label>
            <select
              className="border border-slate-200 rounded px-2 py-1.5 text-sm text-slate-700 min-w-[180px]"
              value={inputCode}
              onChange={(e) => { setInputCode(e.target.value); setQuantity(''); setRate(''); setAmount(''); }}
              required
            >
              <option value="">Select code…</option>
              {INPUT_CODES.map((code) => (
                <option key={code} value={code}>{code}</option>
              ))}
            </select>
          </div>

          {/* Category hint */}
          {category && (
            <div className="flex flex-col gap-1">
              <label className="text-xs text-slate-500">Category</label>
              <span
                className={`px-2 py-1.5 rounded text-xs font-semibold ${
                  category === 'EARNING'
                    ? 'bg-green-100 text-green-700'
                    : 'bg-red-100 text-red-700'
                }`}
              >
                {category}
              </span>
            </div>
          )}

          {/* Quantity */}
          {inputCode && showsQty(inputCode) && (
            <div className="flex flex-col gap-1">
              <label className="text-xs text-slate-500">Quantity</label>
              <input
                type="number"
                step="0.01"
                className="border border-slate-200 rounded px-2 py-1.5 text-sm w-24"
                placeholder="0"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
              />
            </div>
          )}

          {/* Rate */}
          {inputCode && showsRate(inputCode) && (
            <div className="flex flex-col gap-1">
              <label className="text-xs text-slate-500">Rate</label>
              <input
                type="number"
                step="0.01"
                className="border border-slate-200 rounded px-2 py-1.5 text-sm w-28"
                placeholder="0.00"
                value={rate}
                onChange={(e) => setRate(e.target.value)}
              />
            </div>
          )}

          {/* Amount */}
          {inputCode && showsAmt(inputCode) && (
            <div className="flex flex-col gap-1">
              <label className="text-xs text-slate-500">Amount</label>
              <input
                type="number"
                step="0.01"
                className="border border-slate-200 rounded px-2 py-1.5 text-sm w-28"
                placeholder="0.00"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
              />
            </div>
          )}

          {/* For Period */}
          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-500">
              For period <span className="text-slate-400">(optional)</span>
            </label>
            <input
              type="month"
              className="border border-slate-200 rounded px-2 py-1.5 text-sm w-36"
              value={effectivePeriod}
              onChange={(e) => setEffectivePeriod(e.target.value)}
            />
            <span className="text-xs text-slate-400 max-w-[160px] leading-tight">
              Leave blank for current run. Set for late-arriving events from a previous month.
            </span>
          </div>

          <Btn type="submit" disabled={submitting || !employeeId || !inputCode}>
            {submitting ? 'Adding…' : 'Add Input'}
          </Btn>
        </form>
      </Card>

      {/* Inputs Table */}
      {loading ? (
        <p className="text-sm text-slate-500 mt-4">Loading inputs…</p>
      ) : (
        <Card>
          {inputs.length === 0 ? (
            <p className="text-sm text-slate-400 py-8 text-center">
              No pending inputs. Add one above.
            </p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100">
                  <Th>Employee</Th>
                  <Th>Code</Th>
                  <Th>Category</Th>
                  <Th>Qty</Th>
                  <Th>Rate</Th>
                  <Th>Amount</Th>
                  <Th>For Period</Th>
                  <Th>Source</Th>
                  <Th></Th>
                </tr>
              </thead>
              <tbody>
                {inputs.map((inp) => (
                  <tr key={inp.payroll_input_id} className="border-b border-slate-50 hover:bg-slate-50">
                    <Td>
                      <span className="font-medium text-slate-700">{inp.employee_name}</span>
                      <span className="block text-xs text-slate-400">{inp.employee_number}</span>
                    </Td>
                    <Td className="font-mono text-xs">{inp.input_code}</Td>
                    <Td>
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-semibold ${
                          inp.input_category === 'EARNING'
                            ? 'bg-green-100 text-green-700'
                            : 'bg-red-100 text-red-700'
                        }`}
                      >
                        {inp.input_category}
                      </span>
                    </Td>
                    <Td>{inp.quantity ?? '—'}</Td>
                    <Td>{inp.rate ?? '—'}</Td>
                    <Td>{inp.amount ?? '—'}</Td>
                    <Td>
                      {inp.reference_date
                        ? inp.reference_date.slice(0, 7)   // "YYYY-MM"
                        : <span className="text-slate-400">current</span>}
                    </Td>
                    <Td>{inp.source}</Td>
                    <Td>
                      <Btn
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(inp.payroll_input_id)}
                      >
                        Delete
                      </Btn>
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
