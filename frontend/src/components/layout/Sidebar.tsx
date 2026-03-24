import { NavLink, useParams } from 'react-router-dom';

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `flex items-center gap-2 px-3 py-2 rounded text-sm font-medium transition-colors ${
    isActive
      ? 'bg-slate-700 text-white'
      : 'text-slate-400 hover:bg-slate-700 hover:text-white'
  }`;

export function Sidebar() {
  const { workspaceId } = useParams<{ workspaceId?: string }>();

  return (
    <aside className="w-56 min-h-screen bg-slate-900 flex flex-col py-4 px-3 gap-1 shrink-0">
      <div className="px-3 mb-6">
        <span className="text-white font-bold text-base tracking-tight">
          Payroll Bureau
        </span>
        <p className="text-slate-500 text-xs mt-0.5">Operations Console</p>
      </div>

      <NavLink to="/" end className={navLinkClass}>
        <Icon d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        Dashboard
      </NavLink>

      <NavLink to="/onboarding" className={navLinkClass}>
        <Icon d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        New Client
      </NavLink>

      {workspaceId && (
        <>
          <div className="mt-4 mb-1 px-3">
            <p className="text-slate-600 text-xs uppercase tracking-wider font-semibold">
              Workspace
            </p>
          </div>

          <NavLink to={`/workspaces/${workspaceId}`} end className={navLinkClass}>
            <Icon d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            Overview
          </NavLink>

          <NavLink to={`/workspaces/${workspaceId}/config`} className={navLinkClass}>
            <Icon d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            Configuration
          </NavLink>

          <NavLink to={`/workspaces/${workspaceId}/setup`} className={navLinkClass}>
            <Icon d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            Client Setup
          </NavLink>

          <NavLink to={`/workspaces/${workspaceId}/employees`} className={navLinkClass}>
            <Icon d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
            Employees
          </NavLink>

          <NavLink to={`/workspaces/${workspaceId}/payroll`} end className={navLinkClass}>
            <Icon d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            Payroll Runs
          </NavLink>

          <NavLink to={`/workspaces/${workspaceId}/payroll/inputs`} end className={navLinkClass}>
            <Icon d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            Period Inputs
          </NavLink>

          <NavLink to={`/workspaces/${workspaceId}/payroll/inputs/bulk`} className={navLinkClass}>
            <Icon d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            Bulk Upload
          </NavLink>
        </>
      )}

      <div className="mt-auto px-3 pt-4 border-t border-slate-800">
        <p className="text-slate-600 text-xs">v0.1.0 · internal</p>
      </div>
    </aside>
  );
}

function Icon({ d }: { d: string }) {
  return (
    <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d={d} />
    </svg>
  );
}
