"""Entity repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from models.entity import Entity
from repositories.base_repository import BaseRepository


class EntityRepository(BaseRepository[Entity]):
    """CRUD access for customers/vendors."""

    model = Entity

    def list(
        self,
        organization_id: UUID,
        *,
        entity_type: str | None = None,
        include_inactive: bool = False,
    ) -> list[Entity]:
        stmt = select(self.model).where(self.model.organization_id == organization_id)

        if entity_type:
            stmt = stmt.where(self.model.entity_type == entity_type)

        if not include_inactive:
            stmt = stmt.where(self.model.is_active.is_(True))

        stmt = stmt.order_by(self.model.legal_name.asc())
        return list(self.session.scalars(stmt).all())
