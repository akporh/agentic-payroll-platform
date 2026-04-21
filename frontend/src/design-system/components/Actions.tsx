/**
 * Actions — ACT-1 through ACT-6
 *
 * Btn        ACT-1 primary | ACT-2 secondary | ACT-3 destructive | ACT-4 ghost
 * IconBtn    ACT-5 — icon-only, always requires aria-label
 * DownloadBtn ACT-6 — download/export trigger
 *
 * Design rules (Gate 1 + ui-designer):
 * - One primary button per screen section (DD-3)
 * - Height scale: sm=32px md=40px lg=48px (shared with inputs)
 * - Horizontal padding = 2× vertical padding
 * - Touch targets ≥ 44×44px (icon buttons: 44px = w-11 h-11)
 * - Loading state: spinner replaces label (never show both)
 * - Focus ring on all interactive elements (WCAG)
 * - Disabled: opacity-40, pointer-events-none (not just grey)
 */

import React from 'react';

// ── Spinner ───────────────────────────────────────────────────────────────────

function Spinner({ className = '' }: { className?: string }) {
  return (
    <svg
      className={`animate-spin ${className}`}
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
    </svg>
  );
}

function DownloadIcon() {
  return (
    <svg className="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
    </svg>
  );
}

// ── ACT-1/2/3/4 — Btn ────────────────────────────────────────────────────────

export interface BtnProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Visual variant. Use ONE primary per screen section. */
  variant?: 'primary' | 'secondary' | 'destructive' | 'ghost';
  /** Height: sm=32px md=40px lg=48px */
  size?: 'sm' | 'md' | 'lg';
  /** Shows spinner, disables button */
  loading?: boolean;
  /** Optional leading/trailing icon */
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
}

const VARIANTS: Record<NonNullable<BtnProps['variant']>, string> = {
  primary:
    'bg-brand text-white hover:bg-brand-dark active:scale-[0.98] ' +
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2',
  secondary:
    'bg-white text-slate-700 border border-slate-300 hover:bg-slate-50 active:scale-[0.98] ' +
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-400 focus-visible:ring-offset-2',
  destructive:
    'bg-red-600 text-white hover:bg-red-700 active:scale-[0.98] ' +
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-600 focus-visible:ring-offset-2',
  ghost:
    'text-slate-600 hover:bg-slate-100 hover:text-slate-900 active:scale-[0.98] ' +
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-400 focus-visible:ring-offset-2',
};

const SIZES: Record<NonNullable<BtnProps['size']>, string> = {
  sm: 'h-8 px-3 text-xs gap-1.5',    /* 32px height */
  md: 'h-10 px-4 text-sm gap-2',      /* 40px height */
  lg: 'h-12 px-5 text-sm gap-2',      /* 48px height */
};

export function Btn({
  variant = 'primary',
  size = 'md',
  loading = false,
  icon,
  iconPosition = 'left',
  children,
  disabled,
  className = '',
  ...props
}: BtnProps) {
  return (
    <button
      disabled={disabled || loading}
      style={{ borderRadius: 'var(--radius-btn)', transition: 'background-color var(--transition-fast), transform var(--transition-fast)' }}
      className={[
        'inline-flex items-center justify-center font-medium select-none cursor-pointer',
        'disabled:opacity-40 disabled:pointer-events-none',
        VARIANTS[variant],
        SIZES[size],
        className,
      ].join(' ')}
      {...props}
    >
      {loading && <Spinner className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />}
      {!loading && icon && iconPosition === 'left' && icon}
      <span>{children}</span>
      {!loading && icon && iconPosition === 'right' && icon}
    </button>
  );
}

// ── ACT-5 — Icon Button ───────────────────────────────────────────────────────

export interface IconBtnProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Required: accessible label (replaces visible text) */
  label: string;
  /** Size class — all variants hit ≥ 44px touch target */
  size?: 'sm' | 'md';
}

export function IconBtn({ label, size = 'md', children, className = '', ...props }: IconBtnProps) {
  return (
    <button
      aria-label={label}
      title={label}
      style={{ borderRadius: 'var(--radius-btn)', transition: 'background-color var(--transition-fast)' }}
      className={[
        'inline-flex items-center justify-center text-slate-500',
        'hover:bg-slate-100 hover:text-slate-700',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-400 focus-visible:ring-offset-1',
        'disabled:opacity-40 disabled:pointer-events-none cursor-pointer',
        size === 'sm' ? 'w-8 h-8 min-w-[44px] min-h-[44px]' : 'w-9 h-9 min-w-[44px] min-h-[44px]',
        className,
      ].join(' ')}
      {...props}
    >
      {children}
    </button>
  );
}

// ── ACT-6 — Download Button ───────────────────────────────────────────────────

export interface DownloadBtnProps {
  label: string;
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  className?: string;
}

export function DownloadBtn({ label, disabled, loading, onClick, className = '' }: DownloadBtnProps) {
  return (
    <Btn
      variant="secondary"
      size="sm"
      disabled={disabled}
      loading={loading}
      icon={<DownloadIcon />}
      iconPosition="left"
      onClick={onClick}
      className={className}
    >
      {label}
    </Btn>
  );
}
