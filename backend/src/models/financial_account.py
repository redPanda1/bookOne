"""Financial account ORM model."""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, CheckConstraint, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base, TimestampMixin


class FinancialAccount(TimestampMixin, Base):
    """Represents bank or credit card account metadata."""

    __tablename__ = "financial_accounts"
    __table_args__ = (
        CheckConstraint(
            "institution_name <> ''",
            name="financial_accounts_institution_name_not_empty",
        ),
        CheckConstraint("account_name <> ''", name="financial_accounts_account_name_not_empty"),
        CheckConstraint("account_type <> ''", name="financial_accounts_account_type_not_empty"),
        CheckConstraint("currency <> ''", name="financial_accounts_currency_not_empty"),
        Index("ix_financial_accounts_org_type", "organization_id", "account_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    institution_name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_type: Mapped[str] = mapped_column(String(64), nullable=False)
    masked_account_number: Mapped[str | None] = mapped_column(String(16))
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
