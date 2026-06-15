import { useMemo, useState } from 'react';
import * as XLSX from 'xlsx';
import { FileDropZone, Btn, AlertBanner } from '../../design-system';
import { ColumnMappingPanel } from './ColumnMappingPanel';
import type { ColumnMapping } from './ColumnMappingPanel';
import type { AliasMap } from '../../utils/nativeExcelParser';
import {
  detectHeaderRow,
  forwardFillRow,
} from '../../utils/nativeExcelParser';

export interface SubmitResultDetail {
  name: string;
  employee_number: string;
  status: 'created' | 'skipped' | 'failed';
  error?: string;
}

export interface SubmitResult {
  success: boolean;
  message: string;
  details?: SubmitResultDetail[];
  /** For upload flows where the API returns a bulk skip count (e.g. period inputs) rather than per-row skipped details. */
  skippedCount?: number;
}

export interface NativeUploadFlowProps<TRow> {
  aliases: AliasMap;
  minMatchesForAutoDetect: number;
  /** Optional override for header detection — used when alias-based scoring doesn't apply */
  detectHeaderFn?: (rows: unknown[][]) => { rowIndex: number; confidence: number };
  buildMappings: (headerRow: string[]) => ColumnMapping[];
  parseRows: (
    data: unknown[][],
    headerRowIndex: number,
    mappings: ColumnMapping[],
  ) => { rows: TRow[]; errors: string[] };
  renderPreview: (rows: TRow[], errors: string[]) => React.ReactNode;
  /** Static label or a function receiving the parsed row count — e.g. (n) => `Add ${n} input rows` */
  submitLabel: string | ((count: number) => string);
  onSubmit: (rows: TRow[]) => Promise<SubmitResult>;
  onDone: () => void;
  /**
   * When provided, Continue is gated on ALL of these system fields being matched —
   * not on client-column resolution. Add new fields here as the data model grows.
   */
  requiredTargets?: { value: string; label: string }[];
  /** Useful but not blocking — shown in the checklist with muted styling. */
  optionalTargets?: { value: string; label: string }[];
  /** Pass true for period inputs — multiple columns legitimately share the same input_code. */
  allowDuplicateTargets?: boolean;
}

type Step = 'drop' | 'row-picker' | 'mapping' | 'preview' | 'submitting' | 'done';

function downloadErrorsCsv(filename: string, headers: string[], rows: string[][]): void {
  const csv = [headers, ...rows]
    .map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(','))
    .join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// NativeUploadFlow drives the full drop→map→preview→submit flow.
