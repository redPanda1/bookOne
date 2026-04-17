import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';

import { getDatabaseHealth, type HealthDbResponse } from '../apis/endpoints';
import type { ApiError } from '../types/api';
import type { RootState } from './store';

type HealthStatus = 'idle' | 'loading' | 'succeeded' | 'failed';

interface HealthState {
  status: HealthStatus;
  data: HealthDbResponse | null;
  error: ApiError | null;
  checkedAt: string | null;
}

const initialState: HealthState = {
  status: 'idle',
  data: null,
  error: null,
  checkedAt: null,
};

export const FETCH_DATABASE_HEALTH = createAsyncThunk<
  HealthDbResponse,
  void,
  { state: RootState; rejectValue: ApiError }
>('health/fetchDatabaseHealth', async (_, { getState, rejectWithValue }) => {
  const token = getState().auth.token;
  if (!token) {
    return rejectWithValue({
      kind: 'unauthenticated',
      status: 401,
      message: 'Login is required before checking backend health',
    });
  }

  const result = await getDatabaseHealth(token);
  if (!result.ok) {
    return rejectWithValue(result.error);
  }
  return result.data;
});

const healthSlice = createSlice({
  name: 'health',
  initialState,
  reducers: {
    clearHealthState: () => initialState,
  },
  extraReducers: (builder) => {
    builder
      .addCase(FETCH_DATABASE_HEALTH.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(FETCH_DATABASE_HEALTH.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.data = action.payload;
        state.error = null;
        state.checkedAt = new Date().toISOString();
      })
      .addCase(FETCH_DATABASE_HEALTH.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload ?? {
          kind: 'unexpected',
          status: null,
          message: action.error.message ?? 'Health check failed',
        };
      });
  },
});

export const { clearHealthState: CLEAR_HEALTH_STATE } = healthSlice.actions;
export const healthReducer = healthSlice.reducer;
