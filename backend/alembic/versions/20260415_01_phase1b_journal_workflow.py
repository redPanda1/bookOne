"""Phase 1B journal workflow schema additions."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260415_01"
down_revision: str | None = "20260414_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply journal posting metadata and audit history schema changes."""
    op.add_column("journal_entries", sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("journal_entries", sa.Column("posted_by", sa.String(length=255), nullable=True))

    op.create_table(
        "journal_entry_audit_history",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("from_status", sa.String(length=32), nullable=True),
        sa.Column("to_status", sa.String(length=32), nullable=True),
        sa.Column("performed_by", sa.String(length=255), nullable=False),
        sa.Column("performed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.CheckConstraint(
            "entity_type <> ''",
            name="journal_entry_audit_history_entity_type_not_empty",
        ),
        sa.CheckConstraint(
            "action <> ''",
            name="journal_entry_audit_history_action_not_empty",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_journal_entry_audit_history_org",
        "journal_entry_audit_history",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        "ix_journal_entry_audit_history_entity",
        "journal_entry_audit_history",
        ["entity_type", "entity_id"],
        unique=False,
    )


def downgrade() -> None:
    """Rollback phase 1B schema changes."""
    op.drop_index("ix_journal_entry_audit_history_entity", table_name="journal_entry_audit_history")
    op.drop_index("ix_journal_entry_audit_history_org", table_name="journal_entry_audit_history")
    op.drop_table("journal_entry_audit_history")

    op.drop_column("journal_entries", "posted_by")
    op.drop_column("journal_entries", "posted_at")
