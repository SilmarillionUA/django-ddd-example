import logging
from datetime import date, timedelta

from lending.domain.interfaces import ReminderSenderInterface
from lending.domain.models import Loan
from lending.domain.settings import REMINDER_DAYS_BEFORE_DUE

logger = logging.getLogger(__name__)


class SendDueReminders:
    """
    Tells members about books due soon, once per loan.

    Each loan is marked right after its email goes out. If sending
    fails halfway, a retry picks up only the loans still unmarked and
    nobody gets the same email twice.
    """

    def __init__(self, *, reminder_sender: ReminderSenderInterface) -> None:
        self._reminder_sender = reminder_sender

    def execute(self, *, today: date) -> int:
        due_on = today + timedelta(days=REMINDER_DAYS_BEFORE_DUE)
        sent_count = 0

        for values in Loan.repository.needing_reminder(due_on=due_on):
            email = values.get("email")
            if not email:
                logger.info(
                    "No email for loan reminder: id=%s", values.get("id")
                )
                continue

            self._reminder_sender.send_due_reminder(
                email=email,
                book_title=values.get("book_title"),
                due_on=values.get("due_on"),
            )
            Loan.repository.mark_reminded(loan_id=values.get("id"), on=today)
            sent_count += 1

        return sent_count
