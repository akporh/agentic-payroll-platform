/**
 * Employees — Gate 4 rewrite + Sprint enhancements
 *
 * Design decisions:
 * - Edit opens a SlideOver (not inline row editing)
 * - AlertBanner for unmatched employees with scroll-to link
 * - border-l-4 border-amber-400 on unmatched rows (accessibility, not colour alone)
 * - Add Employee: SlideOver with form
 * - Bulk Upload: SlideOver wrapping EmployeeUpload with confirm/import step
 * - Both Start and End date visible in every table section
 */

import { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import { workspaceApi } from '../api/workspace';
import type { Employee } from '../types/payroll';
import {
  ContentHeader,
  Card,
  Btn,
  StatusBadge,
  AlertBanner,
  EmptyState,
  SlideOver,
  SearchableSelect,
  TextInput,
  DateInput,
  useToast,
  Breadcrumb,
} from '../design-system';
import { useWorkspaceContext } from '../context/WorkspaceContext';
import {
  EmployeeUpload,
  type MappedEmployee,
  type SalaryDefinitionOption,
} from '../components/onboarding/EmployeeUpload';

// ── Icons ─────────────────────────────────────────────────────────────────────

function PeopleIcon() {
  return (
    <svg className="w-full h-full" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  );
}

function UploadIcon() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
    </svg>
  );
}

function PlusIcon() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
    </svg>
  );
}

// ── Edit SlideOver ────────────────────────────────────────────────────────────

interface EditSlideOverProps {
  employee: Employee | null;
  gradeOptions: string[];
  designationOptions: string[];
  onClose: () => void;
  onSaved: () => void;
  workspaceId: string;
}

function EditSlideOver({ employee, gradeOptions, designationOptions, onClose, onSaved, workspaceId }: EditSlideOverProps) {
  const toast = useToast();
  const [grade, setGrade] = useState(employee?.grade ?? '');
  const [designation, setDesignation] = useState(employee?.designation ?? '');
  const [contractEnd, setContractEnd] = useState(employee?.contract_end ?? '');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (employee) {
      setGrade(employee.grade ?? '');
      setDesignation(employee.designation ?? '');
      setContractEnd(employee.contract_end ?? '');
      setError(null);
    }
  }, [employee]);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!employee) return;
    setSaving(true);
    setError(null);
    try {
      await workspaceApi.updateEmployeeContract(workspaceId, employee.employee_id, {
        grade_code: grade || null,
        designation_code: designation || null,
        contract_end: contractEnd || null,
        set_contract_end: true,
      });
      toast.show('success', 'Contract updated');
      onSaved();
      onClose();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Save failed');
    } finally {
      setSaving(false);
    }
  }

  return (
    <SlideOver
      open={!!employee}
      onClose={onClose}
      title="Edit Employee Contract"
      description={employee ? `${employee.full_name} · ${employee.employee_number}` : ''}
      footer={
        <div className="flex gap-3">
          <Btn type="submit" form="edit-employee-form" variant="primary" size="md" loading={saving}>
            Save Changes
          </Btn>
          <Btn type="button" variant="secondary" size="md" onClick={onClose}>
            Cancel
          </Btn>
        </div>
      }
    >
      <form id="edit-employee-form" onSubmit={handleSave} className="space-y-5">
        <SearchableSelect
          label="Grade"
          value={grade}
          onChange={setGrade}
          options={[
            { value: '', label: '— unassigned —' },
            ...gradeOptions.map((g) => ({ value: g, label: g })),
          ]}
        />
        <SearchableSelect
          label="Designation"
          value={designation}
          onChange={setDesignation}
          options={[
            { value: '', label: '— unassigned —' },
            ...designationOptions.map((d) => ({ value: d, label: d })),
          ]}
        />
        <DateInput
          label="Contract End Date"
          value={contractEnd}
          onChange={setContractEnd}
          hint="Leave blank for open-ended contracts. Set a date to schedule contract termination."
        />
        {error && <AlertBanner variant="error" description={error} />}
      </form>
    </SlideOver>
  );
}

// ── Add Employee SlideOver ────────────────────────────────────────────────────

interface AddEmployeeSlideOverProps {
  open: boolean;
  gradeOptions: string[];
  designationOptions: string[];
  salaryDefinitions: SalaryDefinitionOption[];
  onClose: () => void;
  onSaved: () => void;
  workspaceId: string;
}

