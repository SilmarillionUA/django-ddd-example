from smtplib import SMTPException
from typing import Any

from django.utils import timezone

import structlog
from celery import shared_task

from lending.infrastructure.di import LendingContainer

logger = structlog.get_logger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(SMTPException,),
    retry_kwargs={"max_retries": 3, "countdown": 300},
)
def send_due_reminders(self) -> dict[str, Any]:
    logger.info("send_due_reminders.started", task_id=self.request.id)

    use_case = LendingContainer.get_send_due_reminders_use_case()
    sent_count = use_case.execute(today=timezone.localdate())

    logger.info(
        "send_due_reminders.completed",
        task_id=self.request.id,
        sent_count=sent_count,
    )
    return {"sent_count": sent_count}
