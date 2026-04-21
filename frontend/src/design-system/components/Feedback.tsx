/**
 * Feedback — FBK-1 through FBK-4
 *
 * useToast + Toast   FBK-1 — bottom-right toast stack, 4s auto-dismiss (errors persist)
 * InlineError        FBK-2 — field-level validation error (appears on blur)
 * ConfirmDialog      FBK-3 — irreversible action confirmation modal
 * EmptyState         FBK-4 — list empty state with icon + CTA
 *
 * Design rules:
 * - DD-4: Mark as Paid dialog is intentionally friction-heavy (red btn + consequences)
 * - DD-5: Empty states always have an action — never just "No data"
 * - ux-designer: error recovery — what went wrong + why + what to do
 * - ui-designer: modals use 24px padding, focus-trap, Escape key closes
 */

import React, { createContext, useCallback, useContext, useEffect, useId, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { Btn } from './Actions';

// ── FBK-1 — Toast ─────────────────────────────────────────────────────────────

export type ToastVariant = 'success' | 'error' | 'warning' | 'info';

export interface ToastItem {
  id: string;
  variant: ToastVariant;
  message: string;
}

interface ToastContextValue {
  show: (variant: ToastVariant, message: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

const TOAST_COLORS: Record<ToastVariant, { bg: string; icon: string; bar: string; iconPath: string }> = {
  success: { bg: 'bg-white border-green-500',  icon: 'text-green-600', bar: 'bg-green-500', iconPath: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
  error:   { bg: 'bg-white border-red-500',    icon: 'text-red-600',   bar: 'bg-red-500',   iconPath: 'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z' },
  warning: { bg: 'bg-white border-amber-500',  icon: 'text-amber-600', bar: 'bg-amber-500', iconPath: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' },
  info:    { bg: 'bg-white border-blue-500',   icon: 'text-blue-600',  bar: 'bg-blue-500',  iconPath: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
};

const AUTO_DISMISS_MS = 4000;

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  let nextId = 0;

  const show = useCallback((variant: ToastVariant, message: string) => {
    const id = `toast-${++nextId}`;
    setToasts((prev) => [...prev, { id, variant, message }]);
    if (variant !== 'error') {
      setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), AUTO_DISMISS_MS);
    }
  }, []);

  const dismiss = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ show }}>
      {children}
      {createPortal(
        <div
          aria-live="polite"
          aria-atomic="false"
          className="fixed bottom-5 right-5 z-[9999] flex flex-col gap-2 items-end"
        >
          {toasts.map((t) => {
            const cfg = TOAST_COLORS[t.variant];
            return (
              <div
                key={t.id}
                role="status"
                style={{ borderRadius: 'var(--radius-card)', boxShadow: 'var(--shadow-dropdown)', animation: 'slideInRight 150ms ease-out' }}
                className={`relative flex items-start gap-3 min-w-[280px] max-w-sm pl-3 pr-10 py-3 border-l-4 border border-gray-200 ${cfg.bg} overflow-hidden`}
              >
                <svg className={`w-5 h-5 shrink-0 mt-0.5 ${cfg.icon}`} fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={cfg.iconPath} />
                </svg>
                <p className="text-sm text-gray-800 font-medium">{t.message}</p>
                <button
                  onClick={() => dismiss(t.id)}
                  aria-label="Dismiss notification"
                  className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            );
          })}
        </div>,
        document.body,
      )}
    </ToastContext.Provider>
  );
}

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used inside <ToastProvider>');
  return ctx;
}

// ── FBK-2 — Inline Field Error ───────────────────────────────────────────────

export interface InlineErrorProps {
  id?: string;
  message: string;
  className?: string;
}

export function InlineError({ id, message, className = '' }: InlineErrorProps) {
  return (
    <p
      id={id}
      role="alert"
      className={`flex items-center gap-1 mt-1 text-xs text-red-600 ${className}`}
    >
      <svg className="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
      </svg>
      {message}
    </p>
  );
}

// ── FBK-3 — Confirmation Dialog ───────────────────────────────────────────────

export interface ConfirmDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  /** What is happening — e.g. "Mark run as PAID" */
  title: string;
  /** Specific consequences — not generic. DD-4: irreversible actions need context. */
  body: React.ReactNode;
  /** Label on the confirm button — must name the action, never just "OK" */
  confirmLabel: string;
  /** Label on cancel button — default "Cancel" */
  cancelLabel?: string;
  /** Red destructive button vs. blue primary */
  destructive?: boolean;
  loading?: boolean;
}

export function ConfirmDialog({
  open,
  onClose,
  onConfirm,
  title,
  body,
  confirmLabel,
  cancelLabel = 'Cancel',
  destructive = false,
  loading = false,
}: ConfirmDialogProps) {
  const dialogRef = useRef<HTMLDivElement>(null);

  /* Escape key */
  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [open, onClose]);

  /* Focus trap */
  useEffect(() => {
    if (open) {
      const firstFocusable = dialogRef.current?.querySelector<HTMLElement>('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
      firstFocusable?.focus();
    }
  }, [open]);

  if (!open) return null;

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-title"
    >
      {/* Overlay */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Panel */}
      <div
        ref={dialogRef}
        style={{
          borderRadius: 'var(--radius-card)',
          boxShadow: 'var(--shadow-modal)',
          width: 'var(--modal-width-form)',
          maxWidth: 'calc(100vw - 32px)',
        }}
        className="relative bg-white p-6 z-10"
      >
        {/* Icon + title */}
        {destructive && (
          <div className="flex items-center justify-center w-12 h-12 rounded-full bg-red-100 mx-auto mb-4">
            <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
        )}
        <h2 id="confirm-title" className="text-lg font-semibold text-gray-900 text-center">
          {title}
        </h2>
        <div className="mt-3 text-sm text-gray-600 text-center space-y-1">
          {body}
        </div>

        {/* Actions */}
        <div className="mt-6 flex flex-col-reverse sm:flex-row gap-3 justify-end">
          <Btn variant="secondary" onClick={onClose} disabled={loading}>
            {cancelLabel}
          </Btn>
          <Btn
            variant={destructive ? 'destructive' : 'primary'}
            onClick={onConfirm}
            loading={loading}
          >
            {confirmLabel}
          </Btn>
        </div>
      </div>
    </div>,
    document.body,
  );
}

// ── FBK-4 — Empty State ───────────────────────────────────────────────────────

export interface EmptyStateProps {
  icon?: React.ReactNode;
  headline: string;
  body: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

export function EmptyState({ icon, headline, body, action, className = '' }: EmptyStateProps) {
  return (
    <div className={`flex flex-col items-center justify-center py-16 px-6 text-center ${className}`}>
      {icon && (
        <div className="w-12 h-12 text-gray-300 mb-4" aria-hidden="true">
          {icon}
        </div>
      )}
      <p className="text-base font-semibold text-gray-700">{headline}</p>
      <p className="mt-1 text-sm text-gray-500 max-w-sm">{body}</p>
      {action && (
        <Btn variant="primary" size="md" className="mt-6" onClick={action.onClick}>
          {action.label}
        </Btn>
      )}
    </div>
  );
}