function AddEmployeeSlideOver({
  open, gradeOptions, designationOptions, salaryDefinitions, onClose, onSaved, workspaceId
}: AddEmployeeSlideOverProps) {
  const toast = useToast();
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [employeeNumber, setEmployeeNumber] = useState('');
  const [salaryDefCode, setSalaryDefCode] = useState('');
  const [grade, setGrade] = useState('');
  const [designation, setDesignation] = useState('');
  const [contractStart, setContractStart] = useState('');
  const [contractEnd, setContractEnd] = useState('');
  const [tin, setTin] = useState('');
  const [rsa, setRsa] = useState('');
  const [bank, setBank] = useState('');
  const [accountNumber, setAccountNumber] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function reset() {
    setFirstName(''); setLastName(''); setEmployeeNumber('');
    setSalaryDefCode(''); setGrade(''); setDesignation('');
    setContractStart(''); setContractEnd('');
    setTin(''); setRsa(''); setBank(''); setAccountNumber('');
    setError(null);
  }

  function handleClose() { reset(); onClose(); }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!firstName.trim() || !lastName.trim() || !employeeNumber.trim() || !salaryDefCode) {
      setError('First name, last name, employee number, and salary definition are required.');
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const result = await workspaceApi.createEmployee(workspaceId, {
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        employee_number: employeeNumber.trim(),
        salary_definition_code: salaryDefCode,
        grade_code: grade || null,
        designation_code: designation || null,
        contract_start: contractStart || null,
        contract_end: contractEnd || null,
        tin: tin || null,
        rsa: rsa || null,
        bank: bank || null,
        account_number: accountNumber || null,
      });
      toast.show('success', `${result.full_name} added`);
      reset();
      onSaved();
      onClose();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to create employee');
    } finally {
      setSaving(false);
    }
  }

  return (
    <SlideOver
      open={open}
      onClose={handleClose}
      title="Add Employee"
      description="Create a new employee and contract record"
      footer={
        <div className="flex gap-3">
          <Btn type="submit" form="add-employee-form" variant="primary" size="md" loading={saving}>
            Add Employee
          </Btn>
          <Btn type="button" variant="secondary" size="md" onClick={handleClose}>
            Cancel
          </Btn>
        </div>
      }
    >
      <form id="add-employee-form" onSubmit={handleSave} className="space-y-5">

        {/* Identity */}
        <div className="space-y-1">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Identity</p>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <TextInput
            label="First Name"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            required
          />
          <TextInput
            label="Last Name"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            required
          />
        </div>
        <TextInput
          label="Employee Number / ID"
          value={employeeNumber}
          onChange={(e) => setEmployeeNumber(e.target.value)}
          hint="Must be unique within this workspace"
          required
        />

        {/* Contract */}
        <div className="pt-2 space-y-1 border-t border-gray-100">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider pt-2">Contract</p>
        </div>
        <SearchableSelect
          label="Salary Definition"
          value={salaryDefCode}
          onChange={setSalaryDefCode}
          options={[
            { value: '', label: '— select —' },
            ...salaryDefinitions.map((sd) => ({ value: sd.code, label: sd.name ? `${sd.code} — ${sd.name}` : sd.code })),
          ]}
          required
        />
        <SearchableSelect
          label="Grade"
          value={grade}
          onChange={setGrade}
          options={[
            { value: '', label: '— unassigned —' },
            ...gradeOptions.map((g) => ({ value: g, label: g })),
          ]}
        />
        <SearchableSelect
          label="Designation"
          value={designation}
          onChange={setDesignation}
          options={[
            { value: '', label: '— unassigned —' },
            ...designationOptions.map((d) => ({ value: d, label: d })),
          ]}
        />
        <div className="grid grid-cols-2 gap-4">
          <DateInput
            label="Contract Start"
            value={contractStart}
            onChange={setContractStart}
            hint="Defaults to today if blank"
          />
          <DateInput
            label="Contract End"
            value={contractEnd}
            onChange={setContractEnd}
            hint="Leave blank for open-ended"
          />
        </div>

        {/* Bank / payroll details */}
        <div className="pt-2 space-y-1 border-t border-gray-100">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider pt-2">Payroll Details <span className="font-normal normal-case">(optional)</span></p>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <TextInput label="TIN" value={tin} onChange={(e) => setTin(e.target.value)} />
          <TextInput label="RSA" value={rsa} onChange={(e) => setRsa(e.target.value)} />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <TextInput label="Bank" value={bank} onChange={(e) => setBank(e.target.value)} />
          <TextInput label="Account Number" value={accountNumber} onChange={(e) => setAccountNumber(e.target.value)} />
        </div>

        {error && <AlertBanner variant="error" description={error} />}
      </form>
    </SlideOver>
  );
}

