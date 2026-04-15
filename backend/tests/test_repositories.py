"""Repository CRUD tests."""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import models  # noqa: F401
from database.base import Base
from models.organization import Organization
from repositories.entity_repository import EntityRepository
from repositories.financial_account_repository import FinancialAccountRepository
from repositories.journal_repository import JournalRepository
from repositories.ledger_account_repository import LedgerAccountRepository


def _build_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return Session(bind=engine, autoflush=False, expire_on_commit=False)


def _seed_organization(session: Session) -> uuid.UUID:
    org = Organization(name="Acme Corp")
    session.add(org)
    session.flush()
    return org.id


def test_ledger_account_repository_crud_soft_delete() -> None:
    """LedgerAccountRepository should support create/read/update/soft delete."""
    session = _build_session()
    try:
        org_id = _seed_organization(session)
        repository = LedgerAccountRepository(session)

        created = repository.create(
            {
                "organization_id": org_id,
                "account_code": "1000",
                "name": "Cash",
                "description": "Primary bank cash account",
                "account_type": "Asset",
                "subtype": "Bank",
            }
        )
        session.commit()

        fetched = repository.get_by_id(org_id, created.id)
        assert fetched is not None
        assert fetched.name == "Cash"

        updated = repository.update(created, {"name": "Operating Cash"})
        session.commit()
        assert updated.name == "Operating Cash"

        deleted = repository.soft_delete(org_id, created.id)
        session.commit()
        assert deleted is not None
        assert deleted.is_active is False
    finally:
        session.close()


def test_entity_and_financial_account_repository_list_filters() -> None:
    """Entity and FinancialAccount repositories should support typed filtering."""
    session = _build_session()
    try:
        org_id = _seed_organization(session)
        entity_repository = EntityRepository(session)
        financial_repository = FinancialAccountRepository(session)

        entity_repository.create(
            {
                "organization_id": org_id,
                "entity_type": "customer",
                "legal_name": "Example Customer LLC",
                "display_name": "Example Customer",
            }
        )
        entity_repository.create(
            {
                "organization_id": org_id,
                "entity_type": "vendor",
                "legal_name": "Office Supplies Inc",
                "display_name": "Office Supplies",
            }
        )
        financial_repository.create(
            {
                "organization_id": org_id,
                "institution_name": "Bank A",
                "account_name": "Operating",
                "account_type": "bank",
                "currency": "USD",
            }
        )
        session.commit()

        customers = entity_repository.list(org_id, entity_type="customer")
        bank_accounts = financial_repository.list(org_id, account_type="bank")
        assert len(customers) == 1
        assert customers[0].entity_type == "customer"
        assert len(bank_accounts) == 1
        assert bank_accounts[0].account_type == "bank"
    finally:
        session.close()


def test_journal_repository_crud() -> None:
    """JournalRepository should support create/read/list/update."""
    session = _build_session()
    try:
        org_id = _seed_organization(session)
        account_repository = LedgerAccountRepository(session)
        journal_repository = JournalRepository(session)

        ledger_account = account_repository.create(
            {
                "organization_id": org_id,
                "account_code": "2000",
                "name": "Accounts Payable",
                "description": "A/P control",
                "account_type": "Liability",
                "subtype": "AccountsPayable",
            }
        )
        journal = journal_repository.create(
            {
                "organization_id": org_id,
                "journal_number": "JE-0001",
                "entry_date": date(2026, 4, 14),
                "description": "Opening entry",
                "source_type": "manual",
                "source_reference": "seed",
                "status": "draft",
                "lines": [
                    {
                        "ledger_account_id": ledger_account.id,
                        "debit_amount": Decimal("100.00"),
                        "credit_amount": Decimal("0.00"),
                        "memo": "Debit line",
                        "line_order": 1,
                    },
                    {
                        "ledger_account_id": ledger_account.id,
                        "debit_amount": Decimal("0.00"),
                        "credit_amount": Decimal("100.00"),
                        "memo": "Credit line",
                        "line_order": 2,
                    },
                ],
            }
        )
        session.commit()

        fetched = journal_repository.get_by_id(org_id, journal.id)
        assert fetched is not None
        assert fetched.journal_number == "JE-0001"
        assert len(fetched.lines) == 2

        journal_repository.update(journal, {"status": "posted"})
        session.commit()
        posted_journals = journal_repository.list(org_id, status="posted")
        assert len(posted_journals) == 1
    finally:
        session.close()
