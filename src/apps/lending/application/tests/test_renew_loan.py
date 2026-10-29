from datetime import timedelta

import pytest

from lending.application.use_cases.renew_loan import RenewLoanUseCase
from lending.conftest import TODAY
from lending.domain.exceptions import LoanOverdue, RenewalLimitReached
from lending.domain.settings import LOAN_PERIOD_DAYS, MAX_RENEWALS


def renew(*, user, loan_id):
    return RenewLoanUseCase().execute(user=user, loan_id=loan_id, today=TODAY)


def test_renewal_extends_from_old_due_date(make_member, make_copy, make_loan):
    member_obj = make_member()
    due_on = TODAY + timedelta(days=5)
    loan_obj = make_loan(member=member_obj, copy=make_copy(), due_on=due_on)

    new_due_on = renew(user=member_obj.user, loan_id=loan_obj.pk)

    loan_obj.refresh_from_db()
    assert new_due_on == due_on + timedelta(days=LOAN_PERIOD_DAYS)
    assert loan_obj.renewal_count == 1


def test_overdue_loan_cannot_be_renewed(make_member, make_copy, make_loan):
    member_obj = make_member()
    loan_obj = make_loan(
        member=member_obj,
        copy=make_copy(),
        borrowed_on=TODAY - timedelta(days=30),
        due_on=TODAY - timedelta(days=1),
    )

    with pytest.raises(LoanOverdue):
        renew(user=member_obj.user, loan_id=loan_obj.pk)


def test_renewals_run_out(make_member, make_copy, make_loan):
    member_obj = make_member()
    loan_obj = make_loan(
        member=member_obj, copy=make_copy(), renewal_count=MAX_RENEWALS
    )

    with pytest.raises(RenewalLimitReached):
        renew(user=member_obj.user, loan_id=loan_obj.pk)
