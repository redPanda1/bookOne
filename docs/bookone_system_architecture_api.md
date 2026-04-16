# BookOne — System Architecture & API Design

## 1. Purpose

This document defines the system architecture and API design for BookOne, translating the accounting domain into an implementable system.

---

## 2. Architecture Principles

- Strong consistency for accounting core (Aurora transactions)
- Modular monolith backend
- Async boundaries outside ledger core
- REST APIs via API Gateway HTTP API
- Tenant context derived from JWT
- Minimal optimistic UI for financial actions

---

## 3. High-Level Architecture

### Frontend
- React + TypeScript
- Redux + thunks

### Backend
- API Gateway HTTP API
- Lambda backend (modular monolith)

### Data
- Aurora PostgreSQL (source of truth)
- DynamoDB (workflow state)

---

## 4. Backend Modules

- Identity / Session
- Chart of Accounts
- Customers / Vendors
- Financial Accounts
- Imported Transactions / Review Queue
- Journal Entries / Posting
- Rules Engine
- Reporting
- Reconciliation / AR/AP
- Sync Orchestration

---

## 5. Async Workers

- Sync runner
- Account sync worker
- Webhook handler (future)
- AI suggestion worker (future)

---

## 6. Sync Model

- Manual trigger via API
- Scheduled via EventBridge
- Optional webhooks later

---

## 7. Transaction Boundaries

All posting actions must run in a single Aurora transaction:

- JournalEntry + JournalLines
- ImportedTransaction linkage
- AuditLog
- Payment applications

---

## 8. Read / Write Model

- Writes → normalized Aurora tables
- Reads → SQL queries/views
- No CQRS for MVP

---

## 9. API Design

REST endpoints, mix of CRUD and workflow actions.

---

## 10. Tenant Model

- Organization derived from JWT
- All queries scoped by organization_id

---

## 11. Frontend State

Redux slices:
- auth
- accounts
- customers/vendors
- transactions
- journalEntries
- rules
- reports
- reconciliation
- syncJobs

---

## 12. Optimistic UI

Allowed:
- UI-only updates

Not allowed:
- posting
- matching
- reconciliation actions

---

## 13. Core API Endpoints

### Session
GET /session

### GL Accounts
GET /gl-accounts  
POST /gl-accounts  
PATCH /gl-accounts/{id}

### Customers / Vendors
GET /customers  
POST /customers  

GET /vendors  
POST /vendors  

### Financial Accounts
GET /financial-accounts  
POST /financial-accounts  
POST /financial-accounts/{id}/sync  

### Imported Transactions
GET /imported-transactions  
POST /imported-transactions/{id}/post  
POST /imported-transactions/{id}/match  
POST /imported-transactions/{id}/ignore  

### Journal Entries
GET /journal-entries  
POST /journal-entries  
PATCH /journal-entries/{id}  
POST /journal-entries/{id}/post  
POST /journal-entries/{id}/reverse  

### Rules
GET /rules  
POST /rules  
PATCH /rules/{id}  

### Reconciliation
POST /payments/applications  

### Reports
GET /reports/profit-and-loss  
GET /reports/balance-sheet  

---

## 14. Backend Layering

- Handler layer
- Service layer
- Repository layer
- Domain validation layer

---

## 15. Error Handling

- Synchronous accounting actions → immediate response
- Async workflows → job-based with DynamoDB tracking

---

## 16. Security

- JWT validation
- org-level scoping
- parameterized queries
- secure secret storage

---

## 17. Deployment

### API Stack
- API Gateway HTTP API
- Lambda
- Aurora
- Cognito

### Async Stack
- EventBridge
- Lambda workers
- DynamoDB

---

## 18. Key Invariants

1. Accounting truth lives in Aurora  
2. All posting uses single DB transactions  
3. No optimistic accounting updates  
4. Org scoping enforced server-side  

---

## End of Document
