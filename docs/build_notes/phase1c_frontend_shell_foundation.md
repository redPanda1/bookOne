# Build Note — Phase 1C Frontend Shell Foundation

Date: 2026-04-16

## 1. Summary of Work Completed

- Created the initial React + Vite + TypeScript frontend scaffold under `frontend/`.
- Added Redux Toolkit store setup with typed hooks and thunk-based async conventions.
- Added auth slice and development bearer-token login scaffold.
- Added `sessionStorage` token persistence; user and organization metadata remain Redux-memory state and are rehydrated from `/session`.
- Added React Router routes:
  - `/login`
  - `/app/dashboard`
  - `/app/system-health`
  - placeholder protected routes for future modules
- Added authenticated app shell with left navigation, top bar, page content area, and logout.
- Added shared typed API client with normalized `ApiResult<T>` and `ApiError` conventions.
- Added protected system health page calling `GET /health/db`.
- Added MUI theme scaffold using the BookOne dark green/deep teal palette and Onest font.
- Added common page, section card, loading, inline error, and empty state components.
- Added `statusSlice` for centralised user messaging (snackbar) and global loading state; replaced notistack with a Redux-driven MUI Snackbar/Alert rendered by `StatusController`.
- Standardized **page-level** responsive layout on MUI v9 **Grid** (`container` + breakpoint `size`, including `grow` / `auto` where appropriate) for shared shells and key screens; left **Box** for the authenticated app frame (flex sidebar + main), purely decorative elements, and single-column helpers such as loading and empty states.

## 2. Architectural Choices

- Frontend remains a SPA using React Router and Redux Toolkit thunks.
- API calls must go through the Axios-based `src/apis` client; ad hoc component fetches should be avoided.
- The API client centralizes auth header injection, retry behavior, 401 normalization, and compatible `message` / `errorMessage` server error parsing.
- Thunks reject with typed `ApiError` payloads and slices model async state with `idle/loading/succeeded/failed`.
- User-facing notifications (snackbar) and global loading/backdrop state are managed exclusively through `statusSlice`. Components dispatch `USER_MESSAGE`, `CLOSE_MESSAGE`, `START_LOADING`, or `END_LOADING` actions; rendering is handled once in `StatusController` (mounted in `AppProviders`). This eliminates per-component notification hook calls and keeps UI feedback state inspectable in Redux DevTools.
- All action creators (thunks and slice actions) are exported in SCREAMING_SNAKE_CASE so every `dispatch(...)` call site is immediately identifiable as a state-mutation point (see §4.4).
- Only the bearer token is persisted, and only in `sessionStorage`.
- Sensitive session metadata is reloaded from `/session` and kept in memory.
- The development login is truthful but incomplete: it validates a provided bearer token against the current backend scaffold and is ready to be replaced by Cognito Hosted UI or a richer Cognito client flow.
- The protected reference endpoint is `GET /health/db` because it is read-only, already deployed, and verifies auth-header injection plus backend-to-Aurora connectivity.

### 2.1 Source directory structure

The `src/` tree follows a **library-by-concern** layout rather than a features-by-domain layout. This keeps the scaffold clean and extensible as new accounting modules are added.

```
src/
├── app/           Bootstrap wiring — AppProviders, AuthBootstrap
├── apis/          HTTP layer — apiClient (Axios), endpoints
├── assets/        Static assets imported into components (images, icons, fonts)
├── components/    Shared reusable UI — AppShell, PageContainer, SectionCard, LoadingState, StatusController, etc.
├── hooks/         Custom React hooks — useAppDispatch, useAppSelector
├── pages/         Route-level page components — LoginPage, DashboardPage, etc.
├── routes/        Router definition and route guards — AppRouter, RequireAuth
├── store/         Redux store, slices, and slice tests — authSlice, healthSlice, statusSlice
├── theme/         MUI theme definition (palette, typography, component overrides)
├── types/         Shared TypeScript interfaces — ApiError, ApiResult, ApiRequestOptions
└── utils/         Pure utility modules — env config, sessionStorage helpers
```

Adding a new domain (e.g. journal entries) follows a consistent pattern: add slice(s) to `store/`, add endpoint functions to `apis/endpoints.ts`, add page component(s) to `pages/`, wire the route into `routes/AppRouter.tsx`.

### 2.2 Page layout (MUI Grid)

