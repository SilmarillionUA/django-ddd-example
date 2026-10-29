from datetime import date, timedelta

import pytest

from catalog.domain.models import Book, Copy
from lending.domain.models import Loan, Member
from lending.domain.settings import LOAN_PERIOD_DAYS

TODAY = date(2026, 3, 10)


@pytest.fixture
def make_member(db, make_user):
    def _make(*, user=None, is_suspended=False):
        return Member.objects.create(
            user=user or make_user(), is_suspended=is_suspended
        )

    return _make


@pytest.fixture
def make_copy(db):
    """
    A catalog copy for lending tests to point loans at.

    Test setup may write catalog rows directly. Only production code has
    to go through CatalogInterface.
    """

    def _make(*, barcode="copy-001", title="Test Book"):
        book_obj, _ = Book.objects.get_or_create(
            isbn="9780000000001", defaults={"title": title}
        )
        return Copy.objects.create(book=book_obj, barcode=barcode)

    return _make


@pytest.fixture
def make_loan(db):
    def _make(
        *,
        member,
        copy,
        borrowed_on=TODAY,
        due_on=None,
        returned_on=None,
        renewal_count=0,
    ):
        return Loan.objects.create(
            member=member,
            copy=copy,
            borrowed_on=borrowed_on,
            due_on=due_on or borrowed_on + timedelta(days=LOAN_PERIOD_DAYS),
            returned_on=returned_on,
            renewal_count=renewal_count,
        )

    return _make
