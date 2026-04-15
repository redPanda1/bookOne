"""Repository skeleton for chart-of-accounts data access."""

from __future__ import annotations

from typing import Any

from repositories.db import fetch_all, fetch_one


def list_gl_accounts(organization_id: str) -> list[dict[str, Any]]:
    """List GL accounts for an organization."""
    query = """
    SELECT
        id,
        organization_id,
        code,
        name,
        natural_class,
        subtype,
        is_active,
        created_at,
        updated_at
    FROM gl_accounts
    WHERE organization_id = %s
    ORDER BY code ASC
    """
    return fetch_all(query, (organization_id,))


def get_gl_account_by_id(
    organization_id: str,
    gl_account_id: str,
) -> dict[str, Any] | None:
    """Fetch one GL account by id scoped to organization."""
    query = """
    SELECT
        id,
        organization_id,
        code,
        name,
        natural_class,
        subtype,
        is_active,
        created_at,
        updated_at
    FROM gl_accounts
    WHERE organization_id = %s
      AND id = %s
    """
    return fetch_one(query, (organization_id, gl_account_id))
