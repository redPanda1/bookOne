# BookOne Frontend

React + TypeScript SPA for the BookOne application shell.

## Stack

- React 19
- Vite 8
- TypeScript 6
- MUI 9
- Redux Toolkit + thunks
- React Router
- Axios API transport
- Redux-backed MUI status notifications

## Local Setup

```bash
cd /Users/simon/Developer/bookOne/frontend
npm install
cp .env.example .env.local
npm run dev
```

`VITE_API_BASE_URL` controls the backend API base URL. The default example points to the deployed dev API. For local SAM, set:

```bash
VITE_API_BASE_URL=http://127.0.0.1:3001
```

## Authentication

Phase 1C uses a development bearer-token scaffold. The login page stores only the token in `sessionStorage`, then calls `/session` to hydrate user and organization metadata into Redux memory.

This is intentionally not a complete Cognito sign-in flow. Future Cognito Hosted UI or token-refresh work should replace the token source while keeping the shared API client and route guards intact.

## API Client

All backend calls should go through `src/apis`. The API layer uses Axios so auth headers, response normalization, retries, and future token-refresh behavior stay centralized.

Token refresh is not implemented yet because BookOne does not currently have a frontend refresh-token state model or backend refresh contract. The Axios 401 runtime hook is deliberately left as the integration point for Phase 1D.

## Validation

```bash
npm run lint
npm run typecheck
npm test
npm run build
```
