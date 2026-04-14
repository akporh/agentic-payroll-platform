import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { workspaceApi } from '../api/workspace';
import type { PublicHoliday } from '../types/payroll';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Btn } from '../components/ui/Btn';
import { AlertBox } from '../components/ui/AlertBox';

export function PublicHolidays() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const currentYear = new Date().getFullYear();

  const [year, setYear] = useState(currentYear);
  const [holidays, setHolidays] = useState<PublicHoliday[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Add form
  const [addDate, setAddDate] = useState('');
  const [addName, setAddName] = useState('');
  const [addError, setAddError] = useState<string | null>(null);
  const [addSaving, setAddSaving] = useState(false);

  // Delete confirm
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  function fetchHolidays() {
    if (!workspaceId) return;
    setLoading(true);
    workspaceApi.getPublicHolidays(workspaceId, year)
      .then(setHolidays)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    fetchHolidays();
  }, [workspaceId, year]);

  async function handleAdd() {
    if (!workspaceId || !addDate || !addName.trim()) return;
    setAddError(null);
    setAddSaving(true);
    try {
      await workspaceApi.addPublicHoliday(workspaceId, { date: addDate, name: addName.trim() });
      setAddDate('');
      setAddName('');
      fetchHolidays();
    } catch (e: unknown) {
      setAddError(e instanceof Error ? e.message : 'Failed to add holiday');
    } finally {
      setAddSaving(false);
    }
  }

  async function handleDelete(holidayId: string) {
    if (!workspaceId) return;
    setDeleteError(null);
    try {
      await workspaceApi.deletePublicHoliday(workspaceId, holidayId);
      setDeleteId(null);
      fetchHolidays();
    } catch (e: unknown) {
      setDeleteError(e instanceof Error ? e.message : 'Failed to delete holiday');
    }
  }

  return (
    <div>
      <PageHeader
        title="Public Holidays"
        subtitle={`${year} calendar — workspace ${workspaceId}`}
      />

      {/* Year navigator */}
      <div className="flex items-center gap-3 mb-5">
        <button
          onClick={() => setYear((y) => y - 1)}
          className="px-3 py-1.5 text-sm rounded border border-slate-200 hover:bg-slate-50"
        >
          ← {year - 1}
        </button>
        <span className="text-base font-semibold text-slate-700 w-16 text-center">{year}</span>
        <button
          onClick={() => setYear((y) => y + 1)}
          className="px-3 py-1.5 text-sm rounded border border-slate-200 hover:bg-slate-50"
        >
          {year + 1} →
        </button>
      </div>

      {error && <AlertBox type="error" messages={[error]} />}

      <Card>
        {loading ? (
          <p className="text-sm text-slate-400 py-6 text-center">Loading…</p>
        ) : holidays.length === 0 ? (
          <div className="py-6 text-center space-y-2">
            <p className="text-sm text-amber-600 font-medium">No public holidays found for {year}.</p>
            <p className="text-xs text-slate-400">
              National holidays may not be seeded for this country yet. Add workspace-specific holidays below.
            </p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100">
                <Th>Date</Th>
                <Th>Name</Th>
                <Th>Source</Th>
                <Th>Actions</Th>
              </tr>
            </thead>
            <tbody>
              {holidays.map((h, i) => (
                <tr key={i} className="border-b border-slate-50 hover:bg-slate-50">
                  <Td className="font-mono text-xs">{h.date}</Td>
                  <Td>{h.name}</Td>
                  <Td>
                    {h.source === 'NATIONAL' ? (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-blue-100 text-blue-700">
                        National
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-amber-100 text-amber-700">
                        Workspace
                      </span>
                    )}
                  </Td>
                  <Td>
                    {h.source === 'WORKSPACE' && h.holiday_id ? (
                      <button
                        onClick={() => setDeleteId(h.holiday_id!)}
                        className="text-xs text-red-500 hover:text-red-700"
                      >
                        Delete
                      </button>
                    ) : (
                      <span className="text-xs text-slate-300">—</span>
                    )}
                  </Td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>

      {/* Add holiday form */}
      <div className="mt-5">
        <Card title="Add Workspace Holiday">
          <div className="flex gap-3 items-end flex-wrap">
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Date</label>
              <input
                type="date"
                value={addDate}
                onChange={(e) => setAddDate(e.target.value)}
                className="border border-slate-200 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-slate-400"
              />
            </div>
            <div className="flex-1 min-w-40">
              <label className="block text-xs font-medium text-slate-600 mb-1">Name</label>
              <input
                type="text"
                value={addName}
                onChange={(e) => setAddName(e.target.value)}
                placeholder="e.g. Company Founder's Day"
                className="w-full border border-slate-200 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-slate-400"
              />
            </div>
            <Btn
              onClick={handleAdd}
              loading={addSaving}
              disabled={!addDate || !addName.trim()}
            >
              Add Holiday
            </Btn>
          </div>
          {addError && <p className="text-xs text-red-500 mt-2">{addError}</p>}
        </Card>
      </div>

      {/* Delete confirm modal */}
      {deleteId && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-sm w-full mx-4">
            <h3 className="text-base font-semibold text-slate-800 mb-2">Delete holiday?</h3>
            <p className="text-sm text-slate-500 mb-4">
              This will remove the workspace-specific holiday. National holidays cannot be deleted.
            </p>
            {deleteError && <p className="text-xs text-red-500 mb-3">{deleteError}</p>}
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => { setDeleteId(null); setDeleteError(null); }}
                className="px-3 py-1.5 text-sm text-slate-600 border border-slate-200 rounded hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(deleteId)}
                className="px-3 py-1.5 text-sm text-white bg-red-600 rounded hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Th({ children }: { children: React.ReactNode }) {
  return (
    <th className="text-left text-xs font-semibold text-slate-500 uppercase tracking-wide py-2 px-3">
      {children}
    </th>
  );
}

function Td({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return <td className={`py-3 px-3 text-slate-600 ${className}`}>{children}</td>;
}
