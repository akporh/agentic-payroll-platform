import { useRef, useState } from 'react';
import * as XLSX from 'xlsx';
import { Card } from '../ui/Card';
import { Btn } from '../ui/Btn';
import { AlertBox } from '../ui/AlertBox';

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

// ── Helpers ───────────────────────────────────────────────────────────────────

/**
 * Convert an Excel cell value to a YYYY-MM-DD string.
 * When XLSX is read with `cellDates: true`, date cells arrive as JS Date objects.
 * CSV date columns arrive as plain strings (already YYYY-MM-DD).
 * Anything else is coerced to string and trimmed.
 */
function toISODate(val: unknown): string {
  if (val instanceof Date) {
    // Undo UTC-offset shift so the local calendar date is preserved.
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

  // Normalise header keys
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

  // Normalize: trim + uppercase + collapse spaces to underscores
  const norm = (s: string) => s.trim().toUpperCase().replace(/\s+/g, '_');

  normalised.forEach((row, i) => {
    const rowNum = i + 2;
    const employeeId = String(row['employee_id'] ?? '').trim();
    if (!employeeId) {
      errors.push(`Row ${rowNum}: employee_id is empty.`);
      return;
    }

    const grade = norm(String(row['grade'] ?? ''));
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
      first_name: String(row['first_name'] ?? '').trim(),
      last_name: String(row['last_name'] ?? '').trim(),
      grade,
      designation,
      tin: String(row['tin'] ?? '').trim(),
      rsa: String(row['rsa'] ?? '').trim(),
      bank: String(row['bank'] ?? '').trim(),
      account_number: String(row['account_number'] ?? '').trim(),
      contract_start,
      contract_end,
    });
  });

  return { employees, errors };
}

// ── Component ─────────────────────────────────────────────────────────────────

export function EmployeeUpload({ employees, onEmployeesLoaded }: Props) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [parseErrors, setParseErrors] = useState<string[]>([]);
  const [fileName, setFileName] = useState<string | null>(null);

  function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    setParseErrors([]);
    onEmployeesLoaded([]);

    const reader = new FileReader();
    reader.onload = (ev) => {
      try {
        const workbook = XLSX.read(ev.target?.result, { type: 'array', cellDates: true });
        const sheet = workbook.Sheets[workbook.SheetNames[0]];
        const rows = XLSX.utils.sheet_to_json<Record<string, unknown>>(sheet, { defval: '' });
        const { employees: parsed, errors } = parseSheetRows(rows);
        if (errors.length > 0) setParseErrors(errors);
        if (parsed.length > 0) onEmployeesLoaded(parsed);
      } catch {
        setParseErrors(['Failed to read file. Ensure it is a valid .xlsx or .csv.']);
      }
    };
    reader.readAsArrayBuffer(file);
    e.target.value = '';
  }

  const previewRows = employees.slice(0, 10);

  return (
    <div className="flex flex-col gap-4">
      {/* Upload card */}
      <Card title="Upload Employee File">
        <p className="text-xs text-slate-500 mb-2">
          Upload an <strong>.xlsx</strong> or <strong>.csv</strong> file.
          Employees are registered immediately — payroll structure is assigned separately after upload.
        </p>
        <p className="font-mono text-xs text-slate-400 bg-slate-50 rounded px-3 py-2 mb-4 leading-relaxed">
          employee_id · first_name · last_name · grade · designation
          <br />
          tin · rsa · bank · account_number
          <br />
          contract_start (YYYY-MM-DD, required) · contract_end (YYYY-MM-DD, optional)
        </p>

        <div className="flex items-center gap-3">
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,text/csv"
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

        {parseErrors.length > 0 && (
          <div className="mt-3">
            <AlertBox type="error" title="Parse Errors" messages={parseErrors} />
          </div>
        )}
        {employees.length > 0 && parseErrors.length === 0 && (
          <div className="mt-3">
            <AlertBox
              type="success"
              messages={[`${employees.length} employee${employees.length !== 1 ? 's' : ''} ready to register.`]}
            />
          </div>
        )}
      </Card>

      {/* Employee preview table */}
      {employees.length > 0 && (
        <Card
          title={`Employee Preview — ${employees.length} employees${employees.length > 10 ? ' (first 10)' : ''}`}
        >
          <div className="overflow-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-100">
                  <Th>#</Th>
                  <Th>ID</Th>
                  <Th>Name</Th>
                  <Th>Imported Grade</Th>
                  <Th>Imported Designation</Th>
                  <Th>Contract Start</Th>
                </tr>
              </thead>
              <tbody>
                {previewRows.map((emp, i) => (
                  <tr key={emp.employee_id} className="border-b border-slate-50">
                    <Td>{i + 1}</Td>
                    <Td>{emp.employee_id}</Td>
                    <Td>{emp.first_name} {emp.last_name}</Td>
                    <Td>
                      <span className="font-mono">{emp.grade || '—'}</span>
                    </Td>
                    <Td>
                      <span className="font-mono">{emp.designation || '—'}</span>
                    </Td>
                    <Td>
                      <span className="font-mono">{emp.contract_start}</span>
                      {emp.contract_end && (
                        <span className="text-slate-400"> → {emp.contract_end}</span>
                      )}
                    </Td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {employees.length > 10 && (
            <p className="text-xs text-slate-400 mt-2">
              + {employees.length - 10} more rows not shown.
            </p>
          )}
        </Card>
      )}
    </div>
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
