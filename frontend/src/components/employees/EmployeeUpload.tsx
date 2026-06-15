import { useState } from 'react';
import * as XLSX from 'xlsx';
import { FileDropZone, AlertBanner } from '../../design-system';
import type { DropZoneState } from '../../design-system';

// ── Types ─────────────────────────────────────────────────────────────────────

/** Raw row parsed from Excel. Grade and designation are stored as imported labels only. */
export interface EmployeeRow {
  employee_id: string;
  first_name: string;
  last_name: string;
  /** Raw grade value from Excel — stored as imported_grade_label, never sent as grade_code */
  grade: string;
  /** Raw designation value from Excel — stored as imported_designation_label */
  designation: string;
  tin: string;
  rsa: string;
  bank: string;
  account_number: string;
  /** ISO date YYYY-MM-DD — when this employee's contract started */
  contract_start: string;
  /** ISO date YYYY-MM-DD — when this employee's contract ends (empty = open-ended) */
  contract_end: string;
}

export interface SalaryDefinitionOption {
  salary_definition_id: string;
  code: string;
  name: string;
}

interface Props {
  employees: EmployeeRow[];
  onEmployeesLoaded: (employees: EmployeeRow[]) => void;
}

// ── Required Excel columns ────────────────────────────────────────────────────

const REQUIRED_COLS = [
  'employee_id',
  'first_name',
  'last_name',
  'grade',
  'designation',
  'tin',
  'rsa',
  'bank',
  'account_number',
  'contract_start',
] as const;

// ── Template download ─────────────────────────────────────────────────────────

export function downloadEmployeeTemplate() {
  const wb = XLSX.utils.book_new();
  const example = {
    employee_id:    'SMC-001',
    first_name:     'John',
    last_name:      'Doe',
    grade:          'MANAGER',
    designation:    'PROJECT MANAGER',
    tin:            '12345678-0001',
    rsa:            'PEN100123456789',
    bank:           'GTBANK',
    account_number: '0123456789',
    contract_start: '2024-01-01',
    contract_end:   '',
  };
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet([example]), 'Employees');
  XLSX.writeFile(wb, 'employee_upload_template.xlsx');
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function toISODate(val: unknown): string {
  if (val instanceof Date) {
    const d = new Date(val.getTime() - val.getTimezoneOffset() * 60000);
    return d.toISOString().slice(0, 10);
  }
  return String(val ?? '').trim();
}

// ── Excel parser ──────────────────────────────────────────────────────────────

function parseSheetRows(
  rows: Record<string, unknown>[],
): { employees: EmployeeRow[]; errors: string[] } {
  const errors: string[] = [];
  const employees: EmployeeRow[] = [];

  const normalised = rows.map((r) => {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(r)) {
      out[k.trim().toLowerCase()] = v;
    }
    return out;
  });

  if (normalised.length === 0) {
    errors.push('File contains no data rows.');
    return { employees, errors };
  }

  const firstRowKeys = Object.keys(normalised[0]);
  const missing = REQUIRED_COLS.filter((c) => !firstRowKeys.includes(c));
  if (missing.length > 0) {
    errors.push(`Missing columns: ${missing.join(', ')}`);
    return { employees, errors };
  }

  const norm = (s: string) => s.trim().toUpperCase().replace(/\s+/g, '_');

  normalised.forEach((row, i) => {
    const rowNum = i + 2;
    const employeeId = String(row['employee_id'] ?? '').trim();
    if (!employeeId) {
      errors.push(`Row ${rowNum}: employee_id is empty.`);
      return;
    }

    const grade       = norm(String(row['grade'] ?? ''));
    const designation = norm(String(row['designation'] ?? ''));
    const contract_start = toISODate(row['contract_start']);
    const contract_end   = toISODate(row['contract_end']);

    if (!contract_start) {
      errors.push(`Row ${rowNum}: contract_start is required (use YYYY-MM-DD).`);
      return;
    }
    if (isNaN(new Date(contract_start).getTime())) {
      errors.push(`Row ${rowNum}: contract_start '${contract_start}' is not a valid date (use YYYY-MM-DD).`);
      return;
    }
    if (contract_end) {
      if (isNaN(new Date(contract_end).getTime())) {
        errors.push(`Row ${rowNum}: contract_end '${contract_end}' is not a valid date (use YYYY-MM-DD).`);
        return;
      }
      if (contract_end < contract_start) {
        errors.push(`Row ${rowNum}: contract_end must be on or after contract_start.`);
        return;
      }
    }

    employees.push({
      employee_id: employeeId,
      first_name:  String(row['first_name'] ?? '').trim(),
      last_name:   String(row['last_name']  ?? '').trim(),
      grade,
      designation,
      tin:            String(row['tin']            ?? '').trim(),
      rsa:            String(row['rsa']            ?? '').trim(),
      bank:           String(row['bank']           ?? '').trim(),
      account_number: String(row['account_number'] ?? '').trim(),
      contract_start,
      contract_end,
    });
  });

  return { employees, errors };
}

