import logging
from datetime import date, timedelta
from typing import TYPE_CHECKING

from django.db import IntegrityError, transaction

from lending.domain.exceptions import (
    CopyAlreadyOnLoan,
    CopyNotLendable,
    LoanLimitReached,
    MembershipRequired,
    MemberSuspended,
    OverdueLoansOutstanding,
    UnknownCopy,
)
from lending.domain.interfaces import CatalogInterface
from lending.domain.models import Loan, Member
from lending.domain.settings import (
    LOAN_PERIOD_DAYS,
    MAX_OPEN_LOANS_PER_MEMBER,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class BorrowCopyUseCase:
    """
    Lends one copy, found by its barcode, to the member asking for it.

    The member is checked first and the copy second. A member who may
    not borrow at all hears that, rather than a reason about one copy.
    """

    def __init__(self, *, catalog: CatalogInterface) -> None:
        self._catalog = catalog

    def execute(self, *, user: "User", barcode: str, today: date) -> Loan:
        member_obj = self._member(user=user)
        self._check_in_good_standing(member_obj=member_obj, today=today)
        copy_id = self._lendable_copy_id(barcode=barcode.strip())

        loan_obj = self._open_loan(
            member_obj=member_obj, copy_id=copy_id, today=today
        )

        logger.info("Copy lent: copy=%s member=%s", copy_id, member_obj.pk)
        return loan_obj

    @staticmethod
    def _member(*, user: "User") -> Member:
        member_obj = Member.repository.for_user(user_id=user.pk)
        if member_obj is None:
            raise MembershipRequired(user.pk)

        return member_obj

    @staticmethod
    def _check_in_good_standing(*, member_obj: Member, today: date) -> None:
        if member_obj.is_suspended:
            raise MemberSuspended(member_obj.pk)

        if Loan.repository.member_has_overdue(
            member_id=member_obj.pk, today=today
        ):
            raise OverdueLoansOutstanding(member_obj.pk)

        open_count = Loan.repository.open_count_for_member(
            member_id=member_obj.pk
        )
        if open_count >= MAX_OPEN_LOANS_PER_MEMBER:
            raise LoanLimitReached(member_obj.pk)

    def _lendable_copy_id(self, *, barcode: str) -> int:
        copy_id = self._catalog.copy_id_for_barcode(barcode=barcode)
        if copy_id is None:
            raise UnknownCopy(barcode)

        if not self._catalog.is_lendable(copy_id=copy_id):
            raise CopyNotLendable(barcode)

        if Loan.repository.is_copy_out(copy_id=copy_id):
            raise CopyAlreadyOnLoan(barcode)

        return copy_id

    @staticmethod
    def _open_loan(*, member_obj: Member, copy_id: int, today: date) -> Loan:
        # The checks above read first, so a second desk can pass them in
        # the same moment. The partial unique index decides who wins.
        try:
            with transaction.atomic():
                return Loan.objects.create(
                    member=member_obj,
                    copy_id=copy_id,
                    borrowed_on=today,
                    due_on=today + timedelta(days=LOAN_PERIOD_DAYS),
                )
        except IntegrityError as exc:
            raise CopyAlreadyOnLoan(copy_id) from exc
