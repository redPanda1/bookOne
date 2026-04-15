# BookOne — Architecture & Development Plan

## Overview

BookOne is a personal finance and lightweight accounting application designed to provide core bookkeeping capabilities similar to a simplified QuickBooks or Xero. The system will support bank feed ingestion, double-entry accounting, rule-based and AI-assisted transaction classification, and financial reporting.

---

## 1. MVP Scope

### Included
- User authentication and authorization
- Organization ("book") management
- Bank and credit card account connection (via Teller)
- Transaction ingestion and normalization
- Chart of Accounts (GL Accounts)
- Vendors and Customers
- Deterministic rule engine
- AI-assisted transaction classification
- Manual journal entries
- Double-entry ledger system
- Account balances
- Profit & Loss report (by period)
- Balance Sheet (as-of date)
- Basic audit trail

### Excluded (Phase 2+)
- Invoicing (A/R workflows)
- Bill pay (A/P workflows)
- Payroll
- Sales tax handling
- Multi-currency
- Budgeting/forecasting
- Fixed assets/depreciation
- Receipt OCR / attachments
- Full reconciliation workflows

---

## 2. System Architecture

### Frontend
- React + TypeScript
- Redux + Thunks for state management
- Component library (e.g., MUI)
- Responsibilities:
  - UI rendering
  - Workflow orchestration
  - Minimal business logic

### Backend
- AWS API Gateway + Lambda (Python)
- Event-driven processing via EventBridge
- Async pipelines via SQS

### Database Architecture: Hybrid Model

#### Aurora PostgreSQL (System of Record)
Used for durable, relational, reportable accounting data.

Stores:
- Users
- Organizations and memberships
- GL accounts / chart of accounts
- Financial accounts (bank / credit card definitions)
- Vendors
- Customers
- Imported normalized transactions
- Journal entries
- Journal lines
- Posting batches
- Audit trail
- Balance snapshots / reporting tables

#### DynamoDB (Operational / Workflow State)
Used for high-write, stateful, event-driven workflow and orchestration data.

Stores:
- Teller sync state
- Webhook processing state
- Deduplication keys
- Transaction review queue state
- AI classification job state
- Rule engine runtime cache
- Background job coordination state
- Notifications / alerts
- Lightweight activity feeds

### Supporting Services
- Cognito (authentication)
- S3 (exports, documents)
- Secrets Manager + KMS (secure storage)

### Architectural Principle

**If data affects accounting truth, reporting truth, or audit truth, it belongs in Aurora.**  
**If data affects workflow progress, processing state, queue state, or ephemeral operational flow, it belongs in DynamoDB.**

---

## 3. Core Domains

### Identity & Access
- Users
- Organizations (Books)
- Roles (Owner, Admin, User)
- JWT-based authentication

### Accounting Engine
- GL Accounts
- Journal Entries
- Journal Lines
- Ledger postings

**Invariant:**
All transactions must balance:

Debits = Credits

---

### Operational Entities
- Financial Accounts (Bank/Credit Card)
- Vendors
- Customers

---

### Bank Feed Ingestion Pipeline

1. Connect account via Teller
2. Store encrypted access credentials
3. Fetch transactions
4. Normalize to internal schema
5. Deduplicate
6. Apply deterministic rules
7. Apply AI classification
8. Generate proposed postings
9. User review (if required)
10. Commit to ledger

---

### Rules & AI Decisioning

#### Deterministic Rules
- Merchant-based classification
- Amount-based matching
- Known recurring transactions
- Transfer detection

#### AI Layer
- Suggest GL account
- Suggest vendor
- Detect patterns
- Provide confidence scores
- Generate explanations

#### Human-in-the-loop
- User approval/edit
- Feedback loop into rules

---

### Reporting

#### Profit & Loss
- Time-bound activity
- Income vs expenses

#### Balance Sheet
- Point-in-time balances
- Assets, liabilities, equity

---

## 4. Data Model (High Level)

### Identity
- User
- Organization
- OrganizationUser

