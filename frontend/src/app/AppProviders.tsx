import type { ReactNode } from 'react';
import { Provider } from 'react-redux';
import { ThemeProvider } from '@mui/material/styles';

import { store } from '../store/store';
import { theme } from '../theme/theme';
import { StatusController } from '../components/StatusController';

interface AppProvidersProps {
  children: ReactNode;
}

export function AppProviders({ children }: AppProvidersProps) {
  return (
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <StatusController />
        {children}
      </ThemeProvider>
    </Provider>
  );
}
