import logging

from django.db import IntegrityError, transaction

from catalog.domain.exceptions import CopyCountOutOfRange, DuplicateIsbn
from catalog.domain.models import Book, Copy
from catalog.domain.settings import MAX_COPIES_PER_BOOK_REQUEST
from catalog.domain.types import Isbn

logger = logging.getLogger(__name__)


class AddBookUseCase:
    """
    Puts a new title in the catalog together with its first copies.

    The book and its copies are written in one transaction, so a
    catalog never holds a title nobody can borrow because the copies
    failed halfway.
    """

    def execute(
        self, *, raw_isbn: str, title: str, author: str, copy_count: int
    ) -> Book:
        isbn = Isbn.from_raw(raw_isbn)
        self._check_new(isbn=isbn)
        self._check_copy_count(copy_count=copy_count)

        book_obj = self._create(
            isbn=isbn, title=title, author=author, copy_count=copy_count
        )

        logger.info("Book added: isbn=%s copies=%s", isbn, copy_count)
        return book_obj

    @staticmethod
    def _check_new(*, isbn: Isbn) -> None:
        if Book.repository.exists_with_isbn(isbn=isbn.value):
            raise DuplicateIsbn(isbn.value)

    @staticmethod
    def _check_copy_count(*, copy_count: int) -> None:
        if not 1 <= copy_count <= MAX_COPIES_PER_BOOK_REQUEST:
            raise CopyCountOutOfRange(copy_count)

    @staticmethod
    def _create(
        *, isbn: Isbn, title: str, author: str, copy_count: int
    ) -> Book:
        # The check above reads first, so two librarians adding the same
        # book at once can both pass it. The unique index settles that.
        try:
            with transaction.atomic():
                book_obj = Book.objects.create(
                    isbn=isbn.value, title=title, author=author
                )
                Copy.repository.add_copies(book=book_obj, count=copy_count)
        except IntegrityError as exc:
            raise DuplicateIsbn(isbn.value) from exc

        return book_obj
