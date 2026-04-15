# BookOne — Bank Feed Import & Classification Pipeline

## 1. Purpose

The bank feed import pipeline is responsible for:

- Connecting to external financial institutions via Teller
- Importing bank and credit card transactions
- Normalizing provider payloads into BookOne’s internal schema
- Storing imported transactions in a pending state
- Applying deterministic classification rules
- Optionally invoking a suggestion engine later
- Presenting transactions for user review
- Converting approved items into posted journal entries

Imported transactions do NOT affect the ledger directly.  
Only posted JournalEntries affect the GL.

---

## 2. Design Principles

### 2.1 Imported transactions are not the ledger
Bank feeds are evidence, not accounting truth.

### 2.2 Import → Classify → Post
These stages are strictly separated.

### 2.3 Deterministic-first
MVP must work without AI.

### 2.4 User control
Nothing hits the GL without explicit user action.

### 2.5 Idempotency
Duplicate imports must be prevented.

### 2.6 Auditability
Every stage must be traceable.

---

## 3. Pipeline Stages

1. Connect financial account  
2. Fetch transactions from Teller  
3. Normalize data  
4. Deduplicate  
5. Store as ImportedTransaction (pending)  
6. Apply rules  
7. Create classification proposal  
8. Present for review  
9. User edits (if needed)  
10. User posts → JournalEntry created  
11. Link ImportedTransaction to JournalEntry  
12. Audit logged  

---

## 4. Core Objects

### 4.1 ImportedTransaction

| Field | Type |
|------|------|
| id | UUID |
| organization_id | UUID |
| financial_account_id | UUID |
| external_transaction_id | VARCHAR |
| provider_transaction_hash | VARCHAR |
| transaction_date | DATE |
| posted_date | DATE |
| amount | DECIMAL |
| currency | VARCHAR |
| description_raw | TEXT |
| description_normalized | TEXT |
| direction | ENUM |
| status | ENUM |
| review_status | ENUM |
| clearing_status | ENUM |
| rule_match_id | UUID |
| suggestion_source | ENUM |
| linked_journal_entry_id | UUID |
| metadata_json | JSONB |
| imported_at | TIMESTAMP |
| updated_at | TIMESTAMP |

---

### 4.2 Classification Proposal

| Field | Type |
|------|------|
| id | UUID |
| organization_id | UUID |
| imported_transaction_id | UUID |
| source | ENUM |
| confidence_score | FLOAT |
| proposed_entry_type | VARCHAR |
| proposed_primary_gl_account_id | UUID |
| proposed_vendor_id | UUID |
| proposed_customer_id | UUID |
| proposed_lines_json | JSONB |
| explanation | TEXT |
| flags_json | JSONB |
| created_at | TIMESTAMP |

---

### 4.3 DeterministicRule

| Field | Type |
|------|------|
| id | UUID |
| organization_id | UUID |
| name | VARCHAR |
| priority | INT |
| is_active | BOOLEAN |
| match_type | VARCHAR |
| match_operator | VARCHAR |
| match_value | TEXT |
| amount_min | DECIMAL |
| amount_max | DECIMAL |
| financial_account_id | UUID |
| direction | VARCHAR |
| result_entry_type | VARCHAR |
| result_gl_account_id | UUID |
| result_vendor_id | UUID |
| result_customer_id | UUID |
| result_lines_json | JSONB |
| auto_apply | BOOLEAN |
| created_at | TIMESTAMP |
| updated_at | TIMESTAMP |

---

## 5. Lifecycle States

### ImportedTransaction Status
- pending
- classified
- posted
- ignored

### Review Status
- unreviewed
- suggested
- user_edited
- approved

---

## 6. Import Flow

### 6.1 Account connection
- Create FinancialAccount  
- Store provider metadata  
- Initialize sync state  

### 6.2 Fetch transactions
- Use sync cursor  
- Fetch from Teller  
- Normalize  
- Deduplicate  
- Store  

---

## 7. Normalization

Normalize:
- Amount (signed)
- Direction
- Description (raw + normalized)
- Dates
- Provider metadata

---

## 8. Idempotency

Use:
- external_transaction_id  
- fallback hash  

Prevent duplicate inserts.

---

## 9. Deterministic Classification

Order:
1. Account-specific exact match  
2. Global exact match  
3. Normalized text  
4. Regex  
5. Amount patterns  
6. Fallback  

---

## 10. Suggestion Interface

```json
{
  "source": "rule",
  "confidence_score": 0.96,
  "primary_gl_account_id": "uuid",
  "vendor_id": "uuid",
  "customer_id": null,
  "proposed_lines": [],
  "explanation": "...",
  "flags": []
}
```

---

## 11. Review Queue

User sees:
- date  
- amount  
- description  
- account  
- suggestion  
- confidence  

User actions:
- accept & post  
- edit & post  
- ignore  
- split  

---

## 12. Posting Flow

1. Build JournalEntry  
2. Validate balance  
3. Save as posted  
4. Link transaction  
5. Audit log  

---

## 13. Learning from User Corrections

Support:
- manual “save as rule”  

Future:
- auto-learning  

---

## 14. AI Integration (Future)

Flow:
Rules → fallback to AI → user review → post  

AI never posts directly.

---

## 15. Architecture Split

Aurora:
- imported transactions  
- rules  
- proposals  
- journal entries  

DynamoDB:
- sync state  
- workflow state  

---

## 16. Failure Handling

- Sync failures retry safely  
- Classification failures remain pending  
- Posting failures rollback  

---

## 17. MVP Scope

### In scope
- import  
- normalization  
- rules  
- review  
- posting  

### Out of scope
- AI  
- advanced matching  
- reconciliation  

---

## 18. Key Invariants

1. Imported data ≠ ledger  
2. Only posted JEs affect balances  
3. No duplicates  
4. Full audit trail  

---

## End of Document
