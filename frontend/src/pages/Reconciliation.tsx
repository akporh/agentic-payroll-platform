/**
 * Legacy Reconciliation page — now a tab inside PayrollResults (DD-2).
 * This redirect preserves any bookmarked URLs.
 */

import { useParams, Navigate } from 'react-router-dom';

export function Reconciliation() {
  const { workspaceId, runId } = useParams<{ workspaceId: string; runId: string }>();
  return (
    <Navigate
      to={`/workspaces/${workspaceId}/payroll/${runId}/results`}
      replace
    />
  );
}
