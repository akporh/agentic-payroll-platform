/**
 * RateCodes — Gate 5 / UI-NAV-3
 *
 * Rate Code Registry: view platform codes (read-only) and manage
 * workspace-specific codes for OT, PH, and shift allowances.
 *
 * Design decisions:
 * - Two Card sections: Platform (read-only) and Workspace (CRUD)
 * - SlideOver for add — keeps the main page uncluttered
 * - ConfirmDialog for delete (destructive action)
 * - Breadcrumb via ContentHeader `back` prop
 */

import { useEffect, useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { workspaceApi } from '../api/workspace';
import type { RateCode } from '../types/payroll';
import {
  ContentHeader,
  Card,
  Btn,
  AlertBanner,
  EmptyState,
  SlideOver,
  ConfirmDialog,
  TextInput,
  NumberInput,
  SearchableSelect,
  useToast,
  Breadcrumb,
} from '../design-system';
import { useWorkspaceContext } from '../context/WorkspaceContext';

// ── Icons ─────────────────────────────────────────────────────────────────────

function TagIcon() {
  return (
    <svg className="w-full h-full" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
    </svg>
  );
}

// ── Add Rate Code SlideOver ───────────────────────────────────────────────────

interface AddSlideOverProps {
  open: boolean;
  workspaceId: string;
  onClose: () => void;
  onAdded: () => void;
}

function AddRateCodeSlideOver({ open, workspaceId, onClose, onAdded }: AddSlideOverProps) {
  const toast = useToast();
  const [code, setCode] = useState('');
  const [multiplier, setMultiplier] = useState('');
  const [unit, setUnit] = useState('hour');
  const [base, setBase] = useState('basic_hourly');
  const [description, setDescription] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      setCode('');
      setMultiplier('');
      setUnit('hour');
      setBase('basic_hourly');
      setDescription('');
      setError(null);
    }
  }, [open]);

  // Keep base in sync with unit selection sensibly
  function handleUnitChange(val: string) {
    setUnit(val);
    setBase(val === 'hour' ? 'basic_hourly' : 'basic_daily');
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const mult = parseFloat(multiplier);
    if (!code.trim() || isNaN(mult) || mult <= 0) return;
    setSaving(true);
    setError(null);
    try {
      await workspaceApi.addRateCode(workspaceId, {
        code: code.trim().toUpperCase(),
        multiplier: mult,
        unit: unit as 'hour' | 'day',
        base: base as 'basic_hourly' | 'basic_daily',
        description: description.trim() || undefined,
      });
      toast.show('success', `Rate code ${code.trim().toUpperCase()} added`);
      onAdded();
      onClose();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to add rate code');
    } finally {
      setSaving(false);
    }
  }

  const canSubmit = code.trim().length > 0 && parseFloat(multiplier) > 0;

  return (
    <SlideOver
      open={open}
      onClose={onClose}
      title="Add Rate Code"
      description="Define a workspace-specific multiplier for overtime, public holidays, or shift allowances."
      footer={
        <div className="flex gap-3">
          <Btn type="submit" form="add-rate-code-form" variant="primary" size="md" loading={saving} disabled={!canSubmit}>
            Add Rate Code
          </Btn>
          <Btn type="button" variant="secondary" size="md" onClick={onClose}>
            Cancel
          </Btn>
        </div>
      }
    >
      <form id="add-rate-code-form" onSubmit={handleSubmit} className="space-y-5">
        <TextInput
          label="Code"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="e.g. SHIFT2"
          hint="Uppercase letters, digits, and underscores. Will be stored in uppercase."
          required
        />
        <NumberInput
          label="Multiplier"
          value={multiplier}
          onChange={(e) => setMultiplier(e.target.value)}
          placeholder="e.g. 1.5"
          hint="The rate factor applied to the base. Must be greater than 0."
          required
          min={0}
          step="0.01"
        />
        <SearchableSelect
          label="Unit"
          value={unit}
          onChange={handleUnitChange}
          options={[
            { value: 'hour', label: 'Hour' },
            { value: 'day',  label: 'Day'  },
          ]}
          required
        />
        <SearchableSelect
          label="Base"
          value={base}
          onChange={setBase}
          options={[
            { value: 'basic_hourly', label: 'Basic Hourly Rate' },
            { value: 'basic_daily',  label: 'Basic Daily Rate'  },
          ]}
          required
        />
        <TextInput
          label="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="e.g. Weekend shift allowance at 25%"
        />
        {error && <AlertBanner variant="error" description={error} />}
      </form>
    </SlideOver>
  );
}

// ── Rate Code Table ───────────────────────────────────────────────────────────

interface RateCodeTableProps {
  codes: RateCode[];
  onDelete?: (rc: RateCode) => void;
}

