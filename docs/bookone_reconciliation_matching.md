# BookOne — Reconciliation & Matching (Bank / AR / AP)

## 1. Purpose

The Reconciliation & Matching system ensures that:

- imported bank and credit card transactions are linked to posted JournalEntries  
- customer and vendor balances reflect real-world outstanding amounts  
- payments are correctly applied to invoices and bills  
- unmatched items remain visible and explainable  

---

## 2. Design Principles

- Ledger is the source of truth  
- Imported transactions are evidence  
- Matching is explicit (no fuzzy logic)  
- Simplicity over completeness  
- Unmatched items must remain visible  

---

## 3. Scope

### In Scope
- Bank / credit card matching  
- AR/AP application  

### Out of Scope
- Statement reconciliation  
- Automated matching  
- Writeoffs automation  

---

## 4. Bank & Credit Card Matching

### Matching Types
1. During posting (review queue)  
2. Post-hoc matching to existing JournalEntries  

### Constraints
- Exact amount match  
- Same financial account  
- One-to-one mapping  

---

## 5. Imported Transaction Status

- unmatched  
- matched  
- ignored  

---

## 6. AR/AP Open Item Model

### Behavior
- payments can apply to multiple invoices  
- invoices can be partially paid  
- payments can remain unapplied  

---

## 7. Payment Applications Table

| Field | Type |
|------|------|
| id | UUID |
| organization_id | UUID |
| source_journal_line_id | UUID |
| target_journal_line_id | UUID |
| amount | DECIMAL |
| created_at | TIMESTAMP |

---

## 8. Open Item Status

- open  
- partially_applied  
- closed  

---

## 9. Matching Workflow

### Bank Matching
- link imported transaction → JournalEntry  

### AR/AP Matching
- apply payments → invoices/bills  

---

## 10. Writeoffs & Differences

User must:
- create manual JournalEntry  
- then apply/match  

---

## 11. Data Integrity Rules

- No direct ledger impact from imported transactions  
- Matching must be explicit  
- No over-application  
- One-to-one transaction matching  

---

## 12. UI Model

### Bank View
- unmatched transactions  
- matched transactions  
- match/create options  

### AR/AP View
- balances  
- open items  
- apply payments  

---

## 13. Future Extensions

- automated matching  
- tolerance matching  
- reconciliation reports  

---

## 14. Key Invariants

1. Ledger is authoritative  
2. Matching is explicit  
3. AR/AP derived from JournalLines  
4. Unmatched items remain visible  

---

## End of Document
