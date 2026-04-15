"""Ledger account ORM model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from models.journal_line import JournalLine


class LedgerAccount(TimestampMixin, Base):
    """Represents a chart of account row."""

    __tablename__ = "ledger_accounts"
    __table_args__ = (
        CheckConstraint("account_code <> ''", name="ledger_accounts_account_code_not_empty"),
        CheckConstraint("name <> ''", name="ledger_accounts_name_not_empty"),
        CheckConstraint("account_type <> ''", name="ledger_accounts_account_type_not_empty"),
        Index("ix_ledger_accounts_org_account_code", "organization_id", "account_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    account_code: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1024))
    account_type: Mapped[str] = mapped_column(String(64), nullable=False)
    subtype: Mapped[str | None] = mapped_column(String(64))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    journal_lines: Mapped[list["JournalLine"]] = relationship(
        back_populates="ledger_account",
        lazy="selectin",
    )
