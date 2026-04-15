"""Repository skeleton for journal entry data access."""

from __future__ import annotations

from typing import Any

from repositories.db import fetch_all, fetch_one


def list_journal_entries(organization_id: str) -> list[dict[str, Any]]:
    """List journal entries for an organization."""
    query = """
    SELECT
        id,
        organization_id,
        entry_date,
        description,
        status,
        created_by,
        created_at,
        updated_at
    FROM journal_entries
    WHERE organization_id = %s
    ORDER BY created_at DESC
    """
    return fetch_all(query, (organization_id,))


def get_journal_entry_by_id(
    organization_id: str,
    journal_entry_id: str,
) -> dict[str, Any] | None:
    """Fetch one journal entry by id scoped to organization."""
    query = """
    SELECT
        id,
        organization_id,
        entry_date,
        description,
        status,
        created_by,
        created_at,
        updated_at
    FROM journal_entries
    WHERE organization_id = %s
      AND id = %s
    """
    return fetch_one(query, (organization_id, journal_entry_id))
