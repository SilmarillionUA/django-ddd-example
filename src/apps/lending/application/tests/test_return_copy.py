from datetime import timedelta

import pytest

from lending.application.use_cases.return_copy import ReturnCopyUseCase
from lending.conftest import TODAY
from lending.domain.exceptions import UnknownLoan
from lending.domain.services.late_fees import LateFeeCalculator, LateFeePolicy

POLICY = LateFeePolicy(cents_per_day=10, grace_days=0, max_cents=1000)


def return_loan(*, user, loan_id):
    use_case = ReturnCopyUseCase(late_fees=LateFeeCalculator(policy=POLICY))

    return use_case.execute(user=user, loan_id=loan_id, today=TODAY)


def test_late_return_stores_the_fee(make_member, make_copy, make_loan):
    member_obj = make_member()
    loan_obj = make_loan(
        member=member_obj,
        copy=make_copy(),
        borrowed_on=TODAY - timedelta(days=30),
        due_on=TODAY - timedelta(days=3),
    )

    receipt = return_loan(user=member_obj.user, loan_id=loan_obj.pk)

    loan_obj.refresh_from_db()
    assert receipt.late_fee.cents == 30
    assert (loan_obj.returned_on, loan_obj.late_fee_cents) == (TODAY, 30)


def test_second_return_is_an_unknown_loan(make_member, make_copy, make_loan):
    member_obj = make_member()
    loan_obj = make_loan(member=member_obj, copy=make_copy())
    return_loan(user=member_obj.user, loan_id=loan_obj.pk)

    with pytest.raises(UnknownLoan):
        return_loan(user=member_obj.user, loan_id=loan_obj.pk)


def test_member_cannot_return_another_members_loan(
    make_member, make_copy, make_loan, make_user
):
    loan_obj = make_loan(member=make_member(), copy=make_copy())

    with pytest.raises(UnknownLoan):
        return_loan(user=make_user(username="stranger"), loan_id=loan_obj.pk)
