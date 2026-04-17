import { AxiosError, type AxiosAdapter, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { apiRequest, axiosApiClient } from './apiClient';

function makeResponse<T>(config: InternalAxiosRequestConfig, status: number, data: T): AxiosResponse<T> {
  return {
    data,
    status,
    statusText: String(status),
    headers: {},
    config,
  };
}

function makeHttpError<T>(config: InternalAxiosRequestConfig, status: number, data: T): AxiosError<T> {
  return new AxiosError(
    `Request failed with status ${status}`,
    undefined,
    config,
    undefined,
    makeResponse(config, status, data),
  );
}

describe('apiRequest', () => {
  const originalAdapter = axiosApiClient.defaults.adapter;

  afterEach(() => {
    axiosApiClient.defaults.adapter = originalAdapter;
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it('returns typed successful payloads', async () => {
    const adapter = vi.fn<AxiosAdapter>(async (config) => makeResponse(config, 200, { status: 'ok' }));
    axiosApiClient.defaults.adapter = adapter;

    const result = await apiRequest<{ status: string }>('/health/db', { token: 'token-1' });

    expect(result).toEqual({ ok: true, data: { status: 'ok' } });
    expect(adapter).toHaveBeenCalledWith(expect.objectContaining({ url: '/health/db' }));
    expect(adapter.mock.calls[0][0].headers.Authorization).toBe('Bearer token-1');
  });

  it('normalizes backend message errors', async () => {
    axiosApiClient.defaults.adapter = vi.fn<AxiosAdapter>(async (config) => {
      throw makeHttpError(config, 401, { message: 'Unauthorized' });
    });

    const result = await apiRequest('/health/db', { maxRetries: 0 });

    expect(result).toEqual({
      ok: false,
      error: expect.objectContaining({
        kind: 'unauthenticated',
        status: 401,
        message: 'Unauthorized',
      }),
    });
  });

  it('normalizes NYA-style errorMessage payloads', async () => {
    axiosApiClient.defaults.adapter = vi.fn<AxiosAdapter>(async (config) => {
      throw makeHttpError(config, 400, { errorMessage: 'Bad thing' });
    });

    const result = await apiRequest('/health/db', { maxRetries: 0 });

    expect(result).toEqual({
      ok: false,
      error: expect.objectContaining({
        kind: 'validation',
        status: 400,
        message: 'Bad thing',
      }),
    });
  });

  it('normalizes network errors', async () => {
    axiosApiClient.defaults.adapter = vi.fn<AxiosAdapter>(async (config) => {
      throw new AxiosError('Network Error', 'ERR_NETWORK', config);
    });

    const result = await apiRequest('/health/db', { maxRetries: 0 });

    expect(result).toEqual({
      ok: false,
      error: expect.objectContaining({
        kind: 'network',
        status: null,
        message: 'Network Error',
      }),
    });
  });

  it('retries retryable failures', async () => {
    vi.useFakeTimers();
    vi.spyOn(Math, 'random').mockReturnValue(0);
    const adapter = vi.fn<AxiosAdapter>(async (config) => {
      if (adapter.mock.calls.length === 1) {
        throw makeHttpError(config, 503, { message: 'Unavailable' });
      }
      return makeResponse(config, 200, { status: 'ok' });
    });
    axiosApiClient.defaults.adapter = adapter;

    const request = apiRequest<{ status: string }>('/health/db', {
      maxRetries: 1,
      retryDelayMs: 1,
    });
    await vi.advanceTimersByTimeAsync(1);
    const result = await request;

    expect(result).toEqual({ ok: true, data: { status: 'ok' } });
    expect(adapter).toHaveBeenCalledTimes(2);
  });

  it('does not retry validation or auth failures', async () => {
    const adapter = vi.fn<AxiosAdapter>(async (config) => {
      throw makeHttpError(config, 400, { message: 'Invalid' });
    });
    axiosApiClient.defaults.adapter = adapter;

    const result = await apiRequest('/health/db');

    expect(result).toEqual({
      ok: false,
      error: expect.objectContaining({
        kind: 'validation',
        message: 'Invalid',
      }),
    });
    expect(adapter).toHaveBeenCalledTimes(1);
  });
});
