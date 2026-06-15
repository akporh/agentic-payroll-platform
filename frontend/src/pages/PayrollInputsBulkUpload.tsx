/**
 * S8 — Bulk Period Inputs Upload
 *
 * Design decisions honoured:
 * DD-5  Empty state (before file chosen) has a download CTA
 * FRM-7 FileDropZone replaces hidden input + button
 *
 * All Excel parse logic preserved exactly from prior implementation.
 */

import React, { useState, useEffect, useMemo } from 'react';
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
import { NativeUploadFlow } from '../components/shared/NativeUploadFlow';
import type { ColumnMapping } from '../components/shared/ColumnMappingPanel';
import {
  parseInputColumnHeader,
  matchInputCode,
  detectHeaderRowByScorer,
  scoreRowAsInputHeaders,
} from '../utils/nativeExcelParser';
import type { InputCodeDef } from '../utils/nativeExcelParser';

// ── Constants ─────────────────────────────────────────────────────────────────

const EMP_NO_ALIASES = ['ID NUMBER', 'STAFF ID', 'EMPLOYEE ID', 'EMPLOYEE NO', 'EMPLOYEE NUMBER', 'EMP NO', 'STAFF NO', 'EMP_NO'];

// ── Types ─────────────────────────────────────────────────────────────────────

interface ParsedRow {
  employee_number: string;
  input_code: string;
  quantity?: number;
  reference_date?: string;
  _error?: string;
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

  const [uploadMode, setUploadMode] = useState<'template' | 'native'>('native');
  const [fileName, setFileName] = useState<string | null>(null);
  const [rows, setRows] = useState<ParsedRow[]>([]);
  const [parseErrors, setParseErrors] = useState<string[]>([]);
  const [dropState, setDropState] = useState<DropZoneState>('idle');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<{ created: number; skipped?: number; errors: { row: number; detail: string }[] } | null>(null);
  const [inputDefs, setInputDefs] = useState<InputCodeDef[]>([]);
  const [inputDefsLoaded, setInputDefsLoaded] = useState(false);
  const [codeMap, setCodeMap] = useState<Map<string, string>>(new Map());

  useEffect(() => {
    if (!workspaceId) return;
    workspaceApi
      .getInputCodes(workspaceId)
      .then((data) => {
        setInputDefs(data.input_codes);
        setCodeMap(new Map(data.input_codes.map((d) => [d.code.toUpperCase(), d.code])));
        setInputDefsLoaded(true);
      })
      .catch(() => { setInputDefsLoaded(true); });
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
      const res = await api.post<{ created: number; skipped: number; errors: { row: number; detail: string }[] }>(
        `/${workspaceId}/payroll/inputs/bulk`,
        { rows: validRows },
      );
      setResult(res);
      if (res.created > 0) window.dispatchEvent(new Event('payroll-inputs-changed'));
      if (res.errors.length === 0) {
        const msg = [
          res.created > 0 ? `${res.created} input${res.created !== 1 ? 's' : ''} added` : null,
          res.skipped > 0 ? `${res.skipped} already exist — skipped` : null,
        ].filter(Boolean).join(', ') || 'No new inputs';
        toast.show('success', msg);
      } else {
        toast.show('warning', `${res.created} added, ${res.errors.length} failed — see details below`);
      }
    } catch (e: unknown) {
      setParseErrors([e instanceof Error ? e.message : 'Submission failed']);
      toast.show('error', 'Submission failed');
    } finally {
      setSubmitting(false);
    }
  }

  const validCount = rows.filter((r) => !r._error).length;
  const invalidCount = rows.length - validCount;

  // ── Native upload helpers (wide format: one column per input type × period) ───
  //
  // Column headers encode: "THE MONTH OF {MONTH} {YEAR} {INPUT TYPE} @ N{AMOUNT}"
  // Each non-empty cell = total amount paid → quantity = cell_value / payroll_rule_amount.
  // The @AMOUNT in the header IS the payroll rule rate (operator copies it from the rule).

  const INPUT_REQUIRED_TARGETS = useMemo(() => [
    { value: '__employee_no__', label: 'Employee Number / ID' },
  ], []);

