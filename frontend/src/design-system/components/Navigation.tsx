/**
 * Navigation — NAV-1 through NAV-5
 *
 * TopBar           NAV-1 — global top bar: logo | workspace picker | user menu
 * WorkspaceSidebar NAV-2 — workspace nav: expanded 240px | collapsed 64px | mobile drawer
 * Breadcrumb       NAV-3 — Bureau / Workspace / Section / [Detail]
 * TabBar           NAV-4 — run detail tabs (Results | Reconciliation | Timeline | Audit Log)
 * OnboardingStepper NAV-5 — workspace setup stepper
 *
 * Design rules:
 * - DD-1: Two-tier navigation — top bar (bureau) + sidebar (workspace)
 * - DD-15: Desktop-primary. Sidebar collapses to 64px on tablet, drawer on mobile
 * - Top bar height: 56px (--topbar-height)
 * - Sidebar expanded: 240px | collapsed: 64px
 * - Active state: must be immediately obvious (background + font-weight)
 * - Icons: 20×20px, consistent stroke-width 1.75
 * - NAV-4: tabs are text-only (no icon overload)
 * - NAV-5: numbered steps, completed/current/upcoming states
 */

import React, { useState } from 'react';
import { NavLink, Link } from 'react-router-dom';

// ── Icon primitives ───────────────────────────────────────────────────────────

function Icon({ d, className = '' }: { d: string; className?: string }) {
  return (
    <svg
      className={`shrink-0 ${className}`}
      width="20"
      height="20"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
      strokeWidth={1.75}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d={d} />
    </svg>
  );
}

const ICONS = {
  home:     'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
  newClient:'M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
  payroll:  'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  inputs:   'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4',
  employees:'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z',
  config:   'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z',
  calendar: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
  tag:      'M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z',
  setup:    'M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z',
  upload:   'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12',
  chevronDown: 'M19 9l-7 7-7-7',
  user:     'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
  check:    'M5 13l4 4L19 7',
  menu:     'M4 6h16M4 12h16M4 18h16',
  x:        'M6 18L18 6M6 6l12 12',
};

// ── NAV-1 — Global Top Bar ────────────────────────────────────────────────────

export interface WorkspaceOption {
  id: string;
  name: string;
  status: string;
}

export interface TopBarProps {
  bureauName?: string;
  currentWorkspace?: WorkspaceOption | null;
  recentWorkspaces?: WorkspaceOption[];
  userName?: string;
  onWorkspaceSelect?: (id: string) => void;
  onBureauClick?: () => void;
}

