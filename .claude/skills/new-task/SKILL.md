---
name: new-task
description: Add a Celery task that delegates to a use case through the DI container. Use for background or periodic work.
---

# Create a Celery task

Create a task with the name the user gives in the app's `infrastructure/tasks.py`.

```python
from typing import Any

import structlog
from celery import shared_task

from {app}.infrastructure.di import {App}Container

logger = structlog.get_logger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(SpecificNetworkError,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)
def do_thing(self, thing_id: int) -> dict[str, Any]:
    logger.info("do_thing.started", task_id=self.request.id, thing_id=thing_id)

    use_case = {App}Container.get_do_thing_use_case()
    result = use_case.execute(thing_id=thing_id)

    logger.info("do_thing.completed", task_id=self.request.id, result=result)
    return {"thing_id": thing_id, "result": result}
```

## Rules

- The task is a thin shell: read arguments, call one use case from the container, log, return a dict.
- `autoretry_for` lists the specific errors worth retrying, not `Exception`.
- Pass ids, not model instances.
- Queue tasks from views with `transaction.on_commit`, so the worker never reads a row that is not there yet.
- Periodic tasks go in `CELERY_BEAT_SCHEDULE` in `settings/base.py`.
- Make sure the app is in `autodiscover_tasks` in `project_src/celery.py`.

## After creating

- Add a test in `infrastructure/tests/test_tasks.py`. Tests run Celery eagerly.
- `make format`
