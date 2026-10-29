from datetime import timedelta

import pytest

from lending.application.use_cases.borrow_copy import BorrowCopyUseCase
from lending.conftest import TODAY
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
from lending.domain.settings import LOAN_PERIOD_DAYS, MAX_OPEN_LOANS_PER_MEMBER


class StubCatalog(CatalogInterface):
    """A catalog that knows the barcodes it is given and nothing else."""

    def __init__(self, *, copies=None, not_lendable=()):
        self._copies = copies or {}
        self._not_lendable = set(not_lendable)

    def copy_id_for_barcode(self, *, barcode):
        return self._copies.get(barcode)

    def is_lendable(self, *, copy_id):
        return copy_id not in self._not_lendable


def borrow(*, user, copy_obj, catalog=None):
    use_case = BorrowCopyUseCase(
        catalog=catalog or StubCatalog(copies={copy_obj.barcode: copy_obj.pk})
    )

    return use_case.execute(user=user, barcode=copy_obj.barcode, today=TODAY)


def test_member_borrows_for_one_loan_period(make_member, make_copy):
    member_obj = make_member()

    loan_obj = borrow(user=member_obj.user, copy_obj=make_copy())

    assert loan_obj.due_on == TODAY + timedelta(days=LOAN_PERIOD_DAYS)


def test_user_without_card_cannot_borrow(make_user, make_copy):
    with pytest.raises(MembershipRequired):
        borrow(user=make_user(), copy_obj=make_copy())


def test_suspended_member_cannot_borrow(make_member, make_copy):
    member_obj = make_member(is_suspended=True)

    with pytest.raises(MemberSuspended):
        borrow(user=member_obj.user, copy_obj=make_copy())


def test_overdue_loan_blocks_new_ones(make_member, make_copy, make_loan):
    member_obj = make_member()
    make_loan(
        member=member_obj,
        copy=make_copy(barcode="late"),
        due_on=TODAY - timedelta(days=1),
        borrowed_on=TODAY - timedelta(days=30),
    )

    with pytest.raises(OverdueLoansOutstanding):
        borrow(user=member_obj.user, copy_obj=make_copy(barcode="new"))


def test_loan_limit(make_member, make_copy, make_loan):
    member_obj = make_member()
    for number in range(MAX_OPEN_LOANS_PER_MEMBER):
        make_loan(member=member_obj, copy=make_copy(barcode=f"out-{number}"))

    with pytest.raises(LoanLimitReached):
        borrow(user=member_obj.user, copy_obj=make_copy(barcode="one-more"))


def test_unknown_barcode(make_member, make_copy):
    with pytest.raises(UnknownCopy):
        borrow(
            user=make_member().user,
            copy_obj=make_copy(),
            catalog=StubCatalog(),
        )


def test_catalog_says_copy_is_not_lendable(make_member, make_copy):
    copy_obj = make_copy()
    catalog = StubCatalog(
        copies={copy_obj.barcode: copy_obj.pk}, not_lendable=[copy_obj.pk]
    )

    with pytest.raises(CopyNotLendable):
        borrow(user=make_member().user, copy_obj=copy_obj, catalog=catalog)


def test_copy_already_out(make_member, make_copy, make_loan, make_user):
    copy_obj = make_copy()
    make_loan(member=make_member(), copy=copy_obj)
    other_member = make_member(user=make_user(username="other"))

    with pytest.raises(CopyAlreadyOnLoan):
        borrow(user=other_member.user, copy_obj=copy_obj)
