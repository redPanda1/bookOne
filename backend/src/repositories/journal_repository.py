"""Journal entry and line repository."""

from __future__ import annotations

from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy import select

from models.journal_entry import JournalEntry
from models.journal_entry_audit_history import JournalEntryAuditHistory
from models.journal_line import JournalLine
from repositories.base_repository import BaseRepository


class JournalRepository(BaseRepository[JournalEntry]):
    """CRUD access for journal entries."""

    model = JournalEntry

    def create(self, payload: dict[str, object]) -> JournalEntry:
        """Create a journal entry with optional nested lines payload."""
        mutable_payload = dict(payload)
        raw_lines = mutable_payload.pop("lines", [])

        journal_entry = JournalEntry(**mutable_payload)
        if isinstance(raw_lines, list):
            journal_entry.lines = [
                JournalLine(**line_payload)
                for line_payload in raw_lines
                if isinstance(line_payload, dict)
            ]

        self.session.add(journal_entry)
        self.session.flush()
        self.session.refresh(journal_entry)
        return journal_entry

    def list(
        self,
        organization_id: UUID,
        *,
        status: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[JournalEntry]:
        stmt = select(self.model).where(self.model.organization_id == organization_id)

        if status:
            stmt = stmt.where(self.model.status == status)
        if from_date:
            stmt = stmt.where(self.model.entry_date >= from_date)
        if to_date:
            stmt = stmt.where(self.model.entry_date <= to_date)

        stmt = stmt.order_by(self.model.entry_date.desc(), self.model.journal_number.desc())
        return list(self.session.scalars(stmt).all())

    def replace_lines(
        self,
        journal_entry: JournalEntry,
        lines_payload: list[dict[str, Any]],
    ) -> JournalEntry:
        """Replace all lines for one journal entry."""
        journal_entry.lines = [JournalLine(**line_payload) for line_payload in lines_payload]
        self.session.flush()
        self.session.refresh(journal_entry)
        return journal_entry

    def insert_audit_history(
        self,
        *,
        organization_id: UUID,
        entity_id: UUID,
        action: str,
        from_status: str,
        to_status: str,
        performed_by: str,
        metadata_json: dict[str, Any] | None = None,
    ) -> JournalEntryAuditHistory:
        """Insert one journal-entry audit history event row."""
        history_row = JournalEntryAuditHistory(
            organization_id=organization_id,
            entity_type="journal_entry",
            entity_id=entity_id,
            action=action,
            from_status=from_status,
            to_status=to_status,
            performed_by=performed_by,
            metadata_json=metadata_json,
        )
        self.session.add(history_row)
        self.session.flush()
        self.session.refresh(history_row)
        return history_row
