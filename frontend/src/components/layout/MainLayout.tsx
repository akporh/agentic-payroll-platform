import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageShell } from '../../design-system';
import { workspaceApi } from '../../api/workspace';
import type { Workspace } from '../../types/workspace';
import { WorkspaceContext } from '../../context/WorkspaceContext';

export function MainLayout() {
  const { workspaceId } = useParams<{ workspaceId?: string }>();
  const navigate = useNavigate();
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    workspaceApi.list().then(setWorkspaces).catch(() => {});
  }, [workspaceId]); // re-fetch when navigating to a different workspace so newly-created workspaces appear

  const currentWorkspace = workspaces.find(w => w.workspace_id === workspaceId) ?? null;
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
      />
    </WorkspaceContext.Provider>
  );
}
