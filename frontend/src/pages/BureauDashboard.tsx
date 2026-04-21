/**
 * Bureau Dashboard — Gate 4 rewrite
 *
 * Design decisions:
 * - "New Client" opens a SlideOver (absorbs JsonOnboarding; that page is deleted)
 * - LIVE workspaces sort first, then alphabetically within group
 * - Search filter on workspace name (client-side)
 * - Names truncated at 40 chars for display
 */

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { workspaceApi } from '../api/workspace';
import type { Workspace } from '../types/workspace';
import { saveDraft } from '../utils/onboardingDraft';
import {
  ContentHeader,
  Card,
  Btn,
  StatusBadge,
  AlertBanner,
  EmptyState,
  SlideOver,
  TextInput,
  SearchableSelect,
} from '../design-system';

// ── Constants ─────────────────────────────────────────────────────────────────

const COUNTRIES = [
  { value: 'NG', label: 'Nigeria' },
  { value: 'GH', label: 'Ghana' },
  { value: 'KE', label: 'Kenya' },
  { value: 'ZA', label: 'South Africa' },
  { value: 'UG', label: 'Uganda' },
];

const CURRENCIES: Record<string, string> = {
  NG: 'NGN', GH: 'GHS', KE: 'KES', ZA: 'ZAR', UG: 'UGX',
};

