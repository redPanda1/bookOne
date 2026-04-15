# BookOne — Phase 3, 4, 5, 6 & 7 Detailed Delivery Plan

## Overview

This document provides a detailed, execution-ready plan for the second half of the BookOne MVP delivery sequence:

- Phase 3 — Bank Feed Import
- Phase 4 — Review Queue & Posting from Imported Transactions
- Phase 5 — Rules & Suggestion Engine
- Phase 6 — Reconciliation & Matching
- Phase 7 — Hardening, UX Refinement & MVP Readiness

The goal is to move from a working internal accounting core to a usable, bank-driven product workflow.

---

# Phase 3 — Bank Feed Import

## Goal

Connect external bank and credit card accounts and import transactions into BookOne without yet posting them to the ledger.

At the end of this phase, the system should be able to:
- connect a financial account
- trigger sync
- fetch transactions from Teller
- normalize incoming data
- deduplicate repeated syncs
- store imported transactions in a pending state
- show imported transactions in the UI

This phase is about **ingestion**, not classification or posting.

---

## Scope

### In Scope
- FinancialAccount model and CRUD
- Teller connection metadata
- Manual sync
- Scheduled sync
- Sync job state in DynamoDB
- ImportedTransaction table
- Normalization and deduplication
- Read-only imported transaction list in the frontend

### Out of Scope
- Classification proposals
- Posting imported transactions
- Rules engine
- Reconciliation
- AI
- Webhook-driven sync as required functionality

---

## Database (Aurora)

### financial_accounts

Recommended fields:
- id
- organization_id
- name
- type
- gl_account_id
- external_provider
- external_account_id
- currency
- is_active
- created_at
- updated_at

### imported_transactions

Recommended fields:
- id
- organization_id
- financial_account_id
- external_transaction_id
- provider_transaction_hash
- transaction_date
- posted_date
- amount
- currency
- description_raw
- description_normalized
- direction
- status
- review_status
- clearing_status
- linked_journal_entry_id
- metadata_json
- imported_at
- updated_at

### Suggested initial status values

#### status
- pending
- ignored

#### review_status
- unreviewed

#### clearing_status
- pending
- cleared

---

## Operational State (DynamoDB)

### sync_jobs

Suggested fields:
- job_id
- organization_id
- financial_account_id
- status
- started_at
- completed_at
- error_message
- sync_cursor
- records_fetched
- records_inserted

### status values
- queued
- running
- succeeded
- failed

This state is operational and should not live in the accounting truth tables.

---

## Backend Implementation

## 1. Financial Accounts module

Build:
- create financial account
- update financial account
- list financial accounts
- validate 1:1 mapping to GL account

### API endpoints
- GET /financial-accounts
- POST /financial-accounts
- GET /financial-accounts/{id}
- PATCH /financial-accounts/{id}

---

## 2. Sync orchestration

Build:
- POST /sync-jobs
- POST /financial-accounts/{id}/sync
- GET /sync-jobs
- GET /sync-jobs/{id}

### MVP sync flow
1. API request triggers sync job
2. Job record created in DynamoDB
3. Worker Lambda fetches transactions from Teller
4. Normalize payloads
5. Deduplicate
6. Insert imported transactions into Aurora
7. Update job status in DynamoDB

---

## 3. Normalization logic

Normalize at least:
- signed amount
- direction
- raw description
- cleaned/normalized description
- transaction date
- posted date if available
- provider transaction identifiers
- pending vs cleared indicator

### Implementation advice
Keep normalization deterministic and small.
Do not try to infer accounting meaning in this phase.

---

## 4. Deduplication logic

Use:
- provider transaction ID where available
- fallback provider_transaction_hash

Hash inputs should include:
- organization_id
- financial_account_id
- amount
- date
- normalized description

### Important
This phase should prevent duplicates from repeated syncs.
Do not build advanced near-duplicate detection yet.

---

## Frontend Implementation

## 1. Financial Accounts screen

Features:
- list financial accounts
- create/edit account
- show mapped GL account
- trigger manual sync
- show last sync status

