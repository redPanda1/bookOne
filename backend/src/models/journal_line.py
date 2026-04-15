"""Journal line ORM model."""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.journal_entry import JournalEntry
from models.ledger_account import LedgerAccount


class JournalLine(Base):
    """Represents one debit/credit line inside a journal entry."""

    __tablename__ = "journal_lines"
    __table_args__ = (
        CheckConstraint(
            "debit_amount >= 0 AND credit_amount >= 0",
            name="journal_lines_amount_non_negative",
        ),
        CheckConstraint(
            "(debit_amount = 0 AND credit_amount > 0) OR "
            "(credit_amount = 0 AND debit_amount > 0)",
            name="journal_lines_single_sided_amount",
        ),
        CheckConstraint("line_order > 0", name="journal_lines_line_order_positive"),
        Index("ix_journal_lines_entry_order", "journal_entry_id", "line_order"),
        Index("ix_journal_lines_ledger_account", "ledger_account_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    journal_entry_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("journal_entries.id", ondelete="CASCADE"),
        nullable=False,
    )
    ledger_account_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("ledger_accounts.id", ondelete="RESTRICT"),
        nullable=False,
    )
    debit_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    credit_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    memo: Mapped[str | None] = mapped_column(String(1024))
    line_order: Mapped[int] = mapped_column(Integer, nullable=False)

    journal_entry: Mapped[JournalEntry] = relationship(back_populates="lines", lazy="joined")
    ledger_account: Mapped[LedgerAccount] = relationship(back_populates="journal_lines", lazy="joined")
