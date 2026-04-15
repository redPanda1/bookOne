"""Database health utilities."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text

from database.session import session_scope


def probe_database() -> dict[str, Any]:
    """Execute a lightweight query and return health details."""
    with session_scope() as session:
        scalar_result = session.execute(text("SELECT 1")).scalar_one()
    return {"ok": bool(scalar_result == 1)}
