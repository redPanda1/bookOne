import axios, { AxiosError, type AxiosRequestConfig, type AxiosResponse } from 'axios';

import type { ApiError, ApiRequestOptions, ApiResult } from '../types/api';
import { appConfig } from '../utils/env';

declare module 'axios' {
  export interface AxiosRequestConfig {
    _retryCount?: number;
    _maxRetries?: number;
    _retryDelayMs?: number;
    _authToken?: string | null;
  }

  export interface InternalAxiosRequestConfig {
    _retryCount?: number;
    _maxRetries?: number;
    _retryDelayMs?: number;
    _authToken?: string | null;
  }
}

interface BackendErrorPayload {
  message?: unknown;
  errorMessage?: unknown;
}

interface ApiClientRuntime {
  getToken?: () => string | null;
  onUnauthenticated?: (error: ApiError) => void;
  refreshToken?: () => Promise<string | null>;
}

const DEFAULT_MAX_RETRIES = 2;
const DEFAULT_RETRY_DELAY_MS = 500;

let runtimeConfig: ApiClientRuntime = {};

export const axiosApiClient = axios.create({
  baseURL: appConfig.apiBaseUrl,
  headers: {
    accept: 'application/json',
  },
});

function errorKindForStatus(status: number): ApiError['kind'] {
  if (status === 400 || status === 422) return 'validation';
  if (status === 401) return 'unauthenticated';
  if (status === 403) return 'unauthorized';
  if (status === 404) return 'not_found';
  if (status === 409) return 'conflict';
  if (status >= 500) return 'server';
  return 'unexpected';
}

function readMessage(payload: unknown, fallback: string): string {
  if (payload && typeof payload === 'object') {
    const { message, errorMessage } = payload as BackendErrorPayload;
    for (const candidate of [message, errorMessage]) {
      if (typeof candidate === 'string' && candidate.trim()) {
        return candidate;
      }
    }
  }
  return fallback;
}

function normalizeAxiosError(error: unknown): ApiError {
  if (!axios.isAxiosError(error)) {
    return {
      kind: 'unexpected',
      status: null,
      message: error instanceof Error ? error.message : 'Request failed',
      details: error,
    };
  }

  const status = error.response?.status ?? null;
  if (status === null) {
    return {
      kind: 'network',
      status: null,
      message: error.message || 'Network request failed',
      details: {
        code: error.code,
        message: error.message,
      },
    };
  }

  return {
    kind: errorKindForStatus(status),
    status,
    message: readMessage(error.response?.data, error.message || `Request failed with status ${status}`),
    details: error.response?.data,
  };
}

function isRetriableError(error: AxiosError): boolean {
  if (!error.response) return true;
  const status = error.response.status;
  if (status === 408) return true;
  return status >= 500 && status !== 501 && status !== 505;
}

function calculateRetryDelay(retryCount: number, baseDelayMs: number): number {
  const exponentialDelay = baseDelayMs * 2 ** retryCount;
  const jitter = Math.random() * 0.3 * exponentialDelay;
  return Math.min(exponentialDelay + jitter, 10_000);
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

export function configureApiClient(config: ApiClientRuntime): void {
  runtimeConfig = config;
}

axiosApiClient.interceptors.request.use((config) => {
  const token = config._authToken ?? runtimeConfig.getToken?.() ?? null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

axiosApiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;
    if (!originalRequest) {
      return Promise.reject(error);
    }

    if (error.response?.status === 401) {
      const normalizedError = normalizeAxiosError(error);
      runtimeConfig.onUnauthenticated?.(normalizedError);

      // Future Cognito work should plug token refresh into runtimeConfig.refreshToken
      // once refresh-token storage and the backend refresh contract exist.
      return Promise.reject(error);
    }

    const retryCount = originalRequest._retryCount ?? 0;
    const maxRetries = originalRequest._maxRetries ?? DEFAULT_MAX_RETRIES;
    if (isRetriableError(error) && retryCount < maxRetries) {
      originalRequest._retryCount = retryCount + 1;
      const delayMs = calculateRetryDelay(retryCount, originalRequest._retryDelayMs ?? DEFAULT_RETRY_DELAY_MS);
      await sleep(delayMs);
      return axiosApiClient(originalRequest);
    }

    return Promise.reject(error);
  },
);

export async function apiRequest<T>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<ApiResult<T>> {
  try {
    const requestConfig: AxiosRequestConfig = {
      url: path,
      method: options.method ?? 'GET',
      data: options.body,
      headers: options.headers,
      _authToken: options.token,
      _maxRetries: options.maxRetries,
      _retryDelayMs: options.retryDelayMs,
    };

    const response = await axiosApiClient.request<T>(requestConfig);
    return { ok: true, data: response.data };
  } catch (error) {
    return {
      ok: false,
      error: normalizeAxiosError(error),
    };
  }
}