// Each feature supplies its own alias map, row builder, and submit handler.
export function NativeUploadFlow<TRow>({
  aliases,
  minMatchesForAutoDetect,
  detectHeaderFn,
  buildMappings,
  parseRows,
  renderPreview,
  submitLabel,
  onSubmit,
  onDone,
  requiredTargets,
  optionalTargets,
  allowDuplicateTargets,
}: NativeUploadFlowProps<TRow>) {
  const [step, setStep] = useState<Step>('drop');
  const [allRows, setAllRows] = useState<unknown[][]>([]);
  const [headerRowIndex, setHeaderRowIndex] = useState(0);
  const [lastRow, setLastRow] = useState(0);           // 1-based; 0 = not yet set
  const [mappings, setMappings] = useState<ColumnMapping[]>([]);
  const [parsedRows, setParsedRows] = useState<TRow[]>([]);
  const [parseErrors, setParsedErrors] = useState<string[]>([]);
  const [submitResult, setSubmitResult] = useState<SubmitResult | null>(null);
  const [dropError, setDropError] = useState<string | null>(null);

  const canContinue = useMemo(() => {
    // Unresolved columns always block continuation regardless of required targets
    if (mappings.some((m) => m.status === 'unresolved')) return false;
    if (requiredTargets && requiredTargets.length > 0) {
      const matched = new Set(
        mappings
          .filter((m) => m.status === 'matched' && m.proposedTarget)
          .map((m) => m.proposedTarget!),
      );
      return requiredTargets.every((t) => matched.has(t.value));
    }
    return true;
  }, [mappings, requiredTargets]);

  function commitHeaderRow(rowIdx: number, rows: unknown[][]) {
    const headerRow = forwardFillRow(rows[rowIdx]);
    setHeaderRowIndex(rowIdx);
    setLastRow(rows.length);        // default: import all rows
    setMappings(buildMappings(headerRow));
    setStep('mapping');
  }

  function handleFile(file: File) {
    setDropError(null);
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext !== 'xlsx' && ext !== 'xls') {
      setDropError('Only .xlsx and .xls files are accepted.');
      return;
    }

    const reader = new FileReader();
    reader.onload = (ev) => {
      try {
        const wb = XLSX.read(ev.target?.result, { type: 'array', cellDates: true });
        const sheet = wb.Sheets[wb.SheetNames[0]];
        const raw = XLSX.utils.sheet_to_json<unknown[]>(sheet, { header: 1, defval: '' }) as unknown[][];
        setAllRows(raw);

        const detected = detectHeaderFn
          ? detectHeaderFn(raw)
          : detectHeaderRow(raw, aliases);
        if (detected.confidence >= minMatchesForAutoDetect) {
          commitHeaderRow(detected.rowIndex, raw);
        } else {
          setStep('row-picker');
        }
      } catch {
        setDropError('Failed to read file. Make sure it is a valid Excel file.');
      }
    };
    reader.readAsArrayBuffer(file);
  }

  function handleMappingConfirm() {
    // slice to the user-specified last row (1-based, so slice(0, lastRow) is correct)
    const data = lastRow > 0 && lastRow < allRows.length ? allRows.slice(0, lastRow) : allRows;
    const { rows, errors } = parseRows(data, headerRowIndex, mappings);
    setParsedRows(rows);
    setParsedErrors(errors);
    setStep('preview');
  }

  async function handleSubmit() {
    setStep('submitting');
    const result = await onSubmit(parsedRows);
    setSubmitResult(result);
    setStep('done');
  }

  // ── Drop ──────────────────────────────────────────────────────────────────
  if (step === 'drop') {
    return (
      <div className="space-y-3">
        {dropError && (
          <AlertBanner variant="error" title={dropError} />
        )}
        <FileDropZone
          accept=".xlsx,.xls,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel"
          label="Drop your Excel file here, or click to browse"
          hint="Accepted formats: .xlsx, .xls"
          state="idle"
          onFile={handleFile}
        />
      </div>
    );
  }

  // ── Row picker ────────────────────────────────────────────────────────────
  if (step === 'row-picker') {
    const preview = allRows.slice(0, 15);
    return (
      <div className="space-y-3">
        <AlertBanner
          variant="info"
          title="Could not auto-detect the header row"
          description="Click 'Use as header' on the row that contains column names."
        />
        <div className="overflow-x-auto rounded-lg border border-gray-200">
          <table className="w-full text-xs">
            <tbody>
              {preview.map((row, i) => (
                <tr key={i} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="px-3 py-2 text-gray-400 w-8">{i + 1}</td>
                  {(row as unknown[]).slice(0, 6).map((cell, j) => (
                    <td key={j} className="px-3 py-2 text-gray-700 max-w-[120px] truncate">
                      {String(cell ?? '')}
                    </td>
                  ))}
                  <td className="px-3 py-2">
                    <button
                      type="button"
                      className="text-xs text-brand underline hover:opacity-80 whitespace-nowrap"
                      onClick={() => commitHeaderRow(i, allRows)}
                    >
                      Use as header
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  // ── Mapping ───────────────────────────────────────────────────────────────
  if (step === 'mapping') {
    const firstDataRow = headerRowIndex + 2;   // 1-based: header row + 1
    const totalRows    = allRows.length;        // 1-based count

    function handleLastRowChange(raw: string) {
      const n = parseInt(raw, 10);
      if (isNaN(n)) return;
      setLastRow(Math.max(firstDataRow, Math.min(totalRows, n)));
    }

    return (
      <div className="space-y-4">
        <ColumnMappingPanel
          mappings={mappings}
          onChange={setMappings}
          requiredTargets={requiredTargets}
          optionalTargets={optionalTargets}
          allowDuplicateTargets={allowDuplicateTargets}
        />

        {/* Row range selector */}
        <div className="flex items-center gap-2 rounded-lg border border-gray-200 bg-gray-50 px-4 py-2.5 text-sm">
          <svg className="w-4 h-4 text-gray-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 7h18M3 12h18M3 17h18" />
          </svg>
          <span className="text-gray-500 whitespace-nowrap">Import rows</span>
          <span className="font-medium text-gray-700 whitespace-nowrap">{firstDataRow}</span>
          <span className="text-gray-400">—</span>
          <input
            type="number"
            min={firstDataRow}
            max={totalRows}
            value={lastRow || totalRows}
            onChange={(e) => handleLastRowChange(e.target.value)}
            aria-label="Last row to import"
            className="w-20 rounded border border-gray-300 bg-white px-2 py-0.5 text-center text-sm focus:outline-none focus:ring-1 focus:ring-brand"
          />
          <span className="text-gray-400 whitespace-nowrap">of {totalRows} rows</span>
          {(lastRow > 0 && lastRow < totalRows) && (
            <button
              type="button"
              className="ml-auto text-xs text-brand underline hover:opacity-80 whitespace-nowrap"
              onClick={() => setLastRow(totalRows)}
            >
              Import all
            </button>
          )}
        </div>

        <div className="flex items-center gap-3 pt-2">
          <Btn
            variant="primary"
            size="md"
            disabled={!canContinue}
            onClick={handleMappingConfirm}
          >
            Continue
          </Btn>
          <Btn variant="secondary" size="sm" onClick={() => setStep('drop')}>
            Back
          </Btn>
        </div>
      </div>
    );
  }

  // ── Preview ───────────────────────────────────────────────────────────────
  if (step === 'preview') {
    return (
      <div className="space-y-4">
        {renderPreview(parsedRows, parseErrors)}
        <div className="flex items-center gap-3 pt-2">
          <Btn
            variant="primary"
            size="md"
            disabled={parsedRows.length === 0}
            onClick={handleSubmit}
          >
            {typeof submitLabel === 'function' ? submitLabel(parsedRows.length) : submitLabel}
          </Btn>
          <Btn variant="secondary" size="sm" onClick={() => setStep('mapping')}>
            Back
          </Btn>
        </div>
      </div>
    );
  }

  // ── Submitting ────────────────────────────────────────────────────────────
  if (step === 'submitting') {
    return (
      <div className="flex items-center gap-2 py-6 justify-center text-sm text-gray-500">
        <svg className="animate-spin w-4 h-4 text-brand" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
        </svg>
        Submitting…
      </div>
    );
  }

  // ── Done ──────────────────────────────────────────────────────────────────
  if (submitResult) {
    const failedDetails = submitResult.details?.filter((d) => d.status === 'failed') ?? [];
    const skippedCount =
      submitResult.skippedCount ??
      (submitResult.details?.filter((d) => d.status === 'skipped').length ?? 0);

    return (
      <div className="space-y-4">
        {/* Layer 1 — status: what happened */}
        <AlertBanner
          variant={submitResult.success ? 'success' : failedDetails.length > 0 ? 'warning' : 'error'}
          title={submitResult.message}
        />
        {skippedCount > 0 && (
          <AlertBanner variant="info" title={`${skippedCount} already exist — skipped`} />
        )}

        {/* Layer 2 — action required: what to do */}
        {failedDetails.length > 0 && (
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
                  {failedDetails.length} {failedDetails.length === 1 ? 'row' : 'rows'} weren't uploaded.
                  Save a copy now — fix them in your spreadsheet and re-upload whenever you're ready.
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={() =>
                downloadErrorsCsv(
                  'upload_errors.csv',
                  ['Reference', 'Name', 'Error'],
                  failedDetails.map((d) => [d.employee_number, d.name, d.error ?? 'Unknown error']),
                )
              }
              className="flex items-center gap-2 px-4 py-2 rounded-md border border-amber-400 bg-white text-sm font-medium text-amber-800 hover:bg-amber-50 transition-colors focus:outline-none focus:ring-2 focus:ring-amber-400 focus:ring-offset-1"
            >
              <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download error report ({failedDetails.length} {failedDetails.length === 1 ? 'row' : 'rows'})
            </button>
          </div>
        )}

        {/* Layer 3 — detail: reference table */}
        {failedDetails.length > 0 && (
          <div className="rounded-lg border border-red-100 overflow-auto max-h-56">
            <table className="w-full text-xs">
              <thead className="sticky top-0">
                <tr className="bg-red-50 border-b border-red-100">
                  <th className="px-3 py-2 text-left font-semibold text-red-700 whitespace-nowrap">Reference</th>
                  <th className="px-3 py-2 text-left font-semibold text-red-700">Reason</th>
                </tr>
              </thead>
              <tbody>
                {failedDetails.map((d, i) => (
                  <tr key={i} className="border-b border-red-50 last:border-0">
                    <td className="px-3 py-2 text-gray-700 whitespace-nowrap">
                      {d.name}
                      {d.name !== d.employee_number && (
                        <span className="ml-1 font-mono text-gray-400">({d.employee_number})</span>
                      )}
                    </td>
                    <td className="px-3 py-2 text-red-600">{d.error ?? 'Unknown error'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <Btn variant="secondary" size="md" onClick={onDone}>
          {submitResult.success ? 'Done' : 'Close'}
        </Btn>
      </div>
    );
  }

  return null;
}
