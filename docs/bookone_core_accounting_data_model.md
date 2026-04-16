# BookOne — Core Accounting Data Model

## 1. Design Principles

1. **Double-entry is enforced at all times**
   - Every JournalEntry must balance:
     - `SUM(debits) = SUM(credits)`

2. **Aurora is the source of truth**
   - All accounting data is relational and auditable

3. **Separation of concerns**
   - GL Accounts = financial truth
   - Financial Accounts = real-world accounts (bank/credit card)
   - Customers/Vendors = sub-ledger entities

4. **Two-layer account classification**
   - Natural Class → drives accounting behavior
   - Subtype → drives reporting + UI

5. **Audit is append-only**
   - No destructive updates without trace

6. **Period-aware mutability**
   - Draft → editable
   - Posted (open period) → editable with audit
   - Posted (closed period) → immutable (reversal required)

---

## 2. Core Entities Overview

### Identity / Multi-tenancy
- Organization
- All tables include `organization_id`

### Accounting Core
- GLAccount
- FinancialAccount
- Customer
- Vendor
- JournalEntry
- JournalLine
- ImportedTransaction
- AuditLog

---

## 3. Account Model

### 3.1 GLAccount

| Field | Type | Notes |
|------|------|------|
| id | UUID (PK) | |
| organization_id | UUID | tenant isolation |
| code | VARCHAR | e.g. 1000 |
| name | VARCHAR | |
| natural_class | ENUM | Asset, Liability, Equity, Income, Expense |
| subtype | ENUM | see below |
| is_control_account | BOOLEAN | |
| is_system_account | BOOLEAN | |
| is_active | BOOLEAN | |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

#### Subtypes
- Bank
- CreditCard
- CurrentAsset
- NonCurrentAsset
- FixedAsset
- AccountsReceivable
- AccountsPayable
- CurrentLiability
- NonCurrentLiability
- EquityRetainedEarnings
- Sales
- DirectCost
- OperatingExpense
- DepreciationExpense
- OtherIncome
- OtherExpense

---

### 3.2 FinancialAccount

| Field | Type |
|------|------|
| id | UUID |
| organization_id | UUID |
| name | VARCHAR |
| type | ENUM |
| gl_account_id | UUID |
| external_provider | VARCHAR |
| external_account_id | VARCHAR |
| currency | VARCHAR |
| is_active | BOOLEAN |
| created_at | TIMESTAMP |

---

## 4. Customer & Vendor Model

### Customers

| Field | Type |
|------|------|
| id | UUID |
| organization_id | UUID |
| name | VARCHAR |
| ar_control_account_id | UUID |
| is_active | BOOLEAN |
| created_at | TIMESTAMP |

### Vendors

| Field | Type |
|------|------|
| id | UUID |
| organization_id | UUID |
| name | VARCHAR |
| ap_control_account_id | UUID |
| is_active | BOOLEAN |
| created_at | TIMESTAMP |

---

## 5. Journal Entry Model

### JournalEntry

| Field | Type |
|------|------|
| id | UUID |
| organization_id | UUID |
| entry_date | DATE |
| status | ENUM (Draft, Posted) |
| description | TEXT |
| source_type | ENUM |
| source_id | UUID |
| posted_at | TIMESTAMP |
| posted_by | VARCHAR |
| created_at | TIMESTAMP |
| updated_at | TIMESTAMP |

### JournalLine

| Field | Type |
|------|------|
| id | UUID |
| journal_entry_id | UUID |
| organization_id | UUID |
| gl_account_id | UUID |
| debit_amount | DECIMAL |
| credit_amount | DECIMAL |
| customer_id | UUID |
| vendor_id | UUID |
| memo | TEXT |
| created_at | TIMESTAMP |

---

## 6. Imported Transactions

| Field | Type |
|------|------|
| id | UUID |
| organization_id | UUID |
| financial_account_id | UUID |
| external_transaction_id | VARCHAR |
| date | DATE |
| amount | DECIMAL |
| description | TEXT |
| status | ENUM |
| is_cleared | BOOLEAN |
| linked_journal_entry_id | UUID |
| created_at | TIMESTAMP |

---

## 7. Accounting Periods

| Field | Type |
|------|------|
| id | UUID |
| organization_id | UUID |
| start_date | DATE |
| end_date | DATE |
| is_closed | BOOLEAN |

---

## 8. Audit Log

| Field | Type |
|------|------|
| id | UUID |
| organization_id | UUID |
| entity_type | VARCHAR |
| entity_id | UUID |
| action | ENUM |
| before_state | JSONB |
| after_state | JSONB |
| created_at | TIMESTAMP |
| created_by | UUID |

---

## 9. Ledger Invariants

1. Entries must balance  
2. Posted entries remain valid  
3. Valid account references required  
4. Financial accounts map 1:1 to GL  
5. Customer → AR, Vendor → AP  
6. Organization isolation enforced  

---

## 10. Phase 1A Implementation Notes (2026-04-14)

- SQLAlchemy 2.0 ORM implementation now exists for:
  - `Organization`
  - `LedgerAccount`
  - `Entity` (shared customer/vendor abstraction)
  - `FinancialAccount`
  - `JournalEntry`
  - `JournalLine`
- Tenant isolation is implemented via `organization_id` in all master/transactional accounting tables.
- `JournalEntry` schema now includes:
  - `journal_number`
  - `source_type`
  - `source_reference`
  - `status`
- `JournalLine` includes `line_order`, debit/credit precision (`NUMERIC(18,2)`), and single-sided amount constraints.
- Alembic migration `20260414_01_phase1a_core_database_foundation` is the source of truth for this initial relational foundation.

---

## 11. Phase 1B Implementation Notes (2026-04-15)

- Added workflow metadata to `JournalEntry`:
  - `posted_at`
  - `posted_by`
- Added `JournalEntryAuditHistory` model/table to capture posted transition events.
- Service-layer journal workflow now enforces:
  - draft-only edit/post transitions
  - minimum line count and debit-credit balancing at post time
  - ledger account org/active validation for posting
- Posting now commits status transition metadata and audit row in one transaction boundary.

---

## End of Document
