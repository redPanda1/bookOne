import { combineReducers, configureStore } from '@reduxjs/toolkit';

import { authReducer, LOGOUT } from './authSlice';
import { healthReducer } from './healthSlice';
import { statusReducer } from './statusSlice';

const appReducer = combineReducers({
  auth: authReducer,
  health: healthReducer,
  status: statusReducer,
});

export type RootState = ReturnType<typeof appReducer>;

const rootReducer: typeof appReducer = (state, action) => {
  if (LOGOUT.match(action)) {
    return appReducer(undefined, action);
  }
  return appReducer(state, action);
};

export const store = configureStore({
  reducer: rootReducer,
});

export type AppDispatch = typeof store.dispatch;
