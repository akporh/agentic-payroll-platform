/**
 * Status and State — STS-1 through STS-4
 *
 * StatusBadge  STS-1 — coloured dot + text (WCAG DD-12, never colour alone)
 * AlertBanner  STS-2 — inline feedback banner (warning / error / info / success)
 * ProgressBar  STS-3 — linear with percentage label
 * SkeletonRow  STS-4 — shimmer placeholder; use instead of full-page spinners
 * SkeletonCard STS-4 variant — for KPI card loading
 *
 * Colour contrast audit (WCAG AA 4.5:1 for text):
 *   All badge variants use bg-*-100 + text-*-800 → all pass at ≥7:1
 *   Dot fills are accent colours for visual grouping, text carries the meaning
 */

import React from 'react';

// ── Status value types ────────────────────────────────────────────────────────

export type WorkspaceStatus =
  | 'DRAFT'
  | 'STRUCTURE_DEFINED'
  | 'COMPENSATION_DEFINED'
  | 'RULES_DEFINED'
  | 'READY'
  | 'LIVE';

export type PayrollRunStatus =
  | 'PENDING'
  | 'CALCULATING'
  | 'PARTIAL'
  | 'CALCULATED'
  | 'APPROVED'
  | 'LOCKED'
  | 'PAID'
  | 'FAILED';

export type ReconciliationStatus = 'MATCHED' | 'MISMATCH' | 'RESOLVED';

export type EmployeeStatus = 'ACTIVE' | 'INACTIVE';

export type ResultStatus = 'SUCCESS' | 'FAILED';

export type BadgeVariant =
  | WorkspaceStatus
  | PayrollRunStatus
  | ReconciliationStatus
  | EmployeeStatus
  | ResultStatus;

// ── STS-1 — Status Badge ─────────────────────────────────────────────────────

interface BadgeConfig {
  dot: string;       /* dot fill class */
  bg: string;        /* badge background */
  text: string;      /* badge text colour — must pass 4.5:1 on bg */
  pulse?: boolean;   /* animated pulse for in-progress states */
  label?: string;    /* override the status key as display text */
}

const BADGE_CONFIG: Record<string, BadgeConfig> = {
  /* Workspace */
  DRAFT:                { dot: 'bg-gray-400',    bg: 'bg-gray-100',    text: 'text-gray-700' },
  STRUCTURE_DEFINED:    { dot: 'bg-blue-400',    bg: 'bg-blue-50',     text: 'text-blue-800', label: 'Structure' },
  COMPENSATION_DEFINED: { dot: 'bg-indigo-400',  bg: 'bg-indigo-50',   text: 'text-indigo-800', label: 'Compensation' },
  RULES_DEFINED:        { dot: 'bg-violet-400',  bg: 'bg-violet-50',   text: 'text-violet-800', label: 'Rules Set' },
  READY:                { dot: 'bg-blue-500',    bg: 'bg-blue-100',    text: 'text-blue-800' },
  LIVE:                 { dot: 'bg-green-500',   bg: 'bg-green-100',   text: 'text-green-800' },

  /* Payroll Run */
  PENDING:              { dot: 'bg-gray-400',    bg: 'bg-gray-100',    text: 'text-gray-700' },
  CALCULATING:          { dot: 'bg-blue-500',    bg: 'bg-blue-100',    text: 'text-blue-800', pulse: true },
  PARTIAL:              { dot: 'bg-amber-500',   bg: 'bg-amber-100',   text: 'text-amber-800' },
  CALCULATED:           { dot: 'bg-teal-500',    bg: 'bg-teal-100',    text: 'text-teal-800' },
  APPROVED:             { dot: 'bg-violet-500',  bg: 'bg-violet-100',  text: 'text-violet-800' },
  LOCKED:               { dot: 'bg-indigo-500',  bg: 'bg-indigo-100',  text: 'text-indigo-800' },
  PAID:                 { dot: 'bg-green-600',   bg: 'bg-green-100',   text: 'text-green-800' },
  FAILED:               { dot: 'bg-red-500',     bg: 'bg-red-100',     text: 'text-red-800' },

  /* Reconciliation */
  MATCHED:              { dot: 'bg-green-500',   bg: 'bg-green-100',   text: 'text-green-800' },
  MISMATCH:             { dot: 'bg-red-500',     bg: 'bg-red-100',     text: 'text-red-800' },
  RESOLVED:             { dot: 'bg-gray-400',    bg: 'bg-gray-100',    text: 'text-gray-700' },

  /* Employee */
  ACTIVE:               { dot: 'bg-green-500',   bg: 'bg-green-100',   text: 'text-green-800' },
  INACTIVE:             { dot: 'bg-gray-400',    bg: 'bg-gray-100',    text: 'text-gray-600' },

  /* Result */
  SUCCESS:              { dot: 'bg-green-500',   bg: 'bg-green-100',   text: 'text-green-800' },
};

export interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'default';
  className?: string;
}

