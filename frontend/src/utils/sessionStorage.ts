const TOKEN_STORAGE_KEY = 'bookone.authToken';

export function readStoredAuthToken(): string | null {
  return window.sessionStorage.getItem(TOKEN_STORAGE_KEY);
}

export function storeAuthToken(token: string): void {
  window.sessionStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function clearStoredAuthToken(): void {
  window.sessionStorage.removeItem(TOKEN_STORAGE_KEY);
}
