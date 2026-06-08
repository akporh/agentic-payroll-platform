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
import { employeesApi } from '../api/employees';
import { ApiError } from '../api/client';
import type { ContractRecord } from '../api/employees';
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
} from '../components/employees/EmployeeUpload';

// ── Option builders ───────────────────────────────────────────────────────────

function salaryDefOptions(defs: SalaryDefinitionOption[], emptyLabel = '— select —') {
  return [
    { value: '', label: emptyLabel },
    ...defs.map((sd) => ({ value: sd.code, label: sd.name ? `${sd.code} — ${sd.name}` : sd.code })),
  ];
}

function codeOptions(codes: string[], emptyLabel = '— unassigned —') {
  return [
    { value: '', label: emptyLabel },
    ...codes.map((c) => ({ value: c, label: c })),
  ];
}

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

// ── Enroll Employee SlideOver ─────────────────────────────────────────────────

interface EnrollSlideOverProps {
  employee: Employee | null;
  salaryDefinitions: SalaryDefinitionOption[];
  gradeOptions: string[];
  designationOptions: string[];
  onClose: () => void;
  onSaved: () => void;
  workspaceId: string;
}

function EnrollSlideOver({
  employee, salaryDefinitions, gradeOptions, designationOptions, onClose, onSaved, workspaceId,
}: EnrollSlideOverProps) {
  const toast = useToast();
  const [salaryDefCode, setSalaryDefCode] = useState('');
  const [grade, setGrade] = useState('');
  const [designation, setDesignation] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (employee) {
      setSalaryDefCode('');
      setGrade(employee.grade ?? '');
      setDesignation(employee.designation ?? '');
      setError(null);
    }
  }, [employee]);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!salaryDefCode) { setError('Salary definition is required.'); return; }
    setSaving(true);
    setError(null);
    try {
      await workspaceApi.enrollEmployee(workspaceId, employee!.employee_id, {
        salary_definition_code: salaryDefCode,
        grade_code: grade || null,
        designation_code: designation || null,
      });
      toast.show('success', `${employee!.full_name} enrolled — payroll eligible`);
      onSaved();
      onClose();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to enroll employee');
    } finally {
      setSaving(false);
    }
  }

  return (
    <SlideOver
      open={!!employee}
      onClose={onClose}
      title="Enroll Employee"
      description={employee ? `${employee.full_name} · ${employee.employee_number}` : ''}
      footer={
        <div className="flex gap-3">
          <Btn type="submit" form="enroll-employee-form" variant="primary" size="md" loading={saving}>
            Enroll Employee
          </Btn>
          <Btn type="button" variant="secondary" size="md" onClick={onClose}>
            Cancel
          </Btn>
        </div>
      }
    >
      <form id="enroll-employee-form" onSubmit={handleSave} className="space-y-5">
        <SearchableSelect
          label="Salary Definition"
          value={salaryDefCode}
          onChange={setSalaryDefCode}
          options={salaryDefOptions(salaryDefinitions)}
          required
        />
        <SearchableSelect
          label="Grade"
          value={grade}
          onChange={setGrade}
          options={codeOptions(gradeOptions)}
        />
        <SearchableSelect
          label="Designation"
          value={designation}
          onChange={setDesignation}
          options={codeOptions(designationOptions)}
        />
        {error && <AlertBanner variant="error" description={error} />}
      </form>
    </SlideOver>
  );
}

// ── Bulk Enroll SlideOver ─────────────────────────────────────────────────────

interface BulkEnrollSlideOverProps {
  open: boolean;
  employeeIds: string[];
  salaryDefinitions: SalaryDefinitionOption[];
  gradeOptions: string[];
  designationOptions: string[];
  onClose: () => void;
  onSaved: () => void;
  workspaceId: string;
}

