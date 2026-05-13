import { useEffect, useState, useCallback, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { payrollApi } from '../api/payroll';
import type { TimesheetEntry, DerivationStatus } from '../types/payroll';
import {
  ContentHeader,
  Card,
  Btn,
  AlertBanner,
  StatusBadge,
  Breadcrumb,
  useToast,
} from '../design-system';
import { useWorkspaceContext } from '../context/WorkspaceContext';

// ── Helpers ───────────────────────────────────────────────────────────────────

function extractError(e: unknown): string {
  if (e instanceof Error) return e.message;
  return String(e);
}

function statusVariant(s: DerivationStatus): 'success' | 'warning' | 'error' | 'info' {
  if (s === 'APPROVED') return 'success';
  if (s === 'DERIVED') return 'info';
  if (s === 'FAILED') return 'error';
  return 'warning'; // PENDING
}

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

function firstOfMonth(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-01`;
}

function lastOfMonth(): string {
  const d = new Date();
  return new Date(d.getFullYear(), d.getMonth() + 1, 0).toISOString().slice(0, 10);
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export function TimesheetUpload() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const { workspace } = useWorkspaceContext();
  const toast = useToast();
  const fileRef = useRef<HTMLInputElement>(null);

  const [periodStart, setPeriodStart] = useState(firstOfMonth());
  const [periodEnd, setPeriodEnd] = useState(lastOfMonth());
  const [entries, setEntries] = useState<TimesheetEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<Record<string, unknown> | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const [deriving, setDeriving] = useState(false);
  const [approving, setApproving] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const loadStatus = useCallback(() => {
    if (!workspaceId || !periodStart) return;
    setLoading(true);
    setLoadError(null);
    payrollApi
      .getTimesheetStatus(workspaceId, periodStart)
      .then(setEntries)
      .catch((e: unknown) => setLoadError(extractError(e)))
      .finally(() => setLoading(false));
  }, [workspaceId, periodStart]);

  useEffect(() => { loadStatus(); }, [loadStatus]);

  async function handleUpload() {
    const file = fileRef.current?.files?.[0];
    if (!file || !workspaceId) return;
    setUploading(true);
    setUploadError(null);
    setUploadResult(null);
    try {
      const result = await payrollApi.uploadTimesheet(workspaceId, periodStart, periodEnd, file);
      setUploadResult(result);
      toast.success('Timesheet uploaded successfully.');
      loadStatus();
    } catch (e) {
      setUploadError(extractError(e));
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = '';
    }
  }

  async function handleDerive() {
    if (!workspaceId) return;
    setDeriving(true);
    setActionError(null);
    try {
      await payrollApi.triggerDerivation(workspaceId, periodStart, periodEnd);
      toast.success('Derivation complete.');
      loadStatus();
    } catch (e) {
      setActionError(extractError(e));
    } finally {
      setDeriving(false);
    }
  }

  async function handleApprove() {
    if (!workspaceId) return;
    setApproving(true);
    setActionError(null);
    try {
      await payrollApi.approveTimesheetPeriod(workspaceId, periodStart, periodEnd);
      toast.success('Timesheet period approved. Inputs are now ready for payroll.');
      loadStatus();
    } catch (e) {
      setActionError(extractError(e));
    } finally {
      setApproving(false);
    }
  }

  const allDerived = entries.length > 0 && entries.every((e) => e.derivation_status === 'DERIVED' || e.derivation_status === 'APPROVED');
  const anyPendingOrFailed = entries.some((e) => e.derivation_status === 'PENDING' || e.derivation_status === 'FAILED');
  const allApproved = entries.length > 0 && entries.every((e) => e.derivation_status === 'APPROVED');
  const canDerive = entries.length > 0 && anyPendingOrFailed && !allApproved;
  const canApprove = allDerived && !allApproved;

  const pendingCount = entries.filter((e) => e.derivation_status === 'PENDING').length;
  const derivedCount = entries.filter((e) => e.derivation_status === 'DERIVED').length;
  const failedCount = entries.filter((e) => e.derivation_status === 'FAILED').length;
  const approvedCount = entries.filter((e) => e.derivation_status === 'APPROVED').length;

  return (
    <div>
      <Breadcrumb items={[
        { label: workspace?.name ?? 'Workspace', to: `/workspaces/${workspaceId}` },
        { label: 'Timesheet' },
      ]} />
      <ContentHeader
        title="Timesheet Upload"
        subtitle="Upload attendance grids, derive payroll inputs, and approve for payroll."
      />

      {/* Period selector */}
      <Card>
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Period</p>
        <div className="flex flex-wrap gap-4 items-end">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Period Start</label>
            <input
              type="date"
              className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={periodStart}
              onChange={(e) => setPeriodStart(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Period End</label>
            <input
              type="date"
              className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={periodEnd}
              onChange={(e) => setPeriodEnd(e.target.value)}
            />
          </div>
          <Btn variant="secondary" size="sm" onClick={loadStatus} disabled={loading}>
            {loading ? 'Loading…' : 'Refresh'}
          </Btn>
        </div>
      </Card>

      {/* Upload */}
      <Card>
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Upload Timesheet</p>
        <div className="flex flex-wrap gap-3 items-center">
          <input
            ref={fileRef}
            type="file"
            accept=".xlsx,.xls"
            aria-label="Timesheet Excel file"
            className="block text-sm text-gray-600 file:mr-3 file:py-1.5 file:px-3 file:border file:border-gray-300 file:rounded file:text-xs file:font-medium file:bg-white file:text-gray-700 hover:file:bg-gray-50"
          />
          <Btn variant="primary" size="sm" onClick={handleUpload} disabled={uploading}>
            {uploading ? 'Uploading…' : 'Upload'}
          </Btn>
        </div>
        {uploadError && <div className="mt-3"><AlertBanner variant="error" description={uploadError} /></div>}
        {uploadResult && (
          <div className="mt-3">
            <AlertBanner variant="success" description={`Upload complete. ${JSON.stringify(uploadResult)}`} />
          </div>
        )}
      </Card>

      {/* Status summary + actions */}
      {entries.length > 0 && (
        <Card>
          <div className="flex items-center justify-between mb-4">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
              Derivation Status — {entries.length} employee(s)
            </p>
            <div className="flex gap-2">
              <Btn variant="secondary" size="sm" onClick={handleDerive} disabled={deriving || !canDerive}>
                {deriving ? 'Deriving…' : 'Derive Inputs'}
              </Btn>
              <Btn
                variant="primary"
                size="sm"
                onClick={handleApprove}
                disabled={approving || !canApprove}
              >
                {approving ? 'Approving…' : 'Approve Period'}
              </Btn>
            </div>
          </div>

          {actionError && <div className="mb-3"><AlertBanner variant="error" description={actionError} /></div>}

          <div className="flex gap-4 mb-4 text-sm">
            {pendingCount > 0 && <span className="text-yellow-600">{pendingCount} Pending</span>}
            {derivedCount > 0 && <span className="text-blue-600">{derivedCount} Derived</span>}
            {approvedCount > 0 && <span className="text-green-600">{approvedCount} Approved</span>}
            {failedCount > 0 && <span className="text-red-600">{failedCount} Failed</span>}
          </div>

          {allApproved && (
            <AlertBanner variant="success" description="All employees approved. Payroll inputs are ready." />
          )}

          <div className="overflow-x-auto mt-2">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  {['Employee', 'Status', 'Summary', 'Error'].map((h) => (
                    <th key={h} className="text-left text-xs font-semibold text-gray-400 uppercase tracking-wide pb-2 pr-4">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {entries.map((e) => {
                  const summary = e.derivation_summary_jsonb as Record<string, unknown> | null;
                  return (
                    <tr key={e.timesheet_entry_id}>
                      <td className="py-2 pr-4">
                        <div className="font-medium">{e.employee_name}</div>
                        <div className="text-xs text-gray-400">{e.employee_number}</div>
                      </td>
                      <td className="py-2 pr-4">
                        <StatusBadge status={e.derivation_status} size="sm" />
                      </td>
                      <td className="py-2 pr-4 text-xs text-gray-600">
                        {summary ? (
                          <span>
                            {summary.proration_factor != null && `Factor: ${summary.proration_factor}`}
                            {summary.total_hours_paid != null && ` · ${summary.total_hours_paid}h paid`}
                            {summary.excess_ot1_hours != null && Number(summary.excess_ot1_hours) > 0 && ` · OT1: ${summary.excess_ot1_hours}h`}
                          </span>
                        ) : '—'}
                      </td>
                      <td className="py-2 text-xs text-red-600">{e.derivation_error ?? '—'}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {loadError && <AlertBanner variant="error" description={loadError} />}

      {!loading && entries.length === 0 && !loadError && (
        <Card>
          <p className="text-sm text-gray-400 text-center py-4">
            No timesheet entries for this period. Upload an attendance grid to get started.
          </p>
        </Card>
      )}
    </div>
  );
}
