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
  /** ISO date YYYY-MM-DD — when this employee's contract started */
  contract_start: string;
  /** ISO date YYYY-MM-DD — when this employee's contract ends (empty = open-ended) */
  contract_end: string;
}

/** EmployeeRow enriched with a resolved (or manually selected) salary code. */
export interface MappedEmployee extends EmployeeRow {
  salary_definition_code: string;
  /** true when the grade code was not found in workspace salary definitions */
  mapping_unresolved: boolean;
  /** true when the designation value was not found in workspace designations */
  designation_unresolved: boolean;
}

export interface SalaryDefinitionOption {
  salary_definition_id: string;
  code: string;
  name: string;
}

interface Props {
  employees: MappedEmployee[];
  salaryDefinitions: SalaryDefinitionOption[];
  designationOptions?: string[];
  onEmployeesLoaded: (employees: MappedEmployee[]) => void;
  onMappingChange: (employees: MappedEmployee[]) => void;
  onCreateSalaryDefinition?: (code: string) => Promise<SalaryDefinitionOption>;
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
  salaryDefinitions: SalaryDefinitionOption[],
  designationOptions: string[],
): { employees: MappedEmployee[]; errors: string[] } {
  const errors: string[] = [];
  const employees: MappedEmployee[] = [];

  const knownCodes = new Set(salaryDefinitions.map((sd) => sd.code));
  const knownDesignations = new Set(designationOptions);

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
    // Salary def codes are grade-based (e.g. "STEP_1B", "STEP_1_DRIVER").
    // The grade column in the Excel IS the salary def code.
    const auto_code = grade;
    const mapping_unresolved = !knownCodes.has(auto_code);
    const designation_unresolved = knownDesignations.size > 0 && !knownDesignations.has(designation);

    // Validate contract dates
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
      salary_definition_code: auto_code,
      mapping_unresolved,
      designation_unresolved,
    });
  });

  return { employees, errors };
}

// ── Combo key ─────────────────────────────────────────────────────────────────

function comboKey(grade: string, designation: string) {
  return `${grade}||${designation}`;
}

// ── Component ─────────────────────────────────────────────────────────────────