function BulkEnrollSlideOver({
  open, employeeIds, salaryDefinitions, gradeOptions, designationOptions, onClose, onSaved, workspaceId,
}: BulkEnrollSlideOverProps) {
  const toast = useToast();
  const [salaryDefCode, setSalaryDefCode] = useState('');
  const [grade, setGrade] = useState('');
  const [designation, setDesignation] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      setSalaryDefCode('');
      setGrade('');
      setDesignation('');
      setError(null);
    }
  }, [open]);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!salaryDefCode) { setError('Salary definition is required.'); return; }
    setSaving(true);
    setError(null);
    try {
      const result = await workspaceApi.bulkEnrollEmployees(workspaceId, {
        employee_ids: employeeIds,
        salary_definition_code: salaryDefCode,
        grade_code: grade || null,
        designation_code: designation || null,
      });
      const msg = result.skipped > 0
        ? `${result.enrolled} enrolled — ${result.skipped} already enrolled (skipped)`
        : `${result.enrolled} employee${result.enrolled !== 1 ? 's' : ''} enrolled — payroll eligible`;
      toast.show('success', msg);
      onSaved();
      onClose();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to bulk enroll');
    } finally {
      setSaving(false);
    }
  }

  return (
    <SlideOver
      open={open}
      onClose={onClose}
      title="Enroll Employees"
      description={`Enrolling ${employeeIds.length} employee${employeeIds.length !== 1 ? 's' : ''}`}
      footer={
        <div className="flex gap-3">
          <Btn type="submit" form="bulk-enroll-form" variant="primary" size="md" loading={saving}>
            Enroll {employeeIds.length} Employee{employeeIds.length !== 1 ? 's' : ''}
          </Btn>
          <Btn type="button" variant="secondary" size="md" onClick={onClose}>
            Cancel
          </Btn>
        </div>
      }
    >
      <form id="bulk-enroll-form" onSubmit={handleSave} className="space-y-5">
        <SearchableSelect
          label="Salary Definition"
          value={salaryDefCode}
          onChange={setSalaryDefCode}
          options={salaryDefOptions(salaryDefinitions)}
          required
        />
        <SearchableSelect
          label="Grade (optional)"
          value={grade}
          onChange={setGrade}
          options={codeOptions(gradeOptions)}
        />
        {grade && (
          <AlertBanner
            variant="warning"
            description="This will overwrite any existing grade assignment on selected employees."
          />
        )}
        <SearchableSelect
          label="Designation (optional)"
          value={designation}
          onChange={setDesignation}
          options={codeOptions(designationOptions)}
        />
        {error && <AlertBanner variant="error" description={error} />}
      </form>
    </SlideOver>
  );
}

// ── Edit Employee SlideOver (name + status only) ──────────────────────────────

interface EditSlideOverProps {
  employee: Employee | null;
  onClose: () => void;
  onSaved: () => void;
  workspaceId: string;
}

function EditSlideOver({ employee, onClose, onSaved, workspaceId }: EditSlideOverProps) {
  const toast = useToast();
  const [fullName, setFullName] = useState('');
  const [status, setStatus] = useState('ACTIVE');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (employee) {
      setFullName(employee.full_name ?? '');
      setStatus(employee.status ?? 'ACTIVE');
      setError(null);
    }
  }, [employee]);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!employee) return;
    if (!fullName.trim()) { setError('Full name is required.'); return; }
    setSaving(true);
    setError(null);
    try {
      await employeesApi.updateEmployee(workspaceId, employee.employee_id, {
        full_name: fullName.trim(),
        status,
      });
      toast.show('success', 'Employee updated');
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
      title="Edit Employee"
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
        <TextInput
          label="Full Name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          required
        />
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <option value="ACTIVE">ACTIVE</option>
            <option value="INACTIVE">INACTIVE</option>
          </select>
        </div>
        {error && <AlertBanner variant="error" description={error} />}
      </form>
    </SlideOver>
  );
}

// ── Change Contract SlideOver ─────────────────────────────────────────────────

interface ChangeContractSlideOverProps {
  employee: Employee | null;
  salaryDefinitions: SalaryDefinitionOption[];
  gradeOptions: string[];
  designationOptions: string[];
  onClose: () => void;
  onSaved: () => void;
  workspaceId: string;
}

