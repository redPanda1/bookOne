"""Minimal PostgreSQL access helpers using psycopg."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

import psycopg
from psycopg.rows import dict_row

from config.settings import get_settings

_cached_connection: psycopg.Connection | None = None


def _open_connection() -> psycopg.Connection:
    settings = get_settings()
    return psycopg.connect(settings.db_dsn, row_factory=dict_row)


def get_connection() -> psycopg.Connection:
    """Return a connection re-used across Lambda warm invocations."""
    global _cached_connection

    if _cached_connection is None or _cached_connection.closed:
        _cached_connection = _open_connection()
    return _cached_connection


@contextmanager
def transaction() -> Iterator[psycopg.Connection]:
    """Provide a transaction boundary for accounting writes."""
    conn = get_connection()
    try:
        with conn.transaction():
            yield conn
    except Exception:
        conn.rollback()
        raise


def fetch_all(
    query: str,
    params: tuple[Any, ...] | None = None,
    *,
    conn: psycopg.Connection | None = None,
) -> list[dict[str, Any]]:
    """Run a SELECT query and return all rows."""
    active_conn = conn or get_connection()
    with active_conn.cursor() as cur:
        cur.execute(query, params or ())
        return cur.fetchall()


def fetch_one(
    query: str,
    params: tuple[Any, ...] | None = None,
    *,
    conn: psycopg.Connection | None = None,
) -> dict[str, Any] | None:
    """Run a SELECT query and return one row."""
    active_conn = conn or get_connection()
    with active_conn.cursor() as cur:
        cur.execute(query, params or ())
        return cur.fetchone()


def execute(
    query: str,
    params: tuple[Any, ...] | None = None,
    *,
    conn: psycopg.Connection | None = None,
) -> int:
    """Run INSERT/UPDATE/DELETE and return affected rows."""
    active_conn = conn or get_connection()
    with active_conn.cursor() as cur:
        cur.execute(query, params or ())
        return cur.rowcount
