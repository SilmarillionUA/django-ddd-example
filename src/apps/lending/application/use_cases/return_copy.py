import logging
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from lending.domain.exceptions import UnknownLoan
from lending.domain.models import Loan
from lending.domain.services.late_fees import LateFeeCalculator
from lending.domain.types import LateFee

if TYPE_CHECKING:
    from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ReturnReceipt:
    loan_id: int
    returned_on: date
    late_fee: LateFee


class ReturnCopyUseCase:
    """
    Closes a member's loan and works out the late fee once.

    The fee is stored on the loan when it closes. Changing the fee
    rules later never rewrites what a member was already charged.
    """

    def __init__(self, *, late_fees: LateFeeCalculator) -> None:
        self._late_fees = late_fees

    def execute(
        self, *, user: "User", loan_id: int, today: date
    ) -> ReturnReceipt:
        loan_obj = Loan.repository.open_for_user(
            loan_id=loan_id, user_id=user.pk
        )
        if loan_obj is None:
            raise UnknownLoan(loan_id)

        late_fee = self._late_fees.fee_for(
            due_on=loan_obj.due_on, returned_on=today
        )

        # A second click after the first one closed the loan finds it
        # closed already. That is the same "no such open loan" answer.
        closed = Loan.repository.close(
            loan_id=loan_id, returned_on=today, late_fee_cents=late_fee.cents
        )
        if not closed:
            raise UnknownLoan(loan_id)

        logger.info("Loan closed: id=%s fee=%s", loan_id, late_fee.cents)
        return ReturnReceipt(
            loan_id=loan_id, returned_on=today, late_fee=late_fee
        )
