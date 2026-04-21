/**
 * PublicHolidays — Gate 4 rewrite
 *
 * Design decisions:
 * - SlideOver for add holiday + client-side duplicate check
 * - ConfirmDialog for delete (not inline confirm)
 * - IconBtn for year prev/next navigation
 * - NATIONAL rows have no delete button
 */

import { useEffect, useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { workspaceApi } from '../api/workspace';
import type { PublicHoliday } from '../types/payroll';
import {
  ContentHeader,
  Card,
  Btn,
  IconBtn,
  StatusBadge,
  AlertBanner,
  EmptyState,
  SlideOver,
  ConfirmDialog,
  DateInput,
  TextInput,
  useToast,
  Breadcrumb,
} from '../design-system';
import { useWorkspaceContext } from '../context/WorkspaceContext';

// ── Icons ─────────────────────────────────────────────────────────────────────

function ChevronLeft() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
    </svg>
  );
}

function ChevronRight() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
    </svg>
  );
}

function CalendarIcon() {
  return (
    <svg className="w-full h-full" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
    </svg>
  );
}

// ── Holiday grouping helpers ──────────────────────────────────────────────────

const DAY_SUFFIX = / \(Day \d+\)$/;

function formatDate(iso: string): string {
  const [, m, d] = iso.split('-');
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  return `${parseInt(d, 10)} ${months[parseInt(m, 10) - 1]}`;
}

function isConsecutive(date1: string, date2: string): boolean {
  const d1 = new Date(date1 + 'T00:00:00');
  const d2 = new Date(date2 + 'T00:00:00');
  return d2.getTime() - d1.getTime() === 86_400_000;
}

interface HolidayGroup {
  key: string;
  displayName: string;
  dateDisplay: string;
  multiDay: boolean;
  source: string;
  holiday_id: string | null;
  entries: PublicHoliday[];
}

function groupHolidays(holidays: PublicHoliday[]): HolidayGroup[] {
  const groups: HolidayGroup[] = [];
  let i = 0;

  while (i < holidays.length) {
    const h = holidays[i];
    const isMultiPattern = DAY_SUFFIX.test(h.name);
    const baseName = h.name.replace(DAY_SUFFIX, '');

    if (!isMultiPattern) {
      groups.push({
        key: h.holiday_id ?? `ph-${i}`,
        displayName: h.name,
        dateDisplay: formatDate(h.date),
        multiDay: false,
        source: h.source,
        holiday_id: h.holiday_id ?? null,
        entries: [h],
      });
      i++;
      continue;
    }

    const members: PublicHoliday[] = [h];
    let j = i + 1;
    while (j < holidays.length) {
      const next = holidays[j];
      if (
        next.name.replace(DAY_SUFFIX, '') === baseName &&
        next.source === h.source &&
        isConsecutive(members[members.length - 1].date, next.date)
      ) {
        members.push(next);
        j++;
      } else {
        break;
      }
    }

    if (members.length === 1) {
      groups.push({
        key: h.holiday_id ?? `ph-${i}`,
        displayName: h.name,
        dateDisplay: formatDate(h.date),
        multiDay: false,
        source: h.source,
        holiday_id: h.holiday_id ?? null,
        entries: [h],
      });
    } else {
      groups.push({
        key: `group-${h.date}`,
        displayName: baseName,
        dateDisplay: `${formatDate(members[0].date)} – ${formatDate(members[members.length - 1].date)}`,
        multiDay: true,
        source: h.source,
        holiday_id: null,
        entries: members,
      });
    }

    i = j;
  }

  return groups;
}

// ── Add Holiday SlideOver ─────────────────────────────────────────────────────

interface AddSlideOverProps {
  open: boolean;
  year: number;
  existingDates: Set<string>;
  onClose: () => void;
  onAdded: () => void;
  workspaceId: string;
}

