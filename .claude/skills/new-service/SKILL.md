---
name: new-service
description: Add a pure domain service with a frozen dataclass policy. Use for calculations or rules that need no database and no clock.
---

# Create a domain service

Create a domain service with the name the user gives.

## Service (`domain/services/{name}.py`)

```python
from dataclasses import dataclass
from datetime import date

from {app}.domain.settings import FEE_CENTS_PER_DAY, FEE_GRACE_DAYS


@dataclass(frozen=True)
class FeePolicy:
    cents_per_day: int = FEE_CENTS_PER_DAY
    grace_days: int = FEE_GRACE_DAYS


class FeeCalculator:
    def __init__(self, *, policy: FeePolicy = FeePolicy()) -> None:
        self._policy = policy

    def fee_for(self, *, due_on: date, returned_on: date) -> Fee:
        ...
```

## Rules

- Pure: no ORM, no clock, no network. Values in, values out.
- Configuration is a frozen dataclass whose defaults come from `domain/settings.py`.
- Results are frozen dataclasses in `domain/types.py`.
- Use cases receive the service through `__init__`; the container builds it.
- Tests are plain unit tests with `@pytest.mark.unit` and a custom policy.

## After creating

- `make format`
