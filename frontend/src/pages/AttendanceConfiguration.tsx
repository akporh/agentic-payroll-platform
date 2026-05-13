import { useEffect, useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { payrollApi } from '../api/payroll';
import type { AttendanceCodeConfig } from '../types/payroll';
import {
  ContentHeader,
  Card,
  Btn,
  AlertBanner,
  SlideOver,
  TextInput,
  NumberInput,
  Toggle,
  Breadcrumb,
  useToast,
} from '../design-system';
import { useWorkspaceContext } from '../context/WorkspaceContext';

// ── Helpers ───────────────────────────────────────────────────────────────────

function extractError(e: unknown): string {
  if (e instanceof Error) return e.message;
  return String(e);
}

const CATEGORIES = ['WORK', 'LEAVE', 'OT', 'SHIFT'] as const;
type Category = (typeof CATEGORIES)[number];

// ── Add Code SlideOver ────────────────────────────────────────────────────────

function AddCodeSlideOver({
  open,
  workspaceId,
  onClose,
  onSaved,
}: {
  open: boolean;
  workspaceId: string;
  onClose: () => void;
  onSaved: () => void;
}) {
  const toast = useToast();
  const [clientCode, setClientCode] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState<Category>('LEAVE');
  const [countsAsPaid, setCountsAsPaid] = useState(true);
  const [countsTowardsOt, setCountsTowardsOt] = useState(true);
  const [hoursEquivalent, setHoursEquivalent] = useState('');
  const [unitFraction, setUnitFraction] = useState('');
  const [eligibleForOt, setEligibleForOt] = useState(false);
  const [eligibleForShift, setEligibleForShift] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      setClientCode(''); setDescription(''); setCategory('LEAVE');
      setCountsAsPaid(true); setCountsTowardsOt(true);
      setHoursEquivalent(''); setUnitFraction('');
      setEligibleForOt(false); setEligibleForShift(false);
      setError(null);
    }
  }, [open]);

  async function handleSave() {
    if (!clientCode.trim()) { setError('Code is required.'); return; }
    if (hoursEquivalent && unitFraction) {
      setError('hours_equivalent and unit_fraction are mutually exclusive.');
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await payrollApi.createAttendanceCode(workspaceId, {
        client_code: clientCode.trim().toUpperCase(),
        description: description || null,
        category,
        is_active: true,
        counts_as_paid: countsAsPaid,
        counts_towards_ot_threshold: countsTowardsOt,
        hours_equivalent: hoursEquivalent ? parseFloat(hoursEquivalent) : null,
        unit_fraction: unitFraction ? parseFloat(unitFraction) : null,
        eligible_for_ot: eligibleForOt,
        eligible_for_shift_allowance: eligibleForShift,
      });
      toast.success('Attendance code created.');
      onSaved();
      onClose();
    } catch (e) {
      setError(extractError(e));
    } finally {
      setSaving(false);
    }
  }

  return (
    <SlideOver
      open={open}
      onClose={onClose}
      title="Add Attendance Code"
      footer={
        <div className="flex justify-end gap-3 w-full">
          <Btn variant="secondary" size="md" onClick={onClose}>Cancel</Btn>
          <Btn variant="primary" size="md" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving…' : 'Add Code →'}
          </Btn>
        </div>
      }
    >
      <div className="space-y-4">
        {error && <AlertBanner variant="error" description={error} />}
        <TextInput label="Code" value={clientCode} onChange={setClientCode}
          hint="Short identifier used in the attendance grid (e.g. SLA, OT1)." />
        <TextInput label="Description" value={description} onChange={setDescription} />
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
          <select
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            value={category}
            onChange={(e) => setCategory(e.target.value as Category)}
          >
            {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div className="border-t border-gray-100 pt-4 space-y-3">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Pay Interpretation</p>
          <Toggle label="Counts as paid" checked={countsAsPaid} onChange={setCountsAsPaid} />
          <Toggle label="Counts towards OT threshold" checked={countsTowardsOt} onChange={setCountsTowardsOt}
            hint="Cannot be true when counts as paid is false." />
          <Toggle label="Eligible for OT" checked={eligibleForOt} onChange={setEligibleForOt} />
          <Toggle label="Eligible for shift allowance" checked={eligibleForShift} onChange={setEligibleForShift} />
        </div>
        <div className="border-t border-gray-100 pt-4">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Hours Resolution (mutually exclusive)</p>
          <NumberInput label="Hours equivalent" value={hoursEquivalent} onChange={setHoursEquivalent}
            hint="Fixed hours this code represents (e.g. 6.5 for a half-day sick leave)." />
          <div className="mt-3">
            <NumberInput label="Unit fraction" value={unitFraction} onChange={setUnitFraction}
              hint="Fraction of hours_per_day this code represents (e.g. 1.0 for a full day)." />
          </div>
        </div>
      </div>
    </SlideOver>
  );
}

