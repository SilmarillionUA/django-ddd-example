from datetime import timedelta

from django.db import IntegrityError

import pytest

from lending.conftest import TODAY
from lending.domain.models import Loan
from lending.domain.settings import MAX_RENEWALS


def test_second_open_loan_on_one_copy_is_refused_by_the_database(
    make_member, make_copy, make_loan, make_user
):
    copy_obj = make_copy()
    make_loan(member=make_member(), copy=copy_obj)
    other_member = make_member(user=make_user(username="other"))

    with pytest.raises(IntegrityError):
        make_loan(member=other_member, copy=copy_obj)


def test_returned_loan_frees_the_copy(make_member, make_copy, make_loan):
    member_obj = make_member()
    copy_obj = make_copy()
    make_loan(member=member_obj, copy=copy_obj, returned_on=TODAY)

    make_loan(member=member_obj, copy=copy_obj)

    assert Loan.repository.is_copy_out(copy_id=copy_obj.pk)


def test_overdue_means_open_and_past_due(make_member, make_copy, make_loan):
    member_obj = make_member()
    make_loan(
        member=member_obj,
        copy=make_copy(barcode="late"),
        borrowed_on=TODAY - timedelta(days=30),
        due_on=TODAY - timedelta(days=1),
    )

    assert Loan.repository.member_has_overdue(
        member_id=member_obj.pk, today=TODAY
    )
    assert not Loan.repository.member_has_overdue(
        member_id=member_obj.pk, today=TODAY - timedelta(days=1)
    )


def test_extend_stops_at_renewal_limit(make_member, make_copy, make_loan):
    loan_obj = make_loan(
        member=make_member(), copy=make_copy(), renewal_count=MAX_RENEWALS
    )

    assert not Loan.repository.extend(loan_id=loan_obj.pk, due_on=TODAY)


def test_open_for_user_hides_other_members_loans(
    make_member, make_copy, make_loan, make_user
):
    loan_obj = make_loan(member=make_member(), copy=make_copy())
    stranger = make_user(username="stranger")

    assert (
        Loan.repository.open_for_user(loan_id=loan_obj.pk, user_id=stranger.pk)
        is None
    )
