import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';

import { LoadingState } from '../components/LoadingState';
import { useAppSelector } from '../hooks/redux';

interface RequireAuthProps {
  children: ReactNode;
}

export function RequireAuth({ children }: RequireAuthProps) {
  const { status, hasBootstrapped } = useAppSelector((state) => state.auth);
  const location = useLocation();

  if (!hasBootstrapped || status === 'loading') {
    return <LoadingState message="Checking your session" />;
  }

  if (status !== 'authenticated') {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return children;
}
