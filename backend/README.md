# BookOne Lambda Backend

Modular monolith backend for API Gateway HTTP API + AWS Lambda.

## Source Of Truth

- Runtime code loaded by SAM lives in `backend/src/` (`CodeUri: src`).
- Runtime dependency file is `backend/src/requirements.txt`.
- Test dependency file is `backend/requirements-dev.txt`.

## Structure

```
backend/
  template.yaml
  .env.example
  alembic/
    env.py
    versions/
      20260414_01_phase1a_core_database_foundation.py
  alembic.ini
  db/
    migrations/
      001_init.sql
  scripts/
    run_migrations.py
  src/
    requirements.txt
    config/
      settings.py
    database/
      base.py
      session.py
      health.py
    handlers/
      app.py
    models/
      organization.py
      ledger_account.py
      entity.py
      financial_account.py
      journal_entry.py
      journal_line.py
    services/
    repositories/
      base_repository.py
      ledger_account_repository.py
      entity_repository.py
      financial_account_repository.py
      journal_repository.py
  tests/
    test_database_session.py
    test_models.py
    test_repositories.py
    test_health_endpoint.py
```

## Current Endpoints

- `GET /session`
- `GET /health/db` (protected)

## Prerequisites

1. Start Docker Desktop (required for `sam local` and local Postgres containers).
2. Create a virtual environment once:

```bash
cd /Users/simon/Developer/bookOne/backend
python3 -m venv .venv
```

3. Activate the virtual environment in each new terminal session:

```bash
cd /Users/simon/Developer/bookOne/backend
source .venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r src/requirements.txt
```

## Local Run (SAM)

```bash
cd /Users/simon/Developer/bookOne/backend
source .venv/bin/activate
sam validate
sam build
sam local start-api --port 3001
```

Test:

```bash
curl -i http://127.0.0.1:3001/session
```

## Run Alembic Migrations (Local)

Set DB env vars first (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_SSL_MODE`), then run:

```bash
cd /Users/simon/Developer/bookOne/backend
source .venv/bin/activate
alembic upgrade head
```

To rollback the latest migration:

```bash
alembic downgrade -1
```

## Legacy SQL Runner (Phase 0)

The legacy SQL migration runner is retained for backward compatibility:

```bash
cd /Users/simon/Developer/bookOne/backend
source .venv/bin/activate
python3 scripts/run_migrations.py
```

It applies numbered SQL files in `backend/db/migrations/` and records applied versions in `schema_migrations`.

## Tests

```bash
cd /Users/simon/Developer/bookOne/backend
source .venv/bin/activate
pip install -r src/requirements.txt -r requirements-dev.txt
pytest
```

## Manual SQL Fallback

```bash
cd /Users/simon/Developer/bookOne/backend
psql "$DATABASE_URL" -f db/migrations/001_init.sql
```

## Troubleshooting

If you get:

`Error: Running AWS SAM projects locally requires a container runtime...`

1. Confirm Docker is running:

```bash
docker info
```

2. Confirm you are using Homebrew SAM (newer):

```bash
type -a sam
which sam
sam --version
```

Expected active path:

`/opt/homebrew/bin/sam`

If your shell still uses `/usr/local/bin/sam`, update PATH:

```bash
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:$PATH"
hash -r
which sam
sam --version
```

To persist in zsh:

```bash
echo 'export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:$PATH"' >> ~/.zshrc
source ~/.zshrc
hash -r
```