  function buildInputMappings(headerRow: string[]): ColumnMapping[] {
    const allTargets = [
      { value: '__employee_no__', label: 'Employee Number (identifier)' },
      ...inputDefs.map((d: InputCodeDef) => ({ value: d.code, label: `${d.code} — ${d.rule_name}` })),
    ];

    // Deduplication: files often have a main input block followed by a reporting block
    // with the same headers. First occurrence of each {period+code} wins; duplicates
    // are auto-excluded so they don't emit double rows.
    let empMapped = false;
    const seenPeriodCode = new Set<string>();

    return headerRow.flatMap((cell, colIdx): ColumnMapping[] => {
      if (!cell.trim()) return [];
      const normalized = cell.trim().toUpperCase();

      // Employee identifier — only the first match is active
      if (EMP_NO_ALIASES.some((a) => normalized === a || normalized.includes(a))) {
        if (empMapped) {
          return [{ dataColIdx: colIdx, detectedHeader: cell, proposedTarget: null, status: 'excluded', availableTargets: allTargets }];
        }
        empMapped = true;
        return [{ dataColIdx: colIdx, detectedHeader: cell, proposedTarget: '__employee_no__', status: 'matched', availableTargets: allTargets }];
      }

      // Input column — pattern: THE MONTH OF {MONTH} {YEAR} {TYPE} @ N{AMOUNT}
      const { period, keyword } = parseInputColumnHeader(cell);
      if (period && keyword) {
        const matched = matchInputCode(keyword, inputDefs);
        // Deduplicate matched columns — unmatched columns pass through to let operator resolve
        const dedupKey = matched ? `${period}-${matched}` : null;
        const isDuplicate = dedupKey !== null && seenPeriodCode.has(dedupKey);
        if (dedupKey && !isDuplicate) seenPeriodCode.add(dedupKey);
        return [{
          dataColIdx: colIdx,
          detectedHeader: cell,
          proposedTarget: isDuplicate ? null : (matched ?? null),
          status: isDuplicate ? 'excluded' : (matched ? 'matched' : 'unresolved'),
          availableTargets: allTargets,
        }];
      }

      // Unrecognised column — exclude by default
      return [{ dataColIdx: colIdx, detectedHeader: cell, proposedTarget: null, status: 'excluded', availableTargets: allTargets }];
    });
  }

  function parseNativeInputRows(
    data: unknown[][],
    headerRowIndex: number,
    colMappings: ColumnMapping[],
  ): { rows: ParsedRow[]; errors: string[] } {
    const empMapping = colMappings.find((m) => m.status === 'matched' && m.proposedTarget === '__employee_no__');
    const inputMappings = colMappings.filter((m) => m.status === 'matched' && m.proposedTarget && m.proposedTarget !== '__employee_no__');

    if (!empMapping) return { rows: [], errors: ['Employee number column not found — map it in the panel above'] };
    if (inputMappings.length === 0) return { rows: [], errors: ['Could not detect input columns. Use the Template upload instead.'] };

    const parsedRows: ParsedRow[] = [];
    const errors: string[] = [];

    for (let ri = headerRowIndex + 1; ri < data.length; ri++) {
      const row = data[ri] as unknown[];
      if (row.every((c) => String(c ?? '').trim() === '')) continue;

      const employee_number = String(row[empMapping.dataColIdx] ?? '').trim();
      if (!employee_number) continue;

      for (const m of inputMappings) {
        const raw = String(row[m.dataColIdx] ?? '').trim();
        if (!raw || raw === '0') continue;
        const numVal = parseFloat(raw);
        if (isNaN(numVal) || numVal <= 0) continue;

        // quantity = cell_value / header_rate (@N1000.00 in the column header)
        const { period, amount: headerRate } = parseInputColumnHeader(m.detectedHeader);
        const reference_date = period ? `${period}-01` : undefined;
        const quantity = headerRate && headerRate > 0
          ? parseFloat((numVal / headerRate).toFixed(4))
          : numVal;

        parsedRows.push({ employee_number, input_code: m.proposedTarget!, quantity, reference_date });
      }
    }

    return { rows: parsedRows, errors };
  }

