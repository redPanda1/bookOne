import type { ReactNode } from 'react';
import { useEffect } from 'react';

import { BOOTSTRAP_SESSION } from '../store/authSlice';
import { useAppDispatch, useAppSelector } from '../hooks/redux';

interface AuthBootstrapProps {
  children: ReactNode;
}

export function AuthBootstrap({ children }: AuthBootstrapProps) {
  const dispatch = useAppDispatch();
  const hasBootstrapped = useAppSelector((state) => state.auth.hasBootstrapped);

  useEffect(() => {
    if (!hasBootstrapped) {
      void dispatch(BOOTSTRAP_SESSION());
    }
  }, [dispatch, hasBootstrapped]);

  return children;
}