---

## 2. Imported Transactions list

Read-only table showing:
- date
- description
- account
- amount
- pending/cleared status
- import status

This should live under Bank Feeds but remain read-only in this phase.

---

## Milestone

✅ User can:
- connect or configure a financial account
- trigger sync
- view imported transactions in BookOne

This is your first successful external data ingestion milestone.

---

# Phase 4 — Review Queue & Posting from Imported Transactions

## Goal

Turn imported transactions into posted JournalEntries through a focused review workflow.

At the end of this phase, the user should be able to:
- open a review queue
- inspect imported transaction details
- manually assign an expense/revenue account and memo
- post the transaction into the ledger
- ignore a transaction

This phase is where BookOne becomes a real bookkeeping product.

---

## Scope

### In Scope
- Review queue screen
- Classification proposal persistence
- Manual classification from imported transaction
- Post imported transaction to JE
- Ignore imported transaction
- Link imported transaction to JE
- Audit logging for posting action

### Out of Scope
- Rules engine automation
- AI suggestions
- Matching to existing JEs
- Split-heavy workflows beyond basic support

---

## Database (Aurora)

### classification_proposals

Suggested fields:
- id
- organization_id
- imported_transaction_id
- source
- primary_gl_account_id
- memo
- proposed_lines_json
- flags_json
- created_at
- updated_at

### source values
- user_manual

You can keep this lightweight in MVP.

---

## Backend Implementation

## 1. Imported transaction detail endpoint

Build:
- GET /imported-transactions/{id}

Returns:
- imported transaction
- current proposal if any
- linked journal entry if posted

---

## 2. Update proposal endpoint

Build:
- PATCH /imported-transactions/{id}

Allows user to edit:
- primary_gl_account_id
- memo
- proposed lines (if supporting splits)
- review status

---

## 3. Post imported transaction endpoint

Build:
- POST /imported-transactions/{id}/post

Inside one Aurora transaction:
- load imported transaction
- load proposal
- build JournalEntry
- build JournalLines
- validate balancing
- save JE as posted
- update imported transaction:
  - linked_journal_entry_id
  - status = posted
  - review_status = approved
- insert audit log

### Important
Imported transaction remains source evidence.
It is linked to the JE, not mutated into a JE.

---

## 4. Ignore imported transaction endpoint

Build:
- POST /imported-transactions/{id}/ignore

Behavior:
- status = ignored
- review_status = approved or ignored state if you add one later

---

## Frontend Implementation

## 1. Review Queue screen

Split-panel layout:

### Left panel
List/table showing:
- date
- description
- account
- amount
- review status
- clearing status

### Right panel
Editor showing:
- imported transaction detail
- account selector
- memo field
- optional lines editor
- actions:
  - Post
  - Ignore
  - Save

### UX rules
- keep current row selected as user moves through queue
- make next item easy to open
- show clear confirmation of successful posting

---

## 2. Basic validation UX

Show inline errors for:
- missing account
- imbalanced proposed lines
- transaction already posted
- invalid financial account mapping

---

## Milestone

✅ User can:
- review imported transactions
- classify them manually
- post them into the ledger
- ignore items that should not be posted

This is the **core product milestone**.

---

# Phase 5 — Rules & Suggestion Engine

## Goal

Reduce repetitive manual classification by allowing deterministic rules to prefill transaction treatment.

At the end of this phase, the user should be able to:
- create rules manually
- apply rules to imported transactions
- see auto-applied or suggested classifications
- save a rule from corrected behavior

This phase adds leverage without introducing AI complexity.

---

## Scope

### In Scope
- deterministic_rules table
- rule CRUD
- manual rule creation screen
- rule evaluation against imported transactions
- auto-apply vs suggest-only
- create rule from reviewed transaction

### Out of Scope
- AI
- silent auto-learning
- complex boolean logic
- fuzzy confidence systems
- AR/AP classification from bank feeds

---

## Database (Aurora)

### deterministic_rules