export function TopBar({
  bureauName = 'Payroll Bureau',
  currentWorkspace,
  recentWorkspaces = [],
  userName,
  onWorkspaceSelect,
  onBureauClick,
}: TopBarProps) {
  const [wsOpen, setWsOpen] = useState(false);
  const [userOpen, setUserOpen] = useState(false);

  return (
    <header
      style={{ height: 'var(--topbar-height)', backdropFilter: 'blur(8px)' }}
      className="fixed top-0 inset-x-0 z-30 flex items-center gap-4 px-4 bg-white/95 border-b border-gray-200"
    >
      {/* Logo / bureau name */}
      <button
        onClick={onBureauClick}
        className="flex items-center gap-2 shrink-0 font-semibold text-gray-900 hover:text-brand transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-1"
        style={{ borderRadius: 'var(--radius-btn)' }}
      >
        <span className="text-sm">{bureauName}</span>
      </button>

      {/* Divider */}
      <span className="h-5 w-px bg-gray-200 shrink-0" aria-hidden="true" />

      {/* Workspace picker */}
      <div className="relative">
        <button
          onClick={() => { setWsOpen((v) => !v); setUserOpen(false); }}
          className="flex items-center gap-1.5 px-3 h-8 text-sm text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand"
          style={{ borderRadius: 'var(--radius-btn)' }}
          aria-expanded={wsOpen}
          aria-haspopup="listbox"
        >
          {currentWorkspace ? (
            <span className="font-medium">{currentWorkspace.name}</span>
          ) : (
            <span className="text-gray-400">Select workspace</span>
          )}
          <Icon d={ICONS.chevronDown} className="w-3.5 h-3.5 text-gray-400" />
        </button>

        {wsOpen && (
          <div
            style={{ borderRadius: 'var(--radius-card)', boxShadow: 'var(--shadow-dropdown)', minWidth: '220px' }}
            className="absolute top-full mt-1 left-0 bg-white border border-gray-200 py-1 z-50"
          >
            <button
              className="w-full text-left px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 font-medium"
              onClick={() => { onBureauClick?.(); setWsOpen(false); }}
            >
              Bureau Dashboard
            </button>
            {recentWorkspaces.length > 0 && (
              <>
                <div className="my-1 border-t border-gray-100" />
                <p className="px-4 py-1 text-[10px] font-semibold uppercase tracking-wider text-gray-400">Recent</p>
                {recentWorkspaces.map((ws) => (
                  <button
                    key={ws.id}
                    className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 ${currentWorkspace?.id === ws.id ? 'text-brand font-medium' : 'text-gray-700'}`}
                    onClick={() => { onWorkspaceSelect?.(ws.id); setWsOpen(false); }}
                  >
                    {ws.name}
                  </button>
                ))}
              </>
            )}
          </div>
        )}
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* User menu */}
      <div className="relative">
        <button
          onClick={() => { setUserOpen((v) => !v); setWsOpen(false); }}
          className="flex items-center gap-2 px-2 h-8 text-sm text-gray-600 hover:bg-gray-100 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand"
          style={{ borderRadius: 'var(--radius-btn)' }}
          aria-expanded={userOpen}
        >
          <div className="w-6 h-6 rounded-full bg-brand flex items-center justify-center text-white text-[10px] font-bold shrink-0">
            {(userName ?? 'U')[0].toUpperCase()}
          </div>
          {userName && <span className="hidden sm:block">{userName}</span>}
          <Icon d={ICONS.chevronDown} className="w-3.5 h-3.5 text-gray-400" />
        </button>

        {userOpen && (
          <div
            style={{ borderRadius: 'var(--radius-card)', boxShadow: 'var(--shadow-dropdown)', minWidth: '180px' }}
            className="absolute top-full mt-1 right-0 bg-white border border-gray-200 py-1 z-50"
          >
            {userName && <p className="px-4 py-2 text-xs text-gray-500 border-b border-gray-100">{userName}</p>}
            <button className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50">Sign out</button>
          </div>
        )}
      </div>
    </header>
  );
}

// ── NAV-2 — Workspace Sidebar ─────────────────────────────────────────────────

export interface SidebarSection {
  heading?: string;
  items: SidebarItem[];
}

export interface SidebarItem {
  label: string;
  to: string;
  icon: keyof typeof ICONS;
  end?: boolean;
  badge?: number;
}

export interface WorkspaceSidebarProps {
  workspaceId: string;
  workspaceName: string;
  workspaceStatus: string;
  isLive?: boolean;
  collapsed?: boolean;
  onToggleCollapse?: () => void;
  unmatchedEmployeeCount?: number;
  inputIssueCount?: number;
}

export function WorkspaceSidebar({ workspaceId, workspaceName, workspaceStatus, isLive = false, collapsed = false, onToggleCollapse, unmatchedEmployeeCount = 0, inputIssueCount = 0 }: WorkspaceSidebarProps) {
  const w = workspaceId;

  const sections: SidebarSection[] = [
    {
      heading: 'Payroll',
      items: [
        { label: 'Inputs', to: `/workspaces/${w}/payroll/inputs`, icon: 'inputs',  end: true, badge: inputIssueCount || undefined },
        { label: 'Runs',   to: `/workspaces/${w}/payroll`,        icon: 'payroll', end: true },
      ],
    },
    {
      heading: 'People',
      items: [
        { label: 'Employees', to: `/workspaces/${w}/employees`, icon: 'employees', badge: unmatchedEmployeeCount || undefined },
      ],
    },
    {
      heading: 'Settings',
      items: [
        { label: 'Configuration', to: `/workspaces/${w}/config`,            icon: 'config' },
        { label: 'Public Holidays', to: `/workspaces/${w}/public-holidays`, icon: 'calendar' },
        { label: 'Rate Codes',    to: `/workspaces/${w}/rate-codes`,        icon: 'tag' },
      ],
    },
    ...(!isLive ? [{
      heading: undefined,
      items: [{ label: 'Setup Wizard', to: `/workspaces/${w}/setup`, icon: 'setup' as keyof typeof ICONS }],
    }] : []),
  ];

  return (
    <aside
      style={{
        width: collapsed ? 'var(--sidebar-collapsed)' : 'var(--sidebar-expanded)',
        transition: 'width var(--transition-panel)',
        paddingTop: 'var(--topbar-height)',
      }}
      className="fixed left-0 top-0 bottom-0 z-20 flex flex-col bg-white border-r border-gray-200 overflow-hidden shrink-0"
    >
      {/* Workspace name + status */}
      {!collapsed && (
        <div className="px-4 py-4 border-b border-gray-100">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider truncate">{workspaceName}</p>
          <p className="text-[10px] text-gray-400 mt-0.5">{workspaceStatus.replace(/_/g, ' ')}</p>
        </div>
      )}

      {/* Nav sections */}
      <nav className="flex-1 overflow-y-auto py-3 px-2" aria-label="Workspace navigation">
        {sections.map((section, si) => (
          <div key={si} className={si > 0 ? 'mt-5' : ''}>
            {section.heading && !collapsed && (
              <p className="px-3 mb-1 text-[10px] font-semibold uppercase tracking-wider text-gray-400">
                {section.heading}
              </p>
            )}
            {section.items.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-brand/10 text-brand'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                  }`
                }
                style={{ borderRadius: 'var(--radius-btn)' }}
                title={collapsed ? (item.badge ? `${item.label} (${item.badge} unmatched)` : item.label) : undefined}
              >
                <Icon d={ICONS[item.icon]} className="w-5 h-5 shrink-0" />
                {!collapsed && <span className="flex-1 truncate">{item.label}</span>}
                {!collapsed && item.badge && (
                  <span
                    className="shrink-0 min-w-[18px] h-[18px] px-1 flex items-center justify-center rounded-full bg-amber-500 text-white text-[10px] font-bold leading-none"
                    aria-label={`${item.badge} unmatched`}
                  >
                    {item.badge > 99 ? '99+' : item.badge}
                  </span>
                )}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      {/* Collapse toggle */}
      {onToggleCollapse && (
        <button
          onClick={onToggleCollapse}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          className="flex items-center justify-center p-3 text-gray-400 hover:text-gray-600 hover:bg-gray-50 border-t border-gray-100 transition-colors"
        >
          <svg className={`w-4 h-4 transition-transform ${collapsed ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
      )}
    </aside>
  );
}

// ── NAV-3 — Breadcrumb ────────────────────────────────────────────────────────

export interface BreadcrumbItem {
  label: string;
  to?: string;
}

export interface BreadcrumbProps {
  items: BreadcrumbItem[];
  className?: string;
}

export function Breadcrumb({ items, className = '' }: BreadcrumbProps) {
  return (
    <nav aria-label="Breadcrumb" className={`flex items-center gap-1 text-sm ${className}`}>
      {items.map((item, i) => {
        const isLast = i === items.length - 1;
        return (
          <React.Fragment key={i}>
            {i > 0 && (
              <span className="text-gray-300 select-none" aria-hidden="true">/</span>
            )}
            {isLast || !item.to ? (
              <span className={isLast ? 'text-gray-700 font-medium' : 'text-gray-500'} aria-current={isLast ? 'page' : undefined}>
                {item.label}
              </span>
            ) : (
              <Link to={item.to} className="text-gray-500 hover:text-brand transition-colors">
                {item.label}
              </Link>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
}

// ── NAV-4 — Tab Bar ───────────────────────────────────────────────────────────

export interface Tab {
  key: string;
  label: string;
  disabled?: boolean;
}

export interface TabBarProps {
  tabs: Tab[];
  activeKey: string;
  onChange: (key: string) => void;
  className?: string;
}

export function TabBar({ tabs, activeKey, onChange, className = '' }: TabBarProps) {
  return (
    <nav
      className={`flex border-b border-gray-200 ${className}`}
      role="tablist"
      aria-label="Page sections"
    >
      {tabs.map((tab) => {
        const isActive = tab.key === activeKey;
        return (
          <button
            key={tab.key}
            role="tab"
            aria-selected={isActive}
            aria-disabled={tab.disabled}
            disabled={tab.disabled}
            onClick={() => !tab.disabled && onChange(tab.key)}
            className={[
              'px-5 py-3 text-sm font-medium border-b-2 transition-colors',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-inset',
              isActive
                ? 'border-brand text-brand'
                : 'border-transparent text-gray-500 hover:text-gray-800 hover:border-gray-300',
              tab.disabled ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer',
            ].join(' ')}
          >
            {tab.label}
          </button>
        );
      })}
    </nav>
  );
}

// ── NAV-5 — Onboarding Stepper ────────────────────────────────────────────────

export interface Step {
  label: string;
  description?: string;
}

export type StepState = 'completed' | 'current' | 'upcoming';

export interface OnboardingStepperProps {
  steps: Step[];
  /** 0-indexed current step */
  currentStep: number;
  className?: string;
}

export function OnboardingStepper({ steps, currentStep, className = '' }: OnboardingStepperProps) {
  return (
    <ol className={`flex items-start ${className}`} aria-label="Setup progress">
      {steps.map((step, i) => {
        const state: StepState = i < currentStep ? 'completed' : i === currentStep ? 'current' : 'upcoming';
        const isLast = i === steps.length - 1;

        return (
          <li key={i} className={`flex items-start ${!isLast ? 'flex-1' : ''}`}>
            <div className="flex flex-col items-center">
              {/* Circle */}
              <div
                className={[
                  'w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold shrink-0',
                  state === 'completed' ? 'bg-brand text-white' : '',
                  state === 'current'   ? 'bg-brand text-white ring-4 ring-blue-100' : '',
                  state === 'upcoming'  ? 'border-2 border-gray-300 text-gray-400 bg-white' : '',
                ].join(' ')}
                aria-current={state === 'current' ? 'step' : undefined}
              >
                {state === 'completed'
                  ? <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d={ICONS.check} /></svg>
                  : i + 1}
              </div>
              {/* Step label + description */}
              <div className="mt-2 text-center">
                <p className={`text-xs font-semibold ${state === 'upcoming' ? 'text-gray-400' : 'text-gray-700'}`}>
                  {step.label}
                </p>
                {step.description && <p className="text-[10px] text-gray-400 mt-0.5">{step.description}</p>}
              </div>
            </div>
            {/* Connector line */}
            {!isLast && (
              <div className="flex-1 h-px mt-4 mx-3" aria-hidden="true">
                <div className={`h-full ${i < currentStep ? 'bg-brand' : 'bg-gray-200'}`} />
              </div>
            )}
          </li>
        );
      })}
    </ol>
  );
}
