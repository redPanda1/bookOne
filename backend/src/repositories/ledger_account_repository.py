"""LedgerAccount repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from models.ledger_account import LedgerAccount
from repositories.base_repository import BaseRepository


class LedgerAccountRepository(BaseRepository[LedgerAccount]):
    """CRUD access for ledger accounts."""

    model = LedgerAccount

    def list(
        self,
        organization_id: UUID,
        *,
        account_type: str | None = None,
        include_inactive: bool = False,
    ) -> list[LedgerAccount]:
        stmt = select(self.model).where(self.model.organization_id == organization_id)

        if account_type:
            stmt = stmt.where(self.model.account_type == account_type)

        if not include_inactive:
            stmt = stmt.where(self.model.is_active.is_(True))

        stmt = stmt.order_by(self.model.account_code.asc())
        return list(self.session.scalars(stmt).all())
