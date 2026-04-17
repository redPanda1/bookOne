# BookOne — Phase 0, 1 & 2 Detailed Delivery Plan

## Overview

This document provides a detailed, execution-ready plan for the first MVP phases of BookOne:

- Phase 0 — Foundation
- Phase 1 — Core Ledger
- Phase 1D — Authentication Foundation
- Phase 2 — Reporting

The goal is to move from zero to a functioning accounting system with reporting.

---

# Phase 0 — Foundation

## Goal
Establish a working system with:
- authentication
- backend infrastructure
- database connectivity
- frontend shell

---

## Backend Setup

- API Gateway HTTP API
- Lambda project (modular monolith structure)
- Aurora PostgreSQL connection
- Cognito authentication
- Basic `/session` endpoint

---

## Database

Create initial tables:

### organizations
- id
- name
- created_at

### users (or Cognito mapping)
- id
- email
- created_at

### gl_accounts (empty structure for now)

---

## Frontend

- React + TypeScript app scaffold
- Redux store setup
- App shell:
  - left navigation
  - top bar
- routing structure
- authentication flow

---

## Milestone

User can:
- log in
- see application shell
- navigate between empty pages

---

# Phase 1 — Core Ledger

## Goal
Build a correct accounting engine:
- GL accounts
- Journal Entries
- Posting logic

---

## Database

### gl_accounts

id (uuid)
organization_id
code
name
natural_class
subtype
is_active
created_at
updated_at

---

### journal_entries

id
organization_id
entry_date
description
status (draft/posted)
created_by
created_at
updated_at

---

### journal_lines

id
organization_id
journal_entry_id
gl_account_id
memo
debit_amount
credit_amount
created_at

---

### audit_log

id
organization_id
entity_type
entity_id
action
payload_json
created_at

---

## Backend

### JournalEntryService

- createDraftJE
- updateDraftJE
- postJE
- reverseJE

---

### Posting Logic

Single transaction:
- validate balanced
- update status
- insert audit log

---

### API Endpoints

POST /journal-entries  
PATCH /journal-entries/{id}  
POST /journal-entries/{id}/post  
POST /journal-entries/{id}/reverse  

---

## Frontend

### Chart of Accounts
- list
- create/edit

### Journal Entries
- list page
- edit page
- line editing
- balance indicator
- post button

---

## Milestone

User can:
- create accounts
- create JE
- post JE

---

# Phase 1D — Authentication Foundation

## Goal
Replace the development bearer-token scaffold with real Cognito-backed authentication before expanding protected accounting workflows.

---

## Frontend

- Build a real login screen for Cognito username/password sign-in.
- Preserve the Phase 1C React Router protected route structure.
- Preserve the shared Axios API client and `ApiResult<T>` thunk pattern.
- Store token material only for the browser session.
- Keep user and organization metadata in Redux memory, hydrated through `GET /session`.
- Wire the Axios 401 runtime hook to attempt token refresh once and retry the original request.
- Clear auth state and show a session-expired message only when refresh fails.

---

## Backend / API

- Replace scaffold JWT decode/mock fallback with verified Cognito/JWKS validation or API Gateway HTTP API JWT authorizer claims.
- Keep `GET /session` as the normalized frontend bootstrap endpoint.
- Map Cognito claims to `user.id`, `user.email`, `organization.id`, and `organization.name`.
- Return consistent `401` responses for missing, expired, invalid, or unverifiable tokens.
- Keep tenant scoping tied to verified organization context.

---

## Configuration

- Document required Cognito User Pool, App Client, issuer, region, and audience/client-id settings.
- Add frontend `.env.example` entries for Cognito configuration.
- Add backend environment variables for issuer/audience/JWKS validation if validation is performed in Lambda.

---

## Milestone

User can:
- sign in with a Cognito username and password
- refresh an expired access token without losing the current page
- be redirected to login when refresh fails
- access protected backend endpoints only with verified Cognito identity

---

# Phase 2 — Reporting

## Goal
Generate financial statements from ledger

---

## Backend

### Profit & Loss

Aggregate:
- journal_lines
- grouped by account and month

---

### Balance Sheet

Aggregate:
- journal_lines
- up to as-of date

---

### Retained Earnings

Computed:
- prior year profit/loss

---

### API Endpoints

GET /reports/profit-and-loss  
GET /reports/profit-and-loss/comparison  
GET /reports/balance-sheet  
GET /reports/journal-line-drilldown  

---

## Frontend

### P&L Screen
- monthly table
- grouped rows
- totals

---

### Balance Sheet
- assets
- liabilities
- equity

---

### Drill-down
- click line → journal lines → JE

---

## Milestone

User can:
- view P&L
- view Balance Sheet
- drill into entries

---

# Build Sequence (Recommended)

## Week 1
- backend scaffold
- DB setup
- auth scaffold

## Week 2
- Journal Entry backend
- frontend shell
- real Cognito authentication

## Week 3
- Journal Entry UI
- Chart of Accounts UI
- validations

## Week 4
- reporting backend
- reporting UI

---

# Key Rules

1. Ledger must be correct before anything else  
2. Reports must reconcile exactly  
3. No premature optimization  
4. No bank feeds before ledger + reporting  

---

## End of Document
