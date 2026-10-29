from typing import Any

import requests
import structlog
from celery import shared_task

from catalog.infrastructure.di import CatalogContainer

logger = structlog.get_logger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(requests.RequestException,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)
def refresh_book_details(self, book_id: int) -> dict[str, Any]:
    logger.info(
        "refresh_book_details.started",
        task_id=self.request.id,
        book_id=book_id,
    )

    use_case = CatalogContainer.get_refresh_book_details_use_case()
    updated = use_case.execute(book_id=book_id)

    logger.info(
        "refresh_book_details.completed",
        task_id=self.request.id,
        book_id=book_id,
        updated=updated,
    )
    return {"book_id": book_id, "updated": updated}
