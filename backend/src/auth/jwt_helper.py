"""Minimal JWT/auth scaffold for request context building."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import jwt


@dataclass(frozen=True)
class RequestUserContext:
    """Normalized request identity payload for handlers/services."""

    authenticated: bool
    user_id: str
    email: str
    organization_id: str
    organization_name: str
    token: str | None
    claims: dict[str, Any]


def extract_authorization_header(event: dict[str, Any]) -> str | None:
    """Extract Authorization header from API Gateway event."""
    headers = event.get("headers") or {}
    if not isinstance(headers, dict):
        return None

    for key, value in headers.items():
        if isinstance(key, str) and key.lower() == "authorization":
            return value if isinstance(value, str) else None
    return None


def parse_bearer_token(authorization_header: str | None) -> str | None:
    """Parse bearer token from Authorization header."""
    if not authorization_header:
        return None

    parts = authorization_header.strip().split(" ", 1)
    if len(parts) != 2:
        return None

    scheme, token = parts[0], parts[1].strip()
    if scheme.lower() != "bearer" or not token:
        return None
    return token


def _decode_token_without_verification(token: str) -> dict[str, Any]:
    """Decode token payload without signature verification (scaffold only)."""
    return jwt.decode(
        token,
        options={
            "verify_signature": False,
            "verify_exp": False,
            "verify_aud": False,
            "verify_iss": False,
        },
    )


def _mock_claims_from_token(token: str) -> dict[str, Any]:
    """Fallback mock claims when token is not a decodable JWT."""
    return {
        "sub": token,
        "email": "mock@example.com",
        "custom:organization_id": "mock-org",
        "custom:organization_name": "Mock Organization",
    }


def build_request_user_context(event: dict[str, Any]) -> RequestUserContext:
    """Build request user context from JWT claims or bearer token.

    This is a scaffold: real Cognito/JWKS validation should replace decode logic.
    """
    claims = (
        event.get("requestContext", {})
        .get("authorizer", {})
        .get("jwt", {})
        .get("claims", {})
    )

    token = None
    if not claims:
        auth_header = extract_authorization_header(event)
        token = parse_bearer_token(auth_header)
        if token:
            try:
                claims = _decode_token_without_verification(token)
            except jwt.PyJWTError:
                claims = _mock_claims_from_token(token)

    if not isinstance(claims, dict):
        claims = {}

    authenticated = bool(claims)
    return RequestUserContext(
        authenticated=authenticated,
        user_id=str(claims.get("sub", "mock-user")),
        email=str(claims.get("email", "mock@example.com")),
        organization_id=str(claims.get("custom:organization_id", "mock-org")),
        organization_name=str(
            claims.get("custom:organization_name", "Mock Organization")
        ),
        token=token,
        claims=claims,
    )
