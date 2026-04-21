import { createContext, useContext } from 'react';
import type { Workspace } from '../types/workspace';

interface WorkspaceContextValue {
  workspace: Workspace | null;
  workspaces: Workspace[];
}

export const WorkspaceContext = createContext<WorkspaceContextValue>({
  workspace: null,
  workspaces: [],
});

export function useWorkspaceContext() {
  return useContext(WorkspaceContext);
}