Suggested fields:
- id
- organization_id
- name
- is_active
- priority
- trigger_field
- trigger_operator
- trigger_value
- action_gl_account_id
- action_memo
- auto_apply
- created_at
- updated_at

### trigger_field values
- reference
- description
- amount

### trigger_operator values
- contains
- gt
- lt
- eq

---

## Backend Implementation

## 1. Rule CRUD

Build:
- GET /rules
- POST /rules
- GET /rules/{id}
- PATCH /rules/{id}
- POST /rules/{id}/activate
- POST /rules/{id}/deactivate

---

## 2. Rule evaluation service

Algorithm:
1. load active rules for organization
2. sort by priority
3. evaluate first-match wins
4. create or update classification proposal

### Proposal result
Suggested fields:
- source = rule
- primary_gl_account_id
- memo
- auto_applied
- proposed_lines_json

---

## 3. Save-as-rule flow

Build:
- POST /rules/from-transaction/{importedTransactionId}

Behavior:
- prefill trigger field/value from imported transaction
- prefill action account and memo from current approved classification
- user reviews and saves

---

## Frontend Implementation

## 1. Rules screen

Table columns:
- name
- trigger field
- operator
- value
- action account
- auto-apply
- active
- priority

Form fields:
- name
- trigger field
- operator
- trigger value
- target account
- memo
- auto-apply
- priority
- active

---

## 2. Review Queue enhancement

Add:
- suggestion badges
- source indicator (manual vs rule)
- ability to open “Save as rule”

---

## Milestone

✅ User can:
- define classification rules
- see transactions prefilled from rules
- save recurring logic as reusable rules

This is the milestone where BookOne starts to feel smart.

---

# Phase 6 — Reconciliation & Matching

## Goal

Allow imported bank and credit card transactions to be matched to already-existing posted JournalEntries.

At the end of this phase, the user should be able to:
- see unmatched imported transactions
- match an imported transaction to an existing JE
- confirm that imported activity has been accounted for
- keep unmatched items visible

This phase is deliberately limited to bank/credit card matching only.

---

## Scope

### In Scope
- bank and credit card imported transaction matching
- explicit match to existing JE
- unmatched/matched/ignored views
- reconciliation screen

### Out of Scope
- AR/AP application surfaces
- statement reconciliation
- tolerance matching
- fuzzy match engine
- writeoff automation

---

## Backend Implementation

## 1. Match imported transaction endpoint

Build:
- POST /imported-transactions/{id}/match

Input:
- target_journal_entry_id

Validation:
- imported transaction must not already be matched
- JE must be posted
- amount must match exactly
- financial account must align with JE bank/credit-card side

### Behavior
Inside transaction:
- set linked_journal_entry_id
- status = matched
- insert audit log

---

## 2. Reconciliation query endpoints

Build:
- GET /reconciliation/imported-transactions?status=unmatched
- GET /reconciliation/imported-transactions?status=matched

Returns:
- imported transaction
- account
- amount
- description
- linked JE if applicable

---

## Frontend Implementation

## 1. Reconciliation screen

Table-first layout.

Columns:
- date
- description
- financial account
- amount
- status
- linked JE

Actions:
- match to JE
- view JE
- create JE if missing
- ignore if appropriate

### UX guidance
This screen is for “already accounted for, now link it.”
It should not duplicate the full review queue.

---

## 2. Match dialog / panel

Allow user to:
- search existing posted JEs
- filter by amount
- filter by date if helpful
- select a JE and confirm match

### Keep it simple
No fuzzy recommendations in MVP.

---

## Milestone

✅ User can:
- identify unmatched imported transactions
- match them to already-posted JournalEntries
- maintain visibility over what is accounted for vs unresolved

This is the milestone where operational trust starts to improve.

---

# Phase 7 — Hardening, UX Refinement & MVP Readiness

## Goal

Make the system stable, understandable, and ready for real usage.

At the end of this phase, the MVP should:
- behave reliably
- communicate errors clearly
- feel efficient in repetitive workflows
- have enough observability to debug issues
- be ready for pilot users

---

## Scope

