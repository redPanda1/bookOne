# BookOne — Ledger Posting Rules

## 1. Design Principles

1. **Only posted entries affect the ledger**
   - Pending data (bank feeds, draft JEs) do NOT impact balances

2. **Posting is atomic**
   - A JournalEntry is either:
     - fully posted and balanced
     - or not in the ledger at all

3. **Double-entry is enforced at post time**
   - Draft entries may be imbalanced
   - Posted entries must satisfy:
     - `SUM(debits) = SUM(credits)`

4. **Subledger abstraction (Customer/Vendor)**
   - User selects Customer/Vendor
   - System enforces correct control account (AR/AP)
   - JournalLine stores both:
     - `gl_account_id`
     - `customer_id` or `vendor_id`

5. **No silent automation**
   - Nothing hits the ledger without an explicit user “save/post”

---

## 2. Posting States

### JournalEntry Status

| Status | Description |
|------|-------------|
| Draft | Editable, may be imbalanced |
| Posted | Balanced, impacts GL |

---

### Imported Transactions

| Status | Description |
|------|-------------|
| Pending | Not yet converted to JournalEntry |
| Posted | Linked to JournalEntry |
| Ignored | Explicitly excluded |

---

## 3. Posting Timing Rules

### Core Rule

**Anything that hits the GL is posted immediately on save**

---

### Behavior by Source Type

| Source Type | Behavior |
|------------|--------|
| Imported Transaction | Exists in pending state only until user converts to JE |
| Manual Journal Entry | Can be saved as Draft or Posted |
| Invoice | Posted on save |
| Vendor Bill | Posted on save |
| Customer Payment | Posted on save |
| Vendor Payment | Posted on save |
| Bank Transfer | Manual JE (MVP) |
| Credit Card Payment | Manual JE (MVP) |
| Reversal | Posted immediately |

---

## 4. Canonical Posting Patterns

### Bank Transaction — Expense
- DR Expense  
- CR Bank  

### Bank Transaction — Income
- DR Bank  
- CR Revenue  

### Customer Invoice
- DR Accounts Receivable (customer_id set)  
- CR Revenue  

### Vendor Bill
- DR Expense (or Asset)  
- CR Accounts Payable (vendor_id set)  

### Customer Payment
- DR Bank  
- CR Accounts Receivable (customer_id set)  

### Vendor Payment
- DR Accounts Payable (vendor_id set)  
- CR Bank  

### Credit Card Spend
- DR Expense  
- CR Credit Card Liability  

### Credit Card Payment
- DR Credit Card Liability  
- CR Bank  

### Bank Transfer (MVP via manual JE)
- DR Destination Bank  
- CR Source Bank  

### Reversal Entry
- Exact inverse of original JE  
- Same accounts  
- Same amounts  
- Opposite debit/credit  

---

## 5. User Override Rules

### Allowed before posting

- Change GL account
- Assign/change Customer or Vendor
- Split lines across multiple accounts
- Modify memo/description
- Adjust entry date (within period rules)

### Not allowed

- Breaking balance on posted entries
- Changing organization_id
- Posting to invalid control account

### Imported Transactions

- Amount cannot be changed
- Classification and splits can be changed

---

## 6. Subledger Rules (Customer / Vendor)

### Customer Posting

If `customer_id` is set:
- GLAccount MUST be Accounts Receivable

### Vendor Posting

If `vendor_id` is set:
- GLAccount MUST be Accounts Payable

---

## 7. Editing Rules

### Draft Entries
- Fully editable
- Can be imbalanced

### Posted Entries (Open Period)
- Editable
- Must remain balanced
- AuditLog must capture before/after state

### Posted Entries (Closed Period)
- Not editable
- Must use reversal + replacement

---

## 8. Reversal Rules

- System generates new JournalEntry
- Debits and credits swapped
- Same accounts and amounts
- Date = original date if period open

---

## 9. Imported Transaction Posting Flow

1. Transaction ingested → stored as Pending  
2. User reviews transaction  
3. User creates JournalEntry  
4. JournalEntry is saved as Posted  
5. ImportedTransaction is linked  

---

## 10. Transfer Handling (MVP)

- No automatic matching
- Handled via manual JournalEntry

---

## 11. Rounding Rules

- Exact equality required
- No auto-balancing lines allowed

---

## 12. Ledger Invariants

1. Posted entries must balance  
2. Draft entries do not affect ledger  
3. Valid GLAccount required  
4. Customer → AR, Vendor → AP  
5. Organization isolation enforced  

---

## End of Document
