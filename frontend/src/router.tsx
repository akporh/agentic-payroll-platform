import { createBrowserRouter } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout';
import { BureauDashboard } from './pages/BureauDashboard';
import { WorkspaceDashboard } from './pages/WorkspaceDashboard';
import { WorkspaceSetup } from './pages/WorkspaceSetup';
import { Employees } from './pages/Employees';
import { PayrollRuns } from './pages/PayrollRuns';
import { RunPayroll } from './pages/RunPayroll';
import { PayrollResults } from './pages/PayrollResults';
import { PayrollInputs } from './pages/PayrollInputs';
import { PayrollInputsBulkUpload } from './pages/PayrollInputsBulkUpload';
import { WorkspaceConfig } from './pages/WorkspaceConfig';
import { PublicHolidays } from './pages/PublicHolidays';
import { RateCodes } from './pages/RateCodes';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      { index: true, element: <BureauDashboard /> },
      {
        path: 'workspaces/:workspaceId',
        children: [
          { index: true, element: <WorkspaceDashboard /> },
          { path: 'config', element: <WorkspaceConfig /> },
          { path: 'setup', element: <WorkspaceSetup /> },
          { path: 'public-holidays', element: <PublicHolidays /> },
          { path: 'rate-codes', element: <RateCodes /> },
          { path: 'employees', element: <Employees /> },
          {
            path: 'payroll',
            children: [
              { index: true, element: <PayrollRuns /> },
              { path: 'new', element: <RunPayroll /> },
              { path: ':runId/results', element: <PayrollResults /> },
              { path: 'inputs', element: <PayrollInputs /> },
              { path: 'inputs/bulk', element: <PayrollInputsBulkUpload /> },
            ],
          },
        ],
      },
    ],
  },
]);
