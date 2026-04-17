import { apiRequest } from './apiClient';

export interface SessionResponse {
  authenticated: boolean;
  user: {
    id: string;
    email: string;
  };
  organization: {
    id: string;
    name: string;
  };
}

export interface HealthDbResponse {
  status: 'ok' | 'error';
  database: {
    ok: boolean;
    error?: string;
  };
}

export function getSession(token?: string | null) {
  return apiRequest<SessionResponse>('/session', { method: 'GET', token });
}

export function getDatabaseHealth(token: string) {
  return apiRequest<HealthDbResponse>('/health/db', { method: 'GET', token });
}
