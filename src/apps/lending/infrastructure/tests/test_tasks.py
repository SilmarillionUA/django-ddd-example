from datetime import timedelta

from django.core import mail
from django.core.management import call_command
from django.utils import timezone

from lending.domain.settings import REMINDER_DAYS_BEFORE_DUE
from lending.infrastructure.tasks import send_due_reminders


def make_loan_due_soon(*, make_member, make_copy, make_loan):
    today = timezone.localdate()
    make_loan(
        member=make_member(),
        copy=make_copy(title="Dune"),
        borrowed_on=today,
        due_on=today + timedelta(days=REMINDER_DAYS_BEFORE_DUE),
    )


def test_task_emails_due_reminders(make_member, make_copy, make_loan):
    make_loan_due_soon(
        make_member=make_member, make_copy=make_copy, make_loan=make_loan
    )

    result = send_due_reminders.delay().get()

    assert result == {"sent_count": 1}
    assert mail.outbox[0].to == ["reader@example.com"]
    assert "Dune" in mail.outbox[0].body


def test_management_command_runs_the_same_use_case(
    make_member, make_copy, make_loan
):
    make_loan_due_soon(
        make_member=make_member, make_copy=make_copy, make_loan=make_loan
    )

    call_command("send_due_reminders")

    assert len(mail.outbox) == 1
