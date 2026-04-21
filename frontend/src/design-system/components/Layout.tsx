/**
 * Layout — LAY-1 through LAY-5
 *
 * PageShell      LAY-1 — top bar + sidebar + main content area
 * ContentHeader  LAY-2 — page title + subtitle + primary action slot
 * SlideOver      LAY-3 — right-side drawer (400–480px), overlays content
 * Modal          LAY-4 — centred modal with focus-trap
 * SplitPanel     LAY-5 — horizontal split (JSON onboarding editor | response)
 *
 * Design rules:
 * - DD-1: PageShell implements the two-tier nav pattern
 * - DD-15: Desktop-primary. Sidebar collapses on tablet, content-area expands
 * - Modals: 24px padding, overlay rgba(0,0,0,0.4), Escape key closes, focus-trap
 * - SlideOver: slides in from right, 460px wide, Escape closes
 * - ui-designer: max-width form=480px content=640px
 */

import React, { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { Outlet } from 'react-router-dom';
import { TopBar, WorkspaceSidebar } from './Navigation';
import type { WorkspaceOption } from './Navigation';

// ── LAY-1 — Page Shell ────────────────────────────────────────────────────────

export interface PageShellProps {
  workspaceId?: string;
  workspaceName?: string;
  workspaceStatus?: string;
  isLive?: boolean;
  bureauName?: string;
  userName?: string;
  currentWorkspace?: WorkspaceOption | null;
  recentWorkspaces?: WorkspaceOption[];
  onWorkspaceSelect?: (id: string) => void;
  onBureauClick?: () => void;
  sidebarCollapsed?: boolean;
  onToggleSidebar?: () => void;
}

export function PageShell({
  workspaceId,
  workspaceName,
  workspaceStatus,
  isLive,
  bureauName,
  userName,
  currentWorkspace,
  recentWorkspaces,
  onWorkspaceSelect,
  onBureauClick,
  sidebarCollapsed = false,
  onToggleSidebar,
}: PageShellProps) {
  const sidebarWidth = workspaceId
    ? sidebarCollapsed ? 'var(--sidebar-collapsed)' : 'var(--sidebar-expanded)'
    : '0px';

  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      <TopBar
        bureauName={bureauName}
        currentWorkspace={currentWorkspace}
        recentWorkspaces={recentWorkspaces}
        userName={userName}
        onWorkspaceSelect={onWorkspaceSelect}
        onBureauClick={onBureauClick}
      />

      {workspaceId && (
        <WorkspaceSidebar
          workspaceId={workspaceId}
          workspaceName={workspaceName ?? '…'}
          workspaceStatus={workspaceStatus ?? 'DRAFT'}
          isLive={isLive}
          collapsed={sidebarCollapsed}
          onToggleCollapse={onToggleSidebar}
        />
      )}

      <main
        style={{
          paddingTop: 'calc(var(--topbar-height) + 1.5rem)',
          marginLeft: workspaceId ? sidebarWidth : undefined,
          transition: 'margin-left var(--transition-panel)',
        }}
        className="min-h-screen px-6 pb-6"
      >
        <Outlet />
      </main>
    </div>
  );
}

// ── LAY-2 — Content Header ────────────────────────────────────────────────────

export interface ContentHeaderProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  back?: React.ReactNode;
  className?: string;
}

export function ContentHeader({ title, subtitle, action, back, className = '' }: ContentHeaderProps) {
  return (
    <div className={`flex items-start justify-between gap-4 mb-6 ${className}`}>
      <div>
        {back && <div className="mb-2">{back}</div>}
        <h1 style={{ fontSize: 'var(--text-page)' }} className="font-semibold text-gray-900 leading-tight">
          {title}
        </h1>
        {subtitle && (
          <p className="mt-1 text-sm text-gray-500">{subtitle}</p>
        )}
      </div>
      {action && <div className="shrink-0 flex items-center gap-2">{action}</div>}
    </div>
  );
}

// ── LAY-3 — Slide-Over (Drawer) ───────────────────────────────────────────────

export interface SlideOverProps {
  open: boolean;
  onClose: () => void;
  title: string;
  /** Optional subtitle / description */
  description?: string;
  children: React.ReactNode;
  /** Footer content — typically action buttons */
  footer?: React.ReactNode;
}