function RateCodeTable({ codes, onDelete }: RateCodeTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="border-b border-gray-200 bg-gray-50">
            {['Code', 'Multiplier', 'Unit', 'Base', 'Description', ''].map((h, i) => (
              <th
                key={i}
                className={`px-4 py-3 text-[11px] font-semibold uppercase tracking-wider text-gray-500 text-left ${i === 5 ? 'w-20' : ''}`}
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {codes.map((rc) => (
            <tr key={rc.rate_code_id} className="border-b border-gray-100 hover:bg-slate-50">
              <td className="px-4 py-3 font-mono text-xs font-semibold text-gray-800">{rc.code}</td>
              <td className="px-4 py-3 text-right tabular-nums text-gray-700">{rc.multiplier}×</td>
              <td className="px-4 py-3 text-gray-600 capitalize">{rc.unit}</td>
              <td className="px-4 py-3 text-gray-600 text-xs">{rc.base.replace(/_/g, ' ')}</td>
              <td className="px-4 py-3 text-gray-500 text-xs">{rc.description ?? '—'}</td>
              <td className="px-4 py-3">
                {onDelete && (
                  <Btn variant="ghost" size="sm" onClick={() => onDelete(rc)}>
                    Delete
                  </Btn>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ── Skeleton Rows ─────────────────────────────────────────────────────────────

function TableSkeleton() {
  return (
    <table className="w-full">
      <tbody>
        {Array.from({ length: 4 }).map((_, i) => (
          <tr key={i} className="animate-pulse border-b border-gray-100">
            {[15, 10, 8, 14, 30, 8].map((w, j) => (
              <td key={j} className="px-4 py-3">
                <div className="h-4 bg-gray-200 rounded" style={{ width: `${w}%` }} />
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────

export function RateCodes() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const { workspace } = useWorkspaceContext();
  const toast = useToast();

  const [rateCodes, setRateCodes] = useState<RateCode[]>([]);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  const [addOpen, setAddOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<RateCode | null>(null);
  const [deleting, setDeleting] = useState(false);

  const fetchRateCodes = useCallback(() => {
    if (!workspaceId) return;
    setLoading(true);
    workspaceApi
      .getRateCodes(workspaceId)
      .then(setRateCodes)
      .catch((e: unknown) => setFetchError(e instanceof Error ? e.message : 'Failed to load rate codes'))
      .finally(() => setLoading(false));
  }, [workspaceId]);

  useEffect(() => { fetchRateCodes(); }, [fetchRateCodes]);

  async function handleDelete() {
    if (!workspaceId || !deleteTarget) return;
    setDeleting(true);
    try {
      await workspaceApi.deleteRateCode(workspaceId, deleteTarget.code);
      toast.show('success', `Rate code ${deleteTarget.code} deleted`);
      setDeleteTarget(null);
      fetchRateCodes();
    } catch (e: unknown) {
      toast.show('error', e instanceof Error ? e.message : 'Delete failed');
    } finally {
      setDeleting(false);
    }
  }

  const platformCodes  = rateCodes.filter(rc => rc.is_platform);
  const workspaceCodes = rateCodes.filter(rc => !rc.is_platform);

  const breadcrumb = (
    <Breadcrumb items={[
      { label: 'Bureau Dashboard', to: '/' },
      { label: workspace?.name ?? '…', to: `/workspaces/${workspaceId}` },
      { label: 'Rate Codes' },
    ]} />
  );

  return (
    <div className="max-w-4xl space-y-8">
      <ContentHeader
        title="Rate Codes"
        subtitle="Multipliers for overtime, public holidays, and shift allowances"
        back={breadcrumb}
        action={
          <Btn variant="primary" size="md" onClick={() => setAddOpen(true)}>
            + Add Rate Code
          </Btn>
        }
      />

      {fetchError && <AlertBanner variant="error" description={fetchError} />}

      {/* Platform codes — read-only */}
      <section>
        <div className="mb-3">
          <h2 className="text-sm font-semibold text-gray-700">Platform Rate Codes</h2>
          <p className="text-xs text-gray-500 mt-0.5">Seeded by the platform. These codes apply to all workspaces and cannot be modified.</p>
        </div>
        <Card padding="sm">
          {loading ? (
            <TableSkeleton />
          ) : platformCodes.length === 0 ? (
            <p className="px-4 py-6 text-sm text-gray-400 text-center">No platform codes seeded yet.</p>
          ) : (
            <RateCodeTable codes={platformCodes} />
          )}
        </Card>
      </section>

      {/* Workspace codes — editable */}
      <section>
        <div className="mb-3">
          <h2 className="text-sm font-semibold text-gray-700">Workspace Rate Codes</h2>
          <p className="text-xs text-gray-500 mt-0.5">Custom multipliers for this workspace. These override or supplement platform codes.</p>
        </div>
        <Card padding="sm">
          {loading ? (
            <TableSkeleton />
          ) : workspaceCodes.length === 0 ? (
            <EmptyState
              icon={<TagIcon />}
              headline="No workspace rate codes"
              body="Add custom multipliers for overtime shifts, public holiday pay, or any workspace-specific rate."
              action={{ label: '+ Add Rate Code', onClick: () => setAddOpen(true) }}
            />
          ) : (
            <RateCodeTable codes={workspaceCodes} onDelete={setDeleteTarget} />
          )}
        </Card>
      </section>

      {/* Add SlideOver */}
      {workspaceId && (
        <AddRateCodeSlideOver
          open={addOpen}
          workspaceId={workspaceId}
          onClose={() => setAddOpen(false)}
          onAdded={fetchRateCodes}
        />
      )}

      {/* Delete confirmation */}
      <ConfirmDialog
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        title="Delete rate code?"
        body={
          deleteTarget ? (
            <p className="text-sm text-gray-600">
              Remove <strong>{deleteTarget.code}</strong> ({deleteTarget.multiplier}× {deleteTarget.unit}) from this workspace?
              This cannot be undone.
            </p>
          ) : undefined
        }
        confirmLabel="Delete"
        cancelLabel="Cancel"
        destructive
        loading={deleting}
      />
    </div>
  );
}
