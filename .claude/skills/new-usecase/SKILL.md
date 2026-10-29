---
name: new-usecase
description: Add an application use case class with one execute() method, DI wiring and tests. Use for any new user or scheduled action.
---

# Create an application use case

Create a use case with the name the user gives.

## Use case (`application/use_cases/{name}.py`)

```python
import logging
from datetime import date

from {app}.domain.exceptions import SomethingRefused
from {app}.domain.interfaces import SomeInterface
from {app}.domain.models import Thing

logger = logging.getLogger(__name__)


class DoThingUseCase:
    """
    What the action does and the rule a reader would not guess.
    """

    def __init__(self, *, some_gateway: SomeInterface) -> None:
        self._some_gateway = some_gateway

    def execute(self, *, user, thing_id: int, today: date) -> Thing:
        thing_obj = self._thing(user=user, thing_id=thing_id)
        self._check_allowed(thing_obj=thing_obj, today=today)

        ...
        return thing_obj
```

## Rules

- One public `execute()`, keyword-only. Private helpers for each step.
- Dependencies through `__init__`, typed as domain interfaces or services. Never import from `infrastructure/`.
- Pass the date or time in. Never call `timezone.now()` inside.
- Queries go through `Model.repository`. No inline filters.
- Refusals raise a domain error with a `code`.
- Wrap multi-row writes in `transaction.atomic()`. Catch `IntegrityError` only around the write the constraint protects, and raise the domain error from it.
- Return a model, a value, or a frozen dataclass read model built for the caller.

## DI (`infrastructure/di.py`)

```python
@staticmethod
def get_do_thing_use_case() -> DoThingUseCase:
    return DoThingUseCase(some_gateway=SomeGateway())
```

## Tests (`application/tests/test_{name}.py`)

Stub each interface with a small subclass. One test per rule.

## After creating

- Wire it to a view, API view, task or command through the container.
- `make format` and `make test`.
