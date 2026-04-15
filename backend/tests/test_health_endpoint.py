"""Tests for /health/db handler behavior."""

from __future__ import annotations

import json

from auth.jwt_helper import RequestUserContext
from handlers.app import lambda_handler


def test_health_db_requires_authentication(monkeypatch) -> None:
    """Unauthenticated requests should be rejected."""
    monkeypatch.setattr(
        "handlers.app.build_request_user_context",
        lambda _event: RequestUserContext(
            authenticated=False,
            user_id="u1",
            email="user@example.com",
            organization_id="org-1",
            organization_name="Org",
            token=None,
            claims={},
        ),
    )

    response = lambda_handler(
        {
            "rawPath": "/health/db",
            "requestContext": {"http": {"method": "GET"}},
            "headers": {},
        },
        None,
    )
    assert response["statusCode"] == 401


def test_health_db_success_response(monkeypatch) -> None:
    """Authenticated DB health check should return ok payload."""
    monkeypatch.setattr(
        "handlers.app.build_request_user_context",
        lambda _event: RequestUserContext(
            authenticated=True,
            user_id="u1",
            email="user@example.com",
            organization_id="org-1",
            organization_name="Org",
            token="token",
            claims={"sub": "u1"},
        ),
    )
    monkeypatch.setattr("handlers.app.probe_database", lambda: {"ok": True})

    response = lambda_handler(
        {
            "rawPath": "/health/db",
            "requestContext": {"http": {"method": "GET"}},
            "headers": {"authorization": "Bearer abc.def"},
        },
        None,
    )

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["status"] == "ok"
    assert body["database"]["ok"] is True


def test_health_db_failure_response(monkeypatch) -> None:
    """Database failures should return 503."""
    monkeypatch.setattr(
        "handlers.app.build_request_user_context",
        lambda _event: RequestUserContext(
            authenticated=True,
            user_id="u1",
            email="user@example.com",
            organization_id="org-1",
            organization_name="Org",
            token="token",
            claims={"sub": "u1"},
        ),
    )

    def _raise_probe_error() -> dict[str, bool]:
        raise RuntimeError("db unavailable")

    monkeypatch.setattr("handlers.app.probe_database", _raise_probe_error)

    response = lambda_handler(
        {
            "rawPath": "/health/db",
            "requestContext": {"http": {"method": "GET"}},
            "headers": {"authorization": "Bearer abc.def"},
        },
        None,
    )

    assert response["statusCode"] == 503
    body = json.loads(response["body"])
    assert body["status"] == "error"
    assert body["database"]["ok"] is False
