from datetime import timedelta

from lending.application.use_cases.send_due_reminders import SendDueReminders
from lending.conftest import TODAY
from lending.domain.interfaces import ReminderSenderInterface
from lending.domain.settings import REMINDER_DAYS_BEFORE_DUE

DUE_SOON = TODAY + timedelta(days=REMINDER_DAYS_BEFORE_DUE)


class RecordingSender(ReminderSenderInterface):
    def __init__(self):
        self.sent = []

    def send_due_reminder(self, *, email, book_title, due_on):
        self.sent.append((email, book_title, due_on))


def test_each_loan_due_soon_is_reminded_once(
    make_member, make_copy, make_loan
):
    make_loan(
        member=make_member(),
        copy=make_copy(title="Dune"),
        due_on=DUE_SOON,
    )
    sender = RecordingSender()
    use_case = SendDueReminders(reminder_sender=sender)

    first_run = use_case.execute(today=TODAY)
    second_run = use_case.execute(today=TODAY)

    assert (first_run, second_run) == (1, 0)
    assert sender.sent == [("reader@example.com", "Dune", DUE_SOON)]


def test_member_without_email_is_skipped(
    make_member, make_copy, make_loan, make_user
):
    member_obj = make_member(user=make_user(email=""))
    make_loan(member=member_obj, copy=make_copy(), due_on=DUE_SOON)
    sender = RecordingSender()

    sent_count = SendDueReminders(reminder_sender=sender).execute(today=TODAY)

    assert sent_count == 0
    assert sender.sent == []
