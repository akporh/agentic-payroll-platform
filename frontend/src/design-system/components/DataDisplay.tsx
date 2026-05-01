/**
 * Data Display — DAT-1 through DAT-6
 *
 * SummaryCard       DAT-1 — single KPI card
 * SummaryCards      DAT-1 — 3-up or 4-up KPI row
 * DataTable         DAT-2 — sortable, hoverable, sticky-header table
 * ExpandableRow     DAT-3 — smooth expand/collapse (grid-template-rows, DD-17)
 * ComponentTraceRow DAT-4 — payroll component trace sub-row
 * ReconciliationCard DAT-5 — rec summary with status variant styling
 * TimelineRow       DAT-6 — audit/timeline entry
 *
 * Rules:
 * - Text columns: left-aligned. Monetary: right-aligned + tabular-nums. Status: centre.
 * - DD-17: expandable rows use grid-template-rows (not max-height) + 200ms ease-out
 * - ui-designer: sticky headers on scrollable tables
 * - ux-designer: skeleton rows for loading (STS-4); empty state for no-data (FBK-4)
 * - Monetary values: ₦ prefix, comma separators, right-aligned
 */

import React, { useState } from 'react';
import { StatusBadge } from './Status';

// ── Monetary formatter ────────────────────────────────────────────────────────

