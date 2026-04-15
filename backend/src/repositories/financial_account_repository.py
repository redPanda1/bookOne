"""FinancialAccount repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from models.financial_account import FinancialAccount
from repositories.base_repository import BaseRepository


class FinancialAccountRepository(BaseRepository[FinancialAccount]):
    """CRUD access for financial accounts."""

    model = FinancialAccount

    def list(
        self,
        organization_id: UUID,
        *,
        account_type: str | None = None,
        include_inactive: bool = False,
    ) -> list[FinancialAccount]:
        stmt = select(self.model).where(self.model.organization_id == organization_id)

        if account_type:
            stmt = stmt.where(self.model.account_type == account_type)

        if not include_inactive:
            stmt = stmt.where(self.model.is_active.is_(True))

        stmt = stmt.order_by(self.model.institution_name.asc(), self.model.account_name.asc())
        return list(self.session.scalars(stmt).all())