function ChangeContractSlideOver({
  employee, salaryDefinitions, gradeOptions, designationOptions, onClose, onSaved, workspaceId,
}: ChangeContractSlideOverProps) {
  const toast = useToast();
  const [salaryDefId, setSalaryDefId] = useState('');
  const [startDate, setStartDate] = useState('');
  const [grade, setGrade] = useState('');
  const [designation, setDesignation] = useState('');
  const [changeReason, setChangeReason] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (employee) {
      setSalaryDefId('');
      setStartDate('');
      setGrade(employee.grade ?? '');
      setDesignation(employee.designation ?? '');
      setChangeReason('');
      setError(null);
    }
  }, [employee]);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!salaryDefId || !startDate || !changeReason.trim()) {
      setError('Salary definition, start date, and reason for change are required.');
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await employeesApi.addContract(workspaceId, employee!.employee_id, {
        salary_definition_id: salaryDefId,
        start_date: startDate,
        grade_code: grade || null,
        designation_code: designation || null,
        change_reason: changeReason.trim(),
      });
      toast.show('success', 'New contract created — previous contract closed');
      onSaved();
      onClose();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Failed to create contract';
      if (msg.includes('payroll run is in progress') || msg.includes('pending approval')) {
        setError('A payroll run is in progress. Contract changes are locked until the run completes.');
      } else if (msg.includes('must be after the current contract start_date')) {
        setError('New start date must be after the current contract start date.');
      } else {
        setError(msg);
      }
    } finally {
      setSaving(false);
    }
  }

  return (
    <SlideOver
      open={!!employee}
      onClose={onClose}
      title="Change Grade / Salary"
      description={employee ? `${employee.full_name} · ${employee.employee_number}` : ''}
      footer={
        <div className="flex gap-3">
          <Btn type="submit" form="change-contract-form" variant="primary" size="md" loading={saving}>
            Apply Contract Change
          </Btn>
          <Btn type="button" variant="secondary" size="md" onClick={onClose}>
            Cancel
          </Btn>
        </div>
      }
    >
      <form id="change-contract-form" onSubmit={handleSave} className="space-y-5">
        <AlertBanner
          variant="warning"
          description="This will close the current contract and open a new one from the selected start date."
        />
        <SearchableSelect
          label="New Salary Definition"
          value={salaryDefId}
          onChange={setSalaryDefId}
          options={[
            { value: '', label: '— select —' },
            ...salaryDefinitions.map((sd) => ({
              value: sd.salary_definition_id,
              label: sd.name ? `${sd.code} — ${sd.name}` : sd.code,
            })),
          ]}
          required
        />
        <DateInput
          label="New Contract Start Date"
          value={startDate}
          onChange={setStartDate}
          hint="Must be after the current contract's start date"
          required
        />
        <SearchableSelect
          label="Grade"
          value={grade}
          onChange={setGrade}
          options={codeOptions(gradeOptions)}
        />
        <SearchableSelect
          label="Designation"
          value={designation}
          onChange={setDesignation}
          options={codeOptions(designationOptions)}
        />
        <TextInput
          label="Reason for Change"
          value={changeReason}
          onChange={(e) => setChangeReason(e.target.value)}
          hint="Required — e.g. promotion, regrading, salary review"
          required
        />
        {error && <AlertBanner variant="error" description={error} />}
      </form>
    </SlideOver>
  );
}

// ── View Contracts SlideOver (read-only, Sprint 17: current contract only) ─────

interface ViewContractsSlideOverProps {
  employee: Employee | null;
  onClose: () => void;
  workspaceId: string;
}