export function EmployeeUpload({
  employees,
  salaryDefinitions,
  designationOptions = [],
  onEmployeesLoaded,
  onMappingChange,
  onCreateSalaryDefinition,
}: Props) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [parseErrors, setParseErrors] = useState<string[]>([]);
  const [fileName, setFileName] = useState<string | null>(null);

  // Per-combo pending salary code selections (before Apply is clicked)
  const [pendingMap, setPendingMap] = useState<Record<string, string>>({});
  // Per-raw-designation pending canonical selections
  const [pendingDesignationMap, setPendingDesignationMap] = useState<Record<string, string>>({});
  // Grade codes currently being created
  const [creatingCodes, setCreatingCodes] = useState<Set<string>>(new Set());

  function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    setParseErrors([]);
    setPendingMap({});
    setPendingDesignationMap({});
    setCreatingCodes(new Set());
    onEmployeesLoaded([]);

    const reader = new FileReader();
    reader.onload = (ev) => {
      try {
        const workbook = XLSX.read(ev.target?.result, { type: 'array', cellDates: true });
        const sheet = workbook.Sheets[workbook.SheetNames[0]];
        const rows = XLSX.utils.sheet_to_json<Record<string, unknown>>(sheet, { defval: '' });
        const { employees: parsed, errors } = parseSheetRows(rows, salaryDefinitions, designationOptions);
        if (errors.length > 0) setParseErrors(errors);
        if (parsed.length > 0) onEmployeesLoaded(parsed);
      } catch {
        setParseErrors(['Failed to read file. Ensure it is a valid .xlsx or .csv.']);
      }
    };
    reader.readAsArrayBuffer(file);
    e.target.value = '';
  }

  function handlePendingChange(key: string, code: string) {
    setPendingMap((prev) => ({ ...prev, [key]: code }));
  }

  function applyGroupMapping(key: string, code: string) {
    const [rawGrade, rawDesignation] = key.split('||');
    const updated = employees.map((emp) =>
      emp.grade === rawGrade && emp.designation === rawDesignation
        ? { ...emp, salary_definition_code: code, mapping_unresolved: false }
        : emp
    );
    onMappingChange(updated);
    setPendingMap((prev) => {
      const next = { ...prev };
      delete next[key];
      return next;
    });
  }

  function applyAllPending() {
    let updated = [...employees];
    for (const [key, code] of Object.entries(pendingMap)) {
      if (!code) continue;
      const [rawGrade, rawDesignation] = key.split('||');
      updated = updated.map((emp) =>
        emp.grade === rawGrade && emp.designation === rawDesignation
          ? { ...emp, salary_definition_code: code, mapping_unresolved: false }
          : emp
      );
    }
    onMappingChange(updated);
    setPendingMap({});
  }

  async function handleCreateSalaryDef(grade: string) {
    if (!onCreateSalaryDefinition) return;
    setCreatingCodes((prev) => new Set(prev).add(grade));
    try {
      await onCreateSalaryDefinition(grade);
      // Mark all employees with this grade as resolved
      const updated = employees.map((emp) =>
        emp.grade === grade && emp.mapping_unresolved
          ? { ...emp, mapping_unresolved: false }
          : emp
      );
      onMappingChange(updated);
    } finally {
      setCreatingCodes((prev) => {
        const next = new Set(prev);
        next.delete(grade);
        return next;
      });
    }
  }

  function handleDesignationPendingChange(rawDesignation: string, canonical: string) {
    setPendingDesignationMap((prev) => ({ ...prev, [rawDesignation]: canonical }));
  }

  function applyDesignationMapping(rawDesignation: string, canonical: string) {
    const updated = employees.map((emp) =>
      emp.designation === rawDesignation
        ? { ...emp, designation: canonical, designation_unresolved: false }
        : emp
    );
    onMappingChange(updated);
    setPendingDesignationMap((prev) => {
      const next = { ...prev };
      delete next[rawDesignation];
      return next;
    });
  }

  function applyAllDesignationPending() {
    let updated = [...employees];
    for (const [rawDesignation, canonical] of Object.entries(pendingDesignationMap)) {
      if (!canonical) continue;
      updated = updated.map((emp) =>
        emp.designation === rawDesignation
          ? { ...emp, designation: canonical, designation_unresolved: false }
          : emp
      );
    }
    onMappingChange(updated);
    setPendingDesignationMap({});
  }

  // Build unique unresolved salary def combos
  const unresolvedCombos: { key: string; grade: string; designation: string; count: number }[] = [];
  const seenCombos = new Set<string>();
  for (const emp of employees) {
    if (!emp.mapping_unresolved) continue;
    const key = comboKey(emp.grade, emp.designation);
    if (seenCombos.has(key)) {
      const existing = unresolvedCombos.find((c) => c.key === key);
      if (existing) existing.count++;
    } else {
      seenCombos.add(key);
      unresolvedCombos.push({ key, grade: emp.grade, designation: emp.designation, count: 1 });
    }
  }

  // Build unique unresolved designation combos
  const designationUnresolvedCombos: { rawDesignation: string; count: number }[] = [];
  const seenDesignations = new Set<string>();
  for (const emp of employees) {
    if (!emp.designation_unresolved) continue;
    if (seenDesignations.has(emp.designation)) {
      const existing = designationUnresolvedCombos.find((c) => c.rawDesignation === emp.designation);
      if (existing) existing.count++;
    } else {
      seenDesignations.add(emp.designation);
      designationUnresolvedCombos.push({ rawDesignation: emp.designation, count: 1 });
    }
  }

  const unresolvedCount = employees.filter((e) => e.mapping_unresolved).length;
  const pendingCount = Object.values(pendingMap).filter(Boolean).length;
  const pendingDesignationCount = Object.values(pendingDesignationMap).filter(Boolean).length;
  const previewRows = employees.slice(0, 10);

  return (
    <div className="flex flex-col gap-4">
      {/* Upload card */}
      <Card title="Upload Employee File">
        <p className="text-xs text-slate-500 mb-2">
          Upload an <strong>.xlsx</strong> or <strong>.csv</strong> file.
          Salary structures are matched automatically from the grade column.
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
              messages={[`${employees.length} employee${employees.length !== 1 ? 's' : ''} loaded.`]}
            />
          </div>
        )}
      </Card>

      {/* Salary def mapping panel */}
      {unresolvedCombos.length > 0 && (
        <Card title={`Resolve Salary Mappings — ${unresolvedCombos.length} unmatched grade${unresolvedCombos.length !== 1 ? 's' : ''} (${unresolvedCount} employees)`}>
          <p className="text-xs text-slate-500 mb-3">
            Each grade below has no matching salary definition. Select an existing one or create a new salary definition for that grade code.
          </p>

          <div className="space-y-2 mb-3">
            {unresolvedCombos.map(({ key, grade, designation, count }) => (
              <div
                key={key}
                className="flex flex-col gap-2 px-3 py-2 bg-amber-50 border border-amber-200 rounded-lg"
              >
                <div>
                  <span className="font-mono text-xs font-semibold text-slate-700">{designation}</span>
                  <span className="text-slate-400 text-xs mx-1.5">·</span>
                  <span className="font-mono text-xs text-slate-600">{grade}</span>
                  <span className="ml-2 text-xs text-amber-600">({count} employee{count !== 1 ? 's' : ''})</span>
                </div>
                <div className="flex items-center gap-2">
                  {salaryDefinitions.length > 0 && (
                    <select
                      value={pendingMap[key] ?? ''}
                      onChange={(e) => handlePendingChange(key, e.target.value)}
                      className="flex-1 border border-amber-300 rounded px-2 py-1 text-xs bg-white focus:outline-none focus:ring-1 focus:ring-amber-400"
                    >
                      <option value="">— select existing —</option>
                      {salaryDefinitions.map((sd) => (
                        <option key={sd.code} value={sd.code}>
                          {sd.code}{sd.name ? ` — ${sd.name}` : ''}
                        </option>
                      ))}
                    </select>
                  )}
                  <button
                    onClick={() => {
                      const code = pendingMap[key];
                      if (code) applyGroupMapping(key, code);
                    }}
                    disabled={!pendingMap[key]}
                    className="px-2.5 py-1 text-xs font-medium bg-slate-700 text-white rounded hover:bg-slate-600 disabled:opacity-30 disabled:cursor-not-allowed whitespace-nowrap"
                  >
                    Apply
                  </button>
                  {onCreateSalaryDefinition && (
                    <button
                      onClick={() => handleCreateSalaryDef(grade)}
                      disabled={creatingCodes.has(grade)}
                      className="px-2.5 py-1 text-xs font-medium bg-emerald-700 text-white rounded hover:bg-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
                    >
                      {creatingCodes.has(grade) ? 'Creating…' : `+ Create "${grade}"`}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          {pendingCount > 0 && (
            <button
              onClick={applyAllPending}
              className="w-full py-2 text-xs font-semibold bg-amber-700 text-white rounded-lg hover:bg-amber-600"
            >
              Apply All ({pendingCount} of {unresolvedCombos.length} selected)
            </button>
          )}
        </Card>
      )}

      {/* Designation resolution panel */}
      {designationUnresolvedCombos.length > 0 && designationOptions.length > 0 && (
        <Card title={`Resolve Designations — ${designationUnresolvedCombos.length} unrecognised value${designationUnresolvedCombos.length !== 1 ? 's' : ''}`}>
          <p className="text-xs text-slate-500 mb-3">
            Each designation below doesn't match a workspace designation code. Select the correct canonical designation.
          </p>

          <div className="space-y-2 mb-3">
            {designationUnresolvedCombos.map(({ rawDesignation, count }) => (
              <div
                key={rawDesignation}
                className="flex flex-col gap-2 px-3 py-2 bg-blue-50 border border-blue-200 rounded-lg"
              >
                <div>
                  <span className="font-mono text-xs font-semibold text-slate-700">{rawDesignation}</span>
                  <span className="ml-2 text-xs text-blue-600">({count} employee{count !== 1 ? 's' : ''})</span>
                </div>
                <div className="flex items-center gap-2">
                  <select
                    value={pendingDesignationMap[rawDesignation] ?? ''}
                    onChange={(e) => handleDesignationPendingChange(rawDesignation, e.target.value)}
                    className="flex-1 border border-blue-300 rounded px-2 py-1 text-xs bg-white focus:outline-none focus:ring-1 focus:ring-blue-400"
                  >
                    <option value="">— select —</option>
                    {designationOptions.map((d) => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                  <button
                    onClick={() => {
                      const canonical = pendingDesignationMap[rawDesignation];
                      if (canonical) applyDesignationMapping(rawDesignation, canonical);
                    }}
                    disabled={!pendingDesignationMap[rawDesignation]}
                    className="px-2.5 py-1 text-xs font-medium bg-slate-700 text-white rounded hover:bg-slate-600 disabled:opacity-30 disabled:cursor-not-allowed whitespace-nowrap"
                  >
                    Apply
                  </button>
                </div>
              </div>
            ))}
          </div>

          {pendingDesignationCount > 0 && (
            <button
              onClick={applyAllDesignationPending}
              className="w-full py-2 text-xs font-semibold bg-blue-700 text-white rounded-lg hover:bg-blue-600"
            >
              Apply All ({pendingDesignationCount} of {designationUnresolvedCombos.length} selected)
            </button>
          )}
        </Card>
      )}

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
                  <Th>Grade</Th>
                  <Th>Designation</Th>
                  <Th>Contract Start</Th>
                  <Th>Salary Structure</Th>
                </tr>
              </thead>
              <tbody>
                {previewRows.map((emp, i) => (
                  <tr
                    key={emp.employee_id}
                    className={`border-b border-slate-50 ${emp.mapping_unresolved || emp.designation_unresolved ? 'bg-amber-50' : ''}`}
                  >
                    <Td>{i + 1}</Td>
                    <Td>{emp.employee_id}</Td>
                    <Td>{emp.first_name} {emp.last_name}</Td>
                    <Td>{emp.grade}</Td>
                    <Td>
                      {emp.designation}
                      {emp.designation_unresolved && (
                        <span className="ml-1 text-blue-500" title={`"${emp.designation}" not found in workspace designations`}>⚠</span>
                      )}
                    </Td>
                    <Td>
                      <span className="font-mono">{emp.contract_start}</span>
                      {emp.contract_end && (
                        <span className="text-slate-400"> → {emp.contract_end}</span>
                      )}
                    </Td>
                    <Td>
                      <span
                        className={`font-mono ${emp.mapping_unresolved ? 'text-amber-600' : 'text-green-700'}`}
                      >
                        {emp.salary_definition_code}
                        {emp.mapping_unresolved && ' ⚠'}
                      </span>
                    </Td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {employees.length > 10 && (
            <p className="text-xs text-slate-400 mt-2">
              + {employees.length - 10} more rows not shown. All mappings apply to the full set.
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
