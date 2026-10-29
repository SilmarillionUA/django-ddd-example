from datetime import date

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext

import structlog

from catalog.domain.models import Copy
from lending.domain.interfaces import CatalogInterface, ReminderSenderInterface

logger = structlog.get_logger(__name__)

DUE_REMINDER_TEMPLATE = "lending/email/due_reminder.txt"


class CatalogGateway(CatalogInterface):
    """
    Lending's only door into the catalog app.

    Use cases never import catalog models. If the catalog moves to its
    own service one day, this class is the one thing that changes.
    """

    def copy_id_for_barcode(self, *, barcode: str) -> int | None:
        return Copy.repository.id_for_barcode(barcode=barcode)

    def is_lendable(self, *, copy_id: int) -> bool:
        return Copy.repository.is_lendable(copy_id=copy_id)


class EmailReminderSender(ReminderSenderInterface):
    def send_due_reminder(
        self, *, email: str, book_title: str, due_on: date
    ) -> None:
        send_mail(
            subject=gettext("Your library book is due soon"),
            message=render_to_string(
                DUE_REMINDER_TEMPLATE,
                {"book_title": book_title, "due_on": due_on},
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        logger.info("due_reminder.sent", due_on=due_on.isoformat())
