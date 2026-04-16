"""Journal entry posting audit history ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, CheckConstraint, DateTime, Index, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class JournalEntryAuditHistory(Base):
    """Represents one workflow/audit event for a journal entry."""

    __tablename__ = "journal_entry_audit_history"
    __table_args__ = (
        CheckConstraint("entity_type <> ''", name="journal_entry_audit_history_entity_type_not_empty"),
        CheckConstraint("action <> ''", name="journal_entry_audit_history_action_not_empty"),
        Index("ix_journal_entry_audit_history_org", "organization_id"),
        Index("ix_journal_entry_audit_history_entity", "entity_type", "entity_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(32))
    to_status: Mapped[str | None] = mapped_column(String(32))
    performed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    performed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
