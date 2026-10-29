from abc import ABC, abstractmethod
from datetime import date


class CatalogInterface(ABC):
    """What lending needs to know about copies from the catalog app."""

    @abstractmethod
    def copy_id_for_barcode(self, *, barcode: str) -> int | None: ...

    @abstractmethod
    def is_lendable(self, *, copy_id: int) -> bool: ...


class ReminderSenderInterface(ABC):
    @abstractmethod
    def send_due_reminder(
        self, *, email: str, book_title: str, due_on: date
    ) -> None: ...
