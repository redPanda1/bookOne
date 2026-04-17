const DEFAULT_API_BASE_URL = 'https://3bxkul49pc.execute-api.us-east-1.amazonaws.com';

function trimTrailingSlash(value: string): string {
  return value.replace(/\/+$/, '');
}

export const appConfig = {
  apiBaseUrl: trimTrailingSlash(import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL),
};
