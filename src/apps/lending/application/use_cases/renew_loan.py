import logging
from datetime import date, timedelta
from typing import TYPE_CHECKING

from lending.domain.exceptions import (
    LoanOverdue,
    RenewalLimitReached,
    UnknownLoan,
)
from lending.domain.models import Loan
from lending.domain.settings import LOAN_PERIOD_DAYS

if TYPE_CHECKING:
    from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class RenewLoanUseCase:
    """
    Gives a member another loan period on a book they still have.

    The new period starts from the old due date, not from today, so
    renewing early never costs the member days they already had. An
    overdue loan cannot be renewed: the book goes back first.
    """

    def execute(self, *, user: "User", loan_id: int, today: date) -> date:
        loan_obj = Loan.repository.open_for_user(
            loan_id=loan_id, user_id=user.pk
        )
        if loan_obj is None:
            raise UnknownLoan(loan_id)

        if loan_obj.due_on < today:
            raise LoanOverdue(loan_id)

        new_due_on = loan_obj.due_on + timedelta(days=LOAN_PERIOD_DAYS)
        if not Loan.repository.extend(loan_id=loan_id, due_on=new_due_on):
            raise RenewalLimitReached(loan_id)

        logger.info("Loan renewed: id=%s due=%s", loan_id, new_due_on)
        return new_due_on
