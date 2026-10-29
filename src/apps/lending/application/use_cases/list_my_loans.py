from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from lending.domain.models import Loan, Member
from lending.domain.settings import (
    CENTS_PER_UNIT,
    MAX_LOANS_ON_PAGE,
    MAX_RENEWALS,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import User


@dataclass(frozen=True)
class LoanRow:
    """
    One loan as a member sees it on a given day.

    Every field that depends on "today" is worked out by the use case,
    so the template and the API never read the clock themselves.
    """

    loan_id: int
    book_title: str
    barcode: str
    borrowed_on: date
    due_on: date
    returned_on: date | None = None
    renewal_count: int = 0
    late_fee_cents: int = 0
    days_left: int = 0

    @property
    def is_open(self) -> bool:
        return self.returned_on is None

    @property
    def is_overdue(self) -> bool:
        return self.is_open and self.days_left < 0

    @property
    def late_fee_amount(self) -> Decimal:
        return Decimal(self.late_fee_cents) / CENTS_PER_UNIT

    @property
    def can_renew(self) -> bool:
        return (
            self.is_open
            and not self.is_overdue
            and self.renewal_count < MAX_RENEWALS
        )


@dataclass(frozen=True)
class MyLoansReport:
    """
    A member's loans for the page and the API.

    `is_member` is False for a user without a library card, so the
    page can say how to get one instead of showing an empty table.
    """

    is_member: bool = False
    include_returned: bool = False
    max_loans: int = MAX_LOANS_ON_PAGE
    rows: list[LoanRow] = field(default_factory=list)

    @property
    def has_rows(self) -> bool:
        return bool(self.rows)

    @property
    def overdue_count(self) -> int:
        return sum(1 for row in self.rows if row.is_overdue)


class ListMyLoans:
    def execute(
        self,
        *,
        user: "User",
        today: date,
        include_returned: bool = False,
        limit: int = MAX_LOANS_ON_PAGE,
    ) -> MyLoansReport:
        if Member.repository.for_user(user_id=user.pk) is None:
            return MyLoansReport(include_returned=include_returned)

        values_rows = Loan.repository.rows_for_user(
            user_id=user.pk, include_returned=include_returned, limit=limit
        )

        return MyLoansReport(
            is_member=True,
            include_returned=include_returned,
            max_loans=limit,
            rows=[
                self._row(values=values, today=today) for values in values_rows
            ],
        )

    @staticmethod
    def _row(*, values: dict[str, Any], today: date) -> LoanRow:
        due_on = values.get("due_on")

        return LoanRow(
            loan_id=values.get("id"),
            book_title=values.get("book_title"),
            barcode=values.get("barcode"),
            borrowed_on=values.get("borrowed_on"),
            due_on=due_on,
            returned_on=values.get("returned_on"),
            renewal_count=values.get("renewal_count"),
            late_fee_cents=values.get("late_fee_cents"),
            days_left=(due_on - today).days,
        )
