"""Phase 1A core database foundation."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260414_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply the core accounting schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS organizations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    op.create_table(
        "ledger_accounts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("account_code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=1024), nullable=True),
        sa.Column("account_type", sa.String(length=64), nullable=False),
        sa.Column("subtype", sa.String(length=64), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("account_code <> ''", name="ledger_accounts_account_code_not_empty"),
        sa.CheckConstraint("name <> ''", name="ledger_accounts_name_not_empty"),
        sa.CheckConstraint("account_type <> ''", name="ledger_accounts_account_type_not_empty"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "account_code", name="uq_ledger_accounts_org_code"),
    )
    op.create_index("ix_ledger_accounts_organization_id", "ledger_accounts", ["organization_id"], unique=False)
    op.create_index(
        "ix_ledger_accounts_org_account_code",
        "ledger_accounts",
        ["organization_id", "account_code"],
        unique=False,
    )

    op.create_table(
        "entities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("entity_type", sa.String(length=32), nullable=False),
        sa.Column("legal_name", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=64), nullable=True),
        sa.Column("tax_identifier", sa.String(length=128), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("entity_type <> ''", name="entities_entity_type_not_empty"),
        sa.CheckConstraint("legal_name <> ''", name="entities_legal_name_not_empty"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_entities_organization_id", "entities", ["organization_id"], unique=False)
    op.create_index("ix_entities_org_type", "entities", ["organization_id", "entity_type"], unique=False)

    op.create_table(
        "financial_accounts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("institution_name", sa.String(length=255), nullable=False),
        sa.Column("account_name", sa.String(length=255), nullable=False),
        sa.Column("account_type", sa.String(length=64), nullable=False),
        sa.Column("masked_account_number", sa.String(length=16), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "institution_name <> ''",
            name="financial_accounts_institution_name_not_empty",
        ),
        sa.CheckConstraint("account_name <> ''", name="financial_accounts_account_name_not_empty"),
        sa.CheckConstraint("account_type <> ''", name="financial_accounts_account_type_not_empty"),
        sa.CheckConstraint("currency <> ''", name="financial_accounts_currency_not_empty"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_financial_accounts_organization_id",
        "financial_accounts",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        "ix_financial_accounts_org_type",
        "financial_accounts",
        ["organization_id", "account_type"],
        unique=False,
    )

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "journal_lines" in table_names:
        op.drop_table("journal_lines")
    if "journal_entries" in table_names:
        op.drop_table("journal_entries")

    op.create_table(
        "journal_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("journal_number", sa.String(length=64), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("description", sa.String(length=1024), nullable=True),
        sa.Column("source_type", sa.String(length=64), nullable=True),
        sa.Column("source_reference", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), server_default="draft", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("journal_number <> ''", name="journal_entries_journal_number_not_empty"),
        sa.CheckConstraint("status <> ''", name="journal_entries_status_not_empty"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "journal_number", name="uq_journal_entries_org_number"),
    )
    op.create_index(
        "ix_journal_entries_organization_id",
        "journal_entries",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        "ix_journal_entries_org_entry_date",
        "journal_entries",
        ["organization_id", "entry_date"],
        unique=False,
    )
    op.create_index(
        "ix_journal_entries_org_status",
        "journal_entries",
        ["organization_id", "status"],
        unique=False,
    )

    op.create_table(
        "journal_lines",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("journal_entry_id", sa.Uuid(), nullable=False),
        sa.Column("ledger_account_id", sa.Uuid(), nullable=False),
        sa.Column("debit_amount", sa.Numeric(precision=18, scale=2), server_default="0", nullable=False),
        sa.Column("credit_amount", sa.Numeric(precision=18, scale=2), server_default="0", nullable=False),
        sa.Column("memo", sa.String(length=1024), nullable=True),
        sa.Column("line_order", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "debit_amount >= 0 AND credit_amount >= 0",
            name="journal_lines_amount_non_negative",
        ),
        sa.CheckConstraint(
            "(debit_amount = 0 AND credit_amount > 0) OR "
            "(credit_amount = 0 AND debit_amount > 0)",
            name="journal_lines_single_sided_amount",
        ),
        sa.CheckConstraint("line_order > 0", name="journal_lines_line_order_positive"),
        sa.ForeignKeyConstraint(["journal_entry_id"], ["journal_entries.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ledger_account_id"], ["ledger_accounts.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("journal_entry_id", "line_order", name="uq_journal_lines_entry_order"),
    )
    op.create_index(
        "ix_journal_lines_entry_order",
        "journal_lines",
        ["journal_entry_id", "line_order"],
        unique=False,
    )
    op.create_index(
        "ix_journal_lines_ledger_account",
        "journal_lines",
        ["ledger_account_id"],
        unique=False,
    )


def downgrade() -> None:
    """Rollback the phase 1A schema."""
    op.drop_index("ix_journal_lines_ledger_account", table_name="journal_lines")
    op.drop_index("ix_journal_lines_entry_order", table_name="journal_lines")
    op.drop_table("journal_lines")

    op.drop_index("ix_journal_entries_org_status", table_name="journal_entries")
    op.drop_index("ix_journal_entries_org_entry_date", table_name="journal_entries")
    op.drop_index("ix_journal_entries_organization_id", table_name="journal_entries")
    op.drop_table("journal_entries")

    op.drop_index("ix_financial_accounts_org_type", table_name="financial_accounts")
    op.drop_index("ix_financial_accounts_organization_id", table_name="financial_accounts")
    op.drop_table("financial_accounts")

    op.drop_index("ix_entities_org_type", table_name="entities")
    op.drop_index("ix_entities_organization_id", table_name="entities")
    op.drop_table("entities")

    op.drop_index("ix_ledger_accounts_org_account_code", table_name="ledger_accounts")
    op.drop_index("ix_ledger_accounts_organization_id", table_name="ledger_accounts")
    op.drop_table("ledger_accounts")

    op.create_table(
        "journal_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.Text(), nullable=False, server_default="draft"),
        sa.Column("created_by", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("status IN ('draft', 'posted')", name="journal_entries_status_check"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_journal_entries_org",
        "journal_entries",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        "idx_journal_entries_org_status",
        "journal_entries",
        ["organization_id", "status"],
        unique=False,
    )

    op.create_table(
        "journal_lines",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("journal_entry_id", sa.Uuid(), nullable=False),
        sa.Column("gl_account_id", sa.Uuid(), nullable=False),
        sa.Column("memo", sa.Text(), nullable=False, server_default=""),
        sa.Column("debit_amount", sa.Numeric(precision=18, scale=2), nullable=False, server_default="0"),
        sa.Column("credit_amount", sa.Numeric(precision=18, scale=2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(
            "debit_amount >= 0 AND credit_amount >= 0",
            name="journal_lines_amount_non_negative",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["journal_entry_id"], ["journal_entries.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["gl_account_id"], ["gl_accounts.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_journal_lines_org", "journal_lines", ["organization_id"], unique=False)
    op.create_index("idx_journal_lines_je", "journal_lines", ["journal_entry_id"], unique=False)
