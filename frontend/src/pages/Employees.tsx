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

import { useEffect, useMemo, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { workspaceApi } from '../api/workspace';
import { employeesApi } from '../api/employees';
import { ApiError } from '../api/client';
import type { ContractRecord } from '../api/employees';
import type { Employee } from '../types/payroll';
import {
  ContentHeader,
  Card,
  Btn,
  IconBtn,
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
  type EmployeeRow,
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

// ── Shared helpers ────────────────────────────────────────────────────────────

function codeLabel(code: string, description: string | null | undefined): string {
  return description ? `${code} — ${description}` : code;
}

// ── Enroll Employee SlideOver ─────────────────────────────────────────────────

function autoMatchSalaryDef(
  gradeLabel: string | null | undefined,
  desigLabel: string | null | undefined,
  salaryDefinitions: SalaryDefinitionOption[]
): string {
  const g = (gradeLabel ?? '').toUpperCase();
  const d = (desigLabel ?? '').toUpperCase();
  if (!g && !d) return '';
  const tryMatch = (code: string) => salaryDefinitions.find(sd => sd.code.toUpperCase() === code) ?? null;
  return (
    (g && d ? tryMatch(`${d}_${g}`) ?? tryMatch(`${g}_${d}`) : null)
    ?? (d ? tryMatch(d) : null)
    ?? (g ? tryMatch(g) : null)
  )?.code ?? '';
}

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
      const gradeMatch = gradeOptions.find(
        g => g.toUpperCase() === (employee.imported_grade_label ?? '').toUpperCase()
      ) ?? '';
      const desgMatch = designationOptions.find(
        d => d.toUpperCase() === (employee.imported_designation_label ?? '').toUpperCase()
      ) ?? '';
      const resolvedGrade = gradeMatch || employee.grade || '';
      const resolvedDesig = desgMatch || employee.designation || '';
      setGrade(resolvedGrade);
      setDesignation(resolvedDesig);
      const matched = autoMatchSalaryDef(resolvedGrade, resolvedDesig, salaryDefinitions);
      setSalaryDefCode(matched);
      setError(null);
    }
  }, [employee, gradeOptions, designationOptions, salaryDefinitions]);

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
  presetSalaryCode?: string;
  presetGradeCode?: string;
  presetDesignationCode?: string;
}

function BulkEnrollSlideOver({
  open, employeeIds, salaryDefinitions, gradeOptions, designationOptions, onClose, onSaved, workspaceId,
  presetSalaryCode, presetGradeCode, presetDesignationCode,
}: BulkEnrollSlideOverProps) {
  const toast = useToast();
  const [salaryDefCode, setSalaryDefCode] = useState('');
  const [grade, setGrade] = useState('');
  const [designation, setDesignation] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      setSalaryDefCode(presetSalaryCode ?? '');
      setGrade(presetGradeCode ?? '');
      setDesignation(presetDesignationCode ?? '');
      setError(null);
    }
  }, [open, presetSalaryCode, presetGradeCode, presetDesignationCode]);

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
          label="Designation (optional)"
          value={designation}
          onChange={setDesignation}
          options={codeOptions(designationOptions)}
        />
        <SearchableSelect
          label="Grade (optional)"
          value={grade}
          onChange={setGrade}
          options={codeOptions(gradeOptions)}
        />
        {error && <AlertBanner variant="error" description={error} />}
      </form>
    </SlideOver>
  );
}

// ── Edit Employee SlideOver ───────────────────────────────────────────────────

interface EditSlideOverProps {
  employee: Employee | null;
  onClose: () => void;
  onSaved: () => void;
  workspaceId: string;
  grades: { code: string; description: string | null }[];
  designations: { code: string; description: string | null }[];
  salaryDefinitions: SalaryDefinitionOption[];
}

