# BookOne — Frontend Application Architecture & Screen Flows

## 1. Purpose

This document defines how users interact with BookOne through the frontend application.

It covers:
- application shell and navigation
- primary screens and user flows
- Redux-oriented frontend structure
- UX principles for accounting workflows

---

## 2. Design Principles

- Clean, modern, minimalist UI (admin-style)
- Explicit accounting actions (no hidden behavior)
- Table-first design
- Panel-based editing (not spreadsheet-heavy)
- Show work that needs attention

---

## 3. Application Shell

### Layout
- Left-hand navigation
- Top bar (context, user, sync status)
- Main content area

---

## 4. Navigation

- Dashboard
- Bank Feeds
- Journal Entries
- Chart of Accounts
- Customers
- Vendors
- Rules
- Reports
- Reconciliation
- Settings

---

## 5. Frontend Architecture

### Stack
- React + TypeScript
- Vite SPA
- Redux Toolkit + thunks
- React Router
- MUI
- Redux-backed MUI status notifications

### Structure
- `src/app` — app providers and auth bootstrap wiring
- `src/apis` — API client, endpoint helpers, typed API error/result conventions
- `src/components` — app shell plus reusable page, card, loading, error, status, and empty-state primitives
- `src/hooks` — typed Redux hooks
- `src/pages` — route-level page components
- `src/routes` — router definition and protected route guards
- `src/store` — Redux store, slices, thunks, and slice tests
- `src/theme` — MUI theme and design tokens
- `src/types` — shared TypeScript interfaces
- `src/utils` — environment parsing and pure utility modules

---

## 6. Redux Slices

- session
- bankFeeds
- journalEntries
- accounts
- customers
- vendors
- rules
- reports
- reconciliation
- ui

---

## 7. Primary Screens

### Dashboard
- pending transactions
- unmatched items
- draft entries
- quick links

---

### Bank Feeds (Review Queue)

Split panel layout:

Left:
- transaction list

Right:
- detail panel (account, memo, actions)

Actions:
- post
- ignore
- edit

---

### Journal Entries

- JE list
- JE detail/edit screen
- draft vs posted states
- line-based editing
- balance validation

---

### Chart of Accounts

- account table
- create/edit accounts
- numbering visible

---

### Customers / Vendors

- simple CRUD tables
- lightweight detail views

---

### Rules

- rule list
- simple form creation
- triggers + actions

---

### Reports

- P&L (monthly table)
- Balance Sheet
- drill-down support

---

### Reconciliation

- focus on bank/credit card matching
- match to existing JE
- create JE if needed

---

## 8. Core Flows

### Transaction Review
- select transaction
- review suggestion
- edit or post

### Manual Journal Entry
- create JE
- add lines
- post

### Rule Creation
- create rule manually
- optional “save as rule”

### Reporting
- view reports
- drill down

---

## 9. Interaction Patterns

- explicit actions (post, reverse, match)
- status chips
- inline validation errors

---

## 10. Routing

- /login
- /app
- /app/dashboard
- /app/system-health
- /dashboard
- /bank-feeds
- /journal-entries
- /journal-entries/:id
- /gl-accounts
- /customers
- /vendors
- /rules
- /reports/*
- /reconciliation

---

## 11. MVP Priorities

1. Bank Feeds
2. Journal Entries
3. Reports
4. Chart of Accounts
5. Rules
6. Reconciliation
7. Customers/Vendors
8. Dashboard

---

## 12. Key Invariants

- Review queue is central
- Reports are table-first
- No optimistic accounting updates
- UI remains clean and minimal

---

## 13. Phase 1C Frontend Shell Foundation

Phase 1C establishes frontend shell conventions only. It does not implement full bookkeeping screens.

### Auth / Session

- Login uses a development bearer-token scaffold until Cognito sign-in is implemented.
- The bearer token is persisted in `sessionStorage` only.
- User and organization metadata are kept in Redux memory and rehydrated from `GET /session`.
- Logout clears persisted token and Redux state.
- Phase 1D Cognito username/password sign-in and token refresh should replace token acquisition without changing API callers.

### API Pattern

- All backend calls go through `src/apis`.
- The shared API client is based on Axios so headers, retries, error normalization, and future token refresh are controlled in one place.
- API calls return `ApiResult<T>`:
  - success: `{ ok: true; data: T }`
  - failure: `{ ok: false; error: ApiError }`
- `ApiError` includes `kind`, `status`, `message`, and optional `details`.
- Backend `{"message": "..."}` and NYA-compatible `{"errorMessage": "..."}` responses are normalized into `ApiError.message`.
- Retry behavior is centralized for network failures, HTTP 408, and retryable 5xx responses; validation, auth, not-found, and conflict responses are not retried.
- Thunks use `rejectWithValue<ApiError>`.
- Async slice state uses `idle`, `loading`, `succeeded`, and `failed`.

### Theme / UI

- The UI uses a NiceAdmin-inspired admin shell with left navigation, top bar, and card-based content.
- Primary palette centers on deep green/deep teal values such as `#0f3e38` and `#165a50`.
- Onest is loaded from Google Fonts and configured as the primary MUI typography font.
- Cards and buttons use restrained radius values of `8px` or less.
- Shared layout primitives should be used before adding feature-specific layout code.
- Page-level responsive columns favor **MUI Grid** (`PageContainer`, feature pages); the authenticated **AppShell** stays a flex **Box** sidebar + main column; small decorative or single-purpose wrappers may still use **Box** or **Stack**.

### Protected Reference Page

- `/app/system-health` is the Phase 1C reference backend-connected screen.
- It calls protected `GET /health/db` through the shared API client.
- It demonstrates loading, success, error, auth-header injection, thunk state, and notification patterns.

---

## 14. Phase 1D Authentication Foundation

Phase 1D replaces the development bearer-token login with real Cognito-backed authentication before protected accounting workflows are expanded.

### Scope

- Add a production-shaped login screen using Cognito username/password authentication.
- Store only the minimum token material needed by the SPA, preferring memory plus `sessionStorage` for session-scoped persistence.
- Wire the existing Axios 401 runtime hook to attempt token refresh once, retry the failed request when refresh succeeds, and clear session state only when refresh fails.
- Keep `GET /session` as the frontend bootstrap contract for normalized user and organization metadata.
- Replace scaffold backend JWT behavior with verified Cognito/JWKS validation or API Gateway JWT authorizer claims.

### Out of Scope

- Journal-entry CRUD screens.
- Role/permission administration UI.
- Multi-factor authentication policy design beyond preserving compatibility with Cognito challenge handling.

---

## End of Document