function AddHolidaySlideOver({ open, year, existingDates, onClose, onAdded, workspaceId }: AddSlideOverProps) {
  const toast = useToast();
  const [date, setDate] = useState(`${year}-01-01`);
  const [name, setName] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dupeWarning, setDupeWarning] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      setDate(`${year}-01-01`);
      setName('');
      setError(null);
      setDupeWarning(null);
    }
  }, [open, year]);

  function handleDateChange(val: string) {
    setDate(val);
    // Client-side duplicate check
    if (existingDates.has(val)) {
      setDupeWarning(`A holiday on ${val} already exists this year.`);
    } else {
      setDupeWarning(null);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!date || !name.trim()) return;
    if (existingDates.has(date)) {
      setError(`A holiday on ${date} already exists. Please choose a different date.`);
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await workspaceApi.addPublicHoliday(workspaceId, { date, name: name.trim() });
      toast.show('success', 'Public holiday added');
      onAdded();
      onClose();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to add holiday');
    } finally {
      setSaving(false);
    }
  }

  return (
    <SlideOver
      open={open}
      onClose={onClose}
      title="Add Public Holiday"
      description={`Add a workspace-specific holiday for ${year}. National holidays are managed centrally.`}
      footer={
        <div className="flex gap-3">
          <Btn type="submit" form="add-holiday-form" variant="primary" size="md" loading={saving} disabled={!date || !name.trim()}>
            Add Holiday
          </Btn>
          <Btn type="button" variant="secondary" size="md" onClick={onClose}>
            Cancel
          </Btn>
        </div>
      }
    >
      <form id="add-holiday-form" onSubmit={handleSubmit} className="space-y-5">
        <DateInput
          label="Date"
          value={date}
          onChange={handleDateChange}
          required
        />
        {dupeWarning && <AlertBanner variant="warning" description={dupeWarning} />}
        <TextInput
          label="Holiday Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g. Company Founder's Day"
          required
        />
        {error && <AlertBanner variant="error" description={error} />}
      </form>
    </SlideOver>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────

export function PublicHolidays() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const toast = useToast();
  const { workspace } = useWorkspaceContext();
  const currentYear = new Date().getFullYear();

  const [year, setYear] = useState(currentYear);
  const [holidays, setHolidays] = useState<PublicHoliday[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [addOpen, setAddOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<PublicHoliday | null>(null);
  const [deleting, setDeleting] = useState(false);

  const fetchHolidays = useCallback(() => {
    if (!workspaceId) return;
    setLoading(true);
    workspaceApi
      .getPublicHolidays(workspaceId, year)
      .then(setHolidays)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : 'Failed to load'))
      .finally(() => setLoading(false));
  }, [workspaceId, year]);

  useEffect(() => { fetchHolidays(); }, [fetchHolidays]);

  async function handleDelete() {
    if (!workspaceId || !deleteTarget?.holiday_id) return;
    setDeleting(true);
    try {
      await workspaceApi.deletePublicHoliday(workspaceId, deleteTarget.holiday_id);
      toast.show('success', 'Holiday deleted');
      setDeleteTarget(null);
      fetchHolidays();
    } catch (e: unknown) {
      toast.show('error', e instanceof Error ? e.message : 'Delete failed');
    } finally {
      setDeleting(false);
    }
  }

  const existingDates = new Set(holidays.map((h) => h.date));

  return (
    <div className="max-w-3xl">
      <ContentHeader
        title="Public Holidays"
        subtitle={`${year} calendar`}
        back={
          <Breadcrumb items={[
            { label: 'Bureau Dashboard', to: '/' },
            { label: workspace?.name ?? '…', to: `/workspaces/${workspaceId}` },
            { label: 'Public Holidays' },
          ]} />
        }
        action={
          <Btn variant="primary" size="md" onClick={() => setAddOpen(true)}>
            + Add Holiday
          </Btn>
        }
      />

      {error && <AlertBanner variant="error" description={error} className="mb-4" />}

      {/* Year navigator — IconBtn */}
      <div className="flex items-center gap-2 mb-5">
        <IconBtn label={`Previous year (${year - 1})`} onClick={() => setYear((y) => y - 1)}>
          <ChevronLeft />
        </IconBtn>
        <span className="text-base font-semibold text-gray-800 w-16 text-center select-none">{year}</span>
        <IconBtn label={`Next year (${year + 1})`} onClick={() => setYear((y) => y + 1)}>
          <ChevronRight />
        </IconBtn>
      </div>

      <Card padding="sm">
        {loading ? (
          <table className="w-full">
            <tbody>
              {Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="animate-pulse border-b border-gray-100">
                  {[20, 50, 15, 15].map((w, j) => (
                    <td key={j} className="px-4 py-3">
                      <div className="h-4 bg-gray-200 rounded" style={{ width: `${w}%` }} />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        ) : holidays.length === 0 ? (
          <EmptyState
            icon={<CalendarIcon />}
            headline={`No holidays for ${year}`}
            body="National holidays may not be seeded for this country yet. Add workspace-specific holidays using the button above."
            action={{ label: '+ Add Holiday', onClick: () => setAddOpen(true) }}
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50">
                  {['Date', 'Name', 'Source', ''].map((h, i) => (
                    <th
                      key={i}
                      className={`px-4 py-3 text-[11px] font-semibold uppercase tracking-wider text-gray-500 text-left ${i === 3 ? 'w-20' : ''}`}
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {groupHolidays(holidays).map((g) => (
                  <tr key={g.key} className="border-b border-gray-100 hover:bg-slate-50">
                    <td className="px-4 py-3 font-mono text-xs text-gray-600 whitespace-nowrap">
                      {g.dateDisplay}
                    </td>
                    <td className="px-4 py-3 text-gray-800">
                      <span>{g.displayName}</span>
                      {g.multiDay && (
                        <span className="ml-2 inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-amber-50 text-amber-700 border border-amber-200">
                          {g.entries.length} days
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge
                        status={g.source === 'NATIONAL' ? 'NATIONAL' : 'WORKSPACE'}
                        size="sm"
                      />
                    </td>
                    <td className="px-4 py-3">
                      {g.source === 'WORKSPACE' && g.holiday_id ? (
                        <Btn
                          variant="ghost"
                          size="sm"
                          onClick={() => setDeleteTarget(g.entries[0])}
                        >
                          Delete
                        </Btn>
                      ) : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Add holiday SlideOver */}
      {workspaceId && (
        <AddHolidaySlideOver
          open={addOpen}
          year={year}
          existingDates={existingDates}
          workspaceId={workspaceId}
          onClose={() => setAddOpen(false)}
          onAdded={fetchHolidays}
        />
      )}

      {/* Delete ConfirmDialog */}
      <ConfirmDialog
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        title="Delete public holiday?"
        body={
          deleteTarget ? (
            <p className="text-sm text-gray-600">
              Remove <strong>{deleteTarget.name}</strong> ({deleteTarget.date}) from this workspace's calendar?
              National holidays cannot be deleted.
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
