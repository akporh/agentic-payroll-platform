import { useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import * as XLSX from 'xlsx';
import { api } from '../api/client';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Btn } from '../components/ui/Btn';
import { AlertBox } from '../components/ui/AlertBox';

// ── Constants (mirrored from PayrollInputs.tsx) ───────────────────────────────

const INPUT_CODES = new Set([
  'SPECIAL_OVERTIME',
  'REGULAR_OVERTIME',
  'WEEKEND_ALLOWANCE',
  'ABSENCE',
  'SUSPENSION',
  'ACCIDENT_FREE_BONUS',
  'BONUS',
  'ADJUSTMENT',
]);

// ── Types ─────────────────────────────────────────────────────────────────────

interface ParsedRow {
  employee_id: string;
  input_code: string;
  quantity?: number;
  rate?: number;
  amount?: number;
  reference_date?: string;
  _error?: string;
}

// ── Template download ─────────────────────────────────────────────────────────

function downloadTemplate() {
  const wb = XLSX.utils.book_new();
  const data = [
    {
      employee_id:    'paste-employee-uuid-here',
      input_code:     'REGULAR_OVERTIME',
      quantity:       3,
      rate:           '',
      amount:         '',
      reference_date: '2026-03',
    },
    {
      employee_id:    'paste-employee-uuid-here',
      input_code:     'BONUS',
      quantity:       '',
      rate:           '',
      amount:         50000,
      reference_date: '',
    },
  ];
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(data), 'Payroll Inputs');
  XLSX.writeFile(wb, 'payroll_inputs_bulk_template.xlsx');
}

// ── Parse logic ───────────────────────────────────────────────────────────────

function normaliseMonthDate(raw: string): string | undefined {
  const s = raw.trim();
  if (!s) return undefined;
  // Accept YYYY-MM or YYYY-MM-DD → normalise to YYYY-MM-01
  const match = s.match(/^(\d{4})-(\d{2})(-\d{2})?$/);
  if (!match) return `INVALID:${s}`;
  return `${match[1]}-${match[2]}-01`;
}

function parseSheet(rows: Record<string, unknown>[]): ParsedRow[] {
  return rows.map((r, i) => {
    const rowNum = i + 2;
    const employee_id = String(r['employee_id'] ?? '').trim();
    const input_code  = String(r['input_code']  ?? '').trim().toUpperCase();

    if (!employee_id)
      return { employee_id: '', input_code, _error: `Row ${rowNum}: employee_id is required` };
    if (!input_code)
      return { employee_id, input_code: '', _error: `Row ${rowNum}: input_code is required` };
    if (!INPUT_CODES.has(input_code))
      return { employee_id, input_code, _error: `Row ${rowNum}: unknown input_code '${input_code}'` };

    const qty    = r['quantity'] !== '' && r['quantity'] != null ? Number(r['quantity']) : undefined;
    const rate   = r['rate']     !== '' && r['rate']     != null ? Number(r['rate'])     : undefined;
    const amount = r['amount']   !== '' && r['amount']   != null ? Number(r['amount'])   : undefined;

    const rawDate = String(r['reference_date'] ?? '').trim();
    const ref_date = rawDate ? normaliseMonthDate(rawDate) : undefined;
    if (ref_date?.startsWith('INVALID'))
      return { employee_id, input_code, _error: `Row ${rowNum}: reference_date '${rawDate}' is invalid (use YYYY-MM)` };

    return { employee_id, input_code, quantity: qty, rate, amount, reference_date: ref_date };
  });
}

// ── Component ─────────────────────────────────────────────────────────────────

