import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { workspaceApi } from '../api/workspace';
import type { Employee } from '../types/payroll';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { AlertBox } from '../components/ui/AlertBox';

export function Employees() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [gradeOptions, setGradeOptions] = useState<string[]>([]);
  const [designationOptions, setDesignationOptions] = useState<string[]>([]);

  const [editingId, setEditingId] = useState<string | null>(null);
  const [editGrade, setEditGrade] = useState('');
  const [editDesignation, setEditDesignation] = useState('');
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  function loadEmployees() {
    if (!workspaceId) return;
    return workspaceApi
      .getEmployees(workspaceId)
      .then(setEmployees)
      .catch((e) => setError(e.message));
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
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [workspaceId]);

  function startEdit(emp: Employee) {
    setEditingId(emp.employee_id);
    setEditGrade(emp.grade ?? '');
    setEditDesignation(emp.designation ?? '');
    setSaveError(null);
  }

  function cancelEdit() {
    setEditingId(null);
    setSaveError(null);
  }

  async function saveEdit(employeeId: string) {
    if (!workspaceId) return;
    setSaving(true);
    setSaveError(null);
    try {
      await workspaceApi.updateEmployeeContract(workspaceId, employeeId, {
        grade_code: editGrade || null,
        designation_code: editDesignation || null,
      });
      await loadEmployees();
      setEditingId(null);
    } catch (e) {
      setSaveError(e instanceof Error ? e.message : 'Save failed');
    } finally {
      setSaving(false);
    }
  }

  const [unmatchedOpen, setUnmatchedOpen] = useState(true);

  const unmatched = employees.filter((e) => !e.grade || !e.designation);
  const matched   = employees.filter((e) => e.grade && e.designation);

  return (
    <div>
      <PageHeader title="Employees" subtitle={`Workspace ${workspaceId}`} />

      {loading && <p className="text-sm text-slate-500">Loading employees…</p>}
      {error && <AlertBox type="error" messages={[error]} />}

      {!loading && !error && employees.length === 0 && (
        <Card>
          <p className="text-sm text-slate-400 py-8 text-center">
            No employees found for this workspace.
          </p>
        </Card>
      )}

      {!loading && !error && employees.length > 0 && (
        <div className="flex flex-col gap-4">
          {/* ── Unmatched section ─────────────────────────────────────────── */}
          {unmatched.length > 0 && (
            <Card>
              <button
                onClick={() => setUnmatchedOpen((v) => !v)}
                className="w-full flex items-center justify-between text-left"
              >
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-700">
                  ⚠ {unmatched.length} employee{unmatched.length !== 1 ? 's' : ''} with missing grade or designation
                </span>
                <span className="text-xs text-slate-400">{unmatchedOpen ? '▲ Hide' : '▼ Show'}</span>
              </button>
              {unmatchedOpen && (
                <div className="mt-3">
                  <EmployeeTable
                    rows={unmatched}
                    editingId={editingId}
                    editGrade={editGrade}
                    editDesignation={editDesignation}
                    gradeOptions={gradeOptions}
                    designationOptions={designationOptions}
                    saving={saving}
                    saveError={saveError}
                    onEdit={startEdit}
                    onCancel={cancelEdit}
                    onSave={saveEdit}
                    onEditGradeChange={setEditGrade}
                    onEditDesignationChange={setEditDesignation}
                    rowClassName="bg-amber-50"
                  />
                </div>
              )}
            </Card>
          )}

          {/* ── Matched section ───────────────────────────────────────────── */}
          <Card>
            {matched.length === 0 ? (
              <p className="text-sm text-slate-400 py-4 text-center">No fully-matched employees.</p>
            ) : (
              <EmployeeTable
                rows={matched}
                editingId={editingId}
                editGrade={editGrade}
                editDesignation={editDesignation}
                gradeOptions={gradeOptions}
                designationOptions={designationOptions}
                saving={saving}
                saveError={saveError}
                onEdit={startEdit}
                onCancel={cancelEdit}
                onSave={saveEdit}
                onEditGradeChange={setEditGrade}
                onEditDesignationChange={setEditDesignation}
              />
            )}
          </Card>
        </div>
      )}
    </div>
  );
}

// ── Shared table ──────────────────────────────────────────────────────────────