- **MUI v9 Grid** is used for multi-region, breakpoint-driven page layout. The unified API uses the `size` prop (for example `size={{ xs: 12, md: 'grow' }}` or numeric column counts). The Grid component only supports **`direction` `row` / `row-reverse`**; vertical stacking is expressed by full-width items (for example two `size={12}` siblings in a container) or by **Stack** where a column flow is clearer.
- **`PageContainer`** (`src/components/PageContainer.tsx`): root width/max-width centering and the title row (title + optional actions) are implemented with nested **Grid** containers and items so the actions column can align end on larger breakpoints and stack on narrow viewports.
- **Dashboard welcome banner**: copy and primary CTA sit in a **Grid** row (`grow` / `auto` from the `sm` breakpoint); the decorative background circle and KPI icon tiles remain **Box** wrappers.
- **Login** (`/login`): full-viewport centering uses a **Grid** container with flex alignment; the sign-in card sits in a responsive **Grid** item (`xs` through `lg` sizes) capped by `maxWidth`; the form remains a **`Box component="form"`** for minimal churn.
- **Theme reference** (`/app/theme`): colour swatches use a **Grid** per group; typography samples use a **Grid** row per variant (label vs sample columns). Radius and elevation demos keep **Box** tiles; **Stack** is still used where the layout is a simple row with wrap—flex wrap and alignment are applied via **`sx`** because MUI v9 **Stack** no longer accepts `flexWrap` / `alignItems` as top-level props.

## 3. Temporary Compromises / Technical Debt

- Cognito sign-in, token refresh, JWKS validation, and production logout semantics are not complete in Phase 1C.
- Axios 401 runtime handling is intentionally a future integration point only; Phase 1D should attach token refresh and only fall back to logout/session expiry when refresh fails.
- Journal-entry CRUD screens are intentionally deferred to the next frontend slice.
- Vite build currently emits a bundle-size warning from the initial UI and charting dependency bundle. Code splitting should be considered when feature routes become heavier.
- ESLint is pinned to the latest compatible 9.x line because the current React Hooks ESLint plugin does not yet accept ESLint 10.

## 4. Validation Results

- `npm run lint`: passed
- `npm run typecheck`: passed
- `npm test`: 4 files / 10 tests passed
- `npm run build`: passed with Vite chunk-size warning

## 4.1 API Client Refactor Addendum

- Refactored the Phase 1C API transport from `fetch` to Axios.
- Preserved the public `apiRequest<T>` / `ApiResult<T>` contract used by endpoint helpers and thunks.
- Added retry tests for retryable failures and non-retry tests for validation/auth-style failures.
- Added explicit frontend dependencies for dashboard chart/icon packages so builds resolve locally instead of from ancestor `node_modules`.

## 4.2 Source Structure Refactor Addendum

The original scaffold used a `features/` grouping (co-locating slice, page, and tests per domain) plus a `shared/` subtree for cross-cutting concerns. This was replaced with the library-by-concern layout described in §2.1.

**What moved and where:**

| Old path | New path |
|---|---|
| `src/shared/api/types.ts` | `src/types/api.ts` |
| `src/shared/api/apiClient.ts` | `src/apis/apiClient.ts` |
| `src/shared/api/endpoints.ts` | `src/apis/endpoints.ts` |
| `src/shared/config/env.ts` | `src/utils/env.ts` |
| `src/shared/hooks/redux.ts` | `src/hooks/redux.ts` |
| `src/shared/theme/theme.ts` | `src/theme/theme.ts` |
| `src/shared/components/*` | `src/components/*` |
| `src/layouts/AppShell.tsx` | `src/components/AppShell.tsx` |
| `src/features/auth/AuthBootstrap.tsx` | `src/app/AuthBootstrap.tsx` |
| `src/features/auth/LoginPage.tsx` | `src/pages/LoginPage.tsx` |
| `src/features/auth/RequireAuth.tsx` | `src/routes/RequireAuth.tsx` |
| `src/features/auth/authSlice.ts` | `src/store/authSlice.ts` |
| `src/features/auth/sessionStorage.ts` | `src/utils/sessionStorage.ts` |
| `src/features/health/DashboardPage.tsx` | `src/pages/DashboardPage.tsx` |
| `src/features/health/SystemHealthPage.tsx` | `src/pages/SystemHealthPage.tsx` |
| `src/features/health/healthSlice.ts` | `src/store/healthSlice.ts` |
| `src/features/theme/ThemePage.tsx` | `src/pages/ThemePage.tsx` |
| `src/app/AppRouter.tsx` | `src/routes/AppRouter.tsx` |
| `src/app/store.ts` | `src/store/store.ts` |

All tests (4 files / 10 tests) and TypeScript compilation passed after the refactor with no regressions.

## 4.3 Status Slice Refactor Addendum

Replaced per-component `notistack` calls with a centralised `statusSlice` and a single `StatusController` renderer.

