"""SAM Lambda handler for BookOne API (HTTP API v2)."""

from __future__ import annotations

import json
from typing import Any

from auth import build_request_user_context
from database.health import probe_database


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
