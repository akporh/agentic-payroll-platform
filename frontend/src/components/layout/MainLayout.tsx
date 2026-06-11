import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageShell } from '../../design-system';
import { workspaceApi } from '../../api/workspace';
import { payrollApi } from '../../api/payroll';
import type { Workspace } from '../../types/workspace';
import type { Employee } from '../../types/payroll';
import { WorkspaceContext } from '../../context/WorkspaceContext';

export function MainLayout() {
  const { workspaceId } = useParams<{ workspaceId?: string }>();
  const navigate = useNavigate();
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [collapsed, setCollapsed] = useState(false);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [inputIssueCount, setInputIssueCount] = useState(0);
  const [timesheetEnabled, setTimesheetEnabled] = useState(false);

  useEffect(() => {
    workspaceApi.list().then(setWorkspaces).catch(() => {});
  }, [workspaceId]);

  useEffect(() => {
    if (!workspaceId) { setEmployees([]); setInputIssueCount(0); setTimesheetEnabled(false); return; }
    const fetchEmployees = () => workspaceApi.getEmployees(workspaceId).then(setEmployees).catch(() => {});
    const fetchInputIssues = () => payrollApi.getInputIssues(workspaceId).then((d) => setInputIssueCount(d.total)).catch(() => {});
    fetchEmployees();
    fetchInputIssues();
    workspaceApi.getPayrollConfig(workspaceId).then((cfg) => setTimesheetEnabled(cfg.timesheet_enabled ?? false)).catch(() => {});
    window.addEventListener('employees-changed', fetchEmployees);
    window.addEventListener('payroll-inputs-changed', fetchInputIssues);
    return () => {
      window.removeEventListener('employees-changed', fetchEmployees);
      window.removeEventListener('payroll-inputs-changed', fetchInputIssues);
    };
  }, [workspaceId]);

  const currentWorkspace = workspaces.find(w => w.workspace_id === workspaceId) ?? null;
  const unmatchedEmployeeCount = employees.filter(e => !e.is_ended && (!e.grade || !e.designation)).length;
  const notEnrolledEmployeeCount = employees.filter(e => !e.is_ended && !e.is_enrolled).length;
  const recentWorkspaces = workspaces.slice(0, 5).map(w => ({
    id: w.workspace_id,
    name: w.name,
    status: w.status,
  }));

  return (
    <WorkspaceContext.Provider value={{ workspace: currentWorkspace, workspaces }}>
      <PageShell
        workspaceId={workspaceId}
        workspaceName={currentWorkspace?.name}
        workspaceStatus={currentWorkspace?.status}
        isLive={currentWorkspace?.status === 'LIVE'}
        currentWorkspace={
          currentWorkspace
            ? { id: currentWorkspace.workspace_id, name: currentWorkspace.name, status: currentWorkspace.status }
            : null
        }
        recentWorkspaces={recentWorkspaces}
        onWorkspaceSelect={(id) => navigate(`/workspaces/${id}`)}
        onBureauClick={() => navigate('/')}
        sidebarCollapsed={collapsed}
        onToggleSidebar={() => setCollapsed(v => !v)}
        unmatchedEmployeeCount={unmatchedEmployeeCount}
        notEnrolledEmployeeCount={notEnrolledEmployeeCount}
        inputIssueCount={inputIssueCount}
        timesheetEnabled={timesheetEnabled}
      />
    </WorkspaceContext.Provider>
  );
}
