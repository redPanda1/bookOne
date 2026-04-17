import { createAsyncThunk, createSlice, type PayloadAction } from '@reduxjs/toolkit';

import { getSession, type SessionResponse } from '../apis/endpoints';
import type { ApiError } from '../types/api';
import { clearStoredAuthToken, readStoredAuthToken, storeAuthToken } from '../utils/sessionStorage';

export type AuthStatus = 'idle' | 'loading' | 'authenticated' | 'unauthenticated' | 'failed';

export interface AuthSession {
  user: SessionResponse['user'];
  organization: SessionResponse['organization'];
}

interface AuthState {
  token: string | null;
  session: AuthSession | null;
  status: AuthStatus;
  error: ApiError | null;
  hasBootstrapped: boolean;
}

const initialState: AuthState = {
  token: null,
  session: null,
  status: 'idle',
  error: null,
  hasBootstrapped: false,
};

const MISSING_STORED_TOKEN_ERROR: ApiError = {
  kind: 'unauthenticated',
  status: 401,
  message: 'No saved session token was found',
  details: { reason: 'missing_stored_token' },
};

function normalizeSession(response: SessionResponse): AuthSession {
  return {
    user: response.user,
    organization: response.organization,
  };
}

function isMissingStoredTokenError(error: ApiError | undefined): boolean {
  return (
    !!error?.details &&
    typeof error.details === 'object' &&
    'reason' in error.details &&
    error.details.reason === 'missing_stored_token'
  );
}

export const BOOTSTRAP_SESSION = createAsyncThunk<
  { token: string; session: AuthSession },
  void,
  { rejectValue: ApiError }
>('auth/bootstrapSession', async (_, { rejectWithValue }) => {
  const token = readStoredAuthToken();
  if (!token) {
    return rejectWithValue(MISSING_STORED_TOKEN_ERROR);
  }

  const result = await getSession(token);
  if (!result.ok) {
    clearStoredAuthToken();
    return rejectWithValue(result.error);
  }
  if (!result.data.authenticated) {
    clearStoredAuthToken();
    return rejectWithValue({
      kind: 'unauthenticated',
      status: 401,
      message: 'The saved session is no longer authenticated',
      details: result.data,
    });
  }

  return { token, session: normalizeSession(result.data) };
});

export const LOGIN_WITH_DEV_TOKEN = createAsyncThunk<
  { token: string; session: AuthSession },
  string,
  { rejectValue: ApiError }
>('auth/loginWithDevToken', async (token, { rejectWithValue }) => {
  const trimmedToken = token.trim();
  if (!trimmedToken) {
    return rejectWithValue({
      kind: 'validation',
      status: 400,
      message: 'Enter a bearer token to continue',
    });
  }

  const result = await getSession(trimmedToken);
  if (!result.ok) {
    return rejectWithValue(result.error);
  }
  if (!result.data.authenticated) {
    return rejectWithValue({
      kind: 'unauthenticated',
      status: 401,
      message: 'The backend did not accept this token as an authenticated session',
      details: result.data,
    });
  }

  storeAuthToken(trimmedToken);
  return { token: trimmedToken, session: normalizeSession(result.data) };
});

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      clearStoredAuthToken();
      state.token = null;
      state.session = null;
      state.status = 'unauthenticated';
      state.error = null;
      state.hasBootstrapped = true;
    },
    clearAuthError: (state) => {
      state.error = null;
    },
    setTokenForTest: (state, action: PayloadAction<string>) => {
      state.token = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(BOOTSTRAP_SESSION.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(BOOTSTRAP_SESSION.fulfilled, (state, action) => {
        state.token = action.payload.token;
        state.session = action.payload.session;
        state.status = 'authenticated';
        state.error = null;
        state.hasBootstrapped = true;
      })
      .addCase(BOOTSTRAP_SESSION.rejected, (state, action) => {
        state.token = null;
        state.session = null;
        state.status = 'unauthenticated';
        state.error = isMissingStoredTokenError(action.payload) ? null : action.payload ?? null;
        state.hasBootstrapped = true;
      })
      .addCase(LOGIN_WITH_DEV_TOKEN.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(LOGIN_WITH_DEV_TOKEN.fulfilled, (state, action) => {
        state.token = action.payload.token;
        state.session = action.payload.session;
        state.status = 'authenticated';
        state.error = null;
        state.hasBootstrapped = true;
      })
      .addCase(LOGIN_WITH_DEV_TOKEN.rejected, (state, action) => {
        state.token = null;
        state.session = null;
        state.status = 'failed';
        state.error = action.payload ?? {
          kind: 'unexpected',
          status: null,
          message: action.error.message ?? 'Login failed',
        };
      });
  },
});

export const { clearAuthError: CLEAR_AUTH_ERROR, logout: LOGOUT, setTokenForTest: SET_TOKEN_FOR_TEST } = authSlice.actions;
export const authReducer = authSlice.reducer;
