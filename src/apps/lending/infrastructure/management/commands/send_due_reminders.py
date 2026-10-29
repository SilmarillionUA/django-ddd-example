from django.core.management.base import BaseCommand
from django.utils import timezone

from lending.infrastructure.di import LendingContainer


class Command(BaseCommand):
    help = "Email members whose books are due soon."

    def handle(self, *args, **options) -> None:
        use_case = LendingContainer.get_send_due_reminders_use_case()
        sent_count = use_case.execute(today=timezone.localdate())

        self.stdout.write(f"Sent {sent_count} reminders.")
