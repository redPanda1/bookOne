import type { AxiosAdapter, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { SET_TOKEN_FOR_TEST } from './authSlice';
import { FETCH_DATABASE_HEALTH } from './healthSlice';
import { axiosApiClient } from '../apis/apiClient';
import { createTestStore } from '../test/renderWithStore';

function makeResponse<T>(config: InternalAxiosRequestConfig, data: T): AxiosResponse<T> {
  return {
    data,
    status: 200,
    statusText: '200',
    headers: {},
    config,
  };
}

describe('healthSlice', () => {
  const originalAdapter = axiosApiClient.defaults.adapter;

  afterEach(() => {
    axiosApiClient.defaults.adapter = originalAdapter;
    vi.restoreAllMocks();
  });

  it('rejects when no auth token exists', async () => {
    const store = createTestStore();

    const result = await store.dispatch(FETCH_DATABASE_HEALTH());

    expect(FETCH_DATABASE_HEALTH.rejected.match(result)).toBe(true);
    expect(store.getState().health.error?.kind).toBe('unauthenticated');
  });

  it('loads protected database health through the API client', async () => {
    axiosApiClient.defaults.adapter = vi.fn<AxiosAdapter>(async (config) =>
      makeResponse(config, { status: 'ok', database: { ok: true } }),
    );
    const store = createTestStore();
    store.dispatch(SET_TOKEN_FOR_TEST('token-1'));

    const result = await store.dispatch(FETCH_DATABASE_HEALTH());

    expect(FETCH_DATABASE_HEALTH.fulfilled.match(result)).toBe(true);
    expect(store.getState().health.data?.database.ok).toBe(true);
  });
});