function ViewContractsSlideOver({ employee, onClose, workspaceId }: ViewContractsSlideOverProps) {
  const [contract, setContract] = useState<ContractRecord | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!employee || !workspaceId) return;
    setLoading(true);
    setContract(null);
    setError(null);
    employeesApi
      .getEmployee(workspaceId, employee.employee_id)
      .then((detail) => setContract(detail.contracts[0] ?? null))
      .catch((e: unknown) => setError(e instanceof Error ? e.message : 'Failed to load'))
      .finally(() => setLoading(false));
  }, [employee, workspaceId]);

  return (
    <SlideOver
      open={!!employee}
      onClose={onClose}
      title="Current Contract"
      description={employee ? `${employee.full_name} · ${employee.employee_number}` : ''}
      footer={
        <Btn variant="secondary" size="md" onClick={onClose}>
          Close
        </Btn>
      }
    >
      {loading ? (
        <p className="text-sm text-gray-400">Loading…</p>
      ) : error ? (
        <AlertBanner variant="error" description={error} />
      ) : !contract ? (
        <p className="text-sm text-gray-400">No contract on record.</p>
      ) : (
        <div className="space-y-4">
          <div className="rounded-lg border border-gray-200 overflow-hidden">
            <div className="px-4 py-2 bg-gray-50 border-b border-gray-200 flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Contract</span>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-700">Current</span>
            </div>
            <dl className="divide-y divide-gray-100">
              {[
                ['Salary Definition', contract.salary_definition_code ?? '—'],
                ['Grade', contract.grade_code ?? '—'],
                ['Designation', contract.designation_code ?? '—'],
                ['Start Date', contract.start_date ?? '—'],
                ['End Date', contract.end_date ?? 'Open-ended'],
                ['Change Reason', contract.change_reason ?? '—'],
              ].map(([label, value]) => (
                <div key={label} className="px-4 py-3 grid grid-cols-2 gap-2">
                  <dt className="text-xs font-medium text-gray-500">{label}</dt>
                  <dd className="text-sm text-gray-800 font-mono text-right">{value}</dd>
                </div>
              ))}
            </dl>
          </div>
          <p className="text-xs text-gray-400">Full contract history is available in Sprint 20.</p>
        </div>
      )}
    </SlideOver>
  );
}

// ── Add Employee SlideOver ────────────────────────────────────────────────────

interface PayCycleSummary {
  frequency: string;
  run_day: number;
}

interface AddEmployeeSlideOverProps {
  open: boolean;
  gradeOptions: string[];
  designationOptions: string[];
  salaryDefinitions: SalaryDefinitionOption[];
  payCycle: PayCycleSummary | null;
  onClose: () => void;
  onSaved: () => void;
  workspaceId: string;
}

function currentMonthPeriod(): { start: Date; end: Date; label: string } {
  const today = new Date();
  const start = new Date(today.getFullYear(), today.getMonth(), 1);
  const end   = new Date(today.getFullYear(), today.getMonth() + 1, 0);
  const label = today.toLocaleString('default', { month: 'long', year: 'numeric' });
  return { start, end, label };
}

