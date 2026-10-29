from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _

from lending.domain.managers import LoanRepository, MemberRepository


class Member(models.Model):
    """
    A user who holds a library card.

    Logging in is not enough to borrow. A librarian creates the member
    row after checking who the person is.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="library_member",
        verbose_name=_("User"),
    )
    is_suspended = models.BooleanField(_("Suspended"), default=False)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    objects = models.Manager()
    repository = MemberRepository()

    class Meta:
        verbose_name = _("Member")
        verbose_name_plural = _("Members")

    def __str__(self) -> str:
        return str(self.user)


class Loan(models.Model):
    """
    One copy in one member's hands, from the day it left to its return.

    A loan is closed by setting `returned_on`, never by deleting it, so
    the history of a copy and a member stays readable.
    """

    member = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        related_name="loans",
        verbose_name=_("Member"),
    )
    # Lending points at catalog copies but asks the catalog about them
    # only through CatalogInterface. The foreign key is for integrity.
    copy = models.ForeignKey(
        "catalog.Copy",
        on_delete=models.PROTECT,
        related_name="loans",
        verbose_name=_("Copy"),
    )
    borrowed_on = models.DateField(_("Borrowed on"))
    due_on = models.DateField(_("Due on"))
    returned_on = models.DateField(_("Returned on"), null=True, blank=True)
    renewal_count = models.PositiveSmallIntegerField(_("Renewals"), default=0)
    late_fee_cents = models.PositiveIntegerField(
        _("Late fee, cents"), default=0
    )
    reminder_sent_on = models.DateField(
        _("Reminder sent on"), null=True, blank=True
    )

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    objects = models.Manager()
    repository = LoanRepository()

    class Meta:
        ordering = ["-borrowed_on", "-id"]
        verbose_name = _("Loan")
        verbose_name_plural = _("Loans")
        constraints = [
            # Two desks lending the same copy at the same moment both pass
            # the use case check. This index lets only one of them win.
            models.UniqueConstraint(
                fields=["copy"],
                condition=Q(returned_on__isnull=True),
                name="lending_one_open_loan_per_copy",
            ),
            models.CheckConstraint(
                condition=Q(due_on__gte=F("borrowed_on")),
                name="lending_due_not_before_borrowed",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.copy_id}@{self.member_id}"

    @property
    def is_open(self) -> bool:
        return self.returned_on is None
