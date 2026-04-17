# Agent Prompt — Phase 1D Authentication Foundation

You are working in `/Users/simon/Developer/bookOne`. Implement Phase 1D: replace the Phase 1C development bearer-token authentication scaffold with real Cognito-backed username/password authentication and token refresh.

Before editing, read:

- `docs/project_status.md`
- `docs/build_notes/phase1c_frontend_shell_foundation.md`
- `docs/bookone_frontend_architecture.md`
- `docs/bookone_system_architecture_api.md`
- `frontend/README.md`
- `backend/src/auth/jwt_helper.py`
- `backend/src/handlers/app.py`
- `frontend/src/store/authSlice.ts`
- `frontend/src/apis/apiClient.ts`
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/routes/RequireAuth.tsx`

Goals:

- Replace the development bearer-token form with a real username/password login screen backed by Cognito.
- Preserve the Phase 1C shell conventions: React Router protected routes, Redux Toolkit thunks, `ApiResult<T>`, shared Axios API client, status notifications, and `/session` bootstrap.
- Store only browser-session token material. Do not persist user or organization metadata outside Redux memory.
- Wire the existing Axios 401 runtime hook to attempt token refresh once, retry the original request on refresh success, and clear auth state plus show a session-expired message only when refresh fails.
- Replace backend mock/unverified JWT behavior with verified Cognito/JWKS validation or API Gateway HTTP API JWT authorizer claims.
- Keep `GET /session` as the normalized contract returning `{ authenticated, user, organization }`.
- Add or update `.env.example` files and docs for required Cognito region, user pool id, app client id, issuer/audience, and any backend validation settings.
- Add focused tests for login success/failure, bootstrap with saved token, refresh-on-401 behavior, refresh failure logout, and backend token validation behavior.

Constraints:

- Do not build journal-entry CRUD in this phase.
- Do not introduce broad auth abstractions beyond what the current Cognito integration requires.
- Do not keep accepting arbitrary bearer strings as authenticated users after Phase 1D.
- Do not store refresh tokens in localStorage.
- Keep API error normalization compatible with existing `{"message": "..."}` and `{"errorMessage": "..."}` backend payloads.

Validation:

- Run frontend lint, typecheck, tests, and build from `frontend/`.
- Run relevant backend tests.
- Update `docs/project_status.md` and add a Phase 1D build note under `docs/build_notes/` summarizing implementation choices, compromises, and validation results.