export function formatNaira(value: number | string | null | undefined): string {
  if (value == null || value === '') return '—';
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '—';
  return `₦${num.toLocaleString('en-NG', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

// ── DAT-1 — Summary Card ──────────────────────────────────────────────────────

export interface SummaryCardProps {
  label: string;
  value: string | number | null;
  sublabel?: string;
  /** When true, value renders in KPI size (29px) */
  large?: boolean;
  className?: string;
}

export function SummaryCard({ label, value, sublabel, large = false, className = '' }: SummaryCardProps) {
  return (
    <div
      style={{
        borderRadius: 'var(--radius-card)',
        boxShadow: 'var(--shadow-card)',
      }}
      className={`bg-white px-6 py-5 ${className}`}
    >
      <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">{label}</p>
      <p
        style={{
          fontSize: large ? 'var(--text-kpi)' : 'var(--text-sub)',
          fontVariantNumeric: 'var(--font-numeric)',
        }}
        className="mt-1 font-semibold text-gray-900 tabular-nums"
      >
        {value ?? '—'}
      </p>
      {sublabel && <p className="mt-0.5 text-xs text-gray-500">{sublabel}</p>}
    </div>
  );
}

export interface SummaryCardsProps {
  cards: SummaryCardProps[];
  cols?: 3 | 4;
  className?: string;
}

export function SummaryCards({ cards, cols = 4, className = '' }: SummaryCardsProps) {
  return (
    <div className={`grid gap-4 ${cols === 4 ? 'grid-cols-2 lg:grid-cols-4' : 'grid-cols-1 sm:grid-cols-3'} ${className}`}>
      {cards.map((card, i) => (
        <SummaryCard key={i} {...card} />
      ))}
    </div>
  );
}

// ── DAT-2 — Data Table ────────────────────────────────────────────────────────

export type SortDir = 'asc' | 'desc' | null;

export interface Column<T> {
  key: string;
  header: string;
  /** 'left' | 'right' | 'center' — monetary = right, status = center, text = left */
  align?: 'left' | 'right' | 'center';
  sortable?: boolean;
  render: (row: T) => React.ReactNode;
  /** Approximate width class e.g. 'w-32', 'min-w-[120px]' */
  width?: string;
}

export interface DataTableProps<T> {
  columns: Column<T>[];
  rows: T[];
  getKey: (row: T) => string;
  loading?: boolean;
  /** Node to render when rows is empty */
  empty?: React.ReactNode;
  /** Override default onRowClick */
  onRowClick?: (row: T) => void;
  /** Callback for sort change */
  onSort?: (key: string, dir: SortDir) => void;
  sortKey?: string;
  sortDir?: SortDir;
  className?: string;
  /** Render an expandable detail row */
  renderExpanded?: (row: T) => React.ReactNode;
  /** Use table-fixed layout (required when expanded content must align with columns) */
  tableLayout?: 'fixed' | 'auto';
  /** Content rendered inside <tfoot> — use <tr> elements for column-aligned totals */
  footer?: React.ReactNode;
}

const ALIGN = { left: 'text-left', right: 'text-right', center: 'text-center' };

export function DataTable<T>({
  columns,
  rows,
  getKey,
  loading,
  empty,
  onRowClick,
  onSort,
  sortKey,
  sortDir,
  className = '',
  renderExpanded,
  tableLayout = 'auto',
  footer,
}: DataTableProps<T>) {
  const [expandedKey, setExpandedKey] = useState<string | null>(null);

  const handleRowClick = (row: T) => {
    const key = getKey(row);
    if (renderExpanded) setExpandedKey((prev) => (prev === key ? null : key));
    onRowClick?.(row);
  };

  const handleSort = (key: string) => {
    if (!onSort) return;
    const nextDir: SortDir = sortKey === key ? (sortDir === 'asc' ? 'desc' : sortDir === 'desc' ? null : 'asc') : 'asc';
    onSort(key, nextDir);
  };

  return (
    <div className={`overflow-x-auto ${className}`} style={{ borderRadius: 'var(--radius-card)', boxShadow: 'var(--shadow-card)' }}>
      <table className={`w-full border-collapse bg-white text-sm${tableLayout === 'fixed' ? ' table-fixed' : ''}`}>
        <thead>
          <tr className="border-b border-gray-200 bg-gray-50 sticky top-0 z-10">
            {renderExpanded && <th className="w-10 px-3" />}
            {columns.map((col) => (
              <th
                key={col.key}
                className={[
                  'px-4 py-3 font-semibold text-xs uppercase tracking-wider text-gray-500',
                  ALIGN[col.align ?? 'left'],
                  col.sortable && onSort ? 'cursor-pointer hover:text-gray-700 select-none' : '',
                  col.width ?? '',
                ].join(' ')}
                onClick={col.sortable && onSort ? () => handleSort(col.key) : undefined}
              >
                <span className="inline-flex items-center gap-1">
                  {col.header}
                  {col.sortable && onSort && (
                    <SortIcon active={sortKey === col.key} dir={sortKey === col.key ? sortDir : null} />
                  )}
                </span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {loading
            ? Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="animate-pulse border-b border-gray-100">
                  {renderExpanded && <td className="w-10 px-3 py-3"><div className="h-4 w-4 bg-gray-200 rounded" /></td>}
                  {columns.map((col) => (
                    <td key={col.key} className={`px-4 py-3 ${ALIGN[col.align ?? 'left']}`}>
                      <div className="h-4 bg-gray-200 rounded" style={{ width: col.align === 'right' ? '60%' : '80%', marginLeft: col.align === 'right' ? 'auto' : undefined }} />
                    </td>
                  ))}
                </tr>
              ))
            : rows.length === 0
            ? (
                <tr>
                  <td colSpan={columns.length + (renderExpanded ? 1 : 0)}>
                    {empty ?? <p className="py-12 text-center text-sm text-gray-400">No records found</p>}
                  </td>
                </tr>
              )
            : rows.map((row) => {
                const key = getKey(row);
                const expanded = expandedKey === key;
                return (
                  <React.Fragment key={key}>
                    <tr
                      className={[
                        'border-b border-gray-100 transition-colors',
                        onRowClick || renderExpanded ? 'cursor-pointer hover:bg-slate-50' : '',
                        expanded ? 'bg-slate-50' : '',
                      ].join(' ')}
                      onClick={() => handleRowClick(row)}
                    >
                      {renderExpanded && (
                        <td className="w-10 px-3 py-3 text-gray-400">
                          <svg
                            className={`w-4 h-4 transition-transform duration-150 ${expanded ? 'rotate-90' : ''}`}
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                            aria-hidden="true"
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </td>
                      )}
                      {columns.map((col) => (
                        <td key={col.key} className={`px-4 py-3 text-gray-800 ${ALIGN[col.align ?? 'left']}`}>
                          {col.render(row)}
                        </td>
                      ))}
                    </tr>
                    {renderExpanded && (
                      <tr>
                        <td colSpan={columns.length + 1} className="p-0">
                          <ExpandableRow open={expanded}>{renderExpanded(row)}</ExpandableRow>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
        </tbody>
        {footer && (
          <tfoot className="border-t-2 border-gray-200 bg-gray-50">
            {footer}
          </tfoot>
        )}
      </table>
    </div>
  );
}

function SortIcon({ active, dir }: { active: boolean; dir: SortDir }) {
  return (
    <svg className={`w-3 h-3 shrink-0 ${active ? 'text-gray-700' : 'text-gray-300'}`} fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      {dir === 'asc' ? (
        <path d="M7 14l5-5 5 5H7z" />
      ) : dir === 'desc' ? (
        <path d="M7 10l5 5 5-5H7z" />
      ) : (
        <path d="M7 10l5 5 5-5H7zm0-2l5-5 5 5H7z" />
      )}
    </svg>
  );
}

// ── DAT-3 — Expandable Row ────────────────────────────────────────────────────
// Uses grid-template-rows (not max-height) per DD-17 — no flicker on collapse

export interface ExpandableRowProps {
  open: boolean;
  children: React.ReactNode;
}

export function ExpandableRow({ open, children }: ExpandableRowProps) {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateRows: open ? '1fr' : '0fr',
        transition: `grid-template-rows var(--transition-expand)`,
      }}
    >
      <div className="overflow-hidden">
        <div className="bg-slate-50 border-t border-gray-100 px-6 py-4">
          {children}
        </div>
      </div>
    </div>
  );
}

// ── DAT-4 — Component Trace Row ───────────────────────────────────────────────

export interface TraceEntry {
  code: string;
  method: string;
  status: 'SUCCESS' | 'FAILED' | 'SKIPPED';
  amount: number | null;
  note?: string;
  warning?: string;
}

export interface ComponentTraceTableProps {
  entries: TraceEntry[];
  /** Show a "no trace — legacy run" notice when no trace exists */
  noTrace?: boolean;
}

export function ComponentTraceTable({ entries, noTrace }: ComponentTraceTableProps) {
  if (noTrace) {
    return (
      <p className="text-xs text-gray-400 italic py-2">
        No component trace available — this run used the legacy executor.
      </p>
    );
  }

  const hasNotes = entries.some((e) => e.note || e.warning);

  return (
    <table className="w-full text-xs">
      <thead>
        <tr className="text-gray-500 uppercase tracking-wide">
          <th className="text-left py-1.5 font-semibold w-44 pr-4">Code</th>
          <th className="text-left py-1.5 font-semibold">Method</th>
          <th className="text-center py-1.5 font-semibold w-16">Status</th>
          <th className="text-right py-1.5 font-semibold w-36" style={{ fontVariantNumeric: 'tabular-nums' }}>Amount</th>
          {hasNotes && <th className="text-left py-1.5 font-semibold pl-4">Note</th>}
        </tr>
      </thead>
      <tbody>
        {entries.map((e, i) => (
          <tr key={i} className={`border-t border-gray-100 ${e.status === 'FAILED' ? 'text-red-700' : 'text-gray-700'}`}>
            <td className="py-1.5 pr-4 font-mono font-medium whitespace-nowrap">{e.code}</td>
            <td className="py-1.5 text-gray-500">{e.method}</td>
            <td className="py-1.5 text-center">
              {e.status === 'SUCCESS' ? (
                <svg className="inline w-3.5 h-3.5 text-green-500" fill="none" stroke="currentColor" strokeWidth={2.5} viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                </svg>
              ) : e.status === 'FAILED' ? (
                <svg className="inline w-3.5 h-3.5 text-red-500" fill="none" stroke="currentColor" strokeWidth={2.5} viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <span className="text-gray-300">—</span>
              )}
            </td>
            <td className="py-1.5 text-right" style={{ fontVariantNumeric: 'tabular-nums' }}>
              {e.amount != null ? formatNaira(e.amount) : <span className="text-gray-300">—</span>}
            </td>
            {hasNotes && (
              <td className="py-1.5 pl-4 text-gray-500">
                {e.note}
                {e.warning && <span className="ml-1 text-amber-600">⚠ {e.warning}</span>}
              </td>
            )}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// ── DAT-5 — Reconciliation Card ───────────────────────────────────────────────

export interface ReconciliationCardProps {
  status: 'AWAITING' | 'MATCHED' | 'MISMATCH' | 'RESOLVED';
  expectedTotal: number;
  actualTotal?: number | null;
  variance?: number | null;
  resolvedBy?: string;
  resolvedAt?: string;
  resolutionNote?: string;
  className?: string;
}

const REC_STYLES: Record<ReconciliationCardProps['status'], { border: string; badge: string }> = {
  AWAITING:  { border: 'border-gray-200',  badge: 'bg-gray-100 text-gray-600' },
  MATCHED:   { border: 'border-green-300', badge: 'bg-green-100 text-green-800' },
  MISMATCH:  { border: 'border-red-300',   badge: 'bg-red-100 text-red-800' },
  RESOLVED:  { border: 'border-gray-300',  badge: 'bg-gray-100 text-gray-700' },
};

export function ReconciliationCard({ status, expectedTotal, actualTotal, variance, resolvedBy, resolvedAt, resolutionNote, className = '' }: ReconciliationCardProps) {
  const style = REC_STYLES[status];

  return (
    <div
      style={{ borderRadius: 'var(--radius-card)', boxShadow: 'var(--shadow-card)' }}
      className={`bg-white border-2 p-6 ${style.border} ${className}`}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-700">Reconciliation</h3>
        <span style={{ borderRadius: 'var(--radius-badge)' }} className={`px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide ${style.badge}`}>
          {status}
        </span>
      </div>

      <div className="flex gap-6">
        <div>
          <p className="text-xs text-gray-500 mb-0.5">Expected</p>
          <p className="text-lg font-semibold text-gray-900" style={{ fontVariantNumeric: 'tabular-nums' }}>
            {formatNaira(expectedTotal)}
          </p>
        </div>
        {actualTotal != null && (
          <div>
            <p className="text-xs text-gray-500 mb-0.5">Actual</p>
            <p className="text-lg font-semibold text-gray-900" style={{ fontVariantNumeric: 'tabular-nums' }}>
              {formatNaira(actualTotal)}
            </p>
          </div>
        )}
        {variance != null && variance !== 0 && (
          <div>
            <p className="text-xs text-gray-500 mb-0.5">Variance</p>
            <p className={`text-lg font-semibold ${variance > 0 ? 'text-red-600' : 'text-green-600'}`} style={{ fontVariantNumeric: 'tabular-nums' }}>
              {variance > 0 ? '+' : ''}{formatNaira(variance)}
            </p>
          </div>
        )}
      </div>

      {status === 'RESOLVED' && (resolvedBy || resolutionNote) && (
        <div className="mt-4 pt-4 border-t border-gray-100 text-xs text-gray-500 space-y-0.5">
          {resolvedBy && <p>Resolved by <span className="font-medium text-gray-700">{resolvedBy}</span>{resolvedAt ? ` · ${resolvedAt}` : ''}</p>}
          {resolutionNote && <p className="italic">"{resolutionNote}"</p>}
        </div>
      )}
    </div>
  );
}

// ── DAT-6 — Timeline / Audit Log Row ─────────────────────────────────────────

export interface TimelineEntry {
  timestamp: string;
  action: string;
  actor?: string;
  details?: string;
}

export interface TimelineTableProps {
  entries: TimelineEntry[];
  className?: string;
}

export function TimelineTable({ entries, className = '' }: TimelineTableProps) {
  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="border-b border-gray-200 bg-gray-50">
            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500 w-44">Timestamp</th>
            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Event</th>
            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500 w-40">Actor</th>
            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Details</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((e, i) => (
            <tr key={i} className="border-b border-gray-100 hover:bg-slate-50">
              <td className="px-4 py-3 font-mono text-xs text-gray-500 whitespace-nowrap">{e.timestamp}</td>
              <td className="px-4 py-3 text-gray-800 font-medium">{e.action}</td>
              <td className="px-4 py-3 text-gray-600">{e.actor ?? '—'}</td>
              <td className="px-4 py-3 text-gray-500 text-xs">{e.details ?? '—'}</td>
            </tr>
          ))}
          {entries.length === 0 && (
            <tr>
              <td colSpan={4} className="py-10 text-center text-sm text-gray-400">No events recorded</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