function buildConfigTemplate(workspaceId: string): Record<string, unknown> {
  return {
    workspace_id: workspaceId,
    structure: { pay_cycle: {}, grades: [], designations: [] },
    compensation: { salary_definitions: [] },
    rules: { payroll_rules: [] },
  };
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function truncate(s: string, max = 40) {
  return s.length > max ? s.slice(0, max) + '…' : s;
}

function sortWorkspaces(ws: Workspace[]): Workspace[] {
  return [...ws].sort((a, b) => {
    if (a.status === 'LIVE' && b.status !== 'LIVE') return -1;
    if (b.status === 'LIVE' && a.status !== 'LIVE') return 1;
    return a.name.localeCompare(b.name);
  });
}

// ── New Client SlideOver ──────────────────────────────────────────────────────

interface NewClientSlideOverProps {
  open: boolean;
  onClose: () => void;
  onCreated: () => void;
}

function NewClientSlideOver({ open, onClose, onCreated }: NewClientSlideOverProps) {
  const navigate = useNavigate();
  const [wsName, setWsName] = useState('');
  const [wsCountry, setWsCountry] = useState('NG');
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function reset() {
    setWsName('');
    setWsCountry('NG');
    setCreating(false);
    setError(null);
  }

  function handleClose() {
    reset();
    onClose();
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setCreating(true);
    setError(null);
    try {
      const created = await workspaceApi.create({
        name: wsName.trim(),
        country_code: wsCountry,
        base_currency: CURRENCIES[wsCountry] ?? 'NGN',
      });
      saveDraft(created.workspace_id, {
        version: 1,
        workspaceId: created.workspace_id,
        savedAt: new Date().toISOString(),
        activeStep: 'client-config-json',
        rawJson: JSON.stringify(buildConfigTemplate(created.workspace_id), null, 2),
        employees: [],
      });
      onCreated();
      navigate(`/workspaces/${created.workspace_id}/setup`);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to create workspace');
    } finally {
      setCreating(false);
    }
  }

  return (
    <SlideOver
      open={open}
      onClose={handleClose}
      title="New Client"
      description="Create a workspace to begin client onboarding. You will be taken to the setup wizard immediately after."
      footer={
        <div className="flex gap-3">
          <Btn type="submit" form="new-client-form" variant="primary" size="md" loading={creating} disabled={!wsName.trim()}>
            Create &amp; Continue
          </Btn>
          <Btn type="button" variant="secondary" size="md" onClick={handleClose}>
            Cancel
          </Btn>
        </div>
      }
    >
      <form id="new-client-form" onSubmit={handleSubmit} className="space-y-5">
        <TextInput
          label="Client / Company Name"
          value={wsName}
          onChange={(e) => setWsName(e.target.value)}
          placeholder="e.g. Acme Corporation"
          required
          autoFocus
        />
        <SearchableSelect
          label="Country"
          value={wsCountry}
          onChange={setWsCountry}
          options={COUNTRIES}
        />
        <TextInput
          label="Base Currency"
          value={CURRENCIES[wsCountry] ?? 'NGN'}
          onChange={() => {}}
          readOnly
          hint="Determined by country selection"
        />
        {error && <AlertBanner variant="error" title="Failed to create workspace" description={error} />}
      </form>
    </SlideOver>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────

function BuildingIcon() {
  return (
    <svg className="w-full h-full" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
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

export function BureauDashboard() {
  const navigate = useNavigate();

  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [slideOverOpen, setSlideOverOpen] = useState(false);

  function loadWorkspaces() {
    setLoading(true);
    workspaceApi
      .list()
      .then((ws) => setWorkspaces(sortWorkspaces(ws)))
      .catch((e: unknown) => setError(e instanceof Error ? e.message : 'Failed to load'))
      .finally(() => setLoading(false));
  }

  useEffect(() => { loadWorkspaces(); }, []);

  const filtered = search.trim()
    ? workspaces.filter((ws) => ws.name.toLowerCase().includes(search.trim().toLowerCase()))
    : workspaces;

  return (
    <div className="max-w-5xl">
      <ContentHeader
        title="Bureau Dashboard"
        subtitle={loading ? 'Loading…' : `${workspaces.length} workspace${workspaces.length !== 1 ? 's' : ''}`}
        action={
          <Btn
            variant="primary"
            size="md"
            icon={<PlusIcon />}
            iconPosition="left"
            onClick={() => setSlideOverOpen(true)}
          >
            New Client
          </Btn>
        }
      />

      {error && <AlertBanner variant="error" title="Failed to load workspaces" description={error} className="mb-4" />}

      {/* Search */}
      {workspaces.length > 0 && (
        <div className="mb-4 max-w-xs">
          <TextInput
            label=""
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by client name…"
          />
        </div>
      )}

      <Card padding="sm">
        {loading ? (
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                {['Client', 'Country', 'Status', 'Employees', ''].map((h, i) => (
                  <th key={i} className="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-gray-500">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Array.from({ length: 4 }).map((_, i) => (
                <tr key={i} className="animate-pulse border-b border-gray-100">
                  {[50, 20, 20, 15, 10].map((w, j) => (
                    <td key={j} className="px-4 py-3">
                      <div className="h-4 bg-gray-200 rounded" style={{ width: `${w}%` }} />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        ) : filtered.length === 0 ? (
          search ? (
            <div className="py-10 text-center">
              <p className="text-sm text-gray-500">No clients match "<strong>{search}</strong>"</p>
              <button className="mt-1 text-xs text-brand underline hover:opacity-80" onClick={() => setSearch('')}>
                Clear search
              </button>
            </div>
          ) : (
            <EmptyState
              icon={<BuildingIcon />}
              headline="No clients yet"
              body="Create your first client workspace to get started with onboarding."
              action={{ label: '+ New Client', onClick: () => setSlideOverOpen(true) }}
            />
          )
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50 sticky top-0">
                  {['Client', 'Country', 'Status', 'Employees', ''].map((h, i) => (
                    <th
                      key={i}
                      className={`px-4 py-3 text-[11px] font-semibold uppercase tracking-wider text-gray-500 ${i === 2 ? 'text-center' : 'text-left'} ${i === 4 ? 'w-36' : ''}`}
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtered.map((ws) => (
                  <tr
                    key={ws.workspace_id}
                    className="border-b border-gray-100 hover:bg-slate-50 transition-colors cursor-pointer"
                    onClick={() => navigate(`/workspaces/${ws.workspace_id}`)}
                    title={ws.name}
                  >
                    <td className="px-4 py-3 font-medium text-gray-800">
                      {truncate(ws.name)}
                    </td>
                    <td className="px-4 py-3 text-gray-600 text-xs font-mono">{ws.country_code ?? '—'}</td>
                    <td className="px-4 py-3 text-center">
                      <StatusBadge status={ws.status ?? 'DRAFT'} />
                    </td>
                    <td className="px-4 py-3 text-gray-600 tabular-nums">{ws.active_employee_count ?? 0}</td>
                    <td className="px-4 py-3">
                      <Btn
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          if (ws.status === 'DRAFT') {
                            navigate(`/workspaces/${ws.workspace_id}/setup`);
                          } else {
                            navigate(`/workspaces/${ws.workspace_id}`);
                          }
                        }}
                      >
                        {ws.status === 'DRAFT' ? 'Continue Setup →' : 'Open →'}
                      </Btn>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      <NewClientSlideOver
        open={slideOverOpen}
        onClose={() => setSlideOverOpen(false)}
        onCreated={loadWorkspaces}
      />
    </div>
  );
}