export function SlideOver({ open, onClose, title, description, children, footer }: SlideOverProps) {
  const panelRef = useRef<HTMLDivElement>(null);

  /* Escape key */
  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [open, onClose]);

  /* Focus first element when opens */
  useEffect(() => {
    if (open) {
      const firstFocusable = panelRef.current?.querySelector<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
      );
      firstFocusable?.focus();
    }
  }, [open]);

  return createPortal(
    <div
      aria-modal="true"
      role="dialog"
      aria-labelledby="slide-over-title"
      style={{ pointerEvents: open ? 'auto' : 'none' }}
      className="fixed inset-0 z-40 flex justify-end"
    >
      {/* Overlay */}
      <div
        aria-hidden="true"
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        style={{ opacity: open ? 1 : 0, transition: 'opacity var(--transition-panel)' }}
        onClick={onClose}
      />

      {/* Panel */}
      <div
        ref={panelRef}
        style={{
          width: 'var(--drawer-width)',
          maxWidth: 'calc(100vw - 32px)',
          transform: open ? 'translateX(0)' : 'translateX(100%)',
          transition: 'transform var(--transition-panel)',
        }}
        className="relative flex flex-col h-full bg-white shadow-xl"
      >
        {/* Header */}
        <div className="flex items-start justify-between px-6 py-5 border-b border-gray-200">
          <div>
            <h2 id="slide-over-title" className="text-base font-semibold text-gray-900">{title}</h2>
            {description && <p className="mt-0.5 text-sm text-gray-500">{description}</p>}
          </div>
          <button
            onClick={onClose}
            aria-label="Close panel"
            className="ml-4 shrink-0 text-gray-400 hover:text-gray-600 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand"
            style={{ borderRadius: 'var(--radius-btn)' }}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto px-6 py-5">
          {children}
        </div>

        {/* Footer */}
        {footer && (
          <div className="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
            {footer}
          </div>
        )}
      </div>
    </div>,
    document.body,
  );
}

// ── LAY-4 — Modal (Centred) ───────────────────────────────────────────────────

export interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  /** 'form' = 480px, 'content' = 640px */
  size?: 'form' | 'content';
  children: React.ReactNode;
  footer?: React.ReactNode;
}

export function Modal({ open, onClose, title, size = 'form', children, footer }: ModalProps) {
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [open, onClose]);

  useEffect(() => {
    if (open) {
      const firstFocusable = dialogRef.current?.querySelector<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
      );
      firstFocusable?.focus();
    }
  }, [open]);

  if (!open) return null;

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? 'modal-title' : undefined}
    >
      {/* Overlay */}
      <div
        aria-hidden="true"
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Dialog */}
      <div
        ref={dialogRef}
        style={{
          borderRadius: 'var(--radius-card)',
          boxShadow: 'var(--shadow-modal)',
          width: size === 'form' ? 'var(--modal-width-form)' : 'var(--modal-width-content)',
          maxWidth: 'calc(100vw - 32px)',
          maxHeight: 'calc(100vh - 64px)',
        }}
        className="relative bg-white flex flex-col"
      >
        {/* Header */}
        {title && (
          <div className="flex items-center justify-between px-6 pt-5 pb-4 border-b border-gray-100">
            <h2 id="modal-title" className="text-base font-semibold text-gray-900">{title}</h2>
            <button
              onClick={onClose}
              aria-label="Close"
              className="text-gray-400 hover:text-gray-600 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand"
              style={{ borderRadius: 'var(--radius-btn)' }}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}

        {/* Body */}
        <div className="flex-1 overflow-y-auto px-6 py-5">
          {children}
        </div>

        {/* Footer */}
        {footer && (
          <div className="px-6 py-4 border-t border-gray-100 flex justify-end gap-3">
            {footer}
          </div>
        )}
      </div>
    </div>,
    document.body,
  );
}

// ── LAY-5 — Split Panel ───────────────────────────────────────────────────────

export interface SplitPanelProps {
  /** Left pane (editor) */
  left: React.ReactNode;
  /** Right pane (response / preview) */
  right: React.ReactNode;
  /** 'half' = 50/50, 'left-heavy' = 60/40 */
  ratio?: 'half' | 'left-heavy';
  className?: string;
}

export function SplitPanel({ left, right, ratio = 'half', className = '' }: SplitPanelProps) {
  const leftClass = ratio === 'left-heavy' ? 'flex-[3]' : 'flex-1';
  const rightClass = ratio === 'left-heavy' ? 'flex-[2]' : 'flex-1';

  return (
    <div className={`flex gap-4 min-h-0 ${className}`}>
      <div className={`${leftClass} min-w-0 overflow-auto`}>
        {left}
      </div>
      <div className="w-px bg-gray-200 shrink-0" aria-hidden="true" />
      <div className={`${rightClass} min-w-0 overflow-auto`}>
        {right}
      </div>
    </div>
  );
}

// ── Card — utility wrapper (used by multiple pages) ───────────────────────────

export interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'sm' | 'md' | 'lg';
  /** Optional card title — rendered as a small label above children */
  title?: string;
  action?: React.ReactNode;
}

export function Card({ children, className = '', padding = 'md', title, action }: CardProps) {
  const pad = { sm: 'p-4', md: 'p-6', lg: 'p-8' }[padding];
  return (
    <div
      style={{ borderRadius: 'var(--radius-card)', boxShadow: 'var(--shadow-card)' }}
      className={`bg-white ${pad} ${className}`}
    >
      {(title || action) && (
        <div className="flex items-center justify-between mb-3">
          {title && <p className="text-sm font-semibold text-gray-700">{title}</p>}
          {action && <div>{action}</div>}
        </div>
      )}
      {children}
    </div>
  );
}
