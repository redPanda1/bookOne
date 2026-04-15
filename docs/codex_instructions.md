You are building BookOne, a lightweight accounting system.

Follow these rules strictly:

1. The source of truth is the documentation in /docs
2. Do not invent features not described in the docs
3. Keep implementation simple (MVP-first)
4. Use:
   * Python (AWS Lambda) for backend
   * PostgreSQL (Aurora-compatible SQL)
   * React + TypeScript + Redux for frontend
5. All accounting writes must be transaction-safe
6. Do not introduce microservices
7. Do not introduce CQRS or event sourcing
8. Always explain assumptions before coding if unclear
9. Prefer small, testable steps over large outputs
