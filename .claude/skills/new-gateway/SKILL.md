---
name: new-gateway
description: Add a domain interface (ABC) and its infrastructure gateway, for another app, an outside API or a side effect such as email. Use whenever code needs something outside its own app.
---

# Create a gateway behind a domain interface

Create a gateway with the name the user gives.

## Interface (`domain/interfaces.py`)

```python
from abc import ABC, abstractmethod


class CatalogInterface(ABC):
    """What lending needs to know about copies from the catalog app."""

    @abstractmethod
    def is_lendable(self, *, copy_id: int) -> bool: ...
```

- One interface per outside thing: another app, an outside service or a side effect like email.
- Methods speak domain types (value objects, ids, dataclasses), not HTTP or ORM types.

## Gateway (`infrastructure/gateways.py`)

```python
import structlog

logger = structlog.get_logger(__name__)


class CatalogGateway(CatalogInterface):
    def is_lendable(self, *, copy_id: int) -> bool:
        return Copy.repository.is_lendable(copy_id=copy_id)
```

- The only module allowed to import another app's models or an outside API client.
- For an outside API, never call `requests` here. Put the HTTP in a client in `corelib/external/<service>.py` (session, timeout, `Retry` policy, the API's own dataclasses), and pass it to the gateway in `__init__`. See `OpenLibraryClient` and `OpenLibraryGateway`.
- Put URLs and timeouts in module constants.
- Return `None` for a normal "not found". Let real failures raise, so tasks can retry them.

## DI

Pass the gateway in the container factory of every use case that needs it. Build its client there too:

```python
return RefreshBookDetailsUseCase(
    book_details=OpenLibraryGateway(client=OpenLibraryClient())
)
```

## Tests

- Use case tests use a stub subclass of the interface.
- Client tests in `corelib/external/tests/` patch the client's session.
- Gateway tests in `infrastructure/tests/test_gateways.py` pass a stub client and never touch HTTP.

## After creating

- `make format`