### In Scope
- validation hardening
- error handling improvements
- loading/empty/error UI states
- performance review
- audit visibility
- sync job visibility
- UI polish
- basic permissions hardening
- test coverage on critical flows

### Out of Scope
- major new features
- AI
- multi-currency
- invoice/bill guided workflows
- advanced analytics dashboards

---

## Backend Implementation

## 1. Validation hardening

Review all critical workflows:
- JE posting
- imported transaction posting
- rule evaluation
- matching
- sync failure handling

Ensure explicit validation errors for:
- already posted items
- invalid status transitions
- imbalanced entries
- closed-period constraints when added
- duplicate match attempts

---

## 2. Observability

Add or tighten:
- structured logs
- correlation IDs
- sync job status tracing
- audit logs for all material actions
- operational error notifications if desired

---

## 3. Performance review

Check:
- imported transaction listing queries
- report aggregation queries
- JE detail load speed
- rules query performance

Add:
- indexes
- pagination where needed
- sensible filter defaults

Do not prematurely build caching layers unless proven necessary.

---

## Frontend Implementation

## 1. UX polish

Improve:
- spacing and hierarchy
- inline validation clarity
- success state messaging
- empty states
- loading states
- keyboard-friendly forms

---

## 2. Workflow acceleration

For repetitive screens like Review Queue:
- preserve current filters
- auto-select next transaction after action
- reduce redundant clicks
- make successful posting feel immediate and clear

---

## 3. Audit visibility

Add lightweight UI access to:
- JE audit history
- imported transaction linkage status
- sync job history

This will help trust and debugging.

---

## QA / Testing

## Minimum critical coverage

### Backend tests
- JE balancing and posting
- reversal creation
- imported transaction posting
- rule first-match logic
- deduplication behavior
- matching logic

### Frontend tests
- JE screen validation
- review queue posting flow
- rules screen save/update flow
- report rendering with expected totals
- reconciliation matching flow

### Manual end-to-end tests
- create account → create JE → post → report updates
- sync account → imported transactions appear
- review queue → post transaction → report updates
- create rule → new import gets prefilled
- match imported transaction to existing JE

---

## Release Readiness Checklist

Before calling MVP ready:

- auth works cleanly
- org scoping is enforced everywhere
- posting flows are transaction-safe
- reports reconcile to ledger
- imported transactions never hit ledger directly
- sync jobs can fail safely and visibly
- no major broken validation paths
- core screens are usable without developer intervention

---

## Milestone

✅ System is ready for controlled pilot use.

That means:
- core accounting workflows are usable
- bank-driven workflow is functional
- trust and visibility are high enough for real feedback

---

# Recommended Build Sequence (Phases 3-7)

## Phase 3 first
Build ingestion before review.

## Phase 4 next
Build review/posting before rules.

## Phase 5 next
Automate what the manual review process already proved.

## Phase 6 next
Add matching only after import/posting workflow is stable.

## Phase 7 continuously
Start hardening early, but concentrate it after core flows exist.

---

# Suggested Timeline

### Phase 3
2–3 weeks

### Phase 4
2–3 weeks

### Phase 5
1–2 weeks

### Phase 6
1–2 weeks

### Phase 7
1–3 weeks, depending on polish level and pilot readiness

---

# Key Rules

1. Do not add AI before deterministic rules are working well.
2. Do not add fuzzy matching before explicit matching is stable.
3. Do not let imported transactions post directly without review.
4. Do not let hardening become an excuse to invent new features.
5. Keep the review queue fast and clean — it is the center of the product.

---

# Practical Next Steps

Once Phase 0, 1 & 2 are underway or complete, the immediate next build steps should be:

## Next Step 1
Implement FinancialAccount + ImportedTransaction tables and APIs

## Next Step 2
Stand up manual sync flow with DynamoDB sync_jobs

## Next Step 3
Build read-only imported transactions list in the frontend

## Next Step 4
Add review queue detail panel and manual posting flow

## Next Step 5
Only after that, add deterministic rule creation and evaluation

This sequencing matters. It prevents rework and keeps the product grounded in real workflows.

---

## End of Document
