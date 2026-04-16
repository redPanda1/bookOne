"""Tests for GL account creation endpoint."""

from __future__ import annotations

import json
import uuid
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import models  # noqa: F401
from auth.jwt_helper import RequestUserContext
from database.base import Base
from handlers.app import lambda_handler
from models.organization import Organization


def _build_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return session_factory()


@contextmanager
def _session_scope_override(session: Session) -> Iterator[Session]:
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise


def _seed_organization(session: Session) -> uuid.UUID:
    org = Organization(name="Acme Corp")
    session.add(org)
    session.flush()
    return org.id


def test_create_gl_account_requires_authentication(monkeypatch) -> None:
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
            "rawPath": "/gl-accounts",
            "requestContext": {"http": {"method": "POST"}},
            "headers": {},
            "body": json.dumps({}),
        },
        None,
    )
    assert response["statusCode"] == 401


def test_create_gl_account_success(monkeypatch) -> None:
    """POST /gl-accounts should create one tenant-scoped account."""
    session = _build_session()
    try:
        org_id = _seed_organization(session)

        monkeypatch.setattr(
            "handlers.app.build_request_user_context",
            lambda _event: RequestUserContext(
                authenticated=True,
                user_id="u1",
                email="user@example.com",
                organization_id=str(org_id),
                organization_name="Org",
                token="token",
                claims={"sub": "u1"},
            ),
        )
        monkeypatch.setattr("handlers.app.session_scope", lambda: _session_scope_override(session))

        response = lambda_handler(
            {
                "rawPath": "/gl-accounts",
                "requestContext": {"http": {"method": "POST"}},
                "headers": {"authorization": "Bearer abc.def"},
                "body": json.dumps(
                    {
                        "account_code": "1000",
                        "name": "Cash",
                        "description": "Operating cash",
                        "account_type": "Asset",
                        "subtype": "Bank",
                        "is_active": True,
                    }
                ),
            },
            None,
        )

        assert response["statusCode"] == 201
        body = json.loads(response["body"])
        assert body["gl_account"]["account_code"] == "1000"
        assert body["gl_account"]["name"] == "Cash"
        assert body["gl_account"]["organization_id"] == str(org_id)
    finally:
        session.close()


def test_create_gl_account_validation_error(monkeypatch) -> None:
    """Endpoint should return 400 when required fields are missing."""
    session = _build_session()
    try:
        org_id = _seed_organization(session)

        monkeypatch.setattr(
            "handlers.app.build_request_user_context",
            lambda _event: RequestUserContext(
                authenticated=True,
                user_id="u1",
                email="user@example.com",
                organization_id=str(org_id),
                organization_name="Org",
                token="token",
                claims={"sub": "u1"},
            ),
        )
        monkeypatch.setattr("handlers.app.session_scope", lambda: _session_scope_override(session))

        response = lambda_handler(
            {
                "rawPath": "/gl-accounts",
                "requestContext": {"http": {"method": "POST"}},
                "headers": {"authorization": "Bearer abc.def"},
                "body": json.dumps(
                    {
                        "name": "Cash",
                        "account_type": "Asset",
                    }
                ),
            },
            None,
        )

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "account_code" in body["message"]
    finally:
        session.close()