  function renderNativeInputPreview(rows: ParsedRow[], errors: string[]) {
    const valid   = rows.filter((r) => !r._error);
    const invalid = rows.filter((r) => r._error);
    return (
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold bg-green-100 text-green-800 px-2 py-0.5 rounded-full">
            {valid.length} rows ready
          </span>
          {invalid.length > 0 && (
            <span className="text-xs font-semibold bg-red-100 text-red-800 px-2 py-0.5 rounded-full">
              {invalid.length} with errors
            </span>
          )}
        </div>
        {errors.length > 0 && (
          <AlertBanner variant="warning"
            title={`${errors.length} row${errors.length !== 1 ? 's' : ''} have errors`}
            description={errors.slice(0, 3).join(' · ') + (errors.length > 3 ? ` +${errors.length - 3} more` : '')} />
        )}
        <div className="overflow-x-auto rounded-lg border border-gray-200 max-h-64">
          <table className="w-full text-xs">
            <thead className="bg-gray-50 sticky top-0">
              <tr>
                {['Employee No', 'Code', 'Qty', 'Period', 'Status'].map((h) => (
                  <th key={h} className="px-3 py-2 text-left text-[10px] font-semibold uppercase tracking-wider text-gray-500">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={i} className={`border-b border-gray-100 ${r._error ? 'bg-red-50' : ''}`}>
                  <td className="px-3 py-2 font-mono text-gray-700">{r.employee_number}</td>
                  <td className="px-3 py-2 font-mono text-gray-700">{r.input_code}</td>
                  <td className="px-3 py-2 tabular-nums text-gray-700">{r.quantity ?? '—'}</td>
                  <td className="px-3 py-2 text-gray-500">{r.reference_date?.slice(0, 7) ?? <span className="italic text-gray-400">current</span>}</td>
                  <td className="px-3 py-2">
                    {r._error
                      ? <span className="text-red-600">{r._error}</span>
                      : <span className="text-green-600">✓</span>
                    }
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  async function submitNativeInputRows(rows: ParsedRow[]) {
    if (!workspaceId || rows.length === 0) return { success: false, message: 'No rows to submit.' };
    try {
      const parseFailures = rows.filter((r) => r._error);
      const valid = rows.filter((r) => !r._error).map(({ _error: _e, ...r }) => r);
      const res = await api.post<{ created: number; skipped: number; errors: { row: number; detail: string }[] }>(
        `/${workspaceId}/payroll/inputs/bulk`,
        { rows: valid },
      );
      if (res.created > 0) window.dispatchEvent(new Event('payroll-inputs-changed'));

      const allFailed = [
        ...parseFailures.map((r, i) => ({
          name: `Row ${i + 2}`,
          employee_number: r.employee_number || `row-${i + 2}`,
          status: 'failed' as const,
          error: r._error,
        })),
        ...res.errors.map((e) => ({
          name: `Row ${e.row}`,
          employee_number: String(e.row),
          status: 'failed' as const,
          error: e.detail,
        })),
      ];

      const skipped = res.skipped || 0;
      const parts = [];
      if (res.created > 0) parts.push(`${res.created} added`);
      if (skipped > 0) parts.push(`${skipped} already exist — skipped`);
      if (allFailed.length > 0) parts.push(`${allFailed.length} failed`);
      const message = parts.length > 0 ? parts.join(', ') : 'No inputs processed';

      return {
        success: allFailed.length === 0,
        message,
        skippedCount: skipped,
        details: allFailed.length > 0 ? allFailed : undefined,
      };
    } catch (e: unknown) {
      return { success: false, message: e instanceof Error ? e.message : 'Submission failed' };
    }
  }

  const methods: Array<{ id: 'native' | 'template'; title: string; descriptor: string; icon: React.ReactNode }> = [
    {
      id: 'native',
      title: 'Client file',
      descriptor: 'Map columns from any spreadsheet',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75} aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
        </svg>
      ),
    },
    {
      id: 'template',
      title: 'Our template',
      descriptor: 'Download, fill, re-upload',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75} aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
        </svg>
      ),
    },
  ];

  const modeSelector = (
    <div className="grid grid-cols-2 gap-3 mb-6">
      {methods.map((method) => {
        const selected = uploadMode === method.id;
        return (
          <button
            key={method.id}
            type="button"
            aria-pressed={selected}
            onClick={() => setUploadMode(method.id)}
            className={[
              'relative flex flex-col gap-2 rounded-lg border p-3 text-left',
              'transition-all duration-150 focus:outline-none',
              'focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-1',
              selected
                ? 'border-brand bg-blue-50 shadow-sm'
                : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-slate-50',
            ].join(' ')}
          >
            {selected && (
              <span className="absolute top-2.5 right-2.5 flex h-4 w-4 items-center justify-center rounded-full bg-brand" aria-hidden="true">
                <svg className="w-2.5 h-2.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </span>
            )}
            <span className={selected ? 'text-brand' : 'text-gray-400'}>{method.icon}</span>
            <span className="flex flex-col gap-0.5 pr-5">
              <span className={`text-sm font-semibold leading-tight ${selected ? 'text-brand' : 'text-gray-700'}`}>
                {method.title}
              </span>
              <span className="text-xs text-gray-400 leading-snug">{method.descriptor}</span>
            </span>
          </button>
        );
      })}
    </div>
  );

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

      {modeSelector}

      {uploadMode === 'native' && (
        <Card>
          {!inputDefsLoaded ? (
            <div className="flex items-center gap-2 py-8 justify-center text-sm text-gray-400">
              <svg className="animate-spin w-4 h-4 text-brand" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              Loading input codes…
            </div>
          ) : (
            <NativeUploadFlow<ParsedRow>
              aliases={{}}
              minMatchesForAutoDetect={2}
              detectHeaderFn={(rows) => detectHeaderRowByScorer(
                rows,
                (row) => {
                  let count = 0;
                  for (const cell of row) {
                    const { period, keyword } = parseInputColumnHeader(String(cell ?? ''));
                    if (period && keyword && matchInputCode(keyword, inputDefs)) count++;
                  }
                  return count;
                },
              )}
              buildMappings={buildInputMappings}
              parseRows={parseNativeInputRows}
              renderPreview={renderNativeInputPreview}
              submitLabel={(n) => `Add ${n} input row${n !== 1 ? 's' : ''}`}
              onSubmit={submitNativeInputRows}
              onDone={() => navigate(`/workspaces/${workspaceId}/payroll/inputs`)}
              requiredTargets={INPUT_REQUIRED_TARGETS}
              allowDuplicateTargets={true}
            />
          )}
        </Card>
      )}

      {uploadMode === 'template' && (
        <>
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
        <div className="mt-4 space-y-3">
          {/* Layer 1 — status */}
          <AlertBanner
            variant={result.errors.length === 0 ? (result.skipped ? 'info' : 'success') : 'warning'}
            title={(() => {
              const parts = [];
              if (result.created > 0) parts.push(`${result.created} input${result.created !== 1 ? 's' : ''} added`);
              if (result.skipped) parts.push(`${result.skipped} already exist — skipped`);
              if (result.errors.length > 0) parts.push(`${result.errors.length} failed`);
              return parts.join(', ') || 'No inputs processed';
            })()}
            action={
              result.errors.length === 0
                ? { label: 'View in Inbox →', onClick: () => navigate(`/workspaces/${workspaceId}/payroll/inputs`) }
                : undefined
            }
          />

          {/* Layer 2 — action required */}
          {result.errors.length > 0 && (
            <div
              style={{ borderRadius: 'var(--radius-card)' }}
              className="border border-amber-200 bg-amber-50 p-4 space-y-3"
            >
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div>
                  <p className="text-sm font-semibold text-amber-900">Download before you close</p>
                  <p className="mt-0.5 text-sm text-amber-800">
                    {result.errors.length} {result.errors.length === 1 ? 'row' : 'rows'} weren't uploaded.
                    Save a copy now — fix them in your spreadsheet and re-upload whenever you're ready.
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => {
                  const csv = ['"Row","Error"',
                    ...result.errors.map((e) => `"${e.row}","${String(e.detail).replace(/"/g, '""')}"`)
                  ].join('\n');
                  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url; a.download = 'upload_errors.csv'; a.click();
                  URL.revokeObjectURL(url);
                }}
                className="flex items-center gap-2 px-4 py-2 rounded-md border border-amber-400 bg-white text-sm font-medium text-amber-800 hover:bg-amber-50 transition-colors focus:outline-none focus:ring-2 focus:ring-amber-400 focus:ring-offset-1"
              >
                <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Download error report ({result.errors.length} {result.errors.length === 1 ? 'row' : 'rows'})
              </button>
            </div>
          )}

          {/* Layer 3 — detail table */}
          {result.errors.length > 0 && (
            <div className="rounded-lg border border-red-100 overflow-auto max-h-56">
              <table className="w-full text-xs">
                <thead className="sticky top-0">
                  <tr className="bg-red-50 border-b border-red-100">
                    <th className="px-3 py-2 text-left font-semibold text-red-700 whitespace-nowrap">Row</th>
                    <th className="px-3 py-2 text-left font-semibold text-red-700">Error</th>
                  </tr>
                </thead>
                <tbody>
                  {result.errors.map((e, i) => (
                    <tr key={i} className="border-b border-red-50 last:border-0">
                      <td className="px-3 py-2 font-mono text-gray-700">{e.row}</td>
                      <td className="px-3 py-2 text-red-600">{e.detail}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
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
        </>
      )}
    </div>
  );
}
