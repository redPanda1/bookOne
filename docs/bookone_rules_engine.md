# BookOne — Rules & Suggestion Engine Design

## 1. Purpose

The Rules & Suggestion Engine generates proposed accounting classifications for imported transactions before posting.

For MVP, it is deterministic-first and user-driven.

---

## 2. Design Principles

- Deterministic first (no AI dependency)
- User remains in control
- Keep MVP simple and explicit
- Suggestions are not accounting truth
- Future AI-compatible interface

---

## 3. MVP Scope

### In Scope
- Manual rule creation
- Basic triggers:
  - description contains text
  - reference contains text
  - amount >, <, =
- Basic actions:
  - set expense account
  - set memo
  - auto-apply flag
- Save-as-rule from user corrections

### Out of Scope
- AI suggestions
- automatic learning
- complex rule logic
- AR/AP rule assignment from bank feeds
- multi-condition rules

---

## 4. Rule Model

### Table: deterministic_rules

| Field | Type |
|------|------|
| id | UUID |
| organization_id | UUID |
| name | VARCHAR |
| is_active | BOOLEAN |
| priority | INT |
| trigger_field | VARCHAR |
| trigger_operator | VARCHAR |
| trigger_value | TEXT |
| action_gl_account_id | UUID |
| action_memo | TEXT |
| auto_apply | BOOLEAN |
| created_at | TIMESTAMP |
| updated_at | TIMESTAMP |

---

## 5. Trigger Model

### Supported triggers
- description contains text
- reference contains text
- amount >, <, =

### Single-condition rules only (MVP)

---

## 6. Action Model

Supported actions:
- set expense account
- set memo
- auto-apply

No AR/AP assignments from imported feeds in MVP.

---

## 7. Rule Evaluation

1. Load active rules
2. Sort by priority (lower number = higher priority)
3. First match wins
4. Generate proposal

---

## 8. Suggestion Proposal

```json
{
  "source": "rule",
  "primary_gl_account_id": "uuid",
  "memo": "Amazon purchase",
  "auto_applied": true,
  "proposed_lines": [],
  "flags": []
}
```

---

## 9. Auto-Apply Behavior

- Prefills classification
- Does NOT post automatically
- User still reviews

---

## 10. Suggestion Sources

Enum (future-proof):
- rule
- user_manual
- learned_rule
- ai

MVP uses:
- rule
- user_manual

---

## 11. Save as Rule

User can create a rule from corrected transactions.

- Explicit action only
- No automatic learning

---

## 12. Split Transactions

- Supported in schema
- Manual only in MVP
- Not core to rule engine initially

---

## 13. AI Boundary

AI may:
- Suggest classifications
- Provide explanation

AI may NOT:
- Post transactions
- Modify accounting truth
- Bypass user review

---

## 14. Example Flow

Transaction:
- "AMAZON MKTPLACE PMTS"
- $42.15

Rule:
- description contains "amazon"

Result:
- expense account = Office Supplies
- memo = Amazon purchase

User reviews and posts.

---

## 15. Key Invariants

1. Rules never post to ledger  
2. Rules only generate suggestions  
3. User approval required before posting  
4. First matching rule wins  
5. No auto-learning in MVP  

---

## End of Document
