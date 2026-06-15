import { useState, useMemo } from 'react';

export interface ColumnMapping {
  dataColIdx: number;        // original column index in the raw data row — use this in parseRows
  detectedHeader: string;
  proposedTarget: string | null;
  status: 'matched' | 'unresolved' | 'excluded';
  availableTargets: { value: string; label: string }[];
}

interface Props {
  mappings: ColumnMapping[];
  onChange: (updated: ColumnMapping[]) => void;
  /**
   * System fields the operator MUST map before continuing.
   * Add new entries here as the data model grows — the panel surfaces them automatically.
   */
  requiredTargets?: { value: string; label: string }[];
  /**
   * System fields that are useful but not blocking.
   * Shown in the checklist with muted styling; do not affect the Continue gate.
   */
  optionalTargets?: { value: string; label: string }[];
  /**
   * When true, multiple client columns may map to the same target (e.g. period inputs
   * where Jan OT and Feb OT both map to regular_overtime_days).
   * When false (default), the panel prevents duplicate target assignments.
   */
  allowDuplicateTargets?: boolean;
}

interface SectionProps {
  title: string;
  count: number;
  defaultOpen: boolean;
  children: React.ReactNode;
  action?: React.ReactNode;
}

function Section({ title, count, defaultOpen, children, action }: SectionProps) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <div className="flex items-center bg-gray-50">
        <button
          type="button"
          className="flex-1 flex items-center justify-between px-4 py-3 hover:bg-gray-100 text-left"
          onClick={() => setOpen((v) => !v)}
        >
          <span className="text-sm font-semibold text-gray-700">{title}</span>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-gray-500 bg-gray-200 rounded-full px-2 py-0.5">
              {count}
            </span>
            <svg
              className={`w-4 h-4 text-gray-400 transition-transform ${open ? 'rotate-180' : ''}`}
              fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </button>
        {action && (
          <div className="px-3" onClick={(e) => e.stopPropagation()}>
            {action}
          </div>
        )}
      </div>
      {open && <div className="divide-y divide-gray-100">{children}</div>}
    </div>
  );
}

function XIcon() {
  return (
    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
    </svg>
  );
}

const excludeOption = <option value="__exclude__">— Exclude this column</option>;