// ── Edit Policy SlideOver ─────────────────────────────────────────────────────

function EditPolicySlideOver({
  open,
  workspaceId,
  code,
  onClose,
  onSaved,
}: {
  open: boolean;
  workspaceId: string;
  code: AttendanceCodeConfig | null;
  onClose: () => void;
  onSaved: () => void;
}) {
  const toast = useToast();
  const [countsAsPaid, setCountsAsPaid] = useState(true);
  const [countsTowardsOt, setCountsTowardsOt] = useState(true);
  const [hoursEquivalent, setHoursEquivalent] = useState('');
  const [unitFraction, setUnitFraction] = useState('');
  const [eligibleForOt, setEligibleForOt] = useState(false);
  const [eligibleForShift, setEligibleForShift] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open && code) {
      setCountsAsPaid(code.counts_as_paid ?? true);
      setCountsTowardsOt(code.counts_towards_ot_threshold ?? true);
      setHoursEquivalent(code.hours_equivalent != null ? String(code.hours_equivalent) : '');
      setUnitFraction(code.unit_fraction != null ? String(code.unit_fraction) : '');
      setEligibleForOt(code.eligible_for_ot ?? false);
      setEligibleForShift(code.eligible_for_shift_allowance ?? false);
      setError(null);
    }
  }, [open, code]);

  async function handleSave() {
    if (!code) return;
    if (hoursEquivalent && unitFraction) {
      setError('hours_equivalent and unit_fraction are mutually exclusive.');
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await payrollApi.patchAttendancePolicy(workspaceId, code.client_code, {
        counts_as_paid: countsAsPaid,
        counts_towards_ot_threshold: countsTowardsOt,
        hours_equivalent: hoursEquivalent ? parseFloat(hoursEquivalent) : null,
        unit_fraction: unitFraction ? parseFloat(unitFraction) : null,
        eligible_for_ot: eligibleForOt,
        eligible_for_shift_allowance: eligibleForShift,
      });
      toast.success(`Policy updated for ${code.client_code}.`);
      onSaved();
      onClose();
    } catch (e) {
      setError(extractError(e));
    } finally {
      setSaving(false);
    }
  }

  return (
    <SlideOver
      open={open}
      onClose={onClose}
      title={`Edit Policy — ${code?.client_code ?? ''}`}
      footer={
        <div className="flex justify-end gap-3 w-full">
          <Btn variant="secondary" size="md" onClick={onClose}>Cancel</Btn>
          <Btn variant="primary" size="md" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving…' : 'Save →'}
          </Btn>
        </div>
      }
    >
      <div className="space-y-4">
        {error && <AlertBanner variant="error" description={error} />}
        <Toggle label="Counts as paid" checked={countsAsPaid} onChange={setCountsAsPaid} />
        <Toggle label="Counts towards OT threshold" checked={countsTowardsOt} onChange={setCountsTowardsOt}
          hint="Cannot be true when counts as paid is false." />
        <Toggle label="Eligible for OT" checked={eligibleForOt} onChange={setEligibleForOt} />
        <Toggle label="Eligible for shift allowance" checked={eligibleForShift} onChange={setEligibleForShift} />
        <div className="border-t border-gray-100 pt-4">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Hours Resolution (mutually exclusive)</p>
          <NumberInput label="Hours equivalent" value={hoursEquivalent} onChange={setHoursEquivalent} />
          <div className="mt-3">
            <NumberInput label="Unit fraction" value={unitFraction} onChange={setUnitFraction} />
          </div>
        </div>
      </div>
    </SlideOver>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export function AttendanceConfiguration() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const { workspace } = useWorkspaceContext();
  const toast = useToast();

  const [codes, setCodes] = useState<AttendanceCodeConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [addOpen, setAddOpen] = useState(false);
  const [editPolicy, setEditPolicy] = useState<AttendanceCodeConfig | null>(null);

  const load = useCallback(() => {
    if (!workspaceId) return;
    setLoading(true);
    payrollApi
      .getAttendanceCodes(workspaceId)
      .then(setCodes)
      .catch((e: unknown) => setError(extractError(e)))
      .finally(() => setLoading(false));
  }, [workspaceId]);

  useEffect(() => { load(); }, [load]);

  async function toggleActive(code: AttendanceCodeConfig) {
    if (!workspaceId) return;
    try {
      await payrollApi.patchAttendanceCode(workspaceId, code.client_code, {
        is_active: !code.is_active,
      });
      load();
    } catch (e) {
      toast.error(extractError(e));
    }
  }

  const orphans = codes.filter((c) => !c.has_policy);
  const missingHours = codes.filter(
    (c) => c.has_policy && c.category !== 'WORK' && c.hours_equivalent == null && c.unit_fraction == null
  );

  return (
    <div>
      <Breadcrumb items={[
        { label: workspace?.name ?? 'Workspace', to: `/workspaces/${workspaceId}` },
        { label: 'Config', to: `/workspaces/${workspaceId}/config` },
        { label: 'Attendance Codes' },
      ]} />
      <ContentHeader
        title="Attendance Codes"
        subtitle="Manage attendance code semantics and pay interpretation for timesheet derivation."
        action={<Btn variant="primary" size="sm" onClick={() => setAddOpen(true)}>+ Add Code</Btn>}
      />

      {(orphans.length > 0 || missingHours.length > 0) && (
        <div className="mb-4 space-y-2">
          {orphans.length > 0 && (
            <AlertBanner
              variant="warning"
              description={`${orphans.length} code(s) have no policy configured: ${orphans.map((c) => c.client_code).join(', ')}. Derivation will fail for these codes.`}
            />
          )}
          {missingHours.length > 0 && (
            <AlertBanner
              variant="warning"
              description={`${missingHours.length} code(s) are missing hours configuration: ${missingHours.map((c) => c.client_code).join(', ')}. Derivation may return 0 hours.`}
            />
          )}
        </div>
      )}

      {loading ? (
        <p className="text-sm text-gray-400">Loading…</p>
      ) : error ? (
        <AlertBanner variant="error" description={error} />
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  {['Code', 'Description', 'Category', 'Paid', 'OT Threshold', 'Hours Equiv.', 'Unit Frac.', 'Active', ''].map((h) => (
                    <th key={h} className="text-left text-xs font-semibold text-gray-400 uppercase tracking-wide pb-2 pr-3">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {codes.length === 0 && (
                  <tr><td colSpan={9} className="py-6 text-center text-sm text-gray-400">No attendance codes configured.</td></tr>
                )}
                {codes.map((c) => (
                  <tr key={c.client_code} className={c.is_active ? '' : 'opacity-50'}>
                    <td className="py-2 pr-3 font-mono font-semibold">{c.client_code}</td>
                    <td className="py-2 pr-3 text-gray-600">{c.description ?? '—'}</td>
                    <td className="py-2 pr-3">
                      <span className="inline-block px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700">{c.category}</span>
                    </td>
                    <td className="py-2 pr-3">
                      {c.has_policy ? (c.counts_as_paid ? '✓' : '✗') : <span className="text-orange-500 text-xs">No policy</span>}
                    </td>
                    <td className="py-2 pr-3">
                      {c.has_policy ? (c.counts_towards_ot_threshold ? '✓' : '✗') : '—'}
                    </td>
                    <td className="py-2 pr-3">{c.hours_equivalent ?? '—'}</td>
                    <td className="py-2 pr-3">{c.unit_fraction ?? '—'}</td>
                    <td className="py-2 pr-3">{c.is_active ? 'Yes' : 'No'}</td>
                    <td className="py-2 text-right space-x-2 whitespace-nowrap">
                      <Btn variant="secondary" size="sm" onClick={() => setEditPolicy(c)}>Edit Policy</Btn>
                      <Btn variant="secondary" size="sm" onClick={() => toggleActive(c)}>
                        {c.is_active ? 'Disable' : 'Enable'}
                      </Btn>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      <AddCodeSlideOver
        open={addOpen}
        workspaceId={workspaceId ?? ''}
        onClose={() => setAddOpen(false)}
        onSaved={load}
      />
      <EditPolicySlideOver
        open={editPolicy !== null}
        workspaceId={workspaceId ?? ''}
        code={editPolicy}
        onClose={() => setEditPolicy(null)}
        onSaved={load}
      />
    </div>
  );
}
