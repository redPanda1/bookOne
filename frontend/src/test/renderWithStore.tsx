import type { ReactNode } from 'react';
import { configureStore } from '@reduxjs/toolkit';
import { Provider } from 'react-redux';
import { render } from '@testing-library/react';

import { authReducer } from '../store/authSlice';
import { healthReducer } from '../store/healthSlice';
import { statusReducer } from '../store/statusSlice';

export function createTestStore(preloadedState?: Parameters<typeof configureStore>[0]['preloadedState']) {
  return configureStore({
    reducer: {
      auth: authReducer,
      health: healthReducer,
      status: statusReducer,
    },
    preloadedState,
  });
}

export function renderWithStore(ui: ReactNode, preloadedState?: Parameters<typeof configureStore>[0]['preloadedState']) {
  const store = createTestStore(preloadedState);
  return {
    store,
    ...render(<Provider store={store}>{ui}</Provider>),
  };
}
