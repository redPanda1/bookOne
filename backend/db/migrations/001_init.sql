-- BookOne Phase 0 foundation migration.
-- Aurora PostgreSQL-compatible core tables and indexes.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS gl_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE RESTRICT,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    natural_class TEXT NOT NULL,
    subtype TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT gl_accounts_org_code_unique UNIQUE (organization_id, code)
);

CREATE INDEX IF NOT EXISTS idx_gl_accounts_org ON gl_accounts (organization_id);

CREATE TABLE IF NOT EXISTS journal_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE RESTRICT,
    entry_date DATE NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'draft',
    created_by TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT journal_entries_status_check CHECK (status IN ('draft', 'posted'))
);

CREATE INDEX IF NOT EXISTS idx_journal_entries_org ON journal_entries (organization_id);
CREATE INDEX IF NOT EXISTS idx_journal_entries_org_status ON journal_entries (organization_id, status);

CREATE TABLE IF NOT EXISTS journal_lines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE RESTRICT,
    journal_entry_id UUID NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
    gl_account_id UUID NOT NULL REFERENCES gl_accounts(id) ON DELETE RESTRICT,
    memo TEXT NOT NULL DEFAULT '',
    debit_amount NUMERIC(18, 2) NOT NULL DEFAULT 0,
    credit_amount NUMERIC(18, 2) NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT journal_lines_amount_non_negative CHECK (debit_amount >= 0 AND credit_amount >= 0)
);

CREATE INDEX IF NOT EXISTS idx_journal_lines_org ON journal_lines (organization_id);
CREATE INDEX IF NOT EXISTS idx_journal_lines_je ON journal_lines (journal_entry_id);

CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE RESTRICT,
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    action TEXT NOT NULL,
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_audit_log_org_created ON audit_log (organization_id, created_at DESC);
