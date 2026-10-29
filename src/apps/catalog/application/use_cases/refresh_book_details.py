import logging

from catalog.domain.interfaces import BookDetailsInterface
from catalog.domain.models import Book
from catalog.domain.types import Isbn

logger = logging.getLogger(__name__)


class RefreshBookDetailsUseCase:
    """
    Fills in what an outside catalogue knows about one book.

    The librarian's typing wins on the title when the outside source
    has none. A book the source does not know keeps what it had.
    """

    def __init__(self, *, book_details: BookDetailsInterface) -> None:
        self._book_details = book_details

    def execute(self, *, book_id: int) -> bool:
        book_obj = Book.repository.find(book_id=book_id)
        if book_obj is None:
            # Deleted after the task was queued. Nothing to retry.
            logger.info("Book gone before refresh: id=%s", book_id)
            return False

        details = self._book_details.fetch(isbn=Isbn(value=book_obj.isbn))
        if details is None:
            return False

        return Book.repository.update_details(
            book_id=book_id,
            title=details.title or book_obj.title,
            page_count=details.page_count,
        )