function AddEmployeeSlideOver({
  open, gradeOptions, designationOptions, salaryDefinitions, payCycle, onClose, onSaved, workspaceId
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

  const midPeriodWarning = (() => {
    if (!payCycle || !contractStart) return null;
    try {
      const d = new Date(contractStart);
      if (isNaN(d.getTime())) return null;
      const { start, end, label } = currentMonthPeriod();
      if (d >= start && d <= end) {
        return `This start date falls within the current pay period (${label}). This employee will appear in payroll from the next period onwards.`;
      }
    } catch { /* ignore */ }
    return null;
  })();

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
    if (!firstName.trim() || !lastName.trim() || !employeeNumber.trim()) {
      setError('First name, last name, and employee number are required.');
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const result = await workspaceApi.createEmployee(workspaceId, {
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        employee_number: employeeNumber.trim(),
        salary_definition_code: salaryDefCode || null,
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
          options={salaryDefOptions(salaryDefinitions, '— none (register without enrolling) —')}
        />
        <SearchableSelect
          label="Grade"
          value={grade}
          onChange={setGrade}
          options={codeOptions(gradeOptions)}
        />
        <SearchableSelect
          label="Designation"
          value={designation}
          onChange={setDesignation}
          options={codeOptions(designationOptions)}
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
        {midPeriodWarning && (
          <AlertBanner variant="warning" description={midPeriodWarning} />
        )}

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
  status: 'created' | 'not-enrolled' | 'skipped' | 'failed';
  error?: string;
}

interface UploadSlideOverProps {
  open: boolean;
  onClose: () => void;
  onSaved: () => void;
  workspaceId: string;
  salaryDefinitions: SalaryDefinitionOption[];
  designationOptions: string[];
}

function UploadSlideOver({
  open, onClose, onSaved, workspaceId, salaryDefinitions, designationOptions
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

  const unresolvedCount = employees.filter((e) => e.mapping_unresolved).length;
  const enrolledCount   = employees.filter((e) => !e.mapping_unresolved).length;

  async function handleImport() {
    if (employees.length === 0) return;
    setImporting(true);

    const settled = await Promise.allSettled(
      employees.map((emp) => {
        const salaryCode = emp.mapping_unresolved ? null : emp.salary_definition_code;
        return workspaceApi.createEmployee(workspaceId, {
          first_name: emp.first_name,
          last_name: emp.last_name,
          employee_number: emp.employee_id,
          salary_definition_code: salaryCode,
          grade_code: null,
          designation_code: emp.designation_unresolved ? null : emp.designation || null,
          contract_start: emp.contract_start || null,
          contract_end: emp.contract_end || null,
          tin: emp.tin || null,
          rsa: emp.rsa || null,
          bank: emp.bank || null,
          account_number: emp.account_number || null,
        }).then((): ImportResult => ({
          name: `${emp.first_name} ${emp.last_name}`,
          employee_number: emp.employee_id,
          status: salaryCode ? 'created' : 'not-enrolled',
        })).catch((e: unknown): ImportResult => {
          if (e instanceof ApiError && e.response.status === 409) {
            return { name: `${emp.first_name} ${emp.last_name}`, employee_number: emp.employee_id, status: 'skipped' };
          }
          return {
            name: `${emp.first_name} ${emp.last_name}`,
            employee_number: emp.employee_id,
            status: 'failed',
            error: e instanceof Error ? e.message : 'Unknown error',
          };
        });
      })
    );
    const importResults: ImportResult[] = settled.map((s) =>
      s.status === 'fulfilled' ? s.value : { name: '', employee_number: '', status: 'failed' as const, error: 'Unexpected rejection' }
    );

    setResults(importResults);
    setImporting(false);

    const newCount = importResults.filter((r) => r.status === 'created' || r.status === 'not-enrolled').length;
    if (newCount > 0) {
      toast.show('success', `${newCount} employee${newCount !== 1 ? 's' : ''} created`);
      onSaved();
    }
  }

  const createdCount    = results?.filter((r) => r.status === 'created').length ?? 0;
  const notEnrolledResultCount = results?.filter((r) => r.status === 'not-enrolled').length ?? 0;
  const skippedCount    = results?.filter((r) => r.status === 'skipped').length ?? 0;
  const failedCount     = results?.filter((r) => r.status === 'failed').length ?? 0;

  const importLabel = (() => {
    if (importing) return 'Importing…';
    const total = employees.length;
    if (total === 0) return 'Import';
    if (unresolvedCount > 0) {
      return `Import ${total} employee${total !== 1 ? 's' : ''} (${enrolledCount} enrolled · ${unresolvedCount} not enrolled)`;
    }
    return `Import ${total} employee${total !== 1 ? 's' : ''}`;
  })();

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
          <div className="flex items-center gap-3 flex-wrap">
            <Btn
              variant="primary"
              size="md"
              loading={importing}
              disabled={employees.length === 0 || importing}
              onClick={handleImport}
            >
              {importLabel}
            </Btn>
            {unresolvedCount > 0 && !importing && (
              <span className="text-xs text-gray-500 self-center">
                {unresolvedCount} will import as not enrolled
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
          <div className="space-y-4">
            {/* Summary line */}
            <p className="text-sm text-gray-600">
              {[
                createdCount > 0 && `${createdCount} enrolled`,
                notEnrolledResultCount > 0 && `${notEnrolledResultCount} not enrolled`,
                skippedCount > 0 && `${skippedCount} already registered`,
                failedCount > 0 && `${failedCount} failed`,
              ].filter(Boolean).join(' · ')}
            </p>
            {createdCount > 0 && (
              <AlertBanner
                variant="success"
                title={`${createdCount} employee${createdCount !== 1 ? 's' : ''} enrolled`}
              />
            )}
            {notEnrolledResultCount > 0 && (
              <AlertBanner
                variant="warning"
                title={`${notEnrolledResultCount} employee${notEnrolledResultCount !== 1 ? 's' : ''} registered without salary — not enrolled`}
                description="Assign a salary definition from the Not Enrolled section to make them payroll-eligible."
              />
            )}
            {skippedCount > 0 && (
              <AlertBanner
                variant="info"
                title={`${skippedCount} already registered — skipped`}
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
  variant?: 'active' | 'unmatched' | 'ended' | 'not-enrolled';
  onEdit: (emp: Employee) => void;
  onChangeContract?: (emp: Employee) => void;
  onViewContracts?: (emp: Employee) => void;
  onEnroll?: (emp: Employee) => void;
  canEnroll?: boolean;
  selectedIds?: Set<string>;
  onSelectionChange?: (id: string, checked: boolean) => void;
}

function EmployeeTable({ rows, variant = 'active', onEdit, onChangeContract, onViewContracts, onEnroll, canEnroll = true, selectedIds, onSelectionChange }: TableProps) {
  const isNotEnrolled = variant === 'not-enrolled';
  const showCheckboxes = isNotEnrolled && !!onSelectionChange;

  const allSelected = showCheckboxes && rows.length > 0 && rows.every((r) => selectedIds?.has(r.employee_id));
  const someSelected = showCheckboxes && rows.some((r) => selectedIds?.has(r.employee_id));

  function handleHeaderCheck(e: React.ChangeEvent<HTMLInputElement>) {
    rows.forEach((r) => onSelectionChange?.(r.employee_id, e.target.checked));
  }

  const baseHeaders = isNotEnrolled
    ? ['Name', 'Employee #', 'Start Date', 'Status', '']
    : ['Name', 'Employee #', 'Designation', 'Grade', 'Start Date', 'End Date', 'Status', ''];
  const headers = showCheckboxes ? ['', ...baseHeaders] : baseHeaders;

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="border-b border-gray-200 bg-gray-50">
            {showCheckboxes && (
              <th className="px-4 py-3 w-8">
                <input
                  type="checkbox"
                  aria-label="Select all"
                  checked={allSelected}
                  ref={(el) => { if (el) el.indeterminate = someSelected && !allSelected; }}
                  onChange={handleHeaderCheck}
                  className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
              </th>
            )}
            {baseHeaders.map((h, i) => (
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
              } ${isNotEnrolled ? 'border-l-4 border-rose-400' : ''}`}
            >
              {showCheckboxes && (
                <td className="px-4 py-3 w-8">
                  <input
                    type="checkbox"
                    aria-label={emp.full_name}
                    checked={selectedIds?.has(emp.employee_id) ?? false}
                    onChange={(e) => onSelectionChange?.(emp.employee_id, e.target.checked)}
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                </td>
              )}
              <td className="px-4 py-3 font-medium text-gray-800">{emp.full_name}</td>
              <td className="px-4 py-3 font-mono text-xs text-gray-500">{emp.employee_number}</td>
              {!isNotEnrolled && (
                <>
                  <td className="px-4 py-3 text-gray-600">{emp.designation ?? <span className="text-amber-600 font-medium">Missing</span>}</td>
                  <td className="px-4 py-3 text-gray-600">{emp.grade ?? <span className="text-amber-600 font-medium">Missing</span>}</td>
                </>
              )}
              <td className="px-4 py-3 text-gray-500 text-xs font-mono">{emp.contract_start ?? '—'}</td>
              {!isNotEnrolled && (
                <td className="px-4 py-3 text-xs">
                  {emp.contract_end
                    ? <span className={`font-mono ${variant === 'ended' ? 'text-gray-500' : 'text-amber-700 font-medium'}`}>{emp.contract_end}</span>
                    : <span className="text-gray-300">—</span>
                  }
                </td>
              )}
              <td className="px-4 py-3">
                <StatusBadge status={emp.status ?? 'ACTIVE'} size="sm" />
              </td>
              <td className="px-4 py-3">
                <div className="flex gap-1">
                  {isNotEnrolled ? (
                    <>
                      <Btn
                        variant="primary"
                        size="sm"
                        onClick={() => onEnroll?.(emp)}
                        disabled={!canEnroll}
                        title={canEnroll ? undefined : 'Configure salary definitions first'}
                      >
                        Enroll
                      </Btn>
                      <Btn variant="ghost" size="sm" onClick={() => onEdit(emp)}>
                        Edit
                      </Btn>
                    </>
                  ) : (
                    <>
                      <Btn variant="ghost" size="sm" onClick={() => onEdit(emp)}>
                        Edit
                      </Btn>
                      {variant !== 'ended' && onChangeContract && (
                        <Btn variant="ghost" size="sm" onClick={() => onChangeContract(emp)}>
                          Change Grade / Salary
                        </Btn>
                      )}
                      {onViewContracts && (
                        <Btn variant="ghost" size="sm" onClick={() => onViewContracts(emp)}>
                          View Contracts
                        </Btn>
                      )}
                    </>
                  )}
                </div>
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
  const [payCycle, setPayCycle] = useState<PayCycleSummary | null>(null);
  const [editingEmployee, setEditingEmployee] = useState<Employee | null>(null);
  const [changingContractEmployee, setChangingContractEmployee] = useState<Employee | null>(null);
  const [viewingContractsEmployee, setViewingContractsEmployee] = useState<Employee | null>(null);
  const [enrollingEmployee, setEnrollingEmployee] = useState<Employee | null>(null);
  const [showAddEmployee, setShowAddEmployee] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [selectedNotEnrolledIds, setSelectedNotEnrolledIds] = useState<Set<string>>(new Set());
  const [showBulkEnroll, setShowBulkEnroll] = useState(false);

  const unmatchedRef = useRef<HTMLDivElement>(null);
  const notEnrolledRef = useRef<HTMLDivElement>(null);

  function loadEmployees() {
    if (!workspaceId) return;
    setSelectedNotEnrolledIds(new Set());
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
        setPayCycle(config.pay_cycle ? { frequency: config.pay_cycle.frequency, run_day: config.pay_cycle.run_day } : null);
      })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : 'Failed to load'))
      .finally(() => setLoading(false));
  }, [workspaceId]);

  function handleNotEnrolledSelectionChange(id: string, checked: boolean) {
    setSelectedNotEnrolledIds((prev) => {
      const next = new Set(prev);
      if (checked) next.add(id); else next.delete(id);
      return next;
    });
  }

  const ended        = employees.filter((e) => e.is_ended);
  const active       = employees.filter((e) => !e.is_ended);
  const notEnrolled  = active.filter((e) => e.is_enrolled === false);
  const enrolled     = active.filter((e) => e.is_enrolled !== false);
  const unmatched    = enrolled.filter((e) => !e.grade || !e.designation);
  const matched      = enrolled.filter((e) => e.grade && e.designation);
  const canEnroll    = salaryDefinitions.length > 0;

  return (
    <div className="max-w-5xl">
      <ContentHeader
        title="Employees"
        subtitle={loading ? 'Loading…' : `${active.length} active · ${ended.length} ended${notEnrolled.length > 0 ? ` · ${notEnrolled.length} not enrolled` : ''}`}
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

      {/* Not Enrolled banner */}
      {!loading && notEnrolled.length > 0 && (
        <AlertBanner
          variant="warning"
          title={`${notEnrolled.length} employee${notEnrolled.length !== 1 ? 's' : ''} not enrolled in payroll`}
          description={
            canEnroll
              ? 'These employees will not appear in payroll runs until a salary definition is assigned.'
              : 'Salary definitions must be set up before employees can be enrolled.'
          }
          action={{
            label: 'View not enrolled →',
            onClick: () => notEnrolledRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }),
          }}
          className="mb-4"
        />
      )}

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
          {/* Not Enrolled section */}
          {notEnrolled.length > 0 && (
            <div ref={notEnrolledRef}>
              <Card padding="sm">
                <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                  <p className="text-xs font-semibold text-rose-700 uppercase tracking-wide">
                    Not Enrolled — {notEnrolled.length} employee{notEnrolled.length !== 1 ? 's' : ''}
                  </p>
                  <p className="text-xs text-gray-400">No salary definition assigned</p>
                </div>
                {selectedNotEnrolledIds.size > 0 && (
                  <div className="px-4 py-2 bg-indigo-50 border-b border-indigo-100 flex items-center gap-3 flex-wrap">
                    <span className="text-xs text-indigo-700 font-medium">
                      {selectedNotEnrolledIds.size} selected
                    </span>
                    <Btn
                      variant="primary"
                      size="sm"
                      disabled={!canEnroll}
                      title={canEnroll ? undefined : 'Configure salary definitions first'}
                      onClick={() => setShowBulkEnroll(true)}
                    >
                      Enroll Selected
                    </Btn>
                    <Btn
                      variant="ghost"
                      size="sm"
                      onClick={() => setSelectedNotEnrolledIds(new Set())}
                    >
                      Clear selection
                    </Btn>
                  </div>
                )}
                <EmployeeTable
                  rows={notEnrolled}
                  variant="not-enrolled"
                  onEdit={setEditingEmployee}
                  onEnroll={setEnrollingEmployee}
                  canEnroll={canEnroll}
                  selectedIds={selectedNotEnrolledIds}
                  onSelectionChange={handleNotEnrolledSelectionChange}
                />
              </Card>
            </div>
          )}

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
                <EmployeeTable rows={unmatched} variant="unmatched" onEdit={setEditingEmployee} onChangeContract={setChangingContractEmployee} onViewContracts={setViewingContractsEmployee} />
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
              <EmployeeTable rows={matched} variant="active" onEdit={setEditingEmployee} onChangeContract={setChangingContractEmployee} onViewContracts={setViewingContractsEmployee} />
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
              <EmployeeTable rows={ended} variant="ended" onEdit={setEditingEmployee} onViewContracts={setViewingContractsEmployee} />
            </Card>
          )}
        </div>
      )}

      <EnrollSlideOver
        employee={enrollingEmployee}
        salaryDefinitions={salaryDefinitions}
        gradeOptions={gradeOptions}
        designationOptions={designationOptions}
        workspaceId={workspaceId ?? ''}
        onClose={() => setEnrollingEmployee(null)}
        onSaved={loadEmployees}
      />

      <BulkEnrollSlideOver
        open={showBulkEnroll}
        employeeIds={[...selectedNotEnrolledIds]}
        salaryDefinitions={salaryDefinitions}
        gradeOptions={gradeOptions}
        designationOptions={designationOptions}
        workspaceId={workspaceId ?? ''}
        onClose={() => setShowBulkEnroll(false)}
        onSaved={loadEmployees}
      />

      <EditSlideOver
        employee={editingEmployee}
        workspaceId={workspaceId ?? ''}
        onClose={() => setEditingEmployee(null)}
        onSaved={loadEmployees}
      />

      <ChangeContractSlideOver
        employee={changingContractEmployee}
        salaryDefinitions={salaryDefinitions}
        gradeOptions={gradeOptions}
        designationOptions={designationOptions}
        workspaceId={workspaceId ?? ''}
        onClose={() => setChangingContractEmployee(null)}
        onSaved={loadEmployees}
      />

      <ViewContractsSlideOver
        employee={viewingContractsEmployee}
        workspaceId={workspaceId ?? ''}
        onClose={() => setViewingContractsEmployee(null)}
      />

      <AddEmployeeSlideOver
        open={showAddEmployee}
        gradeOptions={gradeOptions}
        designationOptions={designationOptions}
        salaryDefinitions={salaryDefinitions}
        payCycle={payCycle}
        workspaceId={workspaceId ?? ''}
        onClose={() => setShowAddEmployee(false)}
        onSaved={loadEmployees}
      />

      <UploadSlideOver
        open={showUpload}
        workspaceId={workspaceId ?? ''}
        salaryDefinitions={salaryDefinitions}
        designationOptions={designationOptions}
        onClose={() => setShowUpload(false)}
        onSaved={loadEmployees}
      />
    </div>
  );
}
