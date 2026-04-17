import { Navigate, RouterProvider, createBrowserRouter } from 'react-router-dom';

import { AuthBootstrap } from '../app/AuthBootstrap';
import { AppShell } from '../components/AppShell';
import { PlaceholderPage } from '../components/PlaceholderPage';
import { DashboardPage } from '../pages/DashboardPage';
import { LoginPage } from '../pages/LoginPage';
import { SystemHealthPage } from '../pages/SystemHealthPage';
import { ThemePage } from '../pages/ThemePage';
import { RequireAuth } from './RequireAuth';

const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/app',
    element: (
      <RequireAuth>
        <AppShell />
      </RequireAuth>
    ),
    children: [
      { index: true, element: <Navigate to="/app/dashboard" replace /> },
      { path: 'dashboard', element: <DashboardPage /> },
      { path: 'system-health', element: <SystemHealthPage /> },
      { path: 'theme', element: <ThemePage /> },
      {
        path: 'journal-entries',
        element: (
          <PlaceholderPage
            title="Journal Entries"
            subtitle="Manual journal workflows start in the next frontend phase."
          />
        ),
      },
      {
        path: 'reports',
        element: <PlaceholderPage title="Reports" subtitle="Reporting screens will build on posted ledger data in a later phase." />,
      },
      {
        path: 'settings',
        element: <PlaceholderPage title="Settings" subtitle="Organization and security settings will be added as the platform hardens." />,
      },
    ],
  },
  {
    path: '/',
    element: <Navigate to="/app/dashboard" replace />,
  },
  {
    path: '*',
    element: <Navigate to="/app/dashboard" replace />,
  },
]);

export function AppRouter() {
  return (
    <AuthBootstrap>
      <RouterProvider router={router} />
    </AuthBootstrap>
  );
}