function EditSlideOver({ employee, onClose, onSaved, workspaceId, grades, designations, salaryDefinitions }: EditSlideOverProps) {
  const toast = useToast();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState('');
  const [status, setStatus] = useState('ACTIVE');
  const [contractEnd, setContractEnd] = useState('');
  const [gradeCode, setGradeCode] = useState('');
  const [designationCode, setDesignationCode] = useState('');
  const [autoMatchedSalaryDef, setAutoMatchedSalaryDef] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const goToConfig = () => { onClose(); navigate(`/workspaces/${workspaceId}/config`); };

  useEffect(() => {
    if (!employee) return;
    setFullName(employee.full_name ?? '');
    setStatus(employee.status ?? 'ACTIVE');
    setContractEnd(employee.contract_end ?? '');
    setGradeCode(employee.grade ?? '');
    setDesignationCode(employee.designation ?? '');
    setError(null);
  }, [employee]);

  useEffect(() => {
    if (!employee?.is_enrolled) {
      setAutoMatchedSalaryDef(autoMatchSalaryDef(gradeCode, designationCode, salaryDefinitions));
    }
  }, [gradeCode, designationCode, salaryDefinitions, employee?.is_enrolled]);

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
      if (employee.contract_id) {
        const gradeChanged = gradeCode !== (employee.grade ?? '');
        const desigChanged = designationCode !== (employee.designation ?? '');
        const endChanged = contractEnd !== (employee.contract_end ?? '');
        if (gradeChanged || desigChanged || endChanged) {
          await workspaceApi.updateEmployeeContract(workspaceId, employee.employee_id, {
            ...(gradeChanged ? { grade_code: gradeCode || null } : {}),
            ...(desigChanged ? { designation_code: designationCode || null } : {}),
            ...(endChanged ? { contract_end: contractEnd || null, set_contract_end: true } : {}),
          });
        }
      }
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
        <SearchableSelect
          label="Status"
          value={status}
          onChange={setStatus}
          options={[
            { value: 'ACTIVE', label: 'Active' },
            { value: 'INACTIVE', label: 'Inactive' },
          ]}
        />

        {/* Classification */}
        <div className="pt-2 space-y-1 border-t border-gray-100">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider pt-2">Classification</p>
        </div>
        <div className="space-y-1">
          <SearchableSelect
            label="Grade"
            value={gradeCode}
            onChange={setGradeCode}
            options={[
              { value: '', label: '— unassigned —' },
              ...grades.map(g => ({ value: g.code, label: codeLabel(g.code, g.description) })),
            ]}
          />
          <button
            type="button"
            className="text-xs text-indigo-600 hover:underline pl-0.5 mb-4"
            onClick={goToConfig}
          >
            + Add new grade in Configuration
          </button>
        </div>
        <div className="space-y-1">
          <SearchableSelect
            label="Designation"
            value={designationCode}
            onChange={setDesignationCode}
            options={[
              { value: '', label: '— unassigned —' },
              ...designations.map(d => ({ value: d.code, label: codeLabel(d.code, d.description) })),
            ]}
          />
          <button
            type="button"
            className="text-xs text-indigo-600 hover:underline pl-0.5 mb-4"
            onClick={goToConfig}
          >
            + Add new designation in Configuration
          </button>
        </div>

        {/* Auto-matched salary def — shown only for not-enrolled employees when grade matches */}
        {!employee?.is_enrolled && autoMatchedSalaryDef && (
          <div className="rounded-md bg-indigo-50 border border-indigo-100 px-3 py-2.5">
            <p className="text-xs font-medium text-indigo-700">Salary definition at enrolment</p>
            <p className="text-sm font-mono text-indigo-900 mt-0.5">{autoMatchedSalaryDef}</p>
            <p className="text-xs text-indigo-400 mt-0.5">Auto-matched from grade — assigned when you enrol this employee</p>
          </div>
        )}

        <div className="pt-2 border-t border-gray-100">
          <DateInput
            label="Contract End Date"
            value={contractEnd}
            onChange={setContractEnd}
            hint={
              !employee?.contract_id
                ? 'No contract assigned — enroll this employee first'
                : 'Inclusive last paid day. Leave unchanged to keep the current date.'
            }
            disabled={!employee?.contract_id}
          />
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
  const [salaryDefAutoMatched, setSalaryDefAutoMatched] = useState(false);
  const [startDate, setStartDate] = useState('');
  const [grade, setGrade] = useState('');
  const [designation, setDesignation] = useState('');
  const [changeReason, setChangeReason] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (employee) {
      setSalaryDefId('');
      setSalaryDefAutoMatched(false);
      setStartDate('');
      setGrade(employee.grade ?? '');
      setDesignation(employee.designation ?? '');
      setChangeReason('');
      setError(null);
    }
  }, [employee]);

  useEffect(() => {
    if (!grade) { setSalaryDefAutoMatched(false); return; }
    const matchedCode = autoMatchSalaryDef(grade, designation, salaryDefinitions);
    if (matchedCode) {
      const matchedDef = salaryDefinitions.find(sd => sd.code === matchedCode);
      if (matchedDef) {
        setSalaryDefId(matchedDef.salary_definition_id);
        setSalaryDefAutoMatched(true);
        return;
      }
    }
    setSalaryDefAutoMatched(false);
  }, [grade, designation, salaryDefinitions]);

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
        {salaryDefAutoMatched ? (
          <div className="space-y-1">
            <p className="text-xs font-medium text-gray-700">New Salary Definition</p>
            <p className="text-sm text-gray-900 font-mono">
              {salaryDefinitions.find(sd => sd.salary_definition_id === salaryDefId)?.code ?? salaryDefId}
            </p>
            <p className="text-xs text-gray-400">Auto-matched from grade — change grade to update</p>
          </div>
        ) : (
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
        )}
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

// ── View Contracts SlideOver ──────────────────────────────────────────────────

interface ViewContractsSlideOverProps {
  employee: Employee | null;
  onClose: () => void;
  workspaceId: string;
}

