from datetime import timedelta

from lending.application.use_cases.list_my_loans import ListMyLoans
from lending.conftest import TODAY


def test_user_without_card_gets_an_empty_non_member_report(make_user):
    report = ListMyLoans().execute(user=make_user(), today=TODAY)

    assert not report.is_member
    assert not report.has_rows


def test_returned_loans_are_hidden_unless_asked(
    make_member, make_copy, make_loan
):
    member_obj = make_member()
    make_loan(member=member_obj, copy=make_copy(barcode="open"))
    make_loan(
        member=member_obj, copy=make_copy(barcode="back"), returned_on=TODAY
    )

    open_only = ListMyLoans().execute(user=member_obj.user, today=TODAY)
    everything = ListMyLoans().execute(
        user=member_obj.user, today=TODAY, include_returned=True
    )

    assert [row.barcode for row in open_only.rows] == ["open"]
    assert [row.barcode for row in everything.rows] == ["open", "back"]


def test_overdue_row_cannot_be_renewed(make_member, make_copy, make_loan):
    member_obj = make_member()
    make_loan(
        member=member_obj,
        copy=make_copy(),
        borrowed_on=TODAY - timedelta(days=30),
        due_on=TODAY - timedelta(days=2),
    )

    report = ListMyLoans().execute(user=member_obj.user, today=TODAY)

    row = report.rows[0]
    assert (row.days_left, row.is_overdue, row.can_renew) == (-2, True, False)
    assert report.overdue_count == 1