### Accounting (Aurora)
- GLAccount
- FinancialAccount
- Vendor
- Customer
- ImportedTransaction
- JournalEntry
- JournalLine
- PostingBatch
- AuditLog
- BalanceSnapshot

### Workflow / Operational State (DynamoDB)
- SyncState
- WebhookEvent
- DedupeKey
- ReviewQueueItem
- AIJobState
- RuleRuntimeCache
- BackgroundJobState
- Notification
- ActivityFeedItem

### Rules
- DeterministicRule (durable business configuration in Aurora)
- Rule runtime/cache state (DynamoDB)

---

## 5. Key Workflows

### Onboarding
- Create account
- Create organization
- Seed chart of accounts
- Connect bank account

### Transaction Processing
- Import
- Classify
- Review
- Post to ledger

### Manual Entry
- Create journal entry
- Validate balance
- Commit to ledger

### Reporting
- Generate P&L
- Generate Balance Sheet

### Corrections
- Edit unposted transactions
- Reverse/adjust posted entries

---

## 6. AI Design Principles

AI should:
- Suggest, not decide autonomously
- Provide structured outputs
- Include confidence + reasoning

AI should NOT:
- Directly post transactions without validation
- Create unconstrained journal entries

Example Output Schema:
```
{
  "suggested_gl_account_id": "...",
  "suggested_vendor": "...",
  "confidence": 0.87,
  "reasoning": "...",
  "flags": []
}
```

---

## 7. Security Considerations

- Encrypt all sensitive data
- Secure token storage
- Strict IAM roles
- Tenant isolation
- Full audit logging
- Avoid sensitive data leakage in logs

---

## 8. Testing Strategy

### Unit Tests
- Ledger balancing
- Rule engine
- Date logic

### Integration Tests
- Teller ingestion
- Posting pipeline

### Contract Tests
- API payloads
- AI outputs

### End-to-End
- Core user journeys

---

## 9. Development Phases

### Phase 0: Design
- Data model
- Ledger rules
- Reporting definitions

### Phase 1: Foundation
- Auth
- Org model
- Basic UI

### Phase 2: Accounting Core
- Chart of accounts
- Journal entries
- Ledger

### Phase 3: Bank Feeds
- Teller integration
- Import pipeline

### Phase 4: Rules & AI
- Rule engine
- AI suggestions

### Phase 5: Reporting
- P&L
- Balance Sheet

### Phase 6: Hardening
- Audit
- Performance
- Error handling

---

## 10. Hybrid Database Design Considerations

### Why Hybrid Instead of DynamoDB-Only

Accounting systems are naturally relational and reporting-heavy. A pure DynamoDB design would require substantial denormalization, precomputed aggregates, and careful access-pattern engineering for financial reporting.

Aurora PostgreSQL is a better fit for:
- Relational accounting entities
- Double-entry ledger modeling
- Historical reporting
- Auditability
- Corrections and reversals
- Future expansion of accounting features

DynamoDB is a better fit for:
- Sync cursors and ingestion state
- Event-driven workflow coordination
- Review queues
- AI job lifecycle state
- Idempotency / deduplication markers
- Alerting and notification state

### Practical Guidance

- Aurora is the financial source of truth.
- DynamoDB supports orchestration and workflow acceleration.
- Imported transaction evidence should live in Aurora.
- Import/sync progress and dedupe mechanics should live in DynamoDB.

This hybrid approach minimizes relational strain on DynamoDB while preserving DynamoDB's strengths for operational workflows.

---

## 11. Critical Success Factors

1. Strong ledger model
2. Reliable ingestion pipeline
3. Transparent rules + AI system
4. Accurate financial reporting

---

## 12. Common Pitfalls

- Treating bank data as the ledger
- Weak double-entry enforcement
- Over-reliance on AI
- Lack of audit trail
- Poor tenant isolation

---

## 13. Next Steps

Proceed with detailed design documents in order:

1. MVP Scope (refinement)
2. Core Accounting Data Model
3. Ledger Posting Rules
4. Bank Feed Import Pipeline
5. Rules & AI Decision Engine
6. Reporting Definitions

---

**End of Document**