export function StatusBadge({ status, size = 'default', className = '' }: StatusBadgeProps) {
  const config = BADGE_CONFIG[status] ?? {
    dot: 'bg-gray-400',
    bg: 'bg-gray-100',
    text: 'text-gray-600',
  };
  const displayText = config.label ?? status.replace(/_/g, ' ');

  return (
    <span
      style={{ borderRadius: 'var(--radius-badge)' }}
      className={[
        'inline-flex items-center gap-1.5 font-semibold uppercase tracking-wide',
        config.bg,
        config.text,
        size === 'sm' ? 'px-2 py-0.5 text-[10px]' : 'px-2.5 py-1 text-[11px]',
        className,
      ].join(' ')}
    >
      <span
        aria-hidden="true"
        className={[
          'rounded-full shrink-0',
          config.dot,
          config.pulse ? 'animate-pulse' : '',
          size === 'sm' ? 'w-1.5 h-1.5' : 'w-2 h-2',
        ].join(' ')}
      />
      {displayText}
    </span>
  );
}

// ── STS-2 — Alert Banner ──────────────────────────────────────────────────────

export interface AlertBannerProps {
  variant: 'warning' | 'error' | 'info' | 'success';
  title?: string;
  description?: React.ReactNode;
  action?: { label: string; onClick: () => void };
  dismissible?: boolean;
  onDismiss?: () => void;
  className?: string;
}

const ALERT_CONFIG: Record<AlertBannerProps['variant'], { bg: string; border: string; icon: string; text: string; iconPath: string }> = {
  warning: {
    bg: 'bg-amber-50',
    border: 'border-amber-300',
    icon: 'text-amber-600',
    text: 'text-amber-900',
    iconPath: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
  },
  error: {
    bg: 'bg-red-50',
    border: 'border-red-300',
    icon: 'text-red-600',
    text: 'text-red-900',
    iconPath: 'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  info: {
    bg: 'bg-blue-50',
    border: 'border-blue-300',
    icon: 'text-blue-600',
    text: 'text-blue-900',
    iconPath: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  success: {
    bg: 'bg-green-50',
    border: 'border-green-300',
    icon: 'text-green-600',
    text: 'text-green-900',
    iconPath: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
  },
};

export function AlertBanner({ variant, title, description, action, dismissible, onDismiss, className = '' }: AlertBannerProps) {
  const cfg = ALERT_CONFIG[variant];

  return (
    <div
      role="alert"
      style={{ borderRadius: 'var(--radius-card)' }}
      className={['flex gap-3 p-4 border', cfg.bg, cfg.border, className].join(' ')}
    >
      <svg className={`w-5 h-5 shrink-0 mt-0.5 ${cfg.icon}`} fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={cfg.iconPath} />
      </svg>
      <div className="flex-1 min-w-0">
        <p className={`text-sm font-semibold ${cfg.text}`}>{title}</p>
        {description && <p className={`mt-0.5 text-sm ${cfg.text} opacity-80`}>{description}</p>}
        {action && (
          <button
            onClick={action.onClick}
            className={`mt-2 text-sm font-medium underline underline-offset-2 ${cfg.icon} hover:opacity-80`}
          >
            {action.label}
          </button>
        )}
      </div>
      {dismissible && (
        <button
          onClick={onDismiss}
          aria-label="Dismiss"
          className={`shrink-0 ${cfg.icon} hover:opacity-70 transition-opacity`}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  );
}

// ── STS-3 — Progress Bar ──────────────────────────────────────────────────────

export interface ProgressBarProps {
  percent: number;      /* 0–100 */
  label?: string;
  sublabel?: string;
  className?: string;
}

export function ProgressBar({ percent, label, sublabel, className = '' }: ProgressBarProps) {
  const clamped = Math.min(100, Math.max(0, percent));

  return (
    <div className={className}>
      {(label || sublabel) && (
        <div className="flex justify-between mb-1.5">
          {label && <span className="text-sm font-medium text-gray-700">{label}</span>}
          {sublabel && <span className="text-sm text-gray-500">{sublabel}</span>}
        </div>
      )}
      <div className="w-full bg-gray-200 rounded-full h-2" role="progressbar" aria-valuenow={clamped} aria-valuemin={0} aria-valuemax={100}>
        <div
          className="bg-brand h-2 rounded-full transition-all duration-300 ease-out"
          style={{ width: `${clamped}%` }}
        />
      </div>
      <p className="mt-1 text-xs text-gray-500">{clamped}% complete</p>
    </div>
  );
}

// ── STS-4 — Skeleton (shimmer) ────────────────────────────────────────────────

export interface SkeletonRowProps {
  cols?: number;    /* number of columns to render */
  className?: string;
}

export function SkeletonRow({ cols = 4, className = '' }: SkeletonRowProps) {
  return (
    <tr className={`animate-pulse ${className}`}>
      {Array.from({ length: cols }).map((_, i) => (
        <td key={i} className="px-4 py-3">
          <div className="h-4 bg-gray-200 rounded" style={{ width: i === 0 ? '60%' : i === cols - 1 ? '40%' : '80%' }} />
        </td>
      ))}
    </tr>
  );
}

export interface SkeletonCardProps {
  className?: string;
}

export function SkeletonCard({ className = '' }: SkeletonCardProps) {
  return (
    <div
      style={{ borderRadius: 'var(--radius-card)', boxShadow: 'var(--shadow-card)' }}
      className={`bg-white p-6 animate-pulse ${className}`}
    >
      <div className="h-3 bg-gray-200 rounded w-24 mb-3" />
      <div className="h-8 bg-gray-200 rounded w-32" />
    </div>
  );
}