export function ColumnMappingPanel({ mappings, onChange, requiredTargets, optionalTargets, allowDuplicateTargets }: Props) {
  function update(idx: number, patch: Partial<ColumnMapping>) {
    const next = mappings.map((m, i) => (i === idx ? { ...m, ...patch } : m));
    onChange(next);
  }

  function excludeAllUnresolved() {
    const next = mappings.map((m) =>
      m.status === 'unresolved' ? { ...m, proposedTarget: null, status: 'excluded' as const } : m
    );
    onChange(next);
  }

  function handleTargetChange(idx: number, value: string) {
    if (value === '__exclude__') {
      update(idx, { proposedTarget: null, status: 'excluded' });
    } else {
      update(idx, { proposedTarget: value, status: 'matched' });
    }
  }

  // Targets already claimed — prevents mapping two client columns to the same system field
  const usedTargets = useMemo(() => {
    const s = new Set<string>();
    mappings.forEach((m) => {
      if (m.status === 'matched' && m.proposedTarget) s.add(m.proposedTarget);
    });
    return s;
  }, [mappings]);

  // Reverse lookup: system field → client column header
  const targetToClientHeader = useMemo(() => {
    const m: Record<string, string> = {};
    mappings.forEach((mapping) => {
      if (mapping.status === 'matched' && mapping.proposedTarget) {
        m[mapping.proposedTarget] = mapping.detectedHeader;
      }
    });
    return m;
  }, [mappings]);

  function renderRow(m: ColumnMapping, globalIdx: number) {
    const availableForThis = allowDuplicateTargets
      ? m.availableTargets
      : m.availableTargets.filter((t) => !usedTargets.has(t.value) || t.value === m.proposedTarget);

    return (
      <div key={globalIdx} className="flex items-center gap-3 px-4 py-2.5">
        <span className="flex-1 text-sm text-gray-700 font-mono truncate" title={m.detectedHeader}>
          {m.detectedHeader}
        </span>
        <svg className="w-4 h-4 text-gray-300 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
        {m.status === 'matched' ? (
          <div className="flex items-center gap-2">
            <select
              className="text-sm border border-gray-200 rounded px-2 py-1 bg-white focus:outline-none focus:ring-1 focus:ring-brand"
              value={m.proposedTarget ?? ''}
              onChange={(e) => handleTargetChange(globalIdx, e.target.value)}
            >
              {availableForThis.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
              {excludeOption}
            </select>
            <svg className="w-4 h-4 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <button
              type="button"
              title="Clear this match"
              className="text-gray-300 hover:text-red-400 transition-colors shrink-0"
              onClick={() => update(globalIdx, { status: 'unresolved', proposedTarget: null })}
              aria-label="Clear match"
            >
              <XIcon />
            </button>
          </div>
        ) : m.status === 'unresolved' ? (
          <select
            className="text-sm border border-red-300 rounded px-2 py-1 bg-white focus:outline-none focus:ring-1 focus:ring-red-400"
            value=""
            onChange={(e) => handleTargetChange(globalIdx, e.target.value)}
          >
            <option value="" disabled>Select field…</option>
            {availableForThis.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
            {excludeOption}
          </select>
        ) : (
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-400 italic">excluded</span>
            <button
              type="button"
              className="text-xs text-brand underline hover:opacity-80"
              onClick={() => update(globalIdx, { status: 'unresolved', proposedTarget: null })}
            >
              reassign
            </button>
          </div>
        )}
      </div>
    );
  }

  const sections = mappings.reduce<{
    unresolved: Array<{ m: ColumnMapping; gi: number }>;
    matched:    Array<{ m: ColumnMapping; gi: number }>;
    excluded:   Array<{ m: ColumnMapping; gi: number }>;
  }>(
    (acc, m, gi) => {
      acc[m.status].push({ m, gi });
      return acc;
    },
    { unresolved: [], matched: [], excluded: [] },
  );

  if (mappings.length === 0) {
    return <p className="text-sm text-gray-400 text-center py-4">No columns detected.</p>;
  }

  const unmappedRequired = requiredTargets
    ? requiredTargets.filter((t) => !usedTargets.has(t.value))
    : [];
  const allRequiredMapped = requiredTargets ? unmappedRequired.length === 0 : true;

  const showChecklist = (requiredTargets && requiredTargets.length > 0) ||
                        (optionalTargets && optionalTargets.length > 0);

  return (
    <div className="space-y-3">

      {/* System fields coverage checklist */}
      {showChecklist && (
        <div className={`rounded-lg border px-4 py-3 space-y-2 ${allRequiredMapped ? 'border-green-200 bg-green-50' : 'border-amber-200 bg-amber-50'}`}>
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold text-gray-700">System fields</span>
            {requiredTargets && requiredTargets.length > 0 && (
              <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${allRequiredMapped ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'}`}>
                {requiredTargets.length - unmappedRequired.length} / {requiredTargets.length} required mapped
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 gap-0.5">
            {/* Required fields */}
            {requiredTargets?.map((t) => {
              const clientCol = targetToClientHeader[t.value];
              const isMapped = !!clientCol;
              return (
                <div key={t.value} className="flex items-center gap-2 text-xs">
                  {isMapped ? (
                    <svg className="w-3.5 h-3.5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <svg className="w-3.5 h-3.5 text-amber-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v4m0 4h.01M12 3a9 9 0 100 18A9 9 0 0012 3z" />
                    </svg>
                  )}
                  <span className={isMapped ? 'text-gray-600' : 'text-amber-700 font-medium'}>
                    {t.label}
                  </span>
                  {isMapped && (
                    <span className="text-gray-400 font-mono truncate">← {clientCol}</span>
                  )}
                  {!isMapped && (
                    <span className="text-amber-500 italic">— expand Excluded below to assign</span>
                  )}
                </div>
              );
            })}

            {/* Optional fields — muted, no warning styling */}
            {optionalTargets && optionalTargets.length > 0 && (
              <>
                {requiredTargets && requiredTargets.length > 0 && (
                  <div className="border-t border-gray-200 mt-1.5 pt-1.5" />
                )}
                {optionalTargets.map((t) => {
                  const clientCol = targetToClientHeader[t.value];
                  const isMapped = !!clientCol;
                  return (
                    <div key={t.value} className="flex items-center gap-2 text-xs">
                      {isMapped ? (
                        <svg className="w-3.5 h-3.5 text-gray-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                        </svg>
                      ) : (
                        <span className="w-3.5 h-3.5 flex items-center justify-center text-gray-300 shrink-0 text-base leading-none">—</span>
                      )}
                      <span className="text-gray-400">
                        {t.label}
                        <span className="ml-1 text-gray-300">(optional)</span>
                      </span>
                      {isMapped && (
                        <span className="text-gray-400 font-mono truncate">← {clientCol}</span>
                      )}
                    </div>
                  );
                })}
              </>
            )}
          </div>
        </div>
      )}

      {/* Matched — shown first so user can verify auto-matches */}
      {sections.matched.length > 0 && (
        <Section title="Matched" count={sections.matched.length} defaultOpen={true}>
          {sections.matched.map(({ gi }) => renderRow(mappings[gi], gi))}
        </Section>
      )}

      {/* Needs attention — only shown when something requires user action */}
      {sections.unresolved.length > 0 && (
        <Section
          title="Needs attention"
          count={sections.unresolved.length}
          defaultOpen={true}
          action={
            <button
              type="button"
              className="text-xs text-gray-500 hover:text-gray-700 underline whitespace-nowrap"
              onClick={excludeAllUnresolved}
            >
              Exclude all
            </button>
          }
        >
          {sections.unresolved.map(({ gi }) => renderRow(mappings[gi], gi))}
        </Section>
      )}

      {/* Excluded — collapsed; user can reassign from here if needed */}
      {sections.excluded.length > 0 && (
        <Section title="Excluded" count={sections.excluded.length} defaultOpen={false}>
          {sections.excluded.map(({ gi }) => renderRow(mappings[gi], gi))}
        </Section>
      )}
    </div>
  );
}
