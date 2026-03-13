import { createBrowserRouter } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout';
import { BureauDashboard } from './pages/BureauDashboard';
import { JsonOnboarding } from './pages/JsonOnboarding';
import { WorkspaceDashboard } from './pages/WorkspaceDashboard';
import { WorkspaceSetup } from './pages/WorkspaceSetup';
import { Employees } from './pages/Employees';
import { PayrollRuns } from './pages/PayrollRuns';
import { RunPayroll } from './pages/RunPayroll';
import { PayrollResults } from './pages/PayrollResults';
import { Reconciliation } from './pages/Reconciliation';
import { PayrollInputs } from './pages/PayrollInputs';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      { index: true, element: <BureauDashboard /> },
      { path: 'onboarding', element: <JsonOnboarding /> },
      {
        path: 'workspaces/:workspaceId',
        children: [
          { index: true, element: <WorkspaceDashboard /> },
          { path: 'setup', element: <WorkspaceSetup /> },
          { path: 'employees', element: <Employees /> },
          {
            path: 'payroll',
            children: [
              { index: true, element: <PayrollRuns /> },
              { path: 'new', element: <RunPayroll /> },
              { path: ':runId/results', element: <PayrollResults /> },
              { path: ':runId/reconciliation', element: <Reconciliation /> },
              { path: 'inputs', element: <PayrollInputs /> },
            ],
          },
        ],
      },
    ],
  },
]);
