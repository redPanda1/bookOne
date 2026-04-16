"""SAM Lambda handler for BookOne API (HTTP API v2)."""

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from auth import build_request_user_context
from database.health import probe_database
from database.session import session_scope
from repositories.ledger_account_repository import LedgerAccountRepository
from services import (
    JournalEntryConflictError,
    JournalEntryNotFoundError,
    JournalEntryService,
    JournalEntryValidationError,
)


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Route incoming API Gateway HTTP API requests."""
    del context  # Unused in scaffold.

    request_context = event.get("requestContext", {})
    http_context = request_context.get("http", {})
    method = http_context.get("method", "")
    path = event.get("rawPath", "")

    if method == "GET" and path == "/session":
        body = _build_session_payload(event)
        return _response(200, body)

    if method == "GET" and path == "/health/db":
        user_ctx = build_request_user_context(event)
        if not user_ctx.authenticated:
            return _response(401, {"message": "Unauthorized"})
        return _handle_db_health()

    if method == "POST" and path == "/journal-entries":
        return _handle_create_journal_entry(event)

    if method == "POST" and path == "/gl-accounts":
        return _handle_create_gl_account(event)

    if method == "PATCH":
        is_match, journal_entry_id = _match_journal_entry_route(path)
        if is_match and journal_entry_id is None:
            return _response(400, {"message": "Invalid journal entry id"})
        if journal_entry_id is not None:
            return _handle_update_journal_entry(event, journal_entry_id)

    if method == "POST":
        is_match, journal_entry_id = _match_journal_entry_route(path, suffix="post")
        if is_match and journal_entry_id is None:
            return _response(400, {"message": "Invalid journal entry id"})
        if journal_entry_id is not None:
            return _handle_post_journal_entry(event, journal_entry_id)

    return _response(404, {"message": "Route not found"})


def _response(status_code: int, body: dict[str, Any]) -> dict[str, Any]:
    """Create API Gateway HTTP API-compatible response."""
    return {
        "statusCode": status_code,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(body),
    }


def _build_session_payload(event: dict[str, Any]) -> dict[str, Any]:
    """Return a frontend-bootstrap session payload."""
    user_ctx = build_request_user_context(event)

    return {
        "authenticated": user_ctx.authenticated,
        "user": {
            "id": user_ctx.user_id,
            "email": user_ctx.email,
        },
        "organization": {
            "id": user_ctx.organization_id,
            "name": user_ctx.organization_name,
        },
    }


def _handle_db_health() -> dict[str, Any]:
    """Run lightweight DB probe and return structured status."""
    try:
        result = probe_database()
    except Exception as exc:  # pragma: no cover - exercised by unit test
        return _response(
            503,
            {
                "status": "error",
                "database": {"ok": False, "error": str(exc)},
            },
        )

    return _response(
        200,
        {
            "status": "ok",
            "database": result,
        },
    )


def _handle_create_journal_entry(event: dict[str, Any]) -> dict[str, Any]:
    user_ctx = build_request_user_context(event)
    if not user_ctx.authenticated:
        return _response(401, {"message": "Unauthorized"})

    try:
        organization_id = UUID(user_ctx.organization_id)
    except ValueError:
        return _response(400, {"message": "Invalid organization context"})

    try:
        payload = _parse_json_body(event)
    except ValueError as exc:
        return _response(400, {"message": str(exc)})

    with session_scope() as session:
        service = JournalEntryService(session)
        try:
            journal_entry = service.create_draft_journal_entry(organization_id, payload)
        except JournalEntryValidationError as exc:
            return _response(400, {"message": str(exc)})

    return _response(201, {"journal_entry": _serialize_journal_entry(journal_entry)})


def _handle_create_gl_account(event: dict[str, Any]) -> dict[str, Any]:
    user_ctx = build_request_user_context(event)
    if not user_ctx.authenticated:
        return _response(401, {"message": "Unauthorized"})

    try:
        organization_id = UUID(user_ctx.organization_id)
    except ValueError:
        return _response(400, {"message": "Invalid organization context"})

    try:
        payload = _parse_json_body(event)
        create_payload = _normalize_gl_account_payload(payload)
    except ValueError as exc:
        return _response(400, {"message": str(exc)})

    with session_scope() as session:
        repository = LedgerAccountRepository(session)
        try:
            ledger_account = repository.create(
                {
                    "organization_id": organization_id,
                    **create_payload,
                }
            )
        except IntegrityError:
            return _response(
                409,
                {"message": "GL account could not be created due to a data conflict"},
            )

    return _response(201, {"gl_account": _serialize_ledger_account(ledger_account)})


def _handle_update_journal_entry(event: dict[str, Any], journal_entry_id: UUID) -> dict[str, Any]:
    user_ctx = build_request_user_context(event)
    if not user_ctx.authenticated:
        return _response(401, {"message": "Unauthorized"})

    try:
        organization_id = UUID(user_ctx.organization_id)
    except ValueError:
        return _response(400, {"message": "Invalid organization context"})

    try:
        payload = _parse_json_body(event)
    except ValueError as exc:
        return _response(400, {"message": str(exc)})

    with session_scope() as session:
        service = JournalEntryService(session)
        try:
            journal_entry = service.update_draft_journal_entry(
                organization_id,
                journal_entry_id,
                payload,
            )
        except JournalEntryValidationError as exc:
            return _response(400, {"message": str(exc)})
        except JournalEntryNotFoundError as exc:
            return _response(404, {"message": str(exc)})
        except JournalEntryConflictError as exc:
            return _response(409, {"message": str(exc)})

    return _response(200, {"journal_entry": _serialize_journal_entry(journal_entry)})


def _handle_post_journal_entry(event: dict[str, Any], journal_entry_id: UUID) -> dict[str, Any]:
    user_ctx = build_request_user_context(event)
    if not user_ctx.authenticated:
        return _response(401, {"message": "Unauthorized"})

    try:
        organization_id = UUID(user_ctx.organization_id)
    except ValueError:
        return _response(400, {"message": "Invalid organization context"})

    with session_scope() as session:
        service = JournalEntryService(session)
        try:
            journal_entry = service.post_journal_entry(
                organization_id,
                journal_entry_id,
                actor_user_id=user_ctx.user_id,
            )
        except JournalEntryValidationError as exc:
            return _response(400, {"message": str(exc)})
        except JournalEntryNotFoundError as exc:
            return _response(404, {"message": str(exc)})
        except JournalEntryConflictError as exc:
            return _response(409, {"message": str(exc)})

    return _response(200, {"journal_entry": _serialize_journal_entry(journal_entry)})


def _parse_json_body(event: dict[str, Any]) -> dict[str, Any]:
    raw_body = event.get("body")
    if raw_body is None:
        raise ValueError("Request body is required")
    if not isinstance(raw_body, str):
        raise ValueError("Request body must be a JSON object")

    try:
        parsed = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise ValueError("Request body must be valid JSON") from exc

    if not isinstance(parsed, dict):
        raise ValueError("Request body must be a JSON object")
    return parsed


def _match_journal_entry_route(path: str, *, suffix: str | None = None) -> tuple[bool, UUID | None]:
    if not path.startswith("/journal-entries/"):
        return (False, None)

    parts = path.strip("/").split("/")
    if len(parts) < 2:
        return (False, None)
    if parts[0] != "journal-entries":
        return (False, None)

    if suffix is None and len(parts) != 2:
        return (False, None)
    if suffix is not None and (len(parts) != 3 or parts[2] != suffix):
        return (False, None)

    try:
        return (True, UUID(parts[1]))
    except ValueError:
        return (True, None)


def _serialize_journal_entry(entry: Any) -> dict[str, Any]:
    lines = getattr(entry, "lines", [])
    return {
        "id": str(entry.id),
        "organization_id": str(entry.organization_id),
        "journal_number": entry.journal_number,
        "entry_date": _serialize_value(entry.entry_date),
        "description": entry.description,
        "source_type": entry.source_type,
        "source_reference": entry.source_reference,
        "status": entry.status,
        "posted_at": _serialize_value(getattr(entry, "posted_at", None)),
        "posted_by": getattr(entry, "posted_by", None),
        "lines": [_serialize_journal_line(line) for line in lines],
    }


def _serialize_journal_line(line: Any) -> dict[str, Any]:
    return {
        "id": str(line.id),
        "journal_entry_id": str(line.journal_entry_id),
        "ledger_account_id": str(line.ledger_account_id),
        "debit_amount": _serialize_value(line.debit_amount),
        "credit_amount": _serialize_value(line.credit_amount),
        "memo": line.memo,
        "line_order": line.line_order,
    }


def _serialize_ledger_account(account: Any) -> dict[str, Any]:
    return {
        "id": str(account.id),
        "organization_id": str(account.organization_id),
        "account_code": account.account_code,
        "name": account.name,
        "description": account.description,
        "account_type": account.account_type,
        "subtype": account.subtype,
        "is_active": account.is_active,
    }


def _normalize_gl_account_payload(payload: dict[str, Any]) -> dict[str, Any]:
    account_code = payload.get("account_code")
    name = payload.get("name")
    account_type = payload.get("account_type")
    description = payload.get("description")
    subtype = payload.get("subtype")
    is_active = payload.get("is_active", True)

    if not isinstance(account_code, str) or not account_code.strip():
        raise ValueError("'account_code' is required")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("'name' is required")
    if not isinstance(account_type, str) or not account_type.strip():
        raise ValueError("'account_type' is required")
    if description is not None and not isinstance(description, str):
        raise ValueError("'description' must be a string when provided")
    if subtype is not None and not isinstance(subtype, str):
        raise ValueError("'subtype' must be a string when provided")
    if not isinstance(is_active, bool):
        raise ValueError("'is_active' must be a boolean when provided")

    return {
        "account_code": account_code.strip(),
        "name": name.strip(),
        "description": description.strip() if isinstance(description, str) and description.strip() else None,
        "account_type": account_type.strip(),
        "subtype": subtype.strip() if isinstance(subtype, str) and subtype.strip() else None,
        "is_active": is_active,
    }


def _serialize_value(value: object) -> object:
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value
