/**
 * S8 — Bulk Period Inputs Upload
 *
 * Design decisions honoured:
 * DD-5  Empty state (before file chosen) has a download CTA
 * FRM-7 FileDropZone replaces hidden input + button
 *
 * All Excel parse logic preserved exactly from prior implementation.
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { workspaceApi } from '../api/workspace';
import * as XLSX from 'xlsx';
import { api } from '../api/client';
import {
  ContentHeader,
  Card,
  Btn,
  DownloadBtn,
  FileDropZone,
  AlertBanner,
  useToast,
  Breadcrumb,
} from '../design-system';
import type { DropZoneState } from '../design-system';
import { useWorkspaceContext } from '../context/WorkspaceContext';

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
  const data =
    inputDefs.length > 0
      ? inputDefs.map((def) => ({
          employee_no: 'e.g. SMC 1382',
          input_code: def.code,
          quantity: '',
          reference_date: '',
          _rule_name: def.rule_name,
        }))
      : [{ employee_no: 'e.g. SMC 1382', input_code: '', quantity: '', reference_date: '', _rule_name: '' }];
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(data), 'Payroll Inputs');
  XLSX.writeFile(wb, 'payroll_inputs_bulk_template.xlsx');
}

// ── Parse helpers (unchanged from original) ───────────────────────────────────

function normaliseMonthDate(raw: string): string | undefined {
  const s = raw.trim();
  if (!s) return undefined;
  const match = s.match(/^(\d{4})-(\d{2})(-\d{2})?$/);
  if (!match) return `INVALID:${s}`;
  return `${match[1]}-${match[2]}-01`;
}

function cellToRawMonthDate(val: unknown): string {
  if (val instanceof Date) {
    const d = new Date(val.getTime() - val.getTimezoneOffset() * 60000);
    return d.toISOString().slice(0, 7);
  }
  return String(val ?? '').trim();
}

function parseSheet(rows: Record<string, unknown>[], codeMap: Map<string, string>): ParsedRow[] {
  return rows.map((r, i) => {
    const row: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(r)) row[k.trim().toLowerCase()] = v;

    const rowNum = i + 2;
    const employee_number = String(row['employee_number'] ?? row['employee_no'] ?? '').trim();
    const input_code_raw = String(row['input_code'] ?? '').trim().toUpperCase();

    if (!employee_number)
      return { employee_number: '', input_code: '', _error: `Row ${rowNum}: employee_number is required` };
    if (!input_code_raw)
      return { employee_number, input_code: '', _error: `Row ${rowNum}: input_code is required` };

    const canonical = codeMap.get(input_code_raw);
    if (!canonical)
      return { employee_number, input_code: input_code_raw, _error: `Row ${rowNum}: unknown input_code '${input_code_raw}' — download the template to see valid codes for this workspace` };

    const input_code = canonical;
    const qty = row['quantity'] !== '' && row['quantity'] != null ? Number(row['quantity']) : undefined;
    const rawDate = cellToRawMonthDate(row['reference_date']);
    const ref_date = rawDate ? normaliseMonthDate(rawDate) : undefined;
    if (ref_date?.startsWith('INVALID'))
      return { employee_number, input_code, _error: `Row ${rowNum}: reference_date '${rawDate}' is invalid (use YYYY-MM)` };

    return { employee_number, input_code, quantity: qty, reference_date: ref_date };
  });
}

// ── Icons ─────────────────────────────────────────────────────────────────────

// ── Component ─────────────────────────────────────────────────────────────────

export function PayrollInputsBulkUpload() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const navigate = useNavigate();
  const toast = useToast();
  const { workspace } = useWorkspaceContext();

  const [fileName, setFileName] = useState<string | null>(null);
  const [rows, setRows] = useState<ParsedRow[]>([]);
  const [parseErrors, setParseErrors] = useState<string[]>([]);
  const [dropState, setDropState] = useState<DropZoneState>('idle');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<{ created: number; errors: { row: number; detail: string }[] } | null>(null);
  const [inputDefs, setInputDefs] = useState<InputCodeDef[]>([]);
  const [codeMap, setCodeMap] = useState<Map<string, string>>(new Map());

  useEffect(() => {
    if (!workspaceId) return;
    workspaceApi
      .getInputCodes(workspaceId)
      .then((data) => {
        setInputDefs(data.input_codes);
        setCodeMap(new Map(data.input_codes.map((d) => [d.code.toUpperCase(), d.code])));
      })
      .catch(() => {});
  }, [workspaceId]);

  function handleFile(file: File) {
    setFileName(file.name);
    setRows([]);
    setParseErrors([]);
    setResult(null);
    setDropState('processing');

    const reader = new FileReader();
    reader.onload = (ev) => {
      try {
        const wb = XLSX.read(ev.target?.result, { type: 'array', cellDates: true });
        const sheet = wb.Sheets[wb.SheetNames[0]];
        const raw = XLSX.utils.sheet_to_json<Record<string, unknown>>(sheet, { defval: '' });
        const parsed = parseSheet(raw, codeMap);
        const errs = parsed.filter((r) => r._error).map((r) => r._error!);
        setRows(parsed);
        setParseErrors(errs);
        setDropState(errs.length > 0 ? 'error' : 'success');
      } catch {
        setParseErrors(['Failed to read file. Ensure it is a valid .xlsx or .csv file.']);
        setDropState('error');
      }
    };
    reader.readAsArrayBuffer(file);
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
      if (res.errors.length === 0) {
        toast.show('success', `${res.created} input${res.created !== 1 ? 's' : ''} added to payroll inbox`);
      } else {
        toast.show('warning', `${res.created} created, ${res.errors.length} failed — see details below`);
      }
    } catch (e: unknown) {
      setParseErrors([e instanceof Error ? e.message : 'Submission failed']);
      toast.show('error', 'Submission failed');
    } finally {
      setSubmitting(false);
    }
  }

  const validCount = rows.filter((r) => !r._error).length;
  const invalidCount = rows.filter((r) => r._error).length;

  return (
    <div className="max-w-4xl">
      <ContentHeader
        title="Bulk Input Upload"
        subtitle="Upload an Excel (.xlsx) or CSV (.csv) file to add multiple period inputs at once"
        back={
          <Breadcrumb items={[
            { label: 'Bureau Dashboard', to: '/' },
            { label: workspace?.name ?? '…', to: `/workspaces/${workspaceId}` },
            { label: 'Period Inputs', to: `/workspaces/${workspaceId}/payroll/inputs` },
            { label: 'Bulk Upload' },
          ]} />
        }
      />

      {/* Step 1 — Download template */}
      <Card className="mb-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-sm font-semibold text-gray-800">Step 1 — Download template</p>
            <p className="mt-1 text-sm text-gray-500">
              Fill in your inputs (one per row), then upload the completed file.
              Use <code className="font-mono text-xs bg-gray-100 px-1 py-0.5 rounded">reference_date</code> (YYYY-MM)
              to tag inputs from a prior period — blank = current run.
            </p>
          </div>
          <DownloadBtn
            label="Download Template"
            onClick={() => downloadTemplate(inputDefs)}
            className="shrink-0"
          />
        </div>
      </Card>

      {/* Step 2 — Drop zone */}
      <Card className="mb-4">
        <p className="text-sm font-semibold text-gray-800 mb-3">Step 2 — Upload your file</p>
        <FileDropZone
          accept=".xlsx,.csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,text/csv"
          label={fileName ? `Selected: ${fileName}` : 'Drop your .xlsx or .csv file here, or click to browse'}
          hint="Accepted formats: .xlsx, .csv"
          state={dropState}
          errorMessage={parseErrors.length > 0 ? `${parseErrors.length} validation error${parseErrors.length !== 1 ? 's' : ''} found` : undefined}
          successMessage={rows.length > 0 ? `${rows.length} row${rows.length !== 1 ? 's' : ''} parsed — review below` : undefined}
          onFile={handleFile}
        />
      </Card>

      {/* Parse errors */}
      {parseErrors.length > 0 && (
        <AlertBanner
          variant="error"
          title={`${parseErrors.length} validation error${parseErrors.length !== 1 ? 's' : ''}`}
          description={parseErrors.slice(0, 3).join(' · ') + (parseErrors.length > 3 ? ` +${parseErrors.length - 3} more` : '')}
          className="mb-4"
        />
      )}

      {/* Step 3 — Review & submit */}
      {rows.length > 0 && (
        <Card>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <p className="text-sm font-semibold text-gray-800">Step 3 — Review and submit</p>
              <span
                style={{ borderRadius: 'var(--radius-badge)' }}
                className="px-2.5 py-1 text-[11px] font-semibold bg-green-100 text-green-800"
              >
                {validCount} valid
              </span>
              {invalidCount > 0 && (
                <span
                  style={{ borderRadius: 'var(--radius-badge)' }}
                  className="px-2.5 py-1 text-[11px] font-semibold bg-red-100 text-red-800"
                >
                  {invalidCount} with errors
                </span>
              )}
            </div>
            <div className="flex flex-col items-end gap-1">
              <Btn
                variant="primary"
                size="md"
                loading={submitting}
                disabled={validCount === 0}
                onClick={handleSubmit}
              >
                Submit {validCount} Input{validCount !== 1 ? 's' : ''}
              </Btn>
              {validCount === 0 && rows.length > 0 && (
                <p className="text-xs text-red-600">Fix the errors above before submitting.</p>
              )}
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs border-collapse">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50">
                  {['#', 'Employee No.', 'Code', 'Qty', 'For Period', 'Status'].map((h, i) => (
                    <th key={i} className="px-3 py-2 text-left text-[10px] font-semibold uppercase tracking-wider text-gray-500">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row, i) => (
                  <tr
                    key={i}
                    className={`border-b border-gray-100 ${row._error ? 'bg-red-50' : 'hover:bg-slate-50'}`}
                  >
                    <td className="px-3 py-2 text-gray-400">{i + 1}</td>
                    <td className="px-3 py-2 font-mono text-gray-700">{row.employee_number}</td>
                    <td className="px-3 py-2 font-mono text-gray-700">{row.input_code}</td>
                    <td className="px-3 py-2 text-gray-600 tabular-nums">{row.quantity ?? '—'}</td>
                    <td className="px-3 py-2 text-gray-500">
                      {row.reference_date ? row.reference_date.slice(0, 7) : <span className="text-gray-400 italic">current</span>}
                    </td>
                    <td className="px-3 py-2">
                      {row._error ? (
                        <span className="text-red-600 font-medium">{row._error}</span>
                      ) : (
                        <span className="text-green-600 font-medium">✓ OK</span>
                      )}
                    </td>
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
          <AlertBanner
            variant={result.errors.length === 0 ? 'success' : 'warning'}
            title={`${result.created} input${result.created !== 1 ? 's' : ''} created`}
            description={
              result.errors.length > 0
                ? result.errors.map((e) => `Row ${e.row}: ${e.detail}`).join(' · ')
                : 'All inputs added to the payroll inbox.'
            }
            action={
              result.errors.length === 0
                ? { label: 'View in Inbox →', onClick: () => navigate(`/workspaces/${workspaceId}/payroll/inputs`) }
                : undefined
            }
          />
        </div>
      )}

      {/* Empty state — no file chosen yet */}
      {rows.length === 0 && !fileName && (
        <div className="mt-4">
          <p className="text-xs text-center text-gray-400">
            Need the valid input codes for this workspace?{' '}
            <button
              className="text-brand underline hover:opacity-80"
              onClick={() => downloadTemplate(inputDefs)}
            >
              Download the template
            </button>{' '}
            — it includes all current codes pre-filled.
          </p>
        </div>
      )}
    </div>
  );
}
