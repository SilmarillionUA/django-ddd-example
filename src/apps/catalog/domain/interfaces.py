from abc import ABC, abstractmethod

from catalog.domain.types import BookDetails, Isbn


class BookDetailsInterface(ABC):
    """An outside catalogue we ask about a book by its ISBN."""

    @abstractmethod
    def fetch(self, *, isbn: Isbn) -> BookDetails | None: ...
