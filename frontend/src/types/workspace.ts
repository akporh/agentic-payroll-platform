export type WorkspaceStatus =
  | 'DRAFT'
  | 'STRUCTURE_DEFINED'
  | 'COMPENSATION_DEFINED'
  | 'RULES_DEFINED'
  | 'READY'
  | 'LIVE';

export interface Workspace {
  workspace_id: string;
  name: string;
  country_code: string;
  status: WorkspaceStatus;
  active_employee_count?: number;
}

export interface OnboardingCheck {
  key: string;
  label: string;
  present: boolean;
}

export interface OnboardingStatus {
  status: WorkspaceStatus;
  progress_percent: number;
  missing: string[];
  next_allowed_states: WorkspaceStatus[];
}
