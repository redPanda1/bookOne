"""Journal workflow service and handler tests for Phase 1B."""

from __future__ import annotations

import json
import uuid
from contextlib import contextmanager
from typing import Iterator

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

import models  # noqa: F401
from auth.jwt_helper import RequestUserContext
from database.base import Base
from handlers.app import lambda_handler
from models.journal_entry_audit_history import JournalEntryAuditHistory
from models.organization import Organization
from repositories.ledger_account_repository import LedgerAccountRepository
from repositories.journal_repository import JournalRepository
from services.journal_entry_service import (
    JournalEntryConflictError,
    JournalEntryService,
    JournalEntryValidationError,
)


def _build_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return session_factory()


def _seed_organization(session: Session) -> uuid.UUID:
    org = Organization(name="Acme Corp")
    session.add(org)
    session.flush()
    return org.id


def _seed_ledger_account(
    session: Session,
    organization_id: uuid.UUID,
    *,
    account_code: str,
    name: str,
    is_active: bool = True,
) -> uuid.UUID:
    account = LedgerAccountRepository(session).create(
        {
            "organization_id": organization_id,
            "account_code": account_code,
            "name": name,
            "description": f"{name} account",
            "account_type": "Asset",
            "subtype": "CurrentAsset",
            "is_active": is_active,
        }
    )
    session.flush()
    return account.id


def _valid_draft_payload(*, account_id: uuid.UUID) -> dict[str, object]:
    return {
        "journal_number": "JE-1001",
        "entry_date": "2026-04-15",
        "description": "Office rent",
        "source_type": "manual",
        "source_reference": "web-ui",
        "lines": [
            {
                "ledger_account_id": str(account_id),
                "debit_amount": "120.00",
                "credit_amount": "0",
                "memo": "Debit",
                "line_order": 1,
            },
            {
                "ledger_account_id": str(account_id),
                "debit_amount": "0",
                "credit_amount": "120.00",
                "memo": "Credit",
                "line_order": 2,
            },
        ],
    }


@contextmanager
def _session_scope_override(session: Session) -> Iterator[Session]:
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise


def test_create_draft_journal_entry_success() -> None:
    """Service should create a draft journal with provided lines."""
    session = _build_session()
    try:
        org_id = _seed_organization(session)
        account_id = _seed_ledger_account(
            session,
            org_id,
            account_code="1000",
            name="Cash",
        )
        service = JournalEntryService(session)

        journal_entry = service.create_draft_journal_entry(
            org_id,
            _valid_draft_payload(account_id=account_id),
        )
        session.commit()

        assert journal_entry.status == "draft"
        assert journal_entry.posted_at is None
        assert journal_entry.posted_by is None
        assert len(journal_entry.lines) == 2
    finally:
        session.close()


def test_update_draft_journal_entry_replaces_lines() -> None:
    """Draft updates should replace all lines when lines payload is present."""
    session = _build_session()
    try:
        org_id = _seed_organization(session)
        account_id = _seed_ledger_account(
            session,
            org_id,
            account_code="1000",
            name="Cash",
        )
        service = JournalEntryService(session)
        created = service.create_draft_journal_entry(org_id, _valid_draft_payload(account_id=account_id))
        session.commit()
        original_line_ids = {line.id for line in created.lines}

        updated = service.update_draft_journal_entry(
            org_id,
            created.id,
            {
                "description": "Updated description",
                "lines": [
                    {
                        "ledger_account_id": str(account_id),
                        "debit_amount": "80.00",
                        "credit_amount": "0",
                        "memo": "Updated debit",
                        "line_order": 1,
                    },
                    {
                        "ledger_account_id": str(account_id),
                        "debit_amount": "0",
                        "credit_amount": "80.00",
                        "memo": "Updated credit",
                        "line_order": 2,
                    },
                ],
            },
        )
        session.commit()

        assert updated.description == "Updated description"
        assert len(updated.lines) == 2
        assert {line.id for line in updated.lines}.isdisjoint(original_line_ids)
    finally:
        session.close()


def test_post_journal_entry_success_sets_status_and_audit() -> None:
    """Posting should set posted metadata and insert one audit row."""
    session = _build_session()
    try:
        org_id = _seed_organization(session)
        account_id = _seed_ledger_account(
            session,
            org_id,
            account_code="1000",
            name="Cash",
        )
        service = JournalEntryService(session)
        created = service.create_draft_journal_entry(org_id, _valid_draft_payload(account_id=account_id))
        session.commit()

        posted = service.post_journal_entry(org_id, created.id, actor_user_id="user-123")
        session.commit()

        assert posted.status == "posted"
        assert posted.posted_by == "user-123"
        assert posted.posted_at is not None

        history_rows = session.scalars(
            select(JournalEntryAuditHistory).where(
                JournalEntryAuditHistory.organization_id == org_id,
                JournalEntryAuditHistory.entity_id == created.id,
            )
        ).all()
        assert len(history_rows) == 1
        assert history_rows[0].action == "posted"
        assert history_rows[0].from_status == "draft"
        assert history_rows[0].to_status == "posted"
        assert history_rows[0].performed_by == "user-123"
    finally:
        session.close()


def test_post_journal_entry_fails_when_unbalanced() -> None:
    """Posting should reject entries when debits and credits differ."""
    session = _build_session()
    try:
        org_id = _seed_organization(session)
        account_id = _seed_ledger_account(
            session,
            org_id,
            account_code="1000",
            name="Cash",
        )
        service = JournalEntryService(session)
        payload = _valid_draft_payload(account_id=account_id)
        payload["lines"] = [
            {
                "ledger_account_id": str(account_id),
                "debit_amount": "100.00",
                "credit_amount": "0",
                "memo": "Debit",
                "line_order": 1,
            },
            {
                "ledger_account_id": str(account_id),
                "debit_amount": "0",
                "credit_amount": "40.00",
                "memo": "Credit",
                "line_order": 2,
            },
        ]
        created = service.create_draft_journal_entry(org_id, payload)
        session.commit()

        with pytest.raises(JournalEntryValidationError, match="Total debits must equal total credits"):
            service.post_journal_entry(org_id, created.id, actor_user_id="user-123")
    finally:
        session.close()


