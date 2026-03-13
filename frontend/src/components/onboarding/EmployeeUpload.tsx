import { useRef, useState } from 'react';
import * as XLSX from 'xlsx';
import { Card } from '../ui/Card';
import { Btn } from '../ui/Btn';
import { AlertBox } from '../ui/AlertBox';

// ── Types ─────────────────────────────────────────────────────────────────────

/** Raw row parsed from Excel — no salary fields, no salary_definition_code yet. */
export interface EmployeeRow {
  employee_id: string;
  first_name: string;
  last_name: string;
  grade: string;
  designation: string;
  tin: string;
  rsa: string;
  bank: string;
  account_number: string;
}

/** EmployeeRow enriched with a resolved (or manually selected) salary code. */
export interface MappedEmployee extends EmployeeRow {
  salary_definition_code: string;
  /** true when the auto-generated code was not found in workspace definitions */
  mapping_unresolved: boolean;
}

export interface SalaryDefinitionOption {
  salary_definition_id: string;
  code: string;
  name: string;
}

interface Props {
  employees: MappedEmployee[];
  salaryDefinitions: SalaryDefinitionOption[];
  onEmployeesLoaded: (employees: MappedEmployee[]) => void;
  onMappingChange: (employees: MappedEmployee[]) => void;
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
] as const;

// ── Code derivation ───────────────────────────────────────────────────────────

export function deriveCode(designation: string, grade: string): string {
  return `${designation.trim().toUpperCase()}_${grade.trim().toUpperCase()}`;
}

// ── Excel parser ──────────────────────────────────────────────────────────────

function parseSheetRows(
  rows: Record<string, unknown>[],
  salaryDefinitions: SalaryDefinitionOption[],
): { employees: MappedEmployee[]; errors: string[] } {
  const errors: string[] = [];
  const employees: MappedEmployee[] = [];

  const knownCodes = new Set(salaryDefinitions.map((sd) => sd.code));

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

  normalised.forEach((row, i) => {
    const rowNum = i + 2;
    const employeeId = String(row['employee_id'] ?? '').trim();
    if (!employeeId) {
      errors.push(`Row ${rowNum}: employee_id is empty.`);
      return;
    }

    const grade = String(row['grade'] ?? '').trim();
    const designation = String(row['designation'] ?? '').trim();
    const auto_code = deriveCode(designation, grade);
    const mapping_unresolved = !knownCodes.has(auto_code);

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
      salary_definition_code: auto_code,
      mapping_unresolved,
    });
  });

  return { employees, errors };
}

// ── Component ─────────────────────────────────────────────────────────────────

export function EmployeeUpload({
  employees,
  salaryDefinitions,
  onEmployeesLoaded,
  onMappingChange,
}: Props) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [parseErrors, setParseErrors] = useState<string[]>([]);
  const [fileName, setFileName] = useState<string | null>(null);

  function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    setParseErrors([]);

    const reader = new FileReader();
    reader.onload = (ev) => {
      try {
        const workbook = XLSX.read(ev.target?.result, { type: 'array' });
        const sheet = workbook.Sheets[workbook.SheetNames[0]];
        const rows = XLSX.utils.sheet_to_json<Record<string, unknown>>(sheet, { defval: '' });
        const { employees: parsed, errors } = parseSheetRows(rows, salaryDefinitions);
        if (errors.length > 0) setParseErrors(errors);
        if (parsed.length > 0) onEmployeesLoaded(parsed);
      } catch {
        setParseErrors(['Failed to read file. Ensure it is a valid .xlsx or .csv.']);
      }
    };
    reader.readAsArrayBuffer(file);
    e.target.value = '';
  }

  function handleCodeChange(employeeId: string, newCode: string) {
    const updated = employees.map((emp) =>
      emp.employee_id === employeeId
        ? { ...emp, salary_definition_code: newCode, mapping_unresolved: false }
        : emp
    );
    onMappingChange(updated);
  }

  const unresolvedCount = employees.filter((e) => e.mapping_unresolved).length;
  const previewRows = employees.slice(0, 10);

  return (
    <div className="flex flex-col gap-4">
      {/* Upload card */}
      <Card title="Upload Employee File">
        <p className="text-xs text-slate-500 mb-2">
          Upload an <strong>.xlsx</strong> or <strong>.csv</strong> file.
          Salary structures are mapped automatically from grade + designation.
        </p>
        <p className="font-mono text-xs text-slate-400 bg-slate-50 rounded px-3 py-2 mb-4 leading-relaxed">
          employee_id · first_name · last_name · grade · designation
          <br />
          tin · rsa · bank · account_number
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
              messages={[`${employees.length} employee${employees.length !== 1 ? 's' : ''} loaded.`]}
            />
          </div>
        )}
      </Card>

      {/* Mapping review table */}
      {employees.length > 0 && (
        <Card
          title={`Salary Structure Mapping — ${employees.length} employees${employees.length > 10 ? ' (showing first 10)' : ''}`}
        >
          {unresolvedCount > 0 && (
            <div className="mb-3">
              <AlertBox
                type="warning"
                title={`${unresolvedCount} unresolved mapping${unresolvedCount !== 1 ? 's' : ''}`}
                messages={[
                  'These codes were not found in the workspace salary definitions. ' +
                  'Select a valid structure from the dropdown or add the definition in your config JSON.',
                ]}
              />
            </div>
          )}

          <div className="overflow-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-100">
                  <Th>#</Th>
                  <Th>ID</Th>
                  <Th>Name</Th>
                  <Th>Grade</Th>
                  <Th>Designation</Th>
                  <Th>Salary Structure</Th>
                </tr>
              </thead>
              <tbody>
                {previewRows.map((emp, i) => (
                  <tr
                    key={emp.employee_id}
                    className={`border-b border-slate-50 ${emp.mapping_unresolved ? 'bg-amber-50' : ''}`}
                  >
                    <Td>{i + 1}</Td>
                    <Td>{emp.employee_id}</Td>
                    <Td>{emp.first_name} {emp.last_name}</Td>
                    <Td>{emp.grade}</Td>
                    <Td>{emp.designation}</Td>
                    <Td>
                      {salaryDefinitions.length > 0 ? (
                        <select
                          value={emp.salary_definition_code}
                          onChange={(e) => handleCodeChange(emp.employee_id, e.target.value)}
                          className={`border rounded px-2 py-0.5 text-xs focus:outline-none focus:ring-1 focus:ring-slate-400 ${
                            emp.mapping_unresolved
                              ? 'border-amber-400 bg-amber-50'
                              : 'border-slate-200 bg-white'
                          }`}
                        >
                          {emp.mapping_unresolved && (
                            <option value={emp.salary_definition_code} disabled>
                              {emp.salary_definition_code} (not found)
                            </option>
                          )}
                          {salaryDefinitions.map((sd) => (
                            <option key={sd.code} value={sd.code}>
                              {sd.code}{sd.name ? ` — ${sd.name}` : ''}
                            </option>
                          ))}
                        </select>
                      ) : (
                        <span
                          className={`font-mono ${emp.mapping_unresolved ? 'text-amber-600' : 'text-green-700'}`}
                        >
                          {emp.salary_definition_code}
                          {emp.mapping_unresolved && ' ⚠'}
                        </span>
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
              All mappings apply to the full set.
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
