/**
 * Employees — Gate 4 rewrite
 *
 * Design decisions:
 * - Edit opens a SlideOver (not inline row editing)
 * - AlertBanner for unmatched employees with scroll-to link
 * - border-l-4 border-amber-400 on unmatched rows (not colour alone — accessibility)
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
  useToast,
  Breadcrumb,
} from '../design-system';
import { useWorkspaceContext } from '../context/WorkspaceContext';

// ── Icons ─────────────────────────────────────────────────────────────────────

function PeopleIcon() {
  return (
    <svg className="w-full h-full" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
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
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (employee) {
      setGrade(employee.grade ?? '');
      setDesignation(employee.designation ?? '');
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
        {error && <AlertBanner variant="error" description={error} />}
      </form>
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
  const dateHeader = variant === 'ended' ? 'Contract End' : 'Contract Start';
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="border-b border-gray-200 bg-gray-50">
            {['Name', 'Employee #', 'Designation', 'Grade', dateHeader, 'Status', ''].map((h, i) => (
              <th
                key={i}
                className="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-gray-500"
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
              <td className="px-4 py-3 text-gray-500 text-xs">
                {variant === 'ended' ? (emp.contract_end ?? '—') : (emp.contract_start ?? '—')}
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
  const [editingEmployee, setEditingEmployee] = useState<Employee | null>(null);

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
                  {[40, 20, 20, 15, 15, 10, 5].map((w, j) => (
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
            body="Employees are added during workspace onboarding. Complete the setup wizard to import your headcount."
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
                <EmployeeTable
                  rows={unmatched}
                  variant="unmatched"
                  onEdit={setEditingEmployee}
                />
              </Card>
            </div>
          )}

          {/* Matched section */}
          {matched.length > 0 && (
            <Card padding="sm">
              <div className="px-4 py-3 border-b border-gray-100">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  Matched — {matched.length} employee{matched.length !== 1 ? 's' : ''}
                </p>
              </div>
              <EmployeeTable
                rows={matched}
                variant="active"
                onEdit={setEditingEmployee}
              />
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
              <EmployeeTable
                rows={ended}
                variant="ended"
                onEdit={setEditingEmployee}
              />
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
    </div>
  );
}