**Motivation:** notification state was scattered across three components (`LoginPage`, `AppShell`, `SystemHealthPage`) as imperative `enqueueSnackbar` calls. Centralising in Redux makes notification and loading state visible in DevTools, testable via store dispatch, and consistent across all future pages without any per-component setup.

**New slice — `src/store/statusSlice.ts`:**

| Action | Payload | Effect |
|---|---|---|
| `USER_MESSAGE` | `{ message: string, type: 'ERROR' \| 'INFO' \| 'SUCCESS' \| 'WARNING' }` | Sets the active snackbar message |
| `CLOSE_MESSAGE` | — | Clears the active message |
| `START_LOADING` | `{ showBackdrop?: boolean, backdropMessage?: string }` | Marks loading active; optionally shows a full-screen backdrop |
| `END_LOADING` | — | Clears loading state |

The `type` values map directly to MUI `Alert` severity. The `LOGOUT` full-state reset in `rootReducer` automatically clears `status` state; `USER_MESSAGE` is dispatched *after* `LOGOUT` in `AppShell` so the "Signed out" toast survives the reset.

**New component — `src/components/StatusController.tsx`:**
- Renders a MUI `Snackbar` (bottom-right, 4200 ms auto-hide) wrapping a filled `Alert`; `onClose` dispatches `CLOSE_MESSAGE`.
- Renders a MUI `Backdrop` with `CircularProgress` and optional message text when `loading.active && loading.showBackdrop`.
- Mounted once inside `AppProviders` immediately after `ThemeProvider`; no prop drilling required.

**Removed:** `notistack` dependency (`SnackbarProvider`, `useSnackbar`, `enqueueSnackbar`) removed from all source files and `package.json`.

**What changed in existing files:**

| File | Change |
|---|---|
| `store/store.ts` | Added `status: statusReducer` to `combineReducers` |
| `test/renderWithStore.tsx` | Added `statusReducer` to test store |
| `app/AppProviders.tsx` | Replaced `<SnackbarProvider>` with `<StatusController />` |
| `pages/LoginPage.tsx` | `enqueueSnackbar` → `dispatch(USER_MESSAGE(...))` |
| `components/AppShell.tsx` | `enqueueSnackbar` → `dispatch(USER_MESSAGE(...))` |
| `pages/SystemHealthPage.tsx` | `enqueueSnackbar` → `dispatch(USER_MESSAGE(...))` |

## 4.4 Action Creator Naming Convention

All Redux action creators (both thunks and slice actions) are exported in **SCREAMING_SNAKE_CASE**. This makes every `dispatch(...)` call site immediately recognisable as a state-mutation point and distinguishes actions from selectors, hooks, and component functions.

**Rule:** any function intended to be passed to `dispatch()` is named in uppercase with underscores.

```ts
// slice actions (destructured with alias)
export const { logout: LOGOUT, userMessage: USER_MESSAGE } = mySlice.actions;

// async thunks
export const FETCH_DATABASE_HEALTH = createAsyncThunk(...);
```

**Examples at call sites:**

```ts
dispatch(LOGOUT());
dispatch(USER_MESSAGE({ message: 'Saved', type: 'SUCCESS' }));
void dispatch(BOOTSTRAP_SESSION());
const result = await dispatch(LOGIN_WITH_DEV_TOKEN(token));
if (LOGIN_WITH_DEV_TOKEN.fulfilled.match(result)) { ... }
```

**Current action inventory:**

| Slice | Action creators |
|---|---|
| `authSlice` | `BOOTSTRAP_SESSION`, `LOGIN_WITH_DEV_TOKEN`, `LOGOUT`, `CLEAR_AUTH_ERROR`, `SET_TOKEN_FOR_TEST` |
| `healthSlice` | `FETCH_DATABASE_HEALTH`, `CLEAR_HEALTH_STATE` |
| `statusSlice` | `USER_MESSAGE`, `CLOSE_MESSAGE`, `START_LOADING`, `END_LOADING` |

The internal `createSlice` reducer keys (camelCase) and the Redux DevTools action type strings (e.g. `auth/logout`) are unaffected — only the exported JavaScript binding names change.

## 5. Recommended Next Implementation Step

Start Phase 1D authentication before building protected accounting workflows:

- Replace development bearer-token login with real Cognito username/password sign-in.
- Add token refresh handling through the existing Axios 401 runtime hook.
- Replace scaffold backend JWT decode/mock fallback with verified Cognito/JWKS validation or API Gateway JWT authorizer claims.
- Preserve the Phase 1C API client, Redux, route guard, and status-message conventions.