function ViewContractsSlideOver({ employee, onClose, workspaceId }: ViewContractsSlideOverProps) {
  const toast = useToast();
  const [contract, setContract] = useState<ContractRecord | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [localStatus, setLocalStatus] = useState<string>('ACTIVE');
  const [toggling, setToggling] = useState(false);
  const [endContractOpen, setEndContractOpen] = useState(false);
  const [endContractDate, setEndContractDate] = useState('');
  const [endingSaving, setEndingSaving] = useState(false);

  useEffect(() => {
    if (!employee || !workspaceId) return;
    setLocalStatus(employee.status ?? 'ACTIVE');
    setLoading(true);
    setContract(null);
    setError(null);
    setEndContractOpen(false);
    setEndContractDate('');
    employeesApi
      .getEmployee(workspaceId, employee.employee_id)
      .then((detail) => setContract(detail.contracts[0] ?? null))
      .catch((e: unknown) => setError(e instanceof Error ? e.message : 'Failed to load'))
      .finally(() => setLoading(false));
  }, [employee, workspaceId]);

  async function handleToggleStatus() {
    if (!employee) return;
    const newStatus = localStatus === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE';
    setToggling(true);
    try {
      await workspaceApi.patchEmployee(workspaceId, employee.employee_id, { status: newStatus });
      setLocalStatus(newStatus);
      window.dispatchEvent(new Event('employees-changed'));
      toast.show('success', newStatus === 'INACTIVE' ? 'Employee deactivated' : 'Employee activated');
    } catch {
      toast.show('error', 'Failed to update status');
    } finally {
      setToggling(false);
    }
  }

  async function handleEndContract() {
    if (!employee || !endContractDate) return;
    setEndingSaving(true);
    try {
      await workspaceApi.updateEmployeeContract(workspaceId, employee.employee_id, {
        contract_end: endContractDate,
        set_contract_end: true,
      });
      window.dispatchEvent(new Event('employees-changed'));
      toast.show('success', 'Contract ended');
      onClose();
    } catch (e: unknown) {
      toast.show('error', e instanceof Error ? e.message : 'Failed to end contract');
    } finally {
      setEndingSaving(false);
    }
  }

  return (
    <SlideOver
      open={!!employee}
      onClose={onClose}
      title="Contract Management"
      description={employee ? `${employee.full_name} · ${employee.employee_number}` : ''}
      footer={
        <Btn variant="secondary" size="md" onClick={onClose}>
          Close
        </Btn>
      }
    >
      <div className="space-y-5">
        {/* Status management */}
        <div className="rounded-lg border border-gray-200 overflow-hidden">
          <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Status</span>
          </div>
          <div className="px-4 py-3 flex items-center justify-between">
            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
              localStatus === 'ACTIVE' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
            }`}>
              {localStatus}
            </span>
            <Btn
              variant="secondary"
              size="sm"
              loading={toggling}
              onClick={handleToggleStatus}
            >
              {localStatus === 'ACTIVE' ? 'Deactivate' : 'Activate'}
            </Btn>
          </div>
        </div>

        {/* End contract */}
        {contract && !contract.end_date && (
          <div className="rounded-lg border border-gray-200 overflow-hidden">
            <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">End Contract</span>
            </div>
            <div className="px-4 py-3">
              {endContractOpen ? (
                <div className="space-y-3">
                  <DateInput
                    label="Contract End Date"
                    value={endContractDate}
                    onChange={setEndContractDate}
                    hint="Last paid day — inclusive"
                    required
                  />
                  <div className="flex gap-2">
                    <Btn
                      variant="primary"
                      size="sm"
                      loading={endingSaving}
                      onClick={handleEndContract}
                    >
                      Confirm
                    </Btn>
                    <Btn
                      variant="secondary"
                      size="sm"
                      onClick={() => { setEndContractOpen(false); setEndContractDate(''); }}
                    >
                      Cancel
                    </Btn>
                  </div>
                </div>
              ) : (
                <button
                  className="text-xs text-rose-600 hover:text-rose-800 hover:underline"
                  onClick={() => setEndContractOpen(true)}
                >
                  End Contract…
                </button>
              )}
            </div>
          </div>
        )}

        {/* Contract details */}
        {loading ? (
          <p className="text-sm text-gray-400">Loading…</p>
        ) : error ? (
          <AlertBanner variant="error" description={error} />
        ) : !contract ? (
          <p className="text-sm text-gray-400">No contract on record.</p>
        ) : (
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
        )}
      </div>
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
  onClose: () => void;
  onSaved: () => void;
  workspaceId: string;
  grades: { code: string; description: string | null }[];
  designations: { code: string; description: string | null }[];
}

function AddEmployeeSlideOver({ open, onClose, onSaved, workspaceId, grades, designations }: AddEmployeeSlideOverProps) {
  const toast = useToast();
  const navigate = useNavigate();
  const goToConfig = () => { onClose(); navigate(`/workspaces/${workspaceId}/config`); };
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [employeeNumber, setEmployeeNumber] = useState('');
  const [tin, setTin] = useState('');
  const [rsa, setRsa] = useState('');
  const [bank, setBank] = useState('');
  const [accountNumber, setAccountNumber] = useState('');
  const [contractStart, setContractStart] = useState('');
  const [contractEnd, setContractEnd] = useState('');
  const [gradeCode, setGradeCode] = useState('');
  const [designationCode, setDesignationCode] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [addedCount, setAddedCount] = useState(0);

  function reset() {
    setFirstName(''); setLastName(''); setEmployeeNumber('');
    setContractStart(''); setContractEnd('');
    setTin(''); setRsa(''); setBank(''); setAccountNumber('');
    setGradeCode(''); setDesignationCode('');
    setError(null);
  }

  function handleClose() { reset(); setAddedCount(0); onClose(); }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!firstName.trim() || !lastName.trim() || !employeeNumber.trim() || !contractStart) {
      setError('First name, last name, employee number, and contract start date are required.');
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const result = await workspaceApi.createEmployee(workspaceId, {
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        employee_number: employeeNumber.trim(),
        salary_definition_code: null,
        grade_code: gradeCode || null,
        designation_code: designationCode || null,
        contract_start: contractStart,
        contract_end: contractEnd || null,
        tin: tin || null,
        rsa: rsa || null,
        bank: bank || null,
        account_number: accountNumber || null,
      });
      toast.show('success', `${result.full_name} registered`);
      reset();
      setAddedCount(c => c + 1);
      onSaved();
      // stay open so the user can register the next employee
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to register employee');
    } finally {
      setSaving(false);
    }
  }

  return (
    <SlideOver
      open={open}
      onClose={handleClose}
      title="Register Employee"
      description="Add employees to HR. Enroll them in payroll from the list once done."
      footer={
        <div className="flex gap-3">
          <Btn type="submit" form="add-employee-form" variant="primary" size="md" loading={saving}>
            Register
          </Btn>
          <Btn type="button" variant="secondary" size="md" onClick={handleClose}>
            {addedCount > 0 ? `Done (${addedCount} added)` : 'Cancel'}
          </Btn>
        </div>
      }
    >
      <form id="add-employee-form" onSubmit={handleSave} className="space-y-5">

        {/* Identity */}
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

        {/* Contract dates */}
        <div className="pt-2 space-y-1 border-t border-gray-100">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider pt-2">Contract</p>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <DateInput
            label="Start Date"
            value={contractStart}
            onChange={setContractStart}
            hint="First day of employment"
            required
          />
          <DateInput
            label="End Date"
            value={contractEnd}
            onChange={setContractEnd}
            hint="Leave blank if open-ended"
          />
        </div>

        {/* Classification */}
        <div className="pt-2 space-y-1 border-t border-gray-100">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider pt-2">
            Classification
            <span className="ml-1 text-[10px] font-normal normal-case text-gray-400">optional</span>
          </p>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <SearchableSelect
              label="Grade"
              value={gradeCode}
              onChange={setGradeCode}
              options={[
                { value: '', label: '— unassigned —' },
                ...grades.map(g => ({ value: g.code, label: codeLabel(g.code, g.description) })),
              ]}
            />
            <button
              type="button"
              className="text-xs text-indigo-600 hover:underline pl-0.5"
              onClick={goToConfig}
            >
              + Add new grade in Configuration
            </button>
          </div>
          <div className="space-y-1">
            <SearchableSelect
              label="Designation"
              value={designationCode}
              onChange={setDesignationCode}
              options={[
                { value: '', label: '— unassigned —' },
                ...designations.map(d => ({ value: d.code, label: codeLabel(d.code, d.description) })),
              ]}
            />
            <button
              type="button"
              className="text-xs text-indigo-600 hover:underline pl-0.5"
              onClick={goToConfig}
            >
              + Add new designation in Configuration
            </button>
          </div>
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
  status: 'created' | 'skipped' | 'failed';
  error?: string;
}

interface UploadSlideOverProps {
  open: boolean;
  onClose: () => void;
  onSaved: () => void;
  workspaceId: string;
}

function UploadSlideOver({ open, onClose, onSaved, workspaceId }: UploadSlideOverProps) {
  const toast = useToast();
  const [employees, setEmployees] = useState<EmployeeRow[]>([]);
  const [importing, setImporting] = useState(false);
  const [results, setResults] = useState<ImportResult[] | null>(null);

  function handleClose() {
    if (importing) return;
    setEmployees([]);
    setResults(null);
    onClose();
  }

  async function handleImport() {
    if (employees.length === 0) return;
    setImporting(true);

    const settled = await Promise.allSettled(
      employees.map((emp) =>
        workspaceApi.createEmployee(workspaceId, {
          first_name: emp.first_name,
          last_name: emp.last_name,
          employee_number: emp.employee_id,
          salary_definition_code: null,            // ALWAYS null — grade is payroll setup, not upload
          grade_code: null,                        // ALWAYS null
          designation_code: null,                  // ALWAYS null
          imported_grade_label: emp.grade || null,
          imported_designation_label: emp.designation || null,
          contract_start: emp.contract_start || null,
          contract_end: emp.contract_end || null,
          tin: emp.tin || null,
          rsa: emp.rsa || null,
          bank: emp.bank || null,
          account_number: emp.account_number || null,
        }).then((): ImportResult => ({
          name: `${emp.first_name} ${emp.last_name}`,
          employee_number: emp.employee_id,
          status: 'created',
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
        })
      )
    );
    const importResults: ImportResult[] = settled.map((s) =>
      s.status === 'fulfilled' ? s.value : { name: '', employee_number: '', status: 'failed' as const, error: 'Unexpected rejection' }
    );

    setResults(importResults);
    setImporting(false);

    const newCount = importResults.filter((r) => r.status === 'created').length;
    if (newCount > 0) {
      toast.show('success', `${newCount} employee${newCount !== 1 ? 's' : ''} registered`);
      onSaved();
    }
  }

  const createdCount = results?.filter((r) => r.status === 'created').length ?? 0;
  const skippedCount = results?.filter((r) => r.status === 'skipped').length ?? 0;
  const failedCount  = results?.filter((r) => r.status === 'failed').length ?? 0;

  const importLabel = importing
    ? 'Registering…'
    : employees.length === 0
      ? 'Register'
      : `Register ${employees.length} employee${employees.length !== 1 ? 's' : ''}`;

  return (
    <SlideOver
      open={open}
      onClose={handleClose}
      title="Upload Employees"
      description="Register employees from an Excel or CSV file — payroll structure is assigned separately"
      footer={
        results ? (
          <Btn variant="secondary" size="md" onClick={handleClose}>
            Close
          </Btn>
        ) : (
          <div className="flex items-center gap-3">
            <Btn
              variant="primary"
              size="md"
              loading={importing}
              disabled={employees.length === 0 || importing}
              onClick={handleImport}
            >
              {importLabel}
            </Btn>
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
            <p className="text-sm text-gray-600">
              {[
                createdCount > 0 && `${createdCount} registered`,
                skippedCount > 0 && `${skippedCount} already registered`,
                failedCount > 0 && `${failedCount} failed`,
              ].filter(Boolean).join(' · ')}
            </p>
            {createdCount > 0 && (
              <AlertBanner
                variant="success"
                title={`${createdCount} employee${createdCount !== 1 ? 's' : ''} registered`}
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
                title={`${failedCount} employee${failedCount !== 1 ? 's' : ''} failed`}
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
            onEmployeesLoaded={setEmployees}
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
    ? ['Name', 'Employee #', 'Grade', 'Designation', 'Start Date', '']
    : ['Name', 'Employee #', 'Designation', 'Grade', 'Start Date', 'End Date', ''];
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
                className={`px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-gray-500 whitespace-nowrap${
                  i === baseHeaders.length - 1
                    ? ' sticky right-0 bg-gray-50 shadow-[-4px_0_8px_-4px_rgba(0,0,0,0.06)]'
                    : ''
                }`}
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
              className={`group border-b border-gray-100 hover:bg-slate-50 transition-colors ${
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
              {isNotEnrolled ? (
                <>
                  <td className="px-4 py-3 text-gray-600 text-xs">
                    {emp.imported_grade_label
                      ? <><span className="font-mono">{emp.imported_grade_label}</span><span className="ml-1 text-slate-400">(imported)</span></>
                      : <span className="text-gray-300">—</span>
                    }
                  </td>
                  <td className="px-4 py-3 text-gray-600 text-xs">
                    {emp.imported_designation_label
                      ? <><span className="font-mono">{emp.imported_designation_label}</span><span className="ml-1 text-slate-400">(imported)</span></>
                      : <span className="text-gray-300">—</span>
                    }
                  </td>
                </>
              ) : (
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
              <td className="sticky right-0 bg-white group-hover:bg-slate-50 transition-colors shadow-[-4px_0_8px_-4px_rgba(0,0,0,0.06)] px-4 py-3">
                <div className="flex gap-0.5 items-center">
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
                      <IconBtn label="Edit" size="sm" onClick={() => onEdit(emp)}>
                        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                      </IconBtn>
                    </>
                  ) : variant === 'active' ? (
                    <>
                      {onChangeContract && (
                        <IconBtn label="Change Grade / Salary" size="sm" onClick={() => onChangeContract(emp)}>
                          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M7 16V4m0 0L3 8m4-4 4 4"/><path d="M17 8v12m0 0 4-4m-4 4-4-4"/></svg>
                        </IconBtn>
                      )}
                      {onViewContracts && (
                        <IconBtn label="Contract Management" size="sm" onClick={() => onViewContracts(emp)}>
                          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                        </IconBtn>
                      )}
                    </>
                  ) : (
                    <>
                      <IconBtn label="Edit" size="sm" onClick={() => onEdit(emp)}>
                        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                      </IconBtn>
                      {variant !== 'ended' && onChangeContract && (
                        <IconBtn label="Change Grade / Salary" size="sm" onClick={() => onChangeContract(emp)}>
                          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M7 16V4m0 0L3 8m4-4 4 4"/><path d="M17 8v12m0 0 4-4m-4 4-4-4"/></svg>
                        </IconBtn>
                      )}
                      {onViewContracts && (
                        <IconBtn label="Contract Management" size="sm" onClick={() => onViewContracts(emp)}>
                          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                        </IconBtn>
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
  const navigate = useNavigate();
  const { workspace } = useWorkspaceContext();
  const toast = useToast();

  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [gradeOptions, setGradeOptions] = useState<string[]>([]);
  const [designationOptions, setDesignationOptions] = useState<string[]>([]);
  const [grades, setGrades] = useState<{ code: string; description: string | null }[]>([]);
  const [designations, setDesignations] = useState<{ code: string; description: string | null }[]>([]);
  const [salaryDefinitions, setSalaryDefinitions] = useState<SalaryDefinitionOption[]>([]);
  const [payCycle, setPayCycle] = useState<PayCycleSummary | null>(null);
  const [editingEmployee, setEditingEmployee] = useState<Employee | null>(null);
  const [changingContractEmployee, setChangingContractEmployee] = useState<Employee | null>(null);
  const [viewingContractsEmployee, setViewingContractsEmployee] = useState<Employee | null>(null);
  const [enrollingEmployee, setEnrollingEmployee] = useState<Employee | null>(null);
  const [showAddEmployee, setShowAddEmployee] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [showBulkEnroll, setShowBulkEnroll] = useState(false);
  const [bulkEnrollPresetIds, setBulkEnrollPresetIds] = useState<string[]>([]);
  const [bulkEnrollPresetCode, setBulkEnrollPresetCode] = useState<string | undefined>(undefined);
  const [bulkEnrollPresetGradeCode, setBulkEnrollPresetGradeCode] = useState<string | undefined>(undefined);
  const [bulkEnrollPresetDesignationCode, setBulkEnrollPresetDesignationCode] = useState<string | undefined>(undefined);
  const [expandedGroups, setExpandedGroups] = useState<Set<number>>(new Set());
  const [enrollingGroupIdx, setEnrollingGroupIdx] = useState<number | null>(null);
  const [showEnded, setShowEnded] = useState(false);
  const [parkingEmployeeId, setParkingEmployeeId] = useState<string | null>(null);

  const unmatchedRef = useRef<HTMLDivElement>(null);
  const notEnrolledRef = useRef<HTMLDivElement>(null);
  const activeRef = useRef<HTMLDivElement>(null);
  const endedRef = useRef<HTMLDivElement>(null);

  function loadEmployees() {
    if (!workspaceId) return;
    workspaceApi
      .getEmployees(workspaceId)
      .then((data) => {
        setEmployees(data);
        window.dispatchEvent(new CustomEvent('employees-changed'));
      })
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
        setGrades(config.grades);
        setDesignations(config.designations);
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

  async function handleDirectEnroll(idx: number, group: typeof suggestedGroups[0]) {
    if (!workspaceId || !group.matchedDef) return;
    setEnrollingGroupIdx(idx);
    try {
      const result = await workspaceApi.bulkEnrollEmployees(workspaceId, {
        employee_ids: group.employeeIds,
        salary_definition_code: group.matchedDef.code,
        grade_code: group.matchedGrade ?? group.rawGradeLabel ?? null,
        designation_code: group.matchedDesignation ?? group.rawDesigLabel ?? null,
      });
      const msg = result.skipped > 0
        ? `${result.enrolled} enrolled — ${result.skipped} already enrolled (skipped)`
        : `${result.enrolled} employee${result.enrolled !== 1 ? 's' : ''} enrolled`;
      toast.show('success', msg);
      loadEmployees();
      setExpandedGroups(prev => { const s = new Set(prev); s.delete(idx); return s; });
    } catch {
      // Direct enroll failed (e.g. invalid designation/grade code) — open SlideOver so user can resolve
      openBulkEnrollFromSuggestion(
        group.employeeIds,
        group.matchedDef?.code,
        group.matchedGrade ?? group.rawGradeLabel ?? undefined,
        group.matchedDesignation ?? group.rawDesigLabel ?? undefined,
      );
    } finally {
      setEnrollingGroupIdx(null);
    }
  }

  const { ended, deactivated, live, notEnrolled, unmatched, matched, deactivatedEnrolled } = useMemo(() => {
    const ended       = employees.filter((e) => e.is_ended);
    const deactivated = employees.filter((e) => !e.is_ended && e.status === 'INACTIVE');
    const live        = employees.filter((e) => !e.is_ended && e.status !== 'INACTIVE');
    // not-enrolled includes INACTIVE (paused) so operator can see and enrol them without un-pausing first
    const notEnrolled = employees.filter((e) => !e.is_ended && !e.is_enrolled);
    const unmatched   = live.filter((e) => e.is_enrolled && (!e.grade || !e.designation));
    const matched     = live.filter((e) => e.is_enrolled && e.grade && e.designation);
    // Enrolled INACTIVE with live contract — valid HR state (suspension) but excluded from payroll
    const deactivatedEnrolled = deactivated.filter((e) => e.is_enrolled);
    return { ended, deactivated, live, notEnrolled, unmatched, matched, deactivatedEnrolled };
  }, [employees]);
  const canEnroll = salaryDefinitions.length > 0;

  // Auto-suggest: group not-enrolled employees by (designation + grade), find matching salary defs
  const suggestedGroups = useMemo(() => {
    const grouped = new Map<string, { employees: typeof notEnrolled; desigLabel: string; gradeLabel: string }>();
    for (const emp of notEnrolled) {
      // Use imported label if present; fall back to the assigned grade/designation code
      const desigLabel = (emp.imported_designation_label ?? emp.designation ?? '').toUpperCase();
      const gradeLabel = (emp.imported_grade_label ?? emp.grade ?? '').toUpperCase();
      const key = `${desigLabel}|${gradeLabel}`;
      const existing = grouped.get(key);
      if (existing) existing.employees.push(emp);
      else grouped.set(key, { employees: [emp], desigLabel, gradeLabel });
    }
    return Array.from(grouped.entries())
      .map(([, { employees: emps, desigLabel, gradeLabel }]) => {
        const matchedGrade = gradeOptions.find(g => g.toUpperCase() === gradeLabel) ?? null;
        const matchedDesignation = designationOptions.find(d => d.toUpperCase() === desigLabel) ?? null;
        const firstEmp = emps[0];
        // For the enrol API call, prefer imported label (original casing); fall back to assigned code
        const rawGradeLabel = firstEmp?.imported_grade_label ?? firstEmp?.grade ?? null;
        const rawDesigLabel = firstEmp?.imported_designation_label ?? firstEmp?.designation ?? null;
        const tryMatch = (code: string) => salaryDefinitions.find(sd => sd.code.toUpperCase() === code) ?? null;
        const matchedDef = tryMatch(`${desigLabel}_${gradeLabel}`)
          ?? tryMatch(`${gradeLabel}_${desigLabel}`)
          ?? (desigLabel ? tryMatch(desigLabel) : null)
          ?? (gradeLabel ? tryMatch(gradeLabel) : null);
        return {
          desigLabel: desigLabel || null,
          gradeLabel: gradeLabel || null,
          rawGradeLabel,
          rawDesigLabel,
          count: emps.length,
          employeeIds: emps.map((e) => e.employee_id),
          matchedGrade,
          matchedDesignation,
          matchedDef,
        };
      })
      .sort((a, b) => {
        if (!!a.matchedDef !== !!b.matchedDef) return a.matchedDef ? -1 : 1;
        return b.count - a.count;
      });
  }, [notEnrolled, salaryDefinitions, gradeOptions, designationOptions]);

  function openBulkEnrollFromSuggestion(
    ids: string[],
    salaryCode?: string,
    gradeCode?: string,
    designationCode?: string,
  ) {
    setBulkEnrollPresetIds(ids);
    setBulkEnrollPresetCode(salaryCode);
    setBulkEnrollPresetGradeCode(gradeCode);
    setBulkEnrollPresetDesignationCode(designationCode);
    setShowBulkEnroll(true);
  }

  function downloadEmployeeTemplate() {
    const headers = [
      'employee_id','first_name','last_name','grade','designation',
      'tin','rsa','bank','account_number','contract_start','contract_end',
    ];
    const csv = headers.join(',') + '\n';
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'employee_upload_template.csv'; a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="max-w-5xl">
      <ContentHeader
        title="Employees"
        subtitle={
          loading ? 'Loading…' :
          employees.length === 0 ? undefined :
          <span className="flex gap-2 items-center flex-wrap">
            {notEnrolled.length > 0 && (
              <button className="text-amber-600 hover:underline cursor-pointer" onClick={() => notEnrolledRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })}>
                {notEnrolled.length} awaiting enrollment
              </button>
            )}
            {unmatched.length > 0 && <><span className="text-gray-400">·</span>
            <button className="text-rose-600 hover:underline cursor-pointer" onClick={() => unmatchedRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })}>
              {unmatched.length} incomplete
            </button></>}
            {matched.length > 0 && <><span className="text-gray-400">·</span>
            <button className="text-green-700 hover:underline cursor-pointer" onClick={() => activeRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })}>
              {matched.length} in payroll
            </button></>}
            {ended.length > 0 && <><span className="text-gray-400">·</span>
            <button className="text-gray-500 hover:underline cursor-pointer" onClick={() => { setShowEnded(true); endedRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }); }}>
              {ended.length} contract ended
            </button></>}
            {deactivatedEnrolled.length > 0 && <><span className="text-gray-400">·</span>
            <button className="text-gray-500 hover:underline cursor-pointer" onClick={() => { setShowEnded(true); endedRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }); }}>
              {deactivatedEnrolled.length} deactivated
            </button></>}
          </span>
        }
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
          variant={canEnroll ? 'warning' : 'info'}
          title={`${notEnrolled.length} employee${notEnrolled.length !== 1 ? 's' : ''} not enrolled in payroll`}
          description={
            canEnroll
              ? 'These employees will not appear in payroll runs until a salary definition is assigned.'
              : 'To enroll these employees in payroll, set up a salary structure in Configuration.'
          }
          action={
            canEnroll
              ? { label: 'View not enrolled →', onClick: () => notEnrolledRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }) }
              : { label: 'Set up salary structure →', onClick: () => navigate(`/workspaces/${workspaceId}/config`) }
          }
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
            label: 'View incomplete →',
            onClick: () => unmatchedRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }),
          }}
          className="mb-4"
        />
      )}

      {/* Suspended / deactivated with live contract banner */}
      {!loading && deactivatedEnrolled.length > 0 && (
        <AlertBanner
          variant="info"
          title={`${deactivatedEnrolled.length} employee${deactivatedEnrolled.length !== 1 ? 's' : ''} inactive with a live contract`}
          description="These employees are enrolled and have an active contract but their HR status is Inactive — they will not appear in payroll runs until reactivated."
          action={{
            label: 'View inactive →',
            onClick: () => endedRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }),
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
        <div className="space-y-4">
          {!canEnroll && (
            <AlertBanner
              variant="info"
              title="Set up salary structure before enrolling"
              description="Add salary definitions in Configuration so employees can be enrolled in payroll after upload."
              action={{ label: 'Go to Configuration →', onClick: () => navigate(`/workspaces/${workspaceId}/config`) }}
            />
          )}
          <div className="grid grid-cols-2 gap-4">
            <Card padding="md">
              <div className="flex flex-col h-full gap-3">
                <div className="w-10 h-10 rounded-lg bg-indigo-50 flex items-center justify-center shrink-0">
                  <UploadIcon className="w-5 h-5 text-indigo-600" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 text-sm">Upload from Excel</h3>
                  <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                    Bulk import employees using a spreadsheet. Download the template to get the correct column format.
                  </p>
                  <p className="text-[10px] font-mono text-gray-400 mt-2 leading-relaxed">
                    employee_id · first_name · last_name · grade · designation<br />
                    tin · rsa · bank · account_number · contract_start
                  </p>
                </div>
                <div className="flex gap-2 pt-1">
                  <Btn variant="ghost" size="sm" onClick={downloadEmployeeTemplate}>
                    Download template
                  </Btn>
                  <Btn variant="primary" size="sm" icon={<UploadIcon />} onClick={() => setShowUpload(true)}>
                    Upload spreadsheet
                  </Btn>
                </div>
              </div>
            </Card>
            <Card padding="md">
              <div className="flex flex-col h-full gap-3">
                <div className="w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center shrink-0">
                  <PlusIcon className="w-5 h-5 text-slate-500" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 text-sm">Add one at a time</h3>
                  <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                    Enter employee details manually. Best for individual additions or corrections after an initial upload.
                  </p>
                </div>
                <div className="pt-1">
                  <Btn variant="secondary" size="sm" icon={<PlusIcon />} onClick={() => setShowAddEmployee(true)}>
                    Add Employee
                  </Btn>
                </div>
              </div>
            </Card>
          </div>
        </div>
      ) : (
        <div className="space-y-5">
          {/* Awaiting Enrollment section — accordion groups */}
          {notEnrolled.length > 0 && (
            <div ref={notEnrolledRef}>
              <Card padding="sm">
                <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-0.5 h-4 rounded-full bg-amber-500" aria-hidden="true" />
                    <span className="text-xs font-semibold text-gray-700 uppercase tracking-wide">
                      Awaiting Enrollment
                    </span>
                    <span className="text-xs text-gray-400 tabular-nums font-normal">
                      {notEnrolled.length} employee{notEnrolled.length !== 1 ? 's' : ''}
                    </span>
                  </div>
                  <p className="text-xs text-gray-400">No salary structure assigned</p>
                </div>
                {/* Group header row */}
                <div className="grid text-[10px] uppercase tracking-wider text-gray-400 px-4 py-2 border-b border-gray-100 gap-x-3" style={{ gridTemplateColumns: 'auto 1fr 1fr auto 1fr auto' }}>
                  <span />
                  <span>Designation</span>
                  <span>Grade</span>
                  <span className="text-right">Count</span>
                  <span>Salary Def</span>
                  <span />
                </div>
                {suggestedGroups.map((g, i) => {
                  const isExpanded = expandedGroups.has(i);
                  const isFullyResolved = !!(g.matchedDef);
                  const isEnrolling = enrollingGroupIdx === i;
                  return (
                    <div key={i} className="border-b border-gray-100 last:border-b-0">
                      {/* Group row */}
                      <div
                        className="grid items-center gap-x-3 text-xs px-4 py-2.5 cursor-pointer hover:bg-gray-50 transition-colors"
                        style={{ gridTemplateColumns: 'auto 1fr 1fr auto 1fr auto' }}
                        onClick={() => setExpandedGroups(prev => {
                          const s = new Set(prev);
                          if (s.has(i)) s.delete(i); else s.add(i);
                          return s;
                        })}
                      >
                        <span className="text-gray-400 w-3 text-center select-none">{isExpanded ? '▾' : '▸'}</span>
                        <span className="font-mono text-slate-700 truncate">{g.desigLabel ?? <span className="text-slate-400 italic">not set</span>}</span>
                        <span className="font-mono text-slate-700 truncate">{g.gradeLabel ?? <span className="text-slate-400 italic">not set</span>}</span>
                        <span className="text-slate-500 text-right tabular-nums">{g.count}</span>
                        {g.matchedDef
                          ? <span className="font-mono text-green-700 truncate">{g.matchedDef.code}</span>
                          : <span className="text-amber-600">no match</span>
                        }
                        <span onClick={(e) => e.stopPropagation()}>
                          <Btn
                            variant={g.matchedDef ? 'primary' : 'secondary'}
                            size="sm"
                            disabled={!canEnroll}
                            loading={isEnrolling}
                            onClick={() => {
                              if (isFullyResolved) {
                                handleDirectEnroll(i, g);
                              } else {
                                openBulkEnrollFromSuggestion(
                                  g.employeeIds,
                                  g.matchedDef?.code,
                                  g.matchedGrade ?? undefined,
                                  g.matchedDesignation ?? undefined,
                                );
                              }
                            }}
                          >
                            {g.matchedDef ? `Enroll ${g.count}` : 'Select →'}
                          </Btn>
                        </span>
                      </div>
                      {/* Expanded employee list */}
                      {isExpanded && (
                        <div className="bg-gray-50 border-t border-gray-100">
                          {g.employeeIds.map((eid) => {
                            const emp = notEnrolled.find(e => e.employee_id === eid);
                            if (!emp) return null;
                            return (
                              <div key={eid} className="flex items-center px-8 py-1.5 text-xs border-b border-gray-100 last:border-b-0 hover:bg-gray-100 transition-colors gap-2">
                                <span className={`min-w-0 truncate ${emp.status === 'INACTIVE' ? 'text-gray-400' : 'text-gray-800'}`}>{emp.full_name}</span>
                                <span className="text-gray-400 font-mono shrink-0">{emp.employee_number}</span>
                                {emp.status === 'INACTIVE' && (
                                  <span className="shrink-0 inline-flex items-center rounded-full bg-gray-100 px-1.5 py-0.5 text-[10px] font-medium text-gray-500">
                                    Paused
                                  </span>
                                )}
                                <div className="ml-auto flex items-center gap-3 shrink-0">
                                  <button
                                    className="text-indigo-600 hover:underline"
                                    onClick={() => setEnrollingEmployee(emp)}
                                  >
                                    Enroll →
                                  </button>
                                  <button
                                    className="flex items-center justify-center min-w-[44px] min-h-[44px] text-gray-400 hover:text-indigo-600"
                                    title="Edit employee"
                                    aria-label="Edit employee"
                                    onClick={() => setEditingEmployee(emp)}
                                  >
                                    <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                                  </button>
                                  {/* Pause / Resume toggle */}
                                  <button
                                    className="flex items-center justify-center min-w-[44px] min-h-[44px] text-gray-400 hover:text-amber-600 disabled:opacity-40"
                                    title={emp.status === 'INACTIVE' ? 'Resume — move back to enrolment queue' : 'Pause — keep registered but remove from queue'}
                                    aria-label={emp.status === 'INACTIVE' ? 'Resume employee' : 'Pause employee'}
                                    disabled={parkingEmployeeId === emp.employee_id}
                                    onClick={async () => {
                                      setParkingEmployeeId(emp.employee_id);
                                      const newStatus = emp.status === 'INACTIVE' ? 'ACTIVE' : 'INACTIVE';
                                      try {
                                        await workspaceApi.patchEmployee(workspaceId!, emp.employee_id, { status: newStatus });
                                        loadEmployees();
                                      } catch {
                                        toast.show('error', newStatus === 'ACTIVE' ? 'Failed to resume employee' : 'Failed to pause employee');
                                      } finally {
                                        setParkingEmployeeId(null);
                                      }
                                    }}
                                  >
                                    {parkingEmployeeId === emp.employee_id
                                      ? '…'
                                      : emp.status === 'INACTIVE'
                                        /* Resume/play icon */
                                        ? <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                                        /* Pause icon */
                                        : <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
                                    }
                                  </button>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  );
                })}
              </Card>
            </div>
          )}

          {/* Incomplete section */}
          {unmatched.length > 0 && (
            <div ref={unmatchedRef}>
              <Card padding="sm">
                <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-0.5 h-4 rounded-full bg-rose-500" aria-hidden="true" />
                    <span className="text-xs font-semibold text-gray-700 uppercase tracking-wide">
                      Incomplete
                    </span>
                    <span className="text-xs text-gray-400 tabular-nums font-normal">
                      {unmatched.length} employee{unmatched.length !== 1 ? 's' : ''}
                    </span>
                  </div>
                  <p className="text-xs text-gray-400">Grade or designation missing</p>
                </div>
                <EmployeeTable rows={unmatched} variant="unmatched" onEdit={setEditingEmployee} onChangeContract={setChangingContractEmployee} onViewContracts={setViewingContractsEmployee} />
              </Card>
            </div>
          )}

          {/* In Payroll section */}
          {matched.length > 0 && (
            <div ref={activeRef}>
            <Card padding="sm">
              <div className="px-4 py-3 border-b border-gray-100">
                <div className="flex items-center gap-3">
                  <div className="w-0.5 h-4 rounded-full bg-green-500" aria-hidden="true" />
                  <span className="text-xs font-semibold text-gray-700 uppercase tracking-wide">
                    In Payroll
                  </span>
                  <span className="text-xs text-gray-400 tabular-nums font-normal">
                    {matched.length} employee{matched.length !== 1 ? 's' : ''}
                  </span>
                </div>
              </div>
              <EmployeeTable rows={matched} variant="active" onEdit={setEditingEmployee} onChangeContract={setChangingContractEmployee} onViewContracts={setViewingContractsEmployee} />
            </Card>
            </div>
          )}

          {/* No Longer Active section — collapsed by default */}
          {(ended.length > 0 || deactivated.length > 0) && (
            <div ref={endedRef}>
              <div
                style={{ borderRadius: 'var(--radius-card)', boxShadow: 'var(--shadow-card)' }}
                className="bg-white overflow-hidden"
              >
                <button
                  className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
                  onClick={() => setShowEnded(v => !v)}
                  aria-expanded={showEnded}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-0.5 h-4 rounded-full bg-gray-300" aria-hidden="true" />
                    <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                      No Longer Active
                    </span>
                    <span className="text-xs text-gray-400 tabular-nums font-normal">
                      {ended.length + deactivated.length} employee{(ended.length + deactivated.length) !== 1 ? 's' : ''}
                    </span>
                  </div>
                  <svg
                    className={`w-4 h-4 text-gray-400 shrink-0 transition-transform duration-200 ${showEnded ? 'rotate-180' : ''}`}
                    fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                {showEnded && (
                  <div className="border-t border-gray-100">
                    {ended.length > 0 && (
                      <>
                        <div className="px-4 py-2 border-b border-gray-100 flex items-center gap-2">
                          <div className="w-0.5 h-3 rounded-full bg-gray-300" aria-hidden="true" />
                          <span className="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">
                            Contract Ended
                          </span>
                          <span className="text-[10px] text-gray-300 tabular-nums">
                            {ended.length}
                          </span>
                        </div>
                        <EmployeeTable
                          rows={ended}
                          variant="ended"
                          onEdit={setEditingEmployee}
                          onViewContracts={setViewingContractsEmployee}
                        />
                      </>
                    )}
                    {deactivated.length > 0 && (
                      <>
                        <div className="px-4 py-2 border-b border-gray-100 flex items-center gap-2">
                          <div className="w-0.5 h-3 rounded-full bg-gray-300" aria-hidden="true" />
                          <span className="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">
                            Manually Deactivated
                          </span>
                          <span className="text-[10px] text-gray-300 tabular-nums">
                            {deactivated.length}
                          </span>
                        </div>
                        <EmployeeTable
                          rows={deactivated}
                          variant="ended"
                          onEdit={setEditingEmployee}
                          onViewContracts={setViewingContractsEmployee}
                        />
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
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
        employeeIds={bulkEnrollPresetIds}
        salaryDefinitions={salaryDefinitions}
        gradeOptions={gradeOptions}
        designationOptions={designationOptions}
        workspaceId={workspaceId ?? ''}
        presetSalaryCode={bulkEnrollPresetCode}
        presetGradeCode={bulkEnrollPresetGradeCode}
        presetDesignationCode={bulkEnrollPresetDesignationCode}
        onClose={() => {
          setShowBulkEnroll(false);
          setBulkEnrollPresetIds([]);
          setBulkEnrollPresetCode(undefined);
          setBulkEnrollPresetGradeCode(undefined);
          setBulkEnrollPresetDesignationCode(undefined);
        }}
        onSaved={loadEmployees}
      />

      <EditSlideOver
        employee={editingEmployee}
        workspaceId={workspaceId ?? ''}
        grades={grades}
        designations={designations}
        salaryDefinitions={salaryDefinitions}
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
        workspaceId={workspaceId ?? ''}
        grades={grades}
        designations={designations}
        onClose={() => setShowAddEmployee(false)}
        onSaved={loadEmployees}
      />

      <UploadSlideOver
        open={showUpload}
        workspaceId={workspaceId ?? ''}
        onClose={() => setShowUpload(false)}
        onSaved={loadEmployees}
      />
    </div>
  );
}
