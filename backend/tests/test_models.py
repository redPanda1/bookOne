"""Model integrity tests."""

from __future__ import annotations

from models.journal_line import JournalLine
from models.ledger_account import LedgerAccount


def test_ledger_account_table_metadata() -> None:
    """LedgerAccount should expose expected indexed columns."""
    table = LedgerAccount.__table__
    assert "account_code" in table.c
    assert "account_type" in table.c
    assert any(index.name == "ix_ledger_accounts_org_account_code" for index in table.indexes)


def test_journal_line_financial_precision() -> None:
    """JournalLine amounts should be configured for accounting precision."""
    debit_column = JournalLine.__table__.c.debit_amount
    credit_column = JournalLine.__table__.c.credit_amount
    assert debit_column.type.precision == 18
    assert debit_column.type.scale == 2
    assert credit_column.type.precision == 18
    assert credit_column.type.scale == 2

    check_constraint_names = {constraint.name for constraint in JournalLine.__table__.constraints}
    assert any("journal_lines_amount_non_negative" in name for name in check_constraint_names if name)
    assert any("journal_lines_single_sided_amount" in name for name in check_constraint_names if name)