export function PayrollInputsBulkUpload() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [fileName, setFileName]     = useState<string | null>(null);
  const [rows,     setRows]         = useState<ParsedRow[]>([]);
  const [parseErr, setParseErr]     = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [result,   setResult]       = useState<{ created: number; errors: { row: number; detail: string }[] } | null>(null);

  function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    setRows([]);
    setParseErr([]);
    setResult(null);

    const reader = new FileReader();
    reader.onload = (ev) => {
      try {
        const wb   = XLSX.read(ev.target?.result, { type: 'array' });
        const sheet = wb.Sheets[wb.SheetNames[0]];
        const raw   = XLSX.utils.sheet_to_json<Record<string, unknown>>(sheet, { defval: '' });
        const parsed = parseSheet(raw);
        const errs   = parsed.filter((r) => r._error).map((r) => r._error!);
        setRows(parsed);
        setParseErr(errs);
      } catch {
        setParseErr(['Failed to read file. Ensure it is a valid .xlsx file.']);
      }
    };
    reader.readAsArrayBuffer(file);
    e.target.value = '';
  }

  async function handleSubmit() {
    if (!workspaceId || rows.length === 0) return;
    setSubmitting(true);
    setResult(null);
    try {
      const validRows = rows.filter((r) => !r._error).map(({ _error: _e, ...rest }) => rest);
      const res = await api.post<{ created: number; errors: { row: number; detail: string }[] }>(
        `/${workspaceId}/payroll/inputs/bulk`,
        { rows: validRows },
      );
      setResult(res);
    } catch (e: unknown) {
      setParseErr([e instanceof Error ? e.message : 'Submission failed']);
    } finally {
      setSubmitting(false);
    }
  }

  const validCount   = rows.filter((r) => !r._error).length;
  const invalidCount = rows.filter((r) =>  r._error).length;

  return (
    <div>
      <PageHeader
        title="Bulk Period Inputs"
        subtitle="Upload an Excel file to add multiple period inputs at once"
      />

      {/* Download template */}
      <Card>
        <h2 className="text-sm font-semibold text-slate-700 mb-2">Template</h2>
        <p className="text-xs text-slate-500 mb-3">
          Download the template, fill in your inputs (one per row), then upload the completed file.
          Use <strong>reference_date</strong> (YYYY-MM) to tag inputs from a previous period — blank = current run.
        </p>
        <div className="flex items-center gap-3 flex-wrap">
          <Btn variant="secondary" onClick={downloadTemplate}>
            ↓ Download Template
          </Btn>
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            onChange={handleFile}
            className="hidden"
          />
          <Btn variant="secondary" onClick={() => fileInputRef.current?.click()}>
            Choose File
          </Btn>
          {fileName && (
            <span className="text-xs text-slate-500 truncate max-w-xs">{fileName}</span>
          )}
        </div>
      </Card>

      {parseErr.length > 0 && (
        <div className="mt-4">
          <AlertBox type="error" title="Parse Errors" messages={parseErr} />
        </div>
      )}

      {/* Preview table */}
      {rows.length > 0 && (
        <Card>
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm text-slate-600">
              {validCount} valid row{validCount !== 1 ? 's' : ''}
              {invalidCount > 0 && (
                <span className="ml-2 text-amber-600">{invalidCount} with errors (skipped)</span>
              )}
            </span>
            <Btn
              onClick={handleSubmit}
              disabled={submitting || validCount === 0}
            >
              {submitting ? 'Submitting…' : `Submit ${validCount} Input${validCount !== 1 ? 's' : ''}`}
            </Btn>
          </div>

          <div className="overflow-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-100">
                  <Th>#</Th>
                  <Th>Employee ID</Th>
                  <Th>Code</Th>
                  <Th>Qty</Th>
                  <Th>Rate</Th>
                  <Th>Amount</Th>
                  <Th>For Period</Th>
                  <Th>Status</Th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row, i) => (
                  <tr
                    key={i}
                    className={`border-b border-slate-50 ${row._error ? 'bg-red-50' : ''}`}
                  >
                    <Td>{i + 1}</Td>
                    <Td className="font-mono text-xs truncate max-w-[120px]">{row.employee_id}</Td>
                    <Td className="font-mono">{row.input_code}</Td>
                    <Td>{row.quantity ?? '—'}</Td>
                    <Td>{row.rate ?? '—'}</Td>
                    <Td>{row.amount ?? '—'}</Td>
                    <Td>
                      {row.reference_date
                        ? row.reference_date.slice(0, 7)
                        : <span className="text-slate-400">current</span>}
                    </Td>
                    <Td>
                      {row._error
                        ? <span className="text-red-600">{row._error}</span>
                        : <span className="text-green-600">OK</span>}
                    </Td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Submission result */}
      {result && (
        <div className="mt-4">
          <AlertBox
            type={result.errors.length === 0 ? 'success' : 'error'}
            messages={[
              `${result.created} input${result.created !== 1 ? 's' : ''} created.`,
              ...result.errors.map((e) => `Row ${e.row}: ${e.detail}`),
            ]}
          />
        </div>
      )}
    </div>
  );
}

function Th({ children }: { children?: React.ReactNode }) {
  return (
    <th className="text-left text-xs font-semibold text-slate-500 uppercase tracking-wide py-2 px-3 whitespace-nowrap">
      {children}
    </th>
  );
}

function Td({ children, className = '' }: { children?: React.ReactNode; className?: string }) {
  return <td className={`py-2 px-3 text-slate-600 ${className}`}>{children}</td>;
}