// ── Upload Employees SlideOver ────────────────────────────────────────────────

interface ImportResult {
  name: string;
  employee_number: string;
  status: 'created' | 'failed';
  error?: string;
}

interface UploadSlideOverProps {
  open: boolean;
  onClose: () => void;
  onSaved: () => void;
  workspaceId: string;
  salaryDefinitions: SalaryDefinitionOption[];
  gradeOptions: string[];
  designationOptions: string[];
}

function UploadSlideOver({
  open, onClose, onSaved, workspaceId, salaryDefinitions, gradeOptions, designationOptions
}: UploadSlideOverProps) {
  const toast = useToast();
  const [employees, setEmployees] = useState<MappedEmployee[]>([]);
  const [importing, setImporting] = useState(false);
  const [results, setResults] = useState<ImportResult[] | null>(null);

  function handleClose() {
    if (importing) return;
    setEmployees([]);
    setResults(null);
    onClose();
  }

  const hasUnresolved = employees.some((e) => e.mapping_unresolved || e.designation_unresolved);
  const readyCount = employees.filter((e) => !e.mapping_unresolved && !e.designation_unresolved).length;

  async function handleImport() {
    if (readyCount === 0) return;
    setImporting(true);
    const batch = employees.filter((e) => !e.mapping_unresolved && !e.designation_unresolved);
    const importResults: ImportResult[] = [];

    for (const emp of batch) {
      const fullName = `${emp.first_name} ${emp.last_name}`;
      try {
        await workspaceApi.createEmployee(workspaceId, {
          first_name: emp.first_name,
          last_name: emp.last_name,
          employee_number: emp.employee_id,
          salary_definition_code: emp.salary_definition_code,
          grade_code: emp.grade || null,
          designation_code: emp.designation || null,
          contract_start: emp.contract_start || null,
          contract_end: emp.contract_end || null,
          tin: emp.tin || null,
          rsa: emp.rsa || null,
          bank: emp.bank || null,
          account_number: emp.account_number || null,
        });
        importResults.push({ name: fullName, employee_number: emp.employee_id, status: 'created' });
      } catch (e: unknown) {
        importResults.push({
          name: fullName,
          employee_number: emp.employee_id,
          status: 'failed',
          error: e instanceof Error ? e.message : 'Unknown error',
        });
      }
    }

    setResults(importResults);
    setImporting(false);

    const created = importResults.filter((r) => r.status === 'created').length;
    if (created > 0) {
      toast.show('success', `${created} employee${created !== 1 ? 's' : ''} imported`);
      onSaved();
    }
  }

  const createdCount = results?.filter((r) => r.status === 'created').length ?? 0;
  const failedCount = results?.filter((r) => r.status === 'failed').length ?? 0;

  return (
    <SlideOver
      open={open}
      onClose={handleClose}
      title="Upload Employees"
      description="Import multiple employees from an Excel or CSV file"
      footer={
        results ? (
          <Btn variant="secondary" size="md" onClick={handleClose}>
            Close
          </Btn>
        ) : (
          <div className="flex gap-3">
            <Btn
              variant="primary"
              size="md"
              loading={importing}
              disabled={readyCount === 0 || importing}
              onClick={handleImport}
            >
              {importing ? 'Importing…' : `Import ${readyCount} Employee${readyCount !== 1 ? 's' : ''}`}
            </Btn>
            {hasUnresolved && (
              <span className="text-xs text-amber-600 self-center">
                {employees.length - readyCount} row{employees.length - readyCount !== 1 ? 's' : ''} need mapping
              </span>
            )}
            <Btn variant="secondary" size="md" onClick={handleClose} disabled={importing}>
              Cancel
            </Btn>
          </div>
        )
      }
    >
      <div className="space-y-5">
        {results ? (
          /* ── Import results summary ── */
          <div className="space-y-4">
            {createdCount > 0 && (
              <AlertBanner
                variant="success"
                title={`${createdCount} employee${createdCount !== 1 ? 's' : ''} created successfully`}
              />
            )}
            {failedCount > 0 && (
              <AlertBanner
                variant="error"
                title={`${failedCount} employee${failedCount !== 1 ? 's' : ''} failed to import`}
                description="Review the errors below and correct the data before re-uploading."
              />
            )}
            {failedCount > 0 && (
              <div className="rounded-lg border border-red-100 overflow-hidden">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="bg-red-50 border-b border-red-100">
                      <th className="px-3 py-2 text-left font-semibold text-red-700">Employee</th>
                      <th className="px-3 py-2 text-left font-semibold text-red-700">Reason</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.filter((r) => r.status === 'failed').map((r) => (
                      <tr key={r.employee_number} className="border-b border-red-50 last:border-0">
                        <td className="px-3 py-2 text-gray-700">
                          {r.name}
                          <span className="ml-1 font-mono text-gray-400">({r.employee_number})</span>
                        </td>
                        <td className="px-3 py-2 text-red-600">{r.error}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        ) : (
          /* ── Upload + mapping UI ── */
          <EmployeeUpload
            employees={employees}
            salaryDefinitions={salaryDefinitions}
            designationOptions={designationOptions}
            onEmployeesLoaded={setEmployees}
            onMappingChange={setEmployees}
            onCreateSalaryDefinition={async (code) => {
              const sd = await workspaceApi.addSalaryDefinition(workspaceId, code);
              return { salary_definition_id: sd.salary_definition_id, code: sd.code, name: sd.name };
            }}
          />
        )}
      </div>
    </SlideOver>
  );
}

// ── Employee table ────────────────────────────────────────────────────────────

interface TableProps {
  rows: Employee[];
  variant?: 'active' | 'unmatched' | 'ended';
  onEdit: (emp: Employee) => void;
}

function EmployeeTable({ rows, variant = 'active', onEdit }: TableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="border-b border-gray-200 bg-gray-50">
            {['Name', 'Employee #', 'Designation', 'Grade', 'Start Date', 'End Date', 'Status', ''].map((h, i) => (
              <th
                key={i}
                className="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-gray-500 whitespace-nowrap"
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((emp) => (
            <tr
              key={emp.employee_id}
              className={`border-b border-gray-100 hover:bg-slate-50 transition-colors ${
                variant === 'unmatched' ? 'border-l-4 border-amber-400' : ''
              }`}
            >
              <td className="px-4 py-3 font-medium text-gray-800">{emp.full_name}</td>
              <td className="px-4 py-3 font-mono text-xs text-gray-500">{emp.employee_number}</td>
              <td className="px-4 py-3 text-gray-600">{emp.designation ?? <span className="text-amber-600 font-medium">Missing</span>}</td>
              <td className="px-4 py-3 text-gray-600">{emp.grade ?? <span className="text-amber-600 font-medium">Missing</span>}</td>
              <td className="px-4 py-3 text-gray-500 text-xs font-mono">{emp.contract_start ?? '—'}</td>
              <td className="px-4 py-3 text-xs">
                {emp.contract_end
                  ? <span className={`font-mono ${variant === 'ended' ? 'text-gray-500' : 'text-amber-700 font-medium'}`}>{emp.contract_end}</span>
                  : <span className="text-gray-300">—</span>
                }
              </td>
              <td className="px-4 py-3">
                <StatusBadge status={emp.status ?? 'ACTIVE'} size="sm" />
              </td>
              <td className="px-4 py-3">
                <Btn variant="ghost" size="sm" onClick={() => onEdit(emp)}>
                  Edit
                </Btn>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────

export function Employees() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const { workspace } = useWorkspaceContext();

  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [gradeOptions, setGradeOptions] = useState<string[]>([]);
  const [designationOptions, setDesignationOptions] = useState<string[]>([]);
  const [salaryDefinitions, setSalaryDefinitions] = useState<SalaryDefinitionOption[]>([]);
  const [editingEmployee, setEditingEmployee] = useState<Employee | null>(null);
  const [showAddEmployee, setShowAddEmployee] = useState(false);
  const [showUpload, setShowUpload] = useState(false);

  const unmatchedRef = useRef<HTMLDivElement>(null);

  function loadEmployees() {
    if (!workspaceId) return;
    workspaceApi
      .getEmployees(workspaceId)
      .then(setEmployees)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : 'Failed to reload'));
  }

  useEffect(() => {
    if (!workspaceId) return;
    Promise.all([
      workspaceApi.getEmployees(workspaceId),
      workspaceApi.getConfiguration(workspaceId),
    ])
      .then(([emps, config]) => {
        setEmployees(emps);
        setGradeOptions(config.grades.map((g) => g.code));
        setDesignationOptions(config.designations.map((d) => d.code));
        setSalaryDefinitions(
          config.salary_definitions.map((sd) => ({
            salary_definition_id: sd.salary_definition_id,
            code: sd.code,
            name: sd.name,
          }))
        );
      })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : 'Failed to load'))
      .finally(() => setLoading(false));
  }, [workspaceId]);

  const ended     = employees.filter((e) => e.is_ended);
  const active    = employees.filter((e) => !e.is_ended);
  const unmatched = active.filter((e) => !e.grade || !e.designation);
  const matched   = active.filter((e) => e.grade && e.designation);

  return (
    <div className="max-w-5xl">
      <ContentHeader
        title="Employees"
        subtitle={loading ? 'Loading…' : `${active.length} active · ${ended.length} ended`}
        back={
          <Breadcrumb items={[
            { label: 'Bureau Dashboard', to: '/' },
            { label: workspace?.name ?? '…', to: `/workspaces/${workspaceId}` },
            { label: 'Employees' },
          ]} />
        }
        action={
          <div className="flex gap-2">
            <Btn
              variant="secondary"
              size="sm"
              icon={<UploadIcon />}
              onClick={() => setShowUpload(true)}
            >
              Upload from Excel
            </Btn>
            <Btn
              variant="primary"
              size="sm"
              icon={<PlusIcon />}
              onClick={() => setShowAddEmployee(true)}
            >
              Add Employee
            </Btn>
          </div>
        }
      />

      {error && <AlertBanner variant="error" description={error} className="mb-4" />}

      {/* Unmatched banner */}
      {!loading && unmatched.length > 0 && (
        <AlertBanner
          variant="warning"
          title={`${unmatched.length} employee${unmatched.length !== 1 ? 's' : ''} missing grade or designation`}
          description="These employees cannot be included in a payroll run until their contract is complete."
          action={{
            label: 'View unmatched →',
            onClick: () => unmatchedRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }),
          }}
          className="mb-4"
        />
      )}

      {loading ? (
        <Card padding="sm">
          <table className="w-full">
            <tbody>
              {Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="animate-pulse border-b border-gray-100">
                  {[30, 15, 15, 10, 10, 10, 8, 5].map((w, j) => (
                    <td key={j} className="px-4 py-3">
                      <div className="h-4 bg-gray-200 rounded" style={{ width: `${w}%` }} />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      ) : employees.length === 0 ? (
        <Card>
          <EmptyState
            icon={<PeopleIcon />}
            headline="No employees yet"
            body="Add employees one at a time or upload a spreadsheet using the buttons above."
          />
        </Card>
      ) : (
        <div className="space-y-5">
          {/* Unmatched section */}
          {unmatched.length > 0 && (
            <div ref={unmatchedRef}>
              <Card padding="sm">
                <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                  <p className="text-xs font-semibold text-amber-700 uppercase tracking-wide">
                    Unmatched — {unmatched.length} employee{unmatched.length !== 1 ? 's' : ''}
                  </p>
                  <p className="text-xs text-gray-400">Grade or designation is missing</p>
                </div>
                <EmployeeTable rows={unmatched} variant="unmatched" onEdit={setEditingEmployee} />
              </Card>
            </div>
          )}

          {/* Matched section */}
          {matched.length > 0 && (
            <Card padding="sm">
              <div className="px-4 py-3 border-b border-gray-100">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  Active — {matched.length} employee{matched.length !== 1 ? 's' : ''}
                </p>
              </div>
              <EmployeeTable rows={matched} variant="active" onEdit={setEditingEmployee} />
            </Card>
          )}

          {/* Contract Ended section */}
          {ended.length > 0 && (
            <Card padding="sm">
              <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
                  Contract Ended — {ended.length} employee{ended.length !== 1 ? 's' : ''}
                </p>
                <p className="text-xs text-gray-400">Contract end date has passed</p>
              </div>
              <EmployeeTable rows={ended} variant="ended" onEdit={setEditingEmployee} />
            </Card>
          )}
        </div>
      )}

      <EditSlideOver
        employee={editingEmployee}
        gradeOptions={gradeOptions}
        designationOptions={designationOptions}
        workspaceId={workspaceId ?? ''}
        onClose={() => setEditingEmployee(null)}
        onSaved={loadEmployees}
      />

      <AddEmployeeSlideOver
        open={showAddEmployee}
        gradeOptions={gradeOptions}
        designationOptions={designationOptions}
        salaryDefinitions={salaryDefinitions}
        workspaceId={workspaceId ?? ''}
        onClose={() => setShowAddEmployee(false)}
        onSaved={loadEmployees}
      />

      <UploadSlideOver
        open={showUpload}
        workspaceId={workspaceId ?? ''}
        salaryDefinitions={salaryDefinitions}
        gradeOptions={gradeOptions}
        designationOptions={designationOptions}
        onClose={() => setShowUpload(false)}
        onSaved={loadEmployees}
      />
    </div>
  );
}