interface TableProps {
  rows: Employee[];
  editingId: string | null;
  editGrade: string;
  editDesignation: string;
  gradeOptions: string[];
  designationOptions: string[];
  saving: boolean;
  saveError: string | null;
  rowClassName?: string;
  onEdit: (emp: Employee) => void;
  onCancel: () => void;
  onSave: (id: string) => void;
  onEditGradeChange: (v: string) => void;
  onEditDesignationChange: (v: string) => void;
}

function EmployeeTable({
  rows,
  editingId,
  editGrade,
  editDesignation,
  gradeOptions,
  designationOptions,
  saving,
  saveError,
  rowClassName = '',
  onEdit,
  onCancel,
  onSave,
  onEditGradeChange,
  onEditDesignationChange,
}: TableProps) {
  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b border-slate-100">
          <Th>Name</Th>
          <Th>Employee #</Th>
          <Th>Designation</Th>
          <Th>Grade</Th>
          <Th>Contract Start</Th>
          <Th>Status</Th>
          <Th></Th>
        </tr>
      </thead>
      <tbody>
        {rows.map((emp) => {
          const isEditing = editingId === emp.employee_id;
          return (
            <>
              <tr
                key={emp.employee_id}
                className={`border-b border-slate-50 hover:bg-slate-50 ${rowClassName}`}
              >
                <Td className="font-medium text-slate-800">{emp.full_name}</Td>
                <Td className="font-mono">{emp.employee_number}</Td>
                <Td>
                  {isEditing ? (
                    <select
                      value={editDesignation}
                      onChange={(e) => onEditDesignationChange(e.target.value)}
                      className="border border-slate-300 rounded px-2 py-0.5 text-xs bg-white focus:outline-none focus:ring-1 focus:ring-blue-400 min-w-[140px]"
                    >
                      <option value="">— select —</option>
                      {designationOptions.map((d) => (
                        <option key={d} value={d}>{d}</option>
                      ))}
                    </select>
                  ) : (
                    emp.designation ?? '—'
                  )}
                </Td>
                <Td>
                  {isEditing ? (
                    <select
                      value={editGrade}
                      onChange={(e) => onEditGradeChange(e.target.value)}
                      className="border border-slate-300 rounded px-2 py-0.5 text-xs bg-white focus:outline-none focus:ring-1 focus:ring-blue-400 min-w-[120px]"
                    >
                      <option value="">— select —</option>
                      {gradeOptions.map((g) => (
                        <option key={g} value={g}>{g}</option>
                      ))}
                    </select>
                  ) : (
                    emp.grade ?? '—'
                  )}
                </Td>
                <Td>{emp.contract_start ?? '—'}</Td>
                <Td>
                  <span
                    className={`inline-flex px-2 py-0.5 rounded text-xs font-semibold uppercase ${
                      emp.status === 'ACTIVE'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-slate-100 text-slate-500'
                    }`}
                  >
                    {emp.status}
                  </span>
                </Td>
                <Td>
                  {isEditing ? (
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => onSave(emp.employee_id)}
                        disabled={saving}
                        className="px-2.5 py-1 text-xs font-medium bg-blue-600 text-white rounded hover:bg-blue-500 disabled:opacity-50"
                      >
                        {saving ? 'Saving…' : 'Save'}
                      </button>
                      <button
                        onClick={onCancel}
                        disabled={saving}
                        className="px-2.5 py-1 text-xs font-medium bg-slate-200 text-slate-700 rounded hover:bg-slate-300 disabled:opacity-50"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => onEdit(emp)}
                      className="px-2.5 py-1 text-xs font-medium text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded"
                    >
                      Edit
                    </button>
                  )}
                </Td>
              </tr>
              {isEditing && saveError && (
                <tr key={`${emp.employee_id}-err`} className="bg-red-50">
                  <td colSpan={7} className="px-3 py-1 text-xs text-red-600">{saveError}</td>
                </tr>
              )}
            </>
          );
        })}
      </tbody>
    </table>
  );
}

function Th({ children }: { children?: React.ReactNode }) {
  return (
    <th className="text-left text-xs font-semibold text-slate-500 uppercase tracking-wide py-2 px-3">
      {children}
    </th>
  );
}

function Td({ children, className = '' }: { children?: React.ReactNode; className?: string }) {
  return <td className={`py-3 px-3 text-slate-600 ${className}`}>{children}</td>;
}
