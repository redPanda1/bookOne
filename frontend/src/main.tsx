import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { CssBaseline } from '@mui/material';

import { AppProviders } from './app/AppProviders';
import { AppRouter } from './routes/AppRouter';
import './styles.css';

const root = document.getElementById('root');

if (!root) {
  throw new Error('BookOne root element was not found');
}

createRoot(root).render(
  <StrictMode>
    <AppProviders>
      <CssBaseline />
      <AppRouter />
    </AppProviders>
  </StrictMode>,
);
