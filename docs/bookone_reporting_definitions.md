# BookOne — Reporting Definitions

## 1. Purpose

The Reporting layer defines how accounting data is:

- structured into financial statements  
- aggregated across time periods  
- presented in a user-friendly format  
- derived from the underlying double-entry ledger  

---

## 2. Design Principles

- Reports derive only from posted JournalEntries  
- No mutation of accounting data  
- Presentation is separate from storage  
- Deterministic calculations  
- Minimal MVP scope  

---

## 3. Chart of Accounts & Numbering

| Range | Category |
|------|--------|
| 1xxx | Assets |
| 2xxx | Liabilities |
| 3xxx | Equity |
| 4xxx | Revenue |
| 5xxx | Direct Costs |
| 6xxx | Expenses |
| 7xxx | Depreciation |
| 8xxx | Other Income / Expense |
| 9xxx | Other / Unreconciled |

---

## 4. Profit & Loss

### Structure

- Sales  
- Direct Costs  
- Gross Profit  
- Expenses  
- Depreciation  
- Other Income  
- Other Expense  
- Net Profit  

---

### Monthly Reporting

Columns by month, plus totals.

---

### Comparative Report

- Current Year Total  
- Prior Year Total  

---

## 5. Balance Sheet

### Assets
- Bank  
- Accounts Receivable  
- Current Assets  
- Non-Current Assets  
- Fixed Assets  

### Liabilities
- Credit Card  
- Accounts Payable  
- Current Liabilities  
- Non-Current Liabilities  

### Equity
- Equity  
- Retained Earnings  
- Current Year Earnings  

---

## 6. Retained Earnings

Calculated as prior-year accumulated profit.

---

## 7. Period Handling

- P&L: date range  
- Balance Sheet: as-of date  

---

## 8. Sign Conventions

- All values displayed as positive  
- Sign normalization handled in reporting layer  

---

## 9. Drill Down

- Report → JournalEntry → JournalLines  

---

## 10. Data Source Rules

Include:
- Posted JournalEntries  

Exclude:
- Draft entries  
- Imported transactions  

---

## 11. MVP Scope

### In Scope
- P&L  
- Balance Sheet  
- Monthly view  
- Year comparison  

### Out of Scope
- Cash Flow  
- Budgeting  
- Multi-entity  

---

## 12. Key Invariants

- Reports must reconcile to ledger  
- Balance Sheet must balance  
- Retained earnings derived  
- No unposted data included  

---

## End of Document
