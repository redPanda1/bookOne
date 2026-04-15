"""Tests for SQLAlchemy engine/session configuration."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import text

from config.settings import get_settings
from database.session import get_engine, get_session_factory


def test_engine_and_session_factory(tmp_path: Path, monkeypatch) -> None:
    """Engine and session factory should be buildable from env config."""
    sqlite_path = tmp_path / "bookone.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+pysqlite:///{sqlite_path}")

    get_settings.cache_clear()
    get_engine.cache_clear()
    get_session_factory.cache_clear()

    engine = get_engine()
    assert str(engine.url).startswith("sqlite+pysqlite:///")

    session = get_session_factory()()
    try:
        scalar_value = session.execute(text("SELECT 1")).scalar_one()
        assert scalar_value == 1
    finally:
        session.close()
