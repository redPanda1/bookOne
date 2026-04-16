"""Journal entry ORM model."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from models.journal_line import JournalLine


class JournalEntry(TimestampMixin, Base):
    """Represents a journal entry header."""

    __tablename__ = "journal_entries"
    __table_args__ = (
        CheckConstraint("journal_number <> ''", name="journal_entries_journal_number_not_empty"),
        CheckConstraint("status <> ''", name="journal_entries_status_not_empty"),
        Index("ix_journal_entries_org_entry_date", "organization_id", "entry_date"),
        Index("ix_journal_entries_org_status", "organization_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    journal_number: Mapped[str] = mapped_column(String(64), nullable=False)
    entry_date: Mapped[date] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(String(1024))
    source_type: Mapped[str | None] = mapped_column(String(64))
    source_reference: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft", server_default="draft")
    posted_at: Mapped[datetime | None] = mapped_column(nullable=True)
    posted_by: Mapped[str | None] = mapped_column(String(255))

    lines: Mapped[list["JournalLine"]] = relationship(
        back_populates="journal_entry",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