// ── Component ─────────────────────────────────────────────────────────────────

export function EmployeeUpload({ employees, onEmployeesLoaded }: Props) {
  const [dropState, setDropState] = useState<DropZoneState>('idle');
  const [parseErrors, setParseErrors] = useState<string[]>([]);

  function handleFile(file: File) {
    setDropState('processing');
    setParseErrors([]);
    onEmployeesLoaded([]);

    const reader = new FileReader();
    reader.onload = (ev) => {
      try {
        const workbook = XLSX.read(ev.target?.result, { type: 'array', cellDates: true });
        const sheet = workbook.Sheets[workbook.SheetNames[0]];
        const rows = XLSX.utils.sheet_to_json<Record<string, unknown>>(sheet, { defval: '' });
        const { employees: parsed, errors } = parseSheetRows(rows);
        if (errors.length > 0) {
          setParseErrors(errors);
          setDropState('error');
        } else {
          setDropState('success');
        }
        if (parsed.length > 0) onEmployeesLoaded(parsed);
      } catch {
        setParseErrors(['Failed to read file. Make sure it is a valid .xlsx or .csv.']);
        setDropState('error');
      }
    };
    reader.readAsArrayBuffer(file);
  }

  const previewRows = employees.slice(0, 10);

  return (
    <div className="flex flex-col gap-4">
      <FileDropZone
        accept=".xlsx,.csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,text/csv"
        label="Drop your filled template here, or click to browse"
        hint="Accepted formats: .xlsx, .csv"
        state={dropState}
        successMessage={employees.length > 0 ? `${employees.length} employee${employees.length !== 1 ? 's' : ''} ready to register` : undefined}
        errorMessage={parseErrors.length > 0 ? parseErrors[0] : undefined}
        onFile={handleFile}
      />

      {parseErrors.length > 0 && (
        <>
          {/* Layer 2 — action required */}
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
                  {parseErrors.length} {parseErrors.length === 1 ? 'row' : 'rows'} in your file couldn't be read.
                  Save a copy now — fix them in your spreadsheet and re-upload whenever you're ready.
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => {
                const csv = ['"Error"', ...parseErrors.map((e) => `"${e.replace(/"/g, '""')}"`)]
                  .join('\n');
                const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'employee_upload_errors.csv';
                a.click();
                URL.revokeObjectURL(url);
              }}
              className="flex items-center gap-2 px-4 py-2 rounded-md border border-amber-400 bg-white text-sm font-medium text-amber-800 hover:bg-amber-50 transition-colors focus:outline-none focus:ring-2 focus:ring-amber-400 focus:ring-offset-1"
            >
              <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download error report ({parseErrors.length} {parseErrors.length === 1 ? 'error' : 'errors'})
            </button>
          </div>
          {/* Layer 3 — detail table */}
          <div className="rounded-lg border border-red-100 overflow-auto max-h-48">
            <table className="w-full text-xs">
              <tbody>
                {parseErrors.map((err, i) => (
                  <tr key={i} className="border-b border-red-50 last:border-0">
                    <td className="px-3 py-2 text-red-600">{err}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {employees.length > 0 && parseErrors.length === 0 && (
        <div className="overflow-x-auto rounded-lg border border-gray-200 max-h-56">
          <table className="w-full text-xs">
            <thead className="bg-gray-50 sticky top-0">
              <tr>
                {['ID', 'Name', 'Grade', 'Start Date'].map((h) => (
                  <th key={h} className="px-3 py-2 text-left text-[10px] font-semibold uppercase tracking-wider text-gray-500 whitespace-nowrap">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {previewRows.map((emp, i) => (
                <tr key={emp.employee_id} className={`border-b border-gray-100 ${i % 2 === 1 ? 'bg-gray-50/50' : ''}`}>
                  <td className="px-3 py-2 font-mono text-gray-700">{emp.employee_id}</td>
                  <td className="px-3 py-2 text-gray-700">{emp.first_name} {emp.last_name}</td>
                  <td className="px-3 py-2 text-gray-400 font-mono">{emp.grade || '—'}</td>
                  <td className="px-3 py-2 text-gray-400 font-mono">{emp.contract_start || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {employees.length > 10 && (
            <p className="px-3 py-2 text-xs text-gray-400">
              + {employees.length - 10} more rows not shown
            </p>
          )}
        </div>
      )}
    </div>
  );
}
