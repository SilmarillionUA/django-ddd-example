from datetime import date
from typing import TYPE_CHECKING, Optional

from django.db import models
from django.db.models import F

from lending.domain.settings import MAX_RENEWALS

if TYPE_CHECKING:
    from lending.domain.models import Loan, Member


class MemberRepository(models.Manager):
    def for_user(self, *, user_id: int) -> Optional["Member"]:
        return self.get_queryset().filter(user_id=user_id).first()


class LoanQuerySet(models.QuerySet):
    def still_open(self) -> "LoanQuerySet":
        return self.filter(returned_on__isnull=True)

    def overdue(self, *, today: date) -> "LoanQuerySet":
        return self.still_open().filter(due_on__lt=today)

    def for_user(self, user_id: int) -> "LoanQuerySet":
        return self.filter(member__user_id=user_id)


class LoanRepository(models.Manager):
    def get_queryset(self) -> LoanQuerySet:
        return LoanQuerySet(self.model, using=self._db)

    def open_count_for_member(self, *, member_id: int) -> int:
        return (
            self.get_queryset()
            .still_open()
            .filter(member_id=member_id)
            .count()
        )

    def member_has_overdue(self, *, member_id: int, today: date) -> bool:
        return (
            self.get_queryset()
            .overdue(today=today)
            .filter(member_id=member_id)
            .exists()
        )

    def is_copy_out(self, *, copy_id: int) -> bool:
        return (
            self.get_queryset().still_open().filter(copy_id=copy_id).exists()
        )

    def open_for_user(self, *, loan_id: int, user_id: int) -> Optional["Loan"]:
        """
        One open loan, only if it belongs to this user.

        A loan id arrives from a URL, so a member can never act on a
        loan that is not theirs by guessing a number.
        """
        return (
            self.get_queryset()
            .still_open()
            .for_user(user_id)
            .filter(id=loan_id)
            .first()
        )

    def close(
        self, *, loan_id: int, returned_on: date, late_fee_cents: int
    ) -> bool:
        updated = (
            self.get_queryset()
            .still_open()
            .filter(id=loan_id)
            .update(returned_on=returned_on, late_fee_cents=late_fee_cents)
        )

        return updated > 0

    def extend(self, *, loan_id: int, due_on: date) -> bool:
        """
        Move the due date and count one renewal, if any are left.

        The limit sits in the UPDATE itself, so two clicks landing
        together cannot both renew past it.
        """
        updated = (
            self.get_queryset()
            .still_open()
            .filter(id=loan_id, renewal_count__lt=MAX_RENEWALS)
            .update(due_on=due_on, renewal_count=F("renewal_count") + 1)
        )

        return updated > 0

    def rows_for_user(
        self, *, user_id: int, include_returned: bool, limit: int
    ) -> LoanQuerySet:
        """
        One user's loans with plain keys, open ones first.

        The book title comes through the catalog relation here, so the
        caller never depends on the join path.
        """
        loans_qs = self.get_queryset().for_user(user_id)
        if not include_returned:
            loans_qs = loans_qs.still_open()

        return loans_qs.values(
            "id",
            "borrowed_on",
            "due_on",
            "returned_on",
            "renewal_count",
            "late_fee_cents",
            barcode=F("copy__barcode"),
            book_title=F("copy__book__title"),
        ).order_by(F("returned_on").desc(nulls_first=True), "due_on", "id")[
            :limit
        ]

    def needing_reminder(self, *, due_on: date) -> LoanQuerySet:
        return (
            self.get_queryset()
            .still_open()
            .filter(due_on=due_on, reminder_sent_on__isnull=True)
            .values(
                "id",
                "due_on",
                email=F("member__user__email"),
                book_title=F("copy__book__title"),
            )
            .order_by("id")
        )

    def mark_reminded(self, *, loan_id: int, on: date) -> None:
        self.get_queryset().filter(id=loan_id).update(reminder_sent_on=on)
