"""Shared SQLAlchemy repository abstractions."""

from __future__ import annotations

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Base CRUD repository with reusable SQLAlchemy helpers."""

    model: type[ModelT]

    def __init__(self, session: Session):
        self.session = session

    def create(self, payload: dict[str, Any]) -> ModelT:
        """Create and persist one model instance."""
        instance = self.model(**payload)
        self.session.add(instance)
        self.session.flush()
        self.session.refresh(instance)
        return instance

    def get_by_id(self, organization_id: UUID, entity_id: UUID) -> ModelT | None:
        """Load one entity by tenant and identifier."""
        stmt = select(self.model).where(
            self.model.organization_id == organization_id,  # type: ignore[attr-defined]
            self.model.id == entity_id,  # type: ignore[attr-defined]
        )
        return self.session.scalar(stmt)

    def list(self, organization_id: UUID, *, include_inactive: bool = False) -> list[ModelT]:
        """List entities scoped to organization."""
        stmt = select(self.model).where(
            self.model.organization_id == organization_id,  # type: ignore[attr-defined]
        )

        if hasattr(self.model, "is_active") and not include_inactive:
            stmt = stmt.where(self.model.is_active.is_(True))  # type: ignore[attr-defined]

        return list(self.session.scalars(stmt).all())

    def update(self, instance: ModelT, payload: dict[str, Any]) -> ModelT:
        """Apply in-place updates and return refreshed instance."""
        for key, value in payload.items():
            setattr(instance, key, value)
        self.session.flush()
        self.session.refresh(instance)
        return instance

    def soft_delete(self, organization_id: UUID, entity_id: UUID) -> ModelT | None:
        """Mark an entity inactive when model supports soft deletes."""
        instance = self.get_by_id(organization_id, entity_id)
        if instance is None or not hasattr(instance, "is_active"):
            return instance

        setattr(instance, "is_active", False)
        self.session.flush()
        self.session.refresh(instance)
        return instance
