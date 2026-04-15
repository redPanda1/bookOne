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
- Redux + thunks
- MUI

### Structure
- features/
- components/
- layouts/
- services/api/
- store/

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

## End of Document
