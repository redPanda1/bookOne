"""SQLAlchemy engine and session management."""

from __future__ import annotations

from contextlib import contextmanager
from functools import lru_cache
from typing import Iterator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from config.settings import get_settings

SessionFactory = sessionmaker[Session]


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Return shared SQLAlchemy engine for the runtime."""
    settings = get_settings()
    return create_engine(
        settings.sqlalchemy_database_url,
        future=True,
        pool_pre_ping=True,
    )


@lru_cache(maxsize=1)
def get_session_factory() -> SessionFactory:
    """Create and cache the sessionmaker."""
    return sessionmaker(
        bind=get_engine(),
        class_=Session,
        autoflush=False,
        expire_on_commit=False,
    )


@contextmanager
def session_scope() -> Iterator[Session]:
    """Provide a transactional scope around a series of operations."""
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
