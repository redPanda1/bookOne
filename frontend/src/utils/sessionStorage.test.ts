import { afterEach, describe, expect, it } from 'vitest';

import { clearStoredAuthToken, readStoredAuthToken, storeAuthToken } from './sessionStorage';

describe('auth token session storage', () => {
  afterEach(() => {
    window.sessionStorage.clear();
  });

  it('stores, reads, and clears only the bearer token', () => {
    expect(readStoredAuthToken()).toBeNull();

    storeAuthToken('dev-token');
    expect(readStoredAuthToken()).toBe('dev-token');

    clearStoredAuthToken();
    expect(readStoredAuthToken()).toBeNull();
  });
});
