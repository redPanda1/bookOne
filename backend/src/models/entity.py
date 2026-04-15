"""Entity ORM model (customer/vendor abstraction)."""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, CheckConstraint, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base, TimestampMixin


class Entity(TimestampMixin, Base):
    """Represents an external business entity."""

    __tablename__ = "entities"
    __table_args__ = (
        CheckConstraint("entity_type <> ''", name="entities_entity_type_not_empty"),
        CheckConstraint("legal_name <> ''", name="entities_legal_name_not_empty"),
        Index("ix_entities_org_type", "organization_id", "entity_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(64))
    tax_identifier: Mapped[str | None] = mapped_column(String(128))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