def test_post_journal_entry_fails_with_insufficient_lines() -> None:
    """Posting should require at least two lines."""
    session = _build_session()
    try:
        org_id = _seed_organization(session)
        account_id = _seed_ledger_account(
            session,
            org_id,
            account_code="1000",
            name="Cash",
        )
        service = JournalEntryService(session)
        payload = _valid_draft_payload(account_id=account_id)
        payload["lines"] = [
            {
                "ledger_account_id": str(account_id),
                "debit_amount": "50.00",
                "credit_amount": "0",
                "memo": "Single line",
                "line_order": 1,
            }
        ]
        created = service.create_draft_journal_entry(org_id, payload)
        session.commit()

        with pytest.raises(
            JournalEntryValidationError,
            match="at least two lines",
        ):
            service.post_journal_entry(org_id, created.id, actor_user_id="user-123")
    finally:
        session.close()


def test_post_journal_entry_fails_for_inactive_account() -> None:
    """Posting should reject entries referencing inactive accounts."""
    session = _build_session()
    try:
        org_id = _seed_organization(session)
        inactive_account_id = _seed_ledger_account(
            session,
            org_id,
            account_code="1999",
            name="Old Cash",
            is_active=False,
        )
        service = JournalEntryService(session)
        created = service.create_draft_journal_entry(
            org_id,
            _valid_draft_payload(account_id=inactive_account_id),
        )
        session.commit()

        with pytest.raises(
            JournalEntryValidationError,
            match="must exist, belong to the organization, and be active",
        ):
            service.post_journal_entry(org_id, created.id, actor_user_id="user-123")
    finally:
        session.close()


def test_updating_posted_entry_is_rejected() -> None:
    """Service should enforce immutability once entry is posted."""
    session = _build_session()
    try:
        org_id = _seed_organization(session)
        account_id = _seed_ledger_account(
            session,
            org_id,
            account_code="1000",
            name="Cash",
        )
        service = JournalEntryService(session)
        created = service.create_draft_journal_entry(org_id, _valid_draft_payload(account_id=account_id))
        session.commit()

        service.post_journal_entry(org_id, created.id, actor_user_id="user-123")
        session.commit()

        with pytest.raises(JournalEntryConflictError, match="Only draft journal entries can be edited"):
            service.update_draft_journal_entry(
                org_id,
                created.id,
                {"description": "Should fail"},
            )
    finally:
        session.close()


def test_posting_rolls_back_when_audit_insert_fails() -> None:
    """Posting should not leave partial posted state if audit insert fails."""
    session = _build_session()
    try:
        org_id = _seed_organization(session)
        account_id = _seed_ledger_account(
            session,
            org_id,
            account_code="1000",
            name="Cash",
        )
        service = JournalEntryService(session)
        created = service.create_draft_journal_entry(org_id, _valid_draft_payload(account_id=account_id))
        session.commit()

        def _raise_audit_insert_error(**_kwargs: object) -> None:
            raise RuntimeError("audit write failed")

        service.journal_repository.insert_audit_history = _raise_audit_insert_error  # type: ignore[assignment]

        with pytest.raises(RuntimeError, match="audit write failed"):
            service.post_journal_entry(org_id, created.id, actor_user_id="user-123")
            session.commit()
        session.rollback()

        reloaded = JournalRepository(session).get_by_id(org_id, created.id)
        assert reloaded is not None
        assert reloaded.status == "draft"
        assert reloaded.posted_at is None
        assert reloaded.posted_by is None
    finally:
        session.close()


def test_create_and_post_endpoints() -> None:
    """Handlers should create draft entries and post them."""
    session = _build_session()
    try:
        org_id = _seed_organization(session)
        account_id = _seed_ledger_account(
            session,
            org_id,
            account_code="1000",
            name="Cash",
        )

        def _build_user_context(_event: dict[str, object]) -> RequestUserContext:
            return RequestUserContext(
                authenticated=True,
                user_id="api-user",
                email="api@example.com",
                organization_id=str(org_id),
                organization_name="Acme Corp",
                token="token",
                claims={"sub": "api-user"},
            )

        payload = _valid_draft_payload(account_id=account_id)
        create_event = {
            "rawPath": "/journal-entries",
            "requestContext": {"http": {"method": "POST"}},
            "headers": {"authorization": "Bearer token"},
            "body": json.dumps(payload),
        }

        with pytest.MonkeyPatch.context() as monkeypatch:
            monkeypatch.setattr("handlers.app.build_request_user_context", _build_user_context)
            monkeypatch.setattr("handlers.app.session_scope", lambda: _session_scope_override(session))

            create_response = lambda_handler(create_event, None)
            assert create_response["statusCode"] == 201
            created_body = json.loads(create_response["body"])
            created_id = created_body["journal_entry"]["id"]
            assert created_body["journal_entry"]["status"] == "draft"

            post_event = {
                "rawPath": f"/journal-entries/{created_id}/post",
                "requestContext": {"http": {"method": "POST"}},
                "headers": {"authorization": "Bearer token"},
            }
            post_response = lambda_handler(post_event, None)
            assert post_response["statusCode"] == 200
            posted_body = json.loads(post_response["body"])
            assert posted_body["journal_entry"]["status"] == "posted"
            assert posted_body["journal_entry"]["posted_by"] == "api-user"
    finally:
        session.close()
