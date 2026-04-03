import { useRef, useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { workspaceApi } from '../api/workspace';
import * as XLSX from 'xlsx';
import { api } from '../api/client';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Btn } from '../components/ui/Btn';
import { AlertBox } from '../components/ui/AlertBox';


// ── Types ─────────────────────────────────────────────────────────────────────

interface ParsedRow {
  employee_number: string;
  input_code: string;
  quantity?: number;
  reference_date?: string;
  _error?: string;
}

interface InputCodeDef {
  code: string;
  rule_name: string;
  category: string;
  calculation_method: string;
}

// ── Template download ─────────────────────────────────────────────────────────

function downloadTemplate(inputDefs: InputCodeDef[]) {
  const wb = XLSX.utils.book_new();

  // One example row per rule that accepts inputs, using the actual workspace codes.
  const data = inputDefs.length > 0
    ? inputDefs.map((def) => ({
        employee_no:    'e.g. SMC 1382',
        input_code:     def.code,
        quantity:       '',
        reference_date: '',
        _rule_name:     def.rule_name,
      }))
    : [
        { employee_no: 'e.g. SMC 1382', input_code: '', quantity: '', reference_date: '', _rule_name: '' },
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

/**
 * Convert an Excel cell value to a raw YYYY-MM string for normaliseMonthDate.
 * With cellDates:true, date cells arrive as JS Date objects.
 * CSV / text cells arrive as plain strings.
 */
function cellToRawMonthDate(val: unknown): string {
  if (val instanceof Date) {
    const d = new Date(val.getTime() - val.getTimezoneOffset() * 60000);
    return d.toISOString().slice(0, 7); // YYYY-MM
  }
  return String(val ?? '').trim();
}

/**
 * codeMap: Map<UPPERCASE_CODE, canonical_input_field>
 * Allows case-insensitive matching while storing the exact value the engine expects.
 */
function parseSheet(rows: Record<string, unknown>[], codeMap: Map<string, string>): ParsedRow[] {
  return rows.map((r, i) => {
    // Normalise all header keys: trim + lowercase (handles QUANTITY, Quantity, etc.)
    const row: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(r)) row[k.trim().toLowerCase()] = v;

    const rowNum = i + 2;
    const employee_number = String(row['employee_number'] ?? row['employee_no'] ?? '').trim();
    const input_code_raw  = String(row['input_code']     ?? '').trim().toUpperCase();

    if (!employee_number)
      return { employee_number: '', input_code: '', _error: `Row ${rowNum}: employee_number is required` };
    if (!input_code_raw)
      return { employee_number, input_code: '', _error: `Row ${rowNum}: input_code is required` };

    const canonical = codeMap.get(input_code_raw);
    if (!canonical)
      return { employee_number, input_code: input_code_raw, _error: `Row ${rowNum}: unknown input_code '${input_code_raw}' — download the template to see valid codes for this workspace` };

    // Use the canonical (DB) input_field value — must match rule_evaluator lookup
    const input_code = canonical;

    const qty = row['quantity'] !== '' && row['quantity'] != null ? Number(row['quantity']) : undefined;

    const rawDate = cellToRawMonthDate(row['reference_date']);
    const ref_date = rawDate ? normaliseMonthDate(rawDate) : undefined;
    if (ref_date?.startsWith('INVALID'))
      return { employee_number, input_code, _error: `Row ${rowNum}: reference_date '${rawDate}' is invalid (use YYYY-MM)` };

    return { employee_number, input_code, quantity: qty, reference_date: ref_date };
  });
}

// ── Component ─────────────────────────────────────────────────────────────────

export function PayrollInputsBulkUpload() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [fileName,   setFileName]   = useState<string | null>(null);
  const [rows,       setRows]       = useState<ParsedRow[]>([]);
  const [parseErr,   setParseErr]   = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [result,     setResult]     = useState<{ created: number; errors: { row: number; detail: string }[] } | null>(null);
  const [inputDefs, setInputDefs] = useState<InputCodeDef[]>([]);
  // Map of UPPERCASE_CODE → canonical input_field (for case-insensitive matching)
  const [codeMap, setCodeMap] = useState<Map<string, string>>(new Map());

  useEffect(() => {
    if (!workspaceId) return;
    workspaceApi.getInputCodes(workspaceId)
      .then((data) => {
        setInputDefs(data.input_codes);
        setCodeMap(new Map(data.input_codes.map((d) => [d.code.toUpperCase(), d.code])));
      })
      .catch(() => { /* non-fatal — validation will reject all codes */ });
  }, [workspaceId]);

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
        const wb   = XLSX.read(ev.target?.result, { type: 'array', cellDates: true });
        const sheet = wb.Sheets[wb.SheetNames[0]];
        const raw   = XLSX.utils.sheet_to_json<Record<string, unknown>>(sheet, { defval: '' });
        const parsed = parseSheet(raw, codeMap);
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
          <Btn variant="secondary" onClick={() => downloadTemplate(inputDefs)}>
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
                  <Th>Employee No.</Th>
                  <Th>Code</Th>
                  <Th>Qty</Th>
                  <Th>For Period</Th>
                  <Th>Notes</Th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row, i) => (
                  <tr
                    key={i}
                    className={`border-b border-slate-50 ${row._error ? 'bg-red-50' : ''}`}
                  >
                    <Td>{i + 1}</Td>
                    <Td className="font-mono text-xs truncate max-w-[120px]">{row.employee_number}</Td>
                    <Td className="font-mono">{row.input_code}</Td>
                    <Td>{row.quantity ?? '—'}</Td>
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
