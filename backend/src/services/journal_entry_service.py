"""Journal entry workflow service."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from models.journal_entry import JournalEntry
from models.journal_line import JournalLine
from repositories.journal_repository import JournalRepository
from repositories.ledger_account_repository import LedgerAccountRepository

JOURNAL_STATUS_DRAFT = "draft"
JOURNAL_STATUS_POSTED = "posted"
_ENTRY_MUTABLE_FIELDS = {"journal_number", "entry_date", "description", "source_type", "source_reference"}


class JournalEntryServiceError(Exception):
    """Base exception for journal workflow errors."""


class JournalEntryValidationError(JournalEntryServiceError):
    """Raised when business validations fail."""


class JournalEntryNotFoundError(JournalEntryServiceError):
    """Raised when the journal entry cannot be found for a tenant."""


class JournalEntryConflictError(JournalEntryServiceError):
    """Raised when requested state transition is invalid."""


class JournalEntryNotImplementedError(JournalEntryServiceError):
    """Raised when a workflow action is intentionally scaffolded."""


class JournalEntryService:
    """Service-layer business logic for journal entry workflows."""

    def __init__(self, session: Session):
        self.session = session
        self.journal_repository = JournalRepository(session)
        self.ledger_account_repository = LedgerAccountRepository(session)

    def create_draft_journal_entry(
        self,
        organization_id: UUID,
        payload: dict[str, Any],
    ) -> JournalEntry:
        """Create a draft journal entry and optional lines."""
        create_payload = self._normalize_entry_payload(payload)
        create_payload["organization_id"] = organization_id
        create_payload["status"] = JOURNAL_STATUS_DRAFT
        create_payload["posted_at"] = None
        create_payload["posted_by"] = None

        lines_payload = create_payload.get("lines", [])
        if lines_payload:
            self._validate_ledger_accounts(
                organization_id=organization_id,
                lines_payload=lines_payload,
                require_active=False,
            )

        return self.journal_repository.create(create_payload)

    def update_draft_journal_entry(
        self,
        organization_id: UUID,
        journal_entry_id: UUID,
        payload: dict[str, Any],
    ) -> JournalEntry:
        """Update mutable fields for draft journal entries."""
        journal_entry = self.journal_repository.get_by_id(organization_id, journal_entry_id)
        if journal_entry is None:
            raise JournalEntryNotFoundError("Journal entry was not found")
        self._validate_editable_status(journal_entry.status)

        update_payload = self._normalize_update_payload(payload)
        if update_payload:
            self.journal_repository.update(journal_entry, update_payload)

        if "lines" in payload:
            raw_lines = payload.get("lines")
            if not isinstance(raw_lines, list):
                raise JournalEntryValidationError("'lines' must be an array when provided")

            normalized_lines = self._normalize_lines_payload(raw_lines)
            self._validate_ledger_accounts(
                organization_id=organization_id,
                lines_payload=normalized_lines,
                require_active=False,
            )
            journal_entry = self.journal_repository.replace_lines(journal_entry, normalized_lines)

        self._validate_existing_lines_shape(journal_entry.lines)
        return journal_entry

    def post_journal_entry(
        self,
        organization_id: UUID,
        journal_entry_id: UUID,
        actor_user_id: str,
        metadata_json: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """Post one draft journal entry after accounting validations."""
        journal_entry = self.journal_repository.get_by_id(organization_id, journal_entry_id)
        if journal_entry is None:
            raise JournalEntryNotFoundError("Journal entry was not found")
        self._validate_postable_status(journal_entry.status)

        normalized_lines = [self._line_model_to_payload(line) for line in journal_entry.lines]
        self._validate_postable_lines(normalized_lines)
        self._validate_ledger_accounts(
            organization_id=organization_id,
            lines_payload=normalized_lines,
            require_active=True,
        )

        now_utc = datetime.now(tz=UTC)
        self.journal_repository.update(
            journal_entry,
            {
                "status": JOURNAL_STATUS_POSTED,
                "posted_at": now_utc,
                "posted_by": actor_user_id,
            },
        )
        self.journal_repository.insert_audit_history(
            organization_id=organization_id,
            entity_id=journal_entry.id,
            action="posted",
            from_status=JOURNAL_STATUS_DRAFT,
            to_status=JOURNAL_STATUS_POSTED,
            performed_by=actor_user_id,
            metadata_json=metadata_json,
        )
        return journal_entry

    def reverse_journal_entry(
        self,
        organization_id: UUID,
        journal_entry_id: UUID,
        actor_user_id: str,
    ) -> JournalEntry:
        """Scaffold for reversal workflow; implementation deferred."""
        del organization_id, journal_entry_id, actor_user_id
        raise JournalEntryNotImplementedError(
            "reverse_journal_entry is scaffolded for a future phase"
        )

    def _normalize_entry_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise JournalEntryValidationError("Request payload must be an object")

        normalized = {
            "journal_number": self._read_required_string(payload, "journal_number"),
            "entry_date": self._coerce_date(payload.get("entry_date"), "entry_date"),
            "description": self._read_optional_string(payload, "description"),
            "source_type": self._read_optional_string(payload, "source_type"),
            "source_reference": self._read_optional_string(payload, "source_reference"),
        }
        raw_lines = payload.get("lines", [])
        if not isinstance(raw_lines, list):
            raise JournalEntryValidationError("'lines' must be an array")
        normalized["lines"] = self._normalize_lines_payload(raw_lines)
        return normalized

    def _normalize_update_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise JournalEntryValidationError("Request payload must be an object")

        normalized: dict[str, Any] = {}
        for field_name in _ENTRY_MUTABLE_FIELDS:
            if field_name not in payload:
                continue
            if field_name == "entry_date":
                normalized[field_name] = self._coerce_date(payload.get(field_name), field_name)
                continue
            if field_name == "journal_number":
                normalized[field_name] = self._read_required_string(payload, field_name)
                continue
            normalized[field_name] = self._read_optional_string(payload, field_name)
        return normalized

    def _normalize_lines_payload(self, lines: list[object]) -> list[dict[str, Any]]:
        normalized_lines: list[dict[str, Any]] = []
        for index, line in enumerate(lines, start=1):
            if not isinstance(line, dict):
                raise JournalEntryValidationError(f"Line {index} must be an object")

            ledger_account_id_raw = line.get("ledger_account_id")
            if ledger_account_id_raw is None:
                raise JournalEntryValidationError(f"Line {index} missing ledger_account_id")

            normalized_line = {
                "ledger_account_id": self._coerce_uuid(ledger_account_id_raw, f"lines[{index}].ledger_account_id"),
                "debit_amount": self._coerce_decimal(line.get("debit_amount", "0"), f"lines[{index}].debit_amount"),
                "credit_amount": self._coerce_decimal(
                    line.get("credit_amount", "0"), f"lines[{index}].credit_amount"
                ),
                "memo": self._read_optional_line_memo(line.get("memo")),
                "line_order": self._coerce_positive_int(line.get("line_order"), f"lines[{index}].line_order"),
            }
            self._validate_single_sided_amounts(normalized_line, index)
            normalized_lines.append(normalized_line)
        return normalized_lines

    def _validate_editable_status(self, status: str) -> None:
        if status != JOURNAL_STATUS_DRAFT:
            raise JournalEntryConflictError("Only draft journal entries can be edited")

    def _validate_postable_status(self, status: str) -> None:
        if status != JOURNAL_STATUS_DRAFT:
            raise JournalEntryConflictError("Only draft journal entries can be posted")

    def _validate_postable_lines(self, lines_payload: list[dict[str, Any]]) -> None:
        if len(lines_payload) < 2:
            raise JournalEntryValidationError("Journal entry must contain at least two lines to post")

        total_debits = sum((line["debit_amount"] for line in lines_payload), Decimal("0"))
        total_credits = sum((line["credit_amount"] for line in lines_payload), Decimal("0"))
        if total_debits != total_credits:
            raise JournalEntryValidationError("Total debits must equal total credits")

    def _validate_existing_lines_shape(self, lines: list[JournalLine]) -> None:
        for index, line in enumerate(lines, start=1):
            line_payload = self._line_model_to_payload(line)
            self._validate_single_sided_amounts(line_payload, index)

    def _validate_ledger_accounts(
        self,
        *,
        organization_id: UUID,
        lines_payload: list[dict[str, Any]],
        require_active: bool,
    ) -> None:
        account_ids = {line["ledger_account_id"] for line in lines_payload}
        if not account_ids:
            return

        accounts = self.ledger_account_repository.get_by_ids(
            organization_id,
            account_ids,
            include_inactive=not require_active,
        )
        found_ids = {account.id for account in accounts}
        missing_ids = sorted(str(account_id) for account_id in account_ids if account_id not in found_ids)
        if missing_ids:
            if require_active:
                raise JournalEntryValidationError(
                    "Referenced ledger accounts must exist, belong to the organization, and be active"
                )
            raise JournalEntryValidationError(
                "Referenced ledger accounts must exist and belong to the organization"
            )

    def _line_model_to_payload(self, line: JournalLine) -> dict[str, Any]:
        return {
            "ledger_account_id": line.ledger_account_id,
            "debit_amount": Decimal(line.debit_amount),
            "credit_amount": Decimal(line.credit_amount),
            "memo": line.memo,
            "line_order": line.line_order,
        }

    def _validate_single_sided_amounts(self, line_payload: dict[str, Any], line_index: int) -> None:
        debit_amount = line_payload["debit_amount"]
        credit_amount = line_payload["credit_amount"]
        if debit_amount < 0 or credit_amount < 0:
            raise JournalEntryValidationError(f"Line {line_index} amounts must be non-negative")
        if (debit_amount == 0 and credit_amount == 0) or (
            debit_amount > 0 and credit_amount > 0
        ):
            raise JournalEntryValidationError(
                f"Line {line_index} must have exactly one positive side (debit or credit)"
            )

    def _read_required_string(self, payload: dict[str, Any], field_name: str) -> str:
        value = payload.get(field_name)
        if not isinstance(value, str) or not value.strip():
            raise JournalEntryValidationError(f"'{field_name}' is required")
        return value.strip()

    def _read_optional_string(self, payload: dict[str, Any], field_name: str) -> str | None:
        value = payload.get(field_name)
        if value is None:
            return None
        if not isinstance(value, str):
            raise JournalEntryValidationError(f"'{field_name}' must be a string when provided")
        stripped = value.strip()
        return stripped or None

    def _read_optional_line_memo(self, value: object) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise JournalEntryValidationError("'memo' must be a string when provided")
        stripped = value.strip()
        return stripped or None

    def _coerce_date(self, value: object, field_name: str) -> date:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if not isinstance(value, str):
            raise JournalEntryValidationError(f"'{field_name}' must be an ISO date string")
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise JournalEntryValidationError(f"'{field_name}' must be a valid ISO date") from exc

    def _coerce_decimal(self, value: object, field_name: str) -> Decimal:
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError) as exc:
            raise JournalEntryValidationError(f"'{field_name}' must be a decimal number") from exc

    def _coerce_positive_int(self, value: object, field_name: str) -> int:
        if not isinstance(value, int) or value <= 0:
            raise JournalEntryValidationError(f"'{field_name}' must be a positive integer")
        return value

    def _coerce_uuid(self, value: object, field_name: str) -> UUID:
        try:
            return UUID(str(value))
        except (TypeError, ValueError) as exc:
            raise JournalEntryValidationError(f"'{field_name}' must be a valid UUID") from exc
